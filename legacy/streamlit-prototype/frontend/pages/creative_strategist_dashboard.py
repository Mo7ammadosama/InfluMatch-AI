"""
WaslAI.jo — Creative Strategist Dashboard
Ideas, Engagements, Milestone Progress, Profile
"""
import streamlit as st
import httpx
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
MILESTONE_EVERY = 10


def _headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def render():
    lang = st.session_state.get("language", "ar")
    is_ar = lang == "ar"
    user = st.session_state.user or {}

    name = user.get("full_name_ar") or user.get("full_name", "")
    greeting = f"أهلاً {name} 🎨" if is_ar else f"Hello, {name} 🎨"
    st.header(greeting)
    st.caption("لوحة تحكم المستشار الإبداعي" if is_ar else "Creative Strategist Dashboard")

    tab_labels = (
        ["📋 ملفي الشخصي", "💡 أفكاري", "🌐 تصفح الأفكار", "🤝 مشاركاتي", "📈 الإنجازات"]
        if is_ar else
        ["📋 My Profile", "💡 My Ideas", "🌐 Browse Ideas", "🤝 My Engagements", "📈 Milestones"]
    )
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _profile_tab(is_ar)
    with tabs[1]:
        _my_ideas_tab(is_ar)
    with tabs[2]:
        _browse_ideas_tab(is_ar)
    with tabs[3]:
        _engagements_tab(is_ar)
    with tabs[4]:
        _milestones_tab(is_ar)


# ── Profile ────────────────────────────────────────────────────────────────────

def _profile_tab(is_ar: bool):
    st.subheader("ملفي الشخصي" if is_ar else "My Profile")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/creative-strategists/profile/me", headers=_headers(), timeout=10)
        profile = r.json() if r.status_code == 200 else None
    except Exception:
        profile = None

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        display_name = col1.text_input(
            "الاسم المعروض (EN)" if is_ar else "Display Name (EN)",
            value=profile.get("display_name", "") if profile else "",
        )
        display_name_ar = col2.text_input(
            "الاسم المعروض (AR)" if is_ar else "Display Name (AR)",
            value=profile.get("display_name_ar", "") if profile else "",
        )
        bio = st.text_area("النبذة (EN)" if is_ar else "Bio (EN)", value=profile.get("bio", "") if profile else "")
        bio_ar = st.text_area("النبذة (AR)" if is_ar else "Bio (AR)", value=profile.get("bio_ar", "") if profile else "")

        col3, col4 = st.columns(2)
        city = col3.text_input("المدينة" if is_ar else "City", value=profile.get("city", "Amman") if profile else "Amman")
        portfolio_url = col4.text_input("رابط المعرض" if is_ar else "Portfolio URL", value=profile.get("portfolio_url", "") if profile else "")

        consultation_rate = st.number_input(
            "رسوم الاستشارة (JOD / حملة)" if is_ar else "Consultation Rate (JOD / campaign)",
            value=float(profile.get("consultation_rate_jod", 0)) if profile else 0.0,
            min_value=0.0,
            step=10.0,
        )
        is_available = st.checkbox(
            "متاح للتعاون" if is_ar else "Available for hire",
            value=profile.get("is_available", True) if profile else True,
        )

        submitted = st.form_submit_button("حفظ الملف الشخصي" if is_ar else "Save Profile", type="primary")

    if submitted:
        payload = {
            "display_name": display_name,
            "display_name_ar": display_name_ar,
            "bio": bio,
            "bio_ar": bio_ar,
            "city": city,
            "portfolio_url": portfolio_url or None,
            "consultation_rate_jod": consultation_rate,
            "is_available": is_available,
        }
        try:
            if profile:
                r = httpx.put(f"{API_BASE}/api/v1/creative-strategists/profile/me", json=payload, headers=_headers(), timeout=10)
            else:
                r = httpx.post(f"{API_BASE}/api/v1/creative-strategists/profile", json=payload, headers=_headers(), timeout=10)
            if r.status_code in (200, 201):
                st.success("تم الحفظ ✅" if is_ar else "Profile saved ✅")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Error"))
        except Exception as e:
            st.error(str(e))


# ── My Ideas ───────────────────────────────────────────────────────────────────

