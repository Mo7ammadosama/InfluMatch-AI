"""Module 12 — Streamlit Frontend Writer"""
import os

BASE = "C:/InfluMatch_AI/influmatch"

def w(rel_path, content):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK  {rel_path}  ({len(content)} bytes)")

# ── frontend/assets/css/style.css ──────────────────────────────────────────
w("frontend/assets/css/style.css", """
/* InfluMatch.jo — Global CSS */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --primary: #7C3AED;
    --primary-light: #A78BFA;
    --accent: #F59E0B;
    --dark: #0F172A;
    --surface: #1E293B;
    --surface2: #334155;
    --text: #F1F5F9;
    --text-muted: #94A3B8;
    --success: #10B981;
    --danger: #EF4444;
    --warning: #F59E0B;
    --border: rgba(148,163,184,0.15);
    --radius: 12px;
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
}

/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', 'Cairo', sans-serif !important;
    background-color: var(--dark) !important;
    color: var(--text) !important;
}

/* RTL support */
.rtl { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif !important; }
.ltr { direction: ltr; text-align: left; }

/* Streamlit overrides */
.stApp { background: var(--dark) !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1400px !important; }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #6D28D9) !important;
    color: white !important; border: none !important; border-radius: var(--radius) !important;
    font-weight: 600 !important; padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(124,58,237,0.4) !important; }

/* Cards */
.aria-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem;
    box-shadow: var(--shadow); margin-bottom: 1rem;
}
.aria-card:hover { border-color: var(--primary-light); transform: translateY(-2px); transition: all 0.2s; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--border); border-radius: var(--radius);
    padding: 1.5rem; text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: var(--primary-light); }
.metric-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

/* ARIA Score badge */
.aria-badge {
    display: inline-block; padding: 0.25rem 0.75rem;
    border-radius: 99px; font-size: 0.75rem; font-weight: 700;
}
.aria-platinum { background: linear-gradient(135deg, #e5e7eb, #d1d5db); color: #111; }
.aria-gold { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #111; }
.aria-silver { background: linear-gradient(135deg, #9ca3af, #6b7280); color: white; }
.aria-bronze { background: linear-gradient(135deg, #b45309, #92400e); color: white; }
.aria-unranked { background: var(--surface2); color: var(--text-muted); }

/* Status pills */
.status-pill {
    display: inline-block; padding: 0.2rem 0.6rem;
    border-radius: 99px; font-size: 0.72rem; font-weight: 600;
}
.status-active { background: rgba(16,185,129,0.2); color: var(--success); }
.status-pending { background: rgba(245,158,11,0.2); color: var(--warning); }
.status-completed { background: rgba(124,58,237,0.2); color: var(--primary-light); }
.status-disputed { background: rgba(239,68,68,0.2); color: var(--danger); }

/* Sidebar nav */
.nav-item {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.6rem 0.8rem; border-radius: 8px;
    color: var(--text-muted); cursor: pointer;
    margin-bottom: 0.25rem; transition: all 0.15s;
}
.nav-item:hover, .nav-item.active {
    background: rgba(124,58,237,0.15);
    color: var(--primary-light);
}

/* Floating chatbot */
.chatbot-fab {
    position: fixed; bottom: 24px; right: 24px;
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), #6D28D9);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; box-shadow: 0 8px 32px rgba(124,58,237,0.5);
    z-index: 9999; font-size: 1.5rem;
}
.chatbot-fab:hover { transform: scale(1.1); }

/* Tables */
.stDataFrame { background: var(--surface) !important; border-radius: var(--radius) !important; }

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}

/* Progress bars */
.stProgress > div > div { background: var(--primary) !important; border-radius: 99px !important; }

/* Alerts */
.stSuccess { background: rgba(16,185,129,0.1) !important; border-left: 3px solid var(--success) !important; }
.stError { background: rgba(239,68,68,0.1) !important; border-left: 3px solid var(--danger) !important; }
.stWarning { background: rgba(245,158,11,0.1) !important; border-left: 3px solid var(--warning) !important; }
.stInfo { background: rgba(124,58,237,0.1) !important; border-left: 3px solid var(--primary) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.viewerBadge_container__1QSob { display: none !important; }
""")

# ── frontend/utils/api_client.py ────────────────────────────────────────────
w("frontend/utils/__init__.py", "")
w("frontend/utils/api_client.py", '''"""Async HTTP client for InfluMatch API"""
import httpx
import streamlit as st

API_BASE = "http://localhost:8000"

def get_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_get(path: str, params: dict = None):
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=get_headers(), params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_post(path: str, data: dict = None, json: dict = None):
    try:
        r = httpx.post(f"{API_BASE}{path}", headers=get_headers(), data=data, json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def api_put(path: str, json: dict = None):
    try:
        r = httpx.put(f"{API_BASE}{path}", headers=get_headers(), json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def check_api_health():
    try:
        r = httpx.get(f"{API_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
''')

# ── frontend/utils/session.py ───────────────────────────────────────────────
w("frontend/utils/session.py", '''"""Session state helpers"""
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
''')

