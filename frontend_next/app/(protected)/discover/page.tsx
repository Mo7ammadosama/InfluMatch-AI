"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { InfluencerCard } from "@/components/influencer-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { getInfluencers, smartSearch } from "@/lib/api";
import { InfluencerProfile } from "@/lib/types";
import { toast } from "sonner";
import { Search } from "lucide-react";

export default function DiscoverPage() {
  const { lang } = useApp();
  const router = useRouter();
  const [influencers, setInfluencers] = useState<InfluencerProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({ niche: "", city: "", max_budget: "", tier: "" });

  useEffect(() => { loadInfluencers(); }, []);

  async function loadInfluencers() {
    setLoading(true);
    try {
      const r = await getInfluencers({ limit: 20 });
      // /influencers/ returns {data: [...], total, ...}
      setInfluencers(r.data?.data ?? r.data ?? []);
    } catch {
      toast.error("Failed to load influencers");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch() {
    if (!query.trim() && !filters.niche && !filters.city && !filters.tier) {
      await loadInfluencers();
      return;
    }
    setLoading(true);
    try {
      const payload: Record<string, unknown> = { brief: query || "any" };
      if (filters.niche) payload.niche = filters.niche;
      if (filters.city) payload.city = filters.city;
      if (filters.max_budget) payload.max_budget = parseFloat(filters.max_budget);
      if (filters.tier) payload.tier = filters.tier;
      const r = await smartSearch(payload);
      // smart-search returns {results: [...], total, brief}
      setInfluencers(r.data?.results ?? r.data?.data ?? r.data ?? []);
    } catch {
      toast.error("Search failed");
    } finally {
      setLoading(false);
    }
  }

  function handleBook(influencer: InfluencerProfile) {
    sessionStorage.setItem("booking_influencer", JSON.stringify(influencer));
    router.push("/bookings/new");
  }

  return (
    <div className="space-y-6 max-w-7xl">
      <div>
        <h1 className="text-2xl font-bold text-white">{lang === "ar" ? "🔍 اكتشف المؤثرين" : "🔍 Discover Influencers"}</h1>
        <p className="text-white/40 text-sm mt-1">
          {lang === "ar" ? "ابحث بالذكاء الاصطناعي عن المؤثرين المناسبين" : "AI-powered search for the right influencers"}
        </p>
      </div>

      <div className="aria-card">
        <div className="flex gap-3 mb-4">
          <div className="flex-1">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder={lang === "ar" ? "صف حملتك... مثل: مؤثر أزياء في عمّان" : "Describe your campaign..."}
              className="h-11 text-base"
            />
          </div>
          <Button onClick={handleSearch} disabled={loading} className="h-11 px-6 gap-2">
            <Search size={16} />
            {lang === "ar" ? "بحث" : "Search"}
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "التخصص" : "Niche"}</Label>
            <Input value={filters.niche} onChange={(e) => setFilters((f) => ({ ...f, niche: e.target.value }))} placeholder="fashion..." />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
            <Input value={filters.city} onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value }))} placeholder="Amman..." />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "أقصى ميزانية (JOD)" : "Max Budget (JOD)"}</Label>
            <Input type="number" value={filters.max_budget} onChange={(e) => setFilters((f) => ({ ...f, max_budget: e.target.value }))} placeholder="500" />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "المستوى" : "Tier"}</Label>
            <Select value={filters.tier} onValueChange={(v) => setFilters((f) => ({ ...f, tier: v === "ALL" ? "" : v }))}>
              <SelectTrigger><SelectValue placeholder={lang === "ar" ? "الكل" : "All tiers"} /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">{lang === "ar" ? "الكل" : "All"}</SelectItem>
                <SelectItem value="PLATINUM">🏆 PLATINUM</SelectItem>
                <SelectItem value="GOLD">🥇 GOLD</SelectItem>
                <SelectItem value="SILVER">🥈 SILVER</SelectItem>
                <SelectItem value="BRONZE">🥉 BRONZE</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-40">
          <div className="text-white/40 text-sm">{lang === "ar" ? "جار البحث..." : "Searching..."}</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {influencers.map((inf) => (
            <InfluencerCard key={inf.id} influencer={inf} lang={lang} onBook={handleBook} />
          ))}
          {influencers.length === 0 && (
            <div className="col-span-3 text-center text-white/30 text-sm py-12 space-y-3">
              <div>{lang === "ar" ? "لا نتائج. حاول بحثاً مختلفاً." : "No results. Try a different search."}</div>
              <button
                onClick={loadInfluencers}
                className="text-violet-400 hover:text-violet-300 text-xs underline underline-offset-2"
              >
                {lang === "ar" ? "إعادة المحاولة" : "Retry"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
