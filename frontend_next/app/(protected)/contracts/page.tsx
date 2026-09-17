"use client";
// updated
import { useState, useEffect } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { generateContract, policyQA, getCampaigns } from "@/lib/api";
import { Campaign } from "@/lib/types";
import { toast } from "sonner";
import { FileText, Zap, Download, Copy, Check } from "lucide-react";

export default function ContractsPage() {
  const { lang } = useApp();
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [form, setForm] = useState({
    campaign_id: "",
    merchant_name: "",
    influencer_name: "",
    campaign_title: "",
    agreed_amount_jod: "",
    deliverables: "",
    deadline: "",
  });
  const [copied, setCopied] = useState(false);
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

  function handleCampaignChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const id = e.target.value;
    const c = campaigns.find((c) => String(c.id) === id);
    setForm((f) => ({
      ...f,
      campaign_id: id,
      campaign_title: c ? (lang === "ar" ? c.title_ar ?? c.title : c.title) : f.campaign_title,
      agreed_amount_jod: c?.total_budget_jod != null ? String(c.total_budget_jod) : f.agreed_amount_jod,
      deadline: c?.end_date ? c.end_date.slice(0, 10) : f.deadline,
    }));
  }

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.merchant_name || !form.influencer_name || !form.campaign_title || !form.agreed_amount_jod) {
      toast.error(lang === "ar" ? "أدخل جميع الحقول المطلوبة" : "Fill all required fields");
      return;
    }
    setGenerating(true);
    try {
      const payload: Record<string, unknown> = {
        merchant_name: form.merchant_name,
        influencer_name: form.influencer_name,
        campaign_title: form.campaign_title,
        agreed_amount_jod: parseFloat(form.agreed_amount_jod),
        language: lang,
      };
      if (form.deliverables.trim()) payload.deliverables = form.deliverables.trim();
      if (form.deadline.trim()) payload.deadline = form.deadline.trim();
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
              onChange={handleCampaignChange}
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

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "عنوان الحملة" : "Campaign Title"} *</Label>
              <Input value={form.campaign_title} onChange={(e) => setForm((f) => ({ ...f, campaign_title: e.target.value }))} placeholder={lang === "ar" ? "مثال: رمضان 2025" : "e.g. Ramadan 2025"} required />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "المبلغ المتفق عليه (JOD)" : "Agreed Amount (JOD)"} *</Label>
              <Input type="number" min="0" step="0.01" value={form.agreed_amount_jod} onChange={(e) => setForm((f) => ({ ...f, agreed_amount_jod: e.target.value }))} placeholder="500" required />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "المستحقات (اختياري)" : "Deliverables (optional)"}</Label>
              <Input value={form.deliverables} onChange={(e) => setForm((f) => ({ ...f, deliverables: e.target.value }))} placeholder={lang === "ar" ? "مثال: 3 ريلز، 5 ستوريز" : "e.g. 3 Reels, 5 Stories"} />
            </div>
            <div className="space-y-1.5">
              <Label>{lang === "ar" ? "الموعد النهائي (اختياري)" : "Deadline (optional)"}</Label>
              <Input type="date" value={form.deadline} onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))} />
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
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                className="gap-1"
                onClick={() => {
                  navigator.clipboard.writeText(contractText);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2000);
                }}
              >
                {copied ? <Check size={13} className="text-green-400" /> : <Copy size={13} />}
                {lang === "ar" ? "نسخ العقد" : "Copy Contract"}
              </Button>
              <Button size="sm" variant="outline" onClick={downloadTxt} className="gap-1">
                <Download size={13} /> {lang === "ar" ? "تحميل TXT" : "Download TXT"}
              </Button>
            </div>
          </div>
          <pre className="text-white/70 text-xs font-mono whitespace-pre-wrap leading-relaxed max-h-[600px] overflow-y-auto bg-black/40 border border-white/10 rounded-lg p-5">
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