# ── frontend/utils/i18n.py ──────────────────────────────────────────────────
w("frontend/utils/i18n.py", '''"""Bilingual label lookup — Arabic / English"""
import streamlit as st

LABELS = {
    "app_name":       {"ar": "إنفلو ماتش",       "en": "InfluMatch.jo"},
    "login":          {"ar": "تسجيل الدخول",      "en": "Login"},
    "register":       {"ar": "إنشاء حساب",        "en": "Register"},
    "logout":         {"ar": "خروج",              "en": "Logout"},
    "email":          {"ar": "البريد الإلكتروني",  "en": "Email"},
    "password":       {"ar": "كلمة المرور",       "en": "Password"},
    "full_name":      {"ar": "الاسم الكامل",      "en": "Full Name"},
    "role":           {"ar": "نوع الحساب",        "en": "Account Type"},
    "merchant":       {"ar": "تاجر",              "en": "Merchant"},
    "influencer":     {"ar": "مؤثر",              "en": "Influencer"},
    "dashboard":      {"ar": "لوحة التحكم",       "en": "Dashboard"},
    "campaigns":      {"ar": "الحملات",           "en": "Campaigns"},
    "influencers":    {"ar": "المؤثرون",          "en": "Influencers"},
    "wallet":         {"ar": "المحفظة",           "en": "Wallet"},
    "contracts":      {"ar": "العقود",            "en": "Contracts"},
    "escrow":         {"ar": "الضمان المالي",     "en": "Escrow"},
    "settings":       {"ar": "الإعدادات",         "en": "Settings"},
    "save":           {"ar": "حفظ",               "en": "Save"},
    "cancel":         {"ar": "إلغاء",             "en": "Cancel"},
    "submit":         {"ar": "إرسال",             "en": "Submit"},
    "loading":        {"ar": "جاري التحميل...",   "en": "Loading..."},
    "error":          {"ar": "خطأ",               "en": "Error"},
    "success":        {"ar": "نجاح",              "en": "Success"},
    "aria_score":     {"ar": "نقاط ARIA",         "en": "ARIA Score"},
    "total_budget":   {"ar": "الميزانية الإجمالية","en": "Total Budget"},
    "status":         {"ar": "الحالة",            "en": "Status"},
    "followers":      {"ar": "المتابعون",         "en": "Followers"},
    "engagement":     {"ar": "معدل التفاعل",      "en": "Engagement Rate"},
    "niche":          {"ar": "التخصص",            "en": "Niche"},
    "city":           {"ar": "المدينة",           "en": "City"},
    "create_campaign":{"ar": "إنشاء حملة",       "en": "Create Campaign"},
    "view_details":   {"ar": "عرض التفاصيل",     "en": "View Details"},
    "points":         {"ar": "النقاط",            "en": "Points"},
    "tier":           {"ar": "المستوى",           "en": "Tier"},
    "chat_with_aria": {"ar": "تحدث مع ARIA",     "en": "Chat with ARIA"},
    "type_message":   {"ar": "اكتب رسالتك...",   "en": "Type your message..."},
    "send":           {"ar": "إرسال",             "en": "Send"},
    "welcome":        {"ar": "أهلاً وسهلاً",     "en": "Welcome"},
    "platform":       {"ar": "المنصة",           "en": "Platform"},
    "jordan_market":  {"ar": "سوق الأردن",       "en": "Jordan Market"},
}

def t(key: str) -> str:
    lang = st.session_state.get("lang", "ar")
    return LABELS.get(key, {}).get(lang, key)
''')

# ── frontend/components/navbar.py ───────────────────────────────────────────
w("frontend/components/__init__.py", "")
w("frontend/components/navbar.py", '''"""Top navigation bar"""
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
''')

# ── frontend/components/sidebar.py ─────────────────────────────────────────
w("frontend/components/sidebar.py", '''"""Role-based sidebar navigation"""
import streamlit as st
from ..utils.i18n import t
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

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem">
            <span style="font-size:2.5rem">🎯</span><br>
            <span style="font-weight:700;font-size:1.1rem;color:#A78BFA">InfluMatch.jo</span><br>
            <span style="font-size:0.7rem;color:#64748B">AI Influencer Platform</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr style='border-color:rgba(148,163,184,0.15)'>", unsafe_allow_html=True)

        if not is_logged_in():
            _render_guest_nav()
            return

        role = get_role()
        user = st.session_state.get("user", {})
        name = user.get("full_name", "User") if user else "User"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0.8rem;
                    background:rgba(124,58,237,0.1);border-radius:8px;margin-bottom:0.8rem">
            <span style="font-size:1.4rem">{'🏢' if role=='merchant' else '⭐' if role=='influencer' else '🛡️'}</span>
            <div>
                <div style="font-weight:600;font-size:0.85rem">{name}</div>
                <div style="font-size:0.7rem;color:#94A3B8;text-transform:capitalize">{role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav = MERCHANT_NAV if role == "merchant" else INFLUENCER_NAV if role == "influencer" else ADMIN_NAV
        current = st.session_state.get("page", "dashboard")

        for icon, page_key, label in nav:
            is_active = current == page_key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state["page"] = page_key
                st.rerun()

        st.markdown("<hr style='border-color:rgba(148,163,184,0.15)'>", unsafe_allow_html=True)

        # ARIA Chatbot toggle
        chat_open = st.session_state.get("chat_open", False)
        if st.button("🤖  ARIA AI Assistant", use_container_width=True):
            st.session_state["chat_open"] = not chat_open
            st.rerun()

def _render_guest_nav():
    for label, page in [("🏠 Home", "home"), ("🔍 Browse Influencers", "browse"),
                         ("🔑 Login", "login"), ("📝 Register", "register")]:
        if st.button(label, use_container_width=True, key=f"guest_{page}"):
            st.session_state["page"] = page
            st.rerun()
''')

