"""Campaigns Browser — All Roles"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}

st.markdown("## 📢 الحملات — Campaigns")

# ── Filters ────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.selectbox("Status", ["All", "draft", "active", "in_progress", "completed", "disputed"])
with col2:
    niche_filter = st.text_input("Niche", placeholder="fashion, food, tech...")
with col3:
    search_term = st.text_input("Search", placeholder="Campaign title...")

st.divider()

# ── Load Campaigns ──────────────────────────────────────────
try:
    params = {}
    if status_filter != "All":
        params["status"] = status_filter

    resp = requests.get(f"{API_BASE}/campaigns/", headers=HEADERS, params=params, timeout=5)

    if resp.status_code == 200:
        campaigns = resp.json()

        # Client-side filters
        if niche_filter:
            campaigns = [c for c in campaigns if niche_filter.lower() in (c.get("niche") or "").lower()]
        if search_term:
            campaigns = [c for c in campaigns
                         if search_term.lower() in (c.get("title_en") or c.get("title_ar") or "").lower()]

        if not campaigns:
            st.info("لا توجد حملات — No campaigns found")
        else:
            st.caption(f"Found {len(campaigns)} campaigns")

            for camp in campaigns:
                status = camp.get("status", "draft")
                status_colors = {
                    "draft": "#888", "active": "#00ff88", "in_progress": "#ffd700",
                    "under_review": "#f0a500", "completed": "#533483",
                    "disputed": "#e94560", "cancelled": "#555"
                }
                color = status_colors.get(status, "#888")

                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    with c1:
                        title = camp.get("title_en") or camp.get("title_ar") or "—"
                        st.markdown(f"**{title}**")
                        st.caption(f"Niche: {camp.get('niche','—')} | ID: {camp.get('id')}")
                    with c2:
                        st.markdown(f"<span style='color:{color};font-weight:bold'>{status.upper()}</span>",
                                    unsafe_allow_html=True)
                    with c3:
                        budget = camp.get("total_budget", 0)
                        st.metric("Budget", f"{budget:,.0f} JOD")
                    with c4:
                        role = st.session_state.get("role")
                        if role == "merchant" and status == "draft":
                            if st.button("▶️ Activate", key=f"act_{camp['id']}"):
                                ar = requests.patch(
                                    f"{API_BASE}/campaigns/{camp['id']}/activate",
                                    headers=HEADERS, timeout=5
                                )
                                if ar.status_code == 200:
                                    st.success("Campaign activated!")
                                    st.rerun()
                                else:
                                    st.error(ar.text)
                        elif role == "influencer" and status == "active":
                            st.button("🌟 Apply", key=f"apply_{camp['id']}")
                    st.divider()
    else:
        st.error(f"API Error: {resp.status_code}")

except requests.exceptions.ConnectionError:
    st.warning("⚠️ Backend offline — showing demo data")
    demo = pd.DataFrame([
        {"Title": "Summer Fashion Collection", "Status": "active",  "Budget (JOD)": 2500, "Niche": "fashion"},
        {"Title": "Ramadan Food Campaign",     "Status": "draft",   "Budget (JOD)": 1800, "Niche": "food"},
        {"Title": "Tech Product Launch",       "Status": "completed","Budget (JOD)": 3200, "Niche": "tech"},
    ])
    st.dataframe(demo, use_container_width=True)
