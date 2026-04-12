import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

st.markdown("""
<div style="background:linear-gradient(135deg,#0f3460,#533483);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">🏪 لوحة تحكم التاجر</h2>
    <p style="color:#a0c4ff; margin:5px 0 0 0;">
        Merchant Dashboard | InfluMatch.jo
    </p>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("📢 حملاتي النشطة",    "4",         "+1 هذا الأسبوع")
c2.metric("🌟 مؤثرون محجوزون",  "11",        "+3 هذا الشهر")
c3.metric("💰 رصيد الضمان",     "3,200 JOD", "مؤمّن 🔒")
c4.metric("⭐ نقاط الولاء",     "4,750 pts", "🥈 فضي")

st.divider()

# ── Campaign Performance Chart ─────────────────────────────
st.markdown("### 📊 أداء الحملات — آخر 30 يوم")

dates = pd.date_range(end=datetime.now(), periods=30)
df = pd.DataFrame({
    "التاريخ"       : dates,
    "الوصول"        : [i*450 + 12000 for i in range(30)],
    "التفاعلات"     : [i*120 + 800 for i in range(30)],
    "النقرات"       : [i*45 + 200 for i in range(30)],
})

fig = px.line(
    df, x="التاريخ",
    y=["الوصول", "التفاعلات", "النقرات"],
    color_discrete_map={
        "الوصول"    : "#0f3460",
        "التفاعلات" : "#533483",
        "النقرات"   : "#e94560"
    }
)
fig.update_layout(
    paper_bgcolor="#1a1a2e",
    plot_bgcolor="#1a1a2e",
    font=dict(color="white"),
    height=300,
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=0, r=0, t=10, b=0)
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Active Campaigns Table ─────────────────────────────────
st.markdown("### 📢 حملاتي الحالية")

sample_campaigns = [
    {"العنوان": "إطلاق عطر الربيع",       "الحالة": "🟢 نشطة",   "الميزانية": "800 JOD",  "المؤثرون": 3, "الانتهاء": "2024-03-15"},
    {"العنوان": "عروض رمضان 2024",         "الحالة": "🟡 مسودة",  "الميزانية": "1,500 JOD","المؤثرون": 0, "الانتهاء": "2024-03-25"},
    {"العنوان": "تطبيق توصيل الطعام",      "الحالة": "🔵 قيد المراجعة","الميزانية": "600 JOD","المؤثرون": 5, "الانتهاء": "2024-02-28"},
    {"العنوان": "ملابس الصيف — مجموعة جديدة","الحالة": "🟢 نشطة", "الميزانية": "300 JOD",  "المؤثرون": 2, "الانتهاء": "2024-04-01"},
]

st.dataframe(
    pd.DataFrame(sample_campaigns),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ── Quick Actions ──────────────────────────────────────────
st.markdown("### ⚡ إجراءات سريعة")

qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button("➕ حملة جديدة",     use_container_width=True):
        st.switch_page("_pages/03_campaigns.py")
with qa2:
    if st.button("🔍 ابحث عن مؤثر",  use_container_width=True):
        st.switch_page("_pages/02_influencer_portal.py")
with qa3:
    if st.button("💳 تتبع الضمان",    use_container_width=True):
        st.switch_page("_pages/05_escrow_tracker.py")
with qa4:
    if st.button("🎁 محفظتي",         use_container_width=True):
        st.switch_page("_pages/06_wallet.py")
# ============================================================