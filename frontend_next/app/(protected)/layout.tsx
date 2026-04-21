"use client";

import { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { Chatbot } from "@/components/chatbot";
import { getUnreadCount } from "@/lib/api";
import { useApp } from "@/components/layout/providers";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { lang } = useApp();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    getUnreadCount()
      .then((r) => setUnread(r.data?.unread_count ?? r.data?.count ?? 0))
      .catch(() => {});
  }, []);

  // Sidebar on the right in RTL
  const isRtl = lang === "ar";

  return (
    <div className={`flex min-h-screen ${isRtl ? "flex-row-reverse" : "flex-row"}`}>
      <Sidebar unread={unread} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar unread={unread} />
        <main className="flex-1 p-6 page-enter overflow-y-auto">{children}</main>
      </div>
      <Chatbot />
    </div>
  );
}
