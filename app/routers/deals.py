"""
WaslAI.jo — Deals Router
Deal lifecycle: propose → accept → execute → complete
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.deal import Deal, DealStatus
from app.models.campaign import Campaign
from app.models.merchant import Merchant
from app.models.influencer import Influencer
from app.schemas.deal import DealCreate, DealRead, DealUpdate
from app.middleware.auth_middleware import get_current_user, require_role
from app.services.escrow_service import escrow_service
from app.config import settings

router = APIRouter()


@router.post("/", response_model=DealRead, status_code=201)
async def propose_deal(
    payload: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    vat = round(payload.agreed_amount_jod * settings.vat_rate, 3)
    fee = round(payload.agreed_amount_jod * settings.escrow_fee_percent, 3)
    total = round(payload.agreed_amount_jod + vat + fee, 3)

    escrow = await escrow_service.create_escrow(
        merchant_id=current_user.id,
        influencer_id=payload.influencer_id,
        agreed_amount_jod=payload.agreed_amount_jod,
        db=db,
    )

    deal = Deal(
        campaign_id=payload.campaign_id,
        influencer_id=payload.influencer_id,
        agreed_amount_jod=payload.agreed_amount_jod,
        vat_amount_jod=vat,
        platform_fee_jod=fee,
        total_amount_jod=total,
        deliverables=payload.deliverables,
        deadline=payload.deadline,
        notes=payload.notes,
        escrow_id=escrow.id,
        status=DealStatus.PROPOSED,
    )
    db.add(deal)
    await db.flush()
    return deal


@router.get("/my", response_model=list[DealRead])
async def my_deals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.INFLUENCER:
        result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
        inf = result.scalar_one_or_none()
        if not inf:
            return []
        result = await db.execute(select(Deal).where(Deal.influencer_id == inf.id))
    else:
        result = await db.execute(select(Deal))
    return result.scalars().all()


@router.patch("/{deal_id}", response_model=DealRead)
async def update_deal(
    deal_id: str,
    payload: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(deal, field, value)
    return deal
