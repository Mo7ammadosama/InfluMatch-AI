"""ARIA Chatbot API — Module 14 | RAG-augmented, bilingual"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from ...core.config import get_settings
from ...core.database import get_db
from ...models.chat_history import ChatHistory
from ...services.rag.vector_store import WaslAIVectorStore
from loguru import logger

router = APIRouter(prefix="/chatbot", tags=["AI Chatbot"])
settings = get_settings()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message     : str
    session_id  : Optional[str] = None   # frontend generates UUID once per session
    user_id     : Optional[int] = None
    history     : List[ChatMessage] = []  # kept for backward compat; DB is authoritative
    language    : str = "ar"
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
async def chat_with_aria(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """ARIA Chatbot — context-aware, bilingual (AR/EN), RAG-augmented, DB-persisted"""
    from groq import Groq
    client = Groq(api_key=settings.groq_api_key)
    logger.info(f"[ARIA::CHATBOT] Message | lang={request.language} | session={request.session_id}")

    # Detect language
    arabic_chars = sum(1 for c in request.message if "\u0600" <= c <= "\u06FF")
    lang_detected = "ar" if arabic_chars > len(request.message) * 0.2 else "en"

    # Load history from DB when session_id is provided (last 6 rounds = 12 messages)
    if request.session_id:
        history_r = await db.execute(
            select(ChatHistory)
            .where(ChatHistory.session_id == request.session_id)
            .order_by(ChatHistory.created_at.asc())
            .limit(12)
        )
        db_history = history_r.scalars().all()
        messages = [{"role": m.role, "content": m.content} for m in db_history]
    else:
        # Fallback: use client-supplied history for backward compat
        messages = [{"role": m.role, "content": m.content} for m in request.history[-6:]]

    # RAG context injection
    rag_context = ""
    sources: List[str] = []
    policy_kw = ["سياسة","قانون","عقد","شرط","ضمان","دفع","policy","law","contract","terms","escrow","payment"]
    needs_rag = any(kw in request.message.lower() for kw in policy_kw)

    if needs_rag and settings.groq_api_key:
        try:
            store = WaslAIVectorStore()
            doc_type = "contracts" if any(w in request.message for w in ["عقد","contract","اتفاقية"]) else "policies"
            results = store.semantic_search(request.message, doc_type, top_k=3)
            if results:
                rag_context = "\n\n[CONTEXT FROM PLATFORM KNOWLEDGE BASE]:\n"
                rag_context += "\n---\n".join([r["text"] for r in results[:2]])
                sources = [r.get("metadata", {}).get("source", "Platform Policy") for r in results[:2]]
                logger.info(f"[ARIA::CHATBOT] RAG injected | sources={len(sources)}")
        except Exception as e:
            logger.warning(f"[ARIA::CHATBOT] RAG failed: {e}")

    user_content = request.message + (rag_context if rag_context else "")
    messages.append({"role": "user", "content": user_content})

    if not settings.groq_api_key:
        reply = "ARIA AI غير مفعّل — أضف GROQ_API_KEY في ملف .env / ARIA AI not activated — add GROQ_API_KEY to .env"
    else:
        try:
            logger.info(f"[ARIA::CHATBOT] Calling Groq API | msgs={len(messages)}")
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
                temperature=0.7,
                messages=[{"role": "system", "content": ARIA_SYSTEM}] + messages,
            )
            reply = resp.choices[0].message.content
            logger.success(f"[ARIA::CHATBOT] Response | tokens={resp.usage.completion_tokens}")
        except Exception as e:
            logger.error(f"[ARIA::CHATBOT] API error: {type(e).__name__}: {e}")
            reply = "عذراً، حدث خطأ في ARIA. يرجى المحاولة مرة أخرى. / ARIA encountered an error. Please try again."

    # Persist conversation to DB when session_id provided
    if request.session_id:
        db.add(ChatHistory(
            session_id = request.session_id,
            user_id    = request.user_id,
            role       = "user",
            content    = request.message,   # store raw message, not RAG-augmented
            language   = lang_detected,
        ))
        db.add(ChatHistory(
            session_id = request.session_id,
            user_id    = request.user_id,
            role       = "assistant",
            content    = reply,
            language   = lang_detected,
        ))
        # get_db() context manager commits at end of request

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
