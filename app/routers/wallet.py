"""
WaslAI.jo — Wallet Router
GET /me  |  GET /transactions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet, WalletTransaction
from app.middleware.auth_middleware import get_current_user

router = APIRouter()


class WalletRead(BaseModel):
    id: str
    user_id: str
    available_balance_jod: float
    locked_balance_jod: float
    total_balance_jod: float
    points_balance: int
    total_points_earned: int
    points_to_jod_rate: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionRead(BaseModel):
    id: str
    transaction_type: str
    amount_jod: float
    points_delta: int
    balance_after_jod: float
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


async def _get_wallet(user_id: str, db: AsyncSession) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.get("/me", response_model=WalletRead)
async def get_my_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_wallet(current_user.id, db)


@router.get("/transactions", response_model=list[TransactionRead])
async def get_my_transactions(
    skip: int = 0,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wallet = await _get_wallet(current_user.id, db)
    result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
        .order_by(WalletTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
