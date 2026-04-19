"""Login & Register page — InfluMatch.jo"""
import streamlit as st
from ..utils.api_client import api_post, api_get
from ..utils.i18n import t

def render_login():
    lang = st.session_state.get("lang", "ar")
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1.5rem">
      <div style="display:inline-flex;align-items:center;justify-content:center;
                  width:64px;height:64px;border-radius:18px;
                  background:linear-gradient(135deg,#7c3aed,#4f46e5);
                  box-shadow:0 6px 30px rgba(124,58,237,0.5);margin-bottom:1rem">
        <span style="font-size:2rem;line-height:1">&#9889;</span>
      </div>
      <div style="font-size:2rem;font-weight:900;letter-spacing:-0.03em;margin-bottom:0.3rem">
        <span style="background:linear-gradient(135deg,#a78bfa,#818cf8);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">Influ</span><span
             style="background:linear-gradient(135deg,#f59e0b,#fbbf24);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">Match</span><span
             style="color:#f59e0b;font-size:1.3rem">.jo</span>
      </div>
      <p style="color:#64748b;font-size:0.82rem;margin:0;letter-spacing:0.04em">
        منصة التسويق عبر المؤثرين في الأردن &nbsp;&middot;&nbsp; Jordan Influencer Marketing Platform
      </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 " + t("login"), "📝 " + t("register")])

    # ── Login Tab ────────────────────────────────────────────────
    with tab1:
        with st.form("login_form"):
            email    = st.text_input(t("email"), placeholder="you@example.com")
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login"), use_container_width=True, type="primary")
            if submitted:
                if not email or not password:
                    st.error("يرجى ملء جميع الحقول / Please fill all fields")
                else:
                    status, resp = api_post(
                        "/api/auth/login",
                        data={"username": email, "password": password}
                    )
                    if status == 200:
                        st.session_state["token"] = resp.get("access_token")
                        st.session_state["role"]  = resp.get("role", "merchant")
                        # Fetch full user profile
                        me = api_get("/api/auth/me")
                        if me:
                            st.session_state["user"] = me
                            st.session_state["role"] = me.get("role", "merchant")
                        st.session_state["page"] = "dashboard"
                        display_name = (
                            (me or {}).get("full_name_en") or
                            (me or {}).get("full_name_ar") or
                            email.split("@")[0]
                        )
                        st.success(f"✅ أهلاً {display_name}!")
                        st.rerun()
                    else:
                        detail = resp.get("detail", "فشل تسجيل الدخول / Login failed")
                        st.error(f"❌ {detail}")

        st.markdown("---")
        st.caption("Admin: admin@influmatch.jo / Admin@2024")

    # ── Register Tab ─────────────────────────────────────────────
    with tab2:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name_en = st.text_input("Full Name (English)", placeholder="Mohammad Osama")
            with col2:
                full_name_ar = st.text_input("الاسم الكامل (عربي)", placeholder="محمد أسامة")

            username = st.text_input(
                "Username / اسم المستخدم",
                placeholder="mohammados",
                help="Unique username, no spaces"
            )
            email    = st.text_input(t("email"), placeholder="you@example.com")
            password = st.text_input(t("password"), type="password")
            phone    = st.text_input("Phone / الهاتف", placeholder="+962791234567")
            role     = st.selectbox(
                t("role"),
                ["merchant", "influencer"],
                format_func=lambda x: "🏪 Merchant / تاجر" if x == "merchant" else "⭐ Influencer / مؤثر"
            )

            submitted = st.form_submit_button(t("register"), use_container_width=True, type="primary")
            if submitted:
                if not all([username, email, password]):
                    st.error("البريد الإلكتروني، اسم المستخدم، وكلمة المرور مطلوبة")
                elif len(password) < 8:
                    st.error("كلمة المرور يجب أن تكون 8 أحرف على الأقل / Password must be at least 8 characters")
                else:
                    status, resp = api_post("/api/auth/register", json={
                        "email"        : email,
                        "username"     : username,
                        "password"     : password,
                        "role"         : role,
                        "full_name_en" : full_name_en or None,
                        "full_name_ar" : full_name_ar or None,
                        "phone"        : phone or None,
                    })
                    if status in (200, 201):
                        st.success("✅ تم إنشاء الحساب بنجاح! يرجى تسجيل الدخول / Account created! Please login.")
                        st.balloons()
                    elif status == 409:
                        st.warning("⚠️ البريد الإلكتروني مسجل مسبقاً / Email already registered")
                    else:
                        detail = resp.get("detail", "فشل التسجيل / Registration failed")
                        st.error(f"❌ {detail}")
