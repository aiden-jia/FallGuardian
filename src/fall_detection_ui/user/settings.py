import streamlit as st
import os
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_settings(user_id):
    save_path = os.path.join(base_dir, "..","storage", user_id, "settings.json")
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            return json.load(f)
    return {}


@st.fragment
def draw_settings():
    user_id = st.session_state.get("login_username", "default_user")  # Use the login_username from session state

    # Load previously saved settings
    saved_settings = load_settings(user_id)

    # Initialize session states
    if "sensitivity_threshold" not in st.session_state:
        st.session_state["sensitivity_threshold"] = saved_settings.get("sensitivity_threshold", 0.5)
    if "send_alerts" not in st.session_state:
        st.session_state["send_alerts"] = saved_settings.get("send_alerts", False)
    if "consecutive_falls" not in st.session_state:
        st.session_state["consecutive_falls"] = saved_settings.get("consecutive_falls", 1)
    if "email_address" not in st.session_state:
        st.session_state["email_address"] = saved_settings.get("email_address", "")
    if "model_choice" not in st.session_state:
        st.session_state["model_choice"] = saved_settings.get("model_choice", "2D CNN + LSTM")
    if "alert_interval" not in st.session_state:
        st.session_state["alert_interval"] = saved_settings.get("alert_interval", 10)

    st.title("Settings")


    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Model Settings")
    with st.container(border=True):
        _, col, _ = st.columns([1,2,2])
        with col:
            st.session_state["model_choice"] = st.selectbox(
                "Choose Model", ["2D CNN + LSTM", "3D CNN"], index=["2D CNN + LSTM", "3D CNN"].index(st.session_state["model_choice"]),
                label_visibility="visible"
            )
        #st.write(f"Selected model: {st.session_state['model_choice']}")

            st.markdown("<br><br>", unsafe_allow_html=True)

            st.session_state["sensitivity_threshold"] = st.slider(
                "Sensitivity Threshold - the higher the less sensitive", 0.0, 1.0, st.session_state["sensitivity_threshold"]
            )

            #st.write(f'<p style="color:#9c9d9f">{intro_text}</p>', unsafe_allow_html = True)
            st.write("The sensitivity threshold is set to: ", st.session_state["sensitivity_threshold"])

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Alert Settings")
    with st.container(border=True):
        st.session_state["send_alerts"] = st.checkbox(
            "Send alerts", st.session_state["send_alerts"]
        )
        if st.session_state["send_alerts"]:
            _, col, _ = st.columns([1, 2, 2])
            with col:
                st.session_state["consecutive_falls"] = st.selectbox(
                    "Minimal consecutive seconds detected with fall", list(range(1, 10)), index=st.session_state["consecutive_falls"] - 1
                )

                st.markdown("<br><br>", unsafe_allow_html=True)
                st.session_state["alert_interval"] = st.selectbox(
                    "Minimal interval time between two alerts (minutes)", list(range(10, 31)), index=st.session_state["alert_interval"] - 10
                )

                st.markdown("<br><br>", unsafe_allow_html=True)
                st.session_state["email_address"] = st.text_input(
                    "Email Address for Alerts", st.session_state["email_address"]
                )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Camera Settings")
    with st.container(border=True):
        _, col, _ = st.columns(3)
        with col:
            st.button("Add Camera")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Save Settings"):
        save_path = os.path.join(base_dir, "..","storage", user_id)
        os.makedirs(save_path, exist_ok=True)
        settings = {
            "sensitivity_threshold": st.session_state["sensitivity_threshold"],
            "send_alerts": st.session_state["send_alerts"],
            "consecutive_falls": st.session_state["consecutive_falls"] if st.session_state["send_alerts"] else None,
            "email_address": st.session_state["email_address"],
            "model_choice": st.session_state["model_choice"],
            "alert_interval": st.session_state["alert_interval"]
        }
        with open(os.path.join(save_path, "settings.json"), "w") as f:
            json.dump(settings, f)
        st.success("Settings saved successfully!")