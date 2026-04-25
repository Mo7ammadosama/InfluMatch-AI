"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { KpiBlock } from "@/components/kpi-block";
import { Button } from "@/components/ui/button";
import { getPlatformStats, triggerJob, rebuildRag, blastNotification } from "@/lib/api";
import { PlatformStats } from "@/lib/types";
import { fmtJOD, fmtNum } from "@/lib/utils";
import { toast } from "sonner";
import {
  Zap, ShieldCheck, Database, RefreshCw, BellRing,
  Bot, BarChart3, Users, Scale, Activity,
} from "lucide-react";

type JobKey = "scoring" | "escrow_release" | "reaudit";

export default function AdminPage() {
  const { lang } = useApp();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);

  // blast state
  const [blastMsg, setBlastMsg] = useState("");
  const [blastMsgEn, setBlastMsgEn] = useState("");
  const [blastRole, setBlastRole] = useState<"all" | "merchant" | "influencer">("all");
  const [blasting, setBlasting] = useState(false);

  useEffect(() => {
    getPlatformStats()
      .then((r) => setStats(r.data))
      .catch(() => toast.error("Failed to load stats"))
      .finally(() => setLoading(false));
  }, []);

  async function handleJob(job: JobKey) {
    setRunning(job);
    try {
      const r = await triggerJob(job);
      toast.success(
        (r.data?.message ?? r.data?.status ?? `Job "${job}" triggered`) + ""
      );
    } catch {
      toast.error(`Failed to trigger ${job}`);
    } finally {
      setRunning(null);
    }
  }

  async function handleRag() {
    setRunning("rag");
    try {
      const r = await rebuildRag();
      toast.success(r.data?.message ?? "RAG rebuild started");
    } catch {
      toast.error("RAG rebuild failed");
    } finally {
      setRunning(null);
    }
  }

  async function handleBlast() {
    if (!blastMsg.trim()) {
      toast.error(lang === "ar" ? "أدخل رسالة عربية على الأقل" : "Enter Arabic message");
      return;
    }
    setBlasting(true);
    try {
      await blastNotification({
        message_ar: blastMsg.trim(),
        message_en: blastMsgEn.trim() || undefined,
        target_role: blastRole,
      });
      toast.success(lang === "ar" ? "تم إرسال الإشعار!" : "Notification sent!");
      setBlastMsg("");
      setBlastMsgEn("");
    } catch {
      toast.error("Blast failed");
    } finally {
      setBlasting(false);
    }
  }

  const s = stats as Record<string, number> | null;

  const jobs: { key: JobKey; labelEn: string; labelAr: string; icon: React.ReactNode; color: string }[] = [
    { key: "scoring",       labelEn: "Run Scoring",        labelAr: "تشغيل التقييم",      icon: <BarChart3 size={16} />, color: "violet" },
    { key: "escrow_release",labelEn: "Auto Escrow Release", labelAr: "إطلاق الضمان التلقائي", icon: <Zap size={16} />,       color: "green"  },
    { key: "reaudit",       labelEn: "Re-Audit Influencers",labelAr: "إعادة تدقيق المؤثرين", icon: <ShieldCheck size={16} />, color: "amber"  },
  ];

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="admin-banner flex items-center gap-3">
        <Zap size={26} className="text-red-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">⚡ GOD MODE — ARIA Control Center</h1>
          <p className="text-white/50 text-sm mt-0.5">
            {lang === "ar" ? "لوحة التحكم الشاملة للمنصة" : "Full platform oversight & control"}
          </p>
        </div>
      </div>

      {/* KPIs */}
      {loading ? (
        <div className="text-white/30 text-sm py-4">Loading stats...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <KpiBlock label={lang === "ar" ? "المستخدمون" : "Total Users"}        value={fmtNum(s?.total_users)}       accent="violet" />
            <KpiBlock label={lang === "ar" ? "التجار" : "Merchants"}              value={fmtNum(s?.total_merchants)}    accent="amber"  />
            <KpiBlock label={lang === "ar" ? "المؤثرون" : "Influencers"}          value={fmtNum(s?.total_influencers)}  accent="violet" />
            <KpiBlock label={lang === "ar" ? "الحملات النشطة" : "Active Campaigns"} value={fmtNum(s?.active_campaigns)} accent="green"  />
            <KpiBlock label={lang === "ar" ? "النزاعات" : "Open Disputes"}        value={s?.open_disputes ?? 0}        accent="red"    />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiBlock label={lang === "ar" ? "حجم الضمان الكلي" : "Total Escrow"} value={fmtJOD(s?.total_escrow_volume_jod ?? s?.total_escrow_volume)} accent="blue"   />
            <KpiBlock label={lang === "ar" ? "رسوم المنصة" : "Platform Fees"}      value={fmtJOD(s?.total_platform_fees_jod ?? s?.platform_fees)}       accent="amber"  />
            <KpiBlock label={lang === "ar" ? "مبالغ محجوزة" : "Escrow Locked"}     value={fmtJOD(s?.escrow_locked_jod ?? s?.escrow_locked)}             accent="red"    />
            <KpiBlock label={lang === "ar" ? "مستخدمون جدد اليوم" : "New Today"}   value={s?.new_users_today ?? 0}                                      accent="green"  />
          </div>
        </>
      )}

      {/* Quick nav cards */}
      <div className="grid md:grid-cols-3 gap-4">
        {[
          { href: "/admin/users",    icon: <Users size={20} />,    labelEn: "User Management",  labelAr: "إدارة المستخدمين", color: "violet" },
          { href: "/admin/disputes", icon: <Scale size={20} />,    labelEn: "Disputes",         labelAr: "النزاعات",        color: "red"    },
          { href: "/admin/analytics",icon: <Activity size={20} />, labelEn: "Analytics",        labelAr: "التحليلات",       color: "blue"   },
        ].map((nav) => (
          <a
            key={nav.href}
            href={nav.href}
            className="aria-card flex items-center gap-3 hover:border-white/20 transition-colors group"
          >
            <div className={`w-9 h-9 rounded-lg bg-${nav.color}-500/15 flex items-center justify-center text-${nav.color}-400 group-hover:bg-${nav.color}-500/25 transition-colors`}>
              {nav.icon}
            </div>
            <span className="text-white font-medium text-sm">
              {lang === "ar" ? nav.labelAr : nav.labelEn}
            </span>
          </a>
        ))}
      </div>

      {/* Automated jobs */}
      <div className="aria-card space-y-3">
        <div className="flex items-center gap-2 mb-1">
          <Bot size={16} className="text-violet-400" />
          <h2 className="text-white font-semibold text-sm">
            {lang === "ar" ? "تشغيل الوكلاء الآلية" : "Trigger Automated Jobs"}
          </h2>
        </div>
        <div className="grid md:grid-cols-3 gap-3">
          {jobs.map((j) => (
            <Button
              key={j.key}
              variant="outline"
              disabled={running === j.key}
              onClick={() => handleJob(j.key)}
              className={`gap-2 border-${j.color}-500/30 text-${j.color}-400 hover:bg-${j.color}-500/10 hover:border-${j.color}-500/60 h-11`}
            >
              {running === j.key ? <RefreshCw size={14} className="animate-spin" /> : j.icon}
              {running === j.key
                ? (lang === "ar" ? "جار التشغيل..." : "Running...")
                : (lang === "ar" ? j.labelAr : j.labelEn)}
            </Button>
          ))}
        </div>
      </div>

      {/* RAG Rebuild */}
      <div className="aria-card flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-violet-500/15 flex items-center justify-center">
            <Database size={18} className="text-violet-400" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">RAG Knowledge Base</div>
            <div className="text-white/40 text-xs">
              {lang === "ar"
                ? "إعادة بناء قاعدة المعرفة من وثائق المنصة"
                : "Rebuild vector store from platform documents"}
            </div>
          </div>
        </div>
        <Button
          variant="outline"
          disabled={running === "rag"}
          onClick={handleRag}
          className="gap-2 border-violet-500/30 text-violet-400 hover:bg-violet-500/10 hover:border-violet-500/60"
        >
          {running === "rag" ? <RefreshCw size={14} className="animate-spin" /> : <Database size={14} />}
          {running === "rag"
            ? (lang === "ar" ? "جار البناء..." : "Rebuilding...")
            : (lang === "ar" ? "إعادة البناء" : "Rebuild RAG")}
        </Button>
      </div>

      {/* Notification blast */}
      <div className="aria-card space-y-4">
        <div className="flex items-center gap-2">
          <BellRing size={16} className="text-amber-400" />
          <h2 className="text-white font-semibold text-sm">
            {lang === "ar" ? "إشعار جماعي" : "Broadcast Notification"}
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-white/50 text-xs">
              {lang === "ar" ? "الرسالة (عربي) *" : "Message (Arabic) *"}
            </label>
            <textarea
              value={blastMsg}
              onChange={(e) => setBlastMsg(e.target.value)}
              rows={2}
              placeholder="رسالة الإشعار..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm placeholder-white/30 resize-none focus:outline-none focus:border-white/20"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-white/50 text-xs">
              {lang === "ar" ? "الرسالة (إنجليزي)" : "Message (English)"}
            </label>
            <textarea
              value={blastMsgEn}
              onChange={(e) => setBlastMsgEn(e.target.value)}
              rows={2}
              placeholder="Notification message..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm placeholder-white/30 resize-none focus:outline-none focus:border-white/20"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            {(["all", "merchant", "influencer"] as const).map((role) => (
              <button
                key={role}
                onClick={() => setBlastRole(role)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
                  blastRole === role
                    ? "border-amber-500 bg-amber-500/15 text-amber-400"
                    : "border-white/10 text-white/40 hover:border-white/20 hover:text-white/60"
                }`}
              >
                {role === "all"
                  ? lang === "ar" ? "الكل" : "All"
                  : role === "merchant"
                  ? lang === "ar" ? "التجار" : "Merchants"
                  : lang === "ar" ? "المؤثرون" : "Influencers"}
              </button>
            ))}
          </div>
          <Button
            className="ml-auto gap-2"
            disabled={blasting || !blastMsg.trim()}
            onClick={handleBlast}
          >
            <BellRing size={14} />
            {blasting
              ? (lang === "ar" ? "جار الإرسال..." : "Sending...")
              : (lang === "ar" ? "إرسال الإشعار" : "Send Blast")}
          </Button>
        </div>
      </div>
    </div>
  );
}
