"""Merchant Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post
from ..utils.i18n import t
from ..components.cards.campaign_card import render_campaign_card

def render():
    lang = st.session_state.get("lang", "ar")
    user = st.session_state.get("user", {})

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1.5rem">
        <span style="font-size:2rem">🏢</span>
        <div>
            <h2 style="margin:0;color:#A78BFA">{'لوحة تحكم التاجر' if lang=='ar' else "Merchant Dashboard"}</h2>
            <p style="margin:0;color:#64748B;font-size:0.85rem">{(user.get('full_name_en') or user.get('full_name_ar') or '') if user else ''}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    merchant = api_get("/api/merchants/me") or {}
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("💰", f"{merchant.get('total_spent_jod',0):,.0f} JOD", "Total Spent / إجمالي الإنفاق"),
        ("💎", str(merchant.get("loyalty_points", 0)), "Points / النقاط"),
        ("📢", str(merchant.get("total_campaigns", 0)), "Campaigns / الحملات"),
        ("⭐", str(merchant.get("active_campaigns", 0)), "Active / نشط"),
    ]
    for col, (icon, val, lbl) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # My Campaigns
    tab1, tab2 = st.tabs(["📢 My Campaigns / حملاتي", "➕ New Campaign / حملة جديدة"])

    with tab1:
        campaigns = api_get("/api/campaigns") or []
        if not campaigns:
            st.info("No campaigns yet. Create your first! / لا توجد حملات بعد. أنشئ حملتك الأولى!")
        else:
            for c in campaigns[:10]:
                render_campaign_card(c)

    with tab2:
        _render_create_campaign(lang)


def _render_create_campaign(lang):
    with st.form("new_campaign_form"):
        st.markdown(f"#### {'إنشاء حملة جديدة' if lang=='ar' else 'Create New Campaign'}")
        title_en = st.text_input("Title (English)", placeholder="Ramadan Special Campaign")
        title_ar = st.text_input("العنوان (عربي)", placeholder="حملة رمضان الخاصة")
        desc_en = st.text_area("Description (English)", height=80)
        desc_ar = st.text_area("الوصف (عربي)", height=80)
        col1, col2 = st.columns(2)
        with col1:
            niche = st.selectbox("Niche / التخصص", [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
            total_budget = st.number_input("Budget (JOD) / الميزانية", min_value=50.0, value=500.0, step=50.0)
        with col2:
            budget_per_influencer = st.number_input("Per Influencer (JOD)", min_value=10.0, value=100.0, step=10.0)
            min_followers = st.number_input("Min Followers", min_value=1000, value=5000, step=1000)

        submitted = st.form_submit_button("🚀 Launch Campaign / إطلاق الحملة", use_container_width=True)
        if submitted:
            if not title_en and not title_ar:
                st.error("Title required / العنوان مطلوب")
            else:
                status, resp = api_post("/api/campaigns/", json={
                    "title_en": title_en, "title_ar": title_ar,
                    "description_en": desc_en, "description_ar": desc_ar,
                    "niche": niche, "total_budget": total_budget,
                    "budget_per_influencer": budget_per_influencer,
                    "min_followers": int(min_followers)
                })
                if status in (200, 201):
                    st.success(f"✅ Campaign created! / تم إنشاء الحملة!")
                    st.rerun()
                else:
                    st.error(f"❌ {resp.get('detail', 'Error')}")
