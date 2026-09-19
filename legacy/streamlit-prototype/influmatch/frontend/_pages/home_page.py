"""Landing / Home page"""
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

    platform_label = "JORDAN INFLUENCER PLATFORM" if lang == "en" else "منصة المؤثرين — الأردن"
    tagline        = t("tagline")
    subtitle       = t("subtitle")

    # ── Hero ──────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:3rem 1rem 2rem">
      <div style="font-size:0.65rem;font-weight:700;color:#4b5563;letter-spacing:0.14em;
                  text-transform:uppercase;margin-bottom:1.2rem">{platform_label}</div>
      <div style="font-size:2.8rem;font-weight:800;line-height:1.1;
                  letter-spacing:-0.03em;color:#f1f1f5;margin-bottom:0.75rem">
        Wasl<span style="color:#f59e0b">AI</span><span style="color:#4b5563;font-size:1.8rem">.jo</span>
      </div>
      <div style="font-size:1.15rem;font-weight:600;color:#9ca3af;
                  max-width:520px;line-height:1.5;margin-bottom:0.6rem">{tagline}</div>
      <div style="font-size:0.9rem;color:#4b5563;max-width:460px;line-height:1.6">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    for col, val, unit, label_key, accent in [
        (s1, total_users,                       "", "registered_users", "#f59e0b"),
        (s2, total_influencers,                  "", "influencers_lbl",  "#7c3aed"),
        (s3, total_campaigns,                    "", "campaigns_lbl",    "#3b82f6"),
        (s4, f"{float(total_escrow_jod):,.0f}", " JOD", "escrow_protected", "#22c55e"),
    ]:
        col.markdown(f"""
        <div style="background:#111119;border:1px solid rgba(255,255,255,0.07);
                    border-top:2px solid {accent};border-radius:10px;
                    padding:0.9rem 1rem;text-align:center">
          <div style="font-size:1.55rem;font-weight:800;color:{accent};line-height:1">{val}{unit}</div>
          <div style="font-size:0.65rem;color:#4b5563;margin-top:0.3rem;
                      text-transform:uppercase;letter-spacing:0.07em">{t(label_key)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    cards = [
        (c1, "Escrow", {
            "ar": ("حماية Escrow الكاملة", "أموالك محمية حتى اكتمال الحملة",
                   ["تجميد تلقائي", "إفراج آمن", "حل النزاعات"]),
            "en": ("Full Escrow Protection", "Funds locked until campaign completion",
                   ["Auto-lock", "Safe release", "Dispute resolution"]),
        }, "#22c55e"),
        (c2, "ARIA AI", {
            "ar": ("نظام تقييم ARIA", "كل مؤثر مصنّف بدرجة ذكاء اصطناعي",
                   ["ARIA Score 0–100", "4 مستويات Tier", "تقييم تلقائي"]),
            "en": ("ARIA AI Scoring", "Every influencer scored by real AI metrics",
                   ["ARIA Score 0–100", "4 Tier levels", "Auto re-scoring"]),
        }, "#7c3aed"),
        (c3, "Booking", {
            "ar": ("حجز ذكي متكامل", "من البحث إلى الدفع في خطوات",
                   ["بحث طبيعي بالعربي", "مراجعة AI للمحتوى", "دفع تلقائي"]),
            "en": ("Smart Booking Flow", "From search to payment in minutes",
                   ["Natural language search", "AI content review", "Auto payment"]),
        }, "#f59e0b"),
    ]
    for col, badge_text, texts, accent in cards:
        title, desc, features = texts[lang]
        feats = "".join([
            f'<div style="font-size:0.75rem;color:#6b7280;padding:0.18rem 0;'
            f'display:flex;align-items:center;gap:0.4rem">'
            f'<span style="color:{accent};font-size:0.6rem">&#x25CF;</span>{f}</div>'
            for f in features
        ])
        col.markdown(f"""
        <div style="background:#111119;border:1px solid rgba(255,255,255,0.07);
                    border-top:2px solid {accent};border-radius:10px;
                    padding:1.25rem 1.25rem 1rem;height:100%">
          <div style="font-size:0.6rem;font-weight:700;color:{accent};
                      text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem">{badge_text}</div>
          <div style="font-size:0.95rem;font-weight:700;color:#f1f1f5;margin-bottom:0.4rem">{title}</div>
          <div style="font-size:0.82rem;color:#6b7280;margin-bottom:0.9rem;line-height:1.45">{desc}</div>
          <div style="border-top:1px solid rgba(255,255,255,0.05);padding-top:0.7rem">{feats}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────
    how_title = "كيف تعمل المنصة" if lang == "ar" else "How It Works"
    st.markdown(f"""
    <div style="margin-bottom:1.25rem">
      <div style="font-size:0.65rem;color:#4b5563;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.1em;margin-bottom:0.3rem">PROCESS</div>
      <div style="font-size:1.1rem;font-weight:700;color:#f1f1f5">{how_title}</div>
    </div>""", unsafe_allow_html=True)

    steps = {
        "ar": [("01", "ابحث عن مؤثر",          "#f59e0b"),
               ("02", "احجز وجمّد المبلغ",       "#7c3aed"),
               ("03", "المؤثر ينشر المحتوى",     "#3b82f6"),
               ("04", "دفع تلقائي آمن",           "#22c55e")],
        "en": [("01", "Search for an influencer","#f59e0b"),
               ("02", "Book & lock funds",        "#7c3aed"),
               ("03", "Influencer posts content", "#3b82f6"),
               ("04", "Automatic secure payment", "#22c55e")],
    }
    step_cols = st.columns(4)
    for col, (num, text, accent) in zip(step_cols, steps[lang]):
        col.markdown(f"""
        <div style="background:#111119;border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px;padding:0.9rem 1rem">
          <div style="font-size:1.5rem;font-weight:900;color:rgba(255,255,255,0.06);
                      line-height:1;margin-bottom:0.35rem">{num}</div>
          <div style="width:28px;height:2px;background:{accent};border-radius:1px;margin-bottom:0.5rem"></div>
          <div style="font-size:0.82rem;font-weight:600;color:#d1d5db;line-height:1.4">{text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)

    # ── CTA ───────────────────────────────────────────────────
    start_label = "ابدأ اليوم — مجاني تماماً" if lang == "ar" else "Get started — completely free"
    st.markdown(f"""
    <div style="margin-bottom:0.75rem">
      <div style="font-size:0.75rem;color:#4b5563">{start_label}</div>
    </div>""", unsafe_allow_html=True)

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        lbl = "ابدأ كتاجر" if lang == "ar" else "Start as Merchant"
        if st.button(lbl, use_container_width=True, type="primary", key="cta_merchant"):
            st.session_state["register_role"] = "merchant"
            st.session_state["page"] = "register"
            st.rerun()
    with cta2:
        lbl = "سجّل كمؤثر" if lang == "ar" else "Join as Influencer"
        if st.button(lbl, use_container_width=True, type="primary", key="cta_influencer"):
            st.session_state["register_role"] = "influencer"
            st.session_state["page"] = "register"
            st.rerun()
    with cta3:
        lbl = t("login")
        if st.button(lbl, use_container_width=True, key="cta_login"):
            st.session_state["page"] = "login"
            st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:2rem 0 0.5rem;color:#2a2a35;font-size:0.7rem;
                border-top:1px solid rgba(255,255,255,0.04);margin-top:2.5rem">
      WaslAI.jo &nbsp;&middot;&nbsp; Jordan Market &nbsp;&middot;&nbsp; 2026
    </div>""", unsafe_allow_html=True)
