from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from ...core.database import get_db
from ...services.wallet.loyalty_engine import LoyaltyWalletEngine
from ...models.wallet import LoyaltyWallet, WalletTransaction, TransactionType
from ...models.merchant import Merchant
from ...models.user import User
from ..dependencies.auth_deps import get_current_user
from loguru import logger

router = APIRouter(prefix="/wallet", tags=["Loyalty Wallet"])
engine = LoyaltyWalletEngine()

class EarnRequest(BaseModel):
    wallet_id  : int
    event      : str
    amount_jod : float = 0.0

class RedeemRequest(BaseModel):
    points: int

@router.post("/earn")
async def earn_points(req: EarnRequest, db: AsyncSession = Depends(get_db)):
    """Award loyalty points for merchant actions"""
    result = await engine.earn_points(db, req.wallet_id, req.event, req.amount_jod)
    return result

@router.post("/redeem")
async def redeem_points(
    req: RedeemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Redeem loyalty points for JOD discount (user-authenticated)"""
    if req.points < engine.MIN_REDEMPTION:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum redemption is {engine.MIN_REDEMPTION} points"
        )

    # Load wallet
    result = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    available = wallet.total_points - wallet.redeemed_points
    if req.points > available:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient points. Available: {available}"
        )

    jod_value = engine.calculate_jod_value(req.points)
    wallet.redeemed_points += req.points

    tx = WalletTransaction(
        wallet_id        = wallet.id,
        transaction_type = TransactionType.REDEEM_DISCOUNT,
        points           = -req.points,
        balance_after    = wallet.total_points - wallet.redeemed_points,
        description_en   = f"Redeemed {req.points} pts for {jod_value} JOD discount",
        description_ar   = f"استرداد {req.points} نقطة = {jod_value} JOD خصم",
    )
    db.add(tx)
    await db.commit()

    logger.info(f"[ARIA::WALLET] Redeem: {req.points} pts = {jod_value} JOD | user={current_user.id}")
    return {
        "points_redeemed" : req.points,
        "jod_value"       : jod_value,
        "currency"        : "JOD",
        "status"          : "REDEEMED",
        "message"         : f"تم استرداد {req.points} نقطة = {jod_value} JOD خصم",
        "available_points": wallet.total_points - wallet.redeemed_points,
    }

@router.get("/me")
async def get_my_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current merchant's wallet"""
    # Find merchant profile for this user
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()

    # Find or create wallet — search by user_id first, then merchant_id as fallback
    result = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        # fallback: check by merchant_id
        if merchant:
            result = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.merchant_id == merchant.id))
            wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = LoyaltyWallet(user_id=current_user.id, total_points=0, redeemed_points=0)
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)

    tier_info = engine.get_tier(wallet.total_points)
    available = wallet.total_points - wallet.redeemed_points
    jod_value = engine.calculate_jod_value(available)

    # Recent transactions
    txn_result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
        .order_by(WalletTransaction.created_at.desc())
        .limit(20)
    )
    txns = txn_result.scalars().all()

    return {
        "wallet_id"        : wallet.id,
        "total_points"     : wallet.total_points,
        "redeemed_points"  : wallet.redeemed_points,
        "available_points" : available,
        "jod_value"        : jod_value,
        "tier"             : tier_info,
        "currency"         : "JOD",
        "transactions"     : [
            {
                "id"               : t.id,
                "transaction_type" : t.transaction_type.value if t.transaction_type else "earned",
                "points"           : t.points,
                "balance_after"    : t.balance_after,
                "description"      : t.description_en or t.description_ar or "",
                "created_at"       : str(t.created_at),
            } for t in txns
        ]
    }


@router.get("/{wallet_id}")
async def get_wallet(wallet_id: int, db: AsyncSession = Depends(get_db)):
    """Get wallet balance and tier"""
    result = await db.execute(
        select(LoyaltyWallet).where(LoyaltyWallet.id == wallet_id)
    )
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    tier_info = engine.get_tier(wallet.total_points)
    jod_value = engine.calculate_jod_value(wallet.total_points)

    return {
        "wallet_id"       : wallet_id,
        "total_points"    : wallet.total_points,
        "redeemed_points" : wallet.redeemed_points,
        "available_points": wallet.total_points - wallet.redeemed_points,
        "jod_value"       : jod_value,
        "tier"            : tier_info,
        "currency"        : "JOD"
    }
# ============================================================