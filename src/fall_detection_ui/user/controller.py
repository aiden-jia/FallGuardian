import os

from loguru import logger
import time
import smtplib
from email.mime.text import MIMEText
import threading
import cv2
import streamlit as st
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from streamlit import session_state

from fall_detection_ui.user.settings import base_dir
from fall_detection_ui.utils.FrameFetcher import FrameFetcher
from fall_detection_ui.utils.video_utils import display_frames
from fall_detection_ui.model.FallDetection import FallDetector
from tensorflow.nn import softmax
import tensorflow as tf
import json
import fall_detection_ui.utils.css_utils as utl
from streamlit_custom_notification_box import custom_notification_box # https://github.com/Socvest/streamlit-custom-notification-box?tab=readme-ov-file

# from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx # I can't make session_state visible to different threads

notification_styles = {'material-icons':{'color': 'red'},
          'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
          'notification-text': {'':''},
          'close-button':{'':''},
          'link':{'':''}}

def my_tf_round(x, decimals = 0):
    multiplier = tf.constant(10**decimals, dtype=x.dtype)
    return tf.round(x * multiplier) / multiplier


def fetch_display_pred(camera_id, video_path):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info("Video fps: {fps}".format(fps=fps))
    cap.release()

    frame_fetcher = FrameFetcher(video_path)
    condition_fetch = threading.Condition()
    condition_model = threading.Condition()

    frames_to_display = []
    frames_model_input = []
    model_output = []

    logger.debug("main thread Id: {id}".format(id=threading.get_ident()))

    step = 2
    #ctx = get_script_run_ctx()  # create a context
    thread_fetcher = threading.Thread(target=frame_fetcher.run_fetch, args=(frames_to_display, condition_fetch, step))
    # add_script_run_ctx(thread_fetcher)
    thread_fetcher.start()

    fall_detector = FallDetector(st.session_state["model_choice"])
    thread_model = threading.Thread(target=fall_detector.run_predict,
                                    args=(frames_model_input, model_output, condition_model))
    # add_script_run_ctx(thread_fetcher)
    thread_model.start()

    _, video_col, _,  result_col, _ = st.columns([1, 6, 1 ,10, 2])
    with video_col:
        video_placeholder = st.empty()
    with result_col:
        result_container = st.container()
        alert_placeholder = result_container.empty()
        result_container.markdown("<br><br>", unsafe_allow_html=True)
        prediction_placeholder = result_container.empty()


    detection_results = []
    fall_queue = deque()

    while True:
        with condition_fetch:
            start_wait_time = None
            while not frames_to_display:
                start_wait_time = time.time()
                condition_fetch.wait()

            if start_wait_time:
                wait_time = time.time() - start_wait_time
                logger.debug("received frames to display after {t} secs".format(t=wait_time))
            else:
                logger.debug("received frames to display without waiting")

            with condition_model:
                start_wait_model_intake_time = None
                while frames_model_input:
                    start_wait_model_intake_time = time.time()
                    logger.debug("waiting for model to take input frames...")
                    condition_model.wait()
                if start_wait_model_intake_time:
                    wait_time = time.time() - start_wait_model_intake_time
                    logger.debug("model took input after {t} secs".format(t=wait_time))
                else:
                    logger.debug("model took input without waiting")
                frames_model_input.extend(frames_to_display.copy())
                condition_model.notify()

            start_time = time.time()
            display_frames(video_placeholder, frames_to_display, fps, step)
            frames_to_display.clear()
            condition_fetch.notify()
            time_took = time.time() - start_time
            logger.debug("done displaying. Time spent: {t} secs".format(t=time_took))

            with condition_model:
                while not model_output:
                    condition_model.wait()
                    logger.debug("waiting for model prediction...")

                detection_result = model_output[0] # get the latest and only prediction
                #detection_result = softmax(detection_result)  # make the probabilities less dramatic
                detection_result = my_tf_round(detection_result, 2)
                model_output.clear()
                detection_results.append("Fall probability: {prob0:.2f}            No-fall probability: {prob1:.2f}".format(prob0=detection_result[0], prob1= 1 - detection_result[0]))
                if len(detection_results) > 50:  # Keep only the last 50 results
                    detection_results.pop(0)
                prediction_placeholder.text_area("Detecting Fall/No-Fall probabilities for every second", "\n".join(detection_results),  height=600)

                # Check if the fall probability exceeds the threshold
                threshold = st.session_state.get("sensitivity_threshold", 0.5)
                required_consecutive_falls = st.session_state.get("consecutive_falls", 3)
                if detection_result[0] > threshold:
                    fall_queue.append(detection_result[0])
                    #alert_placeholder.warning("Number of falling batches: {num}".format(num=len(fall_queue)))
                    progress_text = "{num} consecutive seconds of falls have been detected".format(num=len(fall_queue))
                    alert_placeholder.progress(min(1.0, len(fall_queue) / float(required_consecutive_falls)), progress_text)
                else:
                    fall_queue.clear()
                    alert_placeholder.info("No-fall detected")

                # Send alert if the number of consecutive falls exceeds the required number
                check_send_alert(alert_placeholder, len(fall_queue), camera_id)

def check_send_alert(alert_placeholder, num_falls, camera_id):
    required_consecutive_falls = st.session_state.get("consecutive_falls", 3)
    alert_interval = st.session_state.get("alert_interval", 10) * 60  # Convert minutes to seconds

    if "last_alert_time" not in st.session_state:
        st.session_state["last_alert_time"] = 0

    current_time = time.time()
    time_since_last_alert = current_time - st.session_state["last_alert_time"]

    if num_falls >= required_consecutive_falls and time_since_last_alert > alert_interval:
        send_alert_email(camera_id)
        st.session_state["last_alert_time"] = current_time
        alert_placeholder.warning("Alert: Fall detected! An email has been sent to {email}.".format(email=st.session_state["email_address"]))


def send_alert_email(camera_id):
    user_id = st.session_state.get("login_username", "default_user")
    base_dir = os.getcwd()
    alert_dir = os.path.join(base_dir, "..", "storage", user_id, "alerts")
    os.makedirs(alert_dir, exist_ok=True)

    alert_message = {
        "timestamp": time.time(),
        "camera_id": camera_id,
        "message": "Alert: Fall detected! Notified Emergency Services and Important Contacts."
    }

    alert_file = os.path.join(alert_dir, f"alert_{int(alert_message['timestamp'])}.json")
    with open(alert_file, "w") as f:
        json.dump(alert_message, f)

    custom_notification_box(icon='info', textDisplay=alert_message['message'],
        externalLink='more info', url='#', styles=notification_styles, key="alert_notification")