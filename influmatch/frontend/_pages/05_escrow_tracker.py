import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

st.markdown("""
<div style="background:linear-gradient(135deg,#0a2e1a,#1a4e2e);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">🔒 نظام الضمان المالي — Escrow Tracker</h2>
    <p style="color:#80ffa0; margin:5px 0 0 0;">
        جميع المدفوعات محمية حتى الموافقة على المحتوى
    </p>
</div>
""", unsafe_allow_html=True)

# ── Escrow Summary ─────────────────────────────────────────
e1, e2, e3, e4 = st.columns(4)
e1.metric("💰 إجمالي محجوز",   "3,200 JOD", "في الضمان 🔒")
e2.metric("✅ تم الإفراج عنه", "12,450 JOD","هذا الشهر")
e3.metric("⏳ قيد المراجعة",  "850 JOD",  "3 معاملات")
e4.metric("⚠️ نزاعات مفتوحة", "1",        "48h للحسم")

st.divider()

# ── Escrow Transactions Timeline ───────────────────────────
st.markdown("### 📋 سجل معاملات الضمان")

transactions = [
    {
        "رقم المعاملة" : "ESC-2024-001",
        "الحملة"       : "إطلاق عطر الربيع",
        "المؤثر"       : "سارة الأردنية",
        "المبلغ"       : "510 JOD",
        "الصافي"       : "484.5 JOD",
        "الضريبة"      : "81.6 JOD",
        "الحالة"       : "✅ مُفرج",
        "التاريخ"      : "2024-02-10",
    },
    {
        "رقم المعاملة" : "ESC-2024-002",
        "الحملة"       : "عروض رمضان",
        "المؤثر"       : "أحمد التقني",
        "المبلغ"       : "800 JOD",
        "الصافي"       : "760 JOD",
        "الضريبة"      : "128 JOD",
        "الحالة"       : "🔒 محجوز",
        "التاريخ"      : "2024-02-15",
    },
    {
        "رقم المعاملة" : "ESC-2024-003",
        "الحملة"       : "تطبيق توصيل الطعام",
        "المؤثر"       : "لينا كوكس",
        "المبلغ"       : "400 JOD",
        "الصافي"       : "380 JOD",
        "الضريبة"      : "64 JOD",
        "الحالة"       : "⚠️ نزاع",
        "التاريخ"      : "2024-02-18",
    },
]

df = pd.DataFrame(transactions)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

# ── Auto-Release Countdown ─────────────────────────────────
st.markdown("### ⏱️ مؤقتات الإفراج التلقائي (Guardian Agent)")

for tx in transactions:
    if "محجوز" in tx["الحالة"]:
        release_date = datetime.now() + timedelta(days=5)
        days_left    = (release_date - datetime.now()).days
        progress     = (7 - days_left) / 7

        st.markdown(f"""
        <div style="background:#1a1a2e; border:1px solid #533483;
                    border-radius:12px; padding:1rem; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between;">
                <b style="color:white;">{tx['الحملة']}</b>
                <span style="color:#ffd700; font-weight:700;">{tx['المبلغ']}</span>
            </div>
            <p style="color:#a0a0b0; font-size:13px; margin:4px 0;">
                الإفراج التلقائي خلال:
                <b style="color:#00ff88;">{days_left} أيام</b>
                (بواسطة Guardian Agent)
            </p>
            <div style="background:#0f3460; border-radius:4px; height:8px; margin-top:8px;">
                <div style="background:linear-gradient(90deg,#0f3460,#00ff88);
                            width:{int(progress*100)}%; height:100%;
                            border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
# ============================================================