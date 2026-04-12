"""Session state helpers"""
import streamlit as st

def init_session():
    defaults = {
        "token": None,
        "user": None,
        "role": None,
        "lang": "ar",
        "page": "home",
        "chat_messages": [],
        "chat_open": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def is_logged_in() -> bool:
    return st.session_state.get("token") is not None

def get_role() -> str:
    return st.session_state.get("role", "")

def logout():
    for k in ["token", "user", "role"]:
        st.session_state[k] = None
    st.rerun()
