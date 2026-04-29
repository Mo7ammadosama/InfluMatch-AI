"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { getMyStrategistProfile, getMyIdeas, getMyEngagements } from "@/lib/api";
import { CreativeStrategistProfile, CampaignIdea, CreativeEngagement } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import {
  Plus, Zap, Trophy, Lightbulb, TrendingUp,
  Eye, Users, CheckCircle2, Clock, Settings,
  ArrowRight, Sparkles,
} from "lucide-react";

const MILESTONE_EVERY = 10;

const statusStyles: Record<string, string> = {
  open: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  in_progress: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  completed: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  withdrawn: "bg-white/5 text-white/30 border-white/10",
  pending: "bg-violet-500/15 text-violet-400 border-violet-500/30",
  active: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  cancelled: "bg-red-500/15 text-red-400 border-red-500/30",
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${statusStyles[status] ?? "bg-white/5 text-white/40 border-white/10"}`}>
      {status}
    </span>
  );
}

export default function CreativeStrategistDashboard() {
  const { user, lang } = useApp();
  const [profile, setProfile] = useState<CreativeStrategistProfile | null>(null);
  const [ideas, setIdeas] = useState<CampaignIdea[]>([]);
  const [engagements, setEngagements] = useState<CreativeEngagement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getMyStrategistProfile().catch(() => null),
      getMyIdeas().catch(() => null),
      getMyEngagements().catch(() => null),
    ]).then(([p, i, e]) => {
      if (p) setProfile(p.data);
      if (i) setIdeas(Array.isArray(i.data) ? i.data : []);
      if (e) setEngagements(Array.isArray(e.data) ? e.data : []);
    }).catch(() => toast.error(lang === "ar" ? "فشل تحميل البيانات" : "Failed to load"))
      .finally(() => setLoading(false));
  }, [lang]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <Sparkles size={28} className="text-emerald-400/50 animate-pulse" />
          <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
        </div>
      </div>
    );
  }

  const name = lang === "ar" ? (user?.full_name_ar ?? user?.full_name) : user?.full_name;
  const completedCount = profile?.completed_engagements ?? 0;
  const milestoneProgress = completedCount % MILESTONE_EVERY;
  const milestonePercent = (milestoneProgress / MILESTONE_EVERY) * 100;
  const activeEngagements = engagements.filter((e) => e.status === "active" || e.status === "pending");
  const openIdeas = ideas.filter((i) => i.status === "open");

  return (
    <div className="space-y-6 max-w-6xl">

      {/* ── Hero Banner ── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-900/50 via-teal-900/30 to-bg-surface border border-emerald-700/20 p-6">
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full -translate-y-1/2 translate-x-1/4 blur-3xl pointer-events-none" />
        <div className="relative flex items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">🎨</span>
              <h1 className="text-2xl font-bold text-white">
                {lang === "ar" ? `مرحباً، ${name}` : `Welcome back, ${name}`}
              </h1>
            </div>
            <p className="text-white/50 text-sm">
              {lang === "ar"
                ? "لوحة تحكم المستشار الإبداعي · منصة WaslAI"
                : "Creative Strategist Dashboard · WaslAI Platform"}
            </p>
            {profile?.is_verified && (
              <div className="inline-flex items-center gap-1.5 mt-2 px-2.5 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
                <CheckCircle2 size={11} />
                {lang === "ar" ? "موثّق" : "Verified Strategist"}
              </div>
            )}
          </div>
          <div className="flex flex-col gap-2 shrink-0">
            <Link href="/creative-strategist/ideas/new">
              <Button className="bg-emerald-600 hover:bg-emerald-500 text-white gap-2 w-full">
                <Plus size={15} />
                {lang === "ar" ? "فكرة جديدة" : "New Idea"}
              </Button>
            </Link>
            <Link href="/creative-strategist/profile">
              <Button variant="ghost" size="sm" className="gap-2 text-white/50 hover:text-white w-full justify-center">
                <Settings size={13} />
                {lang === "ar" ? "تعديل الملف" : "Edit Profile"}
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* ── Profile completion prompt ── */}
      {!profile && (
        <div className="flex items-center gap-4 p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
          <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
            <Zap size={18} className="text-emerald-400" />
          </div>
          <div className="flex-1">
            <div className="font-semibold text-emerald-400 text-sm">
              {lang === "ar" ? "أكمل ملفك الشخصي أولاً" : "Set up your Creative Profile"}
            </div>
            <div className="text-white/50 text-xs mt-0.5">
              {lang === "ar"
                ? "أنشئ ملفك لتبدأ في نشر أفكارك والحصول على مشاريع"
                : "Create your profile to publish ideas and get hired by merchants"}
            </div>
          </div>
          <Link href="/settings">
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white shrink-0">
              {lang === "ar" ? "إنشاء الملف" : "Set Up"}
              <ArrowRight size={13} className="ml-1" />
            </Button>
          </Link>
        </div>
      )}

      {/* ── KPI Grid ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          {
            icon: <CheckCircle2 size={18} className="text-emerald-400" />,
            value: completedCount,
            label: lang === "ar" ? "مشاركات مكتملة" : "Completed",
            bg: "bg-emerald-500/10",
          },
          {
            icon: <Trophy size={18} className="text-amber-400" />,
            value: profile?.milestone_count ?? 0,
            label: lang === "ar" ? "معالم محققة" : "Milestones",
            bg: "bg-amber-500/10",
          },
          {
            icon: <TrendingUp size={18} className="text-violet-400" />,
            value: fmtJOD(profile?.total_earned_jod ?? 0),
            label: lang === "ar" ? "إجمالي الأرباح" : "Total Earned",
            bg: "bg-violet-500/10",
          },
          {
            icon: <Lightbulb size={18} className="text-blue-400" />,
            value: ideas.length,
            label: lang === "ar" ? "أفكار منشورة" : "Published Ideas",
            bg: "bg-blue-500/10",
          },
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

      {/* ── Milestone Progress ── */}
      {profile && (
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Trophy size={15} className="text-amber-400" />
              <h3 className="font-semibold text-white text-sm">
                {lang === "ar" ? "التقدم نحو مكافأة الـ20 JOD" : "Progress to 20 JOD Milestone Bonus"}
              </h3>
            </div>
            <span className="text-white/50 text-xs tabular-nums">
              {milestoneProgress} / {MILESTONE_EVERY}
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-white/8 overflow-hidden">
            <div
              className="h-2.5 rounded-full bg-gradient-to-r from-emerald-600 to-emerald-400 transition-all duration-700"
              style={{ width: `${milestonePercent}%` }}
            />
          </div>
          <div className="flex items-center justify-between mt-2">
            <p className="text-white/30 text-xs">
              {lang === "ar"
                ? `${MILESTONE_EVERY - milestoneProgress} مشاركة أخرى لفتح المكافأة`
                : `${MILESTONE_EVERY - milestoneProgress} more engagements to unlock`}
            </p>
            <p className="text-amber-400 text-xs font-medium">
              {lang === "ar" ? `${profile.milestone_count} × 20 JOD مكتسبة` : `${profile.milestone_count} × 20 JOD earned`}
            </p>
          </div>
        </div>
      )}

      {/* ── Bottom Grid: Engagements + Ideas ── */}
      <div className="grid lg:grid-cols-2 gap-6">

        {/* Active Engagements */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock size={15} className="text-violet-400" />
              <h3 className="font-semibold text-white text-sm">
                {lang === "ar" ? "المشاركات النشطة" : "Active Engagements"}
              </h3>
              {activeEngagements.length > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-xs bg-violet-500 text-white font-bold">
                  {activeEngagements.length}
                </span>
              )}
            </div>
          </div>
          <div className="space-y-2">
            {activeEngagements.map((eng) => (
              <div key={eng.id} className="flex items-center justify-between gap-3 p-3 rounded-xl bg-white/4 border border-white/5">
                <div className="flex-1 min-w-0">
                  <div className="text-white/80 text-xs font-medium truncate">
                    {lang === "ar" ? "مشاركة" : "Engagement"} #{eng.id.slice(0, 6)}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-emerald-400 text-xs font-semibold">{fmtJOD(eng.agreed_fee_jod)}</span>
                    {eng.merchant_notes && (
                      <span className="text-white/30 text-xs truncate max-w-[120px]">{eng.merchant_notes}</span>
                    )}
                  </div>
                </div>
                <StatusBadge status={eng.status} />
              </div>
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

        {/* My Ideas */}
        <div className="glass-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Lightbulb size={15} className="text-emerald-400" />
              <h3 className="font-semibold text-white text-sm">
                {lang === "ar" ? "أفكاري" : "My Ideas"}
              </h3>
              {openIdeas.length > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {openIdeas.length} {lang === "ar" ? "مفتوحة" : "open"}
                </span>
              )}
            </div>
            <Link href="/creative-strategist/ideas/new">
              <Button size="sm" variant="ghost" className="h-7 text-emerald-400 hover:text-emerald-300 gap-1 text-xs">
                <Plus size={12} />
                {lang === "ar" ? "جديدة" : "New"}
              </Button>
            </Link>
          </div>
          <div className="space-y-2">
            {ideas.slice(0, 5).map((idea) => (
              <div key={idea.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/4 border border-white/5">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-white text-xs truncate">
                    {lang === "ar" ? idea.title_ar ?? idea.title : idea.title}
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="flex items-center gap-1 text-white/30 text-xs">
                      <Eye size={10} />{idea.view_count}
                    </span>
                    <span className="flex items-center gap-1 text-white/30 text-xs">
                      <Users size={10} />{idea.adoption_count}
                    </span>
                    {idea.business_category && (
                      <span className="text-emerald-400/70 text-xs">{idea.business_category}</span>
                    )}
                  </div>
                </div>
                <StatusBadge status={idea.status} />
              </div>
            ))}
            {ideas.length === 0 && (
              <div className="text-center py-8">
                <Lightbulb size={24} className="mx-auto mb-2 text-white/15" />
                <div className="text-white/30 text-xs mb-3">
                  {lang === "ar" ? "لم تنشر أي أفكار بعد" : "No ideas published yet"}
                </div>
                <Link href="/creative-strategist/ideas/new">
                  <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs h-7">
                    {lang === "ar" ? "انشر فكرتك الأولى" : "Publish Your First Idea"}
                  </Button>
                </Link>
              </div>
            )}
          </div>
          {ideas.length > 5 && (
            <Link href="/creative-strategist/ideas" className="mt-3 flex items-center justify-center gap-1 text-white/40 hover:text-white/70 text-xs transition-colors">
              {lang === "ar" ? `عرض جميع الأفكار (${ideas.length})` : `View all ideas (${ideas.length})`}
              <ArrowRight size={11} />
            </Link>
          )}
        </div>

      </div>
    </div>
  );
}
