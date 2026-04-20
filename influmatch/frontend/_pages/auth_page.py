"""Login & Register page — WaslAI.jo"""
import streamlit as st
from ..utils.api_client import api_post, api_get
from ..utils.i18n import t


def render_login():
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
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">Wasl</span><span
             style="background:linear-gradient(135deg,#f59e0b,#fbbf24);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">AI</span><span
             style="color:#f59e0b;font-size:1.3rem">.jo</span>
      </div>
      <p style="color:#64748b;font-size:0.85rem;margin:0;letter-spacing:0.02em">
        {tagline}
      </p>
    </div>
    """.replace("{tagline}", t("tagline")), unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 " + t("login"), "📝 " + t("register")])

    # ── Login Tab ────────────────────────────────────────────────
    with tab1:
        with st.form("login_form"):
            email     = st.text_input(t("email"), placeholder="you@example.com")
            password  = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login"), use_container_width=True, type="primary")
            if submitted:
                if not email or not password:
                    st.error(t("fill_all_fields"))
                else:
                    status, resp = api_post("/api/v1/auth/login", data={"username": email, "password": password})
                    if status == 200:
                        st.session_state["token"] = resp.get("access_token")
                        st.session_state["role"]  = resp.get("role", "merchant")
                        me = api_get("/api/auth/me")
                        if me:
                            st.session_state["user"] = me
                            st.session_state["role"] = me.get("role", "merchant")
                        st.session_state["page"] = "dashboard"
                        display_name = (me or {}).get("full_name_en") or (me or {}).get("full_name_ar") or email.split("@")[0]
                        st.success(f"✅ {t('login_success')} {display_name}!")
                        st.rerun()
                    else:
                        detail = resp.get("detail", t("login_failed"))
                        st.error(f"❌ {detail}")

        st.markdown("---")
        st.caption("Test accounts → Merchant: merchant@waslai.jo | Influencer: influencer@waslai.jo | Password: WaslAI@2026")

    # ── Register Tab ─────────────────────────────────────────────
    with tab2:
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name_en = st.text_input(t("full_name_en"), placeholder="Mohammad Osama")
            with col2:
                full_name_ar = st.text_input(t("full_name_ar"), placeholder="محمد أسامة")

            username = st.text_input(t("username"), placeholder="mohammados", help="Unique username, no spaces")
            email    = st.text_input(t("email"), placeholder="you@example.com")
            password = st.text_input(t("password"), type="password")
            phone    = st.text_input(t("phone"), placeholder="+962791234567")
            role     = st.selectbox(
                t("role"),
                ["merchant", "influencer"],
                format_func=lambda x: f"🏪 {t('merchant')}" if x == "merchant" else f"⭐ {t('influencer')}"
            )

            submitted = st.form_submit_button(t("register"), use_container_width=True, type="primary")
            if submitted:
                if not all([username, email, password]):
                    st.error(t("fill_all_fields"))
                elif len(password) < 8:
                    st.error(t("password_min"))
                else:
                    status, resp = api_post("/api/v1/auth/register", json={
                        "email":        email,
                        "username":     username,
                        "password":     password,
                        "role":         role,
                        "full_name_en": full_name_en or None,
                        "full_name_ar": full_name_ar or None,
                        "phone":        phone or None,
                    })
                    if status in (200, 201):
                        st.success(f"✅ {t('register_success')}")
                        st.balloons()
                    elif status == 409:
                        st.warning(f"⚠️ {t('email_taken')}")
                    else:
                        detail = resp.get("detail", t("register_failed"))
                        st.error(f"❌ {detail}")
