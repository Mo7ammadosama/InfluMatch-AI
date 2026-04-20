"""My Bookings Page — Merchant & Influencer views with status timeline + in-app chat"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t

STATUS_COLOR = {
    "pending"          : "#f59e0b",
    "confirmed"        : "#8b5cf6",
    "content_submitted": "#3b82f6",
    "content_approved" : "#00ff88",
    "released"         : "#00ff88",
    "disputed"         : "#ef4444",
    "cancelled"        : "#6b7280",
}

TIMELINE_KEYS = [
    ("pending",           "tl_booked"),
    ("confirmed",         "tl_confirmed"),
    ("content_submitted", "tl_content"),
    ("content_approved",  "tl_reviewed"),
    ("released",          "tl_paid"),
]

STATUS_ORDER = [s for s, _ in TIMELINE_KEYS]


def _status_label(status: str) -> str:
    key_map = {
        "pending": "pending", "confirmed": "confirmed",
        "content_submitted": "content_submitted", "content_approved": "content_approved",
        "released": "released", "disputed": "disputed", "cancelled": "cancelled",
    }
    return t(key_map.get(status, "status"))


def _timeline_html(current_status: str) -> str:
    try:
        current_idx = STATUS_ORDER.index(current_status)
    except ValueError:
        current_idx = -1

    is_terminal = current_status in ("released", "cancelled")
    items = ""
    for i, (status, label_key) in enumerate(TIMELINE_KEYS):
        if i < current_idx or (i == current_idx and is_terminal):
            cls = "done"
        elif i == current_idx:
            cls = "active"
        else:
            cls = ""
        items += f'<div class="timeline-item {cls}">{t(label_key)}</div>'
    return f'<div class="booking-timeline">{items}</div>'


def render():
    role = st.session_state.get("role", "")

    banner_class = "merchant-banner" if role == "merchant" else "influencer-banner"
    icon  = "📅" if role == "merchant" else "🌟"
    title = t("bookings")
    sub   = t("track_booking")

    st.markdown(f"""
    <div class="{banner_class}">
      <div style="display:flex;align-items:center;gap:1.2rem">
        <div style="font-size:2.8rem">{icon}</div>
        <div>
          <div style="font-size:1.4rem;font-weight:800">{title}</div>
          <div style="color:#a0a0b0;font-size:0.85rem;margin-top:0.2rem">{sub}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    _resp    = api_get("/api/bookings/my") or {}
    bookings = _resp.get("data", []) if isinstance(_resp, dict) and "data" in _resp else (_resp or [])
    _total   = _resp.get("total", len(bookings)) if isinstance(_resp, dict) else len(bookings)

    if not bookings:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:3rem">
          <div style="font-size:3rem;margin-bottom:1rem">📭</div>
          <div style="color:#a0a0b0;font-size:1rem">{t('no_bookings')}</div>
        </div>""", unsafe_allow_html=True)
        if role == "merchant":
            if st.button(t("discover_influencers"), type="primary"):
                st.session_state["page"] = "discover"
                st.rerun()
        return

    total     = _total
    active    = sum(1 for b in bookings if b.get("status") not in ("released", "cancelled", "disputed"))
    released  = sum(1 for b in bookings if b.get("status") == "released")
    total_jod = sum(float(b.get("agreed_rate_jod") or 0) for b in bookings)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("total_bookings"), total)
    c2.metric(t("active"),         active)
    c3.metric(t("completed"),      released)
    c4.metric(t("total_jod"),      f"{total_jod:.3f}")

    st.markdown("---")

    for b in bookings:
        bid    = b.get("id")
        status = b.get("status", "pending")
        color  = STATUS_COLOR.get(status, "#6b7280")
        rate   = float(b.get("agreed_rate_jod") or 0)
        brief  = b.get("brief") or "—"
        deadline = b.get("deadline", "")
        ai_res = b.get("ai_review_result") or {}

        with st.expander(
            f"#{bid} — {_status_label(status)}  |  {rate:.3f} JOD",
            expanded=(status in ("pending", "confirmed", "content_submitted"))
        ):
            col_left, col_right = st.columns([3, 2])

            with col_left:
                st.markdown(f"""
                <div class="glass-card" style="padding:1rem">
                  <div style="margin-bottom:0.6rem">
                    <span style="color:#a0a0b0;font-size:0.75rem">{t('brief')}</span><br>
                    <span style="color:#fff;font-size:0.9rem">{brief[:300]}</span>
                  </div>
                  <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.5rem">
                    <span style="color:#a0a0b0;font-size:0.8rem">💰 {rate:.3f} JOD</span>
                    {"<span style='color:#a0a0b0;font-size:0.8rem'>📅 " + deadline[:10] + "</span>" if deadline else ""}
                  </div>
                </div>""", unsafe_allow_html=True)

                if ai_res:
                    verdict   = ai_res.get("verdict", "PENDING")
                    score_val = ai_res.get("score", 0) or 0
                    approved  = ai_res.get("approved", False)
                    auto_ok   = ai_res.get("auto_approved", False)
                    notes     = str(ai_res.get("notes", "") or "")[:120]
                    v_color   = "#00ff88" if verdict == "APPROVED" else ("#ef4444" if verdict == "REJECTED" else "#f59e0b")
                    v_icon    = "✅" if approved else ("❌" if verdict == "REJECTED" else "⏳")
                    bar_pct   = min(int(score_val), 100)

                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.35);border:1px solid {v_color}44;
                                border-radius:12px;padding:0.9rem 1rem;margin-top:0.6rem">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem">
                        <span style="color:#8b5cf6;font-size:0.75rem;font-weight:700">🤖 ARIA Content Review</span>
                        <span style="color:{v_color};font-weight:800;font-size:0.85rem">
                          {v_icon} {verdict}{"  · Auto-approved" if auto_ok else ""}
                        </span>
                      </div>
                      <div style="display:flex;justify-content:space-between;font-size:0.75rem;
                                  color:#a0a0b0;margin-bottom:0.3rem">
                        <span>Content Score</span>
                        <span style="color:{v_color};font-weight:700">{score_val:.0f} / 100</span>
                      </div>
                      <div style="background:rgba(255,255,255,0.07);border-radius:4px;height:6px;
                                  overflow:hidden;margin-bottom:0.5rem">
                        <div style="width:{bar_pct}%;height:100%;background:{v_color};border-radius:4px"></div>
                      </div>
                      {"<div style='font-size:0.72rem;color:#6b7280;line-height:1.4'>" + notes + "</div>" if notes else ""}
                    </div>""", unsafe_allow_html=True)

            with col_right:
                st.markdown(_timeline_html(status), unsafe_allow_html=True)

            # ── Action buttons ────────────────────────────────────
            if role == "influencer":
                if status == "pending":
                    col_accept, col_cancel = st.columns(2)
                    with col_accept:
                        if st.button(f"✅ {t('accept_booking')}", key=f"confirm_{bid}", type="primary", use_container_width=True):
                            s, r = api_post(f"/api/bookings/{bid}/confirm", json={})
                            if s == 200:
                                st.success(t("booking_confirmed"))
                                st.rerun()
                            else:
                                st.error(r.get("detail", t("error")))
                    with col_cancel:
                        if st.button(f"❌ {t('cancel_booking')}", key=f"cancel_inf_{bid}", use_container_width=True):
                            s, r = api_post(f"/api/bookings/{bid}/cancel", json={})
                            if s == 200:
                                st.success(t("booking_cancelled"))
                                st.rerun()
                            else:
                                st.error(r.get("detail", t("error")))

                elif status in ("confirmed", "content_submitted"):
                    ai_verdict  = ai_res.get("verdict", "") if ai_res else ""
                    is_rejected = ai_verdict == "REJECTED"

                    if status == "content_submitted" and is_rejected:
                        st.markdown(
                            f'<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.4);'
                            f'border-radius:8px;padding:0.6rem 1rem;font-size:0.82rem;color:#fca5a5;margin-bottom:0.5rem">'
                            f'{t("content_rejected")}</div>',
                            unsafe_allow_html=True
                        )

                    if status == "confirmed" or is_rejected:
                        label = f"🔄 {t('resubmit')}" if is_rejected else f"📤 {t('submit_content')}"
                        content_url = st.text_input(
                            t("content_url"),
                            placeholder="https://www.instagram.com/p/...",
                            key=f"url_{bid}"
                        )
                        caption = st.text_area(
                            t("post_caption"),
                            placeholder="اكتب نص المنشور هنا مع الهاشتاق والعلامة التجارية..." if st.session_state.get("lang","ar") == "ar" else "Write your post caption with hashtags and brand mention...",
                            key=f"caption_{bid}",
                            height=100
                        )
                        if st.button(label, key=f"submit_{bid}", type="primary"):
                            if content_url.strip():
                                s, r = api_post(f"/api/bookings/{bid}/submit-content",
                                                json={"content_url": content_url, "caption": caption.strip()})
                                if s == 200:
                                    ai = r.get("ai_review", {})
                                    if ai.get("approved"):
                                        st.success(f"✅ {t('approved_label')} ARIA Score: {ai.get('score')}/100")
                                    else:
                                        st.warning(f"{t('rejected_label')} Score: {ai.get('score')}/100")
                                    st.rerun()
                                else:
                                    st.error(r.get("detail", t("error")))
                            else:
                                st.warning(t("enter_content_url"))

            elif role == "merchant":
                if status in ("pending", "confirmed", "content_submitted"):
                    st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
                    if st.button(f"❌ {t('cancel_booking')}", key=f"cancel_merch_{bid}"):
                        s, r = api_post(f"/api/bookings/{bid}/cancel", json={})
                        if s == 200:
                            st.success(t("booking_cancelled"))
                            st.rerun()
                        else:
                            st.error(r.get("detail", t("error")))

                if status == "content_approved":
                    if st.button(f"💰 {t('release_payment')}", key=f"release_{bid}", type="primary"):
                        s, r = api_post(f"/api/bookings/{bid}/release", json={})
                        if s == 200:
                            st.success(f"✅ {r.get('net_amount','—')} JOD — {t('payment_released')}")
                            st.rerun()
                        else:
                            st.error(r.get("detail", t("error")))

                elif status == "content_submitted":
                    ai_verdict = ai_res.get("verdict", "") if ai_res else ""
                    if ai_verdict == "REJECTED":
                        st.markdown(
                            f'<div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.4);'
                            f'border-radius:8px;padding:0.6rem 1rem;font-size:0.82rem;color:#fcd34d;margin-bottom:0.5rem">'
                            f'{t("aria_rejected_merchant")} (Score: {int(ai_res.get("score", 0))}/100)</div>',
                            unsafe_allow_html=True
                        )
                        if st.button(f"✅ {t('manual_approve')}", key=f"override_{bid}"):
                            s, r = api_post(f"/api/bookings/{bid}/release", json={"override": True})
                            if s == 200:
                                st.success(f"✅ {t('manual_approved')} {r.get('net_amount','—')} JOD!")
                                st.rerun()
                            else:
                                st.error(r.get("detail", t("error")))

            _render_chat(bid)


