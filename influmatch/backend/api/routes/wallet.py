from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from ...core.database import get_db
from ...services.wallet.loyalty_engine import LoyaltyWalletEngine
from ...models.wallet import LoyaltyWallet, WalletTransaction
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
    wallet_id  : int
    points     : int

@router.post("/earn")
async def earn_points(req: EarnRequest, db: AsyncSession = Depends(get_db)):
    """Award loyalty points for merchant actions"""
    result = await engine.earn_points(db, req.wallet_id, req.event, req.amount_jod)
    return result

@router.post("/redeem")
async def redeem_points(req: RedeemRequest, db: AsyncSession = Depends(get_db)):
    """Redeem loyalty points for JOD discount"""
    if req.points < engine.MIN_REDEMPTION:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum redemption is {engine.MIN_REDEMPTION} points"
        )

    jod_value = engine.calculate_jod_value(req.points)
    logger.info(f"[ARIA::WALLET] Redeem: {req.points} pts = {jod_value} JOD")

    return {
        "points_redeemed" : req.points,
        "jod_value"       : jod_value,
        "currency"        : "JOD",
        "status"          : "REDEEMED",
        "message"         : f"تم استرداد {req.points} نقطة = {jod_value} JOD خصم"
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

    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found. Create a merchant profile first.")

    # Find or create wallet
    result = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.merchant_id == merchant.id))
    wallet = result.scalar_one_or_none()

    if not wallet:
        # Auto-create wallet on first access
        wallet = LoyaltyWallet(merchant_id=merchant.id, total_points=0, redeemed_points=0)
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
                "event"            : t.event,
                "points"           : t.points,
                "transaction_type" : t.transaction_type.value if t.transaction_type else "earned",
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