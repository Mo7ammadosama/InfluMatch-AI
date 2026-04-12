import streamlit as st
import requests
import plotly.express as px
import pandas as pd

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a2e,#2d1b4e);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">🌟 بوابة المؤثرين</h2>
    <p style="color:#c0a0ff; margin:5px 0 0 0;">
        Influencer Discovery | ARIA-Scored | Jordan Market
    </p>
</div>
""", unsafe_allow_html=True)

# ── Search & Filter Bar ────────────────────────────────────
st.markdown("### 🔍 البحث عن المؤثرين المثاليين")

f1, f2, f3, f4 = st.columns(4)
with f1:
    niche = st.selectbox("🎯 التخصص",
        ["الكل", "موضة", "طعام", "تقنية", "رياضة",
         "سفر", "جمال", "أسلوب حياة", "تعليم"])
with f2:
    platform = st.selectbox("📱 المنصة",
        ["الكل", "Instagram", "TikTok", "YouTube"])
with f3:
    tier = st.selectbox("⭐ درجة ARIA",
        ["الكل", "PLATINUM 💎", "GOLD 🥇", "SILVER 🥈", "BRONZE 🥉"])
with f4:
    budget = st.slider("💰 الميزانية (JOD/منشور)", 10, 500, (50, 200))

st.button("🔍 بحث", type="primary", use_container_width=False)

st.divider()

# ── Influencer Cards Grid ──────────────────────────────────
st.markdown("### 🌟 المؤثرون المتاحون")

influencers = [
    {
        "الاسم"         : "سارة الأردنية",
        "التخصص"        : "موضة وجمال",
        "Instagram"     : "45K",
        "TikTok"        : "120K",
        "ARIA Score"    : 87.4,
        "الدرجة"        : "GOLD 🥇",
        "السعر/منشور"  : "85 JOD",
        "المدينة"       : "عمان",
    },
    {
        "الاسم"         : "أحمد التقني",
        "التخصص"        : "تقنية وريادة أعمال",
        "Instagram"     : "32K",
        "TikTok"        : "78K",
        "ARIA Score"    : 91.2,
        "الدرجة"        : "PLATINUM 💎",
        "السعر/منشور"  : "110 JOD",
        "المدينة"       : "عمان",
    },
    {
        "الاسم"         : "لينا كوكس",
        "التخصص"        : "طعام ومطاعم",
        "Instagram"     : "28K",
        "TikTok"        : "55K",
        "ARIA Score"    : 73.6,
        "الدرجة"        : "SILVER 🥈",
        "السعر/منشور"  : "65 JOD",
        "المدينة"       : "الزرقاء",
    },
    {
        "الاسم"         : "فارس العقبة",
        "التخصص"        : "سفر وسياحة",
        "Instagram"     : "67K",
        "TikTok"        : "210K",
        "ARIA Score"    : 94.8,
        "الدرجة"        : "PLATINUM 💎",
        "السعر/منشور"  : "150 JOD",
        "المدينة"       : "العقبة",
    },
    {
        "الاسم"         : "ريم الرياضية",
        "التخصص"        : "لياقة بدنية",
        "Instagram"     : "19K",
        "TikTok"        : "43K",
        "ARIA Score"    : 66.1,
        "الدرجة"        : "SILVER 🥈",
        "السعر/منشور"  : "55 JOD",
        "المدينة"       : "إربد",
    },
    {
        "الاسم"         : "خالد المطبخ",
        "التخصص"        : "طبخ أردني تقليدي",
        "Instagram"     : "53K",
        "TikTok"        : "89K",
        "ARIA Score"    : 82.3,
        "الدرجة"        : "GOLD 🥇",
        "السعر/منشور"  : "95 JOD",
        "المدينة"       : "عمان",
    },
]

# Render in 3-column grid
cols = st.columns(3)
for idx, inf in enumerate(influencers):
    score     = inf["ARIA Score"]
    tier_color = (
        "#e5e4e2" if "PLATINUM" in inf["الدرجة"] else
        "#ffd700" if "GOLD"     in inf["الدرجة"] else
        "#c0c0c0" if "SILVER"   in inf["الدرجة"] else
        "#cd7f32"
    )
    with cols[idx % 3]:
        st.markdown(f"""
        <div style="background:#1a1a2e; border:1px solid #533483;
                    border-radius:14px; padding:1.2rem; margin-bottom:1rem;
                    transition: all 0.3s ease;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="color:white; margin:0;">{inf['الاسم']}</h4>
                <span style="background:{tier_color}22; color:{tier_color};
                             border:1px solid {tier_color}; border-radius:20px;
                             padding:2px 10px; font-size:12px; font-weight:700;">
                    {inf['الدرجة']}
                </span>
            </div>
            <p style="color:#a0a0b0; font-size:13px; margin:6px 0;">
                🎯 {inf['التخصص']} | 📍 {inf['المدينة']}
            </p>
            <div style="display:flex; gap:12px; margin:10px 0;">
                <span style="color:#c0a0ff; font-size:13px;">
                    📸 {inf['Instagram']}
                </span>
                <span style="color:#ff88cc; font-size:13px;">
                    🎵 {inf['TikTok']}
                </span>
            </div>
            <div style="background:#0f3460; border-radius:8px;
                        padding:8px; text-align:center; margin:10px 0;">
                <span style="color:{tier_color}; font-size:22px; font-weight:900;">
                    {score}
                </span>
                <span style="color:#a0a0b0; font-size:12px;"> / 100 ARIA</span>
            </div>
            <p style="color:#00ff88; font-size:14px; font-weight:700; margin:6px 0;">
                💰 {inf['السعر/منشور']} / منشور
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"📩 تواصل", key=f"contact_{idx}", use_container_width=True):
            st.toast(f"✅ تم إرسال طلب التعاون إلى {inf['الاسم']}", icon="🌟")
# ============================================================