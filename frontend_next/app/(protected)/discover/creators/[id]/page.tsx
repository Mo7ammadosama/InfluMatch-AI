"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getCreator, listPortfolioItems, sendBookingRequest } from "@/lib/api";
import { ContentCreatorProfile, PortfolioItem } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import { Star, MapPin, CheckCircle2, Globe, LayoutGrid, X } from "lucide-react";

export default function CreatorPublicProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { user, lang } = useApp();
  const [creator, setCreator] = useState<ContentCreatorProfile | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [preSelectedItemId, setPreSelectedItemId] = useState<string | undefined>();
  const [submitting, setSubmitting] = useState(false);
  const [bookingForm, setBookingForm] = useState({
    business_description: "",
    campaign_goal: "",
    target_audience: "",
    budget_jod: "",
    timeline_days: "",
    merchant_notes: "",
    portfolio_item_id: "",
  });

  useEffect(() => {
    Promise.allSettled([
      getCreator(id),
      listPortfolioItems({ limit: 50 }),
    ]).then(([creatorResult, portfolioResult]) => {
      if (creatorResult.status === "fulfilled") {
        setCreator(creatorResult.value.data);
      }
      if (portfolioResult.status === "fulfilled") {
        const items = (Array.isArray(portfolioResult.value.data) ? portfolioResult.value.data : []) as PortfolioItem[];
        setPortfolio(items.filter((i) => i.content_creator_id === id));
      }
    }).finally(() => setLoading(false));
  }, [id]);

  function openBookingModal(portfolioItemId?: string) {
    setPreSelectedItemId(portfolioItemId);
    setBookingForm((f) => ({ ...f, portfolio_item_id: portfolioItemId ?? "" }));
    setShowModal(true);
  }

  async function handleSendBooking(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await sendBookingRequest({
        content_creator_id: id,
        portfolio_item_id: bookingForm.portfolio_item_id || undefined,
        business_description: bookingForm.business_description || undefined,
        campaign_goal: bookingForm.campaign_goal || undefined,
        target_audience: bookingForm.target_audience || undefined,
        budget_jod: bookingForm.budget_jod ? parseFloat(bookingForm.budget_jod) : undefined,
        timeline_days: bookingForm.timeline_days ? parseInt(bookingForm.timeline_days) : undefined,
        merchant_notes: bookingForm.merchant_notes || undefined,
      });
      toast.success(lang === "ar" ? "تم إرسال طلب الحجز!" : "Booking request sent!");
      setShowModal(false);
    } catch {
      toast.error(lang === "ar" ? "فشل إرسال الطلب" : "Failed to send request");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="text-white/40 text-sm">Loading...</div></div>;
  }

  if (!creator) {
    return <div className="text-white/40 text-sm">Creator not found</div>;
  }

  const isMerchant = user?.role === "merchant";
  const displayName = lang === "ar" ? creator.display_name_ar ?? creator.display_name : creator.display_name;
  const bio = lang === "ar" ? creator.bio_ar ?? creator.bio : creator.bio;

  return (
    <div className="space-y-6 max-w-4xl">

      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-start gap-4">
          <div className="w-20 h-20 rounded-2xl bg-pink-500/20 flex items-center justify-center text-pink-400 font-bold text-3xl shrink-0">
            {creator.avatar_url && creator.avatar_url !== ""
              ? <img src={creator.avatar_url} alt="" className="w-full h-full rounded-2xl object-cover" />
              : displayName.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold text-white">{displayName}</h1>
              {creator.is_verified && <CheckCircle2 size={18} className="text-emerald-400" />}
              <span className={`px-2 py-0.5 rounded-full text-xs ${creator.is_available ? "bg-emerald-500/15 text-emerald-400" : "bg-white/5 text-white/30"}`}>
                {creator.is_available ? (lang === "ar" ? "متاح" : "Available") : (lang === "ar" ? "غير متاح" : "Unavailable")}
              </span>
            </div>
            <div className="flex items-center gap-4 mt-2 text-sm text-white/50">
              {creator.city && <span className="flex items-center gap-1"><MapPin size={12} />{creator.city}</span>}
              <span className="flex items-center gap-1"><Star size={12} className="text-amber-400" />{creator.avg_rating?.toFixed(1) ?? "—"}</span>
              <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-emerald-400" />{creator.completed_engagements} {lang === "ar" ? "مشاركة" : "engagements"}</span>
            </div>
            {bio && <p className="text-white/60 text-sm mt-3 leading-relaxed">{bio}</p>}
          </div>
          {isMerchant && creator.is_available && (
            <Button onClick={() => openBookingModal()} className="bg-pink-600 hover:bg-pink-500 text-white shrink-0">
              {lang === "ar" ? "إرسال طلب حجز" : "Send Booking Request"}
            </Button>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {creator.specializations?.map((s) => (
            <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-pink-500/10 text-pink-400 border border-pink-500/20">{s}</span>
          ))}
          {creator.content_categories?.map((c) => (
            <span key={c} className="px-2 py-0.5 rounded-full text-xs bg-violet-500/10 text-violet-400 border border-violet-500/20">{c}</span>
          ))}
          {creator.languages?.map((l) => (
            <span key={l} className="px-2 py-0.5 rounded-full text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20">{l}</span>
          ))}
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm">
          {creator.consultation_rate_jod > 0 && (
            <div>
              <span className="text-white/40 text-xs">{lang === "ar" ? "السعر" : "Rate"} </span>
              <span className="text-emerald-400 font-semibold">{fmtJOD(creator.consultation_rate_jod)}</span>
            </div>
          )}
          {creator.portfolio_url && (
            <a href={creator.portfolio_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1 text-pink-400 hover:text-pink-300 text-xs">
              <Globe size={12} />
              {lang === "ar" ? "الموقع / المعرض" : "Portfolio Site"}
            </a>
          )}
        </div>
      </div>

      {/* Portfolio */}
      {portfolio.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <LayoutGrid size={16} className="text-blue-400" />
            {lang === "ar" ? "معرض الأعمال" : "Portfolio"}
          </h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {portfolio.map((item) => (
              <div key={item.id} className="glass-card p-4 space-y-3">
                <div>
                  <div className="font-semibold text-white text-sm">
                    {lang === "ar" ? item.title_ar ?? item.title : item.title}
                  </div>
                  {item.campaign_type && (
                    <span className="text-xs text-pink-400">{item.campaign_type}</span>
                  )}
                </div>

                {(item.description || item.description_ar) && (
                  <p className="text-white/50 text-xs leading-relaxed">
                    {lang === "ar" ? item.description_ar ?? item.description : item.description}
                  </p>
                )}

                {(item.example_concept || item.example_concept_ar) && (
                  <div className="rounded-lg bg-amber-500/5 border border-amber-500/15 p-3">
                    <div className="text-amber-400 text-xs font-medium mb-1">
                      {lang === "ar" ? "مثال مبدئي" : "Example Concept"}
                    </div>
                    <div className="text-white/60 text-xs leading-relaxed">
                      {lang === "ar" ? item.example_concept_ar ?? item.example_concept : item.example_concept}
                    </div>
                  </div>
                )}

                <div className="flex flex-wrap gap-1">
                  {item.platforms?.map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded-full text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20">{p}</span>
                  ))}
                  {item.content_formats?.map((f) => (
                    <span key={f} className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-white/40 border border-white/10">{f}</span>
                  ))}
                </div>

                {isMerchant && creator.is_available && (
                  <button
                    onClick={() => openBookingModal(item.id)}
                    className="w-full py-1.5 rounded-lg bg-pink-600/20 hover:bg-pink-600/40 text-pink-400 text-xs font-medium transition border border-pink-500/20">
                    {lang === "ar" ? "احجز بناءً على هذا العنصر" : "Book Based on This"}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="glass-card w-full max-w-lg p-6 space-y-4 max-h-[90vh] overflow-y-auto relative">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-white">{lang === "ar" ? "إرسال طلب حجز" : "Send Booking Request"}</h3>
              <button onClick={() => setShowModal(false)} className="text-white/40 hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleSendBooking} className="space-y-4">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "وصف نشاطك التجاري" : "Business Description"}</Label>
                <textarea
                  value={bookingForm.business_description}
                  onChange={(e) => setBookingForm((f) => ({ ...f, business_description: e.target.value }))}
                  className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
                  placeholder={lang === "ar" ? "صف نشاطك وما تحتاجه..." : "Describe your business and what you need..."}
                />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "هدف الحملة" : "Campaign Goal"}</Label>
                <Input value={bookingForm.campaign_goal} onChange={(e) => setBookingForm((f) => ({ ...f, campaign_goal: e.target.value }))}
                  placeholder={lang === "ar" ? "زيادة المبيعات، الوعي بالعلامة..." : "Increase sales, brand awareness..."} />
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الجمهور المستهدف" : "Target Audience"}</Label>
                <Input value={bookingForm.target_audience} onChange={(e) => setBookingForm((f) => ({ ...f, target_audience: e.target.value }))}
                  placeholder={lang === "ar" ? "الشباب 18-25، الأمهات..." : "Young adults 18-25, mothers..."} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "الميزانية (JOD) - اختياري" : "Budget (JOD) — optional"}</Label>
                  <Input type="number" value={bookingForm.budget_jod}
                    onChange={(e) => setBookingForm((f) => ({ ...f, budget_jod: e.target.value }))} placeholder="100" />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "المدة (أيام) - اختياري" : "Timeline (days) — optional"}</Label>
                  <Input type="number" value={bookingForm.timeline_days}
                    onChange={(e) => setBookingForm((f) => ({ ...f, timeline_days: e.target.value }))} placeholder="14" />
                </div>
              </div>
              {portfolio.length > 0 && (
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "عنصر المعرض (اختياري)" : "Portfolio Item (optional)"}</Label>
                  <select
                    value={bookingForm.portfolio_item_id}
                    onChange={(e) => setBookingForm((f) => ({ ...f, portfolio_item_id: e.target.value }))}
                    className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-pink-500"
                  >
                    <option value="">{lang === "ar" ? "بدون تحديد" : "None"}</option>
                    {portfolio.map((item) => (
                      <option key={item.id} value={item.id}>
                        {lang === "ar" ? item.title_ar ?? item.title : item.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "ملاحظات إضافية (اختياري)" : "Additional Notes (optional)"}</Label>
                <textarea
                  value={bookingForm.merchant_notes}
                  onChange={(e) => setBookingForm((f) => ({ ...f, merchant_notes: e.target.value }))}
                  className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[60px] resize-none focus:outline-none focus:border-pink-500"
                />
              </div>
              <div className="flex gap-3">
                <Button type="button" variant="ghost" onClick={() => setShowModal(false)} className="flex-1">
                  {lang === "ar" ? "إلغاء" : "Cancel"}
                </Button>
                <Button type="submit" disabled={submitting} className="flex-1 bg-pink-600 hover:bg-pink-500 text-white">
                  {submitting ? "..." : lang === "ar" ? "إرسال" : "Send Request"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
