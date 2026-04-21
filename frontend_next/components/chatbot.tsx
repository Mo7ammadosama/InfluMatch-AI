"use client";

import { useState } from "react";
import { MessageSquare, X, Send, Zap } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { askChatbot } from "@/lib/api";
import { useApp } from "./layout/providers";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function Chatbot() {
  const { lang } = useApp();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    const msg = input.trim();
    if (!msg || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const res = await askChatbot(msg, lang);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.response ?? res.data.answer ?? "..." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: lang === "ar" ? "حدث خطأ." : "An error occurred." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full bg-violet-600 hover:bg-violet-500 text-white shadow-glow flex items-center justify-center transition-all"
      >
        {open ? <X size={20} /> : <MessageSquare size={20} />}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-20 right-6 z-50 w-80 bg-bg-overlay border border-white/10 rounded-xl shadow-aria flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-white/10 bg-violet-600/20">
            <Zap size={16} className="text-violet-400" />
            <span className="text-sm font-semibold text-white">
              {lang === "ar" ? "وصل AI GPT" : "WaslAI GPT"}
            </span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2 max-h-72">
            {messages.length === 0 && (
              <div className="text-white/30 text-xs text-center mt-4">
                {lang === "ar" ? "اسألني أي شيء..." : "Ask me anything..."}
              </div>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={cn(
                  "text-sm px-3 py-2 rounded-lg max-w-[90%]",
                  m.role === "user"
                    ? "bg-violet-600/30 text-white ml-auto"
                    : "bg-bg-raised text-white/80"
                )}
              >
                {m.content}
              </div>
            ))}
            {loading && (
              <div className="bg-bg-raised text-white/50 text-xs px-3 py-2 rounded-lg w-fit">
                ...
              </div>
            )}
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 p-3 border-t border-white/10">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder={lang === "ar" ? "اكتب سؤالك..." : "Type a message..."}
              className="flex-1 h-8 text-xs"
            />
            <Button size="icon" className="h-8 w-8 flex-shrink-0" onClick={send}>
              <Send size={14} />
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
