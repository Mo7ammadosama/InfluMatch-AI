"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useApp } from "./providers";
import { logout } from "@/lib/auth";
import { tr } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import {
  Home, LayoutDashboard, Search, CalendarDays, ShieldCheck,
  FileText, Wallet, Settings, LogOut, Users, Megaphone,
  Scale, BarChart3, Zap, Star, Globe, Send,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  badge?: number;
}

function NavLink({ item, active }: { item: NavItem; active: boolean }) {
  return (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
        active
          ? "bg-white/10 text-white"
          : "text-white/50 hover:bg-white/5 hover:text-white/80"
      )}
    >
      <span className="flex-shrink-0">{item.icon}</span>
      <span className="flex-1">{item.label}</span>
      {item.badge != null && item.badge > 0 && (
        <span className="px-1.5 py-0.5 text-xs rounded-full bg-violet-500 text-white font-bold">
          {item.badge}
        </span>
      )}
    </Link>
  );
}

export function Sidebar({ unread = 0 }: { unread?: number }) {
  const { user, lang, setLang } = useApp();
  const pathname = usePathname();

  const role = user?.role;

  const merchantNav: NavItem[] = [
    { label: tr("dashboard", lang), href: "/merchant/dashboard", icon: <LayoutDashboard size={16} /> },
    { label: tr("campaigns", lang), href: "/campaigns", icon: <Megaphone size={16} /> },
    { label: tr("discover", lang), href: "/discover", icon: <Search size={16} /> },
    { label: tr("bookings", lang), href: "/bookings", icon: <CalendarDays size={16} />, badge: unread },
    { label: lang === "ar" ? "طلبات المنشئين" : "Creator Requests", href: "/merchant/cc-bookings", icon: <Send size={16} /> },
    { label: lang === "ar" ? "مشاركات المنشئين" : "CC Engagements", href: "/merchant/cc-engagements", icon: <Star size={16} /> },
    { label: tr("escrow", lang), href: "/escrow", icon: <ShieldCheck size={16} /> },
    { label: tr("contracts", lang), href: "/contracts", icon: <FileText size={16} /> },
    { label: tr("wallet", lang), href: "/wallet", icon: <Wallet size={16} /> },
    { label: tr("settings", lang), href: "/settings", icon: <Settings size={16} /> },
  ];

  const influencerNav: NavItem[] = [
    { label: tr("dashboard", lang), href: "/influencer/dashboard", icon: <LayoutDashboard size={16} /> },
    { label: tr("open_campaigns", lang), href: "/open-campaigns", icon: <Megaphone size={16} /> },
    { label: tr("my_campaigns", lang), href: "/campaigns", icon: <Star size={16} /> },
    { label: tr("bookings", lang), href: "/bookings", icon: <CalendarDays size={16} />, badge: unread },
    { label: tr("profile", lang), href: "/settings", icon: <Settings size={16} /> },
    { label: tr("earnings", lang), href: "/wallet", icon: <Wallet size={16} /> },
    { label: tr("contracts", lang), href: "/contracts", icon: <FileText size={16} /> },
  ];

  const adminNav: NavItem[] = [
    { label: tr("god_mode", lang), href: "/admin", icon: <Zap size={16} /> },
    { label: tr("users", lang), href: "/admin/users", icon: <Users size={16} /> },
    { label: tr("campaigns", lang), href: "/campaigns", icon: <Megaphone size={16} /> },
    { label: tr("disputes", lang), href: "/admin/disputes", icon: <Scale size={16} /> },
    { label: tr("analytics", lang), href: "/admin/analytics", icon: <BarChart3 size={16} /> },
  ];

  const creativeStrategistNav: NavItem[] = [
    { label: tr("dashboard", lang), href: "/creative-strategist/dashboard", icon: <LayoutDashboard size={16} /> },
    { label: lang === "ar" ? "أفكاري" : "My Ideas", href: "/creative-strategist/ideas", icon: <Star size={16} /> },
    { label: lang === "ar" ? "نشر فكرة" : "Submit Idea", href: "/creative-strategist/ideas/new", icon: <Zap size={16} /> },
    { label: lang === "ar" ? "المشاريع" : "Engagements", href: "/creative-strategist/dashboard", icon: <CalendarDays size={16} /> },
    { label: lang === "ar" ? "ملفي الشخصي" : "My Profile", href: "/creative-strategist/profile", icon: <Settings size={16} /> },
    { label: lang === "ar" ? "أرباحي" : "Earnings", href: "/wallet", icon: <Wallet size={16} /> },
  ];

  const contentCreatorNav: NavItem[] = [
    { label: tr("dashboard", lang), href: "/content-creator/dashboard", icon: <LayoutDashboard size={16} /> },
    { label: lang === "ar" ? "ملفي الشخصي" : "My Profile", href: "/content-creator/profile", icon: <Settings size={16} /> },
    { label: lang === "ar" ? "معرض أعمالي" : "Portfolio", href: "/content-creator/dashboard", icon: <Star size={16} /> },
    { label: lang === "ar" ? "طلبات الحجز" : "Booking Requests", href: "/content-creator/dashboard", icon: <CalendarDays size={16} /> },
    { label: lang === "ar" ? "أرباحي" : "Earnings", href: "/wallet", icon: <Wallet size={16} /> },
  ];

  const guestNav: NavItem[] = [
    { label: tr("home", lang), href: "/", icon: <Home size={16} /> },
    { label: tr("login", lang), href: "/login", icon: <LogOut size={16} /> },
    { label: tr("register", lang), href: "/register", icon: <Users size={16} /> },
  ];

  const navItems =
    role === "merchant"
      ? merchantNav
      : role === "influencer"
      ? influencerNav
      : role === "admin"
      ? adminNav
      : role === "creative_strategist"
      ? creativeStrategistNav
      : role === "content_creator"
      ? contentCreatorNav
      : guestNav;

  const roleColor =
    role === "merchant"
      ? "text-amber-400"
      : role === "influencer"
      ? "text-violet-400"
      : role === "admin"
      ? "text-red-400"
      : role === "creative_strategist"
      ? "text-emerald-400"
      : role === "content_creator"
      ? "text-pink-400"
      : "text-blue-400";

  const roleBg =
    role === "merchant"
      ? "bg-amber-500/10 border-amber-500/20"
      : role === "influencer"
      ? "bg-violet-500/10 border-violet-500/20"
      : role === "admin"
      ? "bg-red-500/10 border-red-500/20"
      : role === "creative_strategist"
      ? "bg-emerald-500/10 border-emerald-500/20"
      : role === "content_creator"
      ? "bg-pink-500/10 border-pink-500/20"
      : "bg-blue-500/10 border-blue-500/20";

  return (
    <aside className="w-64 min-h-screen bg-bg-surface border-r border-white/5 flex flex-col">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-violet-600 flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-white text-sm">WaslAI</div>
            <div className="text-[10px] text-white/40 uppercase tracking-widest">
              {lang === "ar" ? "منصة المؤثرين" : "Influencer Platform"}
            </div>
          </div>
        </div>
      </div>

      {/* User card */}
      {user && (
        <div className={cn("mx-3 mt-3 px-3 py-2.5 rounded-lg border", roleBg)}>
          <div className="text-white text-sm font-semibold truncate">
            {lang === "ar" ? (user.full_name_ar ?? user.full_name) : (user.full_name_en ?? user.full_name)}
          </div>
          <div className={cn("text-xs font-medium capitalize mt-0.5", roleColor)}>
            {user.role.replace("_", " ")} • {user.username ?? user.email.split("@")[0]}
          </div>
        </div>
      )}

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            active={pathname === item.href || pathname.startsWith(item.href + "/")}
          />
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 py-3 border-t border-white/5 space-y-1">
        {/* Language toggle */}
        <button
          onClick={() => setLang(lang === "en" ? "ar" : "en")}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-white/50 hover:bg-white/5 hover:text-white/80 text-sm transition-colors"
        >
          <Globe size={16} />
          <span>{lang === "en" ? "عربي" : "English"}</span>
        </button>

        {user && (
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-400/70 hover:bg-red-500/10 hover:text-red-400 text-sm transition-colors"
          >
            <LogOut size={16} />
            <span>{tr("logout", lang)}</span>
          </button>
        )}
      </div>
    </aside>
  );
}
