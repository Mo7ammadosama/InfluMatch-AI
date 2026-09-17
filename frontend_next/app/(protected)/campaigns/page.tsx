"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { getCampaigns, getMyCampaigns, getMyBookings, getCampaign, activateCampaign, deleteCampaign } from "@/lib/api";
import { Campaign } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { Tag, Calendar, Trash2, Zap } from "lucide-react";

export default function CampaignsPage() {
  const router = useRouter();
  const { user, lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState<string | null>(null); // used by admin apply

  const isMerchant = user?.role === "merchant";
  const isAdmin    = user?.role === "admin";
  const isInfluencer = user?.role === "influencer";

  async function load() {
    setLoading(true);
    try {
      let list: Campaign[] = [];
      if (isMerchant) {
        const r = await getMyCampaigns();
        list = Array.isArray(r.data) ? r.data : (r.data?.data ?? []);
      } else if (isInfluencer) {
        // Show campaigns the influencer is booked into
        const br = await getMyBookings();
        const bookings: { campaign_id: string | null }[] = Array.isArray(br.data) ? br.data : (br.data?.data ?? []);
        const ids = [...new Set(bookings.map(b => b.campaign_id).filter(Boolean))] as string[];
        const fetched = await Promise.all(ids.map(id => getCampaign(id).then(r => r.data).catch(() => null)));
        list = fetched.filter(Boolean) as Campaign[];
      } else {
        const r = await getCampaigns({});
        list = Array.isArray(r.data) ? r.data : (r.data?.data ?? []);
      }
      setCampaigns(list);
    } catch {
      toast.error("Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { if (user) load(); }, [user?.role]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleActivate(id: string) {
    try {
      await activateCampaign(id );
      toast.success(lang === "ar" ? "تم تفعيل الحملة!" : "Campaign activated!");
      load();
    } catch {
      toast.error(lang === "ar" ? "فشل التفعيل" : "Activation failed");
    }
  }

  async function handleApply(id: string) {
    setApplying(id);
    try {
      await applyToCampaign(id );
      toast.success(lang === "ar" ? "تم إرسال طلبك!" : "Application submitted!");
    } catch (err: unknown) {
      const raw = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const detail = typeof raw === "string" ? raw : Array.isArray(raw) ? raw.map((e: unknown) => (e as { msg?: string })?.msg ?? "Error").join(" · ") : undefined;
      toast.error(detail ?? (lang === "ar" ? "فشل التقديم" : "Application failed"));
    } finally {
      setApplying(null);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm(lang === "ar" ? "هل أنت متأكد؟" : "Are you sure?")) return;
    try {
      await deleteCampaign(id );
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
          📢 {isMerchant || isInfluencer
            ? lang === "ar" ? "حملاتي" : "My Campaigns"
            : lang === "ar" ? "الحملات" : "Campaigns"}
        </h1>
        {isMerchant && (
          <Button variant="merchant" onClick={() => router.push("/campaigns/create")}>
            + {lang === "ar" ? "حملة جديدة" : "New Campaign"}
          </Button>
        )}
      </div>

      <div className="space-y-3">
        {campaigns.map((c) => (
          <div key={c.id} className="glass-card p-5 hover:border-white/10 transition-colors">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-white text-sm">
                  {lang === "ar" ? c.title_ar ?? c.title : c.title}
                </h3>
                <p className="text-white/40 text-xs mt-1 line-clamp-2">
                  {lang === "ar" ? c.description_ar ?? c.description : c.description}
                </p>
                <div className="flex items-center gap-4 mt-2">
                  {c.target_categories?.[0] && (
                    <span className="flex items-center gap-1 text-violet-400 text-xs">
                      <Tag size={10} /> {c.target_categories[0]}
                    </span>
                  )}
                  {c.end_date && (
                    <span className="flex items-center gap-1 text-white/40 text-xs">
                      <Calendar size={10} /> {c.end_date}
                    </span>
                  )}
                  <span className="text-amber-400 text-xs font-medium">
                    {fmtJOD(c.total_budget_jod)} {lang === "ar" ? "الميزانية" : "total"}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <span className={statusClass(c.status)}>{c.status}</span>
                {isMerchant && c.status === "draft" && (
                  <Button size="sm" variant="success" onClick={() => handleActivate(c.id)} className="gap-1">
                    <Zap size={12} /> {lang === "ar" ? "تفعيل" : "Activate"}
                  </Button>
                )}
                {isMerchant && (
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 text-red-400/60 hover:text-red-400 hover:bg-red-400/10"
                    onClick={() => handleDelete(c.id)}
                  >
                    <Trash2 size={13} />
                  </Button>
                )}
                {!isMerchant && !isInfluencer && c.status === "active" && (
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
              : isInfluencer
              ? lang === "ar" ? "لم تنضم إلى أي حملات بعد." : "You haven't joined any campaigns yet."
              : lang === "ar" ? "لا توجد حملات." : "No campaigns available."}
          </div>
        )}
      </div>
    </div>
  );
}
