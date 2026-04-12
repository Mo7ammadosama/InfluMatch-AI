"""Landing / Home page"""
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
