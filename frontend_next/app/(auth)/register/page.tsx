"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register, login, getMe, syncToken } from "@/lib/api";
import { setToken, setUser, getDashboardPath } from "@/lib/auth";
import { useApp } from "@/components/layout/providers";
import { toast } from "sonner";

function RegisterForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { setUser: setCtxUser, lang } = useApp();

  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    full_name_en: "",
    full_name_ar: "",
    phone: "",
    role: params.get("role") ?? "merchant",
  });
  const [loading, setLoading] = useState(false);

  function update(k: string, v: string) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      const loginRes = await login(form.email, form.password);
      const token: string = loginRes.data.access_token;
      syncToken(token);
      setToken(token);
      const meRes = await getMe();
      const user = meRes.data;
      setUser(user);
      setCtxUser(user);
      toast.success(lang === "ar" ? "تم إنشاء حسابك!" : "Account created!");
      router.push(getDashboardPath(user.role));
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? (lang === "ar" ? "فشل التسجيل" : "Registration failed");
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card p-8">
      <div className="flex items-center justify-center gap-2 mb-6">
        <div className="w-9 h-9 rounded-xl bg-violet-600 flex items-center justify-center">
          <Zap size={18} className="text-white" />
        </div>
        <span className="text-xl font-bold text-white">WaslAI</span>
      </div>

      <h1 className="text-2xl font-bold text-white text-center mb-1">
        {lang === "ar" ? "إنشاء حساب" : "Create Account"}
      </h1>
      <p className="text-white/40 text-sm text-center mb-6">
        {lang === "ar" ? "انضم إلى منصة المؤثرين" : "Join the influencer platform"}
      </p>

      {/* Role toggle */}
      <div className="flex rounded-lg bg-bg-overlay p-1 mb-6">
        {["merchant", "influencer"].map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => update("role", r)}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
              form.role === r
                ? r === "merchant"
                  ? "bg-amber-500 text-black"
                  : "bg-violet-600 text-white"
                : "text-white/40 hover:text-white/70"
            }`}
          >
            {r === "merchant"
              ? lang === "ar"
                ? "🏪 تاجر"
                : "🏪 Merchant"
              : lang === "ar"
              ? "🌟 مؤثر"
              : "🌟 Influencer"}
          </button>
        ))}
      </div>

      <form onSubmit={handleRegister} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الاسم (EN)" : "Name (EN)"}</Label>
            <Input
              value={form.full_name_en}
              onChange={(e) => update("full_name_en", e.target.value)}
              placeholder="John Doe"
            />
          </div>
          <div className="space-y-1.5">
            <Label>{lang === "ar" ? "الاسم (AR)" : "Name (AR)"}</Label>
            <Input
              value={form.full_name_ar}
              onChange={(e) => update("full_name_ar", e.target.value)}
              placeholder="جون دو"
              dir="rtl"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "اسم المستخدم" : "Username"}</Label>
          <Input
            value={form.username}
            onChange={(e) => update("username", e.target.value)}
            placeholder="username"
            required
          />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "البريد الإلكتروني" : "Email"}</Label>
          <Input
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            placeholder="you@example.com"
            required
          />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "رقم الهاتف" : "Phone"}</Label>
          <Input
            value={form.phone}
            onChange={(e) => update("phone", e.target.value)}
            placeholder="+962 7x xxx xxxx"
          />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "كلمة المرور" : "Password"}</Label>
          <Input
            type="password"
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            placeholder="Min 8 characters"
            required
          />
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading
            ? lang === "ar"
              ? "جار الإنشاء..."
              : "Creating account..."
            : lang === "ar"
            ? "إنشاء الحساب"
            : "Create Account"}
        </Button>
      </form>

      <p className="text-center text-white/40 text-sm mt-5">
        {lang === "ar" ? "لديك حساب؟" : "Already have an account?"}{" "}
        <Link href="/login" className="text-violet-400 hover:underline">
          {lang === "ar" ? "تسجيل الدخول" : "Login"}
        </Link>
      </p>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="glass-card p-8 text-white/40 text-sm text-center">Loading...</div>}>
      <RegisterForm />
    </Suspense>
  );
}
