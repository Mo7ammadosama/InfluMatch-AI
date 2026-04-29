"""
WaslAI.jo — Campaign Ideas & Engagements Router
Ideas submitted by Creative Strategists; hired by Merchants
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.creative_strategist import CreativeStrategist
from app.models.campaign_idea import CampaignIdea, CampaignIdeaStatus
from app.models.creative_engagement import CreativeEngagement, CreativeEngagementStatus
from app.models.merchant import Merchant
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.schemas.creative_strategist import (
    CampaignIdeaCreate,
    CampaignIdeaUpdate,
    CampaignIdeaRead,
    CreativeEngagementCreate,
    CreativeEngagementRead,
)
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()

MILESTONE_EVERY = 10
MILESTONE_BONUS_JOD = 20.0


# ── Ideas ─────────────────────────────────────────────────────────────────────

@router.post("/", response_model=CampaignIdeaRead, status_code=201)
async def submit_idea(
    payload: CampaignIdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=400, detail="Complete your Creative Strategist profile first")

    idea = CampaignIdea(creative_strategist_id=strategist.id, **payload.model_dump())
    db.add(idea)
    await db.flush()
    return idea


@router.get("/my", response_model=list[CampaignIdeaRead])
async def my_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        return []
    result = await db.execute(
        select(CampaignIdea)
        .where(CampaignIdea.creative_strategist_id == strategist.id)
        .order_by(CampaignIdea.created_at.desc())
    )
    return result.scalars().all()


@router.get("/", response_model=list[CampaignIdeaRead])
async def list_ideas(
    business_category: str | None = Query(default=None),
    idea_status: CampaignIdeaStatus | None = Query(default=None),
    platform: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(CampaignIdea).where(CampaignIdea.status != CampaignIdeaStatus.WITHDRAWN)
    if business_category:
        q = q.where(CampaignIdea.business_category == business_category)
    if idea_status:
        q = q.where(CampaignIdea.status == idea_status)
    q = q.order_by(CampaignIdea.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    ideas = result.scalars().all()

    if platform:
        ideas = [i for i in ideas if platform in (i.suggested_platforms or [])]

    return ideas


@router.get("/{idea_id}", response_model=CampaignIdeaRead)
async def get_idea(
    idea_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.view_count += 1
    return idea


@router.put("/{idea_id}", response_model=CampaignIdeaRead)
async def update_idea(
    idea_id: str,
    payload: CampaignIdeaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=400, detail="Profile not found")

    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.creative_strategist_id != strategist.id:
        raise HTTPException(status_code=403, detail="Not your idea")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(idea, field, value)
    return idea


@router.delete("/{idea_id}", status_code=204)
async def withdraw_idea(
    idea_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=400, detail="Profile not found")

    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.creative_strategist_id != strategist.id:
        raise HTTPException(status_code=403, detail="Not your idea")

    idea.status = CampaignIdeaStatus.WITHDRAWN


# ── Engagements ───────────────────────────────────────────────────────────────

@router.post("/{idea_id}/engage", response_model=CreativeEngagementRead, status_code=201)
async def engage_strategist(
    idea_id: str,
    payload: CreativeEngagementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=400, detail="Merchant profile not found")

    result = await db.execute(select(CampaignIdea).where(CampaignIdea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.status == CampaignIdeaStatus.WITHDRAWN:
        raise HTTPException(status_code=400, detail="This idea has been withdrawn")

    engagement = CreativeEngagement(
        campaign_idea_id=idea.id,
        merchant_id=merchant.id,
        creative_strategist_id=idea.creative_strategist_id,
        agreed_fee_jod=payload.agreed_fee_jod,
        merchant_notes=payload.merchant_notes,
        status=CreativeEngagementStatus.PENDING,
    )
    db.add(engagement)
    idea.adoption_count += 1
    await db.flush()
    return engagement


@router.get("/engagements/my", response_model=list[CreativeEngagementRead])
async def my_engagements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.MERCHANT:
        result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merchant = result.scalar_one_or_none()
        if not merchant:
            return []
        result = await db.execute(
            select(CreativeEngagement)
            .where(CreativeEngagement.merchant_id == merchant.id)
            .order_by(CreativeEngagement.created_at.desc())
        )
    elif current_user.role == UserRole.CREATIVE_STRATEGIST:
        result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
        strategist = result.scalar_one_or_none()
        if not strategist:
            return []
        result = await db.execute(
            select(CreativeEngagement)
            .where(CreativeEngagement.creative_strategist_id == strategist.id)
            .order_by(CreativeEngagement.created_at.desc())
        )
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    return result.scalars().all()


@router.post("/engagements/{engagement_id}/complete", response_model=CreativeEngagementRead)
async def complete_engagement(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=400, detail="Merchant profile not found")

    result = await db.execute(select(CreativeEngagement).where(CreativeEngagement.id == engagement_id))
    engagement = result.scalar_one_or_none()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if engagement.merchant_id != merchant.id:
        raise HTTPException(status_code=403, detail="Not your engagement")
    if engagement.status == CreativeEngagementStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Engagement already completed")

    engagement.status = CreativeEngagementStatus.COMPLETED
    engagement.completed_at = datetime.now(timezone.utc)

    # Update strategist metrics
    result = await db.execute(
        select(CreativeStrategist).where(CreativeStrategist.id == engagement.creative_strategist_id)
    )
    strategist = result.scalar_one_or_none()
    if strategist:
        strategist.completed_engagements += 1
        strategist.total_earned_jod += engagement.agreed_fee_jod

        # Milestone check: every 10 completed engagements
        if strategist.completed_engagements % MILESTONE_EVERY == 0:
            strategist.milestone_count += 1
            strategist.total_earned_jod += MILESTONE_BONUS_JOD

            # Credit milestone bonus to wallet
            result = await db.execute(
                select(Wallet).where(Wallet.user_id == strategist.user_id)
            )
            wallet = result.scalar_one_or_none()
            if wallet:
                wallet.available_balance_jod += MILESTONE_BONUS_JOD
                tx = WalletTransaction(
                    wallet_id=wallet.id,
                    transaction_type=TransactionType.CREDIT,
                    amount_jod=MILESTONE_BONUS_JOD,
                    balance_after_jod=wallet.available_balance_jod,
                    reference_id=engagement.id,
                    description=f"Milestone bonus: {strategist.milestone_count * MILESTONE_EVERY} engagements completed",
                )
                db.add(tx)

    return engagement
