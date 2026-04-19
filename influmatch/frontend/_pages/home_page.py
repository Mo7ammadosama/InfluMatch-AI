"""Landing / Home page — Premium glassmorphism design"""
import streamlit as st
from ..utils.api_client import api_get


def render_home():
    # ── Pull real stats (no auth needed for platform-stats) ──────────────────
    stats = api_get("/api/admin/platform-stats") or {}
    total_users       = stats.get("total_users", 0)
    total_campaigns   = stats.get("total_campaigns", 0)
    total_escrow_jod  = stats.get("total_escrow_volume_jod") or stats.get("escrow_locked_jod", 0)
    total_influencers = stats.get("total_influencers", 0)

    # ── Hero Section ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 1rem 2rem;position:relative">
      <div style="display:inline-block;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.3);
                  border-radius:20px;padding:0.3rem 1rem;font-size:0.75rem;color:#8b5cf6;
                  margin-bottom:1.2rem;letter-spacing:0.1em">
        🇯🇴 &nbsp; JORDAN'S #1 AI INFLUENCER PLATFORM &nbsp; 🇯🇴
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
        منصة المؤثرين الأولى في الأردن
      </div>
      <div style="font-size:0.95rem;color:#6b7280;max-width:500px;margin:0 auto 2rem">
        Connect Brands with Influencers — Secured by Escrow · Scored by ARIA AI
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Live Stats Bar ────────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    for col, val, unit, label, color in [
        (s1, total_users,       "",      "مستخدم مسجّل / Users",           "#f59e0b"),
        (s2, total_influencers, "",      "مؤثر / Influencers",             "#8b5cf6"),
        (s3, total_campaigns,   "",      "حملة / Campaigns",               "#00ff88"),
        (s4, f"{float(total_escrow_jod):,.0f}", " JOD", "محمية بـ Escrow", "#ef4444"),
    ]:
        col.markdown(f"""
        <div style="background:rgba(0,0,0,0.3);border:1px solid {color}33;border-radius:12px;
                    padding:1rem;text-align:center;border-top:3px solid {color}">
          <div style="font-size:1.6rem;font-weight:900;color:{color}">{val}{unit}</div>
          <div style="font-size:0.7rem;color:#6b7280;margin-top:0.2rem">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── 3 Feature Cards ───────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    for col, icon, title_ar, title_en, desc_ar, desc_en, color, features in [
        (
            c1, "🔒",
            "حماية Escrow الكاملة",
            "Full Escrow Protection",
            "أموالك محمية حتى اكتمال الحملة",
            "Funds are locked until campaign completion",
            "#00ff88",
            ["تجميد تلقائي", "إفراج آمن", "حل النزاعات"],
        ),
        (
            c2, "🧠",
            "نظام تقييم ARIA AI",
            "ARIA AI Scoring",
            "كل مؤثر مصنّف بدرجة ذكاء اصطناعي",
            "Every influencer scored by real AI metrics",
            "#8b5cf6",
            ["ARIA Score 0-100", "4 مستويات Tier", "إعادة تسجيل تلقائي"],
        ),
        (
            c3, "📅",
            "حجز ذكي متكامل",
            "Smart Booking Flow",
            "من البحث إلى الدفع في خطوات",
            "From search to payment in minutes",
            "#f59e0b",
            ["بحث طبيعي بالعربي", "مراجعة AI للمحتوى", "دفع تلقائي"],
        ),
    ]:
        features_html = "".join([
            f'<div style="font-size:0.75rem;color:#a0a0b0;padding:0.2rem 0">✓ {f}</div>'
            for f in features
        ])
        col.markdown(f"""
        <div class="glass-card" style="text-align:center;border-top:3px solid {color};height:100%">
          <div style="font-size:2.5rem;margin-bottom:0.8rem">{icon}</div>
          <div style="font-size:1rem;font-weight:800;color:{color};margin-bottom:0.3rem">{title_ar}</div>
          <div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.8rem">{title_en}</div>
          <div style="font-size:0.85rem;color:#c0c0d0;margin-bottom:0.8rem">{desc_ar}</div>
          <div style="font-size:0.75rem;color:#6b7280;margin-bottom:1rem">{desc_en}</div>
          <div style="text-align:right;border-top:1px solid rgba(255,255,255,0.05);padding-top:0.8rem">
            {features_html}
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2.5rem'></div>", unsafe_allow_html=True)

    # ── How It Works ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem">
      <div style="font-size:1.2rem;font-weight:800;color:#e0e0f0">كيف تعمل المنصة؟ / How It Works</div>
    </div>""", unsafe_allow_html=True)

    step_cols = st.columns(4)
    for col, num, icon, text_ar, text_en, color in [
        (step_cols[0], "1", "🔍", "ابحث عن مؤثر",    "Search for an influencer",      "#f59e0b"),
        (step_cols[1], "2", "📅", "احجز وجمّد المبلغ","Book & lock funds in Escrow",   "#8b5cf6"),
        (step_cols[2], "3", "📸", "المؤثر ينشر المحتوى","Influencer posts content",     "#00ff88"),
        (step_cols[3], "4", "💰", "دفع تلقائي آمن",   "Automatic secure payment",      "#ef4444"),
    ]:
        col.markdown(f"""
        <div style="text-align:center;padding:1rem 0.5rem">
          <div style="width:40px;height:40px;border-radius:50%;background:{color}22;
                      border:2px solid {color};display:inline-flex;align-items:center;
                      justify-content:center;font-weight:900;color:{color};
                      font-size:1rem;margin-bottom:0.5rem">{num}</div>
          <div style="font-size:1.5rem;margin-bottom:0.3rem">{icon}</div>
          <div style="font-size:0.8rem;font-weight:700;color:#e0e0f0">{text_ar}</div>
          <div style="font-size:0.7rem;color:#6b7280">{text_en}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

    # ── CTA Buttons ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;margin-bottom:1rem">
      <div style="font-size:1rem;color:#a0a0b0">
        ابدأ رحلتك اليوم — مجاني تماماً
      </div>
    </div>""", unsafe_allow_html=True)

    cta1, cta2, cta3 = st.columns([1, 1, 1])
    with cta1:
        if st.button("🏪 ابدأ كتاجر / Start as Merchant",
                     use_container_width=True, type="primary", key="cta_merchant"):
            st.session_state["register_role"] = "merchant"
            st.session_state["page"] = "register"
            st.rerun()
    with cta2:
        if st.button("🌟 سجّل كمؤثر / Join as Influencer",
                     use_container_width=True, type="primary", key="cta_influencer"):
            st.session_state["register_role"] = "influencer"
            st.session_state["page"] = "register"
            st.rerun()
    with cta3:
        if st.button("🔑 تسجيل الدخول / Login",
                     use_container_width=True, key="cta_login"):
            st.session_state["page"] = "login"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;color:#4b4b6b;font-size:0.75rem;
                border-top:1px solid rgba(255,255,255,0.05);margin-top:2rem">
      WaslAI.jo &nbsp;·&nbsp; مدعوم بـ ARIA AI &nbsp;·&nbsp; السوق الأردني &nbsp;·&nbsp; 2026
    </div>""", unsafe_allow_html=True)
