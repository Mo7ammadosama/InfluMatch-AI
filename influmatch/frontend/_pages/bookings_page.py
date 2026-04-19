"""My Bookings Page — Merchant & Influencer views with status timeline + in-app chat"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_patch, api_list

STATUS_COLOR = {
    "pending"          : ("#f59e0b", "⏳ بانتظار التأكيد"),
    "confirmed"        : ("#8b5cf6", "✅ مؤكد"),
    "content_submitted": ("#3b82f6", "📤 المحتوى مُرسل"),
    "content_approved" : ("#00ff88", "🤖 تمت الموافقة"),
    "released"         : ("#00ff88", "💰 تم الدفع"),
    "disputed"         : ("#ef4444", "⚠️ نزاع"),
    "cancelled"        : ("#6b7280", "❌ ملغى"),
}

TIMELINE_STEPS = [
    ("pending",           "📅 الحجز / Booked"),
    ("confirmed",         "✅ تأكيد المؤثر / Confirmed"),
    ("content_submitted", "📤 رفع المحتوى / Content Uploaded"),
    ("content_approved",  "🤖 مراجعة ARIA / AI Reviewed"),
    ("released",          "💰 تحويل المبلغ / Paid"),
]

STATUS_ORDER = [s for s, _ in TIMELINE_STEPS]


def _timeline_html(current_status: str) -> str:
    try:
        current_idx = STATUS_ORDER.index(current_status)
    except ValueError:
        current_idx = -1

    items = ""
    for i, (status, label) in enumerate(TIMELINE_STEPS):
        if i < current_idx:
            cls = "done"
        elif i == current_idx:
            cls = "active"
        else:
            cls = ""
        items += f'<div class="timeline-item {cls}">{label}</div>'
    return f'<div class="booking-timeline">{items}</div>'


def render():
    role = st.session_state.get("role", "")
    lang = st.session_state.get("lang", "ar")

    # ── Header ──────────────────────────────────────────────────
    banner_class = "merchant-banner" if role == "merchant" else "influencer-banner"
    icon = "📅" if role == "merchant" else "🌟"
    title = "حجوزاتي / My Bookings"
    sub   = "تابع حالة حجوزاتك وتفاصيل الإعلانات" if lang == "ar" else "Track your bookings and campaign status"

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

    # ── Fetch bookings ───────────────────────────────────────────
    _resp    = api_get("/api/bookings/my") or {}
    bookings = _resp.get("data", []) if isinstance(_resp, dict) and "data" in _resp else (_resp or [])
    _total_bookings = _resp.get("total", len(bookings)) if isinstance(_resp, dict) else len(bookings)

    if not bookings:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:3rem">
          <div style="font-size:3rem;margin-bottom:1rem">📭</div>
          <div style="color:#a0a0b0;font-size:1rem">لا توجد حجوزات بعد</div>
          <div style="color:#6b7280;font-size:0.8rem;margin-top:0.5rem">No bookings yet</div>
        </div>""", unsafe_allow_html=True)
        if role == "merchant":
            if st.button("🔍 اكتشف المؤثرين", type="primary"):
                st.session_state["page"] = "discover"
                st.rerun()
        return

    # ── Stats row ────────────────────────────────────────────────
    total    = _total_bookings
    active   = sum(1 for b in bookings if b.get("status") not in ("released", "cancelled", "disputed"))
    released = sum(1 for b in bookings if b.get("status") == "released")
    total_jod= sum(float(b.get("agreed_rate_jod") or 0) for b in bookings)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الحجوزات", total)
    c2.metric("نشطة", active)
    c3.metric("مكتملة", released)
    c4.metric("إجمالي JOD", f"{total_jod:.3f}")

    st.markdown("---")

    # ── Booking cards ────────────────────────────────────────────
    for b in bookings:
        bid     = b.get("id")
        status  = b.get("status", "pending")
        color, status_label = STATUS_COLOR.get(status, ("#6b7280", status))
        rate    = float(b.get("agreed_rate_jod") or 0)
        brief   = b.get("brief") or "—"
        deadline= b.get("deadline", "")
        ai_res  = b.get("ai_review_result") or {}

        with st.expander(
            f"#{bid} — {status_label}  |  {rate:.3f} JOD",
            expanded=(status in ("pending", "confirmed", "content_submitted"))
        ):
            col_left, col_right = st.columns([3, 2])

            with col_left:
                # ── Brief + rate + deadline ──────────────────────────
                st.markdown(f"""
                <div class="glass-card" style="padding:1rem">
                  <div style="margin-bottom:0.6rem">
                    <span style="color:#a0a0b0;font-size:0.75rem">وصف الإعلان / Brief</span><br>
                    <span style="color:#fff;font-size:0.9rem">{brief[:300]}</span>
                  </div>
                  <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.5rem">
                    <span style="color:#a0a0b0;font-size:0.8rem">💰 {rate:.3f} JOD</span>
                    {"<span style='color:#a0a0b0;font-size:0.8rem'>📅 " + deadline[:10] + "</span>" if deadline else ""}
                  </div>
                </div>""", unsafe_allow_html=True)

                # ── ARIA AI Review card (shown when data exists) ──────
                if ai_res:
                    verdict      = ai_res.get("verdict", "PENDING")
                    score_val    = ai_res.get("score", 0) or 0
                    approved     = ai_res.get("approved", False)
                    auto_ok      = ai_res.get("auto_approved", False)
                    notes        = str(ai_res.get("notes", "") or "")[:120]

                    v_color = (
                        "#00ff88" if verdict == "APPROVED"
                        else "#ef4444" if verdict == "REJECTED"
                        else "#f59e0b"
                    )
                    v_icon  = "✅" if approved else ("❌" if verdict == "REJECTED" else "⏳")
                    bar_pct = min(int(score_val), 100)

                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.35);border:1px solid {v_color}44;
                                border-radius:12px;padding:0.9rem 1rem;margin-top:0.6rem">
                      <div style="display:flex;justify-content:space-between;align-items:center;
                                  margin-bottom:0.6rem">
                        <span style="color:#8b5cf6;font-size:0.75rem;font-weight:700">🤖 ARIA Content Review</span>
                        <span style="color:{v_color};font-weight:800;font-size:0.85rem">
                          {v_icon} {verdict}{"  · Auto-approved" if auto_ok else ""}
                        </span>
                      </div>
                      <div style="display:flex;justify-content:space-between;
                                  font-size:0.75rem;color:#a0a0b0;margin-bottom:0.3rem">
                        <span>Content Score</span>
                        <span style="color:{v_color};font-weight:700">{score_val:.0f} / 100</span>
                      </div>
                      <div style="background:rgba(255,255,255,0.07);border-radius:4px;
                                  height:6px;overflow:hidden;margin-bottom:0.5rem">
                        <div style="width:{bar_pct}%;height:100%;background:{v_color};
                                    border-radius:4px"></div>
                      </div>
                      {"<div style='font-size:0.72rem;color:#6b7280;line-height:1.4'>" + notes + "</div>" if notes else ""}
                    </div>""", unsafe_allow_html=True)

            with col_right:
                st.markdown(_timeline_html(status), unsafe_allow_html=True)

            # ── Action buttons per role & status ──────────────────
            if role == "influencer":
                if status == "pending":
                    if st.button("✅ قبول الحجز", key=f"confirm_{bid}", type="primary"):
                        s, r = api_post(f"/api/bookings/{bid}/confirm", json={})
                        if s == 200:
                            st.success("تم قبول الحجز!")
                            st.rerun()
                        else:
                            st.error(r.get("detail", "خطأ"))

                elif status == "confirmed":
                    content_url = st.text_input(
                        "رابط المحتوى / Content URL",
                        placeholder="https://www.instagram.com/p/...",
                        key=f"url_{bid}"
                    )
                    if st.button("📤 رفع المحتوى", key=f"submit_{bid}", type="primary"):
                        if content_url.strip():
                            s, r = api_post(f"/api/bookings/{bid}/submit-content",
                                            json={"content_url": content_url})
                            if s == 200:
                                ai = r.get("ai_review", {})
                                if ai.get("approved"):
                                    st.success(f"✅ تمت الموافقة! ARIA Score: {ai.get('score')}/100")
                                else:
                                    st.warning(f"⏳ بانتظار المراجعة | Score: {ai.get('score')}/100 — {ai.get('notes','')}")
                                st.rerun()
                            else:
                                st.error(r.get("detail", "خطأ"))
                        else:
                            st.warning("أدخل رابط المحتوى")

            elif role == "merchant":
                if status == "content_approved":
                    if st.button("💰 إصدار الدفع للمؤثر", key=f"release_{bid}", type="primary"):
                        s, r = api_post(f"/api/bookings/{bid}/release", json={})
                        if s == 200:
                            st.success(f"✅ تم تحويل {r.get('net_amount','—')} JOD للمؤثر!")
                            st.rerun()
                        else:
                            st.error(r.get("detail", "خطأ"))

            # ── In-app chat thread ─────────────────────────────────
            _render_chat(bid)


def _render_chat(booking_id: int):
    """Collapsible chat thread for a booking."""
    chat_key = f"chat_open_{booking_id}"
    if "chat_open_bookings" not in st.session_state:
        st.session_state["chat_open_bookings"] = set()

    is_open = booking_id in st.session_state["chat_open_bookings"]
    label   = "💬 إخفاء المحادثة" if is_open else "💬 فتح المحادثة"

    if st.button(label, key=f"chat_toggle_{booking_id}", use_container_width=False):
        if is_open:
            st.session_state["chat_open_bookings"].discard(booking_id)
        else:
            st.session_state["chat_open_bookings"].add(booking_id)
        st.rerun()

    if not is_open:
        return

    # Fetch thread
    messages = api_list(f"/api/messages/{booking_id}")

    st.markdown("""
    <div style="background:rgba(10,10,20,0.6);border:1px solid rgba(139,92,246,0.2);
                border-radius:12px;padding:1rem;margin-top:0.5rem;max-height:300px;overflow-y:auto">
    """, unsafe_allow_html=True)

    if not messages:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.8rem;text-align:center;padding:1rem">لا توجد رسائل بعد</div>',
            unsafe_allow_html=True,
        )
    else:
        for m in messages:
            is_mine  = m.get("is_mine", False)
            align    = "flex-end" if is_mine else "flex-start"
            bg       = "rgba(139,92,246,0.25)" if is_mine else "rgba(30,30,50,0.8)"
            border   = "rgba(139,92,246,0.4)"  if is_mine else "rgba(60,60,80,0.4)"
            ts       = str(m.get("created_at", ""))[:16]
            content  = m.get("content", "")
            st.markdown(f"""
            <div style="display:flex;justify-content:{align};margin-bottom:0.5rem">
              <div style="background:{bg};border:1px solid {border};border-radius:10px;
                          padding:0.5rem 0.8rem;max-width:75%">
                <div style="font-size:0.82rem;color:#e0e0f0">{content}</div>
                <div style="font-size:0.6rem;color:#6b7280;margin-top:0.2rem;text-align:right">{ts}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Send input
    msg_input = st.text_input(
        "اكتب رسالة / Type a message",
        key=f"msg_input_{booking_id}",
        placeholder="اكتب رسالتك هنا...",
        label_visibility="collapsed",
    )
    send_col, _ = st.columns([1, 4])
    with send_col:
        if st.button("إرسال ➤", key=f"msg_send_{booking_id}", type="primary"):
            if msg_input.strip():
                s, r = api_post("/api/messages/", json={
                    "booking_id": booking_id,
                    "content"   : msg_input.strip(),
                })
                if s == 201:
                    st.rerun()
                else:
                    st.error(r.get("detail", "فشل الإرسال"))
            else:
                st.warning("الرسالة فارغة")
