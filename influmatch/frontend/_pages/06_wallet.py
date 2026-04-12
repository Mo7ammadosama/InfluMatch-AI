import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

st.markdown("""
<div style="background:linear-gradient(135deg,#2e1a00,#4e3000);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:#ffd700; margin:0;">🎁 محفظة الولاء — Loyalty Wallet</h2>
    <p style="color:#ffa040; margin:5px 0 0 0;">
        اجمع النقاط وحوّلها إلى خصومات حقيقية بالدينار الأردني
    </p>
</div>
""", unsafe_allow_html=True)

# ── Wallet Balance ─────────────────────────────────────────
w1, w2, w3, w4 = st.columns(4)
w1.metric("⭐ رصيد النقاط",    "4,750 pts",  "+250 هذا الأسبوع")
w2.metric("💰 القيمة بالدينار","47.5 JOD",   "قابلة للاسترداد")
w3.metric("🏅 مستواك",        "🥈 فضي",     "250 pts للذهبي")
w4.metric("📅 انتهاء الصلاحية","31 ديسمبر", "2024")

st.divider()

# ── Tier Progress ──────────────────────────────────────────
st.markdown("### 🏆 تقدمك نحو الدرجة التالية")

current_pts = 4750
gold_target = 5000
progress    = current_pts / gold_target

st.markdown(f"""
<div style="background:#1a1a2e; border-radius:12px; padding:1.2rem; margin-bottom:1rem;">
    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <span style="color:#c0c0c0; font-weight:700;">🥈 فضي</span>
        <span style="color:#ffd700; font-weight:700;">🥇 ذهبي</span>
    </div>
    <div style="background:#0f3460; border-radius:6px; height:12px;">
        <div style="background:linear-gradient(90deg,#c0c0c0,#ffd700);
                    width:{int(progress*100)}%; height:100%;
                    border-radius:6px;"></div>
    </div>
    <p style="color:#a0a0b0; font-size:13px; margin-top:8px;">
        {current_pts:,} / {gold_target:,} نقطة
        — تحتاج <b style="color:#ffd700;">{gold_target-current_pts} نقطة</b> للمستوى التالي
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Transaction History ────────────────────────────────────
st.markdown("### 📋 سجل نقاطك")

wallet_txs = [
    {"التاريخ": "2024-02-18", "الحدث": "✅ اكتملت حملة عطر الربيع",   "النقاط": "+200", "الرصيد": "4,750"},
    {"التاريخ": "2024-02-15", "الحدث": "📢 نشر حملة عروض رمضان",      "النقاط": "+100", "الرصيد": "4,550"},
    {"التاريخ": "2024-02-10", "الحدث": "💰 مكافأة الإنفاق (800 JOD)", "النقاط": "+40",  "الرصيد": "4,450"},
    {"التاريخ": "2024-02-01", "الحدث": "⭐ تقييم إيجابي من مؤثر",     "النقاط": "+50",  "الرصيد": "4,410"},
    {"التاريخ": "2024-01-20", "الحدث": "🎁 استرداد نقاط — خصم حملة", "النقاط": "-500", "الرصيد": "4,360"},
]

st.dataframe(
    pd.DataFrame(wallet_txs),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ── Redeem Points ──────────────────────────────────────────
st.markdown("### 💳 استرداد النقاط")

redeem_col1, redeem_col2 = st.columns(2)
with redeem_col1:
    points_to_redeem = st.number_input(
        "عدد النقاط للاسترداد (الحد الأدنى: 500)",
        min_value=500, max_value=4750, step=100, value=500
    )
    jod_value = points_to_redeem * 0.01
    st.info(f"💰 القيمة: **{jod_value:.1f} JOD** خصم على حملتك القادمة")

    if st.button("🎁 استرداد الآن", type="primary", use_container_width=True):
        if points_to_redeem >= 500:
            st.success(f"✅ تم استرداد {points_to_redeem} نقطة = {jod_value:.1f} JOD خصم!")
            st.balloons()
        else:
            st.error("❌ الحد الأدنى للاسترداد هو 500 نقطة")

with redeem_col2:
    st.markdown("""
    <div style="background:#1a1a2e; border:1px solid #ffd700;
                border-radius:12px; padding:1.2rem;">
        <h4 style="color:#ffd700;">💡 كيف تجمع النقاط؟</h4>
        <ul style="color:#a0a0b0; font-size:13px; padding-right:1.2rem;">
            <li>📢 نشر حملة جديدة: <b style="color:#ffd700;">+100 نقطة</b></li>
            <li>✅ إتمام حملة:      <b style="color:#ffd700;">+200 نقطة</b></li>
            <li>⭐ تقييم إيجابي:   <b style="color:#ffd700;">+50 نقطة</b></li>
            <li>👥 دعوة تاجر جديد: <b style="color:#ffd700;">+500 نقطة</b></li>
            <li>💰 مكافأة الإنفاق: <b style="color:#ffd700;">5 نقاط/JOD</b></li>
        </ul>
        <p style="color:#ffa040; font-size:12px; margin-top:8px;">
            100 نقطة = 1 JOD خصم على حملاتك
        </p>
    </div>
    """, unsafe_allow_html=True)
# ============================================================