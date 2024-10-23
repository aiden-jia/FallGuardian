import streamlit as st
import os



def update_username():
    st.session_state["login_username"] = st.session_state["username_input"]

def update_password():
    st.session_state["login_password"] = st.session_state["password_input"]

#st.set_page_config(page_title="Fall Detection System", page_icon=":guardsman:", layout="centered")
def login():
    # Initialize session states
    if "login_username" not in st.session_state:
        st.session_state["login_username"] = ""
    if "login_password" not in st.session_state:
        st.session_state["login_password"] = ""

    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .title {
            font-size: 2rem;
            font-weight: bold;
            color: #4b4b4b;
        }
        .description {
            font-size: 1.2rem;
            color: #6c757d;
            margin-bottom: 2rem;
        }
        .input {
            margin-bottom: 1rem;
        }
        .button {
            background-color: #007bff;
            color: blue;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #0056b3;
        }
        </style>
    """, unsafe_allow_html=True)

    #st.markdown('<div class="main">', unsafe_allow_html=True)
    #st.markdown('<div class="title">Fall Detection System</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([1,2,2])
    with col:
        st.header("FallGuardian")
        st.markdown(
            '<div class="description">An Autonomous Fall Detection and Protection System</div>',
            unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.text_input(
            "Username", key="username_input", placeholder="Enter your username",
            help="Your unique username", value=st.session_state["login_username"],
            on_change=update_username
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input(
            "Password", type="password", key="password_input", placeholder="Enter your password",
            help="Your secure password", value=st.session_state["login_password"],
            on_change=update_password
        )

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Login", key="login_button", help="Click to login"):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            user_folder = os.path.join(base_dir, "storage", st.session_state["login_username"])
            password_file = os.path.join(user_folder, "password.txt")
            if os.path.exists(password_file):
                with open(password_file, "r") as f:
                    saved_password = f.read()
                if st.session_state["login_password"] == saved_password:
                    st.session_state["logged_in"] = True
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Invalid username or password")


if __name__ == "__main__":
    login()