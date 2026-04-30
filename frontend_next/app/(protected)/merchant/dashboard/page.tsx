"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { InfluencerCard } from "@/components/influencer-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getCampaigns, getMerchantAnalytics, getMyEscrow, createCampaign, getInfluencers, listIdeas } from "@/lib/api";
import { Campaign, EscrowTransaction, InfluencerProfile, CampaignIdea } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import Link from "next/link";
import { Plus, Users, Lightbulb, ArrowRight, Tag, Eye } from "lucide-react";

interface AnalyticsData {
  total_budget_jod: number;
  total_campaigns: number;
  completed_campaigns: number;
  total_released_jod: number;
  campaigns: { title_en?: string; title_ar?: string; total_budget?: number; status?: string }[];
}

export default function MerchantDashboard() {
  const { user, lang } = useApp();
  const router = useRouter();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [escrow, setEscrow] = useState<EscrowTransaction[]>([]);
  const [topInfluencers, setTopInfluencers] = useState<InfluencerProfile[]>([]);
  const [creativeIdeas, setCreativeIdeas] = useState<CampaignIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const [newCamp, setNewCamp] = useState({
    title: "", title_ar: "", description: "", description_ar: "",
    target_categories: "", total_budget_jod: "", end_date: "",
    max_influencers: "1",
  });

  useEffect(() => {
    Promise.all([
      getCampaigns(),
      getMerchantAnalytics().catch(() => null),
      getMyEscrow().catch(() => null),
      getInfluencers({ limit: 6, available_only: true }),
      listIdeas({ limit: 4 }).catch(() => null),
    ]).then(([c, a, e, inf, ideas]) => {
      setCampaigns(c.data?.data ?? c.data ?? []);
      if (a) setAnalytics(a.data);
      if (e) setEscrow(Array.isArray(e.data) ? e.data : (e.data?.data ?? []));
      setTopInfluencers(Array.isArray(inf.data) ? inf.data : (inf.data?.data ?? []));
      if (ideas) setCreativeIdeas(Array.isArray(ideas.data) ? ideas.data : []);
    })
      .catch(() => toast.error("Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      await createCampaign({
        title: newCamp.title,
        title_ar: newCamp.title_ar || undefined,
        description: newCamp.description || undefined,
        description_ar: newCamp.description_ar || undefined,
        target_categories: newCamp.target_categories
          ? newCamp.target_categories.split(",").map((s) => s.trim())
          : [],
        total_budget_jod: parseFloat(newCamp.total_budget_jod) || 50,
        max_influencers: parseInt(newCamp.max_influencers) || 1,
        end_date: newCamp.end_date || undefined,
      });
      toast.success(lang === "ar" ? "تم إنشاء الحملة!" : "Campaign created!");
      const r = await getCampaigns();
      setCampaigns(r.data?.data ?? r.data ?? []);
    } catch {
      toast.error(lang === "ar" ? "فشل الإنشاء" : "Failed to create campaign");
    } finally {
      setCreating(false);
    }
  }

  function handleBook(influencer: InfluencerProfile) {
    sessionStorage.setItem("booking_influencer", JSON.stringify(influencer));
    router.push("/bookings/new");
  }

  const escrowLocked = escrow
    .filter((e) => ["FUNDED", "IN_PROGRESS"].includes(e.status))
    .reduce((s, e) => s + (e.gross_amount ?? 0), 0);

  const chartData = (analytics?.campaigns ?? []).slice(0, 6).map((c) => ({
    name: (lang === "ar" ? c.title_ar : c.title_en)?.slice(0, 12) ?? "—",
    budget: c.total_budget ?? 0,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  const name = lang === "ar" ? (user?.full_name_ar ?? user?.full_name) : (user?.full_name_en ?? user?.full_name);
  const activeCnt = campaigns.filter((c) => c.status === "active" || c.status === "in_progress").length;

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Banner */}
      <div className="merchant-banner flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            🏪 {lang === "ar" ? `مرحباً، ${name}` : `Welcome, ${name}`}
          </h1>
          <p className="text-white/50 text-sm mt-1">{lang === "ar" ? "لوحة تحكم التاجر" : "Merchant Dashboard"}</p>
        </div>
        <Link href="/discover">
          <Button variant="merchant">{lang === "ar" ? "🔍 اكتشف المؤثرين" : "🔍 Discover Influencers"}</Button>
        </Link>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiBlock label={lang === "ar" ? "إجمالي الميزانية" : "Total Budget"} value={fmtJOD(analytics?.total_budget_jod ?? 0)} accent="amber" />
        <KpiBlock label={lang === "ar" ? "الحملات النشطة" : "Active"} value={activeCnt} accent="green" />
        <KpiBlock label={lang === "ar" ? "المكتملة" : "Completed"} value={analytics?.completed_campaigns ?? 0} accent="blue" />
        <KpiBlock label={lang === "ar" ? "مبالغ محجوزة" : "Escrow Locked"} value={fmtJOD(escrowLocked)} accent="violet" />
      </div>

      {/* ── Available Influencers ── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users size={16} className="text-violet-400" />
            <h2 className="font-semibold text-white text-sm">
              {lang === "ar" ? "المؤثرون المتاحون" : "Available Influencers"}
            </h2>
            <span className="px-1.5 py-0.5 rounded-full text-xs bg-violet-500/20 text-violet-400 border border-violet-500/30">
              {topInfluencers.length}
            </span>
          </div>
          <Link href="/discover">
            <button className="flex items-center gap-1 text-violet-400 hover:text-violet-300 text-xs transition-colors">
              {lang === "ar" ? "عرض الكل" : "View all"}
              <ArrowRight size={12} />
            </button>
          </Link>
        </div>
        {topInfluencers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {topInfluencers.map((inf) => (
              <InfluencerCard key={inf.id} influencer={inf} lang={lang} onBook={handleBook} />
            ))}
          </div>
        ) : (
          <div className="aria-card text-center py-10 text-white/30 text-sm">
            {lang === "ar" ? "لا يوجد مؤثرون متاحون حالياً" : "No influencers available right now"}
          </div>
        )}
      </div>

      {/* ── Creative Ideas ── */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lightbulb size={16} className="text-emerald-400" />
            <h2 className="font-semibold text-white text-sm">
              {lang === "ar" ? "الأفكار الإبداعية" : "Creative Ideas"}
            </h2>
          </div>
          <Link href="/creative-strategist/ideas">
            <button className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 text-xs transition-colors">
              {lang === "ar" ? "تصفح الكل" : "Browse all"}
              <ArrowRight size={12} />
            </button>
          </Link>
        </div>
        {creativeIdeas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {creativeIdeas.map((idea) => (
              <div
                key={idea.id}
                className="aria-card border border-white/5 hover:border-emerald-500/20 transition-colors flex flex-col gap-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-white text-sm leading-snug">
                    {lang === "ar" ? idea.title_ar ?? idea.title : idea.title}
                  </h3>
                  <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shrink-0">
                    {idea.status}
                  </span>
                </div>
                <p className="text-white/50 text-xs leading-relaxed line-clamp-2">
                  {lang === "ar" ? idea.description_ar ?? idea.description : idea.description}
                </p>
                <div className="flex items-center justify-between text-xs text-white/30 pt-1 border-t border-white/5">
                  <div className="flex items-center gap-3">
                    {idea.business_category && (
                      <span className="flex items-center gap-1 text-emerald-400/70">
                        <Tag size={10} />{idea.business_category}
                      </span>
                    )}
                    <span className="flex items-center gap-1"><Eye size={10} />{idea.view_count}</span>
                  </div>
                  {idea.estimated_budget_jod && (
                    <span className="text-amber-400 font-semibold">{fmtJOD(idea.estimated_budget_jod)}</span>
                  )}
                </div>
                <Link href="/creative-strategist/ideas">
                  <Button size="sm" className="w-full h-8 bg-emerald-600/80 hover:bg-emerald-600 text-white text-xs mt-1">
                    {lang === "ar" ? "توظيف المستشار" : "Hire Strategist"}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="aria-card text-center py-8 text-white/30 text-sm border border-emerald-700/10">
            {lang === "ar" ? "لا توجد أفكار منشورة بعد" : "No creative ideas published yet"}
          </div>
        )}
      </div>

      {/* Tabs: Campaigns / Analytics / New Campaign */}
      <Tabs defaultValue="campaigns">
        <TabsList>
          <TabsTrigger value="campaigns">{lang === "ar" ? "الحملات" : "Campaigns"}</TabsTrigger>
          <TabsTrigger value="roi">{lang === "ar" ? "تحليلات" : "Analytics"}</TabsTrigger>
          <TabsTrigger value="new">
            <Plus size={14} className="mr-1" />
            {lang === "ar" ? "حملة جديدة" : "New Campaign"}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="campaigns">
          <div className="space-y-3">
            {campaigns.slice(0, 10).map((c) => (
              <div key={c.id} className="aria-card flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white text-sm truncate">
                    {lang === "ar" ? c.title_ar ?? c.title : c.title}
                  </div>
                  <div className="text-white/40 text-xs mt-0.5">
                    {c.target_categories?.[0] ?? "—"} • {c.end_date ?? "—"}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-amber-400 text-sm font-medium">{fmtJOD(c.total_budget_jod)}</span>
                  <span className={statusClass(c.status)}>{c.status}</span>
                </div>
              </div>
            ))}
            {campaigns.length === 0 && (
              <div className="text-white/30 text-sm text-center py-8">
                {lang === "ar" ? "لا توجد حملات بعد." : "No campaigns yet."}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="roi">
          <div className="aria-card">
            <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "ميزانيات الحملات" : "Campaign Budgets"}</h3>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" tick={{ fill: "#ffffff50", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#ffffff50", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ background: "#17171f", border: "1px solid #ffffff10", borderRadius: 8 }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="budget" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-white/30 text-sm text-center py-8">
                {lang === "ar" ? "لا توجد بيانات." : "No data yet."}
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="new">
          <div className="aria-card max-w-2xl">
            <h3 className="font-semibold text-white mb-5">{lang === "ar" ? "إنشاء حملة جديدة" : "Create New Campaign"}</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>Title (EN)</Label>
                  <Input
                    value={newCamp.title}
                    onChange={(e) => setNewCamp((p) => ({ ...p, title: e.target.value }))}
                    placeholder="Campaign title"
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Title (AR)</Label>
                  <Input
                    value={newCamp.title_ar}
                    onChange={(e) => setNewCamp((p) => ({ ...p, title_ar: e.target.value }))}
                    placeholder="عنوان الحملة"
                    dir="rtl"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الوصف" : "Description"}</Label>
                <Textarea
                  value={newCamp.description}
                  onChange={(e) => setNewCamp((p) => ({ ...p, description: e.target.value }))}
                  placeholder="Campaign brief..."
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "الميزانية الكلية (JOD)" : "Total Budget (JOD)"}</Label>
                  <Input
                    type="number"
                    value={newCamp.total_budget_jod}
                    onChange={(e) => setNewCamp((p) => ({ ...p, total_budget_jod: e.target.value }))}
                    placeholder="500"
                    min={50}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "عدد المؤثرين" : "Max Influencers"}</Label>
                  <Input
                    type="number"
                    value={newCamp.max_influencers}
                    onChange={(e) => setNewCamp((p) => ({ ...p, max_influencers: e.target.value }))}
                    placeholder="1"
                    min={1}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "القطاعات (مفصولة بفاصلة)" : "Categories (comma-separated)"}</Label>
                  <Input
                    value={newCamp.target_categories}
                    onChange={(e) => setNewCamp((p) => ({ ...p, target_categories: e.target.value }))}
                    placeholder="fashion, tech..."
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "تاريخ الانتهاء" : "End Date"}</Label>
                  <Input
                    type="date"
                    value={newCamp.end_date}
                    onChange={(e) => setNewCamp((p) => ({ ...p, end_date: e.target.value }))}
                  />
                </div>
              </div>
              <Button type="submit" variant="merchant" disabled={creating}>
                {creating
                  ? lang === "ar" ? "جار الإنشاء..." : "Creating..."
                  : lang === "ar" ? "إنشاء الحملة" : "Create Campaign"}
              </Button>
            </form>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
