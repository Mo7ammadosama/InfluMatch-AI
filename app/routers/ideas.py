"""
WaslAI.jo — Campaign Ideas Router
Creative Strategists publish ideas; Merchants browse and hire them.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.campaign_idea import CampaignIdea, IdeaStatus, CreativeEngagement, CreativeEngagementStatus
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


# ── Pydantic schemas ────────────────────────────────────────────────────────────

class IdeaCreate(BaseModel):
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    target_audience: Optional[str] = None
    suggested_platforms: list[str] = []
    content_format: list[str] = []
    influencer_type: Optional[str] = None
    business_category: Optional[str] = None
    estimated_budget_jod: Optional[float] = None
    timeline_days: Optional[int] = None


class EngageCreate(BaseModel):
    agreed_fee_jod: float


# ── Helpers ────────────────────────────────────────────────────────────────────

def _idea_out(idea: CampaignIdea) -> dict:
    return {
        "id": idea.id,
        "creative_strategist_id": idea.user_id,
        "title": idea.title,
        "title_ar": idea.title_ar,
        "description": idea.description,
        "description_ar": idea.description_ar,
        "target_audience": idea.target_audience,
        "suggested_platforms": idea.suggested_platforms or [],
        "content_format": idea.content_format or [],
        "influencer_type": idea.influencer_type,
        "business_category": idea.business_category,
        "estimated_budget_jod": idea.estimated_budget_jod,
        "timeline_days": idea.timeline_days,
        "status": idea.status,
        "view_count": idea.view_count,
        "adoption_count": idea.adoption_count,
        "created_at": idea.created_at.isoformat() if idea.created_at else None,
    }


def _eng_out(eng: CreativeEngagement) -> dict:
    return {
        "id": eng.id,
        "campaign_idea_id": eng.campaign_idea_id,
        "merchant_id": eng.merchant_id,
        "creative_strategist_id": eng.strategist_user_id,
        "status": eng.status,
        "agreed_fee_jod": eng.agreed_fee_jod,
        "merchant_notes": eng.merchant_notes,
        "strategist_notes": eng.strategist_notes,
        "started_at": eng.started_at.isoformat() if eng.started_at else None,
        "completed_at": eng.completed_at.isoformat() if eng.completed_at else None,
        "created_at": eng.created_at.isoformat() if eng.created_at else None,
    }


# ── Routes — order matters: specific before parameterised ──────────────────────

@router.post("/engagements/{engagement_id}/complete")
async def complete_engagement(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CreativeEngagement).where(CreativeEngagement.id == engagement_id)
    )
    eng = result.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if eng.strategist_user_id != current_user.id and eng.merchant_id:
        from app.models.merchant import Merchant as _Merchant
        merch_r = await db.execute(
            select(_Merchant).where(_Merchant.user_id == current_user.id)
        )
        merchant = merch_r.scalar_one_or_none()
        if not merchant or eng.merchant_id != merchant.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    from datetime import datetime as _dt
    eng.status = CreativeEngagementStatus.COMPLETED
    eng.completed_at = _dt.utcnow()
    return _eng_out(eng)


@router.get("/engagements/my")
async def get_my_engagements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CreativeEngagement)
        .where(CreativeEngagement.strategist_user_id == current_user.id)
        .order_by(CreativeEngagement.created_at.desc())
    )
    return [_eng_out(e) for e in result.scalars().all()]


@router.get("/my")
async def get_my_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CampaignIdea)
        .where(CampaignIdea.user_id == current_user.id)
        .order_by(CampaignIdea.created_at.desc())
    )
    return [_idea_out(i) for i in result.scalars().all()]


@router.get("/")
@router.get("")
async def list_ideas(
    business_category: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(CampaignIdea).where(CampaignIdea.status != IdeaStatus.WITHDRAWN)
    if business_category:
        q = q.where(CampaignIdea.business_category == business_category.lower())
    q = q.order_by(CampaignIdea.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return [_idea_out(i) for i in result.scalars().all()]


@router.post("/", status_code=201)
@router.post("", status_code=201)
async def submit_idea(
    payload: IdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = CampaignIdea(user_id=current_user.id, **payload.model_dump())
    db.add(idea)
    await db.flush()
    return _idea_out(idea)


@router.get("/{idea_id}")
async def get_idea(
    idea_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.view_count += 1
    return _idea_out(idea)


@router.put("/{idea_id}")
async def update_idea(
    idea_id: str,
    payload: IdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(idea, k, v)
    return _idea_out(idea)


@router.delete("/{idea_id}")
async def withdraw_idea(
    idea_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    idea.status = IdeaStatus.WITHDRAWN
    return {"status": "withdrawn"}


@router.post("/{idea_id}/engage", status_code=201)
async def engage_strategist(
    idea_id: str,
    payload: EngageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    merch_result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = merch_result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=400, detail="Merchant profile not found")

    eng = CreativeEngagement(
        campaign_idea_id=idea_id,
        merchant_id=merchant.id,
        strategist_user_id=idea.user_id,
        agreed_fee_jod=payload.agreed_fee_jod,
    )
    db.add(eng)
    idea.adoption_count += 1
    if idea.status == IdeaStatus.OPEN:
        idea.status = IdeaStatus.IN_PROGRESS
    await db.flush()
    return _eng_out(eng)
