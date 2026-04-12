"""Discover Influencers page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t
from ..components.cards.influencer_card import render_influencer_card

def render():
    lang = st.session_state.get("lang", "ar")
    st.markdown(f"## {'🔍 اكتشف المؤثرين' if lang=='ar' else '🔍 Discover Influencers'}")

    # Filters
    with st.expander(f"{'🔧 الفلاتر' if lang=='ar' else '🔧 Filters'}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            niche = st.selectbox("Niche", ["All", "Fashion", "Food", "Tech", "Beauty",
                                            "Fitness", "Travel", "Gaming", "Education"])
        with col2:
            city = st.selectbox("City", ["All", "Amman", "Zarqa", "Irbid", "Aqaba"])
        with col3:
            min_score = st.slider("Min ARIA Score", 0, 100, 0)
        with col4:
            tier = st.selectbox("Tier", ["All", "PLATINUM", "GOLD", "SILVER", "BRONZE"])

    params = {}
    if niche != "All": params["niche"] = niche
    if city != "All": params["city"] = city
    if min_score > 0: params["min_score"] = min_score
    if tier != "All": params["tier"] = tier

    influencers = api_get("/api/influencers", params=params) or []

    if not influencers:
        st.info("No influencers found / لا يوجد مؤثرون مطابقون")
        return

    st.markdown(f"**{len(influencers)} influencers found**")

    for inf in influencers:
        invited = render_influencer_card(inf, show_invite=True)
        if invited:
            st.success(f"✅ Invite sent to @{inf.get('instagram_handle', '')}")
