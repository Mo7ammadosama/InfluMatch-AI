"""
InfluMatch.jo — Escrow Router
State machine transitions + finance queries
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.escrow import EscrowTransaction
from app.schemas.escrow import EscrowRead, EscrowStateTransition
from app.middleware.auth_middleware import get_current_user, require_role
from app.services.escrow_service import escrow_service

router = APIRouter()


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


@router.get("/", response_model=list[EscrowRead])
async def list_escrows(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    result = await db.execute(select(EscrowTransaction).offset(skip).limit(limit))
    return result.scalars().all()
