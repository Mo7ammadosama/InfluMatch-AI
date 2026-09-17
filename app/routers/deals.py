"""
WaslAI.jo — Deals/Bookings Router
Deal lifecycle: propose → accept → execute → complete
Also mounted at /bookings for frontend compatibility
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
from app.models.escrow import EscrowTransaction
from app.schemas.deal import DealCreate, DealRead, DealUpdate
from app.middleware.auth_middleware import get_current_user, require_role
from app.services.escrow_service import escrow_service
from app.config import settings

router = APIRouter()


@router.post("", response_model=DealRead, status_code=201)
@router.post("/", response_model=DealRead, status_code=201)
async def propose_deal(
    payload: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    # Resolve merchant profile ID (FK target in escrow/deal tables)
    merch_result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = merch_result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found — complete your profile first")

    vat = round(payload.agreed_amount_jod * settings.vat_rate, 3)
    fee = round(payload.agreed_amount_jod * settings.escrow_fee_percent, 3)
    total = round(payload.agreed_amount_jod + vat + fee, 3)

    escrow = await escrow_service.create_escrow(
        merchant_id=merchant.id,
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
    await db.refresh(deal)
    return deal


@router.get("/my", response_model=list[DealRead])
async def my_deals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.INFLUENCER:
        inf_result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
        inf = inf_result.scalar_one_or_none()
        if not inf:
            return []
        result = await db.execute(select(Deal).where(Deal.influencer_id == inf.id))
    elif current_user.role == UserRole.MERCHANT:
        merch_result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merch = merch_result.scalar_one_or_none()
        if not merch:
            return []
        escrow_result = await db.execute(
            select(EscrowTransaction.id).where(EscrowTransaction.merchant_id == merch.id)
        )
        escrow_ids = [row[0] for row in escrow_result.all()]
        if not escrow_ids:
            return []
        result = await db.execute(select(Deal).where(Deal.escrow_id.in_(escrow_ids)))
    else:
        return []
    return result.scalars().all()


@router.post("/{deal_id}/confirm", response_model=DealRead)
async def confirm_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.status != DealStatus.PROPOSED:
        raise HTTPException(status_code=400, detail="Deal is not in PROPOSED state")
    deal.status = DealStatus.ACCEPTED
    await db.flush()
    await db.refresh(deal)
    return deal


@router.post("/{deal_id}/cancel", response_model=DealRead)
async def cancel_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.status in (DealStatus.COMPLETED, DealStatus.CANCELLED):
        raise HTTPException(status_code=400, detail="Deal already finalized")
    deal.status = DealStatus.CANCELLED
    await db.flush()
    await db.refresh(deal)
    return deal


@router.post("/{deal_id}/submit-content", response_model=DealRead)
async def submit_content(
    deal_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    url = payload.get("content_url") or payload.get("url")
    if url:
        deal.content_urls = [*deal.content_urls, url]
    deal.status = DealStatus.CONTENT_SUBMITTED
    await db.flush()
    await db.refresh(deal)
    return deal


@router.post("/{deal_id}/approve-content", response_model=DealRead)
async def approve_content(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.status != DealStatus.CONTENT_SUBMITTED:
        raise HTTPException(status_code=400, detail="No content submitted yet")
    deal.status = DealStatus.CONTENT_APPROVED
    await db.flush()
    await db.refresh(deal)
    return deal


@router.post("/{deal_id}/release-funds", response_model=DealRead)
async def release_funds(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.status != DealStatus.CONTENT_APPROVED:
        raise HTTPException(status_code=400, detail="Content must be approved before releasing funds")

    if deal.escrow_id:
        escrow_result = await db.execute(
            select(EscrowTransaction).where(EscrowTransaction.id == deal.escrow_id)
        )
        escrow = escrow_result.scalar_one_or_none()
        if escrow:
            from app.models.escrow import EscrowState
            if escrow.state == EscrowState.PENDING:
                await escrow_service.transition(deal.escrow_id, EscrowState.FUNDED, db)
                await escrow_service.transition(deal.escrow_id, EscrowState.LOCKED, db)
            elif escrow.state == EscrowState.FUNDED:
                await escrow_service.transition(deal.escrow_id, EscrowState.LOCKED, db)
            await escrow_service.transition(deal.escrow_id, EscrowState.RELEASED, db, reason="merchant approved content")

    deal.status = DealStatus.AMOUNT_TRANSFERRED
    await db.flush()
    await db.refresh(deal)
    return deal


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
    await db.flush()
    await db.refresh(deal)
    return deal
