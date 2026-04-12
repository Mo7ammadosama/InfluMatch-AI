"""Loyalty Wallet page"""
import streamlit as st
from ..utils.api_client import api_get
from ..utils.i18n import t

TIER_INFO = {
    "BRONZE": ("🥉", 0, 999, "rgba(180,83,9,0.2)", "#b45309"),
    "SILVER": ("🥈", 1000, 4999, "rgba(156,163,175,0.2)", "#9ca3af"),
    "GOLD":   ("🥇", 5000, 19999, "rgba(251,191,36,0.2)", "#fbbf24"),
    "PLATINUM":("🏆", 20000, 999999, "rgba(229,231,235,0.2)", "#e5e7eb"),
}

def render():
    lang = st.session_state.get("lang", "ar")
    wallet = api_get("/api/wallet/me")

    if not wallet:
        st.info("Wallet not found. Make sure your merchant profile is set up. / المحفظة غير موجودة")
        return

    # Use correct field names from API response
    points = wallet.get("available_points", wallet.get("total_points", 0))
    tier_data = wallet.get("tier", {})
    # get_tier() returns {"tier": "GOLD", "emoji": ..., "discount": ...}
    tier = tier_data.get("tier", "BRONZE") if isinstance(tier_data, dict) else str(tier_data)
    icon, low, high, bg, fg = TIER_INFO.get(tier, TIER_INFO["BRONZE"])
    total_earned = wallet.get("total_points", 0)
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

    # Next tier progress
    next_tiers = {"BRONZE": "SILVER", "SILVER": "GOLD", "GOLD": "PLATINUM", "PLATINUM": None}
    next_tier = next_tiers.get(tier)
    if next_tier:
        next_icon, next_low, _, _, next_fg = TIER_INFO[next_tier]
        needed = next_low - points
        progress = min(1.0, points / next_low)
        st.markdown(f"**Progress to {next_icon} {next_tier}** — {needed:,} points needed")
        st.progress(progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_earned:,}</div>
            <div class="metric-label">Total Earned</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{total_redeemed:,}</div>
            <div class="metric-label">Total Redeemed</div></div>""", unsafe_allow_html=True)
    with c3:
        jod_val = points / 100
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{jod_val:.1f} JOD</div>
            <div class="metric-label">Cash Value</div></div>""", unsafe_allow_html=True)

    # Transactions
    st.markdown(f"#### {'المعاملات الأخيرة' if lang=='ar' else 'Recent Transactions'}")
    txns = wallet.get("transactions", [])
    if not txns:
        st.info("No transactions yet / لا توجد معاملات بعد")
    else:
        for tx in txns[-10:]:
            tx_type = tx.get("transaction_type", "")
            pts = tx.get("points", 0)
            sign = "+" if tx_type in ("earned", "bonus", "referral") else "-"
            color = "#10B981" if sign == "+" else "#EF4444"
            st.markdown(f"""
            <div class="aria-card" style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 1rem">
                <div>
                    <span style="font-weight:600">{tx.get('event','—')}</span>
                    <span style="font-size:0.75rem;color:#94A3B8;margin-left:0.5rem">{tx_type}</span>
                </div>
                <span style="color:{color};font-weight:700">{sign}{pts:,} pts</span>
            </div>
            """, unsafe_allow_html=True)
