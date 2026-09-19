"""Loyalty Wallet page"""
import streamlit as st
from ..utils.api_client import api_get, api_post
from ..utils.i18n import t
from ..utils.session import get_role

TIER_INFO = {
    "BRONZE":   ("🥉", 0,     999,    "rgba(180,83,9,0.2)",   "#b45309"),
    "SILVER":   ("🥈", 1000,  4999,   "rgba(156,163,175,0.2)","#9ca3af"),
    "GOLD":     ("🥇", 5000,  19999,  "rgba(251,191,36,0.2)", "#fbbf24"),
    "PLATINUM": ("🏆", 20000, 999999, "rgba(229,231,235,0.2)","#e5e7eb"),
}

def render():
    wallet = api_get("/api/wallet/me")

    if not wallet:
        st.info(t("no_wallet"))
        return

    points       = wallet.get("available_points", wallet.get("total_points", 0))
    tier_data    = wallet.get("tier", {})
    tier         = tier_data.get("tier", "BRONZE") if isinstance(tier_data, dict) else str(tier_data)
    icon, low, high, bg, fg = TIER_INFO.get(tier, TIER_INFO["BRONZE"])
    total_earned   = wallet.get("total_points", 0)
    total_redeemed = wallet.get("redeemed_points", 0)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{bg},{bg.replace('0.2','0.05')});
                border:1px solid {fg}40;border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3rem">{icon}</div>
        <div style="font-size:0.75rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.1em">{t('tier')}</div>
        <div style="font-size:2rem;font-weight:800;color:{fg}">{tier}</div>
        <div style="font-size:3.5rem;font-weight:900;color:#A78BFA;margin:0.5rem 0">{points:,}</div>
        <div style="color:#94A3B8;font-size:0.85rem">{t('points')} · {points/100:.2f} JOD value</div>
    </div>
    """, unsafe_allow_html=True)

    next_tiers = {"BRONZE": "SILVER", "SILVER": "GOLD", "GOLD": "PLATINUM", "PLATINUM": None}
    next_tier  = next_tiers.get(tier)
    if next_tier:
        next_icon, next_low, _, _, next_fg = TIER_INFO[next_tier]
        needed   = next_low - points
        progress = min(1.0, points / next_low)
        st.markdown(f"**{t('progress_to')} {next_icon} {next_tier}** — {needed:,} {t('points_needed')}")
        st.progress(progress)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_earned:,}</div>
            <div class="metric-label">{t('total_earned')}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_redeemed:,}</div>
            <div class="metric-label">{t('total_redeemed')}</div></div>""", unsafe_allow_html=True)
    with c3:
        jod_val = points / 100
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{jod_val:.1f} JOD</div>
            <div class="metric-label">{t('cash_value')}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"#### {t('redeem_points')}")
    min_redeem = 500
    if points >= min_redeem:
        with st.form("redeem_form"):
            redeem_pts = st.number_input(
                f"{t('points_to_redeem')} (min {min_redeem})",
                min_value=min_redeem,
                max_value=int(points),
                value=min_redeem,
                step=100,
            )
            jod_preview = round(redeem_pts * 0.01, 3)
            st.caption(f"= {jod_preview} JOD discount")
            submitted = st.form_submit_button(t("redeem_btn"), use_container_width=True, type="primary")
            if submitted:
                s, r = api_post("/api/wallet/redeem", json={"points": int(redeem_pts)})
                if s == 200:
                    st.success(r.get("message", f"Redeemed {redeem_pts} pts = {jod_preview} JOD"))
                    st.rerun()
                else:
                    st.error(r.get("detail", t("redeem_failed")))
    else:
        st.info(f"{t('no_wallet')} — {points:,} {t('points')}")

    st.markdown("---")
    st.markdown(f"#### {t('recent_transactions')}")
    txns = wallet.get("transactions", [])
    if not txns:
        st.info(t("no_transactions"))
    else:
        for tx in txns[-10:]:
            pts   = tx.get("points", 0)
            sign  = "+" if pts > 0 else ""
            color = "#10B981" if pts >= 0 else "#EF4444"
            label = tx.get("description") or tx.get("transaction_type") or "—"
            st.markdown(f"""
            <div class="aria-card" style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem">
                <div>
                    <span style="font-weight:600">{label}</span>
                    <span style="font-size:0.75rem;color:#94A3B8;margin-left:0.5rem">{tx.get('created_at','')[:10]}</span>
                </div>
                <span style="color:{color};font-weight:700">{sign}{pts:,} pts</span>
            </div>
            """, unsafe_allow_html=True)
