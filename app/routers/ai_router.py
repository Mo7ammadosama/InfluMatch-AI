"""
WaslAI.jo — AI Router
Matching, RAG queries, content analysis endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User, UserRole
from app.models.campaign import Campaign
from app.schemas.influencer import InfluencerRead
from app.middleware.auth_middleware import get_current_user, require_role
from app.services.matching_service import matching_service

router = APIRouter()


class MatchRequest(BaseModel):
    campaign_id: str
    top_k: int = 10


class MatchResult(BaseModel):
    influencer: InfluencerRead
    score: float
    rank: int


@router.post("/match", response_model=list[MatchResult])
async def match_influencers(
    payload: MatchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Campaign).where(Campaign.id == payload.campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    matches = await matching_service.find_matches(campaign, db, top_k=payload.top_k)
    return [
        MatchResult(
            influencer=InfluencerRead.model_validate(m["influencer"]),
            score=m["score"],
            rank=i + 1,
        )
        for i, m in enumerate(matches)
    ]


class ChatRequest(BaseModel):
    message: str
    context: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model_used: str


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    payload: ChatRequest,
    _: User = Depends(get_current_user),
):
    try:
        import anthropic
        from app.config import settings

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        system = (
            "You are an AI assistant for WaslAI.jo, a B2B influencer marketing platform for Jordan. "
            "You help merchants and influencers with campaign planning, pricing, and matching in the Jordanian market. "
            "You respond in Arabic or English based on the user's language. "
            "Currency is Jordanian Dinar (JOD). VAT is 16%."
        )
        if payload.context:
            system += f"\n\nContext:\n{payload.context}"

        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
            system=system,
            messages=[{"role": "user", "content": payload.message}],
        )
        return ChatResponse(reply=response.content[0].text, model_used=settings.claude_model)

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service error: {str(e)}")
