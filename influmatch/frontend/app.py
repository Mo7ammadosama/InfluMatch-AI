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
from frontend._pages.open_campaigns_page import render as render_open_campaigns
from frontend._pages.wallet_page import render as render_wallet
from frontend._pages.god_mode_page import render as render_god_mode
from frontend._pages.bookings_page import render as render_bookings

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
    lang = st.session_state.get("lang", "ar")

    # ── Header Banner ──────────────────────────────────────────
    st.markdown("""
    <div class="merchant-banner">
      <div style="display:flex;align-items:center;gap:1.2rem">
        <div style="font-size:2.8rem">📄</div>
        <div>
          <div style="font-size:1.4rem;font-weight:800;color:#f59e0b">
            العقود الذكية / Smart Contracts
          </div>
          <div style="color:#a0a0b0;font-size:0.85rem;margin-top:0.2rem">
            مدعوم بـ ARIA RAG · قانون الأردن · ضريبة 16%
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    campaigns = api_get("/api/campaigns/") or []
    active = [c for c in campaigns if c.get("status") in ("active", "in_progress", "draft")]

    if not active:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem">
          <div style="font-size:3rem;margin-bottom:1rem">📋</div>
          <div style="color:#a0a0b0">لا توجد حملات نشطة لإنشاء عقد لها</div>
          <div style="color:#6b7280;font-size:0.8rem;margin-top:0.5rem">No active campaigns for contract generation</div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Contract Generator Card ────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;font-size:1.1rem;color:#f59e0b;margin-bottom:1.2rem">⚡ إنشاء عقد ذكي / Generate Smart Contract</div>', unsafe_allow_html=True)

    campaign_titles = {c["id"]: (c.get("title_en") or c.get("title_ar","")) for c in active}
    selected_id = st.selectbox("الحملة / Campaign", list(campaign_titles.keys()),
                               format_func=lambda x: campaign_titles[x])
    campaign = next(c for c in active if c["id"] == selected_id)

    col1, col2 = st.columns(2)
    merchant_name   = col1.text_input("اسم التاجر / Merchant Name", value="InfluMatch Merchant")
    influencer_name = col2.text_input("اسم المؤثر / Influencer Name", value="Jordan Influencer")
    contract_lang   = st.radio("لغة العقد / Contract Language", ["ar", "en"],
                               format_func=lambda x: "🇯🇴 العربية" if x == "ar" else "🇬🇧 English",
                               horizontal=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("⚡ إنشاء العقد عبر ARIA RAG", type="primary", use_container_width=True):
        with st.spinner("ARIA تُولّد العقد..."):
            status, resp = api_post("/api/contracts/generate", json={
                "merchant_name"   : merchant_name,
                "influencer_name" : influencer_name,
                "campaign_details": {
                    "campaign_id": selected_id,
                    "title"      : campaign_titles[selected_id],
                    "budget"     : campaign.get("total_budget"),
                    "niche"      : campaign.get("niche"),
                    "start_date" : str(campaign.get("start_date","TBD")),
                },
                "language": contract_lang
            })
        if status == 200:
            contract_id   = resp.get("contract_id")
            contract_text = resp.get("contract", "")
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(0,255,136,0.3)">
              <div style="color:#00ff88;font-weight:700;margin-bottom:0.5rem">
                ✅ تم إنشاء العقد #{contract_id} | المصادر المستخدمة: {resp.get('rag_sources_used', 0)}
              </div>
            </div>""", unsafe_allow_html=True)
            st.text_area("📄 نص العقد / Contract Text", contract_text, height=400)

            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    "⬇️ تحميل نص / Download TXT",
                    contract_text,
                    file_name=f"contract_{contract_id or selected_id}.txt",
                    use_container_width=True,
                )
            with dl_col2:
                if contract_id:
                    if st.button("📄 تحميل PDF", key="dl_pdf", use_container_width=True, type="primary"):
                        import httpx as _hx
                        token = st.session_state.get("token", "")
                        try:
                            r_pdf = _hx.get(
                                f"http://localhost:8000/api/contracts/{contract_id}/pdf",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=20,
                            )
                            if r_pdf.status_code == 200:
                                st.download_button(
                                    "⬇️ حفظ PDF",
                                    data=r_pdf.content,
                                    file_name=f"contract_{contract_id}.pdf",
                                    mime="application/pdf",
                                    key="save_pdf",
                                )
                            else:
                                st.error(f"PDF error {r_pdf.status_code}")
                        except Exception as _e:
                            st.error(f"PDF error: {_e}")
        else:
            err_msg = resp.get("detail", "") if isinstance(resp, dict) else str(resp)
            if any(k in err_msg.lower() for k in ["credit", "billing", "unavailable", "temporarily"]):
                st.markdown("""
                <div class="glass-card" style="border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.05)">
                  <div style="color:#f59e0b;font-weight:700">⚠️ خدمة ARIA غير متاحة مؤقتاً</div>
                  <div style="color:#a0a0b0;font-size:0.85rem;margin-top:0.5rem">
                    يرجى إضافة ANTHROPIC_API_KEY صالح في ملف .env ثم إعادة تشغيل السيرفر
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="glass-card" style="border-color:rgba(239,68,68,0.4);background:rgba(239,68,68,0.05)">
                  <div style="color:#ef4444;font-weight:700">❌ خطأ ({status})</div>
                  <div style="color:#a0a0b0;font-size:0.8rem;margin-top:0.3rem">{err_msg[:200]}</div>
                </div>""", unsafe_allow_html=True)

    # ── Policy Q&A Card ────────────────────────────────────────
    st.markdown('<div class="glass-card" style="margin-top:1.5rem">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;font-size:1rem;color:#8b5cf6;margin-bottom:1rem">💬 أسئلة السياسات / Policy Q&A</div>', unsafe_allow_html=True)
    q = st.text_input("اسأل ARIA عن سياسات المنصة",
                       placeholder="مثال: ما هي نسبة ضريبة القيمة المضافة؟ / What is the VAT rate?",
                       label_visibility="collapsed")
    if q and st.button("🤖 اسأل ARIA", use_container_width=True):
        s2, r2 = api_post(f"/api/contracts/policy-qa?question={q}&language={lang}", json={})
        if s2 == 200:
            st.markdown(f"""
            <div class="glass-card" style="border-color:rgba(139,92,246,0.3);background:rgba(139,92,246,0.05)">
              <div style="color:#8b5cf6;font-size:0.8rem;font-weight:600;margin-bottom:0.5rem">🤖 ARIA</div>
              <div style="color:#e0e0f0">{r2.get('answer','')}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("ARIA غير متاح حالياً / ARIA not available")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_booking_wizard():
    from frontend.utils.api_client import api_get, api_post
    inf = st.session_state.get("booking_influencer", {})
    if not inf:
        st.session_state["page"] = "discover"
        st.rerun()
        return

    handle = inf.get("instagram_handle") or inf.get("tiktok_handle") or "—"
    rate   = float(inf.get("rate_per_post") or 0)

    st.markdown(f"""
    <div class="merchant-banner">
      <div style="display:flex;align-items:center;gap:1rem">
        <div style="font-size:2.5rem">📅</div>
        <div>
          <div style="font-size:1.3rem;font-weight:700;color:#f59e0b">حجز @{handle}</div>
          <div style="color:#a0a0b0;font-size:0.85rem">Rate: {rate:.3f} JOD per post</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
      <div style="font-weight:700;margin-bottom:1rem;color:#f59e0b">رحلة الحجز / Booking Journey</div>
      <div class="booking-timeline">
        <div class="timeline-item active"><b style="color:#f59e0b">1. الحجز والدفع</b> <span style="color:#6b7280;font-size:0.8rem">— تجميد المبلغ في Escrow</span></div>
        <div class="timeline-item"><b style="color:#fff">2. تأكيد المؤثر</b> <span style="color:#6b7280;font-size:0.8rem">— المؤثر يقبل الحجز</span></div>
        <div class="timeline-item"><b style="color:#fff">3. تنفيذ الإعلان</b> <span style="color:#6b7280;font-size:0.8rem">— المؤثر يرفع المحتوى</span></div>
        <div class="timeline-item"><b style="color:#fff">4. مراجعة ARIA</b> <span style="color:#6b7280;font-size:0.8rem">— ذكاء اصطناعي يراجع</span></div>
        <div class="timeline-item"><b style="color:#fff">5. تحويل المبلغ</b> <span style="color:#6b7280;font-size:0.8rem">— تلقائي بعد القبول</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.form("booking_form"):
        brief = st.text_area(
            "وصف الإعلان المطلوب / Campaign Brief",
            placeholder="مثال: فيديو ريلز 60 ثانية يعرض منتج X مع كود خصم 20%...",
            height=100,
        )
        dc1, dc2 = st.columns(2)
        with dc1:
            agreed_rate = st.number_input("المبلغ المتفق عليه (JOD)", value=float(rate) or 1.0, min_value=1.0, step=1.0)
        with dc2:
            import datetime as _dt
            deadline = st.date_input("الموعد النهائي للنشر", value=_dt.date.today() + _dt.timedelta(days=14))
        deliverables = st.multiselect(
            "المطلوب",
            ["1 Reel", "1 Story", "3 Stories", "TikTok Video", "Instagram Post", "YouTube Short"],
            default=["1 Reel"],
        )
        campaigns   = api_get("/api/campaigns/") or []
        camp_opts   = {"بدون حملة محددة": None}
        camp_opts.update({c.get("title_en") or c.get("title_ar", "—"): c.get("id") for c in campaigns})
        sel_camp    = st.selectbox("ربط بحملة (اختياري)", list(camp_opts.keys()))

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💳 تأكيد الحجز وتجميد المبلغ", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("إلغاء", use_container_width=True)

        if cancelled:
            st.session_state.pop("booking_influencer", None)
            st.session_state["page"] = "discover"
            st.rerun()

        if submitted:
            if not brief.strip():
                st.error("اكتب وصف الإعلان المطلوب")
            else:
                s, r = api_post("/api/bookings/", json={
                    "influencer_id"  : inf.get("id"),
                    "agreed_rate_jod": round(agreed_rate, 3),
                    "brief"          : brief,
                    "deliverables"   : deliverables,
                    "deadline"       : deadline.isoformat(),
                    "campaign_id"    : camp_opts.get(sel_camp),
                })
                if s == 201:
                    st.success(
                        f"✅ تم الحجز بنجاح!\n\n"
                        f"💰 تم تجميد **{agreed_rate:.3f} JOD** في Escrow\n\n"
                        f"📋 رقم الحجز: #{r.get('booking_id')}\n\n"
                        f"⏳ بانتظار تأكيد @{handle}"
                    )
                    st.session_state.pop("booking_influencer", None)
                    st.balloons()
                else:
                    st.error(f"خطأ ({s}): {r.get('detail', '')}")


def _render_settings_page():
    from frontend.utils.api_client import api_patch
    st.markdown("## ⚙️ Settings / الإعدادات")
    user = st.session_state.get("user", {})
    role = get_role()
    lang = st.session_state.get("lang", "ar")

    st.markdown("### 👤 Profile / الملف الشخصي")
    with st.form("profile_update_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Email", value=user.get("email", ""), disabled=True, key="set_email")
            st.text_input("Username", value=user.get("username", ""), disabled=True, key="set_uname")
        with col2:
            fname_en = st.text_input("Full Name (EN)", value=user.get("full_name_en", ""), key="set_fname_en")
            fname_ar = st.text_input("الاسم بالعربي", value=user.get("full_name_ar", ""), key="set_fname_ar")
        phone = st.text_input("Phone / الهاتف", value=user.get("phone", ""), placeholder="+962...")
        if st.form_submit_button("💾 Save Profile / حفظ", use_container_width=True):
            s, r = api_patch("/api/auth/me", json={
                "full_name_en": fname_en or None,
                "full_name_ar": fname_ar or None,
                "phone"       : phone or None,
            })
            if s == 200:
                st.session_state["user"] = r
                st.success("Profile updated! / تم تحديث الملف الشخصي")
                st.rerun()
            else:
                st.error(r.get("detail", "Update failed"))

    # Role-specific profile updates
    if role == "merchant":
        st.markdown("---")
        st.markdown("### 🏪 Business Profile / الملف التجاري")
        m = api_patch  # just reference
        with st.form("merchant_update_form"):
            biz_ar = st.text_input("اسم النشاط التجاري (عربي)", key="m_biz_ar")
            biz_en = st.text_input("Business Name (EN)", key="m_biz_en")
            col1, col2 = st.columns(2)
            with col1:
                industry = st.text_input("Industry / القطاع", key="m_industry")
                website  = st.text_input("Website", key="m_website", placeholder="https://")
            with col2:
                city     = st.text_input("City / المدينة", value="Amman", key="m_city")
            if st.form_submit_button("💾 Save Business Info", use_container_width=True):
                payload = {k: v for k, v in {
                    "business_name_ar": biz_ar or None,
                    "business_name_en": biz_en or None,
                    "industry": industry or None,
                    "website" : website or None,
                    "city"    : city or None,
                }.items() if v}
                s, r = api_patch("/api/merchants/me", json=payload)
                if s == 200:
                    st.success("Business profile updated!")
                else:
                    st.error(r.get("detail", "Update failed"))

    elif role == "influencer":
        st.markdown("---")
        st.markdown("### 🌟 Influencer Profile / ملف المؤثر")
        with st.form("influencer_update_form"):
            col1, col2 = st.columns(2)
            with col1:
                ig_handle    = st.text_input("Instagram Handle", key="i_ig_h")
                ig_followers = st.number_input("Instagram Followers", min_value=0, value=0, key="i_ig_f")
                ig_er        = st.number_input("Instagram Engagement %", min_value=0.0, value=0.0, step=0.1, key="i_ig_er")
            with col2:
                tt_handle    = st.text_input("TikTok Handle", key="i_tt_h")
                tt_followers = st.number_input("TikTok Followers", min_value=0, value=0, key="i_tt_f")
                niche        = st.selectbox("Niche / التخصص", [
                    "Fashion","Food","Tech","Beauty","Fitness",
                    "Travel","Gaming","Education","Lifestyle","Sports"
                ], key="i_niche")
            col3, col4 = st.columns(2)
            with col3:
                rate_post  = st.number_input("Rate/Post (JOD)", min_value=0.0, value=0.0, step=5.0, key="i_rp")
                rate_story = st.number_input("Rate/Story (JOD)", min_value=0.0, value=0.0, step=5.0, key="i_rs")
            with col4:
                rate_reel   = st.number_input("Rate/Reel (JOD)", min_value=0.0, value=0.0, step=5.0, key="i_rr")
                is_available = st.checkbox("Available for campaigns / متاح", value=True, key="i_avail")

            # ── Audience Demographics ──────────────────────────────────────
            st.markdown("**👥 Audience Demographics / ديموغرافيا الجمهور**")
            st.caption("These help merchants find you with relevant campaigns / تساعد التجار على إيجادك")
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                female_pct = st.slider(
                    "Female audience % / نسبة الإناث",
                    min_value=0, max_value=100, value=50, step=5,
                    key="i_female_pct",
                    help="Percentage of female followers"
                )
            with dcol2:
                age_18_24 = st.slider("18–24 age group %", min_value=0, max_value=100, value=35, step=5, key="i_age1")
                age_25_34 = st.slider("25–34 age group %", min_value=0, max_value=100, value=35, step=5, key="i_age2")

            if st.form_submit_button("💾 Update Profile & Rescore", use_container_width=True):
                age_35plus = max(0, 100 - age_18_24 - age_25_34)
                payload = {k: v for k, v in {
                    "instagram_handle"          : ig_handle or None,
                    "instagram_followers"       : int(ig_followers) if ig_followers else None,
                    "instagram_engagement_rate" : ig_er if ig_er else None,
                    "tiktok_handle"             : tt_handle or None,
                    "tiktok_followers"          : int(tt_followers) if tt_followers else None,
                    "niche"                     : niche,
                    "rate_per_post"             : rate_post if rate_post else None,
                    "rate_per_story"            : rate_story if rate_story else None,
                    "rate_per_reel"             : rate_reel if rate_reel else None,
                    "is_available"              : is_available,
                    "audience_gender_split"     : {"female": female_pct, "male": 100 - female_pct},
                    "audience_age_split"        : {"18-24": age_18_24, "25-34": age_25_34, "35+": age_35plus},
                }.items() if v is not None}
                s, r = api_patch("/api/influencers/me", json=payload)
                if s == 200:
                    st.success(f"Profile updated! New ARIA score: {r.get('aria_score', '—')}")
                    st.rerun()
                else:
                    st.error(r.get("detail", "Update failed"))

    st.markdown("---")
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
    if role == "influencer":
        st.session_state["page"] = "open_campaigns"
        st.rerun()
    else:
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
    if role == "influencer":
        st.session_state["page"] = "open_campaigns"
        st.rerun()
    else:
        render_discover()

elif page == "open_campaigns":
    if not logged_in:
        render_login()
    elif role == "influencer":
        render_open_campaigns()
    else:
        # merchants don't need this page — redirect to discover
        st.session_state["page"] = "discover"
        st.rerun()

elif page == "bookings":
    if not logged_in:
        render_login()
    else:
        render_bookings()

elif page == "booking_wizard":
    if not logged_in:
        render_login()
    else:
        _render_booking_wizard()

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
