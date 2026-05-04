"""
WaslAI.jo — Campaigns Router
Full campaign lifecycle management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.campaign import Campaign, CampaignStatus
from app.models.cc_engagement import CCEngagement, CCEngagementStatus
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

    cc_engagement_id = payload.cc_engagement_id

    # Validate the cc_engagement belongs to this merchant and is approved
    if cc_engagement_id:
        eng_result = await db.execute(
            select(CCEngagement).where(
                CCEngagement.id == cc_engagement_id,
                CCEngagement.merchant_id == merchant.id,
            )
        )
        cc_eng = eng_result.scalar_one_or_none()
        if not cc_eng:
            raise HTTPException(status_code=404, detail="CC Engagement not found or not yours")
        if cc_eng.status not in (CCEngagementStatus.IDEA_APPROVED, CCEngagementStatus.ACTIVE):
            raise HTTPException(status_code=400, detail="Engagement must be in idea_approved or active status to link")

    campaign = Campaign(merchant_id=merchant.id, **payload.model_dump())
    db.add(campaign)
    merchant.active_campaigns += 1
    await db.flush()  # assign campaign.id

    # Back-link the engagement to this campaign
    if cc_engagement_id and cc_eng:
        cc_eng.campaign_id = campaign.id
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


@router.post("/{campaign_id}/activate", response_model=CampaignRead)
async def activate_campaign(
    campaign_id: str,
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
    campaign.status = CampaignStatus.ACTIVE
    return campaign


@router.post("/{campaign_id}/apply")
async def apply_to_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != CampaignStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Campaign is not accepting applications")
    return {"message": "Application submitted", "campaign_id": campaign_id}


@router.delete("/{campaign_id}", status_code=204)
async def delete_campaign(
    campaign_id: str,
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
    campaign.status = CampaignStatus.CANCELLED
    merchant.active_campaigns = max(0, merchant.active_campaigns - 1)
