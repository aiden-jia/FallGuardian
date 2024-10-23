import os
from loguru import logger
import cv2
from numpy.f2py.auxfuncs import throw_error
from threading import Condition
import threading
import time
import streamlit as st



class FrameFetcher:

    def __init__(self, selected_file):
        self.selected_file = selected_file
        self.start = False
        self.stop = False

    def run_fetch(self,  frames_to_update, cv: Condition, step):
        logger.debug("run_fetch thread Id: {id}".format(id=threading.get_ident()))
        cap = cv2.VideoCapture(self.selected_file)
        total_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        if not cap.isOpened():
            error_msg = "Failed to open the video file : {file}".format(file=self.selected_file)
            logger.error(error_msg)
            throw_error(error_msg)

        self.start = True
        start_index = 0
        while True:
            # if st.session_state["stop_signal"]:
            #     logger.debug("stop signal received. will stop fetching frames")
            #     break

            start_time = time.time()
            logger.debug("start to get frames...")
            try:
                frames, start_index = self.get_n_frames(start_index, total_frame, cap, 24, step) # need 24 frames as the 3D CNN model is trained with 24 * 128 * 128 * 3 input shape
            except Exception as e:
                logger.error("Error in getting frames: {e}".format(e=e))
                break

            if not frames:
                break

            time_took = time.time() - start_time
            logger.debug("got frames. Time spent: {t} secs".format(t=time_took))
            # once new frames retrieved, check if the previous frames have been consumed
            with cv:
                while frames_to_update:
                    # if st.session_state["stop_signal"]:
                    #     logger.debug("stop signal received. will stop waiting for frames to be consumed")
                    #     break
                    logger.debug("previous frames are not consumed yet. will wait...")
                    cv.wait()
                logger.debug("sending back frames")
                #frames_to_update = frames.copy()  # this will not change the variable outside this function
                frames_to_update.extend(frames)
                cv.notify()

        # at the end, release
        cap.release()



    def get_n_frames(self, start_index, total_frame, cap: cv2.VideoCapture, num_frames_to_get, step = 1):
        frames = []
        next_index = start_index

        if total_frame < start_index:
            return []
        logger.debug("start_index: {start}, total_frame: {total}".format(start=start_index, total=total_frame))
        for index in range(start_index, min(start_index + num_frames_to_get * step, int(total_frame)), step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)

            ret, frame = cap.read()
            if ret:
                # Convert the frame from BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)
                next_index += step

        return frames, next_index