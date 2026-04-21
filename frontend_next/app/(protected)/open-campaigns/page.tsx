"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getCampaigns } from "@/lib/api";
import { Campaign } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { Calendar, Tag } from "lucide-react";

export default function OpenCampaignsPage() {
  const { lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ niche: "", city: "" });

  useEffect(() => {
    loadCampaigns();
  }, []);

  async function loadCampaigns() {
    setLoading(true);
    try {
      const r = await getCampaigns({ status: "ACTIVE" });
      setCampaigns(Array.isArray(r.data) ? r.data : (r.data?.data ?? []));
    } catch {
      toast.error("Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  }

  const filtered = campaigns.filter((c) => {
    const n = filters.niche.toLowerCase();
    const matchNiche = !n || (c.niche?.toLowerCase().includes(n) ?? false);
    return matchNiche;
  });

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="influencer-banner">
        <h1 className="text-2xl font-bold text-white">
          📢 {lang === "ar" ? "الحملات المتاحة" : "Open Campaigns for You"}
        </h1>
        <p className="text-white/50 text-sm mt-1">
          {lang === "ar" ? "تصفح وتقدم للحملات المناسبة" : "Browse and apply for suitable campaigns"}
        </p>
      </div>

      {/* Filters */}
      <div className="aria-card">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "التخصص" : "Niche"}</Label>
            <Input
              value={filters.niche}
              onChange={(e) => setFilters((f) => ({ ...f, niche: e.target.value }))}
              placeholder="fashion, tech..."
            />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
            <Input
              value={filters.city}
              onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value }))}
              placeholder="Amman..."
            />
          </div>
        </div>
      </div>

      {/* Campaign grid */}
      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {filtered.map((c) => (
            <div key={c.id} className="glass-card p-5 hover:border-violet-500/20 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white text-sm">
                    {lang === "ar" ? c.title_ar : c.title_en}
                  </h3>
                  <div className="flex items-center gap-3 mt-1">
                    {c.niche && (
                      <span className="flex items-center gap-1 text-violet-400 text-xs">
                        <Tag size={11} /> {c.niche}
                      </span>
                    )}
                    {c.end_date && (
                      <span className="flex items-center gap-1 text-white/40 text-xs">
                        <Calendar size={11} /> {c.end_date}
                      </span>
                    )}
                  </div>
                </div>
                <span className={statusClass(c.status)}>{c.status}</span>
              </div>

              <p className="text-white/50 text-xs mb-3 line-clamp-2">
                {lang === "ar" ? c.description_ar : c.description_en}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-amber-400 font-semibold text-sm">
                  {fmtJOD(c.budget_per_influencer ?? 0)} / influencer
                </span>
                <Button size="sm">
                  {lang === "ar" ? "تقديم" : "Apply"}
                </Button>
              </div>
            </div>
          ))}
          {filtered.length === 0 && !loading && (
            <div className="col-span-2 text-center text-white/30 text-sm py-10">
              {lang === "ar" ? "لا توجد حملات متاحة." : "No open campaigns available."}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
