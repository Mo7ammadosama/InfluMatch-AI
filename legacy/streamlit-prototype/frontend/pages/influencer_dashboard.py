"""
WaslAI.jo — Influencer Dashboard
Available Campaigns, Active Deals, Earnings, Profile
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
    greeting = f"أهلاً {name} 🌟" if is_ar else f"Hello, {name} 🌟"
    st.header(greeting)

    tab_labels = (
        ["🔍 الحملات المتاحة", "🤝 صفقاتي", "💰 الأرباح", "⚙️ ملفي الشخصي"]
        if is_ar else
        ["🔍 Available Campaigns", "🤝 My Deals", "💰 Earnings", "⚙️ My Profile"]
    )
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _browse_campaigns(is_ar)
    with tabs[1]:
        _my_deals(is_ar)
    with tabs[2]:
        _earnings(is_ar)
    with tabs[3]:
        _profile(is_ar)


def _browse_campaigns(is_ar: bool):
    st.subheader("الحملات المتاحة" if is_ar else "Available Campaigns")
    try:
        r = httpx.get(
            f"{API_BASE}/api/v1/campaigns/",
            headers=_headers(),
            params={"status_filter": "active"},
            timeout=10,
        )
        campaigns = r.json() if r.status_code == 200 else []
    except Exception:
        campaigns = []

    if campaigns:
        for c in campaigns:
            with st.expander(f"📢 {c['title']} | {c['total_budget_jod']} JOD"):
                st.write(c.get("description") or ("لا يوجد وصف" if is_ar else "No description"))
                col1, col2 = st.columns(2)
                col1.metric("الميزانية" if is_ar else "Budget", f"{c['total_budget_jod']} JOD")
                col2.metric("الحد الأدنى للمتابعين" if is_ar else "Min Followers", f"{c['min_followers']:,}")
                if st.button("تقديم طلب" if is_ar else "Apply", key=f"apply_{c['id']}"):
                    st.info("ميزة التقديم قريباً" if is_ar else "Apply feature coming soon.")
    else:
        st.info("لا توجد حملات نشطة حالياً." if is_ar else "No active campaigns available.")


def _my_deals(is_ar: bool):
    st.subheader("صفقاتي" if is_ar else "My Deals")
    try:
        r = httpx.get(f"{API_BASE}/api/v1/deals/my", headers=_headers(), timeout=10)
        deals = r.json() if r.status_code == 200 else []
        if deals:
            df = pd.DataFrame([{
                "ID": d["id"][:8],
                "الحالة" if is_ar else "Status": d["status"],
                "المبلغ (JOD)" if is_ar else "Amount (JOD)": d["total_amount_jod"],
            } for d in deals])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد صفقات بعد." if is_ar else "No deals yet.")
    except Exception as e:
        st.error(str(e))


def _earnings(is_ar: bool):
    st.subheader("الأرباح" if is_ar else "Earnings")
    st.info("لوحة الأرباح قريباً" if is_ar else "Earnings dashboard coming soon.")


def _profile(is_ar: bool):
    st.subheader("ملفي الشخصي" if is_ar else "My Profile")
    st.json(st.session_state.user or {})
