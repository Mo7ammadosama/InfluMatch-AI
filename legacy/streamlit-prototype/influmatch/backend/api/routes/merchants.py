from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from ...core.database import get_db
from ...models.merchant import Merchant
from ...models.campaign import Campaign, CampaignStatus
from ...models.wallet import LoyaltyWallet
from ..dependencies.auth_deps import get_current_user
from ...models.user import User
from loguru import logger

router = APIRouter(prefix="/merchants", tags=["Merchants"])

class MerchantCreate(BaseModel):
    business_name_ar    : str
    business_name_en    : Optional[str]  = None
    business_type       : Optional[str]  = None
    industry            : Optional[str]  = None
    commercial_reg_no   : Optional[str]  = None
    website             : Optional[str]  = None
    city                : str            = "Amman"

class MerchantUpdate(BaseModel):
    business_name_ar    : Optional[str] = None
    business_name_en    : Optional[str] = None
    business_type       : Optional[str] = None
    industry            : Optional[str] = None
    website             : Optional[str] = None
    city                : Optional[str] = None

@router.post("/", status_code=201)
async def create_merchant_profile(
    data: MerchantCreate,
    db  : AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create merchant business profile"""
    # Check if profile already exists
    existing = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Merchant profile already exists")
    merchant = Merchant(user_id=current_user.id, **data.model_dump())
    db.add(merchant)
    await db.flush()
    logger.success(f"[ARIA::MERCHANTS] Profile created: {merchant.id} | {data.business_name_ar}")
    return {"id": merchant.id, "business_name_ar": merchant.business_name_ar}

@router.get("/me")
async def get_my_merchant_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get logged-in merchant's profile + stats"""
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()

    # Count campaigns
    total_q = await db.execute(
        select(Campaign).where(Campaign.merchant_id == (merchant.id if merchant else -1))
    )
    all_campaigns = total_q.scalars().all()
    active_count = sum(1 for c in all_campaigns if c.status == CampaignStatus.ACTIVE)

    # Get wallet points
    wallet_q = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.user_id == current_user.id))
    wallet = wallet_q.scalar_one_or_none()

    if not merchant:
        return {
            "profile_exists": False,
            "total_spent_jod": 0,
            "loyalty_points": wallet.total_points if wallet else 0,
            "total_campaigns": 0,
            "active_campaigns": 0,
            "loyalty_tier": "BRONZE"
        }

    return {
        "profile_exists": True,
        "id": merchant.id,
        "business_name_ar": merchant.business_name_ar,
        "business_name_en": merchant.business_name_en,
        "city": merchant.city,
        "industry": merchant.industry,
        "total_spent_jod": merchant.total_spent_jod,
        "loyalty_tier": merchant.loyalty_tier,
        "is_verified": merchant.is_verified,
        "loyalty_points": wallet.total_points if wallet else 0,
        "total_campaigns": len(all_campaigns),
        "active_campaigns": active_count,
    }

@router.patch("/me")
async def update_my_merchant_profile(
    data: MerchantUpdate,
    db  : AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update logged-in merchant's business profile"""
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(merchant, field, value)
    await db.commit()
    await db.refresh(merchant)
    logger.info(f"[ARIA::MERCHANTS] Profile updated: {merchant.id}")
    return {"message": "Profile updated", "id": merchant.id, "business_name_ar": merchant.business_name_ar}


@router.get("/analytics")
async def get_merchant_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Real campaign + escrow analytics for the logged-in merchant"""
    from ...models.escrow import EscrowTransaction, EscrowStatus
    from sqlalchemy import func

    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        return {
            "profile_exists"       : False,
            "total_campaigns"      : 0,
            "completed_campaigns"  : 0,
            "total_budget_jod"     : 0.0,
            "total_released_jod"   : 0.0,
            "campaign_success_rate": 0.0,
            "campaigns"            : [],
        }

    campaigns_res = await db.execute(
        select(Campaign).where(Campaign.merchant_id == merchant.id)
    )
    campaigns = campaigns_res.scalars().all()

    escrow_res = await db.execute(
        select(func.sum(EscrowTransaction.gross_amount))
        .where(EscrowTransaction.merchant_id == merchant.id)
        .where(EscrowTransaction.status == EscrowStatus.RELEASED)
    )
    total_released = float(escrow_res.scalar() or 0)

    completed      = sum(1 for c in campaigns if c.status == CampaignStatus.COMPLETED)
    total_budget   = sum(float(c.total_budget or 0) for c in campaigns)
    success_rate   = round((completed / len(campaigns) * 100) if campaigns else 0.0, 1)

    campaign_data = [
        {
            "id"        : c.id,
            "title"     : c.title_en or c.title_ar,
            "status"    : c.status.value if c.status else "draft",
            "budget"    : float(c.total_budget or 0),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in campaigns
    ]

    return {
        "profile_exists"       : True,
        "total_campaigns"      : len(campaigns),
        "completed_campaigns"  : completed,
        "total_budget_jod"     : total_budget,
        "total_released_jod"   : total_released,
        "campaign_success_rate": success_rate,
        "campaigns"            : campaign_data,
    }


@router.get("/{merchant_id}")
async def get_merchant(merchant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant