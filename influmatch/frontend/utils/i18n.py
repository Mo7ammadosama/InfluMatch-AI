"""Bilingual label lookup — Arabic / English"""
import streamlit as st

LABELS = {
    "app_name":       {"ar": "إنفلو ماتش",       "en": "InfluMatch.jo"},
    "login":          {"ar": "تسجيل الدخول",      "en": "Login"},
    "register":       {"ar": "إنشاء حساب",        "en": "Register"},
    "logout":         {"ar": "خروج",              "en": "Logout"},
    "email":          {"ar": "البريد الإلكتروني",  "en": "Email"},
    "password":       {"ar": "كلمة المرور",       "en": "Password"},
    "full_name":      {"ar": "الاسم الكامل",      "en": "Full Name"},
    "role":           {"ar": "نوع الحساب",        "en": "Account Type"},
    "merchant":       {"ar": "تاجر",              "en": "Merchant"},
    "influencer":     {"ar": "مؤثر",              "en": "Influencer"},
    "dashboard":      {"ar": "لوحة التحكم",       "en": "Dashboard"},
    "campaigns":      {"ar": "الحملات",           "en": "Campaigns"},
    "influencers":    {"ar": "المؤثرون",          "en": "Influencers"},
    "wallet":         {"ar": "المحفظة",           "en": "Wallet"},
    "contracts":      {"ar": "العقود",            "en": "Contracts"},
    "escrow":         {"ar": "الضمان المالي",     "en": "Escrow"},
    "settings":       {"ar": "الإعدادات",         "en": "Settings"},
    "save":           {"ar": "حفظ",               "en": "Save"},
    "cancel":         {"ar": "إلغاء",             "en": "Cancel"},
    "submit":         {"ar": "إرسال",             "en": "Submit"},
    "loading":        {"ar": "جاري التحميل...",   "en": "Loading..."},
    "error":          {"ar": "خطأ",               "en": "Error"},
    "success":        {"ar": "نجاح",              "en": "Success"},
    "aria_score":     {"ar": "نقاط ARIA",         "en": "ARIA Score"},
    "total_budget":   {"ar": "الميزانية الإجمالية","en": "Total Budget"},
    "status":         {"ar": "الحالة",            "en": "Status"},
    "followers":      {"ar": "المتابعون",         "en": "Followers"},
    "engagement":     {"ar": "معدل التفاعل",      "en": "Engagement Rate"},
    "niche":          {"ar": "التخصص",            "en": "Niche"},
    "city":           {"ar": "المدينة",           "en": "City"},
    "create_campaign":{"ar": "إنشاء حملة",       "en": "Create Campaign"},
    "view_details":   {"ar": "عرض التفاصيل",     "en": "View Details"},
    "points":         {"ar": "النقاط",            "en": "Points"},
    "tier":           {"ar": "المستوى",           "en": "Tier"},
    "chat_with_aria": {"ar": "تحدث مع ARIA",     "en": "Chat with ARIA"},
    "type_message":   {"ar": "اكتب رسالتك...",   "en": "Type your message..."},
    "send":           {"ar": "إرسال",             "en": "Send"},
    "welcome":        {"ar": "أهلاً وسهلاً",     "en": "Welcome"},
    "platform":       {"ar": "المنصة",           "en": "Platform"},
    "jordan_market":  {"ar": "سوق الأردن",       "en": "Jordan Market"},
}

def t(key: str) -> str:
    lang = st.session_state.get("lang", "ar")
    return LABELS.get(key, {}).get(lang, key)
