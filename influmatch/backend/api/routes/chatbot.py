"""ARIA Chatbot API — Module 14 | RAG-augmented, bilingual"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from anthropic import Anthropic
from ...core.config import get_settings
from ...services.rag.vector_store import InfluMatchVectorStore
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
أنت ARIA، المساعد الذكي لمنصة InfluMatch.jo — منصة التسويق بالمؤثرين في الأردن.

[IDENTITY]
- اسمك: ARIA (Autonomous Reasoning & Implementation Assistant)
- تعمل لصالح منصة InfluMatch.jo في الأردن
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
    arabic_chars = sum(1 for c in request.message if "\u0600" <= c <= "\u06FF")
    lang_detected = "ar" if arabic_chars > len(request.message) * 0.2 else "en"

    # RAG context injection
    rag_context = ""
    sources: List[str] = []
    policy_kw = ["سياسة","قانون","عقد","شرط","ضمان","دفع","policy","law","contract","terms","escrow","payment"]
    needs_rag = any(kw in request.message.lower() for kw in policy_kw)

    if needs_rag and settings.anthropic_api_key:
        try:
            store = InfluMatchVectorStore()
            doc_type = "contracts" if any(w in request.message for w in ["عقد","contract","اتفاقية"]) else "policies"
            results = store.semantic_search(request.message, doc_type, top_k=3)
            if results:
                rag_context = "\n\n[CONTEXT FROM PLATFORM KNOWLEDGE BASE]:\n"
                rag_context += "\n---\n".join([r["text"] for r in results[:2]])
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
