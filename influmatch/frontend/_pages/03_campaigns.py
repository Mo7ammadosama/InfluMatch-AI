# ============================================================
# COMPONENT 21: frontend/_pages/03_campaigns.py
# Full Campaign Management — Create / List / Analytics
# ============================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

st.markdown("""
<div style="background:linear-gradient(135deg,#1a0e2e,#2e1a4e);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">📢 إدارة الحملات</h2>
    <p style="color:#c0a0ff; margin:5px 0 0 0;">
        Campaign Management | Powered by ARIA Guardian Agent
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "➕ حملة جديدة",
    "📋 حملاتي الحالية",
    "📊 تحليلات الحملات"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — CREATE NEW CAMPAIGN
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("### ➕ إنشاء حملة تسويقية جديدة")
    st.info(
        "🤖 بعد إنشاء الحملة، سيقوم **Guardian Agent** تلقائياً "
        "بجدولة جميع مراحل دورة حياة الحملة."
    )

    with st.form("create_campaign_form", clear_on_submit=False):
        # Row 1 — Basic Info
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            title_ar = st.text_input(
                "📝 عنوان الحملة (عربي) *",
                placeholder="مثال: إطلاق مجموعة صيف 2024"
            )
        with r1c2:
            title_en = st.text_input(
                "📝 Campaign Title (English)",
                placeholder="e.g. Summer 2024 Collection Launch"
            )

        # Row 2 — Description
        desc_ar = st.text_area(
            "📄 وصف الحملة (عربي)",
            placeholder="اكتب وصفاً تفصيلياً للحملة...",
            height=100
        )

        # Row 3 — Niche & Budget
        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1:
            niche = st.selectbox("🎯 مجال الحملة *", [
                "موضة وأزياء", "طعام ومطاعم", "تقنية",
                "جمال وعناية", "رياضة ولياقة", "سفر وسياحة",
                "تعليم", "أسلوب حياة", "ألعاب", "أعمال"
            ])
        with r3c2:
            total_budget = st.number_input(
                "💰 الميزانية الإجمالية (JOD) *",
                min_value=50.0, max_value=50000.0,
                value=500.0, step=50.0
            )
        with r3c3:
            budget_per_inf = st.number_input(
                "💸 الميزانية/مؤثر (JOD)",
                min_value=10.0, max_value=5000.0,
                value=100.0, step=10.0
            )

        # Row 4 — Dates
        r4c1, r4c2, r4c3 = st.columns(3)
        with r4c1:
            start_date = st.date_input(
                "📅 تاريخ البدء",
                value=datetime.now().date() + timedelta(days=3)
            )
        with r4c2:
            end_date = st.date_input(
                "📅 تاريخ الانتهاء",
                value=datetime.now().date() + timedelta(days=30)
            )
        with r4c3:
            deadline = st.date_input(
                "⏰ موعد التسليم الأخير",
                value=datetime.now().date() + timedelta(days=25)
            )

        # Row 5 — Deliverables & Hashtags
        r5c1, r5c2 = st.columns(2)
        with r5c1:
            deliverables = st.multiselect(
                "📦 التسليمات المطلوبة *",
                ["منشور Instagram", "ستوري Instagram",
                 "ريل Instagram", "فيديو TikTok",
                 "فيديو YouTube", "ستوري TikTok"],
                default=["منشور Instagram", "ستوري Instagram"]
            )
        with r5c2:
            hashtags_input = st.text_input(
                "# الهاشتاقات (مفصولة بفاصلة)",
                placeholder="#Jordan, #عمان, #YourBrand"
            )

        # VAT Preview
        vat_amount   = total_budget * 0.16
        platform_fee = total_budget * 0.05
        net_payout   = total_budget - platform_fee

        st.markdown(f"""
        <div style="background:#0f3460; border-radius:10px; padding:1rem; margin:1rem 0;">
            <h4 style="color:white; margin:0 0 8px 0;">💰 ملخص التكاليف</h4>
            <div style="display:flex; gap:2rem; flex-wrap:wrap;">
                <span style="color:#a0c4ff;">الميزانية الإجمالية:
                    <b style="color:white;">{total_budget:,.1f} JOD</b>
                </span>
                <span style="color:#a0c4ff;">ضريبة القيمة المضافة (16%):
                    <b style="color:#ffd700;">{vat_amount:,.1f} JOD</b>
                </span>
                <span style="color:#a0c4ff;">عمولة المنصة (5%):
                    <b style="color:#ff8888;">{platform_fee:,.1f} JOD</b>
                </span>
                <span style="color:#a0c4ff;">صافي دفعات المؤثرين:
                    <b style="color:#00ff88;">{net_payout:,.1f} JOD</b>
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🚀 إطلاق الحملة وتفعيل Guardian Agent",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not title_ar or not deliverables:
                st.error("❌ يرجى تعبئة الحقول الإلزامية (*)")
            else:
                hashtags = [h.strip() for h in hashtags_input.split(",") if h.strip()]
                payload  = {
                    "title_ar"              : title_ar,
                    "title_en"              : title_en or None,
                    "description_ar"        : desc_ar or None,
                    "niche"                 : niche,
                    "total_budget"          : total_budget,
                    "budget_per_influencer" : budget_per_inf,
                    "start_date"            : start_date.isoformat(),
                    "end_date"              : end_date.isoformat(),
                    "submission_deadline"   : deadline.isoformat(),
                    "required_deliverables" : deliverables,
                    "hashtags"              : hashtags
                }

                try:
                    with st.spinner("⏳ ARIA تُنشئ الحملة وتُجدول Guardian Agent..."):
                        resp = requests.post(
                            f"{API_BASE}/campaigns/",
                            headers=HEADERS,
                            json=payload
                        )

                    if resp.status_code == 201:
                        data = resp.json()
                        st.success(f"✅ تم إنشاء الحملة بنجاح! رقم الحملة: #{data['id']}")
                        st.balloons()
                        st.markdown(f"""
                        <div style="background:#0a2e1a; border:1px solid #00ff88;
                                    border-radius:12px; padding:1rem; margin-top:1rem;">
                            <h4 style="color:#00ff88; margin:0;">
                                ✅ Guardian Agent جاهز
                            </h4>
                            <p style="color:#a0ffb0; font-size:13px; margin:6px 0 0 0;">
                                تم جدولة مراحل الحملة تلقائياً:
                                بدء التنفيذ → متابعة الأداء →
                                مراجعة المحتوى → تحرير الضمان المالي
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"❌ خطأ: {resp.status_code} — {resp.text[:100]}")

                except requests.exceptions.ConnectionError:
                    st.error("⚠️ تعذّر الاتصال بالخادم — تأكد من تشغيل Backend على المنفذ 8000")

# ══════════════════════════════════════════════════════════
# TAB 2 — ACTIVE CAMPAIGNS LIST
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📋 حملاتي الحالية")

    # Filter row
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_status = st.selectbox(
            "تصفية حسب الحالة",
            ["الكل", "نشطة", "مسودة", "قيد المراجعة", "مكتملة"]
        )
    with fc2:
        filter_niche = st.selectbox(
            "تصفية حسب المجال",
            ["الكل", "موضة", "طعام", "تقنية", "جمال", "رياضة"]
        )
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 تحديث", use_container_width=True):
            st.rerun()

    # ── Try live API first, fall back to demo data ──────────
    campaigns_data = []
    try:
        resp = requests.get(f"{API_BASE}/campaigns/", headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            raw = resp.json()
            for c in raw:
                status_map = {
                    "active": "🟢 نشطة", "draft": "🟡 مسودة",
                    "under_review": "🔵 قيد المراجعة", "completed": "✅ مكتملة"
                }
                campaigns_data.append({
                    "رقم الحملة"    : f"#C-{c['id']:03d}",
                    "العنوان"        : c.get("title_ar") or c.get("title_en") or "—",
                    "المجال"         : c.get("niche", "—"),
                    "الميزانية"      : f"{c.get('total_budget', 0):,.0f} JOD",
                    "الحالة"         : status_map.get(c.get("status","draft"), c.get("status","")),
                    "تاريخ الانتهاء" : c.get("end_date", "—"),
                    "Guardian"       : "✅ مجدول" if c.get("status") == "active" else "⏳ ينتظر"
                })
    except requests.exceptions.ConnectionError:
        pass

    # Demo fallback
    if not campaigns_data:
        campaigns_data = [
            {
                "رقم الحملة"    : "#C-001",
                "العنوان"        : "إطلاق عطر الربيع",
                "المجال"         : "موضة",
                "الميزانية"      : "800 JOD",
                "المؤثرون"       : "3/5",
                "الحالة"         : "🟢 نشطة",
                "نسبة الإنجاز"   : "60%",
                "تاريخ الانتهاء" : "2024-03-15",
                "Guardian"       : "✅ مجدول"
            },
            {
                "رقم الحملة"    : "#C-002",
                "العنوان"        : "عروض رمضان 2024",
                "المجال"         : "أسلوب حياة",
                "الميزانية"      : "1,500 JOD",
                "المؤثرون"       : "0/8",
                "الحالة"         : "🟡 مسودة",
                "نسبة الإنجاز"   : "0%",
                "تاريخ الانتهاء" : "2024-03-25",
                "Guardian"       : "⏳ ينتظر التفعيل"
            },
            {
                "رقم الحملة"    : "#C-003",
                "العنوان"        : "تطبيق توصيل الطعام",
                "المجال"         : "طعام",
                "الميزانية"      : "600 JOD",
                "المؤثرون"       : "5/5",
                "الحالة"         : "🔵 قيد المراجعة",
                "نسبة الإنجاز"   : "90%",
                "تاريخ الانتهاء" : "2024-02-28",
                "Guardian"       : "🔍 AI Auditor يراجع"
            },
            {
                "رقم الحملة"    : "#C-004",
                "العنوان"        : "ملابس الصيف الجديدة",
                "المجال"         : "موضة",
                "الميزانية"      : "300 JOD",
                "المؤثرون"       : "2/2",
                "الحالة"         : "✅ مكتملة",
                "نسبة الإنجاز"   : "100%",
                "تاريخ الانتهاء" : "2024-02-10",
                "Guardian"       : "💰 الضمان مُحرَّر"
            },
        ]

    df = pd.DataFrame(campaigns_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Campaign detail expander
    st.markdown("### 🔍 تفاصيل الحملة")
    selected_campaign = st.selectbox(
        "اختر حملة لعرض التفاصيل",
        ["#C-001 — إطلاق عطر الربيع",
         "#C-002 — عروض رمضان 2024",
         "#C-003 — تطبيق توصيل الطعام"]
    )

    if selected_campaign:
        with st.expander("📊 عرض التفاصيل الكاملة", expanded=True):
            dc1, dc2, dc3 = st.columns(3)
            dc1.metric("👁️ إجمالي الوصول",    "128,450",  "+12,000 هذا الأسبوع")
            dc2.metric("❤️ إجمالي التفاعلات", "8,920",    "+890 هذا الأسبوع")
            dc3.metric("🔗 نسبة التفاعل",      "6.94%",    "+0.3%")

            # Influencer assignment status
            st.markdown("**👥 المؤثرون المعيّنون:**")
            inf_status = [
                {"المؤثر": "سارة الأردنية", "الحالة": "✅ تم التسليم", "النقاط": "87.4", "المبلغ": "85 JOD"},
                {"المؤثر": "خالد المطبخ",   "الحالة": "⏳ قيد الإنتاج", "النقاط": "82.3", "المبلغ": "95 JOD"},
                {"المؤثر": "ريم الرياضية",  "الحالة": "🟡 مدعو",       "النقاط": "66.1", "المبلغ": "55 JOD"},
            ]
            st.dataframe(pd.DataFrame(inf_status),
                         use_container_width=True, hide_index=True)

            # Action buttons
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if st.button("✅ الموافقة على جميع المحتوى",
                             use_container_width=True, type="primary"):
                    st.success("✅ تم إرسال أمر الموافقة — Guardian سيُحرر الضمان")
            with ac2:
                if st.button("🔍 طلب مراجعة AI Auditor",
                             use_container_width=True):
                    st.info("🤖 AI Auditor يراجع المحتوى الآن...")
            with ac3:
                if st.button("⚠️ رفع نزاع",
                             use_container_width=True, type="secondary"):
                    st.warning("⚠️ سيتم تجميد الضمان وإشعار فريق الدعم")

# ══════════════════════════════════════════════════════════
# TAB 3 — CAMPAIGN ANALYTICS
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 تحليلات أداء الحملات")

    try:
        import plotly.express as px
        import plotly.graph_objects as go

        # ROI Chart
        campaigns_roi = pd.DataFrame({
            "الحملة"        : ["عطر الربيع", "عروض الشتاء", "تطبيق الطعام",
                                "ملابس الصيف", "إطلاق المتجر"],
            "الإنفاق (JOD)" : [800, 1200, 600, 300, 950],
            "العائد (JOD)"  : [3200, 4800, 2100, 1050, 4200],
            "ROI %"         : [300, 300, 250, 250, 342],
        })

        fig_roi = px.bar(
            campaigns_roi,
            x="الحملة",
            y=["الإنفاق (JOD)", "العائد (JOD)"],
            barmode="group",
            color_discrete_map={
                "الإنفاق (JOD)": "#e94560",
                "العائد (JOD)" : "#00ff88"
            },
            title="مقارنة الإنفاق والعائد لكل حملة"
        )
        fig_roi.update_layout(
            paper_bgcolor="#1a1a2e",
            plot_bgcolor="#1a1a2e",
            font=dict(color="white"),
            height=320,
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_roi, use_container_width=True)

        # Platform Distribution Pie
        pie_col1, pie_col2 = st.columns(2)

        with pie_col1:
            fig_pie = px.pie(
                names=["Instagram", "TikTok", "YouTube"],
                values=[45, 38, 17],
                title="توزيع المنصات",
                color_discrete_sequence=["#533483", "#e94560", "#0f3460"]
            )
            fig_pie.update_layout(
                paper_bgcolor="#1a1a2e",
                font=dict(color="white"),
                height=280,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with pie_col2:
            fig_niche = px.pie(
                names=["موضة", "طعام", "تقنية", "جمال", "أخرى"],
                values=[30, 25, 20, 15, 10],
                title="توزيع المجالات",
                color_discrete_sequence=["#ffd700", "#ff8c00", "#533483", "#e94560", "#0f3460"]
            )
            fig_niche.update_layout(
                paper_bgcolor="#1a1a2e",
                font=dict(color="white"),
                height=280,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig_niche, use_container_width=True)

    except ImportError:
        st.warning("⚠️ plotly not installed — run: pip install plotly")
        st.info("تحليلات الحملات تتطلب مكتبة plotly")
