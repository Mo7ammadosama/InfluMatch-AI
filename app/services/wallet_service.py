"""
InfluMatch.jo — Wallet & Loyalty Points Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from loguru import logger
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.user import User


from app.config import settings
POINTS_PER_JOD = int(1 / settings.loyalty_points_rate) if settings.loyalty_points_rate > 0 else 20


class WalletService:

    async def get_or_create_wallet(self, user_id: str, db: AsyncSession) -> Wallet:
        result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            await db.flush()
        return wallet

    async def credit(
        self,
        user_id: str,
        amount_jod: float,
        tx_type: TransactionType,
        reference_id: str | None,
        description: str | None,
        db: AsyncSession,
    ) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id, db)
        wallet.available_balance_jod = round(wallet.available_balance_jod + amount_jod, 3)

        points_earned = int(amount_jod * POINTS_PER_JOD)
        wallet.points_balance += points_earned
        wallet.total_points_earned += points_earned

        tx = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=tx_type,
            amount_jod=amount_jod,
            points_delta=points_earned,
            balance_after_jod=wallet.available_balance_jod,
            reference_id=reference_id,
            description=description,
        )
        db.add(tx)
        logger.info(f"Wallet credit: user={user_id} +{amount_jod} JOD | +{points_earned} pts")
        return tx

    async def debit(
        self,
        user_id: str,
        amount_jod: float,
        tx_type: TransactionType,
        reference_id: str | None,
        description: str | None,
        db: AsyncSession,
    ) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id, db)
        if wallet.available_balance_jod < amount_jod:
            raise HTTPException(status_code=402, detail="Insufficient wallet balance")

        wallet.available_balance_jod = round(wallet.available_balance_jod - amount_jod, 3)
        tx = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=tx_type,
            amount_jod=-amount_jod,
            points_delta=0,
            balance_after_jod=wallet.available_balance_jod,
            reference_id=reference_id,
            description=description,
        )
        db.add(tx)
        logger.info(f"Wallet debit: user={user_id} -{amount_jod} JOD")
        return tx


wallet_service = WalletService()
