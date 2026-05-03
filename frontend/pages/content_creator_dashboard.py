"""
WaslAI.jo — Content Creator Dashboard
Profile, portfolio, booking requests, engagements — bilingual (AR/EN) + RTL toggle
"""
import streamlit as st
import httpx
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def render():
    lang = st.session_state.get("language", "ar")
    is_ar = lang == "ar"
    user = st.session_state.user or {}

    name = user.get("full_name_ar") or user.get("full_name", "")
    greeting = f"مرحباً {name} 👋" if is_ar else f"Welcome, {name} 👋"
    st.header(greeting)

    tab_labels = (
        ["👤 ملفي الشخصي", "🎨 معرض الأعمال", "📥 طلبات الحجز", "🤝 المشاركات", "💡 نشر فكرة"]
        if is_ar else
        ["👤 My Profile", "🎨 Portfolio", "📥 Booking Requests", "🤝 Engagements", "💡 Submit Idea"]
    )
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _profile_tab(is_ar)
    with tabs[1]:
        _portfolio_tab(is_ar)
    with tabs[2]:
        _bookings_tab(is_ar)
    with tabs[3]:
        _engagements_tab(is_ar)
    with tabs[4]:
        _submit_idea_tab(is_ar)


def _profile_tab(is_ar: bool):
    st.subheader("الملف الشخصي" if is_ar else "My Profile")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/content-creators/profile/me", headers=_headers(), timeout=10)
        profile = r.json() if r.status_code == 200 else None
    except Exception:
        profile = None

    if profile:
        col1, col2, col3 = st.columns(3)
        col1.metric("المشاركات المكتملة" if is_ar else "Completed", profile.get("completed_engagements", 0))
        col2.metric("متوسط التقييم" if is_ar else "Avg Rating", f"{profile.get('avg_rating', 0):.1f}")
        col3.metric("الأرباح (JOD)" if is_ar else "Earned (JOD)", f"{profile.get('total_earned_jod', 0):.2f}")

        available = profile.get("is_available", False)
        status_badge = "🟢 متاح" if available else "🔴 غير متاح"
        st.info(status_badge if is_ar else ("🟢 Available" if available else "🔴 Unavailable"))

    with st.expander("✏️ تعديل الملف الشخصي" if is_ar else "✏️ Edit Profile"):
        with st.form("creator_profile_form"):
            display_name = st.text_input(
                "الاسم المعروض (EN)" if is_ar else "Display Name (EN)",
                value=profile.get("display_name", "") if profile else "",
            )
            display_name_ar = st.text_input(
                "الاسم المعروض (AR)" if is_ar else "Display Name (AR)",
                value=profile.get("display_name_ar", "") if profile else "",
            )
            bio = st.text_area("نبذة (EN)" if is_ar else "Bio (EN)", value=profile.get("bio", "") if profile else "")
            bio_ar = st.text_area("نبذة (AR)" if is_ar else "Bio (AR)", value=profile.get("bio_ar", "") if profile else "")
            city = st.text_input("المدينة" if is_ar else "City", value=profile.get("city", "") if profile else "", placeholder="Amman")
            rate = st.number_input(
                "سعر الاستشارة (JOD)" if is_ar else "Consultation Rate (JOD)",
                min_value=0.0, step=5.0,
                value=float(profile.get("consultation_rate_jod", 0)) if profile else 0.0,
            )
            is_available = st.checkbox(
                "متاح الآن" if is_ar else "Available Now",
                value=profile.get("is_available", True) if profile else True,
            )
            submitted = st.form_submit_button("حفظ" if is_ar else "Save", type="primary")

        if submitted and display_name:
            payload = {
                "display_name": display_name, "display_name_ar": display_name_ar,
                "bio": bio, "bio_ar": bio_ar, "city": city,
                "consultation_rate_jod": rate, "is_available": is_available,
            }
            try:
                if profile:
                    r = httpx.put(f"{API_BASE}/api/v1/content-creators/profile/me", headers=_headers(), json=payload, timeout=10)
                else:
                    r = httpx.post(f"{API_BASE}/api/v1/content-creators/profile", headers=_headers(), json=payload, timeout=10)
                if r.status_code in (200, 201):
                    st.success("تم الحفظ ✅" if is_ar else "Saved ✅")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as e:
                st.error(str(e))


