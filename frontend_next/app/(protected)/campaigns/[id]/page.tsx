"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { getCampaign, getCreator } from "@/lib/api";
import { Campaign, ContentCreatorSummary } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import { Tag, Calendar, Users, Star, ExternalLink, Sparkles } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { lang } = useApp();
  const ar = lang === "ar";

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [creator, setCreator] = useState<ContentCreatorSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const r = await getCampaign(id);
        const c: Campaign = r.data;
        setCampaign(c);

        // If campaign has a linked CC engagement, load the engagement then creator
        if (c.cc_engagement_id) {
          try {
            const { getCCEngagement } = await import("@/lib/api");
            const engR = await getCCEngagement(c.cc_engagement_id);
            const eng = engR.data;
            if (eng?.content_creator_id) {
              const { getCreator } = await import("@/lib/api");
              const crR = await getCreator(eng.content_creator_id);
              setCreator(crR.data);
            }
          } catch {
            // engagement may not be accessible from all roles — skip silently
          }
        }
      } catch {
        toast.error(ar ? "فشل تحميل الحملة" : "Failed to load campaign");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) return <div className="p-8 text-white/40">{ar ? "جاري التحميل..." : "Loading..."}</div>;
  if (!campaign) return <div className="p-8 text-red-400">{ar ? "الحملة غير موجودة" : "Campaign not found"}</div>;

  const statusColors: Record<string, string> = {
    draft: "bg-white/10 text-white/60",
    active: "bg-emerald-500/20 text-emerald-400",
    in_progress: "bg-blue-500/20 text-blue-400",
    completed: "bg-violet-500/20 text-violet-400",
    cancelled: "bg-red-500/20 text-red-400",
    paused: "bg-amber-500/20 text-amber-400",
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 py-8 px-4">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3 flex-wrap">
          <h1 className="text-2xl font-bold text-white">
            {ar && campaign.title_ar ? campaign.title_ar : campaign.title}
          </h1>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[campaign.status] ?? "bg-white/10"}`}>
            {campaign.status}
          </span>
        </div>
        {campaign.description && (
          <p className="text-white/60 text-sm leading-relaxed">
            {ar && (campaign as Campaign & { description_ar?: string }).description_ar
              ? (campaign as Campaign & { description_ar?: string }).description_ar
              : campaign.description}
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <StatCard label={ar ? "الميزانية" : "Budget"} value={fmtJOD(campaign.total_budget_jod)} />
        <StatCard label={ar ? "المنصف" : "Spent"} value={fmtJOD(campaign.spent_budget_jod ?? 0)} />
        <StatCard label={ar ? "المؤثرون" : "Influencers"} value={String(campaign.max_influencers ?? 1)} />
        {campaign.start_date && <StatCard label={ar ? "يبدأ" : "Starts"} value={campaign.start_date} />}
        {campaign.end_date && <StatCard label={ar ? "ينتهي" : "Ends"} value={campaign.end_date} />}
        {campaign.min_followers != null && (
          <StatCard label={ar ? "حد المتابعين" : "Min Followers"} value={campaign.min_followers.toLocaleString()} />
        )}
      </div>

      {/* Platforms & Categories */}
      {(campaign.required_platforms?.length || campaign.target_categories?.length) ? (
        <div className="bg-bg-overlay border border-white/10 rounded-xl p-4 space-y-3">
          {campaign.required_platforms?.length ? (
            <div>
              <p className="text-xs text-white/40 mb-1.5">{ar ? "المنصات" : "Platforms"}</p>
              <div className="flex flex-wrap gap-1.5">
                {campaign.required_platforms.map((p) => (
                  <span key={p} className="px-2 py-0.5 bg-violet-500/15 text-violet-300 text-xs rounded-full">{p}</span>
                ))}
              </div>
            </div>
          ) : null}
          {campaign.target_categories?.length ? (
            <div>
              <p className="text-xs text-white/40 mb-1.5">{ar ? "الفئات" : "Categories"}</p>
              <div className="flex flex-wrap gap-1.5">
                {campaign.target_categories.map((c) => (
                  <span key={c} className="px-2 py-0.5 bg-pink-500/15 text-pink-300 text-xs rounded-full">{c}</span>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}

      {/* Linked Content Creator */}
      {campaign.cc_engagement_id && (
        <div className="bg-gradient-to-r from-pink-600/10 to-rose-600/10 border border-pink-500/20 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles size={16} className="text-pink-400" />
            <h3 className="text-sm font-semibold text-pink-300">
              {ar ? "منشئ المحتوى المرتبط" : "Linked Content Creator"}
            </h3>
          </div>
          {creator ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-pink-600/30 flex items-center justify-center text-lg">
                {creator.display_name?.charAt(0) ?? "C"}
              </div>
              <div className="flex-1">
                <p className="text-white font-medium text-sm">{creator.display_name}</p>
                {creator.city && <p className="text-white/40 text-xs">{creator.city}</p>}
              </div>
              <Link href={`/discover/creators/${creator.id}`}>
                <Button variant="outline" size="sm" className="text-xs h-7">
                  <ExternalLink size={12} className="mr-1" />
                  {ar ? "عرض الملف" : "View Profile"}
                </Button>
              </Link>
            </div>
          ) : (
            <p className="text-white/50 text-xs">
              {ar
                ? "هذه الحملة مرتبطة بمنشئ محتوى. يمكن للمشاركين مباشرة رؤية التفاصيل."
                : "This campaign is linked to a content creator. Participants can view the full details."}
            </p>
          )}
        </div>
      )}

      {/* AI Brief */}
      {campaign.ai_brief_summary && (
        <div className="bg-bg-overlay border border-white/10 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-violet-400" />
            <span className="text-xs font-semibold text-violet-300">{ar ? "ملخص الذكاء الاصطناعي" : "AI Summary"}</span>
          </div>
          <p className="text-white/70 text-sm leading-relaxed">{campaign.ai_brief_summary}</p>
        </div>
      )}

      {/* Back */}
      <Link href="/campaigns">
        <Button variant="outline" size="sm" className="text-xs">
          {ar ? "رجوع للحملات" : "Back to Campaigns"}
        </Button>
      </Link>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-bg-overlay border border-white/10 rounded-lg p-3">
      <p className="text-white/40 text-xs mb-1">{label}</p>
      <p className="text-white font-semibold text-sm">{value}</p>
    </div>
  );
}
