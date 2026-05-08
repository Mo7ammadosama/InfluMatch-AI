"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import {
  getMyCreatorProfile, updateCreatorProfile,
  getReceivedBookings, getMyCCEngagements,
  getMyPortfolio, acceptBooking, declineBooking,
} from "@/lib/api";
import { ContentCreatorProfile, BookingRequest, CCEngagement, PortfolioItem } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import {
  Star, CheckCircle2, Clock, Plus, Briefcase,
  LayoutGrid, TrendingUp, ToggleLeft, ToggleRight, ArrowRight,
} from "lucide-react";

const statusStyles: Record<string, string> = {
  active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  idea_submitted: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  idea_approved: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  completed: "bg-white/10 text-white/50 border-white/10",
  cancelled: "bg-red-500/15 text-red-400 border-red-500/30",
  pending: "bg-violet-500/15 text-violet-400 border-violet-500/30",
  accepted: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  declined: "bg-red-500/15 text-red-400 border-red-500/30",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${statusStyles[status] ?? "bg-white/5 text-white/40 border-white/10"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function ContentCreatorDashboard() {
  const { user, lang } = useApp();
  const [profile, setProfile] = useState<ContentCreatorProfile | null>(null);
  const [bookings, setBookings] = useState<BookingRequest[]>([]);
  const [engagements, setEngagements] = useState<CCEngagement[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  useEffect(() => {
    Promise.all([
      getMyCreatorProfile().catch(() => null),
      getReceivedBookings().catch(() => null),
      getMyCCEngagements().catch(() => null),
      getMyPortfolio().catch(() => null),
    ]).then(([p, b, e, port]) => {
      if (p) setProfile(p.data);
      if (b) setBookings(Array.isArray(b.data) ? b.data : []);
      if (e) setEngagements(Array.isArray(e.data) ? e.data : []);
      if (port) setPortfolio(Array.isArray(port.data) ? port.data : []);
    }).finally(() => setLoading(false));
  }, []);

  async function toggleAvailability() {
    if (!profile) return;
    setToggling(true);
    try {
      const r = await updateCreatorProfile({ is_available: !profile.is_available });
      setProfile(r.data);
      toast.success(lang === "ar" ? "تم التحديث" : "Availability updated");
    } catch {
      toast.error(lang === "ar" ? "فشل التحديث" : "Update failed");
    } finally {
      setToggling(false);
    }
  }

  async function refreshEngagements() {
    const e = await getMyCCEngagements().catch(() => null);
    if (e) setEngagements(Array.isArray(e.data) ? e.data : []);
  }

  async function handleAccept(id: string) {
    try {
      await acceptBooking(id);
      setBookings((b) => b.map((r) => r.id === id ? { ...r, status: "accepted" } : r));
      toast.success(lang === "ar" ? "تم قبول الطلب! سيظهر في المشاركات النشطة" : "Booking accepted! It will appear in Active Engagements");
      await refreshEngagements();
    } catch {
      toast.error(lang === "ar" ? "فشل القبول" : "Accept failed");
    }
  }

  async function handleDecline(id: string) {
    try {
      await declineBooking(id);
      setBookings((b) => b.map((r) => r.id === id ? { ...r, status: "declined" } : r));
      toast.success(lang === "ar" ? "تم رفض الطلب" : "Booking declined");
    } catch {
      toast.error(lang === "ar" ? "فشل الرفض" : "Decline failed");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  const name = lang === "ar" ? (user?.full_name_ar ?? user?.full_name) : user?.full_name;
  const pendingBookings = bookings.filter((b) => b.status === "pending");
  const recentBookings = bookings.filter((b) => b.status !== "pending");
  const activeEngagements = engagements.filter((e) => e.status === "active" || e.status === "idea_submitted");

  return (
    <div className="space-y-6 max-w-6xl">

      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-pink-900/50 via-rose-900/30 to-bg-surface border border-pink-700/20 p-6">
        <div className="absolute top-0 right-0 w-64 h-64 bg-pink-500/5 rounded-full -translate-y-1/2 translate-x-1/4 blur-3xl pointer-events-none" />
        <div className="relative flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">✍️</span>
              <h1 className="text-2xl font-bold text-white">
                {lang === "ar" ? `مرحباً، ${name}` : `Welcome, ${name}`}
              </h1>
            </div>
            <p className="text-white/50 text-sm">
              {lang === "ar" ? "لوحة تحكم منشئ المحتوى · WaslAI" : "Content Creator Dashboard · WaslAI"}
            </p>
            {profile?.is_verified && (
              <div className="inline-flex items-center gap-1.5 mt-2 px-2.5 py-1 rounded-full bg-pink-500/15 border border-pink-500/30 text-pink-400 text-xs font-medium">
                <CheckCircle2 size={11} />
                {lang === "ar" ? "موثّق" : "Verified Creator"}
              </div>
            )}
          </div>
          <div className="flex flex-col gap-2 shrink-0">
            <button
              onClick={toggleAvailability}
              disabled={toggling || !profile}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition text-sm text-white"
            >
              {profile?.is_available
                ? <><ToggleRight size={18} className="text-emerald-400" />{lang === "ar" ? "متاح الآن" : "Available"}</>
                : <><ToggleLeft size={18} className="text-white/30" />{lang === "ar" ? "غير متاح" : "Unavailable"}</>}
            </button>
            <Link href="/content-creator/profile">
              <Button variant="ghost" size="sm" className="gap-2 text-white/50 hover:text-white w-full justify-center">
                {lang === "ar" ? "تعديل الملف" : "Edit Profile"}
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* No profile prompt */}
      {!profile && (
        <div className="flex items-center gap-4 p-4 rounded-xl border border-pink-500/30 bg-pink-500/5">
          <div className="flex-1">
            <div className="font-semibold text-pink-400 text-sm">
              {lang === "ar" ? "أنشئ ملفك الشخصي أولاً" : "Set up your Creator Profile"}
            </div>
            <div className="text-white/50 text-xs mt-0.5">
              {lang === "ar" ? "أضف بياناتك لتبدأ في استقبال طلبات الحجز" : "Add your details to start receiving booking requests"}
            </div>
          </div>
          <Link href="/content-creator/profile">
            <Button size="sm" className="bg-pink-600 hover:bg-pink-500 text-white shrink-0">
              {lang === "ar" ? "إنشاء الملف" : "Set Up"}
              <ArrowRight size={13} className="ml-1" />
            </Button>
          </Link>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { icon: <CheckCircle2 size={18} className="text-emerald-400" />, value: profile?.completed_engagements ?? 0, label: lang === "ar" ? "مشاركات مكتملة" : "Completed", bg: "bg-emerald-500/10" },
          { icon: <Star size={18} className="text-amber-400" />, value: profile?.avg_rating?.toFixed(1) ?? "—", label: lang === "ar" ? "متوسط التقييم" : "Avg Rating", bg: "bg-amber-500/10" },
          { icon: <TrendingUp size={18} className="text-pink-400" />, value: fmtJOD(profile?.total_earned_jod ?? 0), label: lang === "ar" ? "إجمالي الأرباح" : "Total Earned", bg: "bg-pink-500/10" },
          { icon: <LayoutGrid size={18} className="text-blue-400" />, value: portfolio.length, label: lang === "ar" ? "عناصر المعرض" : "Portfolio Items", bg: "bg-blue-500/10" },
        ].map((kpi, i) => (
          <div key={i} className="glass-card p-4">
            <div className={`w-9 h-9 rounded-xl ${kpi.bg} flex items-center justify-center mb-3`}>
              {kpi.icon}
            </div>
            <div className="text-xl font-bold text-white">{kpi.value}</div>
            <div className="text-white/40 text-xs mt-0.5">{kpi.label}</div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">

        {/* Pending Booking Requests */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Briefcase size={15} className="text-pink-400" />
              <h3 className="font-semibold text-white text-sm">
                {lang === "ar" ? "طلبات الحجز الواردة" : "Incoming Booking Requests"}
              </h3>
              {pendingBookings.length > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-xs bg-pink-500 text-white font-bold">
                  {pendingBookings.length}
                </span>
              )}
            </div>
          </div>
          <div className="space-y-2">
            {pendingBookings.map((req) => (
              <div key={req.id} className="p-3 rounded-xl bg-pink-500/5 border border-pink-500/15">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-pink-400 text-xs font-semibold truncate mb-0.5">
                      {lang === "ar"
                        ? req.merchant_business_name_ar ?? req.merchant_business_name ?? "تاجر"
                        : req.merchant_business_name ?? "Merchant"}
                    </div>
                    <div className="text-white/80 text-xs font-medium truncate">
                      {req.campaign_goal ?? (lang === "ar" ? "طلب حجز" : "Booking Request")}
                    </div>
                    <div className="text-white/40 text-xs mt-0.5">
                      {req.budget_jod ? fmtJOD(req.budget_jod) : "—"} · {req.timeline_days ? `${req.timeline_days}d` : "—"}
                    </div>
                  </div>
                  <StatusBadge status={req.status} />
                </div>
                <div className="flex gap-2">
                  <Button size="sm" className="h-7 text-xs bg-emerald-600 hover:bg-emerald-500 text-white flex-1"
                    onClick={() => handleAccept(req.id)}>
                    {lang === "ar" ? "قبول" : "Accept"}
                  </Button>
                  <Button size="sm" variant="ghost" className="h-7 text-xs text-red-400 hover:text-red-300 flex-1"
                    onClick={() => handleDecline(req.id)}>
                    {lang === "ar" ? "رفض" : "Decline"}
                  </Button>
                </div>
              </div>
            ))}
            {pendingBookings.length === 0 && recentBookings.length === 0 && (
              <div className="text-center py-8">
                <Briefcase size={24} className="mx-auto mb-2 text-white/15" />
                <div className="text-white/30 text-xs">
                  {lang === "ar" ? "لا توجد طلبات حجز" : "No booking requests yet"}
                </div>
              </div>
            )}
            {recentBookings.length > 0 && (
              <>
                {pendingBookings.length > 0 && <div className="border-t border-white/5 pt-2" />}
                <div className="text-[10px] uppercase tracking-wider text-white/20 px-1 pb-1">
                  {lang === "ar" ? "السابقة" : "History"}
                </div>
                {recentBookings.map((req) => (
                  <div key={req.id} className="p-3 rounded-xl bg-white/3 border border-white/5 opacity-70">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="text-white/50 text-xs font-semibold truncate mb-0.5">
                          {lang === "ar"
                            ? req.merchant_business_name_ar ?? req.merchant_business_name ?? "تاجر"
                            : req.merchant_business_name ?? "Merchant"}
                        </div>
                        <div className="text-white/40 text-xs truncate">
                          {req.campaign_goal ?? (lang === "ar" ? "طلب حجز" : "Booking Request")}
                        </div>
                      </div>
                      <StatusBadge status={req.status} />
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        {/* Active Engagements */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock size={15} className="text-violet-400" />
              <h3 className="font-semibold text-white text-sm">
                {lang === "ar" ? "المشاركات النشطة" : "Active Engagements"}
              </h3>
            </div>
          </div>
          <div className="space-y-2">
            {activeEngagements.map((eng) => (
              <Link key={eng.id} href={`/content-creator/engagements/${eng.id}`}>
                <div className="flex items-center justify-between gap-3 p-3 rounded-xl bg-white/4 border border-white/5 hover:bg-white/8 transition cursor-pointer">
                  <div className="flex-1 min-w-0">
                    <div className="text-white/80 text-xs font-medium truncate">
                      {eng.merchant_business_name
                        ? (lang === "ar" ? eng.merchant_business_name ?? eng.merchant_business_name : eng.merchant_business_name)
                        : `${lang === "ar" ? "مشاركة" : "Engagement"} #${eng.id.slice(0, 6)}`}
                    </div>
                    <div className="text-emerald-400 text-xs mt-0.5">{fmtJOD(eng.agreed_fee_jod)}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={eng.status} />
                    <span className="text-xs text-pink-400 font-medium">
                      {eng.status === "active"
                        ? lang === "ar" ? "أرسل الفكرة ←" : "Submit Idea →"
                        : lang === "ar" ? "عرض" : "View →"}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
            {activeEngagements.length === 0 && (
              <div className="text-center py-8">
                <Clock size={24} className="mx-auto mb-2 text-white/15" />
                <div className="text-white/30 text-xs">
                  {lang === "ar" ? "لا توجد مشاركات نشطة" : "No active engagements"}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Portfolio */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <LayoutGrid size={15} className="text-blue-400" />
            <h3 className="font-semibold text-white text-sm">
              {lang === "ar" ? "معرض أعمالي" : "My Portfolio"}
            </h3>
          </div>
          <Link href="/content-creator/portfolio/new">
            <Button size="sm" className="h-7 text-xs bg-pink-600 hover:bg-pink-500 text-white gap-1">
              <Plus size={11} />
              {lang === "ar" ? "إضافة" : "Add New"}
            </Button>
          </Link>
        </div>
        {portfolio.length === 0 ? (
          <div className="text-center py-8">
            <LayoutGrid size={24} className="mx-auto mb-2 text-white/15" />
            <div className="text-white/30 text-xs mb-3">
              {lang === "ar" ? "لم تنشر أي عناصر بعد" : "No portfolio items yet"}
            </div>
            <Link href="/content-creator/portfolio/new">
              <Button size="sm" className="bg-pink-600 hover:bg-pink-500 text-white text-xs h-7">
                {lang === "ar" ? "أضف أول عنصر" : "Add First Item"}
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {portfolio.map((item) => (
              <div key={item.id} className="p-3 rounded-xl bg-white/4 border border-white/5">
                <div className="font-medium text-white text-xs truncate mb-1">
                  {lang === "ar" ? item.title_ar ?? item.title : item.title}
                </div>
                <div className="text-white/40 text-xs mb-3 truncate">
                  {item.campaign_type ?? "—"} · {item.platforms?.join(", ") ?? "—"}
                </div>
                <div className="flex gap-2">
                  <Link href={`/content-creator/portfolio/${item.id}/edit`} className="flex-1">
                    <Button size="sm" variant="ghost" className="h-6 text-xs w-full">
                      {lang === "ar" ? "تعديل" : "Edit"}
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
