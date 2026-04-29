"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getMyStrategistProfile, createStrategistProfile, updateStrategistProfile } from "@/lib/api";
import { CreativeStrategistProfile } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import {
  CheckCircle2, Globe, DollarSign, Briefcase,
  MapPin, ExternalLink, User, Palette,
} from "lucide-react";

const SPECIALIZATIONS = [
  "Brand Strategy", "Content Planning", "Social Media",
  "Copywriting", "Video Production", "Influencer Matching",
  "Campaign Analytics", "Creative Direction", "Fashion", "Food & Beverage",
  "Tech", "Beauty", "Fitness", "Travel", "Lifestyle", "Education",
];
const LANGUAGES = ["Arabic", "English", "French"];

function PillToggle({ options, selected, onChange, color = "emerald" }: {
  options: string[]; selected: string[]; onChange: (v: string[]) => void; color?: string;
}) {
  const toggle = (opt: string) =>
    onChange(selected.includes(opt) ? selected.filter((x) => x !== opt) : [...selected, opt]);
  const activeClass = color === "emerald"
    ? "bg-emerald-600 border-emerald-500 text-white"
    : "bg-violet-600 border-violet-500 text-white";
  return (
    <div className="flex flex-wrap gap-1.5">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => toggle(opt)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
            selected.includes(opt)
              ? activeClass
              : "border-white/15 text-white/50 hover:border-white/30 hover:text-white/70"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

export default function StrategistProfilePage() {
  const { user, lang } = useApp();
  const [existing, setExisting] = useState<CreativeStrategistProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    display_name: "",
    display_name_ar: "",
    bio: "",
    bio_ar: "",
    city: "",
    portfolio_url: "",
    specializations: [] as string[],
    languages: ["Arabic", "English"] as string[],
    consultation_rate_jod: "",
    is_available: true,
  });

  useEffect(() => {
    getMyStrategistProfile()
      .then((r) => {
        const p: CreativeStrategistProfile = r.data;
        setExisting(p);
        setForm({
          display_name: p.display_name ?? "",
          display_name_ar: p.display_name_ar ?? "",
          bio: p.bio ?? "",
          bio_ar: p.bio_ar ?? "",
          city: p.city ?? "",
          portfolio_url: p.portfolio_url ?? "",
          specializations: p.specializations ?? [],
          languages: p.languages ?? ["Arabic", "English"],
          consultation_rate_jod: String(p.consultation_rate_jod ?? ""),
          is_available: p.is_available ?? true,
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function upd(k: string, v: string | string[] | boolean) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...form,
        consultation_rate_jod: parseFloat(form.consultation_rate_jod) || 0,
      };
      const r = existing
        ? await updateStrategistProfile(payload)
        : await createStrategistProfile(payload);
      setExisting(r.data);
      toast.success(lang === "ar" ? "تم حفظ الملف الشخصي!" : "Profile saved!");
    } catch {
      toast.error(lang === "ar" ? "فشل الحفظ" : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
          <Palette size={18} className="text-emerald-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">
            {lang === "ar" ? "ملفي الشخصي" : "My Creative Profile"}
          </h1>
          <p className="text-white/40 text-xs">
            {lang === "ar" ? "مرئي للتجار والشركاء" : "Visible to merchants and partners on WaslAI"}
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">

        {/* ── Form (left 2 cols) ── */}
        <form onSubmit={handleSave} className="lg:col-span-2 space-y-5">

          {/* Identity */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <User size={14} className="text-white/40" />
              <span className="text-xs text-white/40 uppercase tracking-wider">
                {lang === "ar" ? "الهوية" : "Identity"}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Display Name (EN)</Label>
                <Input
                  required
                  value={form.display_name}
                  onChange={(e) => upd("display_name", e.target.value)}
                  placeholder="Jane Creative"
                />
              </div>
              <div className="space-y-1.5">
                <Label>الاسم المعروض (AR)</Label>
                <Input
                  value={form.display_name_ar}
                  onChange={(e) => upd("display_name_ar", e.target.value)}
                  placeholder="جين كرييتيف"
                  dir="rtl"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label><MapPin size={11} className="inline mr-1 opacity-50" />{lang === "ar" ? "المدينة" : "City"}</Label>
                <Input
                  value={form.city}
                  onChange={(e) => upd("city", e.target.value)}
                  placeholder="Amman"
                />
              </div>
              <div className="space-y-1.5">
                <Label><ExternalLink size={11} className="inline mr-1 opacity-50" />{lang === "ar" ? "رابط الأعمال" : "Portfolio URL"}</Label>
                <Input
                  value={form.portfolio_url}
                  onChange={(e) => upd("portfolio_url", e.target.value)}
                  placeholder="https://..."
                  type="url"
                />
              </div>
            </div>
          </div>

          {/* Bio */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <Briefcase size={14} className="text-white/40" />
              <span className="text-xs text-white/40 uppercase tracking-wider">
                {lang === "ar" ? "السيرة الذاتية" : "Bio"}
              </span>
            </div>
            <div className="space-y-1.5">
              <Label>Bio (EN)</Label>
              <Textarea
                value={form.bio}
                onChange={(e) => upd("bio", e.target.value)}
                placeholder="Tell merchants what you bring to campaigns — your creative philosophy, notable work, what makes you different..."
                rows={3}
              />
            </div>
            <div className="space-y-1.5">
              <Label>السيرة الذاتية (AR)</Label>
              <Textarea
                value={form.bio_ar}
                onChange={(e) => upd("bio_ar", e.target.value)}
                placeholder="صف ما تقدمه للحملات..."
                rows={3}
                dir="rtl"
              />
            </div>
          </div>

          {/* Expertise */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <Globe size={14} className="text-white/40" />
              <span className="text-xs text-white/40 uppercase tracking-wider">
                {lang === "ar" ? "التخصصات واللغات" : "Expertise & Languages"}
              </span>
            </div>
            <div className="space-y-2">
              <Label>{lang === "ar" ? "التخصصات" : "Specializations"}</Label>
              <PillToggle
                options={SPECIALIZATIONS}
                selected={form.specializations}
                onChange={(v) => upd("specializations", v)}
                color="emerald"
              />
            </div>
            <div className="space-y-2">
              <Label>{lang === "ar" ? "اللغات" : "Languages"}</Label>
              <PillToggle
                options={LANGUAGES}
                selected={form.languages}
                onChange={(v) => upd("languages", v)}
                color="violet"
              />
            </div>
          </div>

          {/* Rate & availability */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center gap-2 mb-1">
              <DollarSign size={14} className="text-white/40" />
              <span className="text-xs text-white/40 uppercase tracking-wider">
                {lang === "ar" ? "التسعير والتوافر" : "Pricing & Availability"}
              </span>
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "رسوم الاستشارة (JOD / مشروع)" : "Consultation Rate (JOD / project)"}</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm">JOD</span>
                <Input
                  type="number"
                  value={form.consultation_rate_jod}
                  onChange={(e) => upd("consultation_rate_jod", e.target.value)}
                  placeholder="150"
                  min={0}
                  className="pl-12"
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => upd("is_available", !form.is_available)}
                className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${form.is_available ? "bg-emerald-600" : "bg-white/10"}`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-200 ${form.is_available ? "translate-x-5" : "translate-x-0"}`}
                />
              </button>
              <div>
                <div className={`text-sm font-medium ${form.is_available ? "text-emerald-400" : "text-white/40"}`}>
                  {form.is_available
                    ? lang === "ar" ? "متاح للتعاون الآن" : "Available for hire"
                    : lang === "ar" ? "غير متاح حالياً" : "Not currently available"}
                </div>
                <div className="text-white/30 text-xs">
                  {lang === "ar" ? "يتحكم في ظهورك في نتائج البحث" : "Controls your visibility in merchant searches"}
                </div>
              </div>
            </div>
          </div>

          <Button type="submit" disabled={saving} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white h-11 font-semibold">
            {saving
              ? lang === "ar" ? "جار الحفظ..." : "Saving..."
              : lang === "ar" ? "حفظ الملف الشخصي" : "Save Profile"}
          </Button>
        </form>

        {/* ── Preview Card (right col) ── */}
        <div className="space-y-4">
          <div className="glass-card p-5 sticky top-6">
            <div className="text-xs text-white/30 uppercase tracking-wider mb-4">
              {lang === "ar" ? "معاينة الملف" : "Profile Preview"}
            </div>

            {/* Avatar placeholder */}
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-white">
                {(form.display_name || user?.full_name || "?")[0].toUpperCase()}
              </span>
            </div>

            <div className="text-center mb-4">
              <div className="font-bold text-white text-base">
                {form.display_name || (lang === "ar" ? "اسمك" : "Your Name")}
              </div>
              {form.display_name_ar && (
                <div className="text-white/50 text-sm" dir="rtl">{form.display_name_ar}</div>
              )}
              {existing?.is_verified && (
                <div className="inline-flex items-center gap-1 mt-1.5 px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs">
                  <CheckCircle2 size={10} /> Verified
                </div>
              )}
            </div>

            {form.bio && (
              <p className="text-white/50 text-xs text-center line-clamp-3 mb-4 border-t border-white/5 pt-4">
                {form.bio}
              </p>
            )}

            <div className="space-y-2 text-xs">
              {form.city && (
                <div className="flex items-center gap-2 text-white/40">
                  <MapPin size={11} />
                  <span>{form.city}</span>
                </div>
              )}
              {form.consultation_rate_jod && (
                <div className="flex items-center gap-2 text-white/40">
                  <DollarSign size={11} />
                  <span>{fmtJOD(parseFloat(form.consultation_rate_jod) || 0)} / {lang === "ar" ? "مشروع" : "project"}</span>
                </div>
              )}
            </div>

            {form.specializations.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/5">
                <div className="flex flex-wrap gap-1">
                  {form.specializations.slice(0, 5).map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-emerald-900/40 text-emerald-300 border border-emerald-700/20">
                      {s}
                    </span>
                  ))}
                  {form.specializations.length > 5 && (
                    <span className="px-2 py-0.5 rounded-full text-xs bg-white/5 text-white/30">
                      +{form.specializations.length - 5}
                    </span>
                  )}
                </div>
              </div>
            )}

            {existing && (
              <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-3 gap-2 text-center">
                <div>
                  <div className="text-emerald-400 font-bold text-sm">{existing.completed_engagements}</div>
                  <div className="text-white/30 text-xs">{lang === "ar" ? "مكتملة" : "Done"}</div>
                </div>
                <div>
                  <div className="text-amber-400 font-bold text-sm">{existing.milestone_count}</div>
                  <div className="text-white/30 text-xs">{lang === "ar" ? "معالم" : "Miles"}</div>
                </div>
                <div>
                  <div className="text-violet-400 font-bold text-sm">{fmtJOD(existing.total_earned_jod)}</div>
                  <div className="text-white/30 text-xs">{lang === "ar" ? "أرباح" : "Earned"}</div>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
