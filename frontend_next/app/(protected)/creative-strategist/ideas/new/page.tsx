"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { submitIdea } from "@/lib/api";
import { toast } from "sonner";
import { Lightbulb, Users, MonitorPlay, Target, DollarSign, ArrowRight, ArrowLeft } from "lucide-react";

const PLATFORMS  = ["Instagram", "TikTok", "YouTube", "X (Twitter)", "Snapchat"];
const FORMATS    = ["Reels", "Stories", "Posts", "Live", "Short Video"];
const CATEGORIES = ["fashion", "food", "tech", "beauty", "fitness", "travel", "lifestyle", "education", "entertainment", "other"];

function PillToggle({ options, selected, onChange }: { options: string[]; selected: string[]; onChange: (v: string[]) => void }) {
  const toggle = (opt: string) =>
    onChange(selected.includes(opt) ? selected.filter((x) => x !== opt) : [...selected, opt]);
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => (
        <button
          key={opt}
          type="button"
          onClick={() => toggle(opt)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
            selected.includes(opt)
              ? "bg-emerald-600 border-emerald-500 text-white"
              : "border-white/15 text-white/50 hover:border-white/30 hover:text-white/70"
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

const STEPS = [
  { icon: <Lightbulb size={16} />, label: "Concept", labelAr: "الفكرة" },
  { icon: <MonitorPlay size={16} />, label: "Execution", labelAr: "التنفيذ" },
  { icon: <Target size={16} />, label: "Audience", labelAr: "الجمهور" },
  { icon: <DollarSign size={16} />, label: "Budget", labelAr: "الميزانية" },
];

export default function NewIdeaPage() {
  const { lang } = useApp();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    title: "",
    title_ar: "",
    description: "",
    description_ar: "",
    target_audience: "",
    business_category: "",
    influencer_type: "",
    estimated_budget_jod: "",
    timeline_days: "",
    suggested_platforms: [] as string[],
    content_format: [] as string[],
  });

  function upd(k: string, v: string | string[]) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function handleSubmit() {
    setSaving(true);
    try {
      await submitIdea({
        ...form,
        estimated_budget_jod: form.estimated_budget_jod ? parseFloat(form.estimated_budget_jod) : undefined,
        timeline_days: form.timeline_days ? parseInt(form.timeline_days) : undefined,
      });
      toast.success(lang === "ar" ? "تم نشر الفكرة!" : "Idea published!");
      router.push("/creative-strategist/dashboard");
    } catch {
      toast.error(lang === "ar" ? "فشل النشر" : "Failed to publish idea");
    } finally {
      setSaving(false);
    }
  }

  const canProceed = [
    form.title.length >= 3 && form.description.length >= 10,
    form.suggested_platforms.length > 0,
    !!form.target_audience,
    true,
  ][step];

  return (
    <div className="max-w-2xl space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Lightbulb size={22} className="text-emerald-400" />
          {lang === "ar" ? "نشر فكرة إبداعية" : "Submit a Creative Idea"}
        </h1>
        <p className="text-white/40 text-sm mt-1">
          {lang === "ar"
            ? "الأفكار مرئية للعموم — التجار يدفعون مقابل توجيهك الإبداعي"
            : "Ideas are public — merchants pay for your creative direction, not just the idea"}
        </p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-2 flex-1">
            <div
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                i === step
                  ? "bg-emerald-600 text-white"
                  : i < step
                  ? "bg-emerald-900/40 text-emerald-400 border border-emerald-700/30"
                  : "bg-white/5 text-white/30"
              }`}
              onClick={() => i <= step && setStep(i)}
            >
              {s.icon}
              <span className="hidden sm:inline">{lang === "ar" ? s.labelAr : s.label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`h-px flex-1 transition-colors ${i < step ? "bg-emerald-700/50" : "bg-white/5"}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step panels */}
      <div className="glass-card p-6">

        {/* Step 0: Concept */}
        {step === 0 && (
          <div className="space-y-5">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb size={15} className="text-emerald-400" />
              <span className="font-semibold text-white">{lang === "ar" ? "مفهوم الحملة" : "Campaign Concept"}</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label>Title (EN) *</Label>
                <Input
                  value={form.title}
                  onChange={(e) => upd("title", e.target.value)}
                  placeholder="Ramadan Storytelling Series"
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label>العنوان (AR)</Label>
                <Input
                  value={form.title_ar}
                  onChange={(e) => upd("title_ar", e.target.value)}
                  placeholder="سلسلة قصص رمضان"
                  dir="rtl"
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "الوصف التفصيلي (EN) *" : "Full Description (EN) *"}</Label>
              <Textarea
                value={form.description}
                onChange={(e) => upd("description", e.target.value)}
                placeholder="Describe the full campaign concept — hook, narrative, execution vision, why it resonates..."
                rows={4}
                required
              />
              <div className="text-xs text-white/30 text-right">{form.description.length} / 2000</div>
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "الوصف (AR)" : "Description (AR)"}</Label>
              <Textarea
                value={form.description_ar}
                onChange={(e) => upd("description_ar", e.target.value)}
                placeholder="صف الفكرة بالتفصيل..."
                rows={3}
                dir="rtl"
              />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "قطاع العمل المناسب" : "Business Category"}</Label>
              <select
                value={form.business_category}
                onChange={(e) => upd("business_category", e.target.value)}
                className="w-full rounded-lg bg-white/5 border border-white/10 text-white text-sm px-3 py-2.5 focus:outline-none focus:border-emerald-500/50"
              >
                <option value="">{lang === "ar" ? "اختر القطاع" : "Select category"}</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>
        )}

        {/* Step 1: Execution */}
        {step === 1 && (
          <div className="space-y-5">
            <div className="flex items-center gap-2 mb-4">
              <MonitorPlay size={15} className="text-emerald-400" />
              <span className="font-semibold text-white">{lang === "ar" ? "خطة التنفيذ" : "Execution Plan"}</span>
            </div>
            <div className="space-y-2">
              <Label>{lang === "ar" ? "المنصات المقترحة *" : "Suggested Platforms *"}</Label>
              <p className="text-white/30 text-xs">{lang === "ar" ? "اختر منصة واحدة على الأقل" : "Select at least one platform"}</p>
              <PillToggle
                options={PLATFORMS}
                selected={form.suggested_platforms}
                onChange={(v) => upd("suggested_platforms", v)}
              />
            </div>
            <div className="space-y-2">
              <Label>{lang === "ar" ? "أنواع المحتوى" : "Content Formats"}</Label>
              <PillToggle
                options={FORMATS}
                selected={form.content_format}
                onChange={(v) => upd("content_format", v)}
              />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "نوع المؤثر المقترح" : "Suggested Influencer Type"}</Label>
              <Input
                value={form.influencer_type}
                onChange={(e) => upd("influencer_type", e.target.value)}
                placeholder={lang === "ar" ? "مؤثر ميكرو في الموضة، أنثى، عمّان" : "Micro fashion influencer, female, Amman"}
              />
            </div>
          </div>
        )}

        {/* Step 2: Audience */}
        {step === 2 && (
          <div className="space-y-5">
            <div className="flex items-center gap-2 mb-4">
              <Users size={15} className="text-emerald-400" />
              <span className="font-semibold text-white">{lang === "ar" ? "الجمهور المستهدف" : "Target Audience"}</span>
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "وصف الجمهور المستهدف *" : "Target Audience Description *"}</Label>
              <Textarea
                value={form.target_audience}
                onChange={(e) => upd("target_audience", e.target.value)}
                placeholder={lang === "ar"
                  ? "مثال: نساء 20-35، مهتمات بالموضة والجمال، من عمّان وإربد، دخل متوسط"
                  : "E.g.: Women 20–35, interested in fashion and beauty, in Amman & Irbid, middle income"}
                rows={3}
                required
              />
            </div>
            <div className="p-4 rounded-xl bg-emerald-900/20 border border-emerald-700/20">
              <div className="text-xs text-emerald-400 font-medium mb-1">
                {lang === "ar" ? "نصيحة للمستشارين" : "Pro Tip"}
              </div>
              <div className="text-xs text-white/50">
                {lang === "ar"
                  ? "كلما كنت أكثر تحديداً في وصف جمهورك، زادت قيمة فكرتك بالنسبة للتجار."
                  : "The more specific your audience definition, the more valuable your idea is to merchants."}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Budget */}
        {step === 3 && (
          <div className="space-y-5">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign size={15} className="text-emerald-400" />
              <span className="font-semibold text-white">{lang === "ar" ? "الميزانية والجدول الزمني" : "Budget & Timeline"}</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "الميزانية التقديرية (JOD)" : "Est. Campaign Budget (JOD)"}</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30 text-sm">JOD</span>
                  <Input
                    type="number"
                    value={form.estimated_budget_jod}
                    onChange={(e) => upd("estimated_budget_jod", e.target.value)}
                    placeholder="500"
                    min={0}
                    className="pl-12"
                  />
                </div>
                <p className="text-xs text-white/30">{lang === "ar" ? "للحملة كاملة، ليس رسومك أنت" : "For the full campaign, not your fee"}</p>
              </div>
              <div className="space-y-1.5">
                <Label>{lang === "ar" ? "المدة الزمنية (أيام)" : "Timeline (days)"}</Label>
                <Input
                  type="number"
                  value={form.timeline_days}
                  onChange={(e) => upd("timeline_days", e.target.value)}
                  placeholder="30"
                  min={1}
                />
                <p className="text-xs text-white/30">{lang === "ar" ? "المدة المقترحة لتنفيذ الحملة" : "Suggested campaign duration"}</p>
              </div>
            </div>

            {/* Summary */}
            <div className="p-4 rounded-xl bg-white/4 border border-white/8 space-y-2">
              <div className="text-xs text-white/40 uppercase tracking-wider mb-3">
                {lang === "ar" ? "ملخص الفكرة" : "Idea Summary"}
              </div>
              <div className="text-white text-sm font-medium">{form.title || "—"}</div>
              {form.business_category && (
                <div className="text-emerald-400 text-xs">{form.business_category}</div>
              )}
              {form.suggested_platforms.length > 0 && (
                <div className="flex gap-1 flex-wrap">
                  {form.suggested_platforms.map((p) => (
                    <span key={p} className="px-2 py-0.5 rounded-full text-xs bg-emerald-900/40 text-emerald-300 border border-emerald-700/20">{p}</span>
                  ))}
                </div>
              )}
              <div className="text-white/40 text-xs line-clamp-2">{form.description || "—"}</div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 pt-5 border-t border-white/5">
          <Button
            type="button"
            variant="ghost"
            onClick={() => setStep((s) => s - 1)}
            disabled={step === 0}
            className="gap-2 text-white/50"
          >
            <ArrowLeft size={14} />
            {lang === "ar" ? "السابق" : "Previous"}
          </Button>

          {step < STEPS.length - 1 ? (
            <Button
              type="button"
              onClick={() => setStep((s) => s + 1)}
              disabled={!canProceed}
              className="bg-emerald-600 hover:bg-emerald-500 text-white gap-2"
            >
              {lang === "ar" ? "التالي" : "Next"}
              <ArrowRight size={14} />
            </Button>
          ) : (
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={saving || !form.title}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-6"
            >
              {saving
                ? lang === "ar" ? "جار النشر..." : "Publishing..."
                : lang === "ar" ? "نشر الفكرة" : "Publish Idea"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
