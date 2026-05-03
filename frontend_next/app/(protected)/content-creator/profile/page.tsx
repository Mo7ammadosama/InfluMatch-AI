"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getMyCreatorProfile, createCreatorProfile, updateCreatorProfile } from "@/lib/api";
import { ContentCreatorProfile } from "@/lib/types";
import { toast } from "sonner";

const SPECIALIZATION_OPTIONS = ["Video Production", "Social Media", "Photography", "Animation", "Copywriting", "Graphic Design", "Podcasting", "Live Streaming"];
const CATEGORY_OPTIONS = ["Fashion", "Food", "Tech", "Beauty", "Fitness", "Lifestyle", "Travel", "Education", "Gaming", "Business"];
const LANGUAGE_OPTIONS = ["Arabic", "English", "French"];

export default function ContentCreatorProfilePage() {
  const { lang } = useApp();
  const [profile, setProfile] = useState<ContentCreatorProfile | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    display_name: "",
    display_name_ar: "",
    bio: "",
    bio_ar: "",
    avatar_url: "",
    city: "",
    portfolio_url: "",
    specializations: [] as string[],
    languages: ["Arabic", "English"] as string[],
    content_categories: [] as string[],
    consultation_rate_jod: "",
  });

  useEffect(() => {
    getMyCreatorProfile().then((r) => {
      const p: ContentCreatorProfile = r.data;
      setProfile(p);
      setForm({
        display_name: p.display_name,
        display_name_ar: p.display_name_ar ?? "",
        bio: p.bio ?? "",
        bio_ar: p.bio_ar ?? "",
        avatar_url: p.avatar_url ?? "",
        city: p.city ?? "",
        portfolio_url: p.portfolio_url ?? "",
        specializations: p.specializations,
        languages: p.languages,
        content_categories: p.content_categories,
        consultation_rate_jod: String(p.consultation_rate_jod ?? ""),
      });
    }).catch(() => null);
  }, []);

  function toggleItem(list: string[], item: string): string[] {
    return list.includes(item) ? list.filter((x) => x !== item) : [...list, item];
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        consultation_rate_jod: parseFloat(form.consultation_rate_jod) || 0,
      };
      const r = profile
        ? await updateCreatorProfile(payload)
        : await createCreatorProfile(payload);
      setProfile(r.data);
      toast.success(lang === "ar" ? "تم الحفظ!" : "Profile saved!");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-xl font-bold text-white">
        {lang === "ar" ? "الملف الشخصي" : "Creator Profile"}
      </h1>

      <form onSubmit={handleSave} className="glass-card p-6 space-y-5">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الاسم المعروض (EN)" : "Display Name (EN)"}</Label>
            <Input value={form.display_name} onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))} required />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الاسم المعروض (AR)" : "Display Name (AR)"}</Label>
            <Input value={form.display_name_ar} onChange={(e) => setForm((f) => ({ ...f, display_name_ar: e.target.value }))} dir="rtl" />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>Bio (EN)</Label>
          <textarea
            value={form.bio}
            onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
            className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
          />
        </div>
        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "نبذة (AR)" : "Bio (AR)"}</Label>
          <textarea
            value={form.bio_ar}
            onChange={(e) => setForm((f) => ({ ...f, bio_ar: e.target.value }))}
            dir="rtl"
            className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[80px] resize-none focus:outline-none focus:border-pink-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "المدينة" : "City"}</Label>
            <Input value={form.city} onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))} placeholder="Amman" />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "سعر الاستشارة (JOD)" : "Rate (JOD)"}</Label>
            <Input type="number" value={form.consultation_rate_jod} onChange={(e) => setForm((f) => ({ ...f, consultation_rate_jod: e.target.value }))} placeholder="0" />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "رابط الموقع / المعرض" : "Portfolio URL"}</Label>
          <Input value={form.portfolio_url} onChange={(e) => setForm((f) => ({ ...f, portfolio_url: e.target.value }))} placeholder="https://..." />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "التخصصات" : "Specializations"}</Label>
          <div className="flex flex-wrap gap-2">
            {SPECIALIZATION_OPTIONS.map((s) => (
              <button key={s} type="button"
                onClick={() => setForm((f) => ({ ...f, specializations: toggleItem(f.specializations, s) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.specializations.includes(s) ? "bg-pink-600 border-pink-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "فئات المحتوى" : "Content Categories"}</Label>
          <div className="flex flex-wrap gap-2">
            {CATEGORY_OPTIONS.map((c) => (
              <button key={c} type="button"
                onClick={() => setForm((f) => ({ ...f, content_categories: toggleItem(f.content_categories, c) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.content_categories.includes(c) ? "bg-violet-600 border-violet-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "اللغات" : "Languages"}</Label>
          <div className="flex flex-wrap gap-2">
            {LANGUAGE_OPTIONS.map((l) => (
              <button key={l} type="button"
                onClick={() => setForm((f) => ({ ...f, languages: toggleItem(f.languages, l) }))}
                className={`px-3 py-1 rounded-full text-xs border transition ${form.languages.includes(l) ? "bg-emerald-600 border-emerald-500 text-white" : "border-white/10 text-white/40 hover:text-white/70"}`}>
                {l}
              </button>
            ))}
          </div>
        </div>

        <Button type="submit" disabled={saving} className="bg-pink-600 hover:bg-pink-500 text-white w-full">
          {saving ? (lang === "ar" ? "جار الحفظ..." : "Saving...") : (lang === "ar" ? "حفظ الملف الشخصي" : "Save Profile")}
        </Button>
      </form>
    </div>
  );
}
