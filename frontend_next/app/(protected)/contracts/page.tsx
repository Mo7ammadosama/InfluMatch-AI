"use client";

import { useState, useEffect } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { generateContract, policyQA, getCampaigns } from "@/lib/api";
import { Campaign } from "@/lib/types";
import { toast } from "sonner";
import { FileText, Zap, Download } from "lucide-react";

export default function ContractsPage() {
  const { lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [form, setForm] = useState({ campaign_id: "", merchant_name: "", influencer_name: "" });
  const [contractText, setContractText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [policyQ, setPolicyQ] = useState("");
  const [policyAnswer, setPolicyAnswer] = useState("");
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    getCampaigns()
      .then((r) => setCampaigns(Array.isArray(r.data) ? r.data : (r.data?.data ?? [])))
      .catch(() => {});
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.merchant_name || !form.influencer_name) {
      toast.error(lang === "ar" ? "أدخل أسماء التاجر والمؤثر" : "Enter merchant and influencer names");
      return;
    }
    setGenerating(true);
    try {
      const selectedCampaign = campaigns.find((c) => String(c.id) === form.campaign_id);
      const payload = {
        merchant_name: form.merchant_name,
        influencer_name: form.influencer_name,
        language: lang,
        campaign_details: selectedCampaign
          ? {
              campaign_id: selectedCampaign.id,
              title: lang === "ar" ? selectedCampaign.title_ar : selectedCampaign.title,
              budget: selectedCampaign.total_budget_jod,
              niche: selectedCampaign.target_categories?.[0],
              end_date: selectedCampaign.end_date,
            }
          : { title: "General Campaign" },
      };
      const r = await generateContract(payload);
      const text = r.data?.contract_text ?? r.data?.contract_text_en ?? r.data?.contract_text_ar ?? JSON.stringify(r.data, null, 2);
      setContractText(text);
      toast.success(lang === "ar" ? "تم إنشاء العقد!" : "Contract generated!");
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : (lang === "ar" ? "فشل الإنشاء — الخدمة غير متاحة مؤقتاً" : "Generation failed — service temporarily unavailable"));
    } finally {
      setGenerating(false);
    }
  }

  async function handlePolicyQA(e: React.FormEvent) {
    e.preventDefault();
    if (!policyQ.trim()) return;
    setAsking(true);
    try {
      const r = await policyQA(policyQ, lang);
      setPolicyAnswer(r.data?.answer ?? r.data?.response ?? "");
    } catch {
      toast.error(lang === "ar" ? "خدمة الأسئلة غير متاحة مؤقتاً" : "Q&A service temporarily unavailable");
    } finally {
      setAsking(false);
    }
  }

  function downloadTxt() {
    if (!contractText) return;
    const blob = new Blob([contractText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `waslai_contract.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="merchant-banner flex items-center gap-3">
        <FileText size={22} className="text-amber-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">{lang === "ar" ? "📄 العقود الذكية" : "📄 Smart Contracts"}</h1>
          <p className="text-white/50 text-sm mt-0.5">{lang === "ar" ? "إنشاء عقود قانونية بالذكاء الاصطناعي" : "AI-generated legal contracts via ARIA RAG"}</p>
        </div>
      </div>

      <div className="aria-card">
        <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "مولّد العقود" : "Contract Generator"}</h3>
        <form onSubmit={handleGenerate} className="space-y-4">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الحملة (اختياري)" : "Campaign (optional)"}</Label>
            <select
              value={form.campaign_id}
              onChange={(e) => setForm((f) => ({ ...f, campaign_id: e.target.value }))}
              className="flex h-9 w-full rounded-lg border border-white/10 bg-bg-overlay px-3 text-sm text-white focus:outline-none focus:ring-1 focus:ring-violet-500"
            >
              <option value="">{lang === "ar" ? "— بدون حملة —" : "— No Campaign —"}</option>
              {campaigns.map((c) => (
                <option key={c.id} value={c.id}>{lang === "ar" ? c.title_ar ?? c.title : c.title}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "اسم التاجر" : "Merchant Name"} *</Label>
              <Input value={form.merchant_name} onChange={(e) => setForm((f) => ({ ...f, merchant_name: e.target.value }))} placeholder="Business Name" required />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "اسم المؤثر" : "Influencer Name"} *</Label>
              <Input value={form.influencer_name} onChange={(e) => setForm((f) => ({ ...f, influencer_name: e.target.value }))} placeholder="@handle" required />
            </div>
          </div>

          <Button type="submit" disabled={generating} className="gap-2">
            <Zap size={14} />
            {generating ? (lang === "ar" ? "جار الإنشاء..." : "Generating...") : (lang === "ar" ? "إنشاء العقد عبر ARIA RAG" : "Generate Contract via ARIA RAG")}
          </Button>
        </form>
      </div>

      {contractText && (
        <div className="aria-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">{lang === "ar" ? "العقد المُنشأ" : "Generated Contract"}</h3>
            <Button size="sm" variant="outline" onClick={downloadTxt} className="gap-1">
              <Download size={13} /> {lang === "ar" ? "تحميل TXT" : "Download TXT"}
            </Button>
          </div>
          <pre className="text-white/70 text-xs whitespace-pre-wrap leading-relaxed max-h-96 overflow-y-auto bg-bg-overlay rounded-lg p-4">
            {contractText}
          </pre>
        </div>
      )}

      <div className="aria-card">
        <h3 className="font-semibold text-white mb-4">{lang === "ar" ? "اسأل ARIA عن سياسات المنصة" : "Ask ARIA about Platform Policies"}</h3>
        <form onSubmit={handlePolicyQA} className="space-y-3">
          <Input
            value={policyQ}
            onChange={(e) => setPolicyQ(e.target.value)}
            placeholder={lang === "ar" ? "مثل: ما هي سياسة رفع النزاعات؟" : "e.g. What is the dispute resolution policy?"}
          />
          <Button type="submit" variant="outline" disabled={asking} className="gap-2">
            <Zap size={14} />
            {asking ? (lang === "ar" ? "جار البحث..." : "Searching...") : (lang === "ar" ? "سؤال ARIA" : "Ask ARIA")}
          </Button>
        </form>
        {policyAnswer && (
          <div className="mt-4 p-4 bg-bg-overlay rounded-lg text-white/70 text-sm leading-relaxed">{policyAnswer}</div>
        )}
      </div>
    </div>
  );
}
