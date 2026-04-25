"""Influencer Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t

TIER_META = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render():
    user = st.session_state.get("user") or {}
    lang = st.session_state.get("lang", "ar")
    name = user.get("full_name_en") if lang == "en" else (user.get("full_name_ar") or user.get("full_name_en"))
    name = name or user.get("username", t("influencer"))

    st.markdown(f"""
    <div class="influencer-banner">
      <div style="display:flex;align-items:center;gap:1rem">
        <div style="font-size:2.5rem">🌟</div>
        <div>
          <div style="font-size:1.4rem;font-weight:700;color:#8b5cf6">{t('welcome_influencer')}, {name}</div>
          <div style="color:#a0a0b0;font-size:0.85rem">{t('influencer_banner_sub')} — WaslAI.jo</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    profile   = api_get("/api/influencers/me") or {}
    campaigns = api_list("/api/campaigns/my")
    wallet    = api_get("/api/wallet/me") or {}

    if not profile or profile.get("id") is None:
        _render_profile_setup(lang)
        return

    score    = profile.get("aria_score", 0)
    tier     = profile.get("aria_tier", "UNRANKED")
    earnings = wallet.get("available_points", wallet.get("balance_points", 0)) * 0.01
    active   = [c for c in campaigns if c.get("status") == "in_progress"]

    tier_color = {"PLATINUM": "#e5e7eb", "GOLD": "#fbbf24", "SILVER": "#9ca3af",
                  "BRONZE": "#b45309", "UNRANKED": "#6b7280"}.get(tier, "#6b7280")

    col_score, col_tier, col_earn, col_active = st.columns(4)
    with col_score:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">{t('aria_score')}</div>
          <div class="score-ring">{score:.0f}</div>
        </div>""", unsafe_allow_html=True)
    with col_tier:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">{t('tier')}</div>
          <div style="font-size:1.5rem;font-weight:700;color:{tier_color}">{tier}</div>
        </div>""", unsafe_allow_html=True)
    with col_earn:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">{t('earnings_lbl')}</div>
          <div style="font-size:1.3rem;font-weight:700;color:#22c55e">{earnings:.3f} JOD</div>
        </div>""", unsafe_allow_html=True)
    with col_active:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">{t('active_campaigns')}</div>
          <div style="font-size:1.8rem;font-weight:700;color:#f59e0b">{len(active)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs([t("my_campaigns_tab"), t("upload_report"), t("my_profile")])

    with tab1:
        if not campaigns:
            st.info(t("not_joined"))
            if st.button(t("explore_campaigns"), type="primary"):
                st.session_state["page"] = "discover"
                st.rerun()
        else:
            for c in campaigns:
                status_color = {"in_progress": "#f59e0b", "active": "#22c55e",
                                "completed": "#8b5cf6", "disputed": "#ef4444"}.get(c.get("status", ""), "#6b7280")
                title = (c.get("title_en") if lang == "en" else c.get("title_ar")) or c.get("title_en") or c.get("title", "—")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="aria-card">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                          <div style="font-weight:700">{title}</div>
                          <div style="color:#a0a0b0;font-size:0.8rem">
                            {c.get('total_budget',0):.3f} JOD · {c.get('niche','—')}
                          </div>
                        </div>
                        <span style="color:{status_color};border:1px solid {status_color};
                                     padding:0.2rem 0.7rem;border-radius:20px;font-size:0.75rem">
                          {c.get('status','—')}
                        </span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if c.get("status") in ("active", "draft"):
                        if st.button(t("apply"), key=f"apply_{c.get('id',0)}", use_container_width=True):
                            s, r = api_post(f"/api/campaigns/{c.get('id')}/apply", json={})
                            if s in (200, 201):
                                st.success(t("applied"))
                            elif s == 409:
                                st.info(t("already_applied"))
                            else:
                                st.error(r.get("detail", t("error")))

    with tab2:
        st.markdown(f"#### {t('upload_report_title')}")
        st.markdown('<div class="aria-card">', unsafe_allow_html=True)
        camp_options = {(c.get("title_en") or c.get("title_ar") or str(c.get("id"))): c.get("id")
                        for c in active} if active else {}
        if camp_options:
            selected = st.selectbox(t("select_campaign"), list(camp_options.keys()))
            uploaded = st.file_uploader(t("upload_file"), type=["png", "jpg", "jpeg", "pdf"], help="Max: 10MB")
            if uploaded and st.button(t("upload_btn"), type="primary"):
                cid = camp_options[selected]
                import httpx
                try:
                    token = st.session_state.get("token", "")
                    r = httpx.post(
                        f"http://localhost:8080/api/campaigns/{cid}/upload-report",
                        files={"file": (uploaded.name, uploaded.read(), uploaded.type)},
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=30
                    )
                    if r.status_code == 200:
                        st.success(t("upload_success"))
                    else:
                        st.error(f"{t('error')} ({r.status_code})")
                except Exception as exc:
                    st.error(f"{t('error')}: {exc}")
        else:
            st.info(t("no_active_campaigns"))
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        if not profile:
            st.warning(t("no_profile_setup"))
            if st.button(t("setup_profile_btn"), type="primary"):
                st.session_state["page"] = "settings"
                st.rerun()
        else:
            st.markdown(f"#### {t('social_accounts')}")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric(t("city"),      profile.get("city",  "—"))
            s2.metric(t("niche"),     profile.get("niche", "—"))
            s3.metric(t("instagram"), f"{profile.get('instagram_followers',0):,}")
            s4.metric(t("tiktok"),    f"{profile.get('tiktok_followers',0):,}")

            st.markdown("---")
            st.markdown(f"#### {t('aria_breakdown')}")
            eng  = float(profile.get("engagement_score",   0) or 0)
            auth = float(profile.get("authenticity_score", 0) or 0)
            rel  = float(profile.get("relevance_score",    0) or 0)
            del_ = float(profile.get("delivery_score",     0) or 0)
            cq   = float(profile.get("content_quality_score", 70) or 70)

            def _score_bar(label, val, max_val, color):
                pct = min(int(val / max_val * 100), 100)
                st.markdown(f"""
                <div style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;font-size:0.8rem;
                              color:#a0a0b0;margin-bottom:0.3rem">
                    <span>{label}</span><span style="color:{color};font-weight:700">{val:.1f} / {max_val}</span>
                  </div>
                  <div style="background:rgba(255,255,255,0.07);border-radius:6px;height:8px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{color};border-radius:6px;transition:width .4s ease"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

            _score_bar(t("engagement_score"),   eng,  30,  "#f59e0b")
            _score_bar(t("authenticity_score"), auth, 25,  "#8b5cf6")
            _score_bar(t("relevance_score"),    rel,  10,  "#3b82f6")
            _score_bar(t("delivery_score"),     del_, 15,  "#22c55e")
            _score_bar(t("content_quality"),    cq,   100, "#ec4899")

            st.markdown(f"""
            <div style="background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.25);
                        border-radius:12px;padding:0.8rem 1.2rem;margin-top:0.5rem;
                        display:flex;justify-content:space-between;align-items:center">
              <span style="color:#a0a0b0;font-size:0.85rem">{t('aria_total')}</span>
              <span style="font-size:1.6rem;font-weight:800;color:#22c55e">
                {profile.get('aria_score', 0):.1f}
              </span>
            </div>""", unsafe_allow_html=True)

            st.markdown("---")
            if st.button(t("edit_profile_btn"), use_container_width=True):
                st.session_state["page"] = "settings"
                st.rerun()


