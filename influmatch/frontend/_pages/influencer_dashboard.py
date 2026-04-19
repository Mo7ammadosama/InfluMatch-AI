"""Influencer Dashboard"""
import streamlit as st
from ..utils.api_client import api_get, api_post, api_list
from ..utils.i18n import t
from ..utils.session import get_user

TIER_META = {
    "PLATINUM": ("🏆", "#e5e7eb", "#111"),
    "GOLD":     ("🥇", "#fbbf24", "#111"),
    "SILVER":   ("🥈", "#9ca3af", "white"),
    "BRONZE":   ("🥉", "#b45309", "white"),
    "UNRANKED": ("📊", "#334155", "#94A3B8"),
}

def render():
    user = get_user()
    name = user.get("full_name_ar") or user.get("full_name_en", "مؤثر") if user else "مؤثر"

    st.markdown(f"""
    <div class="influencer-banner">
      <div style="display:flex;align-items:center;gap:1rem">
        <div style="font-size:2.5rem">🌟</div>
        <div>
          <div style="font-size:1.4rem;font-weight:700;color:#8b5cf6">أهلاً، {name}</div>
          <div style="color:#a0a0b0;font-size:0.85rem">بوابة المؤثر — InfluMatch.jo</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    profile   = api_get("/api/influencers/me") or {}
    campaigns = api_list("/api/campaigns/my")
    wallet    = api_get("/api/wallet/me") or {}

    if not profile or profile.get("id") is None:
        _render_profile_setup(st.session_state.get("lang", "ar"))
        return

    score    = profile.get("aria_score", 0)
    tier     = profile.get("aria_tier", "UNRANKED")
    earnings = wallet.get("available_points", wallet.get("balance_points", 0)) * 0.01
    active   = [c for c in campaigns if c.get("status") == "in_progress"]

    tier_color = {"PLATINUM": "#e5e7eb", "GOLD": "#fbbf24", "SILVER": "#9ca3af",
                  "BRONZE": "#b45309", "UNRANKED": "#6b7280"}.get(tier, "#6b7280")

    col_score, col_tier, col_earn, col_active = st.columns(4)
    with col_score:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">ARIA SCORE</div>
          <div class="score-ring">{score:.0f}</div>
        </div>""", unsafe_allow_html=True)
    with col_tier:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">المستوى</div>
          <div style="font-size:1.5rem;font-weight:700;color:{tier_color}">{tier}</div>
        </div>""", unsafe_allow_html=True)
    with col_earn:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">أرباحي</div>
          <div style="font-size:1.3rem;font-weight:700;color:#00ff88">{earnings:.3f} JOD</div>
        </div>""", unsafe_allow_html=True)
    with col_active:
        st.markdown(f"""
        <div class="aria-card" style="text-align:center">
          <div style="color:#a0a0b0;font-size:0.75rem;margin-bottom:0.5rem">حملات نشطة</div>
          <div style="font-size:1.8rem;font-weight:700;color:#f59e0b">{len(active)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 حملاتي", "رفع تقرير", "👤 ملفي الشخصي"])

    with tab1:
        if not campaigns:
            st.info("لم تنضم لأي حملة بعد — اكتشف الفرص المتاحة!")
            if st.button("استكشاف الحملات", type="primary"):
                st.session_state["page"] = "discover"
                st.rerun()
        else:
            for c in campaigns:
                status_color = {"in_progress": "#f59e0b", "active": "#00ff88",
                                "completed": "#8b5cf6", "disputed": "#ef4444"}.get(c.get("status", ""), "#6b7280")
                title = c.get("title_en") or c.get("title_ar") or c.get("title", "—")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="aria-card">
                      <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                          <div style="font-weight:700">{title}</div>
                          <div style="color:#a0a0b0;font-size:0.8rem">
                            {c.get('total_budget',0):.3f} JOD · {c.get('niche','—')}
                          </div>
                        </div>
                        <span style="color:{status_color};border:1px solid {status_color};
                                     padding:0.2rem 0.7rem;border-radius:20px;font-size:0.75rem">
                          {c.get('status','—')}
                        </span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if c.get("status") in ("active", "draft"):
                        if st.button("تقدّم", key=f"apply_{c.get('id',0)}", use_container_width=True):
                            s, r = api_post(f"/api/campaigns/{c.get('id')}/apply", json={})
                            if s in (200, 201):
                                st.success("تم إرسال الطلب!")
                            elif s == 409:
                                st.info("طلبت بالفعل.")
                            else:
                                st.error(r.get("detail", "خطأ"))

    with tab2:
        st.markdown("#### رفع تقرير الحملة")
        st.markdown('<div class="aria-card">', unsafe_allow_html=True)
        camp_options = {(c.get("title_en") or c.get("title_ar") or str(c.get("id"))): c.get("id")
                        for c in active} if active else {}
        if camp_options:
            selected = st.selectbox("اختر الحملة", list(camp_options.keys()))
            uploaded = st.file_uploader(
                "ارفع screenshot أو تقرير PDF",
                type=["png", "jpg", "jpeg", "pdf"],
                help="الحد الأقصى: 10MB"
            )
            if uploaded and st.button("رفع التقرير", type="primary"):
                cid = camp_options[selected]
                import httpx
                try:
                    from ..utils.api_client import api_get as _ag
                    token = st.session_state.get("token", "")
                    r = httpx.post(
                        f"http://localhost:8080/api/campaigns/{cid}/upload-report",
                        files={"file": (uploaded.name, uploaded.read(), uploaded.type)},
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=30
                    )
                    if r.status_code == 200:
                        st.success("تم رفع التقرير بنجاح!")
                    else:
                        st.error(f"خطأ في الرفع ({r.status_code})")
                except Exception as exc:
                    st.error(f"خطأ: {exc}")
        else:
            st.info("لا توجد حملات نشطة حالياً تحتاج تقريراً")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        if not profile:
            st.warning("لم يتم إعداد ملفك الشخصي بعد")
            if st.button("إعداد الملف الشخصي", type="primary"):
                st.session_state["page"] = "settings"
                st.rerun()
        else:
            # ── Social stats ────────────────────────────────────────
            st.markdown("#### 📱 الحسابات الاجتماعية")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("المدينة",   profile.get("city",  "—"))
            s2.metric("التخصص",   profile.get("niche",  "—"))
            s3.metric("Instagram", f"{profile.get('instagram_followers',0):,} متابع")
            s4.metric("TikTok",    f"{profile.get('tiktok_followers',0):,} متابع")

            st.markdown("---")

            # ── ARIA Score breakdown ────────────────────────────────
            st.markdown("#### 🤖 تفاصيل نقاط ARIA")
            eng  = float(profile.get("engagement_score",   0) or 0)
            auth = float(profile.get("authenticity_score", 0) or 0)
            rel  = float(profile.get("relevance_score",    0) or 0)
            del_ = float(profile.get("delivery_score",     0) or 0)
            cq   = float(profile.get("content_quality_score", 70) or 70)

            def _score_bar(label, val, max_val, color):
                pct = min(int(val / max_val * 100), 100)
                st.markdown(f"""
                <div style="margin-bottom:0.8rem">
                  <div style="display:flex;justify-content:space-between;
                              font-size:0.8rem;color:#a0a0b0;margin-bottom:0.3rem">
                    <span>{label}</span><span style="color:{color};font-weight:700">{val:.1f} / {max_val}</span>
                  </div>
                  <div style="background:rgba(255,255,255,0.07);border-radius:6px;height:8px;overflow:hidden">
                    <div style="width:{pct}%;height:100%;background:{color};
                                border-radius:6px;transition:width .4s ease"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

            _score_bar("⚡ Engagement Score",     eng,  30,  "#f59e0b")
            _score_bar("🛡️ Authenticity Score",  auth, 25,  "#8b5cf6")
            _score_bar("🎯 Relevance Score",      rel,  10,  "#3b82f6")
            _score_bar("📦 Delivery Score",       del_, 15,  "#00ff88")
            _score_bar("🎨 Content Quality",      cq,   100, "#ec4899")

            st.markdown(f"""
            <div style="background:rgba(0,255,136,0.06);border:1px solid rgba(0,255,136,0.25);
                        border-radius:12px;padding:0.8rem 1.2rem;margin-top:0.5rem;
                        display:flex;justify-content:space-between;align-items:center">
              <span style="color:#a0a0b0;font-size:0.85rem">ARIA Score الإجمالي</span>
              <span style="font-size:1.6rem;font-weight:800;color:#00ff88">
                {profile.get('aria_score', 0):.1f}
              </span>
            </div>""", unsafe_allow_html=True)

            st.markdown("---")
            if st.button("✏️ تعديل الملف الشخصي / Edit Profile", use_container_width=True):
                st.session_state["page"] = "settings"
                st.rerun()


def _render_profile_setup(lang):
    """Shown to influencers who haven't completed their profile yet"""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,0.15),rgba(109,40,217,0.05));
                border:1px solid rgba(124,58,237,0.4);border-radius:16px;
                padding:2rem;text-align:center;margin-bottom:1.5rem">
        <div style="font-size:3rem">🌟</div>
        <h3 style="color:#A78BFA;margin:0.5rem 0">
            {'أكمل ملفك الشخصي للبدء' if lang=='ar' else 'Complete Your Influencer Profile'}
        </h3>
        <p style="color:#64748B;font-size:0.9rem">
            {'أدخل بيانات حساباتك الاجتماعية لحساب نقاط ARIA وعرضك للتجار' if lang=='ar'
             else 'Add your social media stats to calculate your ARIA score and get discovered by merchants'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("influencer_profile_form"):
        st.markdown(f"#### {'معلومات الحساب الاجتماعي' if lang=='ar' else 'Social Media Info'}")
        col1, col2 = st.columns(2)
        with col1:
            ig_handle     = st.text_input("Instagram Handle", placeholder="@yourhandle")
            ig_followers  = st.number_input("Instagram Followers", min_value=0, value=0, step=100)
            ig_engagement = st.number_input("Instagram Engagement Rate (%)", min_value=0.0, max_value=100.0, value=2.5, step=0.1)
        with col2:
            tt_handle    = st.text_input("TikTok Handle", placeholder="@yourhandle")
            tt_followers = st.number_input("TikTok Followers", min_value=0, value=0, step=100)
            niche        = st.selectbox("Primary Niche / التخصص", [
                "Fashion", "Food", "Tech", "Beauty", "Fitness",
                "Travel", "Gaming", "Education", "Lifestyle", "Sports"
            ])
        bio_en = st.text_area("Bio (English)", height=80, placeholder="Tell merchants about yourself...")
        bio_ar = st.text_area("النبذة (عربي)", height=80, placeholder="عرّف التجار بنفسك...")

        submitted = st.form_submit_button("🚀 Create Profile & Calculate ARIA Score", use_container_width=True)
        if submitted:
            if ig_followers == 0 and tt_followers == 0:
                st.error("Add at least one social media account with followers.")
            else:
                s, r = api_post("/api/influencers/", json={
                    "instagram_handle"           : ig_handle,
                    "instagram_followers"        : int(ig_followers),
                    "instagram_engagement_rate"  : ig_engagement,
                    "tiktok_handle"              : tt_handle,
                    "tiktok_followers"           : int(tt_followers),
                    "niche"                      : niche,
                    "bio_en"                     : bio_en,
                    "bio_ar"                     : bio_ar,
                })
                if s in (200, 201):
                    st.success("✅ Profile created! Calculating your ARIA score...")
                    st.rerun()
                else:
                    st.error(f"❌ {r.get('detail', 'Error creating profile')}")
