"""
WaslAI.jo — Escrow Router
State machine transitions + finance queries.
Route order: specific paths before parameterised /{escrow_id}.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.escrow import EscrowTransaction, EscrowState
from app.schemas.escrow import EscrowRead, EscrowStateTransition
from app.middleware.auth_middleware import get_current_user, require_role
from app.services.escrow_service import escrow_service

router = APIRouter()


@router.get("/my", response_model=list[EscrowRead])
async def get_my_escrows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.merchant import Merchant
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        return []
    result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.merchant_id == merchant.id)
    )
    return result.scalars().all()


@router.get("/campaign/{campaign_id}", response_model=list[EscrowRead])
async def get_escrow_by_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.deal import Deal
    result = await db.execute(
        select(EscrowTransaction)
        .join(Deal, Deal.escrow_id == EscrowTransaction.id)
        .where(Deal.campaign_id == campaign_id)
    )
    return result.scalars().all()


@router.get("/", response_model=list[EscrowRead])
@router.get("", response_model=list[EscrowRead])
async def list_escrows(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    result = await db.execute(select(EscrowTransaction).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{escrow_id}", response_model=EscrowRead)
async def get_escrow(
    escrow_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
    escrow = result.scalar_one_or_none()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    return escrow


@router.post("/{escrow_id}/transition", response_model=EscrowRead)
async def transition_escrow(
    escrow_id: str,
    payload: EscrowStateTransition,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT, UserRole.ADMIN)),
):
    escrow = await escrow_service.transition(
        escrow_id=escrow_id,
        target_state=payload.target_state,
        db=db,
        reason=payload.reason,
    )
    return escrow


@router.post("/{escrow_id}/release", response_model=EscrowRead)
async def release_escrow(
    escrow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT, UserRole.ADMIN)),
):
    result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
    escrow = result.scalar_one_or_none()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    if escrow.state not in (EscrowState.FUNDED, EscrowState.LOCKED):
        raise HTTPException(status_code=400, detail=f"Cannot release escrow in state: {escrow.state}")
    escrow.state = EscrowState.RELEASED
    return escrow


@router.post("/{escrow_id}/dispute", response_model=EscrowRead)
async def dispute_escrow(
    escrow_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
    escrow = result.scalar_one_or_none()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    if escrow.state not in (EscrowState.FUNDED, EscrowState.LOCKED):
        raise HTTPException(status_code=400, detail=f"Cannot dispute escrow in state: {escrow.state}")
    escrow.state = EscrowState.DISPUTED
    escrow.dispute_reason = payload.get("reason", "")
    return escrow
