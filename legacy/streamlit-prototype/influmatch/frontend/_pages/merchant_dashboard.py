"""Merchant Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t
from ..utils.session import get_user
from ..components.cards.campaign_card import render_campaign_card


def render():
    user = get_user()
    lang = st.session_state.get("lang", "ar")
    name = (user.get("full_name_en") if lang == "en" else user.get("full_name_ar")) or user.get("full_name_en", t("merchant")) if user else t("merchant")

    st.markdown(f"""
    <div class="merchant-banner">
      <div style="display:flex;align-items:center;gap:1rem">
        <div style="font-size:2.5rem">🏪</div>
        <div>
          <div style="font-size:1.4rem;font-weight:700;color:#f59e0b">{t('welcome_merchant')} {name}</div>
          <div style="color:#a0a0b0;font-size:0.85rem">{t('merchant_banner_sub')} — WaslAI.jo</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    campaigns = api_list("/api/campaigns/")
    wallet    = api_get("/api/wallet/me") or {}
    escrows   = api_get("/api/escrow/my") or []
    analytics = api_get("/api/merchants/analytics") or {}

    active      = [c for c in campaigns if c.get("status") in ["active", "in_progress"]]
    completed   = [c for c in campaigns if c.get("status") == "completed"]
    total_spent = sum(e.get("net_amount", 0) for e in escrows)
    locked      = sum(e.get("net_amount", 0) for e in escrows if e.get("status") == "funded")
    points      = wallet.get("available_points", wallet.get("balance_points", 0))

    k1, k2, k3, k4 = st.columns(4)
    for col, val, label, delta, up in [
        (k1, f"{total_spent:.3f} JOD", t("budget_spent"),     "", True),
        (k2, len(active),              t("active_count"),      f"{len(active)}", True),
        (k3, len(completed),           t("completed"),         f"{len(completed)}", True),
        (k4, f"{locked:.3f} JOD",      "Escrow",              "", True),
    ]:
        col.markdown(f"""
        <div class="kpi-block">
          <div class="kpi-value">{val}</div>
          <div class="kpi-label">{label}</div>
          <div class="{'kpi-delta-up' if up else 'kpi-delta-down'}">{delta}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        f"📢 {t('my_campaigns_tab')}",
        f"💰 ROI",
        f"⚡ {t('discover')}",
        f"➕ {t('new_campaign_tab')}",
    ])

    with tab1:
        if not campaigns:
            st.info(t("no_campaigns_yet"))
            if st.button(t("create_first"), type="primary"):
                st.session_state["page"] = "campaigns"
                st.rerun()
        else:
            for c in campaigns[:10]:
                status_color = {"active": "#22c55e", "in_progress": "#f59e0b",
                                "completed": "#8b5cf6", "draft": "#6b7280",
                                "disputed": "#ef4444"}.get(c.get("status", "draft"), "#6b7280")
                title = (c.get("title_en") if lang == "en" else c.get("title_ar")) or c.get("title_en") or "—"
                st.markdown(f"""
                <div class="aria-card">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                      <div style="font-weight:700;font-size:1rem">{title}</div>
                      <div style="color:#a0a0b0;font-size:0.8rem">{c.get('niche','—')} · {c.get('total_budget',0):.3f} JOD</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3);border:1px solid {status_color};
                                color:{status_color};padding:0.2rem 0.8rem;
                                border-radius:20px;font-size:0.75rem">{c.get('status','—')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        if completed:
            import plotly.graph_objects as go
            months  = [(c.get("title_en") or c.get("title_ar", ""))[:15] for c in completed[-6:]]
            budgets = [c.get("total_budget", 0) for c in completed[-6:]]
            fig = go.Figure(go.Bar(
                x=months, y=budgets,
                marker_color="#f59e0b",
                text=[f"{b:.0f} JOD" for b in budgets],
                textposition="outside"
            ))
            title_lbl = "Completed Campaign Budgets" if lang == "en" else "ميزانيات الحملات المكتملة"
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff", title=title_lbl, showlegend=False, height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            success_rate   = analytics.get("campaign_success_rate", 0.0)
            total_released = analytics.get("total_released_jod", 0.0)
            col_a, col_b   = st.columns(2)
            col_a.metric("Campaign Success Rate" if lang == "en" else "معدل نجاح الحملات", f"{success_rate:.1f}%")
            col_b.metric("Total Released (JOD)"  if lang == "en" else "إجمالي المدفوعات",  f"{total_released:.3f} JOD")
        else:
            info_lbl = "Complete your first campaign to see ROI analysis" if lang == "en" else "أكمل حملتك الأولى لعرض تحليل ROI"
            st.info(info_lbl)

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(t("create_campaign"), use_container_width=True, type="primary"):
                st.session_state["page"] = "campaigns"
                st.rerun()
        with c2:
            if st.button(t("discover"), use_container_width=True):
                st.session_state["page"] = "discover"
                st.rerun()
        with c3:
            if st.button(t("wallet"), use_container_width=True):
                st.session_state["page"] = "wallet"
                st.rerun()

        points_lbl = "Loyalty Points" if lang == "en" else "نقاط الولاء"
        redeem_lbl = f"= {points * 0.01:.3f} JOD {'redeemable' if lang=='en' else 'قابل للاسترداد'}"
        st.markdown(f"""
        <div class="aria-card" style="margin-top:1rem">
          <div style="color:#f59e0b;font-weight:700;margin-bottom:0.5rem">{points_lbl}</div>
          <div style="font-size:1.8rem;font-weight:700">{points:,} {t('points')}</div>
          <div style="color:#a0a0b0;font-size:0.8rem;margin-top:0.3rem">{redeem_lbl}</div>
        </div>""", unsafe_allow_html=True)

    with tab4:
        _render_create_campaign(lang)


def _render_create_campaign(lang):
    with st.form("new_campaign_form"):
        st.markdown(f"#### {t('create_campaign')}")
        title_en = st.text_input("Title (English)", placeholder="Ramadan Special Campaign")
        title_ar = st.text_input("العنوان (عربي)", placeholder="حملة رمضان الخاصة")
        desc_en  = st.text_area("Description (English)", height=80)
        desc_ar  = st.text_area("الوصف (عربي)", height=80)
        col1, col2 = st.columns(2)
        with col1:
            niche = st.selectbox(t("niche"), [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
            total_budget = st.number_input(f"{t('budget')} (JOD)", min_value=50.0, value=500.0, step=50.0)
        with col2:
            budget_per_influencer = st.number_input("Per Influencer (JOD)", min_value=10.0, value=100.0, step=10.0)
            min_followers = st.number_input(t("min_followers"), min_value=1000, value=5000, step=1000)

        launch_lbl = f"🚀 {'Launch Campaign' if lang=='en' else 'إطلاق الحملة'}"
        submitted = st.form_submit_button(launch_lbl, use_container_width=True)
        if submitted:
            if not title_en and not title_ar:
                st.error(t("fill_all_fields"))
            else:
                status, resp = api_post("/api/campaigns/", json={
                    "title_en": title_en, "title_ar": title_ar,
                    "description_en": desc_en, "description_ar": desc_ar,
                    "niche": niche, "total_budget": total_budget,
                    "budget_per_influencer": budget_per_influencer,
                    "min_followers": int(min_followers)
                })
                if status in (200, 201):
                    st.success(f"✅ {'Campaign created!' if lang=='en' else 'تم إنشاء الحملة!'}")
                    st.rerun()
                else:
                    st.error(f"❌ {resp.get('detail', t('error'))}")
