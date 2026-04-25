"""Open Campaigns page — Influencer view of available campaigns to join"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t
import datetime as _dt


def render():
    lang = st.session_state.get("lang", "ar")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(83,52,131,0.1));
                border:1px solid rgba(139,92,246,0.4);border-radius:16px;
                padding:1.5rem 2rem;margin-bottom:1.5rem">
      <div style="display:flex;align-items:center;gap:1rem">
        <div style="font-size:2.8rem">📢</div>
        <div>
          <div style="font-size:1.4rem;font-weight:800;
                      background:linear-gradient(135deg,#8b5cf6,#f59e0b);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            {t('open_campaigns_title')}
          </div>
          <div style="color:#a0a0b0;font-size:0.85rem;margin-top:0.2rem">
            {t('open_campaigns_sub')}
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        niche_options = [t("all_filter"), "Fashion", "Food", "Tech", "Beauty", "Fitness",
                         "Travel", "Gaming", "Education", "Lifestyle", "Sports"]
        niche_filter = st.selectbox(t("niche"), niche_options, key="oc_niche")
    with fc2:
        city_filter = st.text_input(t("city"), placeholder="Amman, Irbid..." if lang == "en" else "عمان، إربد...", key="oc_city")
    with fc3:
        sort_options = [t("newest"), t("highest_budget"), t("soonest_deadline")]
        sort_by = st.selectbox(t("sort_by"), sort_options, key="oc_sort")

    st.markdown("---")

    params = {"limit": 50}
    if niche_filter != t("all_filter"):
        params["niche"] = niche_filter
    if city_filter:
        params["city"] = city_filter

    campaigns = api_list("/api/campaigns", params=params)
    campaigns = [c for c in campaigns if c.get("status") in ("active", "draft", "open")]

    if sort_by == t("highest_budget"):
        campaigns.sort(key=lambda x: float(x.get("total_budget") or 0), reverse=True)
    elif sort_by == t("soonest_deadline"):
        campaigns.sort(key=lambda x: str(x.get("end_date") or "9999"))

    if not campaigns:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:3rem 2rem">
          <div style="font-size:3rem;margin-bottom:1rem">📭</div>
          <div style="color:#a0a0b0;font-size:1rem;font-weight:600">{t('no_open_campaigns')}</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(
        f"<div style='color:#8b5cf6;font-size:0.85rem;margin-bottom:1rem'>"
        f"✨ {len(campaigns)} {t('available_campaigns')}</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, c in enumerate(campaigns):
        with cols[i % 2]:
            cid      = c.get("id")
            title    = (c.get("title_en") if lang == "en" else c.get("title_ar")) or c.get("title_en") or f"Campaign #{cid}"
            title_alt = c.get("title_ar") if lang == "en" else c.get("title_en") or ""
            niche    = c.get("niche") or "—"
            budget   = float(c.get("total_budget") or 0)
            status   = c.get("status", "").upper()
            end_date = str(c.get("end_date") or "TBD")[:10]
            desc     = (c.get("description_en") if lang == "en" else c.get("description_ar")) or c.get("description_en") or ""
            city     = c.get("city") or ""

            status_color = "#22c55e" if status in ("ACTIVE", "OPEN") else "#f59e0b"

            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:0.5rem">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem">
                <div style="flex:1">
                  <div style="font-weight:800;font-size:1rem;color:#e0e0f0">{title}</div>
                  {f'<div style="color:#6b7280;font-size:0.75rem">{title_alt}</div>' if title_alt and title_alt != title else ''}
                </div>
                <span style="color:{status_color};font-size:0.7rem;border:1px solid {status_color};
                             padding:0.2rem 0.6rem;border-radius:10px;white-space:nowrap;margin-left:0.5rem">
                  {status}
                </span>
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.75rem">
                <span style="background:rgba(139,92,246,0.2);color:#8b5cf6;border-radius:8px;
                             padding:0.2rem 0.6rem;font-size:0.75rem">{niche}</span>
                {f'<span style="background:rgba(245,158,11,0.1);color:#f59e0b;border-radius:8px;padding:0.2rem 0.6rem;font-size:0.75rem">{city}</span>' if city else ''}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:0.75rem">
                <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.5rem;text-align:center">
                  <div style="font-size:1rem;font-weight:800;color:#f59e0b">{budget:,.0f}</div>
                  <div style="font-size:0.65rem;color:#6b7280">JOD {t('budget')}</div>
                </div>
                <div style="background:rgba(0,0,0,0.3);border-radius:8px;padding:0.5rem;text-align:center">
                  <div style="font-size:0.85rem;font-weight:700;color:#a0a0b0">{end_date}</div>
                  <div style="font-size:0.65rem;color:#6b7280">{t('deadline')}</div>
                </div>
              </div>
              {f'<div style="color:#a0a0b0;font-size:0.8rem;line-height:1.5;margin-bottom:0.5rem">{desc[:120]}{"..." if len(desc) > 120 else ""}</div>' if desc else ''}
            </div>""", unsafe_allow_html=True)

            apply_key = f"apply_{cid}_{i}"
            if f"applied_{cid}" in st.session_state:
                st.success(t("applied"))
            elif st.button(f"📩 {t('apply')}", key=apply_key, use_container_width=True, type="primary"):
                profile = api_get("/api/influencers/me") or {}
                if not profile.get("profile_exists"):
                    st.warning(t("complete_profile_first"))
                    if st.button(t("complete_profile_btn"), key=f"goto_profile_{cid}"):
                        st.session_state["page"] = "settings"
                        st.rerun()
                else:
                    status_code, resp = api_post(f"/api/campaigns/{cid}/apply", json={})
                    if status_code in (200, 201):
                        st.session_state[f"applied_{cid}"] = True
                        st.success(t("applied"))
                        st.rerun()
                    elif status_code == 409:
                        st.session_state[f"applied_{cid}"] = True
                        st.info(t("already_applied"))
                        st.rerun()
                    elif status_code == 404:
                        st.session_state[f"applied_{cid}"] = True
                        st.info(t("interest_noted"))
                        st.rerun()
                    else:
                        err = resp.get("detail", "") if isinstance(resp, dict) else str(resp)
                        st.error(f"{t('error')} ({status_code}): {err}")
