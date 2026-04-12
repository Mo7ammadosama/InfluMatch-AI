"""
InfluMatch.jo — Streamlit Frontend Entry Point
Bilingual (Arabic RTL + English) | Jordan Market
Run: streamlit run frontend/app.py
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.components.navbar import render_navbar
from frontend.pages import landing, auth, merchant_dashboard, influencer_dashboard

st.set_page_config(
    page_title="InfluMatch.jo | منصة المؤثرين",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "InfluMatch.jo — AI-Powered Influencer Marketing Platform | Jordan",
    },
)

# --- Load CSS ---
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Session State Init ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "token" not in st.session_state:
    st.session_state.token = None
if "language" not in st.session_state:
    st.session_state.language = "ar"

# --- Navigation ---
render_navbar()

# --- Page Router ---
if not st.session_state.authenticated:
    page = st.session_state.get("page", "landing")
    if page == "landing":
        landing.render()
    elif page in ("login", "register"):
        auth.render()
else:
    role = st.session_state.user.get("role", "")
    page = st.session_state.get("page", "dashboard")

    if role == "merchant":
        merchant_dashboard.render()
    elif role == "influencer":
        influencer_dashboard.render()
    else:
        st.error("Unknown role. Please contact support.")
