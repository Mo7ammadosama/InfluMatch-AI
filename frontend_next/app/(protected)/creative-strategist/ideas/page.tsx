"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { listIdeas, engageStrategist, withdrawIdea } from "@/lib/api";
import { CampaignIdea } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import {
  Eye, Users, Plus, Search, SlidersHorizontal,
  Lightbulb, Tag, Calendar, Trash2, ChevronDown,
} from "lucide-react";

const CATEGORIES = ["Fashion", "Food", "Tech", "Beauty", "Fitness", "Travel", "Lifestyle", "Education", "Entertainment"];
const PLATFORMS  = ["Instagram", "TikTok", "YouTube", "X", "Snapchat"];

const statusStyles: Record<string, string> = {
  open:        "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  in_progress: "bg-amber-500/15  text-amber-400  border-amber-500/30",
  completed:   "bg-blue-500/15   text-blue-400   border-blue-500/30",
  withdrawn:   "bg-white/5       text-white/30   border-white/10",
};

export default function IdeasPage() {
  const { user, lang } = useApp();
  const [ideas, setIdeas] = useState<CampaignIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [platform, setPlatform] = useState("");
  const [search, setSearch] = useState("");
  const [engagingId, setEngagingId] = useState<string | null>(null);
  const [withdrawingId, setWithdrawingId] = useState<string | null>(null);
  const [feeInputs, setFeeInputs] = useState<Record<string, string>>({});
  const [hireOpen, setHireOpen] = useState<string | null>(null);

  const isMerchant = user?.role === "merchant";
  const isCS = user?.role === "creative_strategist";

  async function load() {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (category) params.business_category = category;
      if (platform) params.platform = platform;
      const r = await listIdeas(params);
      setIdeas(Array.isArray(r.data) ? r.data : []);
    } catch {
      toast.error(lang === "ar" ? "فشل تحميل الأفكار" : "Failed to load ideas");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [category, platform]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleEngage(idea: CampaignIdea) {
    const fee = parseFloat(feeInputs[idea.id] ?? "0") || 0;
    if (!fee) {
      toast.error(lang === "ar" ? "أدخل الرسوم المتفق عليها" : "Enter agreed fee");
      return;
    }
    setEngagingId(idea.id);
    try {
      await engageStrategist(idea.id, { agreed_fee_jod: fee });
      toast.success(lang === "ar" ? "تم إرسال طلب التعاون!" : "Engagement request sent!");
      setHireOpen(null);
      load();
    } catch {
      toast.error(lang === "ar" ? "فشل الطلب" : "Request failed");
    } finally {
      setEngagingId(null);
    }
  }

  async function handleWithdraw(id: string) {
    if (!confirm(lang === "ar" ? "هل تريد سحب هذه الفكرة؟" : "Withdraw this idea?")) return;
    setWithdrawingId(id);
    try {
      await withdrawIdea(id);
      toast.success(lang === "ar" ? "تم سحب الفكرة" : "Idea withdrawn");
      load();
    } catch {
      toast.error(lang === "ar" ? "فشل السحب" : "Withdraw failed");
    } finally {
      setWithdrawingId(null);
    }
  }

  const filtered = ideas.filter((idea) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return idea.title.toLowerCase().includes(q) || (idea.title_ar ?? "").includes(q) || (idea.description ?? "").toLowerCase().includes(q);
  });

  return (
    <div className="space-y-6 max-w-6xl">

      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Lightbulb size={22} className="text-emerald-400" />
            {lang === "ar" ? "الأفكار الإبداعية" : "Creative Ideas"}
          </h1>
          <p className="text-white/40 text-sm mt-1">
            {isMerchant
              ? lang === "ar" ? "استكشف أفكار المستشارين ووظّف أفضلهم" : "Discover strategist pitches and hire your creative partner"
              : lang === "ar" ? "أفكارك وأفكار المستشارين الآخرين" : "Your ideas and the community feed"}
          </p>
        </div>
        {isCS && (
          <Link href="/creative-strategist/ideas/new">
            <Button className="bg-emerald-600 hover:bg-emerald-500 text-white gap-2 shrink-0">
              <Plus size={15} />
              {lang === "ar" ? "فكرة جديدة" : "New Idea"}
            </Button>
          </Link>
        )}
      </div>

      {/* ── Filters ── */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={lang === "ar" ? "ابحث عن فكرة..." : "Search ideas..."}
              className="pl-9"
            />
          </div>

          <div className="flex items-center gap-2">
            <SlidersHorizontal size={14} className="text-white/30" />
          </div>

          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="rounded-lg bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-emerald-500/50"
          >
            <option value="">{lang === "ar" ? "كل القطاعات" : "All Categories"}</option>
            {CATEGORIES.map((c) => <option key={c} value={c.toLowerCase()}>{c}</option>)}
          </select>

          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="rounded-lg bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-emerald-500/50"
          >
            <option value="">{lang === "ar" ? "كل المنصات" : "All Platforms"}</option>
            {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        <div className="flex items-center gap-1.5 mt-3">
          {["", ...CATEGORIES.slice(0, 6)].map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c.toLowerCase())}
              className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-all ${
                category === c.toLowerCase()
                  ? "bg-emerald-600 border-emerald-500 text-white"
                  : "border-white/10 text-white/40 hover:border-white/20 hover:text-white/60"
              }`}
            >
              {c || (lang === "ar" ? "الكل" : "All")}
            </button>
          ))}
        </div>
      </div>

      {/* ── Ideas Grid ── */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-5 animate-pulse">
              <div className="h-4 bg-white/5 rounded w-3/4 mb-3" />
              <div className="h-3 bg-white/5 rounded w-full mb-1" />
              <div className="h-3 bg-white/5 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16">
          <Lightbulb size={40} className="mx-auto mb-3 text-white/10" />
          <div className="text-white/30 text-sm mb-2">{lang === "ar" ? "لا توجد أفكار مطابقة" : "No matching ideas"}</div>
          {isCS && (
            <Link href="/creative-strategist/ideas/new">
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white mt-2">
                {lang === "ar" ? "كن الأول وانشر فكرة" : "Be first — publish an idea"}
              </Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filtered.map((idea) => (
            <div key={idea.id} className="glass-card p-5 flex flex-col gap-3 hover:border-emerald-500/20 transition-colors">

              {/* Title row */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white text-sm leading-snug">
                    {lang === "ar" ? idea.title_ar ?? idea.title : idea.title}
                  </h3>
                  {idea.business_category && (
                    <div className="flex items-center gap-1 mt-1 text-emerald-400/80 text-xs">
                      <Tag size={10} />
                      {idea.business_category}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${statusStyles[idea.status] ?? "bg-white/5 text-white/40 border-white/10"}`}>
                    {idea.status}
                  </span>
                  {isCS && idea.status !== "withdrawn" && (
                    <button
                      onClick={() => handleWithdraw(idea.id)}
                      disabled={withdrawingId === idea.id}
                      className="text-red-400/40 hover:text-red-400 transition-colors"
                    >
                      <Trash2 size={13} />
                    </button>
                  )}
                </div>
              </div>

              {/* Description */}
              <p className="text-white/50 text-xs leading-relaxed line-clamp-2">
                {lang === "ar" ? idea.description_ar ?? idea.description : idea.description}
              </p>

              {/* Platforms */}
              {idea.suggested_platforms.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {idea.suggested_platforms.map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded-full text-xs bg-emerald-900/40 text-emerald-300 border border-emerald-700/20">
                      {p}
                    </span>
                  ))}
                </div>
              )}

              {/* Meta row */}
              <div className="flex items-center justify-between text-xs text-white/30 border-t border-white/5 pt-2">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1"><Eye size={11} />{idea.view_count}</span>
                  <span className="flex items-center gap-1"><Users size={11} />{idea.adoption_count} {lang === "ar" ? "توظيف" : "hires"}</span>
                  {idea.timeline_days && (
                    <span className="flex items-center gap-1"><Calendar size={11} />{idea.timeline_days}d</span>
                  )}
                </div>
                {idea.estimated_budget_jod && (
                  <span className="text-amber-400 font-semibold">{fmtJOD(idea.estimated_budget_jod)}</span>
                )}
              </div>

              {/* Merchant hire panel */}
              {isMerchant && idea.status === "open" && (
                <div className="border-t border-white/5 pt-3">
                  {hireOpen === idea.id ? (
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        placeholder={lang === "ar" ? "الرسوم المتفق عليها (JOD)" : "Agreed fee (JOD)"}
                        className="flex-1 h-8 text-xs"
                        value={feeInputs[idea.id] ?? ""}
                        onChange={(e) => setFeeInputs((f) => ({ ...f, [idea.id]: e.target.value }))}
                        min={0}
                        autoFocus
                      />
                      <Button
                        size="sm"
                        className="h-8 bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3"
                        disabled={engagingId === idea.id}
                        onClick={() => handleEngage(idea)}
                      >
                        {engagingId === idea.id ? "..." : lang === "ar" ? "إرسال" : "Send"}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-8 text-white/40 text-xs px-2"
                        onClick={() => setHireOpen(null)}
                      >
                        {lang === "ar" ? "إلغاء" : "Cancel"}
                      </Button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setHireOpen(idea.id)}
                      className="w-full flex items-center justify-center gap-1.5 py-2 rounded-lg text-emerald-400 text-xs font-medium border border-emerald-500/20 hover:bg-emerald-500/10 transition-colors"
                    >
                      <Users size={12} />
                      {lang === "ar" ? "توظيف هذا المستشار" : "Hire This Strategist"}
                      <ChevronDown size={12} />
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="text-center text-white/20 text-xs pb-4">
        {filtered.length > 0 && `${filtered.length} ${lang === "ar" ? "فكرة" : "ideas"}`}
      </div>
    </div>
  );
}
