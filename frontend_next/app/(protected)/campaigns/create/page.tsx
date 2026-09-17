"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createCampaign } from "@/lib/api";
import { toast } from "sonner";

export default function CreateCampaignPage() {
  const router = useRouter();
  const { lang } = useApp();
  const ar = lang === "ar";

  const [form, setForm] = useState({
    title: "",
    description: "",
    total_budget_jod: "",
  });
  const [submitting, setSubmitting] = useState(false);

  function set(field: string, value: string) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const budget = parseFloat(form.total_budget_jod);
    if (!form.title.trim()) {
      toast.error(ar ? "اسم الحملة مطلوب" : "Campaign name is required");
      return;
    }
    if (isNaN(budget) || budget < 0) {
      toast.error(ar ? "الميزانية يجب أن تكون رقماً موجباً" : "Budget must be a positive number");
      return;
    }

    setSubmitting(true);
    try {
      await createCampaign({
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        total_budget_jod: budget,
      });
      toast.success(ar ? "تم إنشاء الحملة!" : "Campaign created!");
      router.push("/campaigns");
    } catch (err: unknown) {
      const raw = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const msg =
        typeof raw === "string"
          ? raw
          : Array.isArray(raw)
          ? raw.map((e: unknown) => (e as { msg?: string })?.msg ?? "Error").join(" · ")
          : ar
          ? "فشل إنشاء الحملة"
          : "Failed to create campaign";
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">
          📢 {ar ? "إنشاء حملة جديدة" : "New Campaign"}
        </h1>
        <p className="text-white/40 text-sm mt-1">
          {ar ? "أدخل تفاصيل حملتك الإعلانية" : "Enter your campaign details"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card p-6 space-y-5">
        <div className="space-y-1.5">
          <Label>{ar ? "اسم الحملة" : "Campaign Name"} *</Label>
          <Input
            value={form.title}
            onChange={(e) => set("title", e.target.value)}
            placeholder={ar ? "مثال: حملة رمضان 2026" : "e.g. Ramadan 2026 Campaign"}
            required
          />
        </div>

        <div className="space-y-1.5">
          <Label>{ar ? "الوصف" : "Description"}</Label>
          <textarea
            value={form.description}
            onChange={(e) => set("description", e.target.value)}
            className="w-full rounded-md bg-white/5 border border-white/10 text-white text-sm p-2 min-h-[100px] resize-none focus:outline-none focus:border-violet-500"
            placeholder={ar ? "وصف مختصر للحملة..." : "Brief description of the campaign..."}
          />
        </div>

        <div className="space-y-1.5">
          <Label>{ar ? "الميزانية (JOD)" : "Budget (JOD)"} *</Label>
          <Input
            type="number"
            min="0"
            step="0.01"
            value={form.total_budget_jod}
            onChange={(e) => set("total_budget_jod", e.target.value)}
            placeholder="500"
            required
          />
        </div>

        <div className="flex gap-3 pt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={() => router.push("/campaigns")}
            className="flex-1"
          >
            {ar ? "إلغاء" : "Cancel"}
          </Button>
          <Button type="submit" disabled={submitting} variant="merchant" className="flex-1">
            {submitting ? (ar ? "جار الإنشاء..." : "Creating...") : ar ? "إنشاء الحملة" : "Create Campaign"}
          </Button>
        </div>
      </form>
    </div>
  );
}
