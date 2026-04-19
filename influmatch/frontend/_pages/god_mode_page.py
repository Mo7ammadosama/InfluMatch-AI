"""God Mode Admin Dashboard — InfluMatch.jo"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from ..utils.api_client import api_get, api_post, api_patch, api_delete, api_list
from ..utils.session import get_role

def render():
    if get_role() != "admin":
        st.error("وصول مرفوض — للمدير فقط / Admin Access Only")
        st.stop()

    st.markdown("""
<div class="admin-banner">
  <div style="display:flex;align-items:center;gap:1rem">
    <div style="font-size:3rem">⚡</div>
    <div>
      <div style="font-size:1.8rem;font-weight:900;color:#ef4444;letter-spacing:0.05em">
        GOD MODE — ARIA Control Center
      </div>
      <div style="color:#a0a0b0;font-size:0.85rem">
        Full platform oversight | Zero restrictions | Executive authority
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── REAL PLATFORM STATS ──
    stats = api_get("/api/admin/platform-stats") or {}
    st.markdown("### Platform Pulse — Live")

    cols = st.columns(5)
    kpis = [
        ("المستخدمون",      stats.get("total_users", 0)),
        ("التجار",          stats.get("total_merchants", 0)),
        ("المؤثرون",        stats.get("total_influencers", 0)),
        ("الحملات النشطة", stats.get("active_campaigns", 0)),
        ("Escrow المحجوز",  f"{stats.get('escrow_locked_jod', 0):.3f} JOD"),
    ]
    icons = ["👥", "🏪", "🌟", "📢", "💰"]
    for col, icon, (label, val) in zip(cols, icons, kpis):
        col.markdown(f"""
<div class="kpi-block" style="border-left-color:#ef4444">
  <div style="font-size:1.4rem">{icon}</div>
  <div class="kpi-value">{val}</div>
  <div class="kpi-label">{label}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color in [
        (c1, "إجمالي حجم Escrow",  f"{stats.get('total_escrow_volume_jod', 0):.3f} JOD", "#f59e0b"),
        (c2, "عمولات المنصة",       f"{stats.get('total_platform_fees_jod', 0):.3f} JOD", "#00ff88"),
        (c3, "نزاعات مفتوحة",       stats.get("open_disputes", 0),                        "#ef4444"),
        (c4, "مستخدمون اليوم",      stats.get("new_users_today", 0),                       "#8b5cf6"),
    ]:
        col.markdown(f"""
<div class="aria-card" style="text-align:center;border-top:3px solid {color}">
  <div style="color:{color};font-size:1.5rem;font-weight:700">{val}</div>
  <div style="color:#a0a0b0;font-size:0.75rem;margin-top:0.3rem">{label}</div>
</div>""", unsafe_allow_html=True)

    st.divider()

    # ── AGENT STATUS (from real stats) ──
    st.markdown("### ARIA Agent Status")
    a1, a2 = st.columns(2)
    guardian_raw = stats.get("guardian_agent", "unknown")
    rag_raw      = stats.get("rag_system", "unknown")

    def _sc(s):
        return "#00ff88" if s.lower() in ("active", "ready", "online") else "#ef4444"

    with a1:
        st.markdown(f"""
<div class="aria-card" style="border-left:4px solid {_sc(guardian_raw)}">
  <div style="font-weight:700;color:{_sc(guardian_raw)};margin-bottom:0.5rem">
    Guardian Agent — {guardian_raw.upper()}
  </div>
  <div style="color:#a0a0b0;font-size:0.85rem">نزاعات مفتوحة: <b style="color:#fff">{stats.get("open_disputes", 0)}</b></div>
  <div style="color:#a0a0b0;font-size:0.85rem">حملات مكتملة: <b style="color:#fff">{stats.get("completed_campaigns", 0)}</b></div>
  <div style="color:#a0a0b0;font-size:0.85rem">إجمالي الحملات: <b style="color:#fff">{stats.get("total_campaigns", 0)}</b></div>
</div>""", unsafe_allow_html=True)

    with a2:
        st.markdown(f"""
<div class="aria-card" style="border-left:4px solid {_sc(rag_raw)}">
  <div style="font-weight:700;color:{_sc(rag_raw)};margin-bottom:0.5rem">
    RAG System — {rag_raw.upper()}
  </div>
  <div style="color:#a0a0b0;font-size:0.85rem">إجمالي المستخدمين: <b style="color:#fff">{stats.get("total_users", 0)}</b></div>
  <div style="color:#a0a0b0;font-size:0.85rem">مستخدمون جدد اليوم: <b style="color:#fff">{stats.get("new_users_today", 0)}</b></div>
  <div style="color:#a0a0b0;font-size:0.85rem">عمولات المنصة: <b style="color:#fff">{stats.get("total_platform_fees_jod", 0):.3f} JOD</b></div>
</div>""", unsafe_allow_html=True)

    st.divider()

    # ── EXECUTIVE CONTROL PANEL ──
    st.markdown("### Executive Control Panel")
    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown("**Manual Triggers**")
        if st.button("Force Influencer Scoring", use_container_width=True):
            s, r = api_post("/api/admin/trigger/scoring", json={})
            st.success(r.get("message", "Queued")) if s == 200 else st.error(str(r))
        if st.button("Force Escrow Release", use_container_width=True):
            s, r = api_post("/api/admin/trigger/escrow_release", json={})
            st.success(r.get("message", "Queued")) if s == 200 else st.error(str(r))
        if st.button("Re-Audit Content", use_container_width=True):
            s, r = api_post("/api/admin/trigger/reaudit", json={})
            st.success(r.get("message", "Queued")) if s == 200 else st.error(str(r))

    with p2:
        st.markdown("**Emergency Controls**")
        if st.button("Freeze ALL Escrows", use_container_width=True, type="primary"):
            if not st.session_state.get("freeze_confirm"):
                st.session_state["freeze_confirm"] = True
                st.warning("اضغط مرة أخرى للتأكيد!")
            else:
                s, r = api_post("/api/admin/freeze-all-escrows", json={})
                st.session_state["freeze_confirm"] = False
                if s == 200:
                    st.error(f"تم تجميد {r.get('frozen_count', 0)} escrow")
                else:
                    st.error(str(r))
        st.markdown("**Blast Notification**")
        blast_msg = st.text_area("الرسالة / Message", placeholder="اكتب الإشعار هنا...", key="blast_msg", height=80)
        blast_role = st.selectbox("الجمهور", ["all", "merchant", "influencer"], key="blast_role")
        if st.button("📢 إرسال الإشعار", use_container_width=True, type="primary"):
            if blast_msg.strip():
                s, r = api_post("/api/admin/notification/blast", json={
                    "message_ar": blast_msg, "target_role": blast_role
                })
                if s == 200:
                    st.success(f"✅ أُرسل لـ {r.get('sent', 0)} مستخدم")
                else:
                    st.error(str(r.get("detail", r)))
            else:
                st.warning("اكتب الرسالة أولاً")
        st.divider()
        if st.button("🔄 Rebuild RAG Index", use_container_width=True):
            with st.spinner("جاري إعادة بناء الفهرس..."):
                s, r = api_post("/api/admin/rag/rebuild", json={})
            if s == 200:
                st.success("✅ تم إعادة بناء RAG بنجاح")
            else:
                st.error(str(r.get("detail", r)))

    with p3:
        st.markdown("**Data Exports**")
        users_data     = api_list("/api/admin/users")
        campaigns_data = api_list("/api/campaigns/")
        if users_data:
            import json as _json
            st.download_button(
                "Export Users (JSON)",
                _json.dumps(users_data, ensure_ascii=False, indent=2),
                "influmatch_users.json", "application/json",
                use_container_width=True
            )
        if campaigns_data:
            rows = [{"ID": c.get("id"),
                     "Title": c.get("title_en") or c.get("title_ar"),
                     "Status": c.get("status"),
                     "Budget JOD": c.get("total_budget"),
                     "Niche": c.get("niche")} for c in campaigns_data]
            st.download_button(
                "Export Campaigns (CSV)",
                pd.DataFrame(rows).to_csv(index=False),
                "influmatch_campaigns.csv", "text/csv",
                use_container_width=True
            )

    st.divider()

    # ── MAIN TABS ──
    tab1, tab2, tab3, tab4 = st.tabs(["👥 المستخدمون", "📢 الحملات", "⚖️ النزاعات", "📊 التحليلات"])

    # TAB 1 — USER MANAGEMENT
    with tab1:
        st.markdown("#### إدارة المستخدمين")
        search = st.text_input("بحث بالاسم أو الإيميل", placeholder="admin@influmatch.jo", key="user_search")
        users = api_list("/api/admin/users")
        if search:
            users = [u for u in users if search.lower() in
                     (u.get("email", "") + u.get("full_name_en", "") + u.get("username", "")).lower()]

        if not users:
            st.info("لا يوجد مستخدمون")
        else:
            for u in users:
                uid       = u.get("id")
                is_active = u.get("is_active", True)
                role_val  = u.get("role", "")
                role_color = {"admin": "#ef4444", "merchant": "#f59e0b",
                              "influencer": "#8b5cf6"}.get(role_val, "#6b7280")
                display_name = u.get("full_name_en") or u.get("full_name_ar") or u.get("username") or u.get("email")
                status_dot = "🟢" if is_active else "🔴"

                with st.expander(f"{status_dot} [{role_val.upper()}] {display_name} — {u.get('email')}"):
                    uc1, uc2, uc3, uc4 = st.columns(4)

                    with uc1:
                        st.markdown(f"**ID:** {uid}")
                        st.markdown(f"**Role:** <span style='color:{role_color}'>{role_val.upper()}</span>",
                                    unsafe_allow_html=True)
                        st.markdown(f"**Active:** {'نعم' if is_active else 'لا'}")
                        joined = u.get("created_at", "—")[:10] if u.get("created_at") else "—"
                        st.markdown(f"**Joined:** {joined}")

                    with uc2:
                        role_options = ["merchant", "influencer", "admin"]
                        cur_idx = role_options.index(role_val) if role_val in role_options else 0
                        new_role = st.selectbox("تغيير الدور", role_options,
                                                index=cur_idx, key=f"role_sel_{uid}")
                        if st.button("حفظ الدور", key=f"save_role_{uid}", use_container_width=True):
                            s, r = api_patch(f"/api/admin/users/{uid}/role", json={"role": new_role})
                            if s == 200:
                                st.success(f"الدور الجديد: {new_role}")
                                st.rerun()
                            else:
                                st.error(str(r))

                    with uc3:
                        toggle_lbl = "تعطيل" if is_active else "تفعيل"
                        if st.button(toggle_lbl, key=f"toggle_{uid}", use_container_width=True):
                            s, r = api_patch(f"/api/admin/users/{uid}/toggle-active", json={})
                            if s == 200:
                                st.success(f"is_active = {r.get('is_active')}")
                                st.rerun()
                            else:
                                st.error(str(r))

                    with uc4:
                        if role_val != "admin":
                            if st.button("حذف", key=f"del_{uid}", use_container_width=True):
                                s, r = api_delete(f"/api/admin/users/{uid}")
                                if s == 200:
                                    st.success("تم الحذف")
                                    st.rerun()
                                else:
                                    st.error(str(r))

    # TAB 2 — CAMPAIGNS
    with tab2:
        st.markdown("#### جميع الحملات")
        all_statuses = ["الكل", "draft", "active", "in_progress", "under_review",
                        "completed", "disputed", "cancelled"]
        status_filter = st.selectbox("فلتر الحالة", all_statuses, key="camp_status_filter")
        campaigns = api_list("/api/campaigns/")
        if status_filter != "الكل":
            campaigns = [c for c in campaigns if c.get("status") == status_filter]

        if not campaigns:
            st.info("لا توجد حملات بهذه الحالة")
        else:
            for c in campaigns:
                cid   = c.get("id")
                title = c.get("title_en") or c.get("title_ar") or f"Campaign #{cid}"
                s_color = {"active": "#00ff88", "in_progress": "#f59e0b",
                           "completed": "#8b5cf6", "disputed": "#ef4444",
                           "draft": "#6b7280", "cancelled": "#374151",
                           "under_review": "#3b82f6"}.get(c.get("status", ""), "#6b7280")

                with st.expander(f"[{c.get('status','').upper()}] {title} — {c.get('total_budget', 0):.3f} JOD"):
                    cc1, cc2 = st.columns([3, 1])
                    with cc1:
                        st.markdown(f"**Niche:** {c.get('niche', '—')} | **Merchant ID:** {c.get('merchant_id', '—')}")
                        st.markdown(
                            f"**Status:** <span style='color:{s_color}'>{c.get('status','').upper()}</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"**Budget:** {c.get('total_budget', 0):.3f} JOD")
                    with cc2:
                        editable_statuses = ["draft", "active", "in_progress",
                                             "under_review", "completed", "cancelled"]
                        cur_s = c.get("status", "draft")
                        if cur_s not in editable_statuses:
                            cur_s = "draft"
                        new_status = st.selectbox("تغيير الحالة", editable_statuses,
                                                  index=editable_statuses.index(cur_s),
                                                  key=f"cstatus_{cid}")
                        if st.button("حفظ", key=f"save_c_{cid}", use_container_width=True):
                            s, r = api_patch(f"/api/admin/campaigns/{cid}/status",
                                             json={"status": new_status})
                            if s == 200:
                                st.success(f"الحالة الجديدة: {new_status}")
                                st.rerun()
                            else:
                                st.error(str(r))

    # TAB 3 — DISPUTES
    with tab3:
        st.markdown("#### النزاعات النشطة")
        disputes = api_list("/api/admin/disputes")
        if not disputes:
            st.success("لا توجد نزاعات مفتوحة — المنصة بخير")
        else:
            st.error(f"{len(disputes)} نزاع نشط يحتاج قراراً")
            for d in disputes:
                eid   = d.get("escrow_id") or d.get("id")
                title = d.get("title_en") or d.get("title_ar") or f"Campaign #{d.get('campaign_id','?')}"

                with st.expander(f"نزاع #{eid} — {title} — {d.get('total_budget', 0):.3f} JOD"):
                    st.markdown(f"**سبب النزاع:** {d.get('dispute_reason') or 'غير محدد'}")
                    st.markdown(f"**تاريخ الرفع:** {(d.get('dispute_raised_at') or '—')[:19]}")
                    st.markdown(f"**Merchant ID:** {d.get('merchant_id', '—')}")
                    st.markdown(f"**المبلغ الصافي:** {d.get('net_amount', 0):.3f} JOD")

                    reason = st.text_area("سبب القرار", key=f"reason_{eid}",
                                          placeholder="اشرح قرارك للطرفين...")
                    dr1, dr2 = st.columns(2)
                    with dr1:
                        if st.button(f"لصالح التاجر #{eid}", key=f"merch_{eid}",
                                     use_container_width=True):
                            if not reason.strip():
                                st.warning("أدخل سبب القرار أولاً")
                            else:
                                s, r = api_post(f"/api/admin/disputes/{eid}/resolve",
                                                json={"decision": "MERCHANT", "reason": reason})
                                if s == 200:
                                    st.success(f"تم الاسترداد للتاجر | {r.get('amount_jod', 0):.3f} JOD")
                                    st.rerun()
                                else:
                                    st.error(str(r))
                    with dr2:
                        if st.button(f"لصالح المؤثر #{eid}", key=f"infl_{eid}",
                                     use_container_width=True):
                            if not reason.strip():
                                st.warning("أدخل سبب القرار أولاً")
                            else:
                                s, r = api_post(f"/api/admin/disputes/{eid}/resolve",
                                                json={"decision": "INFLUENCER", "reason": reason})
                                if s == 200:
                                    st.success(f"تم الإفراج للمؤثر | {r.get('amount_jod', 0):.3f} JOD")
                                    st.rerun()
                                else:
                                    st.error(str(r))

    # TAB 4 — ANALYTICS (real endpoint)
    with tab4:
        st.markdown("#### تحليلات المنصة")
        analytics = api_get("/api/admin/analytics") or {}
        daily = analytics.get("daily_campaigns", [])

        if daily:
            df_a = pd.DataFrame(daily)
            fig = go.Figure(go.Bar(
                x=df_a["date"], y=df_a["count"],
                marker_color="#ef4444",
                text=df_a["count"], textposition="outside"
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ffffff", title="الحملات الجديدة يومياً",
                height=350, showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات تحليلية بعد — أنشئ حملات أولاً")

        sc1, sc2, sc3 = st.columns(3)
        total_c = max(stats.get("total_campaigns", 1), 1)
        sc1.metric("إجمالي حجم المعاملات",
                   f"{stats.get('total_escrow_volume_jod', 0):.3f} JOD")
        sc2.metric("عمولات المنصة المحققة",
                   f"{stats.get('total_platform_fees_jod', 0):.3f} JOD")
        sc3.metric("معدل إتمام الحملات",
                   f"{round(stats.get('completed_campaigns', 0) / total_c * 100, 1)}%")
