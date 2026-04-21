export type Lang = "en" | "ar";

export const t: Record<string, Record<Lang, string>> = {
  // Nav
  home: { en: "Home", ar: "الرئيسية" },
  dashboard: { en: "Dashboard", ar: "لوحة التحكم" },
  campaigns: { en: "Campaigns", ar: "الحملات" },
  discover: { en: "Discover", ar: "اكتشف" },
  bookings: { en: "Bookings", ar: "الحجوزات" },
  escrow: { en: "Escrow", ar: "الضمان المالي" },
  contracts: { en: "Contracts", ar: "العقود" },
  wallet: { en: "Wallet", ar: "المحفظة" },
  settings: { en: "Settings", ar: "الإعدادات" },
  logout: { en: "Logout", ar: "تسجيل الخروج" },
  login: { en: "Login", ar: "تسجيل الدخول" },
  register: { en: "Register", ar: "إنشاء حساب" },
  profile: { en: "Profile", ar: "الملف الشخصي" },
  earnings: { en: "Earnings", ar: "الأرباح" },
  open_campaigns: { en: "Open Campaigns", ar: "الحملات المتاحة" },
  my_campaigns: { en: "My Campaigns", ar: "حملاتي" },
  god_mode: { en: "God Mode", ar: "لوحة الإدارة" },
  users: { en: "Users", ar: "المستخدمون" },
  disputes: { en: "Disputes", ar: "النزاعات" },
  analytics: { en: "Analytics", ar: "التحليلات" },

  // Auth
  email: { en: "Email", ar: "البريد الإلكتروني" },
  password: { en: "Password", ar: "كلمة المرور" },
  full_name: { en: "Full Name", ar: "الاسم الكامل" },
  username: { en: "Username", ar: "اسم المستخدم" },
  phone: { en: "Phone", ar: "رقم الهاتف" },
  role: { en: "Role", ar: "الدور" },
  merchant: { en: "Merchant", ar: "تاجر" },
  influencer: { en: "Influencer", ar: "مؤثر" },

  // Common
  save: { en: "Save", ar: "حفظ" },
  cancel: { en: "Cancel", ar: "إلغاء" },
  confirm: { en: "Confirm", ar: "تأكيد" },
  submit: { en: "Submit", ar: "إرسال" },
  loading: { en: "Loading...", ar: "جار التحميل..." },
  search: { en: "Search", ar: "بحث" },
  filter: { en: "Filter", ar: "تصفية" },
  book_now: { en: "Book Now", ar: "احجز الآن" },
  apply: { en: "Apply", ar: "تقديم" },
  generate: { en: "Generate", ar: "إنشاء" },
  download: { en: "Download", ar: "تحميل" },
  release_funds: { en: "Release Funds", ar: "تحرير الأموال" },
  raise_dispute: { en: "Raise Dispute", ar: "رفع نزاع" },
  redeem: { en: "Redeem", ar: "استرداد" },
  resolve: { en: "Resolve", ar: "حل" },

  // Dashboard labels
  budget_spent: { en: "Budget Spent", ar: "الميزانية المنفقة" },
  active: { en: "Active", ar: "نشط" },
  completed: { en: "Completed", ar: "مكتمل" },
  escrow_locked: { en: "Escrow Locked", ar: "مبالغ محجوزة" },
  aria_score: { en: "ARIA Score", ar: "نقاط ARIA" },
  tier: { en: "Tier", ar: "المستوى" },
  followers: { en: "Followers", ar: "المتابعون" },
  engagement: { en: "Engagement", ar: "التفاعل" },
  rate_per_post: { en: "Rate/Post", ar: "سعر المنشور" },
  niche: { en: "Niche", ar: "التخصص" },
  city: { en: "City", ar: "المدينة" },
  budget: { en: "Budget", ar: "الميزانية" },
  deadline: { en: "Deadline", ar: "الموعد النهائي" },
  deliverables: { en: "Deliverables", ar: "المخرجات" },
  brief: { en: "Brief", ar: "الموجز" },
  status: { en: "Status", ar: "الحالة" },
  points: { en: "Points", ar: "النقاط" },
  available_points: { en: "Available Points", ar: "النقاط المتاحة" },

  // Platform
  platform_name: { en: "WaslAI", ar: "وصل AI" },
  tagline: {
    en: "AI-Powered Influencer Marketing Platform",
    ar: "منصة تسويق المؤثرين بالذكاء الاصطناعي",
  },
};

export function tr(key: string, lang: Lang): string {
  return t[key]?.[lang] ?? key;
}
