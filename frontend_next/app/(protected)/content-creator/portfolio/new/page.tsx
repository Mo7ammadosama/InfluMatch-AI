"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createPortfolioItem } from "@/lib/api";
import { toast } from "sonner";

const PLATFORM_OPTIONS = ["Instagram", "TikTok", "YouTube", "Snapchat", "X"];
const FORMAT_OPTIONS = ["Reels", "Stories", "Posts", "Live", "Short Video", "Long Video", "Podcast"];
const CATEGORY_OPTIONS = ["Fashion", "Food", "Tech", "Beauty", "Fitness", "Lifestyle", "Travel", "Education", "Gaming", "Business"];
const CAMPAIGN_TYPES = ["Brand Awareness", "Product Launch", "Event Promotion", "Tutorial", "Review", "Challenge", "Behind the Scenes"];

export default function NewPortfolioItemPage() {
  const router = useRouter();
  const { lang } = useApp();
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    title: "",
    title_ar: "",
    description: "",
    description_ar: "",
    campaign_type: "",
    business_categories: [] as string[],
    platforms: [] as string[],
    content_formats: [] as string[],
    example_concept: "",
    example_concept_ar: "",
  });

  function toggleItem(list: string[], item: string): string[] {
    return list.includes(item) ? list.filter((x) => x !== item) : [...list, item];
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await createPortfolioItem(form);
      toast.success(lang === "ar" ? "تم إنشاء العنصر!" : "Portfolio item created!");
      router.push("/content-creator/dashboard");
    } catch {
      toast.error(lang === "ar" ? "فشل الإنشاء" : "Create failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-bold text-white">
        {lang === "ar" ? "إضافة عنصر جديد للمعرض" : "Add Portfolio Item"}
      </h1>

      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-5">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "العنوان (EN)" : "Title (EN)"} *</Label>
            <Input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} required placeholder="My Creative Approach" />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "العنوان (AR)" : "Title (AR)"}</Label>
            <Input value={form.title_ar} onChange={(e) => setForm((f) => ({ ...f, title_ar: e.target.value }))} dir="rtl" placeholder="أسلوبي الإبداعي" />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "الوصف (EN)" : "Description (EN)"}</Label>
          <textarea
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            placeholder="Describe your creative style and approach..."
            className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
          />
        </div>
        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "الوصف (AR)" : "Description (AR)"}</Label>
          <textarea
            value={form.description_ar}
            onChange={(e) => setForm((f) => ({ ...f, description_ar: e.target.value }))}
            dir="rtl"
            className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
          />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "نوع الحملة" : "Campaign Type"}</Label>
          <div className="flex flex-wrap gap-2">
            {CAMPAIGN_TYPES.map((t) => (
              <button key={t} type="button"
                onClick={() => setForm((f) => ({ ...f, campaign_type: f.campaign_type === t ? "" : t }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.campaign_type === t ? "bg-pink-600 border-pink-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "فئات الأعمال" : "Business Categories"}</Label>
          <div className="flex flex-wrap gap-2">
            {CATEGORY_OPTIONS.map((c) => (
              <button key={c} type="button"
                onClick={() => setForm((f) => ({ ...f, business_categories: toggleItem(f.business_categories, c) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.business_categories.includes(c) ? "bg-violet-600 border-violet-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "المنصات" : "Platforms"}</Label>
          <div className="flex flex-wrap gap-2">
            {PLATFORM_OPTIONS.map((p) => (
              <button key={p} type="button"
                onClick={() => setForm((f) => ({ ...f, platforms: toggleItem(f.platforms, p) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.platforms.includes(p) ? "bg-blue-600 border-blue-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "صيغ المحتوى" : "Content Formats"}</Label>
          <div className="flex flex-wrap gap-2">
            {FORMAT_OPTIONS.map((f) => (
              <button key={f} type="button"
                onClick={() => setForm((fm) => ({ ...fm, content_formats: toggleItem(fm.content_formats, f) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.content_formats.includes(f) ? "bg-emerald-600 border-emerald-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Example Concept — clearly labeled as generalized, NOT a tailored campaign idea */}
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 space-y-3">
          <div className="text-amber-400 text-xs font-medium">
            {lang === "ar"
              ? "⚠️ مثال مبدئي عام (ليس فكرة حملة مخصصة — يتم تقديم الأفكار المخصصة بعد قبول طلب الحجز)"
              : "⚠️ Generalized example concept (NOT a tailored campaign idea — tailored ideas are shared privately after booking)"}
          </div>
          <div className="space-y-1.5">
            <Label>Example Concept (EN)</Label>
            <textarea
              value={form.example_concept}
              onChange={(e) => setForm((f) => ({ ...f, example_concept: e.target.value }))}
              placeholder="A general example of your creative approach, e.g. 'For a fitness brand I might create a 30-day challenge series...'"
              className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-amber-500"
            />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "مثال مبدئي (AR)" : "Example Concept (AR)"}</Label>
            <textarea
              value={form.example_concept_ar}
              onChange={(e) => setForm((f) => ({ ...f, example_concept_ar: e.target.value }))}
              dir="rtl"
              className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        <div className="flex gap-3">
          <Button type="button" variant="ghost" onClick={() => router.back()} className="flex-1">
            {lang === "ar" ? "إلغاء" : "Cancel"}
          </Button>
          <Button type="submit" disabled={saving} className="flex-1 bg-pink-600 hover:bg-pink-500 text-white">
            {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "نشر" : "Publish")}
          </Button>
        </div>
      </form>
    </div>
  );
}
