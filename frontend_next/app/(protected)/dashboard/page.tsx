"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/components/layout/providers";
import { getDashboardPath } from "@/lib/auth";

export default function DashboardPage() {
  const { user } = useApp();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.replace(getDashboardPath(user.role));
    }
  }, [user, router]);

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-white/40 text-sm">Redirecting...</div>
    </div>
  );
}
