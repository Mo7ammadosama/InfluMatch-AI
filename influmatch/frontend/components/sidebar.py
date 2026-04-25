"""Role-based sidebar navigation — always visible"""
import streamlit as st
from ..utils.session import is_logged_in, get_role
from ..utils.api_client import api_get
from ..utils.i18n import t


def _nav_items(role: str):
    """Return nav items for the given role, labels translated to current lang."""
    if role == "merchant":
        return [
            ("🏠", "dashboard",   t("dashboard")),
            ("📢", "campaigns",   t("campaigns")),
            ("🔍", "discover",    t("discover")),
            ("📅", "bookings",    t("bookings")),
            ("💰", "escrow",      t("escrow")),
            ("📄", "contracts",   t("contracts")),
            ("💎", "wallet",      t("wallet")),
            ("⚙️", "settings",   t("settings")),
        ]
    elif role == "influencer":
        return [
            ("🏠", "dashboard",       t("dashboard")),
            ("📢", "open_campaigns",  t("open_campaigns")),
            ("📊", "my_campaigns",    t("my_campaigns")),
            ("📅", "bookings",        t("bookings")),
            ("💼", "profile",         t("profile")),
            ("💰", "earnings",        t("earnings")),
            ("📄", "contracts",       t("contracts")),
            ("⚙️", "settings",       t("settings")),
        ]
    elif role == "admin":
        return [
            ("👁️", "god_mode",  t("god_mode")),
            ("👥", "users",      t("users")),
            ("📢", "campaigns",  t("all_campaigns")),
            ("⚖️", "disputes",  t("disputes")),
            ("📊", "analytics", t("analytics")),
        ]
    else:
        return [
            ("🏠", "home",     t("home")),
            ("🔍", "browse",   t("browse")),
            ("🔑", "login",    t("login")),
            ("📝", "register", t("register")),
        ]


def render_sidebar():
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────
        st.markdown(
            """
            <div style="padding:1.2rem 0.5rem 0.8rem">
              <div style="display:flex;align-items:center;gap:0.75rem">
                <div style="width:36px;height:36px;border-radius:8px;
                            background:#1e1e2c;border:1px solid rgba(255,255,255,0.1);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;flex-shrink:0">&#9889;</div>
                <div>
                  <div style="font-weight:800;font-size:1.05rem;letter-spacing:-0.01em;line-height:1.2;color:#f1f1f5">
                    WaslAI<span style="color:#f59e0b">.jo</span>
                  </div>
                  <div style="font-size:0.6rem;color:#4b5563;letter-spacing:0.08em;text-transform:uppercase">
                    Influencer Platform
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        logged_in = is_logged_in()

        if not logged_in:
            _render_nav(_nav_items("guest"), badge_map={})
            return

        role = get_role()
        user = st.session_state.get("user") or {}
        name = (
            user.get("full_name_en")
            or user.get("full_name_ar")
            or user.get("username")
            or "User"
        )

        lang = st.session_state.get("lang", "ar")

        role_meta = {
            "merchant":   {"label": t("merchant"),   "icon": "🏪", "color": "#f59e0b", "desc": t("merchant_portal")},
            "influencer": {"label": t("influencer"),  "icon": "🌟", "color": "#8b5cf6", "desc": t("influencer_portal")},
            "admin":      {"label": t("admin"),       "icon": "⚡", "color": "#ef4444", "desc": t("admin_portal")},
        }.get(role, {"label": "User", "icon": "👤", "color": "#6b7280", "desc": "WaslAI.jo"})

        st.sidebar.markdown(f"""
<div style="background:#17171f;border:1px solid rgba(255,255,255,0.07);
            border-left:3px solid {role_meta['color']};border-radius:8px;
            padding:0.65rem 0.9rem;margin-bottom:0.75rem">
  <div style="color:{role_meta['color']};font-weight:700;font-size:0.82rem;margin-bottom:0.1rem">
    {name}
  </div>
  <div style="color:#4b5563;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em">
    {role_meta['label']}
  </div>
</div>""", unsafe_allow_html=True)

        # ── Unread message badge on Bookings nav item ─────────────
        unread_badge: dict = {}
        try:
            unread_data = api_get("/api/messages/unread-count/me") or {}
            unread_n    = int(unread_data.get("unread_count", 0))
            if unread_n > 0:
                unread_badge["bookings"] = unread_n
        except Exception:
            pass

        _render_nav(_nav_items(role), badge_map=unread_badge)

        st.divider()

        # ── Language toggle ───────────────────────────────────────
        current_lang = st.session_state.get("lang", "ar")
        toggle_label = "🌐  English" if current_lang == "ar" else "🌐  عربي"
        if st.button(toggle_label, use_container_width=True, key="lang_toggle"):
            st.session_state["lang"] = "en" if current_lang == "ar" else "ar"
            st.rerun()

        # ── Platform Notifications Bell ───────────────────────
        _render_notifications(role)

        # ARIA Chatbot toggle
        if st.button("⚡  WaslAI GPT", use_container_width=True, key="sidebar_chatbot_toggle"):
            st.session_state["chat_open"] = not st.session_state.get("chat_open", False)
            st.rerun()

        # Quick logout
        if st.button(f"🚪  {t('logout')}", use_container_width=True, key="sidebar_logout", type="secondary"):
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

    lang = st.session_state.get("lang", "ar")
    latest = notifs[0]
    msg = (latest.get("message_en") if lang == "en" else latest.get("message_ar")) or latest.get("message_ar") or latest.get("message_en") or ""
    ts  = str(latest.get("created_at", ""))[:16]
    notif_label = "📢 Platform Notification" if lang == "en" else "📢 إشعار من المنصة"

    st.markdown(f"""
    <div style="background:#17171f;border:1px solid rgba(124,58,237,0.2);
                border-left:3px solid #7c3aed;border-radius:8px;
                padding:0.6rem 0.8rem;margin-bottom:0.5rem">
      <div style="font-size:0.6rem;color:#7c3aed;font-weight:700;margin-bottom:0.2rem;
                  text-transform:uppercase;letter-spacing:0.06em">{notif_label}</div>
      <div style="font-size:0.76rem;color:#d1d5db;line-height:1.4">{msg}</div>
      <div style="font-size:0.6rem;color:#4b5563;margin-top:0.3rem">{ts}</div>
    </div>""", unsafe_allow_html=True)

    all_label = f"📋 {t('all_notifications')} ({len(notifs)})"
    if len(notifs) > 1 and st.button(all_label, key="notif_all", use_container_width=True):
        st.session_state["show_all_notifs"] = not st.session_state.get("show_all_notifs", False)

    if st.session_state.get("show_all_notifs"):
        for n in notifs[1:]:
            n_msg = (n.get("message_en") if lang == "en" else n.get("message_ar")) or ""
            st.markdown(f"""
            <div style="background:#17171f;border:1px solid rgba(255,255,255,0.06);
                        border-radius:6px;padding:0.45rem 0.65rem;margin-bottom:0.35rem">
              <div style="font-size:0.74rem;color:#d1d5db">{n_msg}</div>
              <div style="font-size:0.6rem;color:#4b5563">{str(n.get('created_at',''))[:16]}</div>
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
            key=f"nav__{page_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )
        if clicked:
            st.session_state["page"] = page_key
            st.rerun()
