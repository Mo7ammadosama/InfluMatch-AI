"""Influencer Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post
from ..utils.i18n import t

TIER_META = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render():
    lang = st.session_state.get("lang", "ar")
    user = st.session_state.get("user", {})

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1.5rem">
        <span style="font-size:2rem">⭐</span>
        <div>
            <h2 style="margin:0;color:#A78BFA">{'لوحة تحكم المؤثر' if lang=='ar' else 'Influencer Dashboard'}</h2>
            <p style="margin:0;color:#64748B;font-size:0.85rem">{(user.get('full_name_en') or user.get('full_name_ar') or '') if user else ''}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    inf  = api_get("/api/influencers/me") or {}

    # Handle new influencer with no profile — show setup form
    if not inf or inf.get("profile_exists") is False or inf.get("id") is None:
        _render_profile_setup(lang)
        return

    tier = inf.get("aria_tier", "UNRANKED")
    icon, bg, fg = TIER_META.get(tier, TIER_META["UNRANKED"])
    score = inf.get("aria_score", 0)

    # ARIA Score hero card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.2),rgba(109,40,217,0.1));
                border:1px solid rgba(124,58,237,0.3);border-radius:16px;padding:1.5rem;
                text-align:center;margin-bottom:1.5rem">
        <div style="font-size:0.8rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em">ARIA Score</div>
        <div style="font-size:4rem;font-weight:800;color:#A78BFA;line-height:1.1">{score:.1f}</div>
        <span style="background:{bg};color:{fg};padding:0.3rem 1rem;border-radius:99px;
                     font-size:0.8rem;font-weight:700">{icon} {tier}</span>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("📸", f"{inf.get('instagram_followers',0):,}", "Instagram"),
        ("🎵", f"{inf.get('tiktok_followers',0):,}", "TikTok"),
        ("📊", f"{inf.get('instagram_engagement_rate',0):.1f}%", "Engagement"),
        ("✅", str(inf.get("campaigns_completed", 0)), "Completed"),
    ]
    for col, (icon2, val, lbl) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon2}</div>
                <div class="metric-value" style="font-size:1.5rem">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Score breakdown
    if score > 0:
        st.markdown(f"#### {'تفاصيل نقاط ARIA' if lang=='ar' else 'ARIA Score Breakdown'}")
        dims = [
            ("🔥 Engagement", inf.get("engagement_score", 0), 30),
            ("🛡️ Authenticity", inf.get("authenticity_score", 0), 25),
            ("🎨 Content Quality", inf.get("engagement_score", 0) * 0.8, 20),
            ("⏱️ Reliability", inf.get("delivery_score", 0), 15),
            ("🎯 Relevance", inf.get("relevance_score", 0), 10),
        ]
        for label, raw, weight in dims:
            normalized = min(100, raw)
            weighted = (normalized / 100) * weight
            st.markdown(f"**{label}** — {weighted:.1f}/{weight}")
            st.progress(normalized / 100)

    # Available Campaigns
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### {'الحملات المتاحة' if lang=='ar' else 'Available Campaigns'}")
    campaigns = api_get("/api/campaigns") or []
    for c in campaigns[:5]:
        with st.container():
            status = c.get("status", "")
            if status in ("active", "draft"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="aria-card" style="margin-bottom:0.3rem">
                        <b>{c.get('title_en') or c.get('title_ar','')}</b> &nbsp;
                        <span style="color:#94A3B8;font-size:0.82rem">· {c.get('niche','—')} · {c.get('budget_per_influencer',0):.0f} JOD</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Apply ✉️", key=f"apply_{c.get('id',0)}", use_container_width=True):
                        s, r = api_post(f"/api/campaigns/{c.get('id')}/apply", json={})
                        if s in (200, 201):
                            st.success("Application submitted!")
                        elif s == 409:
                            st.info("Already applied.")
                        else:
                            st.error(r.get("detail", "Error applying"))


def _render_profile_setup(lang):
    """Shown to influencers who haven't completed their profile yet"""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(109,40,217,0.05));
                border:1px solid rgba(124,58,237,0.4);border-radius:16px;
                padding:2rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3rem">🌟</div>
        <h3 style="color:#A78BFA;margin:0.5rem 0">
            {'أكمل ملفك الشخصي للبدء' if lang=='ar' else 'Complete Your Influencer Profile'}
        </h3>
        <p style="color:#64748B;font-size:0.9rem">
            {'أدخل بيانات حساباتك الاجتماعية لحساب نقاط ARIA وعرضك للتجار' if lang=='ar'
             else 'Add your social media stats to calculate your ARIA score and get discovered by merchants'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("influencer_profile_form"):
        st.markdown(f"#### {'معلومات الحساب الاجتماعي' if lang=='ar' else 'Social Media Info'}")
        col1, col2 = st.columns(2)
        with col1:
            ig_handle     = st.text_input("Instagram Handle", placeholder="@yourhandle")
            ig_followers  = st.number_input("Instagram Followers", min_value=0, value=0, step=100)
            ig_engagement = st.number_input("Instagram Engagement Rate (%)", min_value=0.0, max_value=100.0, value=2.5, step=0.1)
        with col2:
            tt_handle    = st.text_input("TikTok Handle", placeholder="@yourhandle")
            tt_followers = st.number_input("TikTok Followers", min_value=0, value=0, step=100)
            niche        = st.selectbox("Primary Niche / التخصص", [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
        bio_en = st.text_area("Bio (English)", height=80, placeholder="Tell merchants about yourself...")
        bio_ar = st.text_area("النبذة (عربي)", height=80, placeholder="عرّف التجار بنفسك...")

        submitted = st.form_submit_button("🚀 Create Profile & Calculate ARIA Score", use_container_width=True)
        if submitted:
            if ig_followers == 0 and tt_followers == 0:
                st.error("Add at least one social media account with followers.")
            else:
                s, r = api_post("/api/influencers/", json={
                    "instagram_handle"           : ig_handle,
                    "instagram_followers"        : int(ig_followers),
                    "instagram_engagement_rate"  : ig_engagement,
                    "tiktok_handle"              : tt_handle,
                    "tiktok_followers"           : int(tt_followers),
                    "niche"                      : niche,
                    "bio_en"                     : bio_en,
                    "bio_ar"                     : bio_ar,
                })
                if s in (200, 201):
                    st.success("✅ Profile created! Calculating your ARIA score...")
                    st.rerun()
                else:
                    st.error(f"❌ {r.get('detail', 'Error creating profile')}")
