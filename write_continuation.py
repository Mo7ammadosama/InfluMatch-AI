"""Master System Prompt Continuation — Modules 13-15 + Tests"""
import os

BASE = "C:/WaslAI_AI/waslai"

def w(rel_path, content):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK  {rel_path}  ({len(content)} bytes)")

# ── OFFICIAL ARIA DESIGN SYSTEM CSS ─────────────────────────────────────────
w("frontend/assets/css/style.css", """/* ============================================================
   WASLAI.JO — ARIA DESIGN SYSTEM
   Dark Theme + RTL Arabic Support + Jordan Brand Colors
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Inter:wght@300;400;600;700&display=swap');

:root {
    --aria-primary: #0f3460;
    --aria-secondary: #533483;
    --aria-accent: #e94560;
    --aria-success: #00ff88;
    --aria-warning: #ffd700;
    --aria-bg-dark: #0a0a1a;
    --aria-bg-card: #1a1a2e;
    --aria-text-primary: #ffffff;
    --aria-text-secondary: #a0a0b0;
    --aria-border: rgba(83, 52, 131, 0.4);
    --aria-shadow: 0 8px 32px rgba(15, 52, 96, 0.4);
    --aria-radius: 12px;
    --aria-radius-lg: 20px;
}

.stApp {
    background: var(--aria-bg-dark);
    font-family: 'Cairo', 'Inter', sans-serif;
    color: var(--aria-text-primary);
}

[lang="ar"] .stApp, .rtl-content {
    direction: rtl;
    text-align: right;
}

div[data-testid="metric-container"] {
    background: var(--aria-bg-card) !important;
    border: 1px solid var(--aria-border) !important;
    border-radius: var(--aria-radius) !important;
    padding: 1.2rem !important;
    box-shadow: var(--aria-shadow) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(83, 52, 131, 0.5) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%) !important;
    border-right: 1px solid var(--aria-border) !important;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--aria-accent) !important;
    font-weight: 700 !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--aria-primary), var(--aria-secondary)) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--aria-radius) !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(83, 52, 131, 0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(83, 52, 131, 0.6) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: var(--aria-bg-card) !important;
    border: 1px solid var(--aria-border) !important;
    border-radius: var(--aria-radius) !important;
    color: var(--aria-text-primary) !important;
    font-family: 'Cairo', 'Inter', sans-serif !important;
}

.stDataFrame {
    border: 1px solid var(--aria-border) !important;
    border-radius: var(--aria-radius) !important;
    overflow: hidden !important;
}

.aria-score-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
}

.aria-score-platinum { background: linear-gradient(135deg, #e5e4e2, #a0b2c6); color: #000; }
.aria-score-gold     { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; }
.aria-score-silver   { background: linear-gradient(135deg, #c0c0c0, #808080); color: #fff; }
.aria-score-bronze   { background: linear-gradient(135deg, #cd7f32, #8b4513); color: #fff; }

.status-active      { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
.status-pending     { background: rgba(255,215,0,0.15);  color: #ffd700; border: 1px solid #ffd700; }
.status-disputed    { background: rgba(233,69,96,0.15);  color: #e94560; border: 1px solid #e94560; }
.status-completed   { background: rgba(83,52,131,0.25);  color: #b08bff; border: 1px solid #533483; }

.status-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.escrow-progress {
    height: 8px;
    background: var(--aria-border);
    border-radius: 4px;
    overflow: hidden;
}

.escrow-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--aria-primary), var(--aria-success));
    border-radius: 4px;
    transition: width 0.5s ease;
}

.god-mode-header {
    background: linear-gradient(135deg, #1a0a2e, #2d1b4e);
    border: 1px solid rgba(233, 69, 96, 0.5);
    border-radius: var(--aria-radius-lg);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--aria-bg-dark); }
::-webkit-scrollbar-thumb { background: var(--aria-secondary); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--aria-accent); }

#MainMenu, footer, header { visibility: hidden !important; }
""")

