"""
InfluMatch.jo — Campaigns Router
Full campaign lifecycle management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.campaign import Campaign, CampaignStatus
from app.schemas.campaign import CampaignCreate, CampaignRead, CampaignUpdate
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


@router.post("/", response_model=CampaignRead, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile required before creating campaigns")

    campaign = Campaign(merchant_id=merchant.id, **payload.model_dump())
    db.add(campaign)
    merchant.active_campaigns += 1
    await db.flush()
    return campaign


@router.get("/", response_model=list[CampaignRead])
async def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    status_filter: CampaignStatus | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Campaign)
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/my", response_model=list[CampaignRead])
async def my_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        return []
    result = await db.execute(select(Campaign).where(Campaign.merchant_id == merchant.id))
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(
    campaign_id: str,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result2 = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result2.scalar_one_or_none()
    if not merchant or campaign.merchant_id != merchant.id:
        raise HTTPException(status_code=403, detail="Not your campaign")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(campaign, field, value)
    return campaign