def _my_ideas_tab(is_ar: bool):
    st.subheader("أفكاري" if is_ar else "My Ideas")

    try:
        r = httpx.get(f"{API_BASE}/api/v1/ideas/my", headers=_headers(), timeout=10)
        ideas = r.json() if r.status_code == 200 else []
    except Exception:
        ideas = []

    if ideas:
        import pandas as pd
        df = pd.DataFrame([{
            "ID": i["id"][:8],
            "العنوان" if is_ar else "Title": i.get("title", ""),
            "القطاع" if is_ar else "Category": i.get("business_category", ""),
            "الحالة" if is_ar else "Status": i.get("status", ""),
            "المشاهدات" if is_ar else "Views": i.get("view_count", 0),
            "التوظيف" if is_ar else "Hires": i.get("adoption_count", 0),
        } for i in ideas])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لم تنشر أي أفكار بعد." if is_ar else "No ideas published yet.")

    st.divider()
    st.subheader("نشر فكرة جديدة" if is_ar else "Submit New Idea")
    with st.form("new_idea_form"):
        col1, col2 = st.columns(2)
        title = col1.text_input("العنوان (EN)" if is_ar else "Title (EN)")
        title_ar = col2.text_input("العنوان (AR)" if is_ar else "Title (AR)")
        description = st.text_area("الوصف (EN)" if is_ar else "Description (EN)", height=100)
        description_ar = st.text_area("الوصف (AR)" if is_ar else "Description (AR)", height=100)
        target_audience = st.text_input("الجمهور المستهدف" if is_ar else "Target Audience")
        business_category = st.selectbox(
            "القطاع" if is_ar else "Category",
            ["fashion", "food", "tech", "beauty", "fitness", "travel", "lifestyle", "education", "entertainment", "other"],
        )
        col3, col4 = st.columns(2)
        estimated_budget = col3.number_input("الميزانية التقديرية (JOD)" if is_ar else "Est. Budget (JOD)", min_value=0.0, step=50.0)
        timeline_days = col4.number_input("المدة (أيام)" if is_ar else "Timeline (days)", min_value=1, step=1, value=30)
        submitted = st.form_submit_button("نشر الفكرة" if is_ar else "Publish Idea", type="primary")

    if submitted and title and description:
        payload = {
            "title": title, "title_ar": title_ar,
            "description": description, "description_ar": description_ar,
            "target_audience": target_audience or None,
            "business_category": business_category,
            "estimated_budget_jod": estimated_budget or None,
            "timeline_days": int(timeline_days),
            "suggested_platforms": [], "content_format": [],
        }
        try:
            r = httpx.post(f"{API_BASE}/api/v1/ideas/", json=payload, headers=_headers(), timeout=10)
            if r.status_code == 201:
                st.success("تم نشر الفكرة ✅" if is_ar else "Idea published ✅")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Error"))
        except Exception as e:
            st.error(str(e))


# ── Browse Ideas ───────────────────────────────────────────────────────────────

def _browse_ideas_tab(is_ar: bool):
    st.subheader("تصفح الأفكار" if is_ar else "Browse Ideas")
    try:
        r = httpx.get(f"{API_BASE}/api/v1/ideas/", headers=_headers(), timeout=10)
        ideas = r.json() if r.status_code == 200 else []
    except Exception:
        ideas = []

    if ideas:
        for idea in ideas:
            with st.expander(f"💡 {idea.get('title', '')} | {idea.get('business_category', '')}"):
                st.write(idea.get("description", ""))
                col1, col2, col3 = st.columns(3)
                col1.metric("الحالة" if is_ar else "Status", idea.get("status", ""))
                col2.metric("المشاهدات" if is_ar else "Views", idea.get("view_count", 0))
                col3.metric("الميزانية (JOD)" if is_ar else "Budget (JOD)", idea.get("estimated_budget_jod") or "—")
    else:
        st.info("لا توجد أفكار متاحة." if is_ar else "No ideas available.")


# ── Engagements ────────────────────────────────────────────────────────────────

def _engagements_tab(is_ar: bool):
    st.subheader("مشاركاتي" if is_ar else "My Engagements")
    try:
        r = httpx.get(f"{API_BASE}/api/v1/ideas/engagements/my", headers=_headers(), timeout=10)
        engagements = r.json() if r.status_code == 200 else []
    except Exception:
        engagements = []

    if engagements:
        import pandas as pd
        df = pd.DataFrame([{
            "ID": e["id"][:8],
            "الحالة" if is_ar else "Status": e.get("status", ""),
            "الرسوم (JOD)" if is_ar else "Fee (JOD)": e.get("agreed_fee_jod", 0),
            "تاريخ الإنشاء" if is_ar else "Created": e.get("created_at", "")[:10],
        } for e in engagements])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("لا توجد مشاركات بعد." if is_ar else "No engagements yet.")


# ── Milestones ─────────────────────────────────────────────────────────────────

def _milestones_tab(is_ar: bool):
    st.subheader("إنجازاتي" if is_ar else "Milestones")
    try:
        r = httpx.get(f"{API_BASE}/api/v1/creative-strategists/profile/me", headers=_headers(), timeout=10)
        profile = r.json() if r.status_code == 200 else {}
    except Exception:
        profile = {}

    completed = profile.get("completed_engagements", 0)
    milestone_count = profile.get("milestone_count", 0)
    total_earned = profile.get("total_earned_jod", 0)
    progress = completed % MILESTONE_EVERY

    col1, col2, col3 = st.columns(3)
    col1.metric("المشاركات المكتملة" if is_ar else "Completed Engagements", completed)
    col2.metric("المعالم المحققة" if is_ar else "Milestones Reached", milestone_count)
    col3.metric("إجمالي الأرباح (JOD)" if is_ar else "Total Earned (JOD)", f"{total_earned:.2f}")

    st.divider()
    label = f"{'التقدم نحو المعلم التالي' if is_ar else 'Progress to Next Milestone'}: {progress}/{MILESTONE_EVERY}"
    st.progress(progress / MILESTONE_EVERY, text=label)
    remaining = MILESTONE_EVERY - progress
    st.caption(
        f"{'تحتاج إلى' if is_ar else 'Need'} {remaining} {'مشاركات مكتملة إضافية للحصول على مكافأة 20 JOD' if is_ar else 'more completed engagements for a 20 JOD bonus'}"
    )
