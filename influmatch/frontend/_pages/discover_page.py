"""Discover Influencers page — Premium UI v2"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t


def render():
    lang = st.session_state.get("lang", "ar")
    role = st.session_state.get("role", "")

    # ── HERO SEARCH BAR ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="search-container">
      <div style="text-align:center;margin-bottom:1.5rem">
        <div style="font-size:1.5rem;font-weight:800;
                    background:linear-gradient(135deg,#f59e0b,#8b5cf6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent">
          🔍 ابحث عن المؤثر المناسب لعملك
        </div>
        <div style="color:#6b7280;font-size:0.85rem;margin-top:0.3rem">
          Find the Perfect Influencer — Powered by ARIA AI
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    col_search, col_btn = st.columns([5, 1])
    with col_search:
        brief = st.text_input(
            "",
            placeholder="مثال: مؤثرة في عمّان تهتم بالمكياج ومتابعوها بنات / e.g. female makeup influencer in Amman",
            label_visibility="collapsed",
            key="search_brief",
        )
    with col_btn:
        search_clicked = st.button("🔍 بحث", use_container_width=True, type="primary")

    # Filters — row 1
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        niche_filter = st.selectbox(
            "التخصص",
            ["الكل", "Fashion", "Food", "Tech", "Beauty", "Fitness",
             "Travel", "Gaming", "Education", "Lifestyle", "Sports"],
        )
    with fc2:
        city_filter = st.text_input("المدينة", placeholder="عمان، إربد...")
    with fc3:
        budget_max = st.number_input("الحد الأقصى للميزانية (JOD)", min_value=0, value=500, step=50)
    with fc4:
        tier_filter = st.selectbox("الـ Tier", ["الكل", "PLATINUM", "GOLD", "SILVER", "BRONZE"])

    # Filters — row 2: audience demographics
    fd1, fd2, fd3 = st.columns([2, 2, 4])
    with fd1:
        gender_filter = st.selectbox(
            "🚻 جمهور الجنس",
            ["الكل", "إناث", "ذكور", "مختلط"],
            key="disc_gender",
        )
    with fd2:
        age_filter = st.selectbox(
            "🎂 الفئة العمرية",
            ["الكل", "18-24", "25-34", "35+"],
            key="disc_age",
        )
    with fd3:
        st.markdown(
            "<div style='padding-top:1.9rem;font-size:0.72rem;color:#6b7280'>"
            "💡 فلاتر الديموغرافيا تعمل عند إدخال وصف أو تفعيل بحث ذكي</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Fetch results
    influencers = []
    if search_clicked or brief or niche_filter != "الكل" or city_filter or gender_filter != "الكل" or age_filter != "الكل":
        if brief.strip() or gender_filter != "الكل" or age_filter != "الكل":
            s, results_data = api_post("/api/influencers/smart-search", json={
                "brief"           : brief,
                "city"            : city_filter,
                "budget_max"      : budget_max,
                "audience_gender" : "" if gender_filter == "الكل" else gender_filter,
                "audience_age"    : "" if age_filter    == "الكل" else age_filter,
                "top_k"           : 12,
            })
            influencers = results_data.get("results", []) if s == 200 else []
            if s == 200 and influencers:
                st.markdown(
                    f"<div style='color:#00ff88;font-size:0.85rem;margin-bottom:1rem'>"
                    f"✨ وجد ARIA {len(influencers)} مؤثر مناسب لطلبك</div>",
                    unsafe_allow_html=True,
                )
        else:
            params = {}
            if niche_filter != "الكل": params["niche"] = niche_filter
            if city_filter:            params["city"]  = city_filter
            if tier_filter != "الكل": params["tier"]  = tier_filter
            influencers = api_list("/api/influencers", params=params)
    else:
        influencers = api_list("/api/influencers", params={"limit": 12})

    if not influencers:
        st.info("لا توجد نتائج. جرّب تغيير الفلاتر أو اكتب وصفاً مختلفاً.")
        return

    # Display in 3-column grid
    cols = st.columns(3)
    for i, inf in enumerate(influencers):
        with cols[i % 3]:
            tier        = inf.get("aria_tier", "UNRANKED") or "UNRANKED"
            score       = float(inf.get("aria_score") or 0)
            handle      = inf.get("instagram_handle") or inf.get("tiktok_handle") or "—"
            followers   = int(inf.get("instagram_followers") or 0)
            engagement  = float(inf.get("instagram_engagement_rate") or 0)
            rate        = float(inf.get("rate_per_post") or 0)
            available   = inf.get("is_available", True)
            match_score = inf.get("match_score", "")

            avail_color = "#00ff88" if available else "#ef4444"
            avail_text  = "متاح ✓"  if available else "محجوز ✗"

            match_badge = (
                f'<span style="color:#f59e0b;font-size:0.7rem;border:1px solid rgba(245,158,11,0.3);'
                f'padding:0.2rem 0.6rem;border-radius:10px">⚡ {match_score}% match</span>'
                if match_score else ""
            )

            # ── Demographics mini-display ─────────────────────────────────
            gender_data = inf.get("audience_gender_split") or {}
            age_data    = inf.get("audience_age_split")    or {}
            demo_html   = ""
            if gender_data:
                female_pct = gender_data.get("female", 0)
                male_pct   = gender_data.get("male", 100 - female_pct)
                demo_html += (
                    f'<div style="margin-top:0.6rem">'
                    f'<div style="font-size:0.65rem;color:#8b5cf6;margin-bottom:0.3rem">👥 الجمهور</div>'
                    f'<div style="display:flex;gap:0.3rem;align-items:center">'
                    f'<div style="background:rgba(236,72,153,0.3);border-radius:4px;height:6px;'
                    f'width:{female_pct}%;min-width:4px" title="إناث {female_pct}%"></div>'
                    f'<div style="background:rgba(59,130,246,0.3);border-radius:4px;height:6px;'
                    f'width:{male_pct}%;min-width:4px" title="ذكور {male_pct}%"></div>'
                    f'</div>'
                    f'<div style="display:flex;gap:1rem;margin-top:0.2rem">'
                    f'<span style="font-size:0.62rem;color:#ec4899">♀ {female_pct}%</span>'
                    f'<span style="font-size:0.62rem;color:#3b82f6">♂ {male_pct}%</span>'
                    f'</div></div>'
                )
            if age_data:
                age_items = " · ".join(
                    f'<span style="font-size:0.62rem;color:#a78bfa">{k}: {v}%</span>'
                    for k, v in sorted(age_data.items())
                )
                demo_html += (
                    f'<div style="margin-top:0.4rem;font-size:0.62rem;color:#6b7280">'
                    f'🎂 {age_items}</div>'
                )

            st.markdown(f"""
            <div class="inf-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem">
                <div>
                  <div style="font-weight:800;font-size:1rem">@{handle}</div>
                  <div style="color:#6b7280;font-size:0.75rem">{inf.get('niche','—')} · {inf.get('city','—')}</div>
                </div>
                <div style="text-align:center">
                  <div class="score-ring" style="width:50px;height:50px;font-size:0.9rem;border:3px solid #8b5cf6">{score:.0f}</div>
                </div>
              </div>
              <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem">
                <span class="tier-badge tier-{tier}">{tier}</span>
                <span style="color:{avail_color};font-size:0.75rem;border:1px solid {avail_color};
                             padding:0.2rem 0.6rem;border-radius:10px">{avail_text}</span>
                {match_badge}
              </div>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{followers/1000:.1f}K</div>
                  <div class="stat-label">Followers</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{engagement:.1f}%</div>
                  <div class="stat-label">Engagement</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{rate:.0f} JOD</div>
                  <div class="stat-label">Rate/Post</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{score:.0f}</div>
                  <div class="stat-label">ARIA Score</div>
                </div>
              </div>
              {demo_html}
            </div>""", unsafe_allow_html=True)

            if role == "merchant" and available:
                if st.button("📅 احجز الآن", key=f"book_{inf.get('id', i)}", use_container_width=True):
                    st.session_state["booking_influencer"] = inf
                    st.session_state["page"] = "booking_wizard"
                    st.rerun()
            elif role == "merchant" and not available:
                st.button("محجوز", key=f"unavail_{inf.get('id', i)}", disabled=True, use_container_width=True)
