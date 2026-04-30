"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { getMyEscrow, releaseEscrow, disputeEscrow } from "@/lib/api";
import { EscrowTransaction } from "@/lib/types";
import { fmtJOD, statusClass } from "@/lib/utils";
import { toast } from "sonner";
import { ShieldCheck, AlertTriangle } from "lucide-react";

export default function EscrowPage() {
  const { lang } = useApp();
  const [transactions, setTransactions] = useState<EscrowTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyEscrow()
      .then((r) => setTransactions(r.data?.items ?? r.data ?? []))
      .catch(() => toast.error("Failed to load escrow"))
      .finally(() => setLoading(false));
  }, []);

  async function handleRelease(id: number) {
    try {
      await releaseEscrow(id);
      toast.success(lang === "ar" ? "تم تحرير الأموال!" : "Funds released!");
      const r = await getMyEscrow();
      setTransactions(r.data?.items ?? r.data ?? []);
    } catch {
      toast.error(lang === "ar" ? "فشل التحرير" : "Release failed");
    }
  }

  async function handleDispute(id: number) {
    const reason = window.prompt(
      lang === "ar" ? "سبب النزاع:" : "Dispute reason:"
    );
    if (!reason) return;
    try {
      await disputeEscrow(id, { reason });
      toast.success(lang === "ar" ? "تم رفع النزاع!" : "Dispute raised!");
      const r = await getMyEscrow();
      setTransactions(r.data?.items ?? r.data ?? []);
    } catch {
      toast.error(lang === "ar" ? "فشل رفع النزاع" : "Failed to raise dispute");
    }
  }

  const totalLocked = transactions
    .filter((t) => ["FUNDED", "IN_PROGRESS", "UNDER_REVIEW"].includes(t.status))
    .reduce((s, t) => s + (t.gross_amount ?? 0), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="merchant-banner flex items-center gap-3">
        <ShieldCheck size={24} className="text-amber-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">
            {lang === "ar" ? "💰 الضمان المالي" : "💰 Escrow"}
          </h1>
          <p className="text-white/50 text-sm mt-0.5">
            {lang === "ar" ? "المبالغ المحجوزة: " : "Currently locked: "}
            <span className="text-amber-400 font-semibold">{fmtJOD(totalLocked)}</span>
          </p>
        </div>
      </div>

      {transactions.length === 0 && (
        <div className="text-white/30 text-sm text-center py-12">
          {lang === "ar" ? "لا توجد معاملات ضمان." : "No escrow transactions."}
        </div>
      )}

      <div className="space-y-4">
        {transactions.map((t) => (
          <div key={t.id} className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="font-semibold text-white text-sm">
                  {lang === "ar" ? `معاملة #${t.id}` : `Transaction #${t.id}`}
                  {t.campaign && (
                    <span className="text-white/40 font-normal">
                      {" "}— {lang === "ar" ? t.campaign.title_ar ?? t.campaign.title : t.campaign.title}
                    </span>
                  )}
                </div>
                {t.auto_release_at && (
                  <div className="text-white/40 text-xs mt-0.5">
                    {lang === "ar" ? "الإفراج التلقائي: " : "Auto-release: "}
                    {new Date(t.auto_release_at).toLocaleDateString()}
                  </div>
                )}
              </div>
              <span className={statusClass(t.status)}>{t.status}</span>
            </div>

            <div className="grid grid-cols-4 gap-3 mb-4">
              <div className="stats-grid-item">
                <div className="text-white text-sm font-bold">{fmtJOD(t.gross_amount)}</div>
                <div className="text-white/40 text-[10px]">{lang === "ar" ? "الإجمالي" : "Gross"}</div>
              </div>
              <div className="stats-grid-item">
                <div className="text-green-400 text-sm font-bold">{fmtJOD(t.net_amount)}</div>
                <div className="text-white/40 text-[10px]">{lang === "ar" ? "الصافي" : "Net"}</div>
              </div>
              <div className="stats-grid-item">
                <div className="text-amber-400 text-sm font-bold">{fmtJOD(t.platform_fee)}</div>
                <div className="text-white/40 text-[10px]">{lang === "ar" ? "رسوم المنصة" : "Platform Fee"}</div>
              </div>
              <div className="stats-grid-item">
                <div className="text-white/60 text-sm font-bold">{fmtJOD(t.vat_amount)}</div>
                <div className="text-white/40 text-[10px]">VAT</div>
              </div>
            </div>

            {["FUNDED", "IN_PROGRESS", "UNDER_REVIEW"].includes(t.status) && (
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="success"
                  onClick={() => handleRelease(t.id)}
                >
                  ✅ {lang === "ar" ? "تحرير الأموال" : "Release Funds"}
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => handleDispute(t.id)}
                  className="gap-1"
                >
                  <AlertTriangle size={13} />
                  {lang === "ar" ? "رفع نزاع" : "Raise Dispute"}
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
