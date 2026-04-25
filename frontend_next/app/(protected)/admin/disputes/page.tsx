"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAdminDisputes, resolveDispute } from "@/lib/api";
import { toast } from "sonner";

interface Dispute {
  id: number;
  escrow_id?: number;
  booking_id?: number;
  reason: string;
  status: string;
  raised_by?: number;
}

export default function AdminDisputesPage() {
  const { lang } = useApp();
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    getAdminDisputes()
      .then((r) => setDisputes(Array.isArray(r.data) ? r.data : (r.data?.data ?? r.data?.disputes ?? [])))
      .catch(() => toast.error("Failed to load disputes"))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  async function handleResolve(id: number) {
    const resolution = window.prompt(lang === "ar" ? "قرار الحل:" : "Resolution:");
    if (!resolution) return;
    try {
      await resolveDispute(id, { resolution });
      toast.success(lang === "ar" ? "تم حل النزاع!" : "Dispute resolved!");
      await load();
    } catch {
      toast.error(lang === "ar" ? "فشل الحل" : "Failed to resolve");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-5xl">
      <div className="admin-banner">
        <h1 className="text-2xl font-bold text-white">
          ⚖️ {lang === "ar" ? "النزاعات" : "Disputes"}
        </h1>
        <p className="text-white/50 text-sm mt-1">
          {lang === "ar" ? `${disputes.length} نزاع` : `${disputes.length} disputes`}
        </p>
      </div>

      <div className="space-y-3">
        {disputes.map((d) => (
          <div key={d.id} className="glass-card p-4 border-l-2 border-red-500/40">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-white text-sm font-medium">
                  {lang === "ar" ? `نزاع #${d.id}` : `Dispute #${d.id}`}
                  {(d.escrow_id || d.booking_id) && (
                    <span className="text-white/40 font-normal"> — #{d.escrow_id ?? d.booking_id}</span>
                  )}
                </div>
                <div className="text-white/50 text-xs mt-1">{d.reason}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={d.status === "OPEN" || d.status === "DISPUTED" ? "destructive" : "success"}>
                  {d.status}
                </Badge>
                {(d.status === "OPEN" || d.status === "DISPUTED") && (
                  <Button size="sm" variant="outline" onClick={() => handleResolve(d.id)}>
                    {lang === "ar" ? "حل" : "Resolve"}
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}
        {disputes.length === 0 && (
          <div className="text-white/30 text-sm text-center py-10">
            {lang === "ar" ? "لا نزاعات مفتوحة" : "No open disputes"}
          </div>
        )}
      </div>
    </div>
  );
}
