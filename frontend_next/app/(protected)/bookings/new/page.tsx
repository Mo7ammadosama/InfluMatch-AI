"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { BookingTimeline } from "@/components/booking-timeline";
import { createBooking, getCampaigns } from "@/lib/api";
import { InfluencerProfile, Campaign } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";

const DELIVERABLES = ["Reel", "Story", "TikTok", "Post", "YouTube Short"];

export default function NewBookingPage() {
  const router = useRouter();
  const { lang } = useApp();
  const [influencer, setInfluencer] = useState<InfluencerProfile | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [form, setForm] = useState({
    brief: "",
    agreed_rate_jod: "",
    deadline: "",
    deliverables: [] as string[],
    campaign_id: "",
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("booking_influencer");
    if (raw) {
      const inf = JSON.parse(raw) as InfluencerProfile;
      setInfluencer(inf);
      setForm((f) => ({ ...f, agreed_rate_jod: String(inf.rate_per_post_jod ?? "") }));
    } else {
      router.replace("/discover");
    }
    getCampaigns().then((r) => setCampaigns(r.data?.data ?? r.data ?? [])).catch(() => {});
  }, [router]);

  function toggleDeliverable(d: string) {
    setForm((f) => ({
      ...f,
      deliverables: f.deliverables.includes(d)
        ? f.deliverables.filter((x) => x !== d)
        : [...f.deliverables, d],
    }));
  }

  async function handleBook(e: React.FormEvent) {
    e.preventDefault();
    if (!influencer) return;
    setLoading(true);
    try {
      await createBooking({
        influencer_id: influencer.id,
        agreed_rate_jod: parseFloat(form.agreed_rate_jod),
        brief: form.brief,
        deadline: form.deadline,
        deliverables: form.deliverables,
        campaign_id: form.campaign_id ? parseInt(form.campaign_id) : undefined,
      });
      sessionStorage.removeItem("booking_influencer");
      toast.success(lang === "ar" ? "تم الحجز وتجميد المبلغ!" : "Booking created & funds locked!");
      router.push("/bookings");
    } catch {
      toast.error(lang === "ar" ? "فشل الحجز" : "Booking failed");
    } finally {
      setLoading(false);
    }
  }

  if (!influencer) return null;

  return (
    <div className="max-w-3xl space-y-6">
      <div className="merchant-banner">
        <h1 className="text-xl font-bold text-white">
          💳 {lang === "ar" ? "تأكيد الحجز" : "Confirm Booking"}
        </h1>
        <p className="text-white/50 text-sm mt-1">
          {influencer.display_name} • {fmtJOD(influencer.rate_per_post_jod ?? 0)} / post
        </p>
      </div>

      {/* Booking lifecycle visual */}
      <div className="aria-card">
        <h3 className="font-semibold text-white mb-3 text-sm">
          {lang === "ar" ? "دورة حياة الحجز" : "Booking Lifecycle"}
        </h3>
        <BookingTimeline currentStatus="PENDING" lang={lang} />
      </div>

      {/* Form */}
      <div className="aria-card">
        <form onSubmit={handleBook} className="space-y-5">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الموجز / Brief" : "Campaign Brief"}</Label>
            <Textarea
              value={form.brief}
              onChange={(e) => setForm((f) => ({ ...f, brief: e.target.value }))}
              placeholder={lang === "ar" ? "اشرح متطلبات الحملة..." : "Describe campaign requirements..."}
              rows={4}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "السعر المتفق عليه (JOD)" : "Agreed Rate (JOD)"}</Label>
              <Input
                type="number"
                value={form.agreed_rate_jod}
                onChange={(e) => setForm((f) => ({ ...f, agreed_rate_jod: e.target.value }))}
                placeholder="100"
                required
                min={1}
              />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "الموعد النهائي" : "Deadline"}</Label>
              <Input
                type="date"
                value={form.deadline}
                onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))}
                required
              />
            </div>
          </div>

          {/* Deliverables */}
          <div className="space-y-2">
            <Label>{lang === "ar" ? "المخرجات المطلوبة" : "Deliverables"}</Label>
            <div className="flex flex-wrap gap-2">
              {DELIVERABLES.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => toggleDeliverable(d)}
                  className={`px-3 py-1.5 rounded-lg text-sm border transition-all ${
                    form.deliverables.includes(d)
                      ? "bg-violet-600 border-violet-500 text-white"
                      : "border-white/10 text-white/50 hover:border-white/20"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Campaign association */}
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "ربط بحملة (اختياري)" : "Link to Campaign (optional)"}</Label>
            <select
              value={form.campaign_id}
              onChange={(e) => setForm((f) => ({ ...f, campaign_id: e.target.value }))}
              className="flex h-9 w-full items-center rounded-lg border border-white/10 bg-bg-overlay px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-violet-500"
            >
              <option value="">{lang === "ar" ? "— بدون حملة —" : "— No Campaign —"}</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>
                  {lang === "ar" ? c.title_ar ?? c.title : c.title}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3">
            <Button type="submit" variant="merchant" disabled={loading} className="flex-1">
              {loading
                ? lang === "ar" ? "جار الحجز..." : "Booking..."
                : lang === "ar" ? "💳 تأكيد الحجز وتجميد المبلغ" : "💳 Confirm & Lock Funds"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push("/discover")}
            >
              {lang === "ar" ? "إلغاء" : "Cancel"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
