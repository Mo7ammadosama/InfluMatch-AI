"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { getPlatformStats, getAdminUsers, getAdminDisputes, resolveDispute } from "@/lib/api";
import { PlatformStats, User } from "@/lib/types";
import { fmtJOD, fmtNum } from "@/lib/utils";
import { toast } from "sonner";
import { Zap, ShieldCheck, Database } from "lucide-react";

interface Dispute {
  id: number;
  escrow_id?: number;
  booking_id?: number;
  reason: string;
  status: string;
  raised_by?: number;
}

export default function AdminPage() {
  const { lang } = useApp();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getPlatformStats(),
      getAdminUsers().catch(() => ({ data: [] })),
      getAdminDisputes().catch(() => ({ data: [] })),
    ]).then(([s, u, d]) => {
      setStats(s.data);
      // admin/users may return array or paginated
      setUsers(Array.isArray(u.data) ? u.data : (u.data?.data ?? u.data?.users ?? []));
      setDisputes(Array.isArray(d.data) ? d.data : (d.data?.data ?? d.data?.disputes ?? []));
    }).finally(() => setLoading(false));
  }, []);

  async function handleResolve(id: number) {
    const resolution = window.prompt(lang === "ar" ? "قرار الحل:" : "Resolution:");
    if (!resolution) return;
    try {
      await resolveDispute(id, { resolution });
      toast.success(lang === "ar" ? "تم حل النزاع!" : "Dispute resolved!");
      const r = await getAdminDisputes().catch(() => ({ data: [] }));
      setDisputes(Array.isArray(r.data) ? r.data : (r.data?.data ?? []));
    } catch {
      toast.error(lang === "ar" ? "فشل الحل" : "Failed to resolve");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">Loading God Mode...</div>
      </div>
    );
  }

  // Map backend field names
  const s = stats as Record<string, number> | null;

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="admin-banner flex items-center gap-3">
        <Zap size={26} className="text-red-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">⚡ GOD MODE — ARIA Control Center</h1>
          <p className="text-white/50 text-sm mt-0.5">{lang === "ar" ? "لوحة التحكم الشاملة" : "Full platform oversight"}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <KpiBlock label={lang === "ar" ? "المستخدمون" : "Total Users"} value={fmtNum(s?.total_users)} accent="violet" />
        <KpiBlock label={lang === "ar" ? "التجار" : "Merchants"} value={fmtNum(s?.total_merchants)} accent="amber" />
        <KpiBlock label={lang === "ar" ? "المؤثرون" : "Influencers"} value={fmtNum(s?.total_influencers)} accent="violet" />
        <KpiBlock label={lang === "ar" ? "الحملات النشطة" : "Active Campaigns"} value={fmtNum(s?.active_campaigns)} accent="green" />
        <KpiBlock label={lang === "ar" ? "مبالغ محجوزة" : "Escrow Locked"} value={fmtJOD(s?.escrow_locked_jod ?? s?.escrow_locked)} accent="red" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiBlock label={lang === "ar" ? "حجم الضمان الكلي" : "Total Escrow Volume"} value={fmtJOD(s?.total_escrow_volume_jod ?? s?.total_escrow_volume)} accent="blue" />
        <KpiBlock label={lang === "ar" ? "رسوم المنصة" : "Platform Fees"} value={fmtJOD(s?.total_platform_fees_jod ?? s?.platform_fees)} accent="amber" />
        <KpiBlock label={lang === "ar" ? "النزاعات المفتوحة" : "Open Disputes"} value={s?.open_disputes ?? 0} accent="red" />
        <KpiBlock label={lang === "ar" ? "مستخدمون جدد اليوم" : "New Users Today"} value={s?.new_users_today ?? 0} accent="green" />
      </div>

      {/* Agent status */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="aria-card flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-500/15 flex items-center justify-center">
            <ShieldCheck size={18} className="text-green-400" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">Guardian Agent</div>
            <div className="text-green-400 text-xs">● {lang === "ar" ? "يعمل" : "Active"}</div>
          </div>
        </div>
        <div className="aria-card flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-violet-500/15 flex items-center justify-center">
            <Database size={18} className="text-violet-400" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">RAG System</div>
            <div className="text-violet-400 text-xs">● {lang === "ar" ? "يعمل" : "Active"}</div>
          </div>
        </div>
      </div>

      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">{lang === "ar" ? "المستخدمون" : "Users"} ({users.length})</TabsTrigger>
          <TabsTrigger value="disputes">{lang === "ar" ? "النزاعات" : "Disputes"} ({disputes.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <div className="space-y-2">
            {users.length === 0 && (
              <div className="aria-card text-white/40 text-sm text-center py-6">
                {lang === "ar" ? "يتطلب صلاحيات المدير للعرض" : "Requires admin role to view"}
              </div>
            )}
            {users.slice(0, 50).map((u) => (
              <div key={u.id} className="aria-card flex items-center justify-between">
                <div>
                  <div className="text-white text-sm font-medium">{u.full_name_en ?? u.username}</div>
                  <div className="text-white/40 text-xs">{u.email} • {u.created_at?.slice(0, 10)}</div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={u.role === "merchant" ? "amber" : u.role === "admin" ? "destructive" : "default"}>{u.role}</Badge>
                  <Badge variant={u.is_active ? "success" : "secondary"}>{u.is_active ? "active" : "inactive"}</Badge>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="disputes">
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
                    <Badge variant={d.status === "OPEN" || d.status === "DISPUTED" ? "destructive" : "success"}>{d.status}</Badge>
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
              <div className="text-white/30 text-sm text-center py-8">
                {lang === "ar" ? "لا نزاعات مفتوحة." : "No open disputes."}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
