import os
import streamlit as st
import fall_detection_ui.utils.css_utils as utl
from PIL import Image
import time


def main():
    # Settings
    st.set_page_config(layout="wide", page_title='Demo item')
    utl.set_page_title('Inshop Analytics tool')
    #st.set_option('deprecation.showPyplotGlobalUse', False)
    # Loading CSS
    dir_root = os.getcwd()
    css_path = os.path.join(dir_root, 'css', 'streamlit.css')
    #utl.local_css(css_path)
    utl.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
    # Logo
    logo_path = os.path.join(dir_root, 'images', 'fall-app-icon.png')
    logo = Image.open(logo_path)
    # Selecting a job
    # st.sidebar.image(logo)
    st.sidebar.selectbox('Select', ('loren', 'Ipsum'))
    st.sidebar.multiselect('Multi', ('loren', 'Ipsum'))
    st.sidebar.date_input('Date')
    st.sidebar.text_input('Text')
    st.sidebar.slider('Slider', min_value=5, max_value=20)
    st.warning('Warning')
    st.info('Info')
    st.error('Error')

    with utl.stNotification('Sample notification, always on top and floats (spiner is optional)'):
        time.sleep(5)


if __name__ == '__main__':
    main()