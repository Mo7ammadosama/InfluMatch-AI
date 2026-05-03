"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { getCCEngagement, submitIdeaBrief } from "@/lib/api";
import { CCEngagement } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import { CheckCircle2, Clock, Lightbulb, Trophy } from "lucide-react";

const STEPS = ["active", "idea_submitted", "idea_approved", "completed"] as const;
const STEP_LABELS: Record<string, { en: string; ar: string }> = {
  active: { en: "Active", ar: "نشطة" },
  idea_submitted: { en: "Idea Submitted", ar: "الفكرة مُرسلة" },
  idea_approved: { en: "Idea Approved", ar: "الفكرة موافق عليها" },
  completed: { en: "Completed", ar: "مكتملة" },
};

export default function CreatorEngagementPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useApp();
  const [eng, setEng] = useState<CCEngagement | null>(null);
  const [loading, setLoading] = useState(true);
  const [idea, setIdea] = useState("");
  const [ideaAr, setIdeaAr] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    getCCEngagement(id)
      .then((r) => setEng(r.data))
      .catch(() => toast.error("Failed to load engagement"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmitIdea(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const r = await submitIdeaBrief(id, { idea_brief: idea, idea_brief_ar: ideaAr });
      setEng(r.data);
      toast.success(lang === "ar" ? "تم إرسال الفكرة!" : "Idea submitted!");
    } catch {
      toast.error(lang === "ar" ? "فشل الإرسال" : "Submit failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="text-white/40 text-sm">Loading...</div></div>;
  }

  if (!eng) {
    return <div className="text-white/40 text-sm">Engagement not found</div>;
  }

  const currentStep = STEPS.indexOf(eng.status as typeof STEPS[number]);

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-bold text-white">
        {lang === "ar" ? "تفاصيل المشاركة" : "Engagement Detail"}
      </h1>

      {/* Step indicator */}
      <div className="glass-card p-5">
        <div className="flex items-center gap-0">
          {STEPS.map((step, idx) => {
            const done = idx < currentStep;
            const active = idx === currentStep;
            return (
              <div key={step} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 text-xs font-bold transition-all
                    ${done ? "bg-emerald-600 border-emerald-500 text-white" : active ? "bg-pink-600 border-pink-500 text-white" : "bg-white/5 border-white/10 text-white/30"}`}>
                    {done ? <CheckCircle2 size={14} /> : idx + 1}
                  </div>
                  <div className={`text-xs mt-1 text-center leading-tight ${active ? "text-pink-400 font-medium" : done ? "text-emerald-400" : "text-white/30"}`}>
                    {lang === "ar" ? STEP_LABELS[step].ar : STEP_LABELS[step].en}
                  </div>
                </div>
                {idx < STEPS.length - 1 && (
                  <div className={`flex-1 h-0.5 mx-1 mb-5 ${idx < currentStep ? "bg-emerald-600" : "bg-white/10"}`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Merchant brief */}
      <div className="glass-card p-5 space-y-3">
        <h3 className="font-semibold text-white text-sm flex items-center gap-2">
          <Briefcase size={15} className="text-violet-400" />
          {lang === "ar" ? "ملخص التاجر" : "Merchant Brief"}
        </h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="text-white/40 text-xs">{lang === "ar" ? "الأجر المتفق عليه" : "Agreed Fee"}</div>
            <div className="text-emerald-400 font-semibold">{fmtJOD(eng.agreed_fee_jod)}</div>
          </div>
          <div>
            <div className="text-white/40 text-xs">{lang === "ar" ? "الحالة" : "Status"}</div>
            <div className="text-pink-400 font-medium">{eng.status.replace("_", " ")}</div>
          </div>
        </div>
        {eng.merchant_feedback && (
          <div>
            <div className="text-white/40 text-xs mb-1">{lang === "ar" ? "ملاحظات التاجر" : "Merchant Feedback"}</div>
            <div className="text-white/70 text-sm bg-white/4 rounded-lg p-3">{eng.merchant_feedback}</div>
          </div>
        )}
        {eng.creator_rating && (
          <div className="flex items-center gap-2">
            <Trophy size={14} className="text-amber-400" />
            <span className="text-amber-400 text-sm font-semibold">{eng.creator_rating}/5</span>
            <span className="text-white/40 text-xs">{lang === "ar" ? "تقييمك" : "Your Rating"}</span>
          </div>
        )}
      </div>

      {/* Status-specific actions */}
      {eng.status === "active" && (
        <div className="glass-card p-5 space-y-4">
          <h3 className="font-semibold text-white text-sm flex items-center gap-2">
            <Lightbulb size={15} className="text-amber-400" />
            {lang === "ar" ? "أرسل فكرتك المخصصة (خاصة بالتاجر فقط)" : "Submit Your Private Tailored Idea"}
          </h3>
          <div className="text-white/40 text-xs bg-amber-500/5 border border-amber-500/20 rounded-lg p-3">
            {lang === "ar"
              ? "⚠️ فكرتك ستكون خاصة — يراها التاجر وأنت فقط. لا تُشاركها مع أي طرف ثالث."
              : "⚠️ Your idea is private — only you and the merchant can read it. It is never exposed publicly."}
          </div>
          <form onSubmit={handleSubmitIdea} className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-white/60 text-xs">Idea Brief (EN)</label>
              <textarea
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
                required
                placeholder="Your tailored campaign idea for this specific merchant..."
                className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[100px] resize-none focus:outline-none focus:border-pink-500"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-white/60 text-xs">{lang === "ar" ? "الفكرة (AR)" : "Idea Brief (AR)"}</label>
              <textarea
                value={ideaAr}
                onChange={(e) => setIdeaAr(e.target.value)}
                dir="rtl"
                className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
              />
            </div>
            <Button type="submit" disabled={submitting || !idea.trim()} className="w-full bg-pink-600 hover:bg-pink-500 text-white">
              {submitting ? "..." : lang === "ar" ? "إرسال الفكرة" : "Submit Idea"}
            </Button>
          </form>
        </div>
      )}

      {eng.status === "idea_submitted" && (
        <div className="glass-card p-5 text-center">
          <Clock size={32} className="mx-auto mb-3 text-amber-400" />
          <div className="font-semibold text-white text-sm mb-1">
            {lang === "ar" ? "بانتظار موافقة التاجر" : "Waiting for Merchant Approval"}
          </div>
          <div className="text-white/40 text-xs">
            {lang === "ar" ? "سيتم إشعارك عند مراجعة التاجر لفكرتك" : "You will be notified when the merchant reviews your idea"}
          </div>
          {eng.idea_brief && (
            <div className="mt-4 text-left">
              <div className="text-white/40 text-xs mb-1">{lang === "ar" ? "فكرتك المُرسلة" : "Your Submitted Idea"}</div>
              <div className="text-white/70 text-sm bg-white/4 rounded-lg p-3 text-left">{lang === "ar" ? eng.idea_brief_ar ?? eng.idea_brief : eng.idea_brief}</div>
            </div>
          )}
        </div>
      )}

      {eng.status === "idea_approved" && (
        <div className="glass-card p-5 text-center">
          <CheckCircle2 size={32} className="mx-auto mb-3 text-emerald-400" />
          <div className="font-semibold text-white text-sm mb-1">
            {lang === "ar" ? "تم الموافقة على فكرتك!" : "Your Idea was Approved!"}
          </div>
          <div className="text-white/40 text-xs">
            {lang === "ar" ? "التاجر بصدد إنشاء الحملة" : "The merchant is creating the campaign"}
          </div>
          {eng.campaign_id && (
            <Link href={`/campaigns/${eng.campaign_id}`} className="inline-block mt-3">
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white">
                {lang === "ar" ? "عرض الحملة" : "View Campaign"}
              </Button>
            </Link>
          )}
        </div>
      )}

      {eng.status === "completed" && (
        <div className="glass-card p-5 text-center">
          <Trophy size={32} className="mx-auto mb-3 text-amber-400" />
          <div className="font-semibold text-white text-sm mb-1">
            {lang === "ar" ? "مشاركة مكتملة!" : "Engagement Completed!"}
          </div>
          <div className="text-emerald-400 font-bold text-lg mt-2">{fmtJOD(eng.agreed_fee_jod * eng.platform_share_percent / 100)}</div>
          <div className="text-white/40 text-xs">{lang === "ar" ? "تم إضافتها لمحفظتك" : "Added to your wallet"}</div>
        </div>
      )}
    </div>
  );
}

function Briefcase({ size, className }: { size: number; className: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className={className}>
      <rect width="20" height="14" x="2" y="7" rx="2" ry="2" />
      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
    </svg>
  );
}
