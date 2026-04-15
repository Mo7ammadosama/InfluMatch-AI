"""Landing / Home page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t

def render_home():
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 2rem">
      <div style="font-size:3.5rem;font-weight:900;
                  background:linear-gradient(135deg,#f59e0b,#8b5cf6,#ef4444);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  line-height:1.1;margin-bottom:1rem">
        InfluMatch.jo
      </div>
      <div style="font-size:1.2rem;color:#a0a0b0;margin-bottom:0.5rem">
        منصة التسويق بالمؤثرين — مدعومة بالذكاء الاصطناعي
      </div>
      <div style="font-size:0.9rem;color:#6b7280">
        Jordan's First AI-Powered Influencer Marketing Platform
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc, color in [
        (c1, "🏪", "للتجار",   "أطلق حملاتك، اختر المؤثر المناسب بالذكاء الاصطناعي",      "#f59e0b"),
        (c2, "🌟", "للمؤثرين", "احصل على فرص حقيقية مع ضمان الدفع عبر Escrow",            "#8b5cf6"),
        (c3, "🔒", "ضمان مالي","نظام Escrow يحمي حقوق الطرفين حتى اكتمال الحملة",         "#00ff88"),
    ]:
        col.markdown(f"""
        <div class="aria-card" style="text-align:center;border-top:3px solid {color}">
          <div style="font-size:2rem;margin-bottom:0.5rem">{icon}</div>
          <div style="font-size:1rem;font-weight:700;color:{color};margin-bottom:0.5rem">{title}</div>
          <div style="color:#a0a0b0;font-size:0.85rem">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
            st.session_state["page"] = "login"
            st.rerun()
    with c2:
        if st.button("إنشاء حساب", use_container_width=True):
            st.session_state["page"] = "register"
            st.rerun()
