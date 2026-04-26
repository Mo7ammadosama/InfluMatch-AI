"use client";

import { useApp } from "./providers";
import { Bell, MessageSquare } from "lucide-react";
import { useRouter } from "next/navigation";

export function Navbar({ unread = 0 }: { unread?: number }) {
  const { user, lang } = useApp();
  const router = useRouter();

  return (
    <header className="h-14 bg-bg-surface/80 backdrop-blur border-b border-white/5 flex items-center justify-between px-6 sticky top-0 z-30">
      <div />
      <div className="flex items-center gap-3">
        {unread > 0 && (
          <button
            onClick={() => router.push("/bookings")}
            className="relative p-2 rounded-lg hover:bg-white/5 transition-colors"
            title={lang === "ar" ? "الرسائل غير المقروءة" : "Unread messages"}
          >
            <MessageSquare size={18} className="text-white/50" />
            <span className="absolute top-1 right-1 w-4 h-4 text-[10px] font-bold bg-violet-500 text-white rounded-full flex items-center justify-center">
              {unread}
            </span>
          </button>
        )}
        <button
          onClick={() => router.push("/bookings")}
          className="relative p-2 rounded-lg hover:bg-white/5 transition-colors"
          title={lang === "ar" ? "الحجوزات" : "Bookings"}
        >
          <Bell size={18} className="text-white/50" />
          {unread > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-violet-500 rounded-full" />
          )}
        </button>
        {user && (
          <div className="flex items-center gap-2 pl-2 border-l border-white/10">
            <div className="w-7 h-7 rounded-full bg-violet-600 flex items-center justify-center text-white text-xs font-bold">
              {((lang === "ar" ? user.full_name_ar : user.full_name_en) ?? user.username)
                ?.charAt(0)
                ?.toUpperCase() ?? "U"}
            </div>
            <span className="text-sm text-white/70">
              {(lang === "ar" ? user.full_name_ar : user.full_name_en) ?? user.username}
            </span>
          </div>
        )}
      </div>
    </header>
  );
}
