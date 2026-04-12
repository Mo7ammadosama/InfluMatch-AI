from typing import Dict
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.core.config import get_settings

settings = get_settings()

class LoyaltyWalletEngine:
    EVENTS = {
        "campaign_published": 100, "campaign_completed": 200,
        "positive_review": 50, "merchant_referral": 500,
        "profile_completed": 75, "first_campaign": 250,
    }
    REDEMPTION_RATE = 0.01
    MIN_REDEMPTION = 500

    def get_points_for_event(self, event: str, amount_jod: float = 0) -> int:
        if event == "spend_bonus":
            return int(amount_jod * settings.loyalty_points_rate * 100)
        return self.EVENTS.get(event, 0)

    def calculate_jod_value(self, points: int) -> float:
        if points < self.MIN_REDEMPTION: return 0.0
        return round(points * self.REDEMPTION_RATE, 3)

    def get_tier(self, total_points: int) -> Dict:
        if total_points >= 50000: return {"tier": "PLATINUM", "emoji": "diamond", "discount": 0.20}
        if total_points >= 20000: return {"tier": "GOLD", "emoji": "gold", "discount": 0.15}
        if total_points >= 5000:  return {"tier": "SILVER", "emoji": "silver", "discount": 0.10}
        return {"tier": "BRONZE", "emoji": "bronze", "discount": 0.05}

    def earn_points_summary(self, event: str, amount_jod: float = 0) -> Dict:
        pts = self.get_points_for_event(event, amount_jod)
        logger.info(f"[ARIA::WALLET] +{pts} pts | event={event}")
        return {"points_earned": pts, "event": event, "jod_equivalent": self.calculate_jod_value(pts)}

    async def earn_points(self, db, wallet_id: int, event: str, amount_jod: float = 0) -> Dict:
        """Award points to a wallet (async, DB-backed)"""
        from sqlalchemy import select
        from backend.models.wallet import LoyaltyWallet, WalletTransaction, TransactionType
        pts = self.get_points_for_event(event, amount_jod)
        result = await db.execute(
            select(LoyaltyWallet).where(LoyaltyWallet.id == wallet_id)
        )
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise ValueError(f"Wallet {wallet_id} not found")
        wallet.total_points += pts
        new_tier = self.get_tier(wallet.total_points)
        wallet.tier = new_tier["tier"]
        tx = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type=TransactionType.EARN_CAMPAIGN_PUBLISHED,
            points=pts,
            balance_after=wallet.total_points,
            description_en=f"Earned {pts} pts for {event}",
            description_ar=f"اكتسبت {pts} نقطة",
            reference_id=str(wallet_id)
        )
        db.add(tx)
        await db.commit()
        logger.info(f"[ARIA::WALLET] +{pts} pts | wallet={wallet_id} | event={event}")
        return {
            "points_earned"   : pts,
            "total_points"    : wallet.total_points,
            "tier"            : new_tier,
            "event"           : event,
            "jod_equivalent"  : self.calculate_jod_value(pts)
        }

wallet_engine = LoyaltyWalletEngine()
