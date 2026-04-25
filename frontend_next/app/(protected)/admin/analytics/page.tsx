"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { getPlatformStats } from "@/lib/api";
import { PlatformStats } from "@/lib/types";
import { fmtJOD, fmtNum } from "@/lib/utils";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export default function AdminAnalyticsPage() {
  const { lang } = useApp();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPlatformStats()
      .then((r) => setStats(r.data))
      .catch(() => toast.error("Failed to load analytics"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">Loading analytics...</div>
      </div>
    );
  }

  const s = stats as Record<string, number> | null;

  const userBreakdown = [
    { name: lang === "ar" ? "تجار" : "Merchants",   value: s?.total_merchants ?? 0,  color: "#f59e0b" },
    { name: lang === "ar" ? "مؤثرون" : "Influencers", value: s?.total_influencers ?? 0, color: "#7c3aed" },
  ];

  const escrowData = [
    { name: lang === "ar" ? "محجوز" : "Locked",   value: s?.escrow_locked_jod ?? s?.escrow_locked ?? 0 },
    { name: lang === "ar" ? "محرر" : "Released",  value: (s?.total_escrow_volume_jod ?? 0) - (s?.escrow_locked_jod ?? 0) },
    { name: lang === "ar" ? "رسوم" : "Fees",      value: s?.total_platform_fees_jod ?? s?.platform_fees ?? 0 },
  ];

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="admin-banner">
        <h1 className="text-2xl font-bold text-white">
          📊 {lang === "ar" ? "تحليلات المنصة" : "Platform Analytics"}
        </h1>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiBlock label={lang === "ar" ? "المستخدمون" : "Total Users"}       value={fmtNum(s?.total_users)}        accent="violet" />
        <KpiBlock label={lang === "ar" ? "الحملات النشطة" : "Active Campaigns"} value={fmtNum(s?.active_campaigns)}   accent="green"  />
        <KpiBlock label={lang === "ar" ? "النزاعات" : "Open Disputes"}        value={s?.open_disputes ?? 0}          accent="red"    />
        <KpiBlock label={lang === "ar" ? "مستخدمون جدد اليوم" : "New Today"} value={s?.new_users_today ?? 0}        accent="blue"   />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <KpiBlock label={lang === "ar" ? "حجم الإيداع الكلي" : "Total Escrow"} value={fmtJOD(s?.total_escrow_volume_jod ?? s?.total_escrow_volume)} accent="amber" />
        <KpiBlock label={lang === "ar" ? "رسوم المنصة" : "Platform Fees"}       value={fmtJOD(s?.total_platform_fees_jod ?? s?.platform_fees)}       accent="violet" />
        <KpiBlock label={lang === "ar" ? "مبالغ محجوزة" : "Escrow Locked"}      value={fmtJOD(s?.escrow_locked_jod ?? s?.escrow_locked)}             accent="red"    />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="aria-card">
          <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "توزيع المستخدمين" : "User Breakdown"}</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={userBreakdown} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, value }) => `${name}: ${value}`}>
                {userBreakdown.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#17171f", border: "1px solid #ffffff10", borderRadius: 8 }} labelStyle={{ color: "#fff" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="aria-card">
          <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "توزيع الإيداع (JOD)" : "Escrow Breakdown (JOD)"}</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={escrowData}>
              <XAxis dataKey="name" tick={{ fill: "#ffffff50", fontSize: 11 }} />
              <YAxis tick={{ fill: "#ffffff50", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#17171f", border: "1px solid #ffffff10", borderRadius: 8 }} labelStyle={{ color: "#fff" }} />
              <Bar dataKey="value" fill="#7c3aed" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
