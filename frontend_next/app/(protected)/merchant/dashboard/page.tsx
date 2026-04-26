"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { getCampaigns, getMerchantAnalytics, getMyEscrow, createCampaign } from "@/lib/api";
import { Campaign, EscrowTransaction } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import Link from "next/link";
import { Plus } from "lucide-react";

interface AnalyticsData {
  total_budget_jod: number;
  total_campaigns: number;
  completed_campaigns: number;
  total_released_jod: number;
  campaigns: { title_en?: string; title_ar?: string; total_budget?: number; status?: string }[];
}

export default function MerchantDashboard() {
  const { user, lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [escrow, setEscrow] = useState<EscrowTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const [newCamp, setNewCamp] = useState({
    title_en: "", title_ar: "", description_en: "", description_ar: "",
    niche: "", total_budget: "", budget_per_influencer: "", end_date: "",
  });

  useEffect(() => {
    Promise.all([getCampaigns(), getMerchantAnalytics(), getMyEscrow()])
      .then(([c, a, e]) => {
        // campaigns/ returns {data: [...], total, page, ...}
        setCampaigns(c.data?.data ?? c.data ?? []);
        setAnalytics(a.data);
        // escrow/my returns array directly
        setEscrow(Array.isArray(e.data) ? e.data : (e.data?.data ?? []));
      })
      .catch(() => toast.error("Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      await createCampaign({
        ...newCamp,
        total_budget: parseFloat(newCamp.total_budget) || 0,
        budget_per_influencer: parseFloat(newCamp.budget_per_influencer) || 0,
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

  const name = lang === "ar" ? user?.full_name_ar : user?.full_name_en;
  const activeCnt = campaigns.filter((c) => c.status === "ACTIVE" || c.status === "IN_PROGRESS").length;

  return (
    <div className="space-y-6 max-w-6xl">
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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiBlock label={lang === "ar" ? "الميزانية المنفقة" : "Budget Spent"} value={fmtJOD(analytics?.total_budget_jod)} accent="amber" />
        <KpiBlock label={lang === "ar" ? "الحملات النشطة" : "Active"} value={activeCnt} accent="green" />
        <KpiBlock label={lang === "ar" ? "المكتملة" : "Completed"} value={analytics?.completed_campaigns ?? 0} accent="blue" />
        <KpiBlock label={lang === "ar" ? "مبالغ محجوزة" : "Escrow Locked"} value={fmtJOD(escrowLocked)} accent="violet" />
      </div>

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
                    {lang === "ar" ? c.title_ar : c.title_en}
                  </div>
                  <div className="text-white/40 text-xs mt-0.5">{c.niche} • {c.end_date}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-amber-400 text-sm font-medium">{fmtJOD(c.total_budget)}</span>
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
                  <Tooltip contentStyle={{ background: "#17171f", border: "1px solid #ffffff10", borderRadius: 8 }} labelStyle={{ color: "#fff" }} />
                  <Bar dataKey="budget" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-white/30 text-sm text-center py-8">{lang === "ar" ? "لا توجد بيانات." : "No data yet."}</div>
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
                  <Input value={newCamp.title_en} onChange={(e) => setNewCamp((p) => ({ ...p, title_en: e.target.value }))} placeholder="Campaign title" required />
                </div>
                <div className="space-y-1.5">
                  <Label>Title (AR)</Label>
                  <Input value={newCamp.title_ar} onChange={(e) => setNewCamp((p) => ({ ...p, title_ar: e.target.value }))} placeholder="عنوان الحملة" dir="rtl" />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الوصف" : "Description"}</Label>
                <Textarea value={newCamp.description_en} onChange={(e) => setNewCamp((p) => ({ ...p, description_en: e.target.value }))} placeholder="Campaign brief..." rows={3} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "الميزانية الكلية (JOD)" : "Total Budget (JOD)"}</Label>
                  <Input type="number" value={newCamp.total_budget} onChange={(e) => setNewCamp((p) => ({ ...p, total_budget: e.target.value }))} placeholder="500" min={0} />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "ميزانية المؤثر (JOD)" : "Budget / Influencer (JOD)"}</Label>
                  <Input type="number" value={newCamp.budget_per_influencer} onChange={(e) => setNewCamp((p) => ({ ...p, budget_per_influencer: e.target.value }))} placeholder="100" min={0} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "التخصص" : "Niche"}</Label>
                  <Input value={newCamp.niche} onChange={(e) => setNewCamp((p) => ({ ...p, niche: e.target.value }))} placeholder="fashion, tech..." />
                </div>
                <div className="space-y-1.5">
                  <Label>{lang === "ar" ? "تاريخ الانتهاء" : "End Date"}</Label>
                  <Input type="date" value={newCamp.end_date} onChange={(e) => setNewCamp((p) => ({ ...p, end_date: e.target.value }))} />
                </div>
              </div>
              <Button type="submit" variant="merchant" disabled={creating}>
                {creating ? (lang === "ar" ? "جار الإنشاء..." : "Creating...") : (lang === "ar" ? "إنشاء الحملة" : "Create Campaign")}
              </Button>
            </form>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
