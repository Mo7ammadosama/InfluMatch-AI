"""Campaign card component"""
import streamlit as st

STATUS_STYLE = {
    "draft":        ("📝", "#334155", "#94A3B8"),
    "active":       ("✅", "rgba(16,185,129,0.15)", "#10B981"),
    "in_progress":  ("⚡", "rgba(245,158,11,0.15)", "#F59E0B"),
    "under_review": ("🔍", "rgba(124,58,237,0.15)", "#A78BFA"),
    "completed":    ("🏁", "rgba(16,185,129,0.1)", "#6EE7B7"),
    "disputed":     ("⚠️", "rgba(239,68,68,0.15)", "#EF4444"),
    "cancelled":    ("❌", "#1E293B", "#475569"),
}

def render_campaign_card(c: dict, actions: list = None):
    status = c.get("status", "draft")
    icon, bg, fg = STATUS_STYLE.get(status, STATUS_STYLE["draft"])
    title = c.get("title_en") or c.get("title_ar", "Untitled")
    budget = c.get("total_budget", 0)
    niche = c.get("niche", "—")

    st.markdown(f"""
    <div class="aria-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem">
            <div style="font-weight:700;font-size:1rem">{title}</div>
            <span style="background:{bg};color:{fg};padding:3px 10px;border-radius:99px;font-size:0.72rem;font-weight:600">
                {icon} {status.replace("_"," ").title()}
            </span>
        </div>
        <div style="display:flex;gap:1.2rem;font-size:0.82rem;color:#94A3B8">
            <span>💰 {budget:,.0f} JOD</span>
            <span>🏷️ {niche}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if actions:
        cols = st.columns(len(actions))
        for i, (label, key, callback) in enumerate(actions):
            with cols[i]:
                if st.button(label, key=key):
                    callback()
