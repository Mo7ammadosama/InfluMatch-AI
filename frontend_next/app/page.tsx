"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Zap, ShieldCheck, Star, Rocket, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getPlatformStats } from "@/lib/api";
import { fmtNum, fmtJOD } from "@/lib/utils";
import { useApp } from "@/components/layout/providers";
import { PlatformStats } from "@/lib/types";
import { Globe } from "lucide-react";

const features = [
  {
    icon: <ShieldCheck size={22} className="text-green-400" />,
    titleEn: "Escrow Protection",
    titleAr: "حماية الدفع المسبق",
    descEn: "Funds locked until content is approved — zero risk for both parties.",
    descAr: "تُحجز الأموال حتى الموافقة على المحتوى — صفر مخاطر للطرفين.",
  },
  {
    icon: <Zap size={22} className="text-violet-400" />,
    titleEn: "ARIA AI Scoring",
    titleAr: "نقاط ARIA الذكية",
    descEn: "Every influencer scored on authenticity, reach, and engagement using AI.",
    descAr: "يُقيَّم كل مؤثر على الأصالة والوصول والتفاعل بالذكاء الاصطناعي.",
  },
  {
    icon: <Rocket size={22} className="text-amber-400" />,
    titleEn: "Smart Bookings",
    titleAr: "حجوزات ذكية",
    descEn: "End-to-end booking lifecycle with automated escrow and review.",
    descAr: "دورة حجز متكاملة مع ضمان مالي آلي ومراجعة محتوى.",
  },
];

const steps = [
  { n: 1, en: "Register & verify your account", ar: "سجّل وتحقق من حسابك" },
  { n: 2, en: "Browse AI-matched influencers", ar: "تصفح المؤثرين المُطابَقين بالذكاء الاصطناعي" },
  { n: 3, en: "Book & lock funds in escrow", ar: "احجز وجمّد الأموال في الضمان" },
  { n: 4, en: "ARIA reviews & releases payment", ar: "ARIA تراجع وتُصدر الدفعة" },
];

export default function HomePage() {
  const { lang, setLang } = useApp();
  const [stats, setStats] = useState<PlatformStats | null>(null);

  useEffect(() => {
    getPlatformStats()
      .then((r) => setStats(r.data))
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Top nav */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <span className="font-bold text-white text-lg">
            {lang === "ar" ? "وصل AI" : "WaslAI"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setLang(lang === "en" ? "ar" : "en")}
            className="flex items-center gap-1.5 text-white/50 hover:text-white text-sm transition-colors"
          >
            <Globe size={14} />
            {lang === "en" ? "عربي" : "English"}
          </button>
          <Link href="/login">
            <Button variant="outline" size="sm">
              {lang === "ar" ? "تسجيل الدخول" : "Login"}
            </Button>
          </Link>
          <Link href="/register">
            <Button size="sm">
              {lang === "ar" ? "إنشاء حساب" : "Get Started"}
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-6 pt-20 pb-16">
        <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/20 rounded-full px-4 py-1.5 text-violet-300 text-sm mb-6">
          <Zap size={14} /> {lang === "ar" ? "مدعوم بالذكاء الاصطناعي" : "AI-Powered Platform"}
        </div>
        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-4">
          {lang === "ar" ? (
            <>
              منصة التسويق عبر المؤثرين<br />
              <span className="text-violet-400">بالذكاء الاصطناعي</span>
            </>
          ) : (
            <>
              Influencer Marketing<br />
              <span className="text-violet-400">Powered by AI</span>
            </>
          )}
        </h1>
        <p className="text-lg text-white/50 max-w-xl mx-auto mb-8">
          {lang === "ar"
            ? "ربط التجار بالمؤثرين في الأردن — مع حماية مالية كاملة وتقييم ذكي"
            : "Connect merchants with influencers in Jordan — with full escrow protection and AI scoring."}
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <Link href="/register?role=merchant">
            <Button variant="merchant" size="lg" className="gap-2">
              {lang === "ar" ? "سجّل كتاجر" : "Register as Merchant"} <ArrowRight size={16} />
            </Button>
          </Link>
          <Link href="/register?role=influencer">
            <Button size="lg" className="gap-2">
              {lang === "ar" ? "سجّل كمؤثر" : "Register as Influencer"} <Star size={16} />
            </Button>
          </Link>
        </div>
      </section>

      {/* Stats */}
      {stats && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto px-6 pb-16">
          {[
            { label: lang === "ar" ? "إجمالي المستخدمين" : "Total Users", value: fmtNum(stats.total_users) },
            { label: lang === "ar" ? "المؤثرون" : "Influencers", value: fmtNum(stats.total_influencers) },
            { label: lang === "ar" ? "الحملات النشطة" : "Active Campaigns", value: fmtNum(stats.active_campaigns) },
            { label: lang === "ar" ? "المبالغ المحجوزة" : "Escrow Locked", value: fmtJOD(stats.escrow_locked) },
          ].map((s) => (
            <div key={s.label} className="kpi-block">
              <div className="text-2xl font-bold text-white">{s.value}</div>
              <div className="kpi-label">{s.label}</div>
            </div>
          ))}
        </section>
      )}

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 pb-16">
        <h2 className="text-2xl font-bold text-white text-center mb-10">
          {lang === "ar" ? "لماذا وصل AI؟" : "Why WaslAI?"}
        </h2>
        <div className="grid md:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <div key={i} className="aria-card">
              <div className="mb-3">{f.icon}</div>
              <h3 className="font-semibold text-white mb-1.5">
                {lang === "ar" ? f.titleAr : f.titleEn}
              </h3>
              <p className="text-sm text-white/50">
                {lang === "ar" ? f.descAr : f.descEn}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-3xl mx-auto px-6 pb-20">
        <h2 className="text-2xl font-bold text-white text-center mb-10">
          {lang === "ar" ? "كيف يعمل؟" : "How It Works"}
        </h2>
        <div className="space-y-4">
          {steps.map((s) => (
            <div key={s.n} className="flex items-center gap-4 aria-card">
              <div className="w-10 h-10 rounded-full bg-violet-600 flex items-center justify-center text-white font-bold flex-shrink-0">
                {s.n}
              </div>
              <div className="text-white/80 text-sm">
                {lang === "ar" ? s.ar : s.en}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
