# https://towardsdatascience.com/developing-web-based-real-time-video-audio-processing-apps-quickly-with-streamlit-7c7bcd0bc5a8

import os
import sys

import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import logging
from loguru import logger


streamlit_cloud_root = "/mount/src/fall_detection_ui/src/"
if os.path.exists(streamlit_cloud_root):
    os.chdir(streamlit_cloud_root)
    sys.path.append(streamlit_cloud_root)

st_webrtc_logger = logging.getLogger("streamlit_webrtc")
st_webrtc_logger.setLevel(logging.WARNING)

aioice_logger = logging.getLogger("aioice")
aioice_logger.setLevel(logging.WARNING)

st.title("My first Streamlit app")
st.write("Hello, world")

threshold1 = st.slider("Threshold1", min_value=0, max_value=1000, step=1, value=100)
threshold2 = st.slider("Threshold2", min_value=0, max_value=1000, step=1, value=200)


def callback(frame):
    logger.debug("got a frame!")
    img = frame.to_ndarray(format="bgr24")

    img = cv2.cvtColor(cv2.Canny(img, threshold1, threshold2), cv2.COLOR_GRAY2BGR)

    return av.VideoFrame.from_ndarray(img, format="bgr24")

def callback_test(frame):
    logger.debug("got a frame!")
    return frame

webrtc_streamer(key="example", video_frame_callback=callback)