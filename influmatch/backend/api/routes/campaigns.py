from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ...core.database import get_db
from ...models.campaign import Campaign, CampaignStatus
from ...models.user import User
from ...schemas.campaign import CampaignCreate, CampaignResponse
from ...agents.guardian_agent import GuardianAgent
from ...services.escrow.escrow_engine import EscrowEngine
from loguru import logger

router  = APIRouter(prefix="/campaigns", tags=["Campaigns"])
escrow  = EscrowEngine()

@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign — Guardian Agent auto-schedules lifecycle events"""

    campaign = Campaign(
        merchant_id             = 1,           # TODO: extract from JWT
        title_ar                = data.title_ar,
        title_en                = data.title_en,
        description_ar          = data.description_ar,
        description_en          = data.description_en,
        niche                   = data.niche,
        total_budget            = data.total_budget,
        budget_per_influencer   = data.budget_per_influencer,
        start_date              = data.start_date,
        end_date                = data.end_date,
        submission_deadline     = data.submission_deadline,
        required_deliverables   = data.required_deliverables,
        hashtags                = data.hashtags,
        status                  = CampaignStatus.DRAFT
    )

    db.add(campaign)
    await db.flush()

    logger.success(f"[ARIA::CAMPAIGNS] Created campaign: {campaign.id} | {data.title_ar}")
    return campaign

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    status: CampaignStatus = None,
    db: AsyncSession = Depends(get_db)
):
    """List all campaigns with optional status filter"""
    query = select(Campaign).offset(skip).limit(limit)
    if status:
        query = query.where(Campaign.status == status)

    result = await db.execute(query)
    campaigns = result.scalars().all()
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.patch("/{campaign_id}/activate")
async def activate_campaign(campaign_id: int, db: AsyncSession = Depends(get_db)):
    """Activate campaign → fund escrow → schedule Guardian jobs"""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = CampaignStatus.ACTIVE

    # Fund escrow
    escrow_tx = await escrow.fund_escrow(
        db, campaign_id, campaign.merchant_id, campaign.total_budget
    )

    logger.success(f"[ARIA::CAMPAIGNS] Activated: {campaign_id} | Escrow: {escrow_tx.id}")
    return {
        "campaign_id"   : campaign_id,
        "status"        : "ACTIVE",
        "escrow_id"     : escrow_tx.id,
        "amount_locked" : escrow_tx.gross_amount,
        "currency"      : "JOD"
    }
# ============================================================