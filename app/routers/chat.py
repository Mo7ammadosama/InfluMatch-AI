"""
WaslAI.jo — Onboarding Chatbot Router
Role-aware stateless chatbot powered by Claude Haiku.
Only answers questions about the InfluMatch platform.
"""
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.config import settings

def _get_api_key() -> str:
    """Return ANTHROPIC_API_KEY from settings, os.environ, or .env file fallback."""
    if settings.anthropic_api_key:
        return settings.anthropic_api_key
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    # Absolute-path fallback: walk up from this file to find .env
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

router = APIRouter()

SYSTEM_PROMPTS = {
    "merchant": (
        "You are the InfluMatch.jo onboarding assistant helping a Merchant user. "
        "InfluMatch.jo is a Jordan-based B2B platform that connects merchants with "
        "influencers and content creators for marketing campaigns. "
        "As a Merchant you can: create campaigns, browse influencers, send booking requests "
        "to content creators, review campaign ideas from creative strategists, and manage deals. "
        "Help this merchant understand how to complete their profile, create their first campaign, "
        "and connect with creators. Answer ONLY questions about the InfluMatch platform. "
        "If asked anything unrelated, politely redirect to platform topics. "
        "Be concise, friendly, and bilingual-aware (Arabic/English)."
    ),
    "influencer": (
        "You are the InfluMatch.jo onboarding assistant helping an Influencer user. "
        "InfluMatch.jo is a Jordan-based B2B platform connecting early-stage influencers "
        "with merchants for marketing campaigns. "
        "As an Influencer you can: build your profile, set your rates, browse open campaigns, "
        "receive and accept deals, submit content, and earn money through your wallet. "
        "Help this influencer complete their profile and land their first campaign. "
        "Answer ONLY questions about the InfluMatch platform. "
        "Be concise, friendly, and bilingual-aware (Arabic/English)."
    ),
    "content_creator": (
        "You are the InfluMatch.jo onboarding assistant helping a Content Creator user. "
        "InfluMatch.jo is a Jordan-based B2B platform. Content Creators publish a portfolio "
        "of style samples and creative concepts to attract merchant booking requests. "
        "After a merchant books you and you accept, a private creative engagement begins "
        "where you submit a tailored idea brief — this is kept strictly private. "
        "You can also apply to merchant campaign briefs. "
        "Help this content creator build their portfolio, accept bookings, and submit ideas. "
        "Answer ONLY questions about the InfluMatch platform. "
        "Be concise, friendly, and bilingual-aware (Arabic/English)."
    ),
    "default": (
        "You are the InfluMatch.jo onboarding assistant. "
        "InfluMatch.jo is a Jordan-based B2B influencer marketing platform. "
        "Answer ONLY questions about the platform. Be concise and friendly."
    ),
}


class ChatRequest(BaseModel):
    message: str
    role: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/onboarding", response_model=ChatResponse)
async def onboarding_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        import anthropic
    except ImportError:
        raise HTTPException(status_code=503, detail="Anthropic SDK not installed")

    api_key = _get_api_key()
    if not api_key:
        raise HTTPException(status_code=503, detail="Anthropic API key not configured [v2]")

    role = payload.role or current_user.role.value
    system_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["default"])

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": payload.message}],
    )

    reply = message.content[0].text if message.content else "How can I help you get started on InfluMatch?"
    return ChatResponse(reply=reply)