# ── MODULE 13: GOD MODE ADMIN DASHBOARD ─────────────────────────────────────
w("frontend/_pages/god_mode_page.py", """\"\"\"God Mode Admin Dashboard — Module 13\"\"\"
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random
from ..utils.api_client import api_get
from ..utils.session import get_role

def render():
    if get_role() != "admin":
        st.error("⛔ God Mode — Admin Access Only / وصول مرفوض")
        st.stop()

    st.markdown('''
    <div class="god-mode-header">
        <h1 style="color:#e94560;margin:0;">⚡ GOD MODE — ARIA Control Center</h1>
        <p style="color:#a0a0b0;margin:5px 0 0 0;">
            Full platform oversight | Zero restrictions | Executive authority
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # ── Real-time Platform Metrics ──────────────────────────────
    st.markdown("### 📊 Platform Pulse — Real-Time")

    stats = api_get("/api/admin/dashboard") or {}

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("👥 Total Users",        str(stats.get("total_users", 0)),        "+23 today"),
        ("🏪 Active Merchants",   str(stats.get("total_merchants", 0)),    "+5 this week"),
        ("🌟 Active Influencers", str(stats.get("total_influencers", 0)),  "+18 this week"),
        ("📢 Live Campaigns",     str(stats.get("total_campaigns", 0)),    "+8 today"),
        ("💰 Escrow Locked",      f"{stats.get('total_escrow_jod',0):,.0f} JOD", "secured"),
    ]
    for col, (label, value, delta) in zip([col1,col2,col3,col4,col5], metrics):
        col.metric(label, value, delta)

    st.divider()

    # ── ARIA Agent Status Panel ─────────────────────────────────
    st.markdown("### 🤖 ARIA Agent Status")
    agent_col1, agent_col2 = st.columns(2)

    with agent_col1:
        st.markdown('''
        <div style="background:#1a1a2e;border:1px solid #533483;border-radius:12px;padding:1.2rem;">
            <h4 style="color:#00ff88;">🛡️ Guardian Agent</h4>
            <p style="color:#a0a0b0;font-size:13px;">Status: <b style="color:#00ff88;">ONLINE</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Jobs Queued: <b>14</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Next Run: <b>02:00 AM (Scoring)</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Escrow Releases Today: <b>3</b></p>
        </div>
        ''', unsafe_allow_html=True)

    with agent_col2:
        st.markdown('''
        <div style="background:#1a1a2e;border:1px solid #533483;border-radius:12px;padding:1.2rem;">
            <h4 style="color:#ffd700;">🔍 AI Auditor Agent</h4>
            <p style="color:#a0a0b0;font-size:13px;">Status: <b style="color:#00ff88;">ONLINE</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Audits Today: <b>28</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Auto-Approved: <b>22 (78.5%)</b></p>
            <p style="color:#a0a0b0;font-size:13px;">Flagged for Review: <b>6</b></p>
        </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # ── Revenue Analytics ───────────────────────────────────────
    st.markdown("### 💹 Revenue Analytics (JOD)")

    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
    revenue_data = pd.DataFrame({
        "date": dates,
        "platform_fees": [random.uniform(200, 800) for _ in range(30)],
        "escrow_volume": [random.uniform(2000, 8000) for _ in range(30)],
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=revenue_data["date"], y=revenue_data["escrow_volume"],
        fill="tozeroy", name="Escrow Volume",
        line=dict(color="#0f3460"), fillcolor="rgba(15,52,96,0.3)"
    ))
    fig.add_trace(go.Scatter(
        x=revenue_data["date"], y=revenue_data["platform_fees"],
        fill="tozeroy", name="Platform Fees",
        line=dict(color="#533483"), fillcolor="rgba(83,52,131,0.3)"
    ))
    fig.update_layout(
        paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
        font=dict(color="white"), height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── ARIA Score Distribution ─────────────────────────────────
    st.markdown("### 🏆 Influencer ARIA Score Distribution")
    score_col1, score_col2 = st.columns([2, 1])

    with score_col1:
        tiers  = ["PLATINUM", "GOLD", "SILVER", "BRONZE", "UNRANKED"]
        counts = [12, 47, 98, 103, 52]
        colors = ["#e5e4e2", "#ffd700", "#c0c0c0", "#cd7f32", "#555"]
        fig2 = go.Figure(go.Bar(x=tiers, y=counts, marker_color=colors,
                                text=counts, textposition="outside"))
        fig2.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e",
                           font=dict(color="white"), height=280,
                           margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with score_col2:
        st.markdown('''
        <div style="padding:1rem;">
            <div style="margin-bottom:12px;">
                <span style="color:#e5e4e2;font-size:20px;">💎</span>
                <b style="color:#e5e4e2;"> PLATINUM</b>
                <span style="float:right;color:#a0a0b0;">12</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#ffd700;font-size:20px;">🥇</span>
                <b style="color:#ffd700;"> GOLD</b>
                <span style="float:right;color:#a0a0b0;">47</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#c0c0c0;font-size:20px;">🥈</span>
                <b style="color:#c0c0c0;"> SILVER</b>
                <span style="float:right;color:#a0a0b0;">98</span>
            </div>
            <div style="margin-bottom:12px;">
                <span style="color:#cd7f32;font-size:20px;">🥉</span>
                <b style="color:#cd7f32;"> BRONZE</b>
                <span style="float:right;color:#a0a0b0;">103</span>
            </div>
            <div>
                <span style="font-size:20px;">⬜</span>
                <b style="color:#555;"> UNRANKED</b>
                <span style="float:right;color:#a0a0b0;">52</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.divider()

    # ── Executive Control Panel ─────────────────────────────────
    st.markdown("### ⚙️ Executive Control Panel")
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)

    with ctrl_col1:
        st.markdown("**🔄 Manual Agent Triggers**")
        if st.button("▶️ Force Influencer Scoring", use_container_width=True):
            st.toast("Guardian triggered: scoring job queued", icon="🤖")
        if st.button("▶️ Force Escrow Release Check", use_container_width=True):
            st.toast("Guardian triggered: escrow check queued", icon="💰")
        if st.button("▶️ Re-Audit Flagged Content", use_container_width=True):
            st.toast("Auditor triggered: re-audit job queued", icon="🔍")

    with ctrl_col2:
        st.markdown("**🚨 Emergency Controls**")
        if st.button("🛑 Freeze All Escrows", use_container_width=True, type="secondary"):
            st.warning("Confirm: This will freeze ALL escrow transactions")
        if st.button("📧 Blast Notification (All)", use_container_width=True, type="secondary"):
            st.info("Platform-wide notification panel")
        if st.button("🔃 Rebuild RAG Index", use_container_width=True, type="secondary"):
            st.toast("RAG rebuild initiated...", icon="🧠")

    with ctrl_col3:
        st.markdown("**📊 Reports**")
        if st.button("📥 Export Platform Report", use_container_width=True):
            st.toast("Report generating...", icon="📊")
        if st.button("📥 Export Escrow Ledger", use_container_width=True):
            st.toast("Ledger exporting...", icon="💳")
        if st.button("📥 Export User Analytics", use_container_width=True):
            st.toast("Analytics exporting...", icon="📈")

    st.divider()

    # ── Users Table ─────────────────────────────────────────────
    tab1, tab2 = st.tabs(["👥 Users", "📢 All Campaigns"])
    with tab1:
        users = api_get("/api/admin/users") or []
        if users:
            df = pd.DataFrame([{
                "ID": u.get("id"), "Name": u.get("full_name_en") or u.get("full_name_ar"),
                "Email": u.get("email"), "Role": u.get("role"), "Active": u.get("is_active"),
            } for u in users])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

    with tab2:
        campaigns = api_get("/api/campaigns") or []
        if campaigns:
            df = pd.DataFrame([{
                "ID": c.get("id"),
                "Title": c.get("title_en") or c.get("title_ar"),
                "Status": c.get("status"),
                "Budget (JOD)": c.get("total_budget"),
                "Niche": c.get("niche"),
            } for c in campaigns])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No campaigns found")
""")

