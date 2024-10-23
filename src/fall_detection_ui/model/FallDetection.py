import time


import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import os
from PIL import Image, ImageTk
import time
import tensorflow as tf
import numpy as np
import threading
from loguru import logger
import streamlit as st


class FallDetector:

    def __init__(self, model_choice):
        self.root = tk.Tk()
        self.result = None  # Result will be set later
        self.video_label = None
        self.result_label = None
        self.file_entry = None
        self.selected_file = None  # To store the selected file path
        self.model_input_queue = []
        self.display_queue = []
        self.model_output_queue = []

        working_directory = os.getcwd()
        model_path = os.path.join(working_directory, "model",
                                  "LRCN_FAIL_Date_Time_2024_08_20__00_12_41__Loss_0.6136224865913391__Accuracy_0.8586956262588501.h5")
        if model_choice == "3D CNN":
            model_path = os.path.join(working_directory, "model", 'fall-detection_v2.h5')
        logger.info("Loading model from: {path}".format(path=model_path))
        self.model = tf.keras.models.load_model(model_path)

    def run_predict(self, model_input_queue, predict_output_queue, cv: threading.Condition):
        try:
            while True:
                with cv:
                    while not model_input_queue:
                        start_time = time.time()
                        logger.debug("waiting for model input...")
                        cv.wait()

                    time_took = time.time() - start_time
                    logger.debug("Received module input after waiting for {t} secs".format(t=time_took))

                    start_time = time.time()
                    frames_list = []
                    for f in model_input_queue:
                        resized_frame = cv2.resize(f, (124, 124))
                        frames_list.append(resized_frame)
                    if len(frames_list) < 24:
                        logger.debug(f"Not enough frames to make a prediction: {len(frames_list)}. Model stopped.")
                        return
                    prob = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
                    predict_output_queue.append(prob)
                    model_input_queue.clear()
                    time_took = time.time() - start_time
                    logger.debug("Prediction done. It took {t} secs".format(t=time_took))
                    cv.notify()
        except Exception as e:
            logger.error("Error in run_predict: {e}".format(e=e))




