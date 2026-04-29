"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { getCampaigns, getMyCampaigns, activateCampaign, deleteCampaign, applyToCampaign } from "@/lib/api";
import { Campaign } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { Tag, Calendar, Trash2, Zap } from "lucide-react";
import Link from "next/link";

export default function CampaignsPage() {
  const { user, lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState<number | null>(null);

  const isMerchant = user?.role === "merchant";
  const isAdmin    = user?.role === "admin";

  async function load() {
    setLoading(true);
    try {
      // admin sees all campaigns, merchant sees own, influencer sees active
      const r = isMerchant ? await getMyCampaigns() : await getCampaigns(isAdmin ? {} : { status: "active" });
      // getMyCampaigns returns array directly; getCampaigns returns {data:[...]}
      const list = Array.isArray(r.data) ? r.data : (r.data?.data ?? []);
      setCampaigns(list);
    } catch {
      toast.error("Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleActivate(id: number) {
    try {
      await activateCampaign(id);
      toast.success(lang === "ar" ? "تم تفعيل الحملة!" : "Campaign activated!");
      load();
    } catch {
      toast.error(lang === "ar" ? "فشل التفعيل" : "Activation failed");
    }
  }

  async function handleApply(id: number) {
    setApplying(id);
    try {
      await applyToCampaign(id);
      toast.success(lang === "ar" ? "تم إرسال طلبك!" : "Application submitted!");
    } catch (err: unknown) {
      const raw = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const detail = typeof raw === "string" ? raw : Array.isArray(raw) ? raw.map((e: unknown) => (e as { msg?: string })?.msg ?? "Error").join(" · ") : undefined;
      toast.error(detail ?? (lang === "ar" ? "فشل التقديم" : "Application failed"));
    } finally {
      setApplying(null);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm(lang === "ar" ? "هل أنت متأكد؟" : "Are you sure?")) return;
    try {
      await deleteCampaign(id);
      toast.success(lang === "ar" ? "تم الحذف!" : "Deleted!");
      load();
    } catch {
      toast.error(lang === "ar" ? "فشل الحذف" : "Delete failed");
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
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">
          📢 {isMerchant ? (lang === "ar" ? "حملاتي" : "My Campaigns") : (lang === "ar" ? "الحملات المتاحة" : "Open Campaigns")}
        </h1>
        {isMerchant && (
          <Link href="/merchant/dashboard">
            <Button variant="merchant">+ {lang === "ar" ? "حملة جديدة" : "New Campaign"}</Button>
          </Link>
        )}
      </div>

      <div className="space-y-3">
        {campaigns.map((c) => (
          <div key={c.id} className="glass-card p-5 hover:border-white/10 transition-colors">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white text-sm">{lang === "ar" ? c.title_ar : c.title_en}</h3>
                <p className="text-white/40 text-xs mt-1 line-clamp-2">{lang === "ar" ? c.description_ar : c.description_en}</p>
                <div className="flex items-center gap-4 mt-2">
                  {c.niche && (
                    <span className="flex items-center gap-1 text-violet-400 text-xs"><Tag size={10} /> {c.niche}</span>
                  )}
                  {c.end_date && (
                    <span className="flex items-center gap-1 text-white/40 text-xs"><Calendar size={10} /> {c.end_date}</span>
                  )}
                  <span className="text-amber-400 text-xs font-medium">{fmtJOD(c.total_budget)} total</span>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <span className={statusClass(c.status)}>{c.status}</span>
                {isMerchant && c.status === "DRAFT" && (
                  <Button size="sm" variant="success" onClick={() => handleActivate(c.id)} className="gap-1">
                    <Zap size={12} /> {lang === "ar" ? "تفعيل" : "Activate"}
                  </Button>
                )}
                {isMerchant && (
                  <Button size="icon" variant="ghost" className="h-7 w-7 text-red-400/60 hover:text-red-400 hover:bg-red-400/10" onClick={() => handleDelete(c.id)}>
                    <Trash2 size={13} />
                  </Button>
                )}
                {!isMerchant && c.status === "ACTIVE" && (
                  <Button size="sm" disabled={applying === c.id} onClick={() => handleApply(c.id)}>
                    {applying === c.id ? "..." : lang === "ar" ? "تقديم" : "Apply"}
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}
        {campaigns.length === 0 && (
          <div className="text-white/30 text-sm text-center py-12">
            {isMerchant
              ? lang === "ar" ? "لا توجد حملات. أنشئ أولى حملاتك!" : "No campaigns yet. Create your first one!"
              : lang === "ar" ? "لا توجد حملات متاحة." : "No open campaigns available."}
          </div>
        )}
      </div>
    </div>
  );
}
