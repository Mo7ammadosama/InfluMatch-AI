"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/components/layout/providers";
import { Input } from "@/components/ui/input";
import { listCreators } from "@/lib/api";
import { ContentCreatorSummary } from "@/lib/types";
import { Star, MapPin, CheckCircle2 } from "lucide-react";

function fmtSpec(s: string) {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function DiscoverCreatorsPage() {
  const { lang } = useApp();
  const [creators, setCreators] = useState<ContentCreatorSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ city: "", specialization: "", category: "", is_available: "" });

  function load() {
    const params: Record<string, string> = {};
    if (filters.city) params.city = filters.city;
    if (filters.specialization) params.specialization = filters.specialization;
    if (filters.category) params.category = filters.category;
    if (filters.is_available) params.is_available = filters.is_available;

    setLoading(true);
    listCreators(params)
      .then((r) => setCreators(Array.isArray(r.data) ? r.data : []))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold text-white">
          {lang === "ar" ? "اكتشف منشئي المحتوى" : "Discover Content Creators"}
        </h1>
        <p className="text-white/40 text-sm mt-1">
          {lang === "ar"
            ? "منشئو محتوى في مرحلة النمو — إبداع حقيقي بتكلفة معقولة"
            : "Early-stage content creators — authentic creativity at accessible rates"}
        </p>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Input
            placeholder={lang === "ar" ? "المدينة" : "City"}
            value={filters.city}
            onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value }))}
          />
          <Input
            placeholder={lang === "ar" ? "التخصص" : "Specialization"}
            value={filters.specialization}
            onChange={(e) => setFilters((f) => ({ ...f, specialization: e.target.value }))}
          />
          <Input
            placeholder={lang === "ar" ? "الفئة" : "Category"}
            value={filters.category}
            onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
          />
          <select
            value={filters.is_available}
            onChange={(e) => setFilters((f) => ({ ...f, is_available: e.target.value }))}
            className="rounded-md bg-white/5 border border-white/10 text-white text-sm px-3 py-2 focus:outline-none focus:border-pink-500"
          >
            <option value="">{lang === "ar" ? "كل الحالات" : "All Status"}</option>
            <option value="true">{lang === "ar" ? "متاح الآن" : "Available"}</option>
            <option value="false">{lang === "ar" ? "غير متاح" : "Unavailable"}</option>
          </select>
        </div>
        <button
          onClick={load}
          className="mt-3 px-4 py-2 rounded-lg bg-pink-600 hover:bg-pink-500 text-white text-sm font-medium transition"
        >
          {lang === "ar" ? "بحث" : "Search"}
        </button>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="text-center py-12 text-white/40 text-sm">
          {lang === "ar" ? "جار التحميل..." : "Loading..."}
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {creators.map((creator) => (
            <div key={creator.id} className="glass-card p-5 flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 font-bold text-lg shrink-0">
                  {creator.avatar_url && creator.avatar_url !== ""
                    ? <img src={creator.avatar_url} alt="" className="w-full h-full rounded-full object-cover" />
                    : (lang === "ar" ? creator.display_name_ar ?? creator.display_name : creator.display_name).charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-white text-sm truncate">
                    {lang === "ar" ? creator.display_name_ar ?? creator.display_name : creator.display_name}
                  </div>
                  {creator.city && (
                    <div className="flex items-center gap-1 text-white/40 text-xs mt-0.5">
                      <MapPin size={10} />
                      {creator.city}
                    </div>
                  )}
                </div>
                <div className={`w-2 h-2 rounded-full shrink-0 ${creator.is_available ? "bg-emerald-400" : "bg-white/20"}`} />
              </div>

              {creator.specializations?.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {creator.specializations.slice(0, 3).map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-pink-500/10 text-pink-400 border border-pink-500/20">{fmtSpec(s)}</span>
                  ))}
                </div>
              )}

              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-amber-400">
                  <Star size={11} />
                  <span>{creator.avg_rating?.toFixed(1) ?? "—"}</span>
                </div>
                <div className="flex items-center gap-1 text-white/40">
                  <CheckCircle2 size={11} />
                  <span>{creator.completed_engagements} {lang === "ar" ? "مشاركة" : "engagements"}</span>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs ${creator.is_available ? "bg-emerald-500/15 text-emerald-400" : "bg-white/5 text-white/30"}`}>
                  {creator.is_available ? (lang === "ar" ? "متاح" : "Available") : (lang === "ar" ? "مشغول" : "Busy")}
                </span>
              </div>

              <Link href={`/discover/creators/${creator.id}`} className="block">
                <button className="w-full py-2 rounded-lg bg-pink-600/20 hover:bg-pink-600/40 text-pink-400 text-xs font-medium transition border border-pink-500/20">
                  {lang === "ar" ? "عرض الملف الشخصي" : "View Profile"}
                </button>
              </Link>
            </div>
          ))}

          {creators.length === 0 && (
            <div className="col-span-full text-center py-12 text-white/30 text-sm">
              {lang === "ar" ? "لا يوجد منشئو محتوى مطابقون" : "No creators match your filters"}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