# ── frontend/components/cards/influencer_card.py ───────────────────────────
w("frontend/components/cards/__init__.py", "")
w("frontend/components/cards/influencer_card.py", '''"""Influencer card component"""
import streamlit as st

TIER_COLORS = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render_influencer_card(inf: dict, show_invite: bool = False) -> bool:
    """Returns True if Invite button was clicked."""
    tier = inf.get("aria_tier", "UNRANKED")
    icon, bg, fg = TIER_COLORS.get(tier, TIER_COLORS["UNRANKED"])
    score = inf.get("aria_score", 0)
    ig_followers = inf.get("instagram_followers", 0)
    ig_er = inf.get("instagram_engagement_rate", 0)
    niche = inf.get("niche", "—")
    city = inf.get("city", "Amman")
    rate = inf.get("rate_per_post", 0)
    handle = inf.get("instagram_handle", "—")

    invited = False
    with st.container():
        st.markdown(f"""
        <div class="aria-card" style="border-radius:12px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div style="font-size:1.05rem;font-weight:700">@{handle}</div>
                    <div style="font-size:0.8rem;color:#94A3B8">{niche} · {city}</div>
                </div>
                <span style="background:{bg};color:{fg};padding:3px 10px;border-radius:99px;
                             font-size:0.72rem;font-weight:700">{icon} {tier}</span>
            </div>
            <div style="margin-top:0.8rem;display:flex;gap:1rem;flex-wrap:wrap">
                <div><span style="font-size:1.2rem;font-weight:700;color:#A78BFA">{score:.0f}</span>
                     <span style="font-size:0.7rem;color:#64748B"> ARIA</span></div>
                <div><span style="font-weight:600">{ig_followers:,}</span>
                     <span style="font-size:0.7rem;color:#64748B"> followers</span></div>
                <div><span style="font-weight:600">{ig_er:.1f}%</span>
                     <span style="font-size:0.7rem;color:#64748B"> engagement</span></div>
                <div><span style="font-weight:600">{rate:.0f}</span>
                     <span style="font-size:0.7rem;color:#64748B"> JOD/post</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if show_invite:
            if st.button(f"✉️ Invite @{handle}", key=f"invite_{inf.get('id',0)}_{handle}"):
                invited = True
    return invited
''')

# ── frontend/components/cards/campaign_card.py ─────────────────────────────
w("frontend/components/cards/campaign_card.py", '''"""Campaign card component"""
import streamlit as st

STATUS_STYLE = {
    "draft":        ("📝", "#334155", "#94A3B8"),
    "active":       ("✅", "rgba(16,185,129,0.15)", "#10B981"),
    "in_progress":  ("⚡", "rgba(245,158,11,0.15)", "#F59E0B"),
    "under_review": ("🔍", "rgba(124,58,237,0.15)", "#A78BFA"),
    "completed":    ("🏁", "rgba(16,185,129,0.1)", "#6EE7B7"),
    "disputed":     ("⚠️", "rgba(239,68,68,0.15)", "#EF4444"),
    "cancelled":    ("❌", "#1E293B", "#475569"),
}

def render_campaign_card(c: dict, actions: list = None):
    status = c.get("status", "draft")
    icon, bg, fg = STATUS_STYLE.get(status, STATUS_STYLE["draft"])
    title = c.get("title_en") or c.get("title_ar", "Untitled")
    budget = c.get("total_budget", 0)
    niche = c.get("niche", "—")

    st.markdown(f"""
    <div class="aria-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem">
            <div style="font-weight:700;font-size:1rem">{title}</div>
            <span style="background:{bg};color:{fg};padding:3px 10px;border-radius:99px;font-size:0.72rem;font-weight:600">
                {icon} {status.replace("_"," ").title()}
            </span>
        </div>
        <div style="display:flex;gap:1.2rem;font-size:0.82rem;color:#94A3B8">
            <span>💰 {budget:,.0f} JOD</span>
            <span>🏷️ {niche}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if actions:
        cols = st.columns(len(actions))
        for i, (label, key, callback) in enumerate(actions):
            with cols[i]:
                if st.button(label, key=key):
                    callback()
''')

# ── frontend/components/chatbot/floating_widget.py ─────────────────────────
w("frontend/components/chatbot/__init__.py", "")
w("frontend/components/chatbot/floating_widget.py", '''"""Floating ARIA Chatbot Widget"""
import streamlit as st
from ...utils.api_client import api_post
from ...utils.i18n import t

def render_chatbot():
    if not st.session_state.get("chat_open", False):
        return

    lang = st.session_state.get("lang", "ar")
    msgs = st.session_state.get("chat_messages", [])

    with st.expander("🤖 ARIA AI Assistant", expanded=True):
        # Message history
        chat_container = st.container()
        with chat_container:
            for msg in msgs[-20:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-end;margin:0.4rem 0">
                        <div style="background:rgba(124,58,237,0.25);padding:0.5rem 0.9rem;
                                    border-radius:12px 12px 0 12px;max-width:80%;font-size:0.88rem">
                            {content}
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:flex-start;margin:0.4rem 0">
                        <div style="background:rgba(30,41,59,0.9);border:1px solid rgba(148,163,184,0.15);
                                    padding:0.5rem 0.9rem;border-radius:12px 12px 12px 0;
                                    max-width:80%;font-size:0.88rem">
                            🤖 {content}
                        </div>
                    </div>""", unsafe_allow_html=True)

        # Input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                t("type_message"), key="chatbot_input",
                label_visibility="collapsed",
                placeholder="اسألني أي شيء... / Ask me anything..."
            )
        with col2:
            send = st.button(t("send"), key="chatbot_send")

        if send and user_input.strip():
            msgs.append({"role": "user", "content": user_input})
            status_code, resp = api_post(
                "/api/chat",
                json={"message": user_input, "language": lang}
            )
            if status_code == 200:
                reply = resp.get("response", "...")
            else:
                reply = "عذراً، حدث خطأ. / Sorry, an error occurred." if lang == "ar" else "Sorry, an error occurred."
            msgs.append({"role": "assistant", "content": reply})
            st.session_state["chat_messages"] = msgs
            st.rerun()

        if st.button("🗑️ Clear / مسح", key="chatbot_clear"):
            st.session_state["chat_messages"] = []
            st.rerun()
''')

