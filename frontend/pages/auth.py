"""
WaslAI.jo — Auth Page
Login + Registration forms
"""
import streamlit as st
import httpx
import os

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")


def render():
    lang = st.session_state.get("language", "ar")
    is_ar = lang == "ar"
    page = st.session_state.get("page", "login")

    tab1, tab2 = st.tabs(
        ["🔑 تسجيل الدخول" if is_ar else "🔑 Login",
         "📝 إنشاء حساب" if is_ar else "📝 Register"]
    )

    with tab1:
        _render_login(is_ar)

    with tab2:
        _render_register(is_ar)


def _render_login(is_ar: bool):
    st.subheader("تسجيل الدخول" if is_ar else "Login")
    with st.form("login_form"):
        email = st.text_input("البريد الإلكتروني" if is_ar else "Email")
        password = st.text_input("كلمة المرور" if is_ar else "Password", type="password")
        submitted = st.form_submit_button("دخول" if is_ar else "Login", type="primary")

    if submitted:
        try:
            response = httpx.post(
                f"{API_BASE}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.authenticated = True
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.session_state.page = "dashboard"
                st.success("تم تسجيل الدخول بنجاح ✅" if is_ar else "Login successful ✅")
                st.rerun()
            else:
                msg = "بيانات غير صحيحة" if is_ar else "Invalid credentials"
                st.error(msg)
        except httpx.ConnectError:
            st.error("لا يمكن الاتصال بالخادم" if is_ar else "Cannot connect to server. Is the API running?")


def _render_register(is_ar: bool):
    st.subheader("إنشاء حساب جديد" if is_ar else "Create Account")
    default_role = st.session_state.get("register_role", "merchant")

    with st.form("register_form"):
        full_name = st.text_input("الاسم الكامل (EN)" if is_ar else "Full Name (EN)")
        full_name_ar = st.text_input("الاسم الكامل (AR)" if is_ar else "Full Name (AR)")
        email = st.text_input("البريد الإلكتروني" if is_ar else "Email")
        phone = st.text_input("رقم الهاتف" if is_ar else "Phone (optional)")
        role = st.selectbox(
            "نوع الحساب" if is_ar else "Account Type",
            ["merchant", "influencer"],
            index=0 if default_role == "merchant" else 1,
        )
        password = st.text_input("كلمة المرور" if is_ar else "Password", type="password")
        submitted = st.form_submit_button("إنشاء الحساب" if is_ar else "Create Account", type="primary")

    if submitted:
        try:
            response = httpx.post(
                f"{API_BASE}/api/v1/auth/register",
                json={
                    "email": email, "password": password,
                    "full_name": full_name, "full_name_ar": full_name_ar,
                    "role": role, "phone": phone or None,
                },
                timeout=10,
            )
            if response.status_code == 201:
                st.success("تم إنشاء الحساب بنجاح! يرجى تسجيل الدخول." if is_ar else "Account created! Please login.")
            else:
                detail = response.json().get("detail", "Error")
                st.error(f"خطأ: {detail}" if is_ar else f"Error: {detail}")
        except httpx.ConnectError:
            st.error("لا يمكن الاتصال بالخادم" if is_ar else "Cannot connect to server.")
