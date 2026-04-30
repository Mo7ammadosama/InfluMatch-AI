"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { BookingTimeline } from "@/components/booking-timeline";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  getMyBookings, confirmBooking, cancelBooking, submitContent, approveContent,
  getBookingMessages, sendMessage,
} from "@/lib/api";
import { Booking, Message } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { Send, ChevronDown, ChevronUp } from "lucide-react";

export default function BookingsPage() {
  const { user, lang } = useApp();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const [msgInput, setMsgInput] = useState("");
  const [contentUrl, setContentUrl] = useState("");

  async function load() {
    const r = await getMyBookings();
    setBookings(r.data?.data ?? r.data ?? []);
  }

  useEffect(() => {
    load().catch(() => toast.error("Failed to load bookings")).finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function loadMessages(bookingId: string) {
    try {
      const r = await getBookingMessages(bookingId as unknown as number);
      setMessages((prev) => ({ ...prev, [bookingId]: r.data ?? [] }));
    } catch {}
  }

  function toggle(id: string) {
    const next = expanded === id ? null : id;
    setExpanded(next);
    if (next) loadMessages(next);
  }

  async function action(fn: () => Promise<unknown>, successMsg: string) {
    try {
      await fn();
      toast.success(successMsg);
      await load();
    } catch {
      toast.error(lang === "ar" ? "فشلت العملية" : "Action failed");
    }
  }

  async function handleSendMsg(bookingId: string) {
    if (!msgInput.trim()) return;
    try {
      await sendMessage({ booking_id: bookingId, content: msgInput });
      setMsgInput("");
      await loadMessages(bookingId);
    } catch {}
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  const bannerClass = user?.role === "merchant" ? "merchant-banner" : "influencer-banner";

  return (
    <div className="space-y-6 max-w-4xl">
      <div className={bannerClass}>
        <h1 className="text-2xl font-bold text-white">📅 {lang === "ar" ? "الحجوزات" : "Bookings"}</h1>
        <p className="text-white/50 text-sm mt-1">{lang === "ar" ? "تتبع دورة حياة حجوزاتك" : "Track your booking lifecycle"}</p>
      </div>

      {bookings.length === 0 && (
        <div className="text-white/30 text-sm text-center py-12">
          {lang === "ar" ? "لا توجد حجوزات بعد." : "No bookings yet."}
        </div>
      )}

      {bookings.map((b) => (
        <div key={b.id} className="glass-card overflow-hidden">
          <button
            className="w-full flex items-center justify-between p-5 hover:bg-white/[0.02] transition-colors"
            onClick={() => toggle(b.id)}
          >
            <div className="flex items-center gap-4">
              <div>
                <div className="font-semibold text-white text-sm">
                  {lang === "ar" ? `حجز #${b.id.slice(0, 8)}` : `Booking #${b.id.slice(0, 8)}`}
                </div>
                <div className="text-white/40 text-xs mt-0.5">
                  {fmtJOD(b.agreed_amount_jod ?? b.agreed_rate_jod ?? 0)} •{" "}
                  {b.deadline ? new Date(b.deadline).toLocaleDateString() : "—"}
                </div>
              </div>
              <span className={statusClass(b.status)}>{b.status}</span>
            </div>
            {expanded === b.id
              ? <ChevronUp size={16} className="text-white/40" />
              : <ChevronDown size={16} className="text-white/40" />}
          </button>

          {expanded === b.id && (
            <div className="px-5 pb-5 space-y-5 border-t border-white/5">
              <BookingTimeline currentStatus={b.status} lang={lang} />

              <div className="flex flex-wrap gap-2">
                {b.status === "proposed" && user?.role === "influencer" && (
                  <Button size="sm" variant="success"
                    onClick={() => action(() => confirmBooking(b.id as unknown as number), lang === "ar" ? "تم التأكيد!" : "Confirmed!")}>
                    ✅ {lang === "ar" ? "تأكيد الحجز" : "Confirm Booking"}
                  </Button>
                )}

                {b.status === "accepted" && user?.role === "influencer" && (
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder={lang === "ar" ? "رابط المحتوى..." : "Content URL..."}
                      value={contentUrl}
                      onChange={(e) => setContentUrl(e.target.value)}
                      className="h-8 text-sm w-60"
                    />
                    <Button size="sm"
                      onClick={() => action(
                        () => submitContent(b.id as unknown as number, { content_url: contentUrl }),
                        lang === "ar" ? "تم الإرسال!" : "Submitted!"
                      )}>
                      {lang === "ar" ? "إرسال المحتوى" : "Submit Content"}
                    </Button>
                  </div>
                )}

                {b.status === "content_submitted" && user?.role === "merchant" && (
                  <Button size="sm" variant="success"
                    onClick={() => action(() => approveContent(b.id as unknown as number), lang === "ar" ? "تمت الموافقة!" : "Approved!")}>
                    ✅ {lang === "ar" ? "موافقة على المحتوى" : "Approve Content"}
                  </Button>
                )}

                {["proposed", "accepted"].includes(b.status) && user?.role === "merchant" && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-red-400/60 hover:text-red-400 hover:bg-red-400/10"
                    onClick={() => {
                      if (!confirm(lang === "ar" ? "إلغاء هذا الحجز؟" : "Cancel this booking?")) return;
                      action(() => cancelBooking(b.id as unknown as number), lang === "ar" ? "تم الإلغاء!" : "Booking cancelled!");
                    }}
                  >
                    ✕ {lang === "ar" ? "إلغاء" : "Cancel"}
                  </Button>
                )}
              </div>

              {b.notes && (
                <div className="text-white/50 text-xs bg-white/4 rounded-lg p-3">
                  <span className="text-white/30">{lang === "ar" ? "الملاحظات: " : "Brief: "}</span>
                  {b.notes}
                </div>
              )}

              <div>
                <Label className="mb-2 block">{lang === "ar" ? "الرسائل" : "Messages"}</Label>
                <div className="bg-bg-overlay rounded-lg p-3 space-y-2 max-h-40 overflow-y-auto mb-2">
                  {(messages[b.id] ?? []).map((m) => (
                    <div key={m.id} className="text-sm">
                      <span className="text-violet-400 text-xs">#{m.sender_id}: </span>
                      <span className="text-white/70">{m.content}</span>
                    </div>
                  ))}
                  {(messages[b.id] ?? []).length === 0 && (
                    <div className="text-white/30 text-xs text-center">{lang === "ar" ? "لا رسائل" : "No messages"}</div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={msgInput}
                    onChange={(e) => setMsgInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMsg(b.id)}
                    placeholder={lang === "ar" ? "اكتب رسالة..." : "Type a message..."}
                    className="h-8 text-sm"
                  />
                  <Button size="icon" className="h-8 w-8" onClick={() => handleSendMsg(b.id)}>
                    <Send size={14} />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
