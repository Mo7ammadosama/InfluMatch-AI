"""Landing / Home page — Premium glassmorphism design"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t


def render_home():
    lang = st.session_state.get("lang", "ar")

    stats = api_get("/api/admin/platform-stats") or {}
    total_users       = stats.get("total_users", 0)
    total_campaigns   = stats.get("total_campaigns", 0)
    total_escrow_jod  = stats.get("total_escrow_volume_jod") or stats.get("escrow_locked_jod", 0)
    total_influencers = stats.get("total_influencers", 0)

    badge = "🇯🇴 &nbsp; JORDAN'S #1 AI INFLUENCER PLATFORM &nbsp; 🇯🇴" if lang == "en" else "🇯🇴 &nbsp; المنصة الأولى للمؤثرين في الأردن &nbsp; 🇯🇴"

    st.markdown(f"""
    <div style="text-align:center;padding:3.5rem 1rem 2rem;position:relative">
      <div style="display:inline-block;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.3);
                  border-radius:20px;padding:0.3rem 1rem;font-size:0.75rem;color:#8b5cf6;
                  margin-bottom:1.2rem;letter-spacing:0.1em">
        {badge}
      </div>
      <div style="margin-bottom:1rem">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:72px;height:72px;border-radius:22px;
                    background:linear-gradient(135deg,#7c3aed,#4f46e5);
                    box-shadow:0 8px 40px rgba(124,58,237,0.55);margin-bottom:1rem">
          <span style="font-size:2.2rem;line-height:1">&#9889;</span>
        </div>
      </div>
      <div style="font-size:3.4rem;font-weight:900;line-height:1.05;margin-bottom:0.8rem;letter-spacing:-0.03em">
        <span style="background:linear-gradient(135deg,#a78bfa,#818cf8);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">Wasl</span><span
             style="background:linear-gradient(135deg,#f59e0b,#fbbf24);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">AI</span><span
             style="color:#f59e0b;font-size:2rem">.jo</span>
      </div>
      <div style="font-size:1.3rem;font-weight:700;color:#e0e0f0;margin-bottom:0.5rem">
        {t('tagline')}
      </div>
      <div style="font-size:0.95rem;color:#6b7280;max-width:500px;margin:0 auto 2rem">
        {t('subtitle')}
      </div>
    </div>""", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    for col, val, unit, label_key, color in [
        (s1, total_users,                           "", "registered_users", "#f59e0b"),
        (s2, total_influencers,                     "", "influencers_lbl",  "#8b5cf6"),
        (s3, total_campaigns,                       "", "campaigns_lbl",    "#00ff88"),
        (s4, f"{float(total_escrow_jod):,.0f}", " JOD", "escrow_protected", "#ef4444"),
    ]:
        col.markdown(f"""
        <div style="background:rgba(0,0,0,0.3);border:1px solid {color}33;border-radius:12px;
                    padding:1rem;text-align:center;border-top:3px solid {color}">
          <div style="font-size:1.6rem;font-weight:900;color:{color}">{val}{unit}</div>
          <div style="font-size:0.7rem;color:#6b7280;margin-top:0.2rem">{t(label_key)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "🔒", {
            "ar": ("حماية Escrow الكاملة", "أموالك محمية حتى اكتمال الحملة", ["تجميد تلقائي","إفراج آمن","حل النزاعات"]),
            "en": ("Full Escrow Protection", "Funds locked until campaign completion", ["Auto-lock","Safe release","Dispute resolution"]),
        }, "#00ff88"),
        (c2, "🧠", {
            "ar": ("نظام تقييم ARIA AI", "كل مؤثر مصنّف بدرجة ذكاء اصطناعي", ["ARIA Score 0-100","4 مستويات Tier","تقييم تلقائي"]),
            "en": ("ARIA AI Scoring", "Every influencer scored by real AI metrics", ["ARIA Score 0-100","4 Tier levels","Auto re-scoring"]),
        }, "#8b5cf6"),
        (c3, "📅", {
            "ar": ("حجز ذكي متكامل", "من البحث إلى الدفع في خطوات", ["بحث طبيعي بالعربي","مراجعة AI للمحتوى","دفع تلقائي"]),
            "en": ("Smart Booking Flow", "From search to payment in minutes", ["Natural language search","AI content review","Auto payment"]),
        }, "#f59e0b"),
    ]
    for col, icon, texts, color in cards:
        title, desc, features = texts[lang]
        features_html = "".join([f'<div style="font-size:0.75rem;color:#a0a0b0;padding:0.2rem 0">✓ {f}</div>' for f in features])
        col.markdown(f"""
        <div class="glass-card" style="text-align:center;border-top:3px solid {color};height:100%">
          <div style="font-size:2.5rem;margin-bottom:0.8rem">{icon}</div>
          <div style="font-size:1rem;font-weight:800;color:{color};margin-bottom:0.5rem">{title}</div>
          <div style="font-size:0.85rem;color:#c0c0d0;margin-bottom:0.8rem">{desc}</div>
          <div style="text-align:{'right' if lang=='ar' else 'left'};border-top:1px solid rgba(255,255,255,0.05);padding-top:0.8rem">
            {features_html}
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────
    how_title = "كيف تعمل المنصة؟" if lang == "ar" else "How It Works"
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:1.5rem">
      <div style="font-size:1.2rem;font-weight:800;color:#e0e0f0">{how_title}</div>
    </div>""", unsafe_allow_html=True)

    steps = {
        "ar": [("1","🔍","ابحث عن مؤثر","#f59e0b"),("2","📅","احجز وجمّد المبلغ","#8b5cf6"),
               ("3","📸","المؤثر ينشر المحتوى","#00ff88"),("4","💰","دفع تلقائي آمن","#ef4444")],
        "en": [("1","🔍","Search for an influencer","#f59e0b"),("2","📅","Book & lock funds","#8b5cf6"),
               ("3","📸","Influencer posts content","#00ff88"),("4","💰","Automatic secure payment","#ef4444")],
    }
    step_cols = st.columns(4)
    for col, (num, icon, text, color) in zip(step_cols, steps[lang]):
        col.markdown(f"""
        <div style="text-align:center;padding:1rem 0.5rem">
          <div style="width:40px;height:40px;border-radius:50%;background:{color}22;
                      border:2px solid {color};display:inline-flex;align-items:center;
                      justify-content:center;font-weight:900;color:{color};
                      font-size:1rem;margin-bottom:0.5rem">{num}</div>
          <div style="font-size:1.5rem;margin-bottom:0.3rem">{icon}</div>
          <div style="font-size:0.8rem;font-weight:700;color:#e0e0f0">{text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── CTA ───────────────────────────────────────────────────────
    start_free = "ابدأ رحلتك اليوم — مجاني تماماً" if lang == "ar" else "Start your journey today — completely free"
    st.markdown(f"""<div style="text-align:center;margin-bottom:1rem">
      <div style="font-size:1rem;color:#a0a0b0">{start_free}</div>
    </div>""", unsafe_allow_html=True)

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        lbl = "🏪 ابدأ كتاجر" if lang == "ar" else "🏪 Start as Merchant"
        if st.button(lbl, use_container_width=True, type="primary", key="cta_merchant"):
            st.session_state["register_role"] = "merchant"
            st.session_state["page"] = "register"
            st.rerun()
    with cta2:
        lbl = "🌟 سجّل كمؤثر" if lang == "ar" else "🌟 Join as Influencer"
        if st.button(lbl, use_container_width=True, type="primary", key="cta_influencer"):
            st.session_state["register_role"] = "influencer"
            st.session_state["page"] = "register"
            st.rerun()
    with cta3:
        lbl = "🔑 " + t("login")
        if st.button(lbl, use_container_width=True, key="cta_login"):
            st.session_state["page"] = "login"
            st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;color:#4b4b6b;font-size:0.75rem;
                border-top:1px solid rgba(255,255,255,0.05);margin-top:2rem">
      WaslAI.jo &nbsp;·&nbsp; Powered by ARIA AI &nbsp;·&nbsp; Jordan Market &nbsp;·&nbsp; 2026
    </div>""", unsafe_allow_html=True)
