import os
import cv2
import base64
from loguru import logger
import streamlit as st
from st_clickable_images import clickable_images

from fall_detection_ui.user.controller import fetch_display_pred


@st.fragment
def draw_video_page():
    # Get the current working directory (this is the project folder)
    project_directory = os.getcwd()
    logger.debug("project_directory: {dir}".format(dir=project_directory))
    video_directory = os.path.join(project_directory, "videos")

    # Define the supported video file extensions
    supported_extensions = ('.mp4', '.avi', '.mov')

    # List all video files in the project directory
    video_files = [f for f in os.listdir(video_directory) if f.endswith(supported_extensions)]

    # Display video cards at the top of the page
    st.subheader("Select a Camera")
    if video_files:
        with st.container(border=True):
            # calculate how many columns to display
            n_cols = 3
            n_rows = 1 + len(video_files) // int(n_cols)
            rows = [st.container() for _ in range(n_rows)]
            cols_per_row = [r.columns(n_cols) for r in rows]
            cols = [column for row in cols_per_row for column in row]

            # for image_index, cat_image in enumerate(cat_images):
            #     cols[image_index].image(cat_image)

            for idx, video_file in enumerate(video_files):
                current_col = cols[idx] # clos is a flattened list of all columns
                video_path = os.path.join(video_directory, video_file)
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    # Convert the frame to a base64-encoded string
                    _, img_encoded = cv2.imencode('.png', frame)
                    img_bytes = img_encoded.tobytes()
                    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    img_data = f"data:image/png;base64,{img_base64}"

                    current_col.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
                            <img src="{img_data}" width="200" alt="Camera {idx + 1}">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    current_col.markdown("<br><br>", unsafe_allow_html=True)
                    _, button_col, _ = current_col.columns(3)
                    if button_col.button(f"Camera {idx + 1}", key=f"camera_button_{idx}"):
                        st.session_state["selected_video"] = video_file
                        st.session_state["selected_camera"] = f"Camera {idx + 1}"


    # If a video has been selected, display the video full-screen
    if "selected_video" in st.session_state:
        selected_video = st.session_state["selected_video"]
        video_path = os.path.join(video_directory, selected_video)

        # THE MAIN FUNCTION THAT DISPLAYS THE VIDEO AND THE PREDICTIONS
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader(st.session_state["selected_camera"])
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_display_pred(st.session_state["selected_camera"], video_path )
        #st.rerun()
