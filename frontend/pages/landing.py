"""
InfluMatch.jo — Landing Page
Hero section, value proposition, CTA
"""
import streamlit as st


def render():
    lang = st.session_state.get("language", "ar")
    is_ar = lang == "ar"

    if is_ar:
        st.markdown("""
<div style="text-align: right; direction: rtl;">
    <h1>🎯 InfluMatch.jo</h1>
    <h2>منصة التسويق عبر المؤثرين المدعومة بالذكاء الاصطناعي</h2>
    <p style="font-size: 1.2em;">ربط التجار الأردنيين بالمؤثرين المناسبين — بشكل تلقائي وذكي</p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
# 🎯 InfluMatch.jo
## AI-Powered Influencer Marketing Platform
**Connecting Jordanian Merchants with the right Influencers — Automatically.**
""")

    col1, col2, col3 = st.columns(3)
    with col1:
        metric = "تاجر مسجل" if is_ar else "Registered Merchants"
        st.metric(metric, "500+", "+12%")
    with col2:
        metric = "مؤثر نشط" if is_ar else "Active Influencers"
        st.metric(metric, "2,000+", "+8%")
    with col3:
        metric = "حملة مكتملة" if is_ar else "Completed Campaigns"
        st.metric(metric, "1,200+", "+25%")

    st.divider()

    col_m, col_i = st.columns(2)
    with col_m:
        label = "🏪 أنا تاجر — ابدأ الآن" if is_ar else "🏪 I'm a Merchant — Start Now"
        if st.button(label, use_container_width=True, type="primary", key="merchant_cta"):
            st.session_state.page = "register"
            st.session_state.register_role = "merchant"
            st.rerun()
    with col_i:
        label = "🌟 أنا مؤثر — انضم الآن" if is_ar else "🌟 I'm an Influencer — Join Now"
        if st.button(label, use_container_width=True, type="secondary", key="influencer_cta"):
            st.session_state.page = "register"
            st.session_state.register_role = "influencer"
            st.rerun()
