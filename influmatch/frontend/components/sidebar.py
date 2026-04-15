"""Role-based sidebar navigation — always visible"""
import streamlit as st
from ..utils.session import is_logged_in, get_role

MERCHANT_NAV = [
    ("🏠", "dashboard",  "Dashboard / لوحة التحكم"),
    ("📢", "campaigns",  "Campaigns / الحملات"),
    ("🔍", "discover",   "Discover / اكتشف"),
    ("💰", "escrow",     "Escrow / الضمان"),
    ("📄", "contracts",  "Contracts / العقود"),
    ("💎", "wallet",     "Wallet / المحفظة"),
    ("⚙️", "settings",  "Settings / الإعدادات"),
]

INFLUENCER_NAV = [
    ("🏠", "dashboard",    "Dashboard / لوحة التحكم"),
    ("📊", "my_campaigns", "My Campaigns / حملاتي"),
    ("💼", "profile",      "Profile / الملف الشخصي"),
    ("💰", "earnings",     "Earnings / الأرباح"),
    ("📄", "contracts",    "Contracts / العقود"),
    ("⚙️", "settings",    "Settings / الإعدادات"),
]

ADMIN_NAV = [
    ("👁️", "god_mode",   "God Mode Dashboard"),
    ("👥", "users",       "Users"),
    ("📢", "campaigns",   "All Campaigns"),
    ("⚖️", "disputes",   "Disputes"),
    ("📊", "analytics",  "Analytics"),
]

GUEST_NAV = [
    ("🏠", "home",     "Home / الرئيسية"),
    ("🔍", "browse",   "Browse Influencers / تصفح"),
    ("🔑", "login",    "Login / تسجيل الدخول"),
    ("📝", "register", "Register / إنشاء حساب"),
]


def render_sidebar():
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center;padding:1rem 0 0.5rem">
                <span style="font-size:2.5rem">🎯</span><br>
                <span style="font-weight:700;font-size:1.1rem;color:#A78BFA">InfluMatch.jo</span><br>
                <span style="font-size:0.7rem;color:#64748B">AI Influencer Platform</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        logged_in = is_logged_in()

        if not logged_in:
            _render_nav(GUEST_NAV)
            return

        role = get_role()
        user = st.session_state.get("user") or {}
        name = (
            user.get("full_name_en")
            or user.get("full_name_ar")
            or user.get("username")
            or "User"
        )

        role_meta = {
            "merchant":   {"label": "تاجر",  "icon": "🏪", "color": "#f59e0b", "desc": "لوحة تحكم التاجر"},
            "influencer": {"label": "مؤثر",  "icon": "🌟", "color": "#8b5cf6", "desc": "بوابة المؤثر"},
            "admin":      {"label": "مدير",  "icon": "⚡", "color": "#ef4444", "desc": "مركز تحكم ARIA"},
        }.get(role, {"label": "زائر", "icon": "👤", "color": "#6b7280", "desc": "InfluMatch.jo"})

        st.sidebar.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,0,0,0.4),rgba(0,0,0,0.2));
            border:1px solid {role_meta['color']}33;border-radius:12px;
            padding:0.8rem 1rem;margin-bottom:1rem;
            border-left:4px solid {role_meta['color']}">
  <div style="display:flex;align-items:center;gap:0.5rem">
    <span style="font-size:1.3rem">{role_meta['icon']}</span>
    <div>
      <div style="color:{role_meta['color']};font-weight:700;font-size:0.9rem">
        {name} · {role_meta['label']}
      </div>
      <div style="color:#a0a0b0;font-size:0.7rem">{role_meta['desc']}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        nav = (
            MERCHANT_NAV   if role == "merchant"   else
            INFLUENCER_NAV if role == "influencer" else
            ADMIN_NAV
        )
        _render_nav(nav)

        st.divider()

        # ARIA Chatbot toggle
        if st.button("🤖  ARIA AI Assistant", use_container_width=True, key="sidebar_chatbot_toggle"):
            st.session_state["chat_open"] = not st.session_state.get("chat_open", False)
            st.rerun()

        # Quick logout
        if logged_in:
            if st.button("🚪  Logout", use_container_width=True, key="sidebar_logout", type="secondary"):
                from ..utils.session import logout
                logout()


def _render_nav(nav):
    current = st.session_state.get("page", "home")
    for icon, page_key, label in nav:
        is_active = (current == page_key)
        clicked = st.button(
            f"{icon}  {label}",
            key=f"nav__{page_key}",          # double underscore avoids key clashes
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )
        if clicked:
            st.session_state["page"] = page_key
            st.rerun()