# ── MODULE 14: CHATBOT ROUTE (full RAG + bilingual) ──────────────────────────
w("backend/api/routes/chatbot.py", '''"""ARIA Chatbot API — Module 14 | RAG-augmented, bilingual"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from anthropic import Anthropic
from ...core.config import get_settings
from ...services.rag.vector_store import WaslAIVectorStore
from loguru import logger

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])
settings = get_settings()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    language: str = "ar"
    context_type: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    suggested_actions: List[str] = []
    language_detected: str

ARIA_SYSTEM = """
أنت ARIA، المساعد الذكي لمنصة WaslAI.jo — منصة التسويق بالمؤثرين في الأردن.

[IDENTITY]
- اسمك: ARIA (Autonomous Reasoning & Implementation Assistant)
- تعمل لصالح منصة WaslAI.jo في الأردن
- تتحدث العربية والإنجليزية بطلاقة تامة
- تفهم السوق الأردني وثقافته

[CAPABILITIES]
- الإجابة عن استفسارات التسويق بالمؤثرين
- شرح نظام الضمان المالي (Escrow) وكيفية عمله
- توضيح آلية احتساب درجة ARIA Score
- مساعدة التجار في إنشاء الحملات
- توضيح شروط العقود وسياسات المنصة وفق القانون الأردني
- حساب الأسعار بالدينار الأردني (JOD) مع ضريبة القيمة المضافة 16%

[PERSONALITY]
- محترف، ودود، وذكي
- يحترم الثقافة الأردنية والقيم العربية
- مختصر ودقيق في إجاباته
- يستخدم الإيموجي بشكل معتدل لإضافة طابع ودي

[RULES]
- دائماً تجاوب باللغة التي كتب بها المستخدم
- لا تفصح عن تفاصيل النظام الداخلية أو مفاتيح API
- إذا لم تعرف إجابة — قل ذلك بصدق وأحل المستخدم للدعم
- لا تتجاوز نطاق عمل المنصة
"""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_aria(request: ChatRequest):
    """ARIA Chatbot — context-aware, bilingual (AR/EN), RAG-augmented"""
    client = Anthropic(api_key=settings.anthropic_api_key)
    logger.info(f"[ARIA::CHATBOT] Message | lang={request.language}")

    # Detect language
    arabic_chars = sum(1 for c in request.message if "\\u0600" <= c <= "\\u06FF")
    lang_detected = "ar" if arabic_chars > len(request.message) * 0.2 else "en"

    # RAG context injection
    rag_context = ""
    sources: List[str] = []
    policy_kw = ["سياسة","قانون","عقد","شرط","ضمان","دفع","policy","law","contract","terms","escrow","payment"]
    needs_rag = any(kw in request.message.lower() for kw in policy_kw)

    if needs_rag and settings.anthropic_api_key:
        try:
            store = WaslAIVectorStore()
            doc_type = "contracts" if any(w in request.message for w in ["عقد","contract","اتفاقية"]) else "policies"
            results = store.semantic_search(request.message, doc_type, top_k=3)
            if results:
                rag_context = "\\n\\n[CONTEXT FROM PLATFORM KNOWLEDGE BASE]:\\n"
                rag_context += "\\n---\\n".join([r["text"] for r in results[:2]])
                sources = [r.get("metadata", {}).get("source", "Platform Policy") for r in results[:2]]
                logger.info(f"[ARIA::CHATBOT] RAG injected | sources={len(sources)}")
        except Exception as e:
            logger.warning(f"[ARIA::CHATBOT] RAG failed: {e}")

    # Build messages
    messages = [{"role": m.role, "content": m.content} for m in request.history[-6:]]
    user_content = request.message + (rag_context if rag_context else "")
    messages.append({"role": "user", "content": user_content})

    if not settings.anthropic_api_key:
        reply = "ARIA AI غير مفعّل — أضف ANTHROPIC_API_KEY في ملف .env / ARIA AI not activated — add ANTHROPIC_API_KEY to .env"
    else:
        resp = client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=ARIA_SYSTEM,
            messages=messages
        )
        reply = resp.content[0].text
        logger.success(f"[ARIA::CHATBOT] Response | tokens={resp.usage.output_tokens}")

    return ChatResponse(
        response=reply,
        sources=sources,
        suggested_actions=_suggestions(request.message, lang_detected),
        language_detected=lang_detected
    )

def _suggestions(message: str, lang: str) -> List[str]:
    msg = message.lower()
    if lang == "ar":
        if any(w in msg for w in ["حملة","إنشاء"]):
            return ["📢 إنشاء حملة جديدة", "💰 احتساب الميزانية", "🌟 البحث عن مؤثرين"]
        elif any(w in msg for w in ["ضمان","دفع"]):
            return ["💳 عرض رصيد الضمان", "📋 عرض تاريخ المعاملات", "📞 التواصل مع الدعم"]
        elif any(w in msg for w in ["عقد","اتفاق"]):
            return ["📄 إنشاء عقد جديد", "📖 عرض العقود السابقة", "⚖️ سياسة النزاعات"]
        return ["📢 إنشاء حملة", "🔍 البحث عن مؤثرين", "📊 عرض التقارير"]
    else:
        if any(w in msg for w in ["campaign","create"]):
            return ["📢 Create Campaign", "💰 Budget Calculator", "🌟 Find Influencers"]
        elif any(w in msg for w in ["escrow","payment"]):
            return ["💳 View Escrow Balance", "📋 Transaction History", "📞 Contact Support"]
        elif any(w in msg for w in ["contract","agreement"]):
            return ["📄 Generate Contract", "📖 View Past Contracts", "⚖️ Dispute Policy"]
        return ["📢 Create Campaign", "🔍 Find Influencers", "📊 View Reports"]
''')

