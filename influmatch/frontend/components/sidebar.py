"""Role-based sidebar navigation — always visible"""
import streamlit as st
from ..utils.session import is_logged_in, get_role
from ..utils.api_client import api_get

MERCHANT_NAV = [
    ("🏠", "dashboard",  "Dashboard / لوحة التحكم"),
    ("📢", "campaigns",  "Campaigns / الحملات"),
    ("🔍", "discover",   "Discover / اكتشف"),
    ("📅", "bookings",   "My Bookings / حجوزاتي"),
    ("💰", "escrow",     "Escrow / الضمان"),
    ("📄", "contracts",  "Contracts / العقود"),
    ("💎", "wallet",     "Wallet / المحفظة"),
    ("⚙️", "settings",  "Settings / الإعدادات"),
]

INFLUENCER_NAV = [
    ("🏠", "dashboard",      "Dashboard / لوحة التحكم"),
    ("📢", "open_campaigns", "الحملات المتاحة / Open Campaigns"),
    ("📊", "my_campaigns",   "My Campaigns / حملاتي"),
    ("📅", "bookings",       "My Bookings / حجوزاتي"),
    ("💼", "profile",        "Profile / الملف الشخصي"),
    ("💰", "earnings",       "Earnings / الأرباح"),
    ("📄", "contracts",      "Contracts / العقود"),
    ("⚙️", "settings",      "Settings / الإعدادات"),
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
            <div style="text-align:center;padding:1.2rem 0 0.8rem">
              <div style="display:inline-flex;align-items:center;justify-content:center;
                          width:52px;height:52px;border-radius:16px;margin-bottom:0.7rem;
                          background:linear-gradient(135deg,#7c3aed,#4f46e5);
                          box-shadow:0 4px 24px rgba(124,58,237,0.5)">
                <span style="font-size:1.6rem;line-height:1">&#9889;</span>
              </div><br>
              <div style="font-weight:800;font-size:1.2rem;letter-spacing:-0.02em;line-height:1.2">
                <span style="background:linear-gradient(135deg,#a78bfa,#818cf8);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent">Wasl</span><span
                     style="background:linear-gradient(135deg,#f59e0b,#fbbf24);
                             -webkit-background-clip:text;-webkit-text-fill-color:transparent">AI</span><span
                     style="color:#f59e0b;font-size:0.9rem">.jo</span>
              </div>
              <div style="font-size:0.62rem;color:#475569;letter-spacing:0.1em;
                          text-transform:uppercase;margin-top:0.3rem">AI &middot; Influencer &middot; Marketing</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        logged_in = is_logged_in()

        if not logged_in:
            _render_nav(GUEST_NAV, badge_map={})
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
        }.get(role, {"label": "زائر", "icon": "👤", "color": "#6b7280", "desc": "WaslAI.jo"})

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

        # ── Unread message badge on Bookings nav item ─────────────
        unread_badge: dict = {}
        try:
            unread_data = api_get("/api/messages/unread-count/me") or {}
            unread_n    = int(unread_data.get("unread_count", 0))
            if unread_n > 0:
                unread_badge["bookings"] = unread_n
        except Exception:
            pass

        _render_nav(nav, badge_map=unread_badge)

        st.divider()

        # ── Platform Notifications Bell ───────────────────────
        _render_notifications(role)

        # ARIA Chatbot toggle
        if st.button("⚡  WaslAI GPT", use_container_width=True, key="sidebar_chatbot_toggle"):
            st.session_state["chat_open"] = not st.session_state.get("chat_open", False)
            st.rerun()

        # Quick logout
        if logged_in:
            if st.button("🚪  Logout", use_container_width=True, key="sidebar_logout", type="secondary"):
                from ..utils.session import logout
                logout()


def _render_notifications(role: str):
    """Fetch and display platform-wide notifications in sidebar"""
    try:
        notifs = api_get("/api/admin/notifications", params={"role": role}) or []
    except Exception:
        return
    if not notifs:
        return

    latest = notifs[0]
    msg    = latest.get("message_ar") or latest.get("message_en") or ""
    ts     = str(latest.get("created_at", ""))[:16]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(83,52,131,0.1));
                border:1px solid rgba(139,92,246,0.4);border-radius:10px;
                padding:0.6rem 0.8rem;margin-bottom:0.5rem">
      <div style="font-size:0.65rem;color:#8b5cf6;font-weight:700;margin-bottom:0.2rem">
        📢 إشعار من المنصة
      </div>
      <div style="font-size:0.78rem;color:#e0e0f0;line-height:1.4">{msg}</div>
      <div style="font-size:0.6rem;color:#6b7280;margin-top:0.3rem">{ts}</div>
    </div>""", unsafe_allow_html=True)

    if len(notifs) > 1 and st.button(f"📋 كل الإشعارات ({len(notifs)})", key="notif_all", use_container_width=True):
        st.session_state["show_all_notifs"] = not st.session_state.get("show_all_notifs", False)

    if st.session_state.get("show_all_notifs"):
        for n in notifs[1:]:
            st.markdown(f"""
            <div style="background:rgba(26,26,46,0.8);border:1px solid rgba(83,52,131,0.2);
                        border-radius:8px;padding:0.5rem 0.7rem;margin-bottom:0.4rem">
              <div style="font-size:0.75rem;color:#c0c0d0">{n.get('message_ar','')}</div>
              <div style="font-size:0.6rem;color:#6b7280">{str(n.get('created_at',''))[:16]}</div>
            </div>""", unsafe_allow_html=True)


def _render_nav(nav, badge_map: dict = None):
    badge_map = badge_map or {}
    current   = st.session_state.get("page", "home")
    for icon, page_key, label in nav:
        is_active = (current == page_key)
        badge_n   = badge_map.get(page_key, 0)
        btn_label = f"{icon}  {label}" + (f"  🔴 {badge_n}" if badge_n else "")
        clicked   = st.button(
            btn_label,
            key=f"nav__{page_key}",          # double underscore avoids key clashes
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )
        if clicked:
            st.session_state["page"] = page_key
            st.rerun()
