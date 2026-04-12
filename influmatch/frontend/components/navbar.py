"""Top navigation bar"""
import streamlit as st
from ..utils.i18n import t
from ..utils.session import logout, is_logged_in, get_role
from ..utils.api_client import check_api_health

def render_navbar():
    api_ok = check_api_health()
    status_dot = "🟢" if api_ok else "🔴"

    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:8px 0">
            <span style="font-size:1.6rem">🎯</span>
            <span style="font-size:1.1rem;font-weight:700;color:#A78BFA">InfluMatch.jo</span>
            <span style="font-size:0.7rem;color:#64748b">{status_dot} API</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        lang = st.session_state.get("lang", "ar")
        tabs_ar = ["🏠 الرئيسية", "🔍 المؤثرون", "📢 الحملات", "ℹ️ عن المنصة"]
        tabs_en = ["🏠 Home", "🔍 Influencers", "📢 Campaigns", "ℹ️ About"]
        tabs = tabs_ar if lang == "ar" else tabs_en

    with col3:
        lang_col, auth_col = st.columns(2)
        with lang_col:
            lang = st.session_state.get("lang", "ar")
            if st.button("🌐 EN" if lang == "ar" else "🌐 AR", key="lang_toggle"):
                st.session_state["lang"] = "en" if lang == "ar" else "ar"
                st.rerun()
        with auth_col:
            if is_logged_in():
                if st.button(t("logout"), key="nav_logout"):
                    logout()
            else:
                if st.button(t("login"), key="nav_login"):
                    st.session_state["page"] = "login"
                    st.rerun()

    st.markdown("<hr style='border-color:rgba(148,163,184,0.1);margin:0 0 1rem 0'>", unsafe_allow_html=True)
