"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { getWallet, getWalletTransactions } from "@/lib/api";
import { fmtJOD } from "@/lib/utils";
import { toast } from "sonner";
import { Wallet, ArrowDownLeft, ArrowUpRight, Lock } from "lucide-react";

interface WalletData {
  available_balance_jod: number;
  locked_balance_jod: number;
  total_balance_jod: number;
  points_balance: number;
  total_points_earned: number;
  points_to_jod_rate: number;
}

interface TxData {
  id: string;
  transaction_type: string;
  amount_jod: number;
  description: string | null;
  created_at: string;
}

export default function WalletPage() {
  const { user, lang } = useApp();
  const [wallet, setWalletData] = useState<WalletData | null>(null);
  const [txs, setTxs] = useState<TxData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getWallet().then((r) => setWalletData(r.data)),
      getWalletTransactions().then((r) => setTxs(Array.isArray(r.data) ? r.data : [])),
    ])
      .catch(() => toast.error(lang === "ar" ? "فشل تحميل المحفظة" : "Failed to load wallet"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">{lang === "ar" ? "جار التحميل..." : "Loading..."}</div>
      </div>
    );
  }

  if (!wallet) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/30 text-sm text-center">
          <Wallet size={32} className="mx-auto mb-3 opacity-30" />
          {lang === "ar" ? "لا توجد محفظة — سجّل دخولك مجدداً" : "No wallet found — try logging in again"}
        </div>
      </div>
    );
  }

  const bannerClass = user?.role === "merchant" ? "merchant-banner" : user?.role === "creative_strategist" ? "influencer-banner" : "influencer-banner";

  const txIcon = (type: string) => {
    if (type === "credit" || type === "escrow_release") return <ArrowDownLeft size={14} className="text-green-400" />;
    if (type === "debit" || type === "escrow_lock" || type === "platform_fee") return <ArrowUpRight size={14} className="text-red-400" />;
    return <Lock size={14} className="text-amber-400" />;
  };

  const txColor = (type: string) => {
    if (type === "credit" || type === "escrow_release") return "text-green-400";
    if (type === "debit" || type === "escrow_lock" || type === "platform_fee") return "text-red-400";
    return "text-amber-400";
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div className={bannerClass}>
        <h1 className="text-2xl font-bold text-white">💳 {lang === "ar" ? "المحفظة" : "My Wallet"}</h1>
        <p className="text-white/50 text-sm mt-1">
          {lang === "ar" ? "رصيدك وسجل المعاملات" : "Your balance and transaction history"}
        </p>
      </div>

      {/* Balance cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="kpi-block col-span-1">
          <div className="kpi-value text-green-400">{fmtJOD(wallet.available_balance_jod)}</div>
          <div className="kpi-label">{lang === "ar" ? "الرصيد المتاح" : "Available"}</div>
        </div>
        <div className="kpi-block col-span-1">
          <div className="kpi-value text-amber-400">{fmtJOD(wallet.locked_balance_jod)}</div>
          <div className="kpi-label">{lang === "ar" ? "محجوز في Escrow" : "In Escrow"}</div>
        </div>
        <div className="kpi-block col-span-1">
          <div className="kpi-value text-white">{fmtJOD(wallet.total_balance_jod)}</div>
          <div className="kpi-label">{lang === "ar" ? "الإجمالي" : "Total Balance"}</div>
        </div>
      </div>

      {/* Points */}
      <div className="aria-card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-3xl font-bold text-violet-400">{wallet.points_balance.toLocaleString()}</div>
            <div className="text-white/40 text-sm">{lang === "ar" ? "نقاط الولاء المتاحة" : "Loyalty Points Available"}</div>
          </div>
          <div className="text-right">
            <div className="text-white/60 text-sm">{wallet.total_points_earned.toLocaleString()}</div>
            <div className="text-white/30 text-xs">{lang === "ar" ? "إجمالي النقاط المكتسبة" : "Total Earned"}</div>
          </div>
        </div>
        <div className="mt-3 text-xs text-white/30">
          {lang === "ar"
            ? `معدل الاستبدال: ${wallet.points_to_jod_rate} JOD / نقطة`
            : `Redemption rate: ${wallet.points_to_jod_rate} JOD / point`}
        </div>
      </div>

      {/* Transactions */}
      <div className="aria-card">
        <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "سجل المعاملات" : "Transaction History"}</h3>
        {txs.length === 0 ? (
          <div className="text-white/30 text-sm text-center py-6">
            {lang === "ar" ? "لا توجد معاملات بعد" : "No transactions yet"}
          </div>
        ) : (
          <div className="space-y-2">
            {txs.map((tx) => (
              <div key={tx.id} className="flex items-center justify-between py-2.5 border-b border-white/5 last:border-0">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-white/5 flex items-center justify-center">
                    {txIcon(tx.transaction_type)}
                  </div>
                  <div>
                    <div className="text-white/80 text-xs font-medium capitalize">
                      {tx.transaction_type.replace(/_/g, " ")}
                    </div>
                    {tx.description && (
                      <div className="text-white/30 text-xs">{tx.description}</div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-semibold ${txColor(tx.transaction_type)}`}>
                    {tx.amount_jod >= 0 ? "+" : ""}{fmtJOD(tx.amount_jod)}
                  </div>
                  <div className="text-white/30 text-xs">
                    {new Date(tx.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