# ── frontend/pages/auth_page.py ─────────────────────────────────────────────
w("frontend/pages/__init__.py", "")
w("frontend/pages/auth_page.py", '''"""Login & Register page"""
import streamlit as st
from ..utils.api_client import api_post
from ..utils.i18n import t

def render_login():
    lang = st.session_state.get("lang", "ar")
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1rem">
        <span style="font-size:3rem">🎯</span>
        <h2 style="color:#A78BFA;margin:0.5rem 0">InfluMatch.jo</h2>
        <p style="color:#94A3B8;font-size:0.9rem">{'منصة التسويق عبر المؤثرين في الأردن' if lang=='ar' else 'Jordan Influencer Marketing Platform'}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([t("login"), t("register")])

    with tab1:
        with st.form("login_form"):
            email = st.text_input(t("email"), placeholder="you@example.com")
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login"), use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Please fill all fields / يرجى ملء جميع الحقول")
                else:
                    status, resp = api_post("/api/auth/login",
                        data={"username": email, "password": password})
                    if status == 200:
                        st.session_state["token"] = resp.get("access_token")
                        # Fetch /me
                        from ..utils.api_client import api_get
                        me = api_get("/api/auth/me")
                        if me:
                            st.session_state["user"] = me
                            st.session_state["role"] = me.get("role", "merchant")
                            st.session_state["page"] = "dashboard"
                            st.success(f"Welcome {me.get('full_name', '')}!")
                            st.rerun()
                    else:
                        detail = resp.get("detail", "Login failed")
                        st.error(f"❌ {detail}")

    with tab2:
        with st.form("register_form"):
            full_name = st.text_input(t("full_name"), placeholder="محمد أسامة / Mohammad Osama")
            email = st.text_input(t("email"), placeholder="you@example.com")
            password = st.text_input(t("password"), type="password")
            role = st.selectbox(t("role"), ["merchant", "influencer"])
            submitted = st.form_submit_button(t("register"), use_container_width=True)
            if submitted:
                if not all([full_name, email, password]):
                    st.error("Please fill all fields / يرجى ملء جميع الحقول")
                else:
                    status, resp = api_post("/api/auth/register", json={
                        "full_name": full_name, "email": email,
                        "password": password, "role": role
                    })
                    if status in (200, 201):
                        st.success("✅ Account created! Please login. / تم إنشاء الحساب، يرجى تسجيل الدخول")
                    else:
                        detail = resp.get("detail", "Registration failed")
                        st.error(f"❌ {detail}")
''')

# ── frontend/pages/home_page.py ─────────────────────────────────────────────
w("frontend/pages/home_page.py", '''"""Landing / Home page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t

def render_home():
    lang = st.session_state.get("lang", "ar")

    # Hero Section
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem 2rem;background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(109,40,217,0.05));
                border-radius:16px;margin-bottom:2rem;border:1px solid rgba(124,58,237,0.2)">
        <div style="font-size:4rem;margin-bottom:0.5rem">🎯</div>
        <h1 style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#A78BFA,#7C3AED);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 0.5rem">
            InfluMatch.jo
        </h1>
        <p style="font-size:1.1rem;color:#94A3B8;max-width:600px;margin:0 auto 1.5rem">
            {'منصة تسويق ذكية تربط التجار بالمؤثرين في الأردن — مدعومة بالذكاء الاصطناعي ARIA' if lang=='ar'
             else 'AI-Powered Influencer Marketing for Jordan — Connecting Merchants & Creators'}
        </p>
        <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
            <span style="background:rgba(124,58,237,0.2);color:#A78BFA;padding:0.3rem 0.9rem;border-radius:99px;font-size:0.82rem">🤖 ARIA Score</span>
            <span style="background:rgba(16,185,129,0.2);color:#10B981;padding:0.3rem 0.9rem;border-radius:99px;font-size:0.82rem">🔒 Smart Escrow</span>
            <span style="background:rgba(245,158,11,0.2);color:#F59E0B;padding:0.3rem 0.9rem;border-radius:99px;font-size:0.82rem">📄 AI Contracts</span>
            <span style="background:rgba(59,130,246,0.2);color:#93C5FD;padding:0.3rem 0.9rem;border-radius:99px;font-size:0.82rem">💎 Loyalty</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("🏢", "Merchants", "150+"),
        ("⭐", "Influencers", "500+"),
        ("📢", "Campaigns", "1,200+"),
        ("💰", "JOD Processed", "250K+"),
    ]
    for col, (icon, label, val) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.8rem">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown(f"### {'كيف يعمل InfluMatch؟' if lang=='ar' else 'How InfluMatch Works'}")
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("1️⃣", "Create Campaign", "أنشئ حملتك"),
        ("2️⃣", "AI Matching", "مطابقة ذكية"),
        ("3️⃣", "Smart Escrow", "ضمان مالي"),
        ("4️⃣", "Verified Results", "نتائج موثوقة"),
    ]
    for col, (num, en, ar) in zip([c1, c2, c3, c4], steps):
        with col:
            st.markdown(f"""
            <div class="aria-card" style="text-align:center">
                <div style="font-size:2rem">{num}</div>
                <div style="font-weight:600;margin:0.3rem 0">{en}</div>
                <div style="font-size:0.8rem;color:#94A3B8">{ar}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🚀 Get Started as Merchant / ابدأ كتاجر", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
    with col_b:
        if st.button("⭐ Join as Influencer / انضم كمؤثر", use_container_width=True):
            st.session_state["page"] = "login"
            st.rerun()
''')

