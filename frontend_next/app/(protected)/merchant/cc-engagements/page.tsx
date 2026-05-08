"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import {
  getMyCCEngagements,
  approveIdeaBrief,
  completeCCEngagement,
  rateCCCreator,
  createCampaign,
} from "@/lib/api";
import { CCEngagement } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import {
  CheckCircle2,
  Clock,
  Trophy,
  Lightbulb,
  Star,
  ExternalLink,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

export default function MerchantCCEngagementsPage() {
  const { lang } = useApp();
  const ar = lang === "ar";

  const [engagements, setEngagements] = useState<CCEngagement[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<CCEngagement | null>(null);

  // Campaign creation state
  const [creatingCampaign, setCreatingCampaign] = useState(false);
  const [campaignTitle, setCampaignTitle] = useState("");
  const [campaignBudget, setCampaignBudget] = useState(100);

  // Rating state
  const [rating, setRating] = useState(5);
  const [feedback, setFeedback] = useState("");

  async function load() {
    try {
      const r = await getMyCCEngagements();
      setEngagements(Array.isArray(r.data) ? r.data : []);
    } catch {
      toast.error(ar ? "فشل التحميل" : "Failed to load engagements");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleApprove(id: string) {
    try {
      const r = await approveIdeaBrief(id);
      setSelected(r.data);
      toast.success(ar ? "تم الموافقة!" : "Idea approved!");
      load();
    } catch {
      toast.error(ar ? "فشل الموافقة" : "Approval failed");
    }
  }

  async function handleComplete(id: string) {
    try {
      await completeCCEngagement(id);
      toast.success(ar ? "تم إكمال المشاركة!" : "Engagement completed!");
      setSelected(null);
      load();
    } catch {
      toast.error(ar ? "فشل الإكمال" : "Completion failed");
    }
  }

  async function handleRate(id: string) {
    try {
      await rateCCCreator(id, { creator_rating: rating, merchant_feedback: feedback });
      toast.success(ar ? "تم التقييم!" : "Rated successfully!");
      setFeedback("");
      setSelected(null);
      load();
    } catch {
      toast.error(ar ? "فشل التقييم" : "Rating failed");
    }
  }

  async function handleCreateCampaign(eng: CCEngagement) {
    if (!campaignTitle.trim()) {
      toast.error(ar ? "أدخل عنوان الحملة" : "Campaign title required");
      return;
    }
    setCreatingCampaign(true);
    try {
      const r = await createCampaign({
        title: campaignTitle,
        total_budget_jod: campaignBudget,
        description: eng.idea_brief ?? "",
        cc_engagement_id: eng.id,
      });
      toast.success(ar ? "تم إنشاء الحملة!" : "Campaign created!");
      setCreatingCampaign(false);
      setCampaignTitle("");
      load();
      window.location.href = `/campaigns/${r.data.id}`;
    } catch {
      toast.error(ar ? "فشل إنشاء الحملة" : "Campaign creation failed");
      setCreatingCampaign(false);
    }
  }

  if (loading) {
    return <div className="p-8 text-white/40">{ar ? "جاري التحميل..." : "Loading..."}</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">
        {ar ? "مشاركات منشئي المحتوى" : "Content Creator Engagements"}
      </h1>

      {engagements.length === 0 ? (
        <div className="text-white/40 text-sm">
          {ar ? "لا توجد مشاركات بعد." : "No engagements yet."}
        </div>
      ) : (
        <div className="grid gap-3">
          {engagements.map((eng) => (
            <button
              key={eng.id}
              onClick={() => setSelected(selected?.id === eng.id ? null : eng)}
              className="glass-card p-4 text-left w-full hover:border-white/20 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    eng.status === "completed" ? "bg-emerald-500" :
                    eng.status === "idea_approved" ? "bg-blue-500" :
                    eng.status === "idea_submitted" ? "bg-amber-500" :
                    "bg-pink-500"
                  }`} />
                  <div>
                    <div className="text-white text-sm font-medium">
                      {eng.creator_display_name ?? `#${eng.id.slice(0, 8)}`}
                    </div>
                    <div className="text-white/40 text-xs">
                      {eng.status.replace(/_/g, " ")} · {fmtJOD(eng.agreed_fee_jod)}
                    </div>
                  </div>
                </div>
                {eng.status === "idea_submitted" && (
                  <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 text-xs rounded-full">
                    {ar ? "فكرة بانتظار المراجعة" : "Idea Pending Review"}
                  </span>
                )}
                {eng.campaign_id && (
                  <Link
                    href={`/campaigns/${eng.campaign_id}`}
                    onClick={(e) => e.stopPropagation()}
                    className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300"
                  >
                    <ExternalLink size={12} />
                    {ar ? "الحملة" : "Campaign"}
                  </Link>
                )}
              </div>

              {/* Expanded detail */}
              {selected?.id === eng.id && (
                <div className="mt-4 space-y-4 border-t border-white/10 pt-4" onClick={(e) => e.stopPropagation()}>

                  {/* Idea brief (participant only — will show null for non-participants from API) */}
                  {eng.idea_brief && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Lightbulb size={14} className="text-amber-400" />
                        <span className="text-xs font-semibold text-amber-300">
                          {ar ? "الفكرة المقترحة (سرية)" : "Proposed Idea (Private)"}
                        </span>
                      </div>
                      <div className="text-white/80 text-sm bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 leading-relaxed">
                        {ar && eng.idea_brief_ar ? eng.idea_brief_ar : eng.idea_brief}
                      </div>
                    </div>
                  )}

                  {/* Actions by status */}
                  {eng.status === "idea_submitted" && (
                    <Button
                      onClick={() => handleApprove(eng.id)}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-sm"
                    >
                      <CheckCircle2 size={14} className="mr-2" />
                      {ar ? "الموافقة على الفكرة" : "Approve Idea"}
                    </Button>
                  )}

                  {eng.status === "idea_approved" && !eng.campaign_id && (
                    <div className="space-y-3 bg-violet-500/5 border border-violet-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-2">
                        <Sparkles size={14} className="text-violet-400" />
                        <span className="text-sm font-semibold text-violet-300">
                          {ar ? "إنشاء حملة من هذه الفكرة" : "Create Campaign from This Idea"}
                        </span>
                      </div>
                      <div>
                        <label className="text-white/50 text-xs block mb-1">
                          {ar ? "عنوان الحملة" : "Campaign Title"}
                        </label>
                        <input
                          value={campaignTitle}
                          onChange={(e) => setCampaignTitle(e.target.value)}
                          placeholder={ar ? "اسم الحملة..." : "Campaign name..."}
                          className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-violet-500"
                        />
                      </div>
                      <div>
                        <label className="text-white/50 text-xs block mb-1">
                          {ar ? "الميزانية الإجمالية (JOD)" : "Total Budget (JOD)"}
                        </label>
                        <input
                          type="number"
                          value={campaignBudget}
                          onChange={(e) => setCampaignBudget(Number(e.target.value))}
                          min={50}
                          className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-violet-500"
                        />
                      </div>
                      <Button
                        onClick={() => handleCreateCampaign(eng)}
                        disabled={creatingCampaign || !campaignTitle.trim()}
                        className="bg-violet-600 hover:bg-violet-500 text-white text-sm w-full"
                      >
                        <Sparkles size={14} className="mr-2" />
                        {creatingCampaign
                          ? ar ? "جاري الإنشاء..." : "Creating..."
                          : ar ? "إنشاء الحملة" : "Create Campaign"}
                      </Button>
                    </div>
                  )}

                  {eng.status === "idea_approved" && (
                    <Button
                      onClick={() => handleComplete(eng.id)}
                      variant="outline"
                      className="text-sm"
                    >
                      <Trophy size={14} className="mr-2" />
                      {ar ? "تمييز كمكتمل" : "Mark as Completed"}
                    </Button>
                  )}

                  {eng.status === "completed" && !eng.creator_rating && (
                    <div className="space-y-3">
                      <div className="text-xs font-semibold text-white/60">
                        {ar ? "قيّم منشئ المحتوى" : "Rate the Content Creator"}
                      </div>
                      <div className="flex gap-2">
                        {[1, 2, 3, 4, 5].map((n) => (
                          <button key={n} onClick={() => setRating(n)}>
                            <Star
                              size={20}
                              className={n <= rating ? "text-amber-400 fill-amber-400" : "text-white/20"}
                            />
                          </button>
                        ))}
                      </div>
                      <textarea
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder={ar ? "ملاحظاتك (اختياري)" : "Feedback (optional)"}
                        className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[60px] resize-none focus:outline-none focus:border-amber-500"
                      />
                      <Button
                        onClick={() => handleRate(eng.id)}
                        className="bg-amber-600 hover:bg-amber-500 text-white text-sm"
                      >
                        <Star size={14} className="mr-2" />
                        {ar ? "إرسال التقييم" : "Submit Rating"}
                      </Button>
                    </div>
                  )}

                  {eng.creator_rating && (
                    <div className="flex items-center gap-2 text-sm">
                      <Star size={14} className="text-amber-400 fill-amber-400" />
                      <span className="text-amber-400 font-semibold">{eng.creator_rating}/5</span>
                      <span className="text-white/40 text-xs">{ar ? "تقييمك" : "Your rating"}</span>
                    </div>
                  )}
                </div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