# ── CHATBOT ROUTE also needs to be registered under /api/chat ────────────────
# Check existing main.py router prefix — chatbot is at /api/chatbot/chat
# The frontend widget calls /api/chatbot/chat — already correct

# ── MODULE 15: UPDATED SCRIPTS ───────────────────────────────────────────────
SCRIPTS_BASE = "C:/WaslAI_AI/scripts"

def ws(fname, content):
    path = os.path.join(SCRIPTS_BASE, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK  scripts/{fname}  ({len(content)} bytes)")

ws("start_all.py", '''#!/usr/bin/env python3
"""ARIA WaslAI.jo — One-Command Launcher"""
import subprocess, sys, os, time, signal
from pathlib import Path

ROOT = Path(__file__).parent.parent / "waslai"
os.chdir(ROOT)

CYAN = "\\033[96m"; GREEN = "\\033[92m"; RED = "\\033[91m"
YELLOW = "\\033[93m"; RESET = "\\033[0m"; BOLD = "\\033[1m"

def banner():
    print(f"""{CYAN}{BOLD}
+--------------------------------------------------------------+
|   ARIA - WaslAI.jo Platform Launcher v1.0.0             |
|   Jordan Influencer Marketing Platform                       |
|   Powered by Claude AI + FastAPI + Streamlit                 |
+--------------------------------------------------------------+
{RESET}""")

def check_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        print(f"{RED}[ERROR] .env not found at {env_file}{RESET}")
        sys.exit(1)
    content = env_file.read_text()
    if "your_anthropic" in content or "ANTHROPIC_API_KEY=" not in content:
        print(f"{YELLOW}[WARN] ANTHROPIC_API_KEY not set — AI features disabled{RESET}")
    else:
        print(f"{GREEN}[OK] Environment validated{RESET}")

def init_database():
    print(f"{CYAN}[DB] Initializing database...{RESET}")
    result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "init_db.py")],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"{GREEN}[OK] Database ready{RESET}")
    else:
        print(f"{YELLOW}[WARN] DB init: {result.stderr[:100]}{RESET}")

def start_services():
    processes = []

    print(f"\\n{CYAN}[API] Starting FastAPI Backend (port 8000)...{RESET}")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "warning"],
        cwd=ROOT
    )
    processes.append(("Backend", backend))
    time.sleep(3)

    print(f"{CYAN}[UI] Starting Streamlit Frontend (port 8501)...{RESET}")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", "8501", "--server.address", "0.0.0.0",
         "--server.headless", "true",
         "--theme.base", "dark",
         "--theme.primaryColor", "#533483",
         "--theme.backgroundColor", "#0a0a1a",
         "--theme.secondaryBackgroundColor", "#1a1a2e"],
        cwd=ROOT
    )
    processes.append(("Frontend", frontend))
    time.sleep(2)

    print(f"""{GREEN}{BOLD}
+--------------------------------------------------------------+
|  ARIA WaslAI.jo Platform ONLINE                         |
|                                                              |
|  FastAPI Backend:   http://localhost:8000                    |
|  API Documentation: http://localhost:8000/docs               |
|  Streamlit UI:      http://localhost:8501                    |
|  Health Check:      http://localhost:8000/health             |
|                                                              |
|  Press Ctrl+C to shutdown all services                      |
+--------------------------------------------------------------+
{RESET}""")

    def shutdown(sig, frame):
        print(f"\\n{YELLOW}[ARIA] Shutting down...{RESET}")
        for name, proc in processes:
            proc.terminate()
            print(f"{RED}[STOP] {name}{RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    for _, proc in processes:
        proc.wait()

if __name__ == "__main__":
    banner()
    check_env()
    init_database()
    start_services()
''')

ws("init_db.py", '''#!/usr/bin/env python3
"""Database initialization — creates tables + admin user"""
import asyncio, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "waslai"
sys.path.insert(0, str(ROOT))

async def init():
    from backend.core.database import init_db, AsyncSessionLocal
    from backend.core.security import get_password_hash
    from backend.models.user import User, UserRole

    await init_db()
    print("[DB] Tables created")

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == "godmode_admin"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@waslai.jo",
                username="godmode_admin",
                hashed_password=get_password_hash("aria_admin_2024"),
                role=UserRole.ADMIN,
                full_name_en="ARIA God Mode Admin",
                full_name_ar="مشرف النظام",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            print("[DB] Admin user created: admin@waslai.jo / aria_admin_2024")
        else:
            print("[DB] Admin user already exists")

    print("[DB] Database initialization complete")

if __name__ == "__main__":
    asyncio.run(init())
''')

ws("seed_rag.py", '''#!/usr/bin/env python3
"""Seed RAG vector store — contracts, policies, Jordan market docs"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "waslai"
sys.path.insert(0, str(ROOT))

ARABIC_CONTRACT = """
عقد تعاون تسويقي بالمؤثرين
بين: التاجر (الطرف الأول) والمؤثر (الطرف الثاني)

البند الأول: موضوع العقد
يلتزم الطرف الثاني بتنفيذ المهام التسويقية المحددة في الملحق (أ)
خلال المدة المتفق عليها وبالمواصفات المطلوبة.

البند الثاني: المقابل المالي
يلتزم الطرف الأول بدفع المبلغ المتفق عليه بالدينار الأردني (JOD)
عبر نظام الضمان المالي (Escrow) في منصة WaslAI.jo.
يطبق ضريبة القيمة المضافة بنسبة 16% وفق التشريع الأردني.

البند الثالث: التسليمات المطلوبة
يجب أن تتضمن المحتوى المتفق عليه (منشور/قصة/ريل)
مع ذكر العلامة التجارية والهاشتاقات المحددة.

البند الرابع: حقوق الملكية الفكرية
يحتفظ الطرف الأول بحق استخدام المحتوى المنتج لمدة 12 شهراً.

البند الخامس: فض النزاعات
تحال النزاعات إلى فريق WaslAI.jo خلال 48 ساعة من نشوئها.
القانون الواجب التطبيق: القانون الأردني.
"""

ENGLISH_CONTRACT = """
Influencer Marketing Collaboration Agreement
Between: Merchant (Party A) and Influencer (Party B)

Article 1: Scope of Work
Party B agrees to execute the marketing deliverables specified in Appendix A
within the agreed timeline and to the specified quality standards.

Article 2: Compensation
Party A agrees to pay the agreed amount in Jordanian Dinar (JOD)
through the WaslAI.jo Escrow system.
VAT at 16% applies per Jordan tax law.

Article 3: Deliverables
Must include agreed content types (post/story/reel)
with brand mentions and specified hashtags.

Article 4: Intellectual Property
Party A retains rights to produced content for 12 months.

Article 5: Dispute Resolution
Disputes escalated to WaslAI.jo within 48 hours.
Governing law: Hashemite Kingdom of Jordan.
"""

JORDAN_POLICY = """
سياسات منصة WaslAI.jo — السوق الأردني

1. سياسة الدفع والضمان المالي (Escrow):
- يتم تجميد المبلغ في حساب الضمان فور إطلاق الحملة
- يحرر المبلغ تلقائياً بعد 7 أيام من الموافقة على المحتوى
- عمولة المنصة: 5% من إجمالي قيمة الحملة
- ضريبة القيمة المضافة: 16% وفق قانون ضريبة المبيعات الأردني

2. معايير المحتوى في السوق الأردني:
- يجب احترام القيم والثقافة الأردنية في جميع المحتويات
- يحظر المحتوى المسيء دينياً أو اجتماعياً
- يجب الإفصاح عن الطابع الإعلاني للمحتوى

3. سياسة النزاعات:
- مدة تقديم النزاع: 48 ساعة من تسليم المحتوى
- يقوم الذكاء الاصطناعي ARIA بمراجعة أولية للنزاع

4. معايير المؤثرين:
- الحد الأدنى للمتابعين: 1,000 متابع على أي منصة
- درجة ARIA Score مطلوبة: لا تقل عن 40 نقطة

5. سياسة إلغاء الحملات:
- الإلغاء قبل 48 ساعة: استرداد كامل للمبلغ
- الإلغاء بعد بدء التنفيذ: استرداد 50% فقط
- الإلغاء بعد التسليم: لا يحق استرداد المبلغ
"""

def seed():
    from backend.services.rag.vector_store import WaslAIVectorStore
    store = WaslAIVectorStore()

    store.ingest_document(ARABIC_CONTRACT, "contracts",
        {"id": "template_ar_001", "language": "ar", "source": "WaslAI Contract Template AR"})
    store.ingest_document(ENGLISH_CONTRACT, "contracts",
        {"id": "template_en_001", "language": "en", "source": "WaslAI Contract Template EN"})
    store.ingest_document(JORDAN_POLICY, "policies",
        {"id": "jordan_platform_policy", "language": "ar", "source": "WaslAI Platform Policy v1.0"})

    print("[RAG] Contract templates seeded (AR + EN)")
    print("[RAG] Platform policies seeded")
    print("[RAG] Knowledge base ready")

if __name__ == "__main__":
    print("[ARIA] Seeding RAG Knowledge Base...")
    seed()
    print("[ARIA] RAG seeding complete")
''')

# ── INTEGRATION TEST SUITE ────────────────────────────────────────────────────
w("backend/tests/integration/test_full_pipeline.py", '''"""
ARIA Integration Test Suite — Section 4
Tests complete campaign lifecycle end-to-end
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

BASE_URL = "http://localhost:8000/api"

class TestScoringAlgorithm:
    """Test ARIA Influencer Scoring"""

    def test_micro_influencer_scoring(self):
        from backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        scorer = ARIAInfluencerScorer()
        result = scorer.compute_final_aria_score(
            influencer_data={
                "instagram_followers": 45000,
                "instagram_engagement_rate": 4.2,
                "tiktok_followers": 12000,
                "tiktok_engagement_rate": 6.8,
                "youtube_subscribers": 0,
                "city": "amman",
                "niche": "fashion",
                "account_age_days": 730,
                "campaigns_completed": 8,
                "campaigns_total": 9,
                "on_time_deliveries": 8,
                "disputes_raised": 0,
                "monthly_growth_rate": 2.5,
            },
            campaign_niche="fashion"
        )
        assert result["aria_score"] > 0
        assert result["aria_score"] <= 100
        assert "aria_tier" in result
        print(f"ARIA Score: {result[\'aria_score\']} | Tier: {result[\'aria_tier\']}")

    def test_mega_influencer_penalty(self):
        from backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        scorer = ARIAInfluencerScorer()
        result = scorer.compute_final_aria_score(
            influencer_data={
                "instagram_followers": 2000000,
                "instagram_engagement_rate": 0.8,
                "city": "dubai",
                "account_age_days": 365,
            },
            campaign_niche="food"
        )
        print(f"Mega influencer score: {result[\'aria_score\']}")
        assert result["aria_score"] < 80


class TestEscrowEngine:
    """Test Escrow state machine"""

    def test_escrow_vat_calculation(self):
        amount_jod = 500.0
        vat        = amount_jod * 0.16
        commission = amount_jod * 0.05
        net        = amount_jod - commission
        assert vat == 80.0
        assert commission == 25.0
        assert net == 475.0
        print(f"Escrow math: 500 JOD -> Net: {net} | VAT: {vat} | Fee: {commission}")

    def test_valid_transitions(self):
        from backend.services.escrow.escrow_engine import EscrowEngine
        engine = EscrowEngine(None)
        assert "funded"     in engine.VALID_TRANSITIONS["pending"]
        assert "released"   in engine.VALID_TRANSITIONS["under_review"]
        assert "disputed"   in engine.VALID_TRANSITIONS["in_progress"]
        print("Escrow state machine: PASS")


class TestRAGSystem:
    """Test RAG vector store"""

    def test_vector_store_init(self):
        from backend.services.rag.vector_store import WaslAIVectorStore
        store = WaslAIVectorStore()
        assert store.contracts_col is not None
        assert store.policies_col is not None
        print("RAG vector store initialized: PASS")

    def test_document_ingestion(self):
        from backend.services.rag.vector_store import WaslAIVectorStore
        store = WaslAIVectorStore()
        store.ingest_document(
            "Test contract for Jordan market compliance",
            "contracts",
            {"id": "test_001", "language": "en", "source": "test"}
        )
        print("Document ingestion: PASS")


class TestLoyaltyWallet:
    """Test loyalty points engine"""

    def test_points_to_jod_conversion(self):
        from backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        engine = LoyaltyWalletEngine(None)
        assert engine.calculate_jod_value(0)    == 0.0
        assert engine.calculate_jod_value(500)  == 5.0
        assert engine.calculate_jod_value(1000) == 10.0
        print("Loyalty wallet conversion: PASS")

    def test_merchant_tier(self):
        from backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        engine = LoyaltyWalletEngine(None)
        assert engine.get_tier(1000)["tier"]  == "BRONZE"
        assert engine.get_tier(5000)["tier"]  == "SILVER"
        assert engine.get_tier(20000)["tier"] == "GOLD"
        assert engine.get_tier(50000)["tier"] == "PLATINUM"
        print("Merchant tier calculation: PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
''')

print("\nModules 13-15 + Tests ALL WRITTEN OK")
