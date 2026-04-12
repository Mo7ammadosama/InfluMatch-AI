from sqlalchemy import (Column, Integer, String, Float,
                         ForeignKey, DateTime, Enum, Text, JSON)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class TransactionType(str, enum.Enum):
    EARN_CAMPAIGN_PUBLISHED  = "earn_campaign_published"
    EARN_CAMPAIGN_COMPLETED  = "earn_campaign_completed"
    EARN_POSITIVE_REVIEW     = "earn_positive_review"
    EARN_REFERRAL            = "earn_referral"
    EARN_SPEND_BONUS         = "earn_spend_bonus"
    EARN_PROFILE_COMPLETE    = "earn_profile_complete"
    EARN_FIRST_CAMPAIGN      = "earn_first_campaign"
    REDEEM_DISCOUNT          = "redeem_discount"
    EXPIRE                   = "expire"
    ADMIN_ADJUST             = "admin_adjust"

class LoyaltyWallet(Base):
    __tablename__ = "loyalty_wallets"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), unique=True)
    merchant_id     = Column(Integer, ForeignKey("merchants.id"),
                             nullable=True, unique=True)

    # Balances
    total_points    = Column(Integer, default=0)
    redeemed_points = Column(Integer, default=0)
    expired_points  = Column(Integer, default=0)

    @property
    def available_points(self):
        return self.total_points - self.redeemed_points - self.expired_points

    # Tier
    tier            = Column(String, default="BRONZE")
    tier_updated_at = Column(DateTime)

    # Timestamps
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow,
                             onupdate=datetime.utcnow)

    # Relationships
    user            = relationship("User", back_populates="wallet")
    merchant        = relationship("Merchant", back_populates="wallet")
    transactions    = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id              = Column(Integer, primary_key=True, index=True)
    wallet_id       = Column(Integer, ForeignKey("loyalty_wallets.id"))
    transaction_type= Column(Enum(TransactionType))
    points          = Column(Integer, nullable=False)       # +earn / -redeem
    balance_after   = Column(Integer, nullable=False)
    description_ar  = Column(String)
    description_en  = Column(String)
    reference_id    = Column(String)                        # campaign_id or order_id
    extra_data      = Column(JSON, default={})
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relationships
    wallet          = relationship("LoyaltyWallet", back_populates="transactions")
# ============================================================