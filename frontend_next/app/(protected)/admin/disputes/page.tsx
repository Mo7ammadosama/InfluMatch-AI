"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAdminDisputes, resolveDispute } from "@/lib/api";
import { toast } from "sonner";
import { RefreshCw, Scale } from "lucide-react";

interface Dispute {
  id: number;
  escrow_id?: number;
  booking_id?: number;
  reason: string;
  status: string;
  raised_by?: number;
}

interface ResolveState {
  disputeId: number;
  escrowId: number;
  decision: "MERCHANT" | "INFLUENCER";
  reason: string;
}

export default function AdminDisputesPage() {
  const { lang } = useApp();
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<number | null>(null);
  const [dialog, setDialog] = useState<ResolveState | null>(null);

  async function load() {
    setLoading(true);
    try {
      const r = await getAdminDisputes();
      setDisputes(Array.isArray(r.data) ? r.data : (r.data?.data ?? r.data?.disputes ?? []));
    } catch {
      toast.error("Failed to load disputes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  function openResolve(d: Dispute) {
    setDialog({
      disputeId: d.id,
      escrowId: d.escrow_id ?? d.id,
      decision: "MERCHANT",
      reason: "",
    });
  }

  async function submitResolve() {
    if (!dialog) return;
    if (!dialog.reason.trim()) {
      toast.error(lang === "ar" ? "أدخل سبب القرار" : "Enter a reason");
      return;
    }
    setActing(dialog.disputeId);
    try {
      await resolveDispute(dialog.escrowId, dialog.decision, dialog.reason.trim());
      toast.success(lang === "ar" ? "تم حل النزاع!" : "Dispute resolved!");
      setDialog(null);
      await load();
    } catch {
      toast.error(lang === "ar" ? "فشل الحل" : "Failed to resolve");
    } finally {
      setActing(null);
    }
  }

  const open = disputes.filter((d) => d.status === "OPEN" || d.status === "DISPUTED");
  const resolved = disputes.filter((d) => d.status !== "OPEN" && d.status !== "DISPUTED");

  return (
    <div className="space-y-4 max-w-5xl">
      <div className="admin-banner flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            ⚖️ {lang === "ar" ? "النزاعات" : "Disputes"}
          </h1>
          <p className="text-white/50 text-sm mt-1">
            {lang === "ar"
              ? `${open.length} مفتوح · ${resolved.length} محلول`
              : `${open.length} open · ${resolved.length} resolved`}
          </p>
        </div>
        <Button size="sm" variant="outline" onClick={load} className="gap-2">
          <RefreshCw size={14} /> {lang === "ar" ? "تحديث" : "Refresh"}
        </Button>
      </div>

      {/* Resolve dialog */}
      {dialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[#17171f] border border-white/10 rounded-xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <h2 className="text-white font-semibold text-lg flex items-center gap-2">
              <Scale size={18} className="text-amber-400" />
              {lang === "ar" ? "حل النزاع" : "Resolve Dispute"} #{dialog.disputeId}
            </h2>

            <div className="space-y-2">
              <label className="text-white/60 text-xs">{lang === "ar" ? "القرار لصالح" : "Rule in favor of"}</label>
              <div className="flex gap-2">
                {(["MERCHANT", "INFLUENCER"] as const).map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setDialog((d) => d ? { ...d, decision: opt } : d)}
                    className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-colors ${
                      dialog.decision === opt
                        ? opt === "MERCHANT"
                          ? "border-amber-500 bg-amber-500/15 text-amber-400"
                          : "border-violet-500 bg-violet-500/15 text-violet-400"
                        : "border-white/10 text-white/40 hover:border-white/20 hover:text-white/60"
                    }`}
                  >
                    {opt === "MERCHANT"
                      ? lang === "ar" ? "التاجر" : "Merchant"
                      : lang === "ar" ? "المؤثر" : "Influencer"}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-white/60 text-xs">{lang === "ar" ? "السبب" : "Reason"}</label>
              <textarea
                value={dialog.reason}
                onChange={(e) => setDialog((d) => d ? { ...d, reason: e.target.value } : d)}
                rows={3}
                placeholder={lang === "ar" ? "أدخل سبب القرار..." : "Enter resolution reason..."}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm placeholder-white/30 resize-none focus:outline-none focus:border-white/20"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <Button
                className="flex-1"
                onClick={submitResolve}
                disabled={acting === dialog.disputeId}
              >
                {acting === dialog.disputeId
                  ? "..."
                  : lang === "ar" ? "تأكيد القرار" : "Confirm Decision"}
              </Button>
              <Button variant="ghost" onClick={() => setDialog(null)} className="text-white/40">
                {lang === "ar" ? "إلغاء" : "Cancel"}
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {disputes.length === 0 && !loading && (
          <div className="text-white/30 text-sm text-center py-10">
            {lang === "ar" ? "لا نزاعات مفتوحة" : "No open disputes"}
          </div>
        )}
        {disputes.map((d) => {
          const isOpen = d.status === "OPEN" || d.status === "DISPUTED";
          return (
            <div
              key={d.id}
              className={`glass-card p-4 border-l-2 ${isOpen ? "border-red-500/50" : "border-green-500/30"}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="text-white text-sm font-medium">
                    {lang === "ar" ? `نزاع #${d.id}` : `Dispute #${d.id}`}
                    {(d.escrow_id || d.booking_id) && (
                      <span className="text-white/40 font-normal ml-2">
                        — Escrow #{d.escrow_id ?? d.booking_id}
                      </span>
                    )}
                  </div>
                  <div className="text-white/50 text-xs mt-1 line-clamp-2">{d.reason}</div>
                  {d.raised_by && (
                    <div className="text-white/30 text-xs mt-0.5">
                      Raised by user #{d.raised_by}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge variant={isOpen ? "destructive" : "success"}>
                    {d.status}
                  </Badge>
                  {isOpen && (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={acting === d.id}
                      onClick={() => openResolve(d)}
                      className="gap-1.5 text-amber-400 border-amber-500/30 hover:border-amber-500/60 hover:bg-amber-500/10"
                    >
                      <Scale size={12} />
                      {lang === "ar" ? "حل النزاع" : "Resolve"}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