# ── frontend/pages/merchant_dashboard.py ───────────────────────────────────
w("frontend/pages/merchant_dashboard.py", '''"""Merchant Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post
from ..utils.i18n import t
from ..components.cards.campaign_card import render_campaign_card

def render():
    lang = st.session_state.get("lang", "ar")
    user = st.session_state.get("user", {})

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1.5rem">
        <span style="font-size:2rem">🏢</span>
        <div>
            <h2 style="margin:0;color:#A78BFA">{'لوحة تحكم التاجر' if lang=='ar' else "Merchant Dashboard"}</h2>
            <p style="margin:0;color:#64748B;font-size:0.85rem">{user.get('full_name','') if user else ''}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    merchant = api_get("/api/merchants/me") or {}
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("💰", f"{merchant.get('total_spent_jod',0):,.0f} JOD", "Total Spent / إجمالي الإنفاق"),
        ("💎", str(merchant.get("loyalty_points", 0)), "Points / النقاط"),
        ("📢", str(merchant.get("total_campaigns", 0)), "Campaigns / الحملات"),
        ("⭐", str(merchant.get("active_campaigns", 0)), "Active / نشط"),
    ]
    for col, (icon, val, lbl) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # My Campaigns
    tab1, tab2 = st.tabs(["📢 My Campaigns / حملاتي", "➕ New Campaign / حملة جديدة"])

    with tab1:
        campaigns = api_get("/api/campaigns") or []
        if not campaigns:
            st.info("No campaigns yet. Create your first! / لا توجد حملات بعد. أنشئ حملتك الأولى!")
        else:
            for c in campaigns[:10]:
                render_campaign_card(c)

    with tab2:
        _render_create_campaign(lang)


def _render_create_campaign(lang):
    with st.form("new_campaign_form"):
        st.markdown(f"#### {'إنشاء حملة جديدة' if lang=='ar' else 'Create New Campaign'}")
        title_en = st.text_input("Title (English)", placeholder="Ramadan Special Campaign")
        title_ar = st.text_input("العنوان (عربي)", placeholder="حملة رمضان الخاصة")
        desc_en = st.text_area("Description (English)", height=80)
        desc_ar = st.text_area("الوصف (عربي)", height=80)
        col1, col2 = st.columns(2)
        with col1:
            niche = st.selectbox("Niche / التخصص", [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
            total_budget = st.number_input("Budget (JOD) / الميزانية", min_value=50.0, value=500.0, step=50.0)
        with col2:
            budget_per_influencer = st.number_input("Per Influencer (JOD)", min_value=10.0, value=100.0, step=10.0)
            min_followers = st.number_input("Min Followers", min_value=1000, value=5000, step=1000)

        submitted = st.form_submit_button("🚀 Launch Campaign / إطلاق الحملة", use_container_width=True)
        if submitted:
            if not title_en and not title_ar:
                st.error("Title required / العنوان مطلوب")
            else:
                status, resp = api_post("/api/campaigns", json={
                    "title_en": title_en, "title_ar": title_ar,
                    "description_en": desc_en, "description_ar": desc_ar,
                    "niche": niche, "total_budget": total_budget,
                    "budget_per_influencer": budget_per_influencer,
                    "min_followers": int(min_followers)
                })
                if status in (200, 201):
                    st.success(f"✅ Campaign created! / تم إنشاء الحملة!")
                    st.rerun()
                else:
                    st.error(f"❌ {resp.get('detail', 'Error')}")
''')

# ── frontend/pages/influencer_dashboard.py ─────────────────────────────────
w("frontend/pages/influencer_dashboard.py", '''"""Influencer Dashboard"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t

TIER_META = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render():
    lang = st.session_state.get("lang", "ar")
    user = st.session_state.get("user", {})

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1.5rem">
        <span style="font-size:2rem">⭐</span>
        <div>
            <h2 style="margin:0;color:#A78BFA">{'لوحة تحكم المؤثر' if lang=='ar' else 'Influencer Dashboard'}</h2>
            <p style="margin:0;color:#64748B;font-size:0.85rem">{user.get('full_name','') if user else ''}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    inf = api_get("/api/influencers/me") or {}
    tier = inf.get("aria_tier", "UNRANKED")
    icon, bg, fg = TIER_META.get(tier, TIER_META["UNRANKED"])
    score = inf.get("aria_score", 0)

    # ARIA Score hero card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(109,40,217,0.1));
                border:1px solid rgba(124,58,237,0.3);border-radius:16px;padding:1.5rem;
                text-align:center;margin-bottom:1.5rem">
        <div style="font-size:0.8rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em">ARIA Score</div>
        <div style="font-size:4rem;font-weight:800;color:#A78BFA;line-height:1.1">{score:.1f}</div>
        <span style="background:{bg};color:{fg};padding:0.3rem 1rem;border-radius:99px;
                     font-size:0.8rem;font-weight:700">{icon} {tier}</span>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("📸", f"{inf.get('instagram_followers',0):,}", "Instagram"),
        ("🎵", f"{inf.get('tiktok_followers',0):,}", "TikTok"),
        ("📊", f"{inf.get('instagram_engagement_rate',0):.1f}%", "Engagement"),
        ("✅", str(inf.get("campaigns_completed", 0)), "Completed"),
    ]
    for col, (icon2, val, lbl) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon2}</div>
                <div class="metric-value" style="font-size:1.5rem">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Score breakdown
    if score > 0:
        st.markdown(f"#### {'تفاصيل نقاط ARIA' if lang=='ar' else 'ARIA Score Breakdown'}")
        dims = [
            ("🔥 Engagement", inf.get("engagement_score", 0), 30),
            ("🛡️ Authenticity", inf.get("authenticity_score", 0), 25),
            ("🎨 Content Quality", inf.get("engagement_score", 0) * 0.8, 20),
            ("⏱️ Reliability", inf.get("delivery_score", 0), 15),
            ("🎯 Relevance", inf.get("relevance_score", 0), 10),
        ]
        for label, raw, weight in dims:
            normalized = min(100, raw)
            weighted = (normalized / 100) * weight
            st.markdown(f"**{label}** — {weighted:.1f}/{weight}")
            st.progress(normalized / 100)

    # Available Campaigns
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### {'الحملات المتاحة' if lang=='ar' else 'Available Campaigns'}")
    campaigns = api_get("/api/campaigns") or []
    for c in campaigns[:5]:
        with st.container():
            status = c.get("status", "")
            if status in ("active", "draft"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="aria-card" style="margin-bottom:0.3rem">
                        <b>{c.get('title_en') or c.get('title_ar','')}</b> &nbsp;
                        <span style="color:#94A3B8;font-size:0.82rem">· {c.get('niche','—')} · {c.get('budget_per_influencer',0):.0f} JOD</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.button("Apply ✉️", key=f"apply_{c.get('id',0)}", use_container_width=True)
''')

