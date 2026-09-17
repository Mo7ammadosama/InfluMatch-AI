"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login, getMe, syncToken } from "@/lib/api";
import { setToken, setUser, getDashboardPath } from "@/lib/auth";
import { useApp } from "@/components/layout/providers";
import { toast } from "sonner";
import axios from "axios";

export default function LoginPage() {
  const router = useRouter();
  const { setUser: setCtxUser, lang } = useApp();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      // Step 1: login → get token
      const res = await login(email, password);
      const token: string = res.data.access_token;

      if (!token) {
        throw new Error("No access_token in response");
      }

      // Step 2: sync token to module cache + cookie BEFORE calling getMe
      syncToken(token);
      setToken(token);

      // Step 3: fetch user profile with the fresh token
      const meRes = await getMe();
      const user = meRes.data;

      setUser(user);
      setCtxUser(user);

      toast.success(lang === "ar" ? "مرحباً بك!" : "Welcome back!");
      router.push(getDashboardPath(user.role));
    } catch (err: unknown) {
      let msg = lang === "ar" ? "فشل تسجيل الدخول" : "Login failed";

      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        const status = err.response?.status;
        if (detail) {
          msg = typeof detail === "string" ? detail : JSON.stringify(detail);
        } else if (!err.response) {
          msg =
            lang === "ar"
              ? "لا يمكن الوصول إلى الخادم — تأكد من تشغيل الـ backend"
              : "Cannot reach server — make sure the backend is running";
        } else {
          msg = `HTTP ${status}`;
        }
      } else if (err instanceof Error) {
        msg = err.message;
      }

      setErrorMsg(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass-card p-8">
      {/* Brand */}
      <div className="flex items-center justify-center gap-2 mb-8">
        <div className="w-9 h-9 rounded-xl bg-violet-600 flex items-center justify-center">
          <Zap size={18} className="text-white" />
        </div>
        <span className="text-xl font-bold text-white">WaslAI</span>
      </div>

      <h1 className="text-2xl font-bold text-white text-center mb-1">
        {lang === "ar" ? "تسجيل الدخول" : "Welcome Back"}
      </h1>
      <p className="text-white/40 text-sm text-center mb-8">
        {lang === "ar"
          ? "أدخل بياناتك للمتابعة"
          : "Enter your credentials to continue"}
      </p>

      <form onSubmit={handleLogin} className="space-y-5">
        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "البريد الإلكتروني" : "Email"}</Label>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
          />
        </div>

        <div className="space-y-1.5">
          <Label>{lang === "ar" ? "كلمة المرور" : "Password"}</Label>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            autoComplete="current-password"
          />
        </div>

        {errorMsg && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2 text-red-400 text-xs">
            {errorMsg}
          </div>
        )}

        <Button type="submit" className="w-full" disabled={loading}>
          {loading
            ? lang === "ar"
              ? "جار تسجيل الدخول..."
              : "Signing in..."
            : lang === "ar"
            ? "تسجيل الدخول"
            : "Sign In"}
        </Button>
      </form>

      <p className="text-center text-white/40 text-sm mt-6">
        {lang === "ar" ? "ليس لديك حساب؟" : "Don't have an account?"}{" "}
        <Link href="/register" className="text-violet-400 hover:underline">
          {lang === "ar" ? "إنشاء حساب" : "Register"}
        </Link>
      </p>

      {/* Test credentials */}
      <div className="mt-6 p-3 bg-bg-overlay rounded-lg border border-white/5 text-xs space-y-2">
        <div className="font-medium text-white/50 mb-2">
          {lang === "ar" ? "حسابات تجريبية (اضغط للملء):" : "Test accounts (click to fill):"}
        </div>
        {[
          { role: lang === "ar" ? "🏪 تاجر" : "🏪 Merchant", email: "merchant@waslai.jo", password: "Test@1234" },
          { role: lang === "ar" ? "⭐ مؤثر" : "⭐ Influencer", email: "influencer@waslai.jo", password: "Test@1234" },
          { role: lang === "ar" ? "⚡ أدمن" : "⚡ Admin", email: "admin@waslai.jo", password: "Test@1234" },
        ].map((acc) => (
          <button
            key={acc.email}
            type="button"
            onClick={() => { setEmail(acc.email); setPassword(acc.password); }}
            className="w-full flex items-center justify-between px-2 py-1.5 rounded-md bg-white/5 hover:bg-white/10 transition-colors text-left cursor-pointer"
          >
            <span className="text-white/60 font-medium">{acc.role}</span>
            <span className="text-white/30">{acc.email}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
