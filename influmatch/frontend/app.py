"""
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
from frontend._pages.home_page import render_home
from frontend._pages.auth_page import render_login
from frontend._pages.merchant_dashboard import render as render_merchant
from frontend._pages.influencer_dashboard import render as render_influencer
from frontend._pages.discover_page import render as render_discover
from frontend._pages.wallet_page import render as render_wallet
from frontend._pages.god_mode_page import render as render_god_mode

# ── Helper renderers ─────────────────────────────────────────

def _render_escrow_page():
    from frontend.utils.api_client import api_get, api_post
    st.markdown("## 💰 Escrow Tracker / متتبع الضمان")
    campaigns = api_get("/api/campaigns/") or []
    if not campaigns:
        st.info("No campaigns found. / لا توجد حملات.")
        return
    for c in campaigns:
        cid = c.get("id")
        title = c.get("title_en") or c.get("title_ar", "—")
        status = c.get("status", "")
        with st.expander(f"📢 {title} — {status.upper()}"):
            escrow = api_get(f"/api/escrow/{cid}")
            if escrow:
                col1, col2, col3 = st.columns(3)
                col1.metric("Gross Amount", f"{escrow.get('gross_amount',0):,.0f} JOD")
                col2.metric("Net Amount",   f"{escrow.get('net_amount',0):,.0f} JOD")
                col3.metric("Status",       escrow.get("status", "—").upper())
                if escrow.get("auto_release_at"):
                    st.caption(f"Auto-release: {escrow.get('auto_release_at')}")
                if escrow.get("status") in ("funded", "in_progress", "under_review"):
                    bcol1, bcol2 = st.columns(2)
                    if bcol1.button("✅ Release Funds", key=f"rel_{cid}"):
                        s, r = api_post(f"/api/escrow/{escrow.get('id')}/release", json={})
                        if s == 200:
                            st.success("Funds released!")
                            st.rerun()
                        else:
                            st.error(r.get("detail"))
                    if bcol2.button("⚠️ Raise Dispute", key=f"dis_{cid}"):
                        reason = st.text_input("Dispute reason", key=f"dreason_{cid}")
                        if reason:
                            s, r = api_post(f"/api/escrow/{escrow.get('id')}/dispute",
                                            json={"reason": reason, "raised_by_id": 1})
                            st.warning(r.get("message", "Dispute raised"))
            elif status == "draft":
                st.info("Escrow not yet funded. Activate campaign to lock funds.")
                if st.button("🔒 Fund Escrow", key=f"fund_{cid}"):
                    s, r = api_post("/api/escrow/fund", json={
                        "campaign_id": cid,
                        "merchant_id": c.get("merchant_id", 1),
                        "amount_jod" : c.get("total_budget", 0)
                    })
                    if s == 200:
                        st.success(f"Funded: {r.get('gross_amount')} JOD locked")
                        st.rerun()
                    else:
                        st.error(r.get("detail"))
            else:
                st.info("No escrow transaction found for this campaign.")


def _render_contracts_page():
    from frontend.utils.api_client import api_get, api_post
    st.markdown("## 📄 Smart Contracts / العقود الذكية (ARIA RAG)")
    lang = st.session_state.get("lang", "ar")

    campaigns = api_get("/api/campaigns/") or []
    active = [c for c in campaigns if c.get("status") in ("active", "in_progress", "draft")]

    if not active:
        st.info("No campaigns available for contract generation.")
        return

    campaign_titles = {c["id"]: (c.get("title_en") or c.get("title_ar","")) for c in active}
    selected_id = st.selectbox("Select Campaign", list(campaign_titles.keys()),
                               format_func=lambda x: campaign_titles[x])
    campaign = next(c for c in active if c["id"] == selected_id)

    col1, col2 = st.columns(2)
    merchant_name  = col1.text_input("Merchant Name", value="InfluMatch Merchant")
    influencer_name = col2.text_input("Influencer Name", value="Jordan Influencer")
    contract_lang  = st.radio("Contract Language", ["ar", "en"],
                              format_func=lambda x: "🇯🇴 Arabic" if x == "ar" else "🇬🇧 English",
                              horizontal=True)

    if st.button("⚡ Generate Smart Contract via ARIA RAG", type="primary", use_container_width=True):
        with st.spinner("ARIA is generating your contract..."):
            status, resp = api_post("/api/contracts/generate", json={
                "merchant_name"   : merchant_name,
                "influencer_name" : influencer_name,
                "campaign_details": {
                    "title"      : campaign_titles[selected_id],
                    "budget"     : campaign.get("total_budget"),
                    "niche"      : campaign.get("niche"),
                    "start_date" : str(campaign.get("start_date","TBD")),
                },
                "language": contract_lang
            })
        if status == 200:
            st.success(f"✅ Contract generated | Sources used: {resp.get('rag_sources_used')}")
            st.text_area("📄 Smart Contract", resp.get("contract",""), height=400)
            st.download_button("⬇️ Download Contract", resp.get("contract",""),
                               file_name=f"contract_{selected_id}.txt")
        else:
            st.error(f"Generation failed: {resp.get('detail')}")

    st.divider()
    st.markdown("### 💬 Policy Q&A / أسئلة السياسات")
    q = st.text_input("Ask about platform policies / اسأل عن سياسات المنصة",
                       placeholder="What is the VAT rate? / ما هي نسبة ضريبة القيمة المضافة؟")
    if q and st.button("🤖 Ask ARIA"):
        status, resp = api_post(f"/api/contracts/policy-qa?question={q}&language={lang}", json={})
        if status == 200:
            st.info(f"**ARIA:** {resp.get('answer','')}")


def _render_settings_page():
    st.markdown("## ⚙️ Settings / الإعدادات")
    user = st.session_state.get("user", {})
    role = get_role()

    st.markdown("### 👤 Profile / الملف الشخصي")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Email", value=user.get("email", ""), disabled=True, key="set_email")
        st.text_input("Username", value=user.get("username", ""), disabled=True, key="set_uname")
    with col2:
        st.text_input("Full Name (EN)", value=user.get("full_name_en", ""), key="set_fname_en")
        st.text_input("الاسم بالعربي", value=user.get("full_name_ar", ""), key="set_fname_ar")

    st.markdown("---")
    lang = st.session_state.get("lang", "ar")
    new_lang = st.radio("Interface Language / لغة الواجهة", ["ar", "en"],
                        index=0 if lang == "ar" else 1,
                        format_func=lambda x: "🇯🇴 العربية" if x == "ar" else "🇬🇧 English",
                        horizontal=True, key="lang_radio")
    if new_lang != lang:
        st.session_state["lang"] = new_lang
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout / تسجيل الخروج", type="secondary", use_container_width=True):
        from frontend.utils.session import logout
        logout()


# ── App bootstrap ────────────────────────────────────────────

# Inline critical sidebar-force CSS — must fire before everything else
st.markdown("""
<style>
/* CRITICAL: never hide the sidebar or its toggle */
section[data-testid="stSidebar"]       { display: flex !important; visibility: visible !important; min-width: 240px; }
div[data-testid="collapsedControl"]    { display: block !important; visibility: visible !important; }
#MainMenu                              { display: none !important; }
footer                                 { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Load full CSS theme
css_path = os.path.join(os.path.dirname(__file__), "assets", "css", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
render_sidebar()
render_chatbot()

page      = st.session_state.get("page", "home")
role      = get_role()
logged_in = is_logged_in()

# ── Router ───────────────────────────────────────────────────

if page == "home":
    render_navbar()
    render_home()

elif page in ("login", "register"):
    render_login()

elif page == "browse":
    render_discover()

elif page == "dashboard":
    if not logged_in:
        render_login()
    elif role == "merchant":
        render_merchant()
    elif role == "influencer":
        render_influencer()
    elif role == "admin":
        render_god_mode()
    else:
        render_home()

elif page in ("campaigns", "my_campaigns"):
    if not logged_in:
        render_login()
    elif role == "merchant":
        render_merchant()
    else:
        render_influencer()

elif page == "discover":
    render_discover()

elif page == "wallet":
    if not logged_in:
        render_login()
    else:
        render_wallet()

elif page == "earnings":
    if not logged_in:
        render_login()
    else:
        render_wallet()

elif page == "escrow":
    if not logged_in:
        render_login()
    else:
        _render_escrow_page()

elif page == "contracts":
    if not logged_in:
        render_login()
    else:
        _render_contracts_page()

elif page in ("settings", "profile"):
    if not logged_in:
        render_login()
    else:
        _render_settings_page()

elif page in ("god_mode", "users", "disputes", "analytics"):
    if not logged_in or role != "admin":
        st.error("⛔ Admin access required / صلاحية المسؤول مطلوبة")
        render_login()
    else:
        render_god_mode()

else:
    render_home()
