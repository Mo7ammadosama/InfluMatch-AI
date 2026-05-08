"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Toaster } from "sonner";
import { User } from "@/lib/types";
import { getUser, getToken, setUser as storeUser } from "@/lib/auth";
import { getMe } from "@/lib/api";
import { Lang } from "@/lib/i18n";

interface AppContextType {
  user: User | null;
  setUser: (u: User | null) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
}

const AppContext = createContext<AppContextType>({
  user: null,
  setUser: () => {},
  lang: "en",
  setLang: () => {},
});

export function useApp() {
  return useContext(AppContext);
}

function applyLang(l: Lang) {
  document.documentElement.dir = l === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = l;
  // swap font for Arabic
  document.documentElement.style.fontFamily =
    l === "ar"
      ? "'Cairo', system-ui, sans-serif"
      : "'Inter', 'Cairo', system-ui, sans-serif";
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [lang, setLangState] = useState<Lang>("en");

  // Restore persisted state on first mount
  useEffect(() => {
    const u = getUser();
    if (u) setUserState(u);

    const saved = (localStorage.getItem("waslai_lang") as Lang) || "en";
    setLangState(saved);
    applyLang(saved);

    // Always sync with server — prevents stale role data when switching accounts
    const token = getToken();
    if (token) {
      getMe()
        .then((r) => { setUser(r.data); })
        .catch(() => {});
    }
  }, []);

  // Apply direction/font on every lang change
  useEffect(() => {
    applyLang(lang);
  }, [lang]);

  function setUser(u: User | null) {
    setUserState(u);
    if (u) storeUser(u);
  }

  function setLang(l: Lang) {
    setLangState(l);
    localStorage.setItem("waslai_lang", l);
  }

  return (
    <AppContext.Provider value={{ user, setUser, lang, setLang }}>
      {children}
      <Toaster
        theme="dark"
        position="bottom-right"
        toastOptions={{
          style: {
            background: "#17171f",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "#e8e8f0",
          },
        }}
      />
    </AppContext.Provider>
  );
}
