import streamlit as st
from fall_detection_ui.login import login
from fall_detection_ui.register import register
import fall_detection_ui.utils.css_utils as utl
from fall_detection_ui.utils.image_utils import img_to_base64
from fall_detection_ui.user.settings import draw_settings
from fall_detection_ui.user.video_page import draw_video_page
from fall_detection_ui.user.alerts import draw_alerts

# css styling is copied from https://github.com/BugzTheBunny/streamlit_custom_gui/blob/main/application.py
st.set_page_config(layout="wide", page_title="Fall Detection System", page_icon=":guardsman:")
utl.set_page_title('Inshop Analytics tool')
#st.set_option('deprecation.showPyplotGlobalUse', False)
# Loading CSS
utl.local_css("css/dungeon.css")
utl.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


def show_icon():
    st.sidebar.write("FallGuardian")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    #Load and display sidebar image
    img_path = "images/fall-app-icon.png"
    img_base64 = img_to_base64(img_path)
    if img_base64:
        st.sidebar.markdown(
            # f'<img src="data:image/png;base64,{img_base64}" class="cover-glow">',
            f'<img src="data:image/png;base64,{img_base64}">',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown("---")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Check if the user is on the register page
if "on_register_page" not in st.session_state:
    st.session_state["on_register_page"] = False

def show_register():
    st.session_state["on_register_page"] = True

if not st.session_state["logged_in"]:
    if st.session_state["on_register_page"]:
        register()
    else:
        show_icon()
        st.sidebar.button("Register", key="register_button", on_click=show_register)
        login()
else:
    # copy from https://github.com/AdieLaine/Streamly/blob/main/streamly.py#L256
    # Insert custom CSS for glowing effect
    st.markdown(
        """
        <style>
        .cover-glow {
            width: 100%;
            height: auto;
            padding: 3px;
            box-shadow: 
                0 0 5px #1a001a,
                0 0 10px #330033,
                0 0 15px #4d004d,
                0 0 20px #660066,
                0 0 25px #800080,
                0 0 30px #993399,
                0 0 35px #b366b3;
            position: relative;
            z-index: -1;
            border-radius: 45px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    show_icon()

    st.logo("images/fall-app-icon.png", size= "large", icon_image="images/icons8-menu-48.png")
    #
    # pages = {
    #     "Custom View": [
    #         st.Page("user/settings.py", title="settings"),
    #         st.Page("user/video_page.py", title="video page"),
    #     ],
    #     "Developer View": [
    #         st.Page("developer/conv2d_lstm.py", title="conv2d lstm model"),
    #         st.Page("developer/conv3d.py", title="3D Cov Model")
    #     ]
    # }
    #
    # pg = st.navigation(pages)
    # pg.run()

    # use tabs to display the different pages
    # Create tabs for navigation
    tabs = st.tabs(["Video Page", "Alerts", "Settings"])

    with tabs[0]:
        draw_video_page()
    with tabs[1]:
        draw_alerts()
    with tabs[2]:
        draw_settings()


