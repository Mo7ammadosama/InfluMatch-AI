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
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0">
          <div style="display:inline-flex;align-items:center;justify-content:center;
                      width:34px;height:34px;border-radius:10px;
                      background:linear-gradient(135deg,#7c3aed,#4f46e5);
                      box-shadow:0 2px 12px rgba(124,58,237,0.4);flex-shrink:0">
            <span style="font-size:1rem;line-height:1">&#9889;</span>
          </div>
          <div style="line-height:1.1">
            <div style="font-size:1.05rem;font-weight:800;letter-spacing:-0.02em">
              <span style="background:linear-gradient(135deg,#a78bfa,#818cf8);
                           -webkit-background-clip:text;-webkit-text-fill-color:transparent">Wasl</span><span
                   style="background:linear-gradient(135deg,#f59e0b,#fbbf24);
                           -webkit-background-clip:text;-webkit-text-fill-color:transparent">AI</span><span
                   style="color:#f59e0b;font-size:0.8rem">.jo</span>
            </div>
            <div style="font-size:0.55rem;color:#475569;letter-spacing:0.08em;text-transform:uppercase">AI Influencer Platform</div>
          </div>
          <span style="font-size:0.65rem;color:#64748b;margin-left:4px">{status_dot}</span>
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