def _render_profile_setup(lang):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(109,40,217,0.05));
                border:1px solid rgba(124,58,237,0.4);border-radius:16px;
                padding:2rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3rem">🌟</div>
        <h3 style="color:#A78BFA;margin:0.5rem 0">{t('setup_profile')}</h3>
        <p style="color:#64748B;font-size:0.9rem">{t('setup_profile_sub')}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("influencer_profile_form"):
        st.markdown(f"#### {t('social_info')}")
        col1, col2 = st.columns(2)
        with col1:
            ig_handle     = st.text_input("Instagram Handle", placeholder="@yourhandle")
            ig_followers  = st.number_input("Instagram Followers", min_value=0, value=0, step=100)
            ig_engagement = st.number_input("Instagram Engagement Rate (%)", min_value=0.0, max_value=100.0, value=2.5, step=0.1)
        with col2:
            tt_handle    = st.text_input("TikTok Handle", placeholder="@yourhandle")
            tt_followers = st.number_input("TikTok Followers", min_value=0, value=0, step=100)
            niche        = st.selectbox(t("niche"), [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
        bio_en = st.text_area("Bio (English)", height=80, placeholder="Tell merchants about yourself...")
        bio_ar = st.text_area("Bio (Arabic)", height=80, placeholder="عرّف التجار بنفسك...")

        submitted = st.form_submit_button(t("create_profile_btn"), use_container_width=True)
        if submitted:
            if ig_followers == 0 and tt_followers == 0:
                st.error(t("add_social_account"))
            else:
                s, r = api_post("/api/influencers/", json={
                    "instagram_handle":          ig_handle,
                    "instagram_followers":        int(ig_followers),
                    "instagram_engagement_rate":  ig_engagement,
                    "tiktok_handle":              tt_handle,
                    "tiktok_followers":           int(tt_followers),
                    "niche":                      niche,
                    "bio_en":                     bio_en,
                    "bio_ar":                     bio_ar,
                })
                if s in (200, 201):
                    st.success(t("profile_created"))
                    st.rerun()
                else:
                    st.error(f"❌ {r.get('detail', t('profile_error'))}")