# ── frontend/pages/discover_page.py ─────────────────────────────────────────
w("frontend/pages/discover_page.py", '''"""Discover Influencers page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t
from ..components.cards.influencer_card import render_influencer_card

def render():
    lang = st.session_state.get("lang", "ar")
    st.markdown(f"## {'🔍 اكتشف المؤثرين' if lang=='ar' else '🔍 Discover Influencers'}")

    # Filters
    with st.expander(f"{'🔧 الفلاتر' if lang=='ar' else '🔧 Filters'}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            niche = st.selectbox("Niche", ["All", "Fashion", "Food", "Tech", "Beauty",
                                            "Fitness", "Travel", "Gaming", "Education"])
        with col2:
            city = st.selectbox("City", ["All", "Amman", "Zarqa", "Irbid", "Aqaba"])
        with col3:
            min_score = st.slider("Min ARIA Score", 0, 100, 0)
        with col4:
            tier = st.selectbox("Tier", ["All", "PLATINUM", "GOLD", "SILVER", "BRONZE"])

    params = {}
    if niche != "All": params["niche"] = niche
    if city != "All": params["city"] = city
    if min_score > 0: params["min_score"] = min_score
    if tier != "All": params["tier"] = tier

    influencers = api_get("/api/influencers", params=params) or []

    if not influencers:
        st.info("No influencers found / لا يوجد مؤثرون مطابقون")
        return

    st.markdown(f"**{len(influencers)} influencers found**")

    for inf in influencers:
        invited = render_influencer_card(inf, show_invite=True)
        if invited:
            st.success(f"✅ Invite sent to @{inf.get('instagram_handle', '')}")
''')

# ── frontend/pages/wallet_page.py ───────────────────────────────────────────
w("frontend/pages/wallet_page.py", '''"""Loyalty Wallet page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t

TIER_INFO = {
    "BRONZE": ("🥉", 0, 999, "rgba(180,83,9,0.2)", "#b45309"),
    "SILVER": ("🥈", 1000, 4999, "rgba(156,163,175,0.2)", "#9ca3af"),
    "GOLD":   ("🥇", 5000, 19999, "rgba(251,191,36,0.2)", "#fbbf24"),
    "PLATINUM":("🏆", 20000, 999999, "rgba(229,231,235,0.2)", "#e5e7eb"),
}

def render():
    lang = st.session_state.get("lang", "ar")
    wallet = api_get("/api/wallet/me")

    if not wallet:
        st.info("Wallet not found / المحفظة غير موجودة")
        return

    points = wallet.get("points_balance", 0)
    tier = wallet.get("tier", "BRONZE")
    icon, low, high, bg, fg = TIER_INFO.get(tier, TIER_INFO["BRONZE"])
    total_earned = wallet.get("total_points_earned", 0)
    total_redeemed = wallet.get("total_points_redeemed", 0)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{bg},{bg.replace('0.2','0.05')});
                border:1px solid {fg}40;border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3rem">{icon}</div>
        <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em">{t('tier')}</div>
        <div style="font-size:2rem;font-weight:800;color:{fg}">{tier}</div>
        <div style="font-size:3.5rem;font-weight:900;color:#A78BFA;margin:0.5rem 0">{points:,}</div>
        <div style="color:#94A3B8;font-size:0.85rem">{t('points')} · {points/100:.2f} JOD value</div>
    </div>
    """, unsafe_allow_html=True)

    # Next tier progress
    next_tiers = {"BRONZE": "SILVER", "SILVER": "GOLD", "GOLD": "PLATINUM", "PLATINUM": None}
    next_tier = next_tiers.get(tier)
    if next_tier:
        next_icon, next_low, _, _, next_fg = TIER_INFO[next_tier]
        needed = next_low - points
        progress = min(1.0, points / next_low)
        st.markdown(f"**Progress to {next_icon} {next_tier}** — {needed:,} points needed")
        st.progress(progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_earned:,}</div>
            <div class="metric-label">Total Earned</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_redeemed:,}</div>
            <div class="metric-label">Total Redeemed</div></div>""", unsafe_allow_html=True)
    with c3:
        jod_val = points / 100
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{jod_val:.1f} JOD</div>
            <div class="metric-label">Cash Value</div></div>""", unsafe_allow_html=True)

    # Transactions
    st.markdown(f"#### {'المعاملات الأخيرة' if lang=='ar' else 'Recent Transactions'}")
    txns = wallet.get("transactions", [])
    if not txns:
        st.info("No transactions yet / لا توجد معاملات بعد")
    else:
        for tx in txns[-10:]:
            tx_type = tx.get("transaction_type", "")
            pts = tx.get("points", 0)
            sign = "+" if tx_type in ("earned", "bonus", "referral") else "-"
            color = "#10B981" if sign == "+" else "#EF4444"
            st.markdown(f"""
            <div class="aria-card" style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem">
                <div>
                    <span style="font-weight:600">{tx.get('event','—')}</span>
                    <span style="font-size:0.75rem;color:#94A3B8;margin-left:0.5rem">{tx_type}</span>
                </div>
                <span style="color:{color};font-weight:700">{sign}{pts:,} pts</span>
            </div>
            """, unsafe_allow_html=True)
''')

