"""Influencer card component"""
import streamlit as st

TIER_COLORS = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render_influencer_card(inf: dict, show_invite: bool = False) -> bool:
    """Returns True if Invite button was clicked."""
    tier = inf.get("aria_tier", "UNRANKED")
    icon, bg, fg = TIER_COLORS.get(tier, TIER_COLORS["UNRANKED"])
    score = inf.get("aria_score", 0)
    ig_followers = inf.get("instagram_followers", 0)
    ig_er = inf.get("instagram_engagement_rate", 0)
    niche = inf.get("niche", "—")
    city = inf.get("city", "Amman")
    rate = inf.get("rate_per_post", 0)
    handle = inf.get("instagram_handle", "—")

    invited = False
    with st.container():
        st.markdown(f"""
        <div class="aria-card" style="border-radius:12px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div style="font-size:1.05rem;font-weight:700">@{handle}</div>
                    <div style="font-size:0.8rem;color:#94A3B8">{niche} · {city}</div>
                </div>
                <span style="background:{bg};color:{fg};padding:3px 10px;border-radius:99px;
                             font-size:0.72rem;font-weight:700">{icon} {tier}</span>
            </div>
            <div style="margin-top:0.8rem;display:flex;gap:1rem;flex-wrap:wrap">
                <div><span style="font-size:1.2rem;font-weight:700;color:#A78BFA">{score:.0f}</span>
                     <span style="font-size:0.7rem;color:#64748B"> ARIA</span></div>
                <div><span style="font-weight:600">{ig_followers:,}</span>
                     <span style="font-size:0.7rem;color:#64748B"> followers</span></div>
                <div><span style="font-weight:600">{ig_er:.1f}%</span>
                     <span style="font-size:0.7rem;color:#64748B"> engagement</span></div>
                <div><span style="font-weight:600">{rate:.0f}</span>
                     <span style="font-size:0.7rem;color:#64748B"> JOD/post</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if show_invite:
            if st.button(f"✉️ Invite @{handle}", key=f"invite_{inf.get('id',0)}_{handle}"):
                invited = True
    return invited
