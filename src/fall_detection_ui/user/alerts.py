import pandas as pd
import glob
import os
import json
import streamlit as st

def load_alerts(user_id):
    base_dir = os.getcwd()
    alert_dir = os.path.join(base_dir, "..", "storage", user_id, "alerts")
    alert_files = glob.glob(os.path.join(alert_dir, "*.json"))
    alerts = []

    for alert_file in alert_files:
        with open(alert_file, "r") as f:
            alert = json.load(f)
            alerts.append(alert)

    return pd.DataFrame(alerts)

@st.fragment
def draw_alerts():
    user_id = st.session_state.get("login_username", "default_user")
    alerts_df = load_alerts(user_id)

    if not alerts_df.empty:
        st.subheader("Alerts")
        camera_ids = alerts_df["camera_id"].unique()
        selected_camera = st.selectbox("Filter by Camera ID", ["All"] + list(camera_ids))

        if selected_camera != "All":
            alerts_df = alerts_df[alerts_df["camera_id"] == selected_camera]

        alerts_df["timestamp"] = pd.to_datetime(alerts_df["timestamp"], unit='s')
        st.dataframe(alerts_df.sort_values(by="timestamp", ascending=False))
    else:
        st.write("No alerts found.")