# ── frontend/pages/god_mode_page.py ─────────────────────────────────────────
w("frontend/pages/god_mode_page.py", '''"""God Mode Admin Dashboard"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.session import get_role

def render():
    if get_role() != "admin":
        st.error("⛔ Access Denied — Admin only / وصول مرفوض")
        return

    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1.5rem">
        <span style="font-size:2.5rem">🛡️</span>
        <div>
            <h2 style="margin:0;color:#EF4444">God Mode Dashboard</h2>
            <p style="margin:0;color:#64748B;font-size:0.82rem">Full system access — ARIA Admin Console</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    stats = api_get("/api/admin/stats") or {}

    # System KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        ("👥", stats.get("total_users", 0), "Total Users"),
        ("🏢", stats.get("total_merchants", 0), "Merchants"),
        ("⭐", stats.get("total_influencers", 0), "Influencers"),
        ("📢", stats.get("total_campaigns", 0), "Campaigns"),
        ("💰", f"{stats.get('total_escrow_jod', 0):,.0f}", "JOD Escrow"),
    ]
    for col, (icon, val, lbl) in zip([c1, c2, c3, c4, c5], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.4rem">{icon}</div>
                <div class="metric-value" style="font-size:1.6rem">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Users", "📢 Campaigns", "⚖️ Disputes"])

    with tab1:
        users = api_get("/api/admin/users") or []
        if users:
            import pandas as pd
            df = pd.DataFrame([{
                "ID": u.get("id"), "Name": u.get("full_name"),
                "Email": u.get("email"), "Role": u.get("role"),
                "Active": u.get("is_active"),
            } for u in users])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

    with tab2:
        campaigns = api_get("/api/campaigns") or []
        if campaigns:
            import pandas as pd
            df = pd.DataFrame([{
                "ID": c.get("id"),
                "Title": c.get("title_en") or c.get("title_ar"),
                "Status": c.get("status"),
                "Budget": f"{c.get('total_budget',0):.0f} JOD",
                "Niche": c.get("niche"),
            } for c in campaigns])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No campaigns found")

    with tab3:
        disputes = [c for c in (api_get("/api/campaigns") or []) if c.get("status") == "disputed"]
        if disputes:
            for d in disputes:
                st.markdown(f"""
                <div class="aria-card" style="border-left:3px solid #EF4444">
                    <b>{d.get('title_en') or d.get('title_ar','')}</b>
                    <span style="color:#EF4444;margin-left:0.5rem">⚠️ DISPUTED</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No active disputes")
''')

# ── frontend/app.py ─────────────────────────────────────────────────────────
w("frontend/__init__.py", "")
w("frontend/app.py", '''"""
InfluMatch.jo — Streamlit Frontend
Module 12 | Entry Point
Run: streamlit run frontend/app.py --server.port 8501
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="InfluMatch.jo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "InfluMatch.jo — AI Influencer Platform for Jordan"}
)

from frontend.utils.session import init_session, is_logged_in, get_role
from frontend.utils.i18n import t
from frontend.components.sidebar import render_sidebar
from frontend.components.navbar import render_navbar
from frontend.components.chatbot.floating_widget import render_chatbot
from frontend.pages.home_page import render_home
from frontend.pages.auth_page import render_login
from frontend.pages.merchant_dashboard import render as render_merchant
from frontend.pages.influencer_dashboard import render as render_influencer
from frontend.pages.discover_page import render as render_discover
from frontend.pages.wallet_page import render as render_wallet
from frontend.pages.god_mode_page import render as render_god_mode

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "css", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Init session
init_session()

# Sidebar
render_sidebar()

# ARIA Chatbot (floating)
render_chatbot()

# Router
page = st.session_state.get("page", "home")
role = get_role()
logged_in = is_logged_in()

if page == "home":
    render_navbar()
    render_home()
elif page in ("login", "register"):
    render_login()
elif page == "dashboard":
    if role == "merchant":
        render_merchant()
    elif role == "influencer":
        render_influencer()
    elif role == "admin":
        render_god_mode()
    else:
        render_home()
elif page == "discover":
    render_discover()
elif page == "wallet":
    render_wallet()
elif page == "god_mode":
    render_god_mode()
elif page in ("campaigns", "my_campaigns"):
    if role == "merchant":
        render_merchant()
    else:
        render_influencer()
else:
    render_home()
''')

# ── scripts/init_db.py ───────────────────────────────────────────────────────
w("../scripts/init_db.py", '''"""Initialize InfluMatch database"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

async def main():
    from influmatch.backend.core.database import init_db
    from influmatch.backend.core.config import get_settings
    settings = get_settings()
    print(f"[ARIA] Initializing DB: {settings.database_url}")
    await init_db()
    print("[ARIA] ✅ Database initialized successfully")

asyncio.run(main())
''')

