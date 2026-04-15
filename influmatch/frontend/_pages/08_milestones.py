import streamlit as st
import requests
from datetime import datetime, timedelta

if not st.session_state.get("authenticated"):
    st.error("🔒 يجب تسجيل الدخول أولاً")
    st.stop()

API_BASE = "http://localhost:8000/api"
HEADERS  = {"Authorization": f"Bearer {st.session_state.get('token', '')}"}
role     = st.session_state.get("role", "influencer")

st.markdown("""
<div style="background:linear-gradient(135deg,#0a1e3e,#1a2e5e);
            border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
    <h2 style="color:white; margin:0;">🎯 نظام المراحل — Milestones</h2>
    <p style="color:#80a0ff; margin:5px 0 0 0;">
        مدفوعات مرحلية مؤمّنة | Staged Escrow Payments
    </p>
</div>
""", unsafe_allow_html=True)

campaign_id = st.number_input("🔢 رقم الحملة / Campaign ID", min_value=1, value=1, step=1)

tab1, tab2 = st.tabs(["📊 عرض المراحل", "➕ إنشاء مراحل (تاجر)"])

with tab1:
    if st.button("🔄 تحديث", key="refresh_ms"):
        r = requests.get(f"{API_BASE}/milestones/{campaign_id}", headers=HEADERS)
        if r.status_code == 200:
            milestones = r.json()
            if not milestones:
                st.info("لا توجد مراحل لهذه الحملة بعد")
            else:
                total_pct = sum(m["percentage"] for m in milestones)
                st.progress(
                    sum(m["percentage"] for m in milestones if m["status"] == "released") / 100,
                    text=f"الإجمالي المُحرَّر: {sum(m['amount_jod'] for m in milestones if m['status'] == 'released'):.3f} JOD"
                )
                for ms in milestones:
                    color = {"pending": "#ffd700", "released": "#00ff88", "disputed": "#e94560"}.get(ms["status"], "#aaa")
                    st.markdown(f"""
                    <div style="background:#1a1a2e;border-left:4px solid {color};
                                border-radius:8px;padding:1rem;margin-bottom:0.6rem;">
                        <b style="color:white">{ms['title']}</b>
                        <span style="color:{color};float:right">{ms['status'].upper()}</span><br>
                        <span style="color:#a0a0b0">
                            {ms['percentage']}% — {ms['amount_jod']:.3f} JOD |
                            تاريخ الاستحقاق: {ms['due_date'][:10]}
                        </span>
                    </div>""", unsafe_allow_html=True)

                    if role == "merchant" and ms["status"] == "pending":
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ إصدار {ms['title']}", key=f"rel_{ms['id']}"):
                                rr = requests.post(
                                    f"{API_BASE}/milestones/{ms['id']}/release", headers=HEADERS
                                )
                                if rr.status_code == 200:
                                    st.success(f"✅ تم إصدار {ms['amount_jod']:.3f} JOD")
                                    st.rerun()
                                else:
                                    st.error(rr.json().get("detail", "خطأ"))
                        with col2:
                            if st.button(f"⚠️ نزاع", key=f"dis_{ms['id']}"):
                                reason = st.text_input("سبب النزاع", key=f"rsn_{ms['id']}")
                                if reason:
                                    requests.post(
                                        f"{API_BASE}/milestones/{ms['id']}/dispute",
                                        headers=HEADERS, params={"reason": reason}
                                    )
                                    st.warning("تم رفع النزاع")
                                    st.rerun()
        else:
            st.error(f"خطأ: {r.status_code}")

with tab2:
    if role != "merchant":
        st.info("👁️ العرض فقط — إنشاء المراحل متاح للتجار")
        st.stop()

    st.markdown("### ➕ تعريف مراحل الدفع")
    st.info("المجموع يجب أن يساوي 100% بالضبط")

    n = st.number_input("عدد المراحل", min_value=1, max_value=5, value=3, step=1)
    ms_list = []
    total_pct = 0.0

    for i in range(int(n)):
        st.markdown(f"**المرحلة {i+1}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            title = st.text_input("الوصف", key=f"ms_title_{i}",
                                  value=["توقيع العقد", "تسليم القصة", "النشر النهائي"][i] if i < 3 else "")
        with c2:
            pct = st.number_input("النسبة %", min_value=1.0, max_value=100.0,
                                  value=[20.0, 40.0, 40.0][i] if i < 3 else 10.0,
                                  key=f"ms_pct_{i}")
        with c3:
            due = st.date_input("تاريخ الاستحقاق", key=f"ms_due_{i}",
                                value=(datetime.now() + timedelta(days=(i+1)*7)).date())
        ms_list.append({"title": title, "percentage": pct,
                        "due_date": datetime.combine(due, datetime.min.time()).isoformat()})
        total_pct += pct

    color = "#00ff88" if abs(total_pct - 100.0) < 0.01 else "#e94560"
    st.markdown(f"<b style='color:{color}'>المجموع: {total_pct:.1f}%</b>", unsafe_allow_html=True)

    if st.button("💾 حفظ المراحل", type="primary", use_container_width=True):
        if abs(total_pct - 100.0) > 0.01:
            st.error(f"❌ المجموع {total_pct:.1f}% — يجب أن يكون 100% بالضبط")
        else:
            r = requests.post(
                f"{API_BASE}/milestones/{campaign_id}/create",
                headers=HEADERS, json=ms_list
            )
            if r.status_code == 201:
                st.success(f"✅ تم إنشاء {len(ms_list)} مراحل")
            else:
                st.error(f"❌ خطأ {r.status_code}: {r.json().get('detail', '')}")
