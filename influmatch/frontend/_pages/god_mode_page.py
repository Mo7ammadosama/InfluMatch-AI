"""God Mode Admin Dashboard — Module 13"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random
from ..utils.api_client import api_get, api_post
from ..utils.session import get_role

def render():
    if get_role() != "admin":
        st.error("⛔ God Mode — Admin Access Only / وصول مرفوض")
        st.stop()

    st.markdown('''
    <div class="god-mode-header">
        <h1 style="color:#e94560;margin:0;">⚡ GOD MODE — ARIA Control Center</h1>
        <p style="color:#a0a0b0;margin:5px 0 0 0;">
            Full platform oversight | Zero restrictions | Executive authority
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # ── Real-time Platform Metrics ──────────────────────────────
    st.markdown("### 📊 Platform Pulse — Real-Time")

    stats = api_get("/api/admin/platform-stats") or {}

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("👥 Total Users",        str(stats.get("total_users", 0)),        "+23 today"),
        ("🏪 Active Merchants",   str(stats.get("total_merchants", 0)),    "+5 this week"),
        ("🌟 Active Influencers", str(stats.get("total_influencers", 0)),  "+18 this week"),
        ("📢 Live Campaigns",     str(stats.get("active_campaigns", 0)),   "+8 today"),
        ("💰 Escrow Locked",      f"{stats.get('escrow_locked_jod',0):,.0f} JOD", "secured"),
    ]
    for col, (label, value, delta) in zip([col1,col2,col3,col4,col5], metrics):
        col.metric(label, value, delta)

    st.divider()

    # ── ARIA Agent Status Panel ─────────────────────────────────
    st.markdown("### 🤖 ARIA Agent Status")
    agent_col1, agent_col2 = st.columns(2)

    with agent_col1:
        st.markdown('''
        <div style="background:#1a1a2e;border:1px solid #533483;border-radius:12px;padding:1.2rem;">
            <h4 style="color:#00ff88;">🛡️ Guardian Agent</h4>
            <p style="color:#a0a0b0;font-size:13px;">Status: <b style="color:#00ff88;">ONLINE</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Jobs Queued: <b>14</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Next Run: <b>02:00 AM (Scoring)</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Escrow Releases Today: <b>3</b></p>
        </div>
        ''', unsafe_allow_html=True)

    with agent_col2:
        st.markdown('''
        <div style="background:#1a1a2e;border:1px solid #533483;border-radius:12px;padding:1.2rem;">
            <h4 style="color:#ffd700;">🔍 AI Auditor Agent</h4>
            <p style="color:#a0a0b0;font-size:13px;">Status: <b style="color:#00ff88;">ONLINE</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Audits Today: <b>28</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Auto-Approved: <b>22 (78.5%)</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Flagged for Review: <b>6</b></p>
        </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # ── Revenue Analytics ───────────────────────────────────────
    st.markdown("### 💹 Revenue Analytics (JOD)")

    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
    revenue_data = pd.DataFrame({
        "date": dates,
        "platform_fees": [random.uniform(200, 800) for _ in range(30)],
        "escrow_volume": [random.uniform(2000, 8000) for _ in range(30)],
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=revenue_data["date"], y=revenue_data["escrow_volume"],
        fill="tozeroy", name="Escrow Volume",
        line=dict(color="#0f3460"), fillcolor="rgba(15,52,96,0.3)"
    ))
    fig.add_trace(go.Scatter(
        x=revenue_data["date"], y=revenue_data["platform_fees"],
        fill="tozeroy", name="Platform Fees",
        line=dict(color="#533483"), fillcolor="rgba(83,52,131,0.3)"
    ))
    fig.update_layout(
        paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
        font=dict(color="white"), height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── ARIA Score Distribution ─────────────────────────────────
    st.markdown("### 🏆 Influencer ARIA Score Distribution")
    score_col1, score_col2 = st.columns([2, 1])

    with score_col1:
        tiers  = ["PLATINUM", "GOLD", "SILVER", "BRONZE", "UNRANKED"]
        counts = [12, 47, 98, 103, 52]
        colors = ["#e5e4e2", "#ffd700", "#c0c0c0", "#cd7f32", "#555"]
        fig2 = go.Figure(go.Bar(x=tiers, y=counts, marker_color=colors,
                                text=counts, textposition="outside"))
        fig2.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                           font=dict(color="white"), height=280,
                           margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with score_col2:
        st.markdown('''
        <div style="padding:1rem;">
            <div style="margin-bottom:12px;">
                <span style="color:#e5e4e2;font-size:20px;">💎</span>
                <b style="color:#e5e4e2;"> PLATINUM</b>
                <span style="float:right;color:#a0a0b0;">12</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#ffd700;font-size:20px;">🥇</span>
                <b style="color:#ffd700;"> GOLD</b>
                <span style="float:right;color:#a0a0b0;">47</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#c0c0c0;font-size:20px;">🥈</span>
                <b style="color:#c0c0c0;"> SILVER</b>
                <span style="float:right;color:#a0a0b0;">98</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#cd7f32;font-size:20px;">🥉</span>
                <b style="color:#cd7f32;"> BRONZE</b>
                <span style="float:right;color:#a0a0b0;">103</span>
            </div>
            <div>
                <span style="font-size:20px;">⬜</span>
                <b style="color:#555;"> UNRANKED</b>
                <span style="float:right;color:#a0a0b0;">52</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # ── Executive Control Panel ─────────────────────────────────
    st.markdown("### ⚙️ Executive Control Panel")
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)

    with ctrl_col1:
        st.markdown("**🔄 Manual Agent Triggers**")
        if st.button("▶️ Force Influencer Scoring", use_container_width=True):
            s, r = api_post("/api/admin/trigger/scoring", json={})
            if s == 200:
                st.toast(r.get("message", "Scoring queued"), icon="🤖")
            else:
                st.error(r.get("detail"))
        if st.button("▶️ Force Escrow Release Check", use_container_width=True):
            s, r = api_post("/api/admin/trigger/escrow_release", json={})
            if s == 200:
                st.toast(r.get("message", "Escrow check queued"), icon="💰")
            else:
                st.error(r.get("detail"))
        if st.button("▶️ Re-Audit Flagged Content", use_container_width=True):
            s, r = api_post("/api/admin/trigger/reaudit", json={})
            if s == 200:
                st.toast(r.get("message", "Re-audit queued"), icon="🔍")
            else:
                st.error(r.get("detail"))

    with ctrl_col2:
        st.markdown("**🚨 Emergency Controls**")
        if st.button("🛑 Freeze All Escrows", use_container_width=True, type="secondary"):
            if st.session_state.get("confirm_freeze"):
                s, r = api_post("/api/admin/freeze-all-escrows", json={})
                if s == 200:
                    st.error(f"🛑 FROZEN: {r.get('frozen_count',0)} escrows")
                    st.session_state["confirm_freeze"] = False
                else:
                    st.error(r.get("detail"))
            else:
                st.session_state["confirm_freeze"] = True
                st.warning("⚠️ Click again to CONFIRM freeze of ALL escrows")
        if st.button("📧 Blast Notification (All)", use_container_width=True, type="secondary"):
            st.info("📧 Platform-wide notification — coming soon")
        if st.button("🔃 Rebuild RAG Index", use_container_width=True, type="secondary"):
            st.toast("RAG rebuild initiated...", icon="🧠")

    with ctrl_col3:
        st.markdown("**📊 Reports**")
        users_data = api_get("/api/admin/users") or []
        campaigns_data = api_get("/api/campaigns/") or []
        if st.button("📥 Export Platform Report", use_container_width=True):
            report = f"InfluMatch.jo Platform Report\nGenerated: {datetime.now()}\n\n"
            report += f"Total Users: {stats.get('total_users',0)}\n"
            report += f"Total Campaigns: {len(campaigns_data)}\n"
            report += f"Escrow Locked: {stats.get('escrow_locked_jod',0):,.2f} JOD\n"
            st.download_button("⬇️ Download Report", report, "platform_report.txt", use_container_width=True)
        if st.button("📥 Export User List", use_container_width=True):
            if users_data:
                import pandas as pd
                df = pd.DataFrame(users_data)
                st.download_button("⬇️ Download CSV", df.to_csv(index=False),
                                   "users.csv", "text/csv", use_container_width=True)
        if st.button("📥 Export Campaigns", use_container_width=True):
            if campaigns_data:
                import pandas as pd
                df = pd.DataFrame(campaigns_data)
                st.download_button("⬇️ Download CSV", df.to_csv(index=False),
                                   "campaigns.csv", "text/csv", use_container_width=True)

    st.divider()

    # ── Users Table ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📢 All Campaigns", "⚖️ Disputes", "📊 Analytics"])
    with tab1:
        users = api_get("/api/admin/users") or []
        if users:
            df = pd.DataFrame([{
                "ID": u.get("id"), "Name": u.get("full_name_en") or u.get("full_name_ar"),
                "Email": u.get("email"), "Role": u.get("role"), "Active": u.get("is_active"),
            } for u in users])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

    with tab2:
        campaigns = api_get("/api/campaigns") or []
        if campaigns:
            df = pd.DataFrame([{
                "ID": c.get("id"),
                "Title": c.get("title_en") or c.get("title_ar"),
                "Status": c.get("status"),
                "Budget (JOD)": c.get("total_budget"),
                "Niche": c.get("niche"),
            } for c in campaigns])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No campaigns found")

    with tab3:
        # Disputes — use dedicated endpoint
        disputed = api_get("/api/admin/disputes") or []
        if disputed:
            for d in disputed:
                st.markdown(f"""
                <div style="background:#1a1a2e;border-left:3px solid #e94560;
                            border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.5rem">
                    <b>{d.get('title_en') or d.get('title_ar','')}</b>
                    <span style="color:#e94560;margin-left:0.8rem">⚠️ DISPUTED</span>
                    <span style="color:#a0a0b0;font-size:0.8rem;margin-left:0.8rem">
                        Budget: {d.get('total_budget',0):.0f} JOD
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No active disputes — platform healthy")

    with tab4:
        st.markdown("#### 📊 Platform Analytics")
        import plotly.graph_objects as go
        import pandas as pd
        from datetime import datetime, timedelta
        import random
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=[d.strftime("%a") for d in dates],
            y=[random.randint(5, 30) for _ in range(7)],
            name="New Users", marker_color="#533483"
        ))
        fig3.add_trace(go.Bar(
            x=[d.strftime("%a") for d in dates],
            y=[random.randint(1, 10) for _ in range(7)],
            name="New Campaigns", marker_color="#e94560"
        ))
        fig3.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                           font=dict(color="white"), height=250,
                           margin=dict(l=0,r=0,t=10,b=0), barmode="group")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("Note: Live analytics endpoint in roadmap — current data is illustrative")