def _portfolio_tab(is_ar: bool):
    st.subheader("معرض أعمالي" if is_ar else "My Portfolio")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/portfolio/mine", headers=_headers(), timeout=10)
        items = r.json() if r.status_code == 200 else []
    except Exception:
        items = []

    if items:
        for item in items:
            title = item.get("title_ar") or item.get("title", "") if is_ar else item.get("title", "")
            with st.container():
                st.write(f"**{title}** | {item.get('campaign_type', '—')} | 👁 {item.get('view_count', 0)}")
    else:
        st.info("لا توجد عناصر بعد." if is_ar else "No portfolio items yet.")

    with st.expander("➕ إضافة عنصر جديد" if is_ar else "➕ Add New Item"):
        with st.form("new_portfolio_item"):
            title = st.text_input("العنوان (EN)" if is_ar else "Title (EN)")
            title_ar = st.text_input("العنوان (AR)" if is_ar else "Title (AR)")
            description = st.text_area("الوصف (EN)" if is_ar else "Description (EN)")
            campaign_type = st.selectbox(
                "نوع الحملة" if is_ar else "Campaign Type",
                ["", "Brand Awareness", "Product Launch", "Event Promotion", "Tutorial", "Review"],
            )
            platforms = st.multiselect(
                "المنصات" if is_ar else "Platforms",
                ["Instagram", "TikTok", "YouTube", "Snapchat", "X"],
            )
            example_concept = st.text_area(
                "مثال مبدئي عام (ليس فكرة مخصصة)" if is_ar else "Generalized Example Concept (NOT a tailored idea)"
            )
            submitted = st.form_submit_button("نشر" if is_ar else "Publish", type="primary")

        if submitted and title:
            try:
                r = httpx.post(
                    f"{API_BASE}/api/v1/portfolio/",
                    headers=_headers(),
                    json={
                        "title": title, "title_ar": title_ar, "description": description,
                        "campaign_type": campaign_type or None, "platforms": platforms,
                        "example_concept": example_concept,
                    },
                    timeout=10,
                )
                if r.status_code == 201:
                    st.success("تم النشر ✅" if is_ar else "Published ✅")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as e:
                st.error(str(e))


def _bookings_tab(is_ar: bool):
    st.subheader("طلبات الحجز الواردة" if is_ar else "Incoming Booking Requests")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/content-creators/booking-requests/received", headers=_headers(), timeout=10)
        bookings = r.json() if r.status_code == 200 else []
    except Exception:
        bookings = []

    if bookings:
        for b in bookings:
            status = b.get("status", "pending")
            goal = b.get("campaign_goal", "—") or "—"
            budget = b.get("budget_jod")
            st.write(f"**{goal}** | {f'{budget:.2f} JOD' if budget else '—'} | 🔵 {status}")

            if status == "pending":
                col1, col2 = st.columns(2)
                if col1.button(f"✅ قبول" if is_ar else f"✅ Accept", key=f"accept_{b['id']}"):
                    try:
                        httpx.put(f"{API_BASE}/api/v1/content-creators/booking-requests/{b['id']}/accept", headers=_headers(), timeout=10)
                        st.success("تم القبول" if is_ar else "Accepted")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                if col2.button(f"❌ رفض" if is_ar else f"❌ Decline", key=f"decline_{b['id']}"):
                    try:
                        httpx.put(f"{API_BASE}/api/v1/content-creators/booking-requests/{b['id']}/decline", headers=_headers(), timeout=10)
                        st.success("تم الرفض" if is_ar else "Declined")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            st.divider()
    else:
        st.info("لا توجد طلبات حجز." if is_ar else "No booking requests yet.")


def _engagements_tab(is_ar: bool):
    st.subheader("مشاركاتي" if is_ar else "My Engagements")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/content-creators/engagements/", headers=_headers(), timeout=10)
        engagements = r.json() if r.status_code == 200 else []
    except Exception:
        engagements = []

    if engagements:
        for eng in engagements:
            status = eng.get("status", "active")
            fee = eng.get("agreed_fee_jod", 0)
            st.write(f"**#{eng['id'][:8]}** | {fee:.2f} JOD | {status}")
    else:
        st.info("لا توجد مشاركات بعد." if is_ar else "No engagements yet.")


def _submit_idea_tab(is_ar: bool):
    st.subheader("إرسال فكرة لمشاركة نشطة" if is_ar else "Submit Idea to Active Engagement")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/content-creators/engagements/", headers=_headers(), timeout=10)
        engagements = r.json() if r.status_code == 200 else []
    except Exception:
        engagements = []

    active = [e for e in engagements if e.get("status") == "active"]

    if not active:
        st.info("لا توجد مشاركات نشطة." if is_ar else "No active engagements to submit ideas to.")
        return

    options = {f"#{e['id'][:8]} ({e.get('agreed_fee_jod', 0):.2f} JOD)": e["id"] for e in active}
    selected = st.selectbox("اختر مشاركة" if is_ar else "Select Engagement", list(options.keys()))

    with st.form("submit_idea_form"):
        idea_brief = st.text_area(
            "فكرتك المخصصة (خاصة — لن تُشارك مع أطراف أخرى)" if is_ar else "Your Tailored Idea (Private — never shared publicly)",
            height=150,
        )
        idea_brief_ar = st.text_area("الفكرة (AR) — اختياري" if is_ar else "Idea (AR) — optional")
        submitted = st.form_submit_button("إرسال الفكرة" if is_ar else "Submit Idea", type="primary")

    if submitted and idea_brief:
        eng_id = options[selected]
        try:
            r = httpx.put(
                f"{API_BASE}/api/v1/content-creators/engagements/{eng_id}/submit-idea",
                headers=_headers(),
                json={"idea_brief": idea_brief, "idea_brief_ar": idea_brief_ar or None},
                timeout=10,
            )
            if r.status_code == 200:
                st.success("تم إرسال الفكرة ✅" if is_ar else "Idea submitted ✅")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Error"))
        except Exception as e:
            st.error(str(e))
