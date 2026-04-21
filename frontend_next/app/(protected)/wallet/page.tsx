"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { TierBadge } from "@/components/tier-badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getWallet, redeemPoints } from "@/lib/api";
import { Tier } from "@/lib/types";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";

function getNextTierInfo(tier: string, points: number) {
  if (tier === "BRONZE") return { next: "SILVER", needed: Math.max(0, 1000 - points), max: 1000 };
  if (tier === "SILVER") return { next: "GOLD", needed: Math.max(0, 5000 - points), max: 4000 };
  if (tier === "GOLD") return { next: "PLATINUM", needed: Math.max(0, 20000 - points), max: 15000 };
  return null;
}

export default function WalletPage() {
  const { user, lang } = useApp();
  const [walletRaw, setWalletRaw] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [redeemAmt, setRedeemAmt] = useState("");
  const [redeeming, setRedeeming] = useState(false);

  async function load() {
    const r = await getWallet();
    setWalletRaw(r.data);
  }

  useEffect(() => {
    load().catch(() => toast.error("Failed to load wallet")).finally(() => setLoading(false));
  }, []);

  async function handleRedeem(e: React.FormEvent) {
    e.preventDefault();
    const pts = parseInt(redeemAmt);
    if (isNaN(pts) || pts < 500) {
      toast.error(lang === "ar" ? "الحد الأدنى 500 نقطة" : "Minimum 500 points");
      return;
    }
    setRedeeming(true);
    try {
      await redeemPoints(pts);
      toast.success(lang === "ar" ? "تم الاسترداد!" : "Points redeemed!");
      await load();
      setRedeemAmt("");
    } catch {
      toast.error(lang === "ar" ? "فشل الاسترداد" : "Redemption failed");
    } finally {
      setRedeeming(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  // Backend returns tier as {tier: "BRONZE", emoji: "...", discount: 0.05}
  const tierObj = walletRaw?.tier as { tier?: string } | string | undefined;
  const tier: Tier = ((typeof tierObj === "object" ? tierObj?.tier : tierObj) ?? "BRONZE") as Tier;
  const available = (walletRaw?.available_points as number) ?? 0;
  const total = (walletRaw?.total_points as number) ?? 0;
  const redeemed = (walletRaw?.redeemed_points as number) ?? 0;
  const jodValue = (walletRaw?.jod_value as number) ?? available * 0.001;

  const nextTierInfo = getNextTierInfo(tier, available);
  const progressPct = nextTierInfo
    ? Math.min(100, ((nextTierInfo.max - nextTierInfo.needed) / nextTierInfo.max) * 100)
    : 100;
  const previewJOD = parseInt(redeemAmt) > 0 ? parseInt(redeemAmt) * 0.001 : 0;
  const bannerClass = user?.role === "merchant" ? "merchant-banner" : "influencer-banner";

  return (
    <div className="space-y-6 max-w-3xl">
      <div className={bannerClass}>
        <h1 className="text-2xl font-bold text-white">💎 {lang === "ar" ? "المحفظة والمكافآت" : "Wallet & Rewards"}</h1>
      </div>

      <div className="aria-card text-center">
        <div className="flex items-center justify-center mb-3">
          <TierBadge tier={tier} />
        </div>
        <div className="text-5xl font-extrabold text-white mb-1">{available.toLocaleString()}</div>
        <div className="text-white/40 text-sm mb-2">{lang === "ar" ? "النقاط المتاحة" : "Available Points"}</div>
        <div className="text-violet-400 font-semibold text-lg">{fmtJOD(jodValue)}</div>

        {nextTierInfo && (
          <div className="mt-5">
            <div className="flex justify-between text-xs text-white/40 mb-1.5">
              <span>{tier}</span>
              <span>{nextTierInfo.needed.toLocaleString()} {lang === "ar" ? "نقطة للـ" : "pts to"} {nextTierInfo.next}</span>
            </div>
            <Progress value={progressPct} />
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="kpi-block">
          <div className="kpi-value text-green-400">{total.toLocaleString()}</div>
          <div className="kpi-label">{lang === "ar" ? "إجمالي المكتسب" : "Total Earned"}</div>
        </div>
        <div className="kpi-block">
          <div className="kpi-value text-amber-400">{redeemed.toLocaleString()}</div>
          <div className="kpi-label">{lang === "ar" ? "المسترد" : "Redeemed"}</div>
        </div>
        <div className="kpi-block">
          <div className="kpi-value text-violet-400">{fmtJOD(jodValue)}</div>
          <div className="kpi-label">{lang === "ar" ? "القيمة النقدية" : "Cash Value"}</div>
        </div>
      </div>

      <div className="aria-card">
        <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "استرداد النقاط" : "Redeem Points"}</h3>
        <form onSubmit={handleRedeem} className="space-y-4">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "عدد النقاط (الحد الأدنى 500)" : "Points (min 500)"}</Label>
            <Input type="number" value={redeemAmt} onChange={(e) => setRedeemAmt(e.target.value)} placeholder="500" min={500} max={available} />
            {previewJOD > 0 && (
              <div className="text-violet-400 text-sm">= {fmtJOD(previewJOD)} {lang === "ar" ? "خصم" : "discount"}</div>
            )}
          </div>
          <Button type="submit" disabled={redeeming || available < 500}>
            {redeeming ? (lang === "ar" ? "جار الاسترداد..." : "Redeeming...") : (lang === "ar" ? "استرداد" : "Redeem")}
          </Button>
        </form>
      </div>
    </div>
  );
}
