import streamlit as st
import requests

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

st.markdown("""
<div style="background:linear-gradient(135deg,#0a1e3e,#1a2e5e);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">📄 العقود الذكية — Smart Contracts</h2>
    <p style="color:#80a0ff; margin:5px 0 0 0;">
        مدعومة بـ ARIA RAG | متوافقة مع القانون الأردني
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ إنشاء عقد جديد", "📂 عقودي السابقة"])

with tab1:
    st.markdown("### ✍️ توليد عقد ذكي بالذكاء الاصطناعي")
    st.info(
        "🤖 **ARIA RAG** ستولّد عقداً قانونياً متوافقاً مع التشريعات الأردنية "
        "استناداً إلى قاعدة المعرفة المضمّنة في النظام."
    )

    c1, c2 = st.columns(2)
    with c1:
        merchant_name     = st.text_input("🏪 اسم التاجر / المنشأة")
        campaign_title    = st.text_input("📢 عنوان الحملة")
        budget            = st.number_input("💰 قيمة العقد (JOD)", min_value=10.0, value=500.0)
        deliverables      = st.multiselect("📦 التسليمات المطلوبة",
                                           ["منشور", "ستوري", "ريل",
                                            "Post", "Story", "Reel"])
    with c2:
        influencer_name   = st.text_input("🌟 اسم المؤثر")
        campaign_niche    = st.selectbox("🎯 مجال الحملة",
                                         ["موضة", "طعام", "تقنية",
                                          "جمال", "رياضة", "سفر"])
        deadline_days     = st.slider("📅 مدة التنفيذ (أيام)", 3, 30, 7)
        language          = st.radio("🌐 لغة العقد",
                                     ["العربية", "English"], horizontal=True)

    if st.button("🤖 توليد العقد بـ ARIA RAG",
                 type="primary", use_container_width=True):
        if merchant_name and influencer_name and campaign_title:
            with st.spinner("⏳ ARIA تُنشئ عقداً متوافقاً مع القانون الأردني..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/contracts/generate",
                        headers=HEADERS,
                        json={
                            "merchant_name"    : merchant_name,
                            "influencer_name"  : influencer_name,
                            "campaign_details" : {
                                "title"        : campaign_title,
                                "niche"        : campaign_niche,
                                "budget_jod"   : budget,
                                "deliverables" : deliverables,
                                "deadline_days": deadline_days,
                            },
                            "language": "ar" if language == "العربية" else "en"
                        }
                    )
                    if resp.status_code == 200:
                        contract_text = resp.json().get("contract", "")
                        st.success("✅ تم توليد العقد بنجاح!")
                        st.markdown(
                            f"""<div style="background:#1a1a2e; border:1px solid #533483;
                                border-radius:12px; padding:1.5rem; direction:rtl;
                                white-space:pre-wrap; color:white; font-size:14px;
                                line-height:1.8; max-height:400px; overflow-y:auto;">
                                {contract_text}
                            </div>""",
                            unsafe_allow_html=True
                        )
                        st.download_button(
                            "📥 تحميل العقد",
                            contract_text,
                            file_name=f"contract_{merchant_name}_{influencer_name}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ خطأ في التوليد: {resp.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ تعذّر الاتصال بالخادم — تأكد من تشغيل Backend")
        else:
            st.warning("⚠️ يرجى تعبئة جميع الحقول الإلزامية")

with tab2:
    st.markdown("### 📂 عقودي المنجزة")
    contracts = [
        {"رقم العقد" : "CNT-2024-001", "id": 1, "الحملة": "عطر الربيع",
         "المؤثر"   : "سارة الأردنية", "القيمة": "510 JOD",
         "الحالة"   : "موقّع", "التاريخ": "2024-02-10"},
        {"رقم العقد" : "CNT-2024-002", "id": 2, "الحملة": "عروض رمضان",
         "المؤثر"   : "أحمد التقني",  "القيمة": "800 JOD",
         "الحالة"   : "في الانتظار", "التاريخ": "2024-02-15"},
    ]
    import pandas as pd
    display_cols = ["رقم العقد", "الحملة", "المؤثر", "القيمة", "الحالة", "التاريخ"]
    st.dataframe(pd.DataFrame(contracts)[display_cols], use_container_width=True, hide_index=True)

    st.markdown("#### 📄 تحميل عقد بصيغة PDF")
    contract_id_pdf = st.number_input("رقم العقد للتحميل", min_value=1, value=1, step=1, key="pdf_id")
    if st.button("📄 تحميل PDF", use_container_width=True):
        with st.spinner("جارٍ إنشاء PDF ..."):
            try:
                r = requests.get(
                    f"{API_BASE}/contracts/{contract_id_pdf}/pdf", headers=HEADERS
                )
                if r.status_code == 200:
                    st.download_button(
                        label     = "⬇️ حفظ PDF",
                        data      = r.content,
                        file_name = f"contract_{contract_id_pdf}.pdf",
                        mime      = "application/pdf",
                        use_container_width=True,
                    )
                    st.success("تم إنشاء PDF بنجاح")
                else:
                    st.error(f"خطأ {r.status_code}: {r.text[:200]}")
            except requests.exceptions.ConnectionError:
                st.error("تعذّر الاتصال بالخادم — تأكد من تشغيل Backend")
# ============================================================