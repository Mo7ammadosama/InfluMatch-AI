"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { getSentBookings } from "@/lib/api";
import { BookingRequest } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import {
  Clock,
  CheckCircle2,
  XCircle,
  Send,
  Calendar,
  ChevronRight,
  ExternalLink,
} from "lucide-react";

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    colorClass: "text-amber-400",
    bgClass: "bg-amber-500/10 border-amber-500/20",
    dotClass: "bg-amber-400",
    en: "Pending",
    ar: "قيد الانتظار",
  },
  accepted: {
    icon: CheckCircle2,
    colorClass: "text-emerald-400",
    bgClass: "bg-emerald-500/10 border-emerald-500/20",
    dotClass: "bg-emerald-400",
    en: "Accepted",
    ar: "مقبول",
  },
  declined: {
    icon: XCircle,
    colorClass: "text-red-400",
    bgClass: "bg-red-500/10 border-red-500/20",
    dotClass: "bg-red-400",
    en: "Declined",
    ar: "مرفوض",
  },
  expired: {
    icon: Clock,
    colorClass: "text-white/30",
    bgClass: "bg-white/5 border-white/10",
    dotClass: "bg-white/20",
    en: "Expired",
    ar: "منتهي",
  },
};

function BookingCard({ req, lang }: { req: BookingRequest; lang: string }) {
  const ar = lang === "ar";
  const cfg = STATUS_CONFIG[req.status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.pending;
  const StatusIcon = cfg.icon;

  return (
    <div className="glass-card p-5 space-y-4">
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-white font-semibold text-sm">
              {ar
                ? req.creator_display_name_ar ?? req.creator_display_name ?? (ar ? "منشئ محتوى" : "Content Creator")
                : req.creator_display_name ?? (ar ? "منشئ محتوى" : "Content Creator")}
            </span>
            <Link
              href={`/discover/creators/${req.content_creator_id}`}
              className="flex items-center gap-1 text-xs text-pink-400 hover:text-pink-300 transition"
            >
              <ExternalLink size={11} />
              {ar ? "عرض الملف" : "View Profile"}
            </Link>
          </div>
          <div className="flex items-center gap-1.5 mt-1 text-white/40 text-xs">
            <Calendar size={11} />
            {new Date(req.created_at).toLocaleDateString(ar ? "ar-JO" : "en-GB", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </div>
        </div>

        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${cfg.bgClass} ${cfg.colorClass} shrink-0`}>
          <StatusIcon size={12} />
          {ar ? cfg.ar : cfg.en}
        </span>
      </div>

      {/* Brief details */}
      <div className="grid sm:grid-cols-2 gap-3 text-xs">
        {req.campaign_goal && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">
              {ar ? "هدف الحملة" : "Campaign Goal"}
            </div>
            <div className="text-white/70">{req.campaign_goal}</div>
          </div>
        )}
        {req.target_audience && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">
              {ar ? "الجمهور المستهدف" : "Target Audience"}
            </div>
            <div className="text-white/70">{req.target_audience}</div>
          </div>
        )}
        {req.budget_jod != null && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">
              {ar ? "الميزانية" : "Budget"}
            </div>
            <div className="text-emerald-400 font-semibold">{fmtJOD(req.budget_jod)}</div>
          </div>
        )}
        {req.timeline_days != null && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">
              {ar ? "المدة" : "Timeline"}
            </div>
            <div className="text-white/70">{req.timeline_days} {ar ? "يوم" : "days"}</div>
          </div>
        )}
      </div>

      {req.business_description && (
        <div className="rounded-lg bg-white/3 border border-white/8 px-3 py-2.5">
          <div className="text-white/30 uppercase tracking-wider text-[10px] mb-1">
            {ar ? "وصف النشاط التجاري" : "Business Description"}
          </div>
          <p className="text-white/60 text-xs leading-relaxed line-clamp-3">
            {req.business_description}
          </p>
        </div>
      )}

      {/* Creator response */}
      {req.creator_response && (
        <div className="rounded-lg bg-pink-500/5 border border-pink-500/15 px-3 py-2.5">
          <div className="text-pink-400 text-[10px] uppercase tracking-wider font-medium mb-1">
            {ar ? "رد منشئ المحتوى" : "Creator's Response"}
          </div>
          <p className="text-white/70 text-xs leading-relaxed">{req.creator_response}</p>
        </div>
      )}

      {/* Accepted → navigate to engagements */}
      {req.status === "accepted" && (
        <Link
          href="/merchant/cc-engagements"
          className="flex items-center justify-between w-full px-3 py-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 transition"
        >
          <span>{ar ? "عرض المشاركة الكاملة" : "View Full Engagement"}</span>
          <ChevronRight size={14} />
        </Link>
      )}
    </div>
  );
}

export default function MerchantCCBookingsPage() {
  const { lang } = useApp();
  const ar = lang === "ar";
  const [bookings, setBookings] = useState<BookingRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSentBookings()
      .then((r) => setBookings(Array.isArray(r.data) ? r.data : []))
      .catch(() => toast.error(ar ? "فشل تحميل الطلبات" : "Failed to load bookings"))
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const pending = bookings.filter((b) => b.status === "pending");
  const accepted = bookings.filter((b) => b.status === "accepted");
  const other = bookings.filter((b) => b.status !== "pending" && b.status !== "accepted");

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Send size={20} className="text-pink-400" />
          {ar ? "طلبات حجز منشئي المحتوى" : "Content Creator Booking Requests"}
        </h1>
        <p className="text-white/40 text-sm mt-1">
          {ar
            ? "تتبع حالة طلباتك المرسلة إلى منشئي المحتوى"
            : "Track the status of your sent requests to content creators"}
        </p>
      </div>

      {loading ? (
        <div className="text-center py-16 text-white/30 text-sm">
          {ar ? "جاري التحميل..." : "Loading..."}
        </div>
      ) : bookings.length === 0 ? (
        <div className="glass-card p-10 text-center space-y-3">
          <Send size={32} className="text-white/10 mx-auto" />
          <p className="text-white/40 text-sm">
            {ar ? "لم ترسل أي طلبات حجز بعد" : "You haven't sent any booking requests yet"}
          </p>
          <Link
            href="/discover/creators"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-pink-600/20 hover:bg-pink-600/40 text-pink-400 text-xs font-medium border border-pink-500/20 transition"
          >
            {ar ? "اكتشف منشئي المحتوى" : "Discover Creators"}
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary pills */}
          <div className="flex flex-wrap gap-2">
            <span className="px-3 py-1 rounded-full text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {pending.length} {ar ? "قيد الانتظار" : "pending"}
            </span>
            <span className="px-3 py-1 rounded-full text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {accepted.length} {ar ? "مقبول" : "accepted"}
            </span>
            {other.length > 0 && (
              <span className="px-3 py-1 rounded-full text-xs bg-white/5 text-white/30 border border-white/10">
                {other.length} {ar ? "أخرى" : "other"}
              </span>
            )}
          </div>

          {/* Pending */}
          {pending.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-amber-400/70 uppercase tracking-wider">
                {ar ? "قيد الانتظار" : "Pending"}
              </h2>
              {pending.map((req) => (
                <BookingCard key={req.id} req={req} lang={lang} />
              ))}
            </section>
          )}

          {/* Accepted */}
          {accepted.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-emerald-400/70 uppercase tracking-wider">
                {ar ? "مقبول" : "Accepted"}
              </h2>
              {accepted.map((req) => (
                <BookingCard key={req.id} req={req} lang={lang} />
              ))}
            </section>
          )}

          {/* Declined / Expired */}
          {other.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-white/20 uppercase tracking-wider">
                {ar ? "مرفوض / منتهي" : "Declined / Expired"}
              </h2>
              {other.map((req) => (
                <BookingCard key={req.id} req={req} lang={lang} />
              ))}
            </section>
          )}
        </div>
      )}
    </div>
  );
}
