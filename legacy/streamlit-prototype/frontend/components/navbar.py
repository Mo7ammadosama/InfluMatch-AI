"""
WaslAI.jo — Navigation Bar Component
Bilingual toggle + auth state aware
"""
import streamlit as st


def render_navbar():
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        lang = st.session_state.get("language", "ar")
        title = "🎯 WaslAI.jo — منصة المؤثرين" if lang == "ar" else "🎯 WaslAI.jo — Influencer Platform"
        st.markdown(f"### {title}")

    with col2:
        current_lang = st.session_state.get("language", "ar")
        if st.button("🌐 EN" if current_lang == "ar" else "🌐 عربي", key="lang_toggle"):
            st.session_state.language = "en" if current_lang == "ar" else "ar"
            st.rerun()

    with col3:
        if st.session_state.get("authenticated"):
            user = st.session_state.user or {}
            name = user.get("full_name_ar") or user.get("full_name", "User")
            if st.button(f"🚪 {name}", key="logout_btn"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.token = None
                st.session_state.page = "landing"
                st.rerun()
        else:
            if st.button("🔑 تسجيل الدخول" if st.session_state.get("language") == "ar" else "🔑 Login", key="login_btn"):
                st.session_state.page = "login"
                st.rerun()

    st.divider()