# ── scripts/seed_rag.py ──────────────────────────────────────────────────────
w("../scripts/seed_rag.py", '''"""Seed RAG vector store with Jordan market documents"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

CONTRACTS_AR = """
عقد خدمات التسويق عبر المؤثرين
بموجب هذا العقد، يلتزم المؤثر بتقديم المحتوى الإعلاني المتفق عليه في المدة المحددة.
يخضع هذا العقد لأحكام قانون المعاملات الإلكترونية الأردني رقم 15 لسنة 2015.
يتم الدفع عبر منصة InfluMatch.jo بعد الموافقة على المحتوى والتحقق منه.
معدل ضريبة القيمة المضافة: 16% وفقاً للتشريعات الأردنية.
في حال النزاع، يتم اللجوء إلى التحكيم وفقاً لأحكام قانون التحكيم الأردني.
"""

CONTRACTS_EN = """
Influencer Marketing Service Agreement
The Influencer agrees to deliver agreed content within the specified timeline.
This contract is governed by Jordan Electronic Transactions Law No. 15 of 2015.
Payment is processed via InfluMatch.jo escrow after content approval and verification.
VAT rate: 16% as per Jordanian tax regulations.
Disputes resolved through arbitration per Jordanian Arbitration Law.
"""

POLICIES_AR = """
سياسة InfluMatch.jo للمؤثرين - السوق الأردني
1. يجب أن يكون المحتوى أصيلاً وغير مضلل
2. الإفصاح الإلزامي عن المحتوى المدفوع (شراكة برعاية)
3. الالتزام بقوانين حماية المستهلك الأردنية
4. حظر المحتوى المسيء أو المخالف للقيم العامة
5. معايير الجودة: دقة عالية، محتوى واضح، تفاعل حقيقي
"""

POLICIES_EN = """
InfluMatch.jo Influencer Policy - Jordan Market
1. Content must be authentic and non-deceptive
2. Mandatory disclosure of paid content (#ad #sponsored)
3. Compliance with Jordan Consumer Protection Law
4. No offensive or culturally inappropriate content
5. Quality standards: high resolution, clear messaging, genuine engagement
"""

def seed():
    try:
        from influmatch.backend.services.rag.vector_store import InfluMatchVectorStore
        store = InfluMatchVectorStore()
        store.add_document("contracts", CONTRACTS_AR, {"lang": "ar", "type": "contract_template"})
        store.add_document("contracts", CONTRACTS_EN, {"lang": "en", "type": "contract_template"})
        store.add_document("policies", POLICIES_AR, {"lang": "ar", "type": "policy"})
        store.add_document("policies", POLICIES_EN, {"lang": "en", "type": "policy"})
        print("[ARIA] ✅ RAG vector store seeded with Jordan market documents")
    except Exception as e:
        print(f"[ARIA] ⚠️  RAG seed warning: {e}")

seed()
''')

# ── scripts/start_all.py ─────────────────────────────────────────────────────
w("../scripts/start_all.py", '''"""Start InfluMatch.jo — API + Frontend"""
import subprocess, sys, os, time, webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFLUMATCH = os.path.join(ROOT, "influmatch")

print("=" * 60)
print("  🎯 InfluMatch.jo — Starting Platform")
print("=" * 60)

# 1. Init DB
print("\\n[1/3] Initializing database...")
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "init_db.py")], check=False)

# 2. Start FastAPI
print("\\n[2/3] Starting FastAPI backend (port 8000)...")
api = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app",
     "--reload", "--host", "0.0.0.0", "--port", "8000"],
    cwd=INFLUMATCH
)

time.sleep(3)

# 3. Start Streamlit
print("\\n[3/3] Starting Streamlit frontend (port 8501)...")
ui = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
     "--server.port", "8501", "--server.headless", "true"],
    cwd=INFLUMATCH
)

time.sleep(2)
print("\\n✅ InfluMatch.jo is running!")
print("   📡 API:      http://localhost:8000")
print("   📚 API Docs: http://localhost:8000/docs")
print("   🌐 Frontend: http://localhost:8501")
print("\\nPress Ctrl+C to stop.")

try:
    api.wait()
except KeyboardInterrupt:
    print("\\n[ARIA] Shutting down...")
    api.terminate()
    ui.terminate()
''')

# ── docker-compose.yml ──────────────────────────────────────────────────────
w("../docker-compose.yml", """version: '3.9'

services:
  api:
    build:
      context: ./influmatch
      dockerfile: Dockerfile
    container_name: influmatch_api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./influmatch.db
      - DEBUG=false
    volumes:
      - ./influmatch:/app
      - influmatch_data:/app/data
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./influmatch
      dockerfile: Dockerfile.frontend
    container_name: influmatch_ui
    ports:
      - "8501:8501"
    environment:
      - API_BASE=http://api:8000
    depends_on:
      - api
    command: streamlit run frontend/app.py --server.port 8501 --server.headless true

volumes:
  influmatch_data:
""")

# ── Dockerfile ──────────────────────────────────────────────────────────────
w("Dockerfile", """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

w("Dockerfile.frontend", """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt streamlit

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"]
""")

# ── backend/tests ────────────────────────────────────────────────────────────
w("backend/tests/__init__.py", "")
w("backend/tests/conftest.py", '''"""Test configuration — async in-memory SQLite"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

class TestBase(DeclarativeBase):
    pass

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    from influmatch.backend.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client():
    from influmatch.backend.main import app
    from influmatch.backend.core.database import get_db, init_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
''')

w("backend/tests/test_health.py", '''"""Health check tests"""
import pytest

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_api_docs(client):
    resp = await client.get("/docs")
    assert resp.status_code == 200
''')

w("backend/tests/test_auth.py", '''"""Auth endpoint tests"""
import pytest

TEST_USER = {
    "full_name": "Test Merchant",
    "email": "test_merchant@influmatch.jo",
    "password": "SecurePass123!",
    "role": "merchant"
}

@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/api/auth/register", json=TEST_USER)
    assert resp.status_code in (200, 201, 400)  # 400 if already exists

@pytest.mark.asyncio
async def test_login(client):
    # Register first
    await client.post("/api/auth/register", json=TEST_USER)
    # Login
    resp = await client.post("/api/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_me_endpoint(client):
    await client.post("/api/auth/register", json=TEST_USER)
    login = await client.post("/api/auth/login", data={
        "username": TEST_USER["email"],
        "password": TEST_USER["password"]
    })
    token = login.json().get("access_token")
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == TEST_USER["email"]
''')

print("\nM12 ALL FRONTEND FILES WRITTEN OK")
print("Scripts, Docker, Tests — COMPLETE")
