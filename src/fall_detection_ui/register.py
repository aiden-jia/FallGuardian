import streamlit as st
import os

def register():
    st.title("Register")

    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")

    if st.button("Register", key="register_button"):
        if not username or not password or not confirm_password:
            st.error("All fields are required")
        elif password != confirm_password:
            st.error("Passwords do not match")
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            user_folder = os.path.join(base_dir, "storage", username)
            os.makedirs(user_folder, exist_ok=True)
            with open(os.path.join(user_folder, "password.txt"), "w") as f:
                f.write(password)
            st.success("User registered successfully")
            st.session_state["registered"] = True
            st.session_state["on_register_page"] = False  # Redirect to login page
            st.rerun()

if __name__ == "__main__":
    register()