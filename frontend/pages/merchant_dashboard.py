"""
InfluMatch.jo — Merchant Dashboard
Campaigns, AI Matching, Deals, Wallet
"""
import streamlit as st
import httpx
import os
import plotly.express as px
import pandas as pd

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def render():
    lang = st.session_state.get("language", "ar")
    is_ar = lang == "ar"
    user = st.session_state.user or {}

    name = user.get("full_name_ar") or user.get("full_name", "")
    greeting = f"مرحباً {name} 👋" if is_ar else f"Welcome, {name} 👋"
    st.header(greeting)

    tab_labels = (
        ["📢 حملاتي", "🤖 التطابق الذكي", "🤝 الصفقات", "💰 المحفظة", "⚙️ الملف الشخصي"]
        if is_ar else
        ["📢 My Campaigns", "🤖 AI Matching", "🤝 Deals", "💰 Wallet", "⚙️ Profile"]
    )
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _campaigns_tab(is_ar)
    with tabs[1]:
        _matching_tab(is_ar)
    with tabs[2]:
        _deals_tab(is_ar)
    with tabs[3]:
        _wallet_tab(is_ar)
    with tabs[4]:
        _profile_tab(is_ar)


def _campaigns_tab(is_ar: bool):
    st.subheader("حملاتي الإعلانية" if is_ar else "My Campaigns")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/campaigns/my", headers=_headers(), timeout=10)
        campaigns = r.json() if r.status_code == 200 else []
    except Exception:
        campaigns = []

    if campaigns:
        df = pd.DataFrame([{
            "ID": c["id"][:8],
            "العنوان" if is_ar else "Title": c["title"],
            "الميزانية (JOD)" if is_ar else "Budget (JOD)": c["total_budget_jod"],
            "الحالة" if is_ar else "Status": c["status"],
        } for c in campaigns])
        st.dataframe(df, use_container_width=True)

        status_counts = pd.DataFrame(campaigns)["status"].value_counts().reset_index()
        fig = px.pie(status_counts, names="status", values="count", title="توزيع الحملات" if is_ar else "Campaign Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد حملات بعد." if is_ar else "No campaigns yet.")

    with st.expander("➕ إنشاء حملة جديدة" if is_ar else "➕ Create New Campaign"):
        with st.form("new_campaign_form"):
            title = st.text_input("عنوان الحملة" if is_ar else "Campaign Title")
            budget = st.number_input("الميزانية (JOD)" if is_ar else "Budget (JOD)", min_value=50.0, step=10.0)
            categories = st.multiselect("الفئات" if is_ar else "Categories",
                                        ["fashion", "food", "tech", "beauty", "fitness", "lifestyle", "travel"])
            platforms = st.multiselect("المنصات" if is_ar else "Platforms",
                                       ["instagram", "tiktok", "youtube", "twitter", "snapchat"])
            min_followers = st.number_input("الحد الأدنى للمتابعين" if is_ar else "Min Followers", min_value=1000, step=500, value=5000)
            submitted = st.form_submit_button("إنشاء" if is_ar else "Create", type="primary")

        if submitted and title:
            try:
                r = httpx.post(
                    f"{API_BASE}/api/v1/campaigns/",
                    headers=_headers(),
                    json={
                        "title": title, "total_budget_jod": budget,
                        "target_categories": categories, "required_platforms": platforms,
                        "min_followers": min_followers,
                    },
                    timeout=10,
                )
                if r.status_code == 201:
                    st.success("تم إنشاء الحملة ✅" if is_ar else "Campaign created ✅")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as e:
                st.error(str(e))


def _matching_tab(is_ar: bool):
    st.subheader("التطابق الذكي بالذكاء الاصطناعي" if is_ar else "AI-Powered Matching")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/campaigns/my", headers=_headers(), timeout=10)
        campaigns = r.json() if r.status_code == 200 else []
    except Exception:
        campaigns = []

    if not campaigns:
        st.info("أنشئ حملة أولاً لاستخدام المطابقة الذكية." if is_ar else "Create a campaign first to use AI matching.")
        return

    campaign_options = {c["title"]: c["id"] for c in campaigns}
    selected_title = st.selectbox("اختر الحملة" if is_ar else "Select Campaign", list(campaign_options.keys()))
    top_k = st.slider("عدد النتائج" if is_ar else "Number of Results", 5, 20, 10)

    if st.button("🤖 ابدأ المطابقة" if is_ar else "🤖 Start Matching", type="primary"):
        with st.spinner("جارٍ التحليل..." if is_ar else "Analyzing..."):
            try:
                r = httpx.post(
                    f"{API_BASE}/api/v1/ai/match",
                    headers=_headers(),
                    json={"campaign_id": campaign_options[selected_title], "top_k": top_k},
                    timeout=30,
                )
                if r.status_code == 200:
                    matches = r.json()
                    if matches:
                        st.success(f"تم العثور على {len(matches)} مؤثر مناسب" if is_ar else f"Found {len(matches)} matching influencers")
                        for m in matches:
                            inf = m["influencer"]
                            with st.container():
                                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                                c1.write(f"**{inf['display_name']}** | {inf['city']}")
                                c2.metric("متابعون" if is_ar else "Followers", f"{inf['total_followers']:,}")
                                c3.metric("نقاط التطابق" if is_ar else "Match Score", f"{m['score']}/100")
                                c4.write(f"#{m['rank']}")
                    else:
                        st.warning("لا توجد تطابقات" if is_ar else "No matches found")
                else:
                    st.error(r.json().get("detail", "Matching failed"))
            except Exception as e:
                st.error(str(e))


def _deals_tab(is_ar: bool):
    st.subheader("الصفقات النشطة" if is_ar else "Active Deals")
    try:
        r = httpx.get(f"{API_BASE}/api/v1/deals/my", headers=_headers(), timeout=10)
        deals = r.json() if r.status_code == 200 else []
        if deals:
            for d in deals:
                st.write(f"Deal `{d['id'][:8]}` | {d['status']} | {d['total_amount_jod']} JOD")
        else:
            st.info("لا توجد صفقات بعد." if is_ar else "No deals yet.")
    except Exception as e:
        st.error(str(e))


def _wallet_tab(is_ar: bool):
    st.subheader("محفظتي" if is_ar else "My Wallet")
    st.info("ميزة المحفظة قريباً" if is_ar else "Wallet feature coming soon.")


def _profile_tab(is_ar: bool):
    st.subheader("الملف الشخصي" if is_ar else "Profile")
    user = st.session_state.user or {}
    st.json(user)