def _render_chat(booking_id: int):
    if "chat_open_bookings" not in st.session_state:
        st.session_state["chat_open_bookings"] = set()

    is_open = booking_id in st.session_state["chat_open_bookings"]
    label   = t("close_chat") if is_open else t("open_chat")

    if st.button(label, key=f"chat_toggle_{booking_id}", use_container_width=False):
        if is_open:
            st.session_state["chat_open_bookings"].discard(booking_id)
        else:
            st.session_state["chat_open_bookings"].add(booking_id)
        st.rerun()

    if not is_open:
        return

    messages = api_list(f"/api/messages/{booking_id}")

    st.markdown("""
    <div style="background:rgba(10,10,20,0.6);border:1px solid rgba(139,92,246,0.2);
                border-radius:12px;padding:1rem;margin-top:0.5rem;max-height:300px;overflow-y:auto">
    """, unsafe_allow_html=True)

    if not messages:
        st.markdown(f'<div style="color:#6b7280;font-size:0.8rem;text-align:center;padding:1rem">{t("no_messages")}</div>',
                    unsafe_allow_html=True)
    else:
        for m in messages:
            is_mine = m.get("is_mine", False)
            align   = "flex-end" if is_mine else "flex-start"
            bg      = "rgba(139,92,246,0.25)" if is_mine else "rgba(30,30,50,0.8)"
            border  = "rgba(139,92,246,0.4)"  if is_mine else "rgba(60,60,80,0.4)"
            ts      = str(m.get("created_at", ""))[:16]
            st.markdown(f"""
            <div style="display:flex;justify-content:{align};margin-bottom:0.5rem">
              <div style="background:{bg};border:1px solid {border};border-radius:10px;
                          padding:0.5rem 0.8rem;max-width:75%">
                <div style="font-size:0.82rem;color:#e0e0f0">{m.get('content','')}</div>
                <div style="font-size:0.6rem;color:#6b7280;margin-top:0.2rem;text-align:right">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    msg_input = st.text_input(
        t("type_message"),
        key=f"msg_input_{booking_id}",
        placeholder=t("type_message"),
        label_visibility="collapsed",
    )
    send_col, _ = st.columns([1, 4])
    with send_col:
        if st.button(f"{t('send')} ➤", key=f"msg_send_{booking_id}", type="primary"):
            if msg_input.strip():
                s, r = api_post("/api/messages/", json={"booking_id": booking_id, "content": msg_input.strip()})
                if s == 201:
                    st.rerun()
                else:
                    st.error(r.get("detail", t("send_failed")))
            else:
                st.warning(t("type_message"))
