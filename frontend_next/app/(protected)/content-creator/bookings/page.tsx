"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { getReceivedBookings, acceptBooking, declineBooking } from "@/lib/api";
import { BookingRequest } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Clock, CheckCircle2, XCircle, Send, Calendar, ExternalLink } from "lucide-react";

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    colorClass: "text-amber-400",
    bgClass: "bg-amber-500/10 border-amber-500/20",
    en: "Pending",
    ar: "قيد الانتظار",
  },
  accepted: {
    icon: CheckCircle2,
    colorClass: "text-emerald-400",
    bgClass: "bg-emerald-500/10 border-emerald-500/20",
    en: "Accepted",
    ar: "مقبول",
  },
  declined: {
    icon: XCircle,
    colorClass: "text-red-400",
    bgClass: "bg-red-500/10 border-red-500/20",
    en: "Declined",
    ar: "مرفوض",
  },
  expired: {
    icon: Clock,
    colorClass: "text-white/30",
    bgClass: "bg-white/5 border-white/10",
    en: "Expired",
    ar: "منتهي",
  },
};

export default function CCBookingsPage() {
  const { lang } = useApp();
  const ar = lang === "ar";
  const [requests, setRequests] = useState<BookingRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);

  async function load() {
    try {
      const r = await getReceivedBookings();
      setRequests(Array.isArray(r.data) ? r.data : []);
    } catch {
      toast.error(ar ? "فشل تحميل الطلبات" : "Failed to load requests");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleAccept(id: string) {
    setActing(id);
    try {
      await acceptBooking(id);
      toast.success(ar ? "تم قبول الطلب!" : "Request accepted!");
      load();
    } catch {
      toast.error(ar ? "فشل قبول الطلب" : "Failed to accept request");
    } finally {
      setActing(null);
    }
  }

  async function handleDecline(id: string) {
    if (!confirm(ar ? "هل أنت متأكد من رفض الطلب؟" : "Decline this request?")) return;
    setActing(id);
    try {
      await declineBooking(id);
      toast.success(ar ? "تم رفض الطلب" : "Request declined");
      load();
    } catch {
      toast.error(ar ? "فشل رفض الطلب" : "Failed to decline request");
    } finally {
      setActing(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{ar ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  const pending = requests.filter((r) => r.status === "pending");
  const accepted = requests.filter((r) => r.status === "accepted");
  const other = requests.filter((r) => r.status !== "pending" && r.status !== "accepted");

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Send size={20} className="text-pink-400" />
          {ar ? "طلبات الحجز الواردة" : "Incoming Booking Requests"}
        </h1>
        <p className="text-white/40 text-sm mt-1">
          {ar ? "طلبات الحجز المرسلة إليك من التجار" : "Booking requests sent to you by merchants"}
        </p>
      </div>

      {requests.length === 0 ? (
        <div className="glass-card p-10 text-center space-y-3">
          <Send size={32} className="text-white/10 mx-auto" />
          <p className="text-white/40 text-sm">
            {ar ? "لا توجد طلبات حجز بعد" : "No booking requests yet"}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
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

          {pending.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-amber-400/70 uppercase tracking-wider">
                {ar ? "قيد الانتظار" : "Pending"}
              </h2>
              {pending.map((req) => (
                <RequestCard key={req.id} req={req} lang={lang} acting={acting} onAccept={handleAccept} onDecline={handleDecline} />
              ))}
            </section>
          )}

          {accepted.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-emerald-400/70 uppercase tracking-wider">
                {ar ? "مقبول" : "Accepted"}
              </h2>
              {accepted.map((req) => (
                <RequestCard key={req.id} req={req} lang={lang} acting={acting} onAccept={handleAccept} onDecline={handleDecline} />
              ))}
            </section>
          )}

          {other.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-xs font-semibold text-white/20 uppercase tracking-wider">
                {ar ? "مرفوض / منتهي" : "Declined / Expired"}
              </h2>
              {other.map((req) => (
                <RequestCard key={req.id} req={req} lang={lang} acting={acting} onAccept={handleAccept} onDecline={handleDecline} />
              ))}
            </section>
          )}
        </div>
      )}
    </div>
  );
}

function RequestCard({
  req,
  lang,
  acting,
  onAccept,
  onDecline,
}: {
  req: BookingRequest;
  lang: string;
  acting: string | null;
  onAccept: (id: string) => void;
  onDecline: (id: string) => void;
}) {
  const ar = lang === "ar";
  const cfg = STATUS_CONFIG[req.status as keyof typeof STATUS_CONFIG] ?? STATUS_CONFIG.pending;
  const StatusIcon = cfg.icon;

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-white text-sm">
            {ar
              ? req.merchant_business_name_ar ?? req.merchant_business_name ?? (ar ? "تاجر" : "Merchant")
              : req.merchant_business_name ?? (ar ? "تاجر" : "Merchant")}
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

      <div className="grid sm:grid-cols-2 gap-3 text-xs">
        {req.campaign_goal && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">{ar ? "هدف الحملة" : "Campaign Goal"}</div>
            <div className="text-white/70">{req.campaign_goal}</div>
          </div>
        )}
        {req.target_audience && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">{ar ? "الجمهور" : "Target Audience"}</div>
            <div className="text-white/70">{req.target_audience}</div>
          </div>
        )}
        {req.budget_jod != null && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">{ar ? "الميزانية" : "Budget"}</div>
            <div className="text-emerald-400 font-semibold">{fmtJOD(req.budget_jod)}</div>
          </div>
        )}
        {req.timeline_days != null && (
          <div className="space-y-0.5">
            <div className="text-white/30 uppercase tracking-wider text-[10px]">{ar ? "المدة" : "Timeline"}</div>
            <div className="text-white/70">{req.timeline_days} {ar ? "يوم" : "days"}</div>
          </div>
        )}
      </div>

      {req.business_description && (
        <div className="rounded-lg bg-white/3 border border-white/8 px-3 py-2.5">
          <div className="text-white/30 uppercase tracking-wider text-[10px] mb-1">{ar ? "وصف النشاط التجاري" : "Business Description"}</div>
          <p className="text-white/60 text-xs leading-relaxed line-clamp-3">{req.business_description}</p>
        </div>
      )}

      {req.merchant_notes && (
        <div className="rounded-lg bg-white/3 border border-white/8 px-3 py-2.5">
          <div className="text-white/30 uppercase tracking-wider text-[10px] mb-1">{ar ? "ملاحظات إضافية" : "Additional Notes"}</div>
          <p className="text-white/60 text-xs leading-relaxed">{req.merchant_notes}</p>
        </div>
      )}

      {req.status === "pending" && (
        <div className="flex gap-2 pt-1">
          <Button
            size="sm"
            variant="success"
            disabled={acting === req.id}
            onClick={() => onAccept(req.id)}
            className="flex-1"
          >
            ✅ {ar ? "قبول" : "Accept"}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            disabled={acting === req.id}
            onClick={() => onDecline(req.id)}
            className="flex-1 text-red-400/60 hover:text-red-400 hover:bg-red-400/10"
          >
            ✕ {ar ? "رفض" : "Decline"}
          </Button>
        </div>
      )}
    </div>
  );
}
