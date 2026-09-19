from sqlalchemy import (Column, Integer, String, Float,
                         ForeignKey, DateTime, Enum, Text)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class EscrowStatus(str, enum.Enum):
    PENDING        = "pending"
    FUNDED         = "funded"
    IN_PROGRESS    = "in_progress"
    UNDER_REVIEW   = "under_review"
    RELEASED       = "released"
    DISPUTED       = "disputed"
    REFUNDED       = "refunded"
    CANCELLED      = "cancelled"

class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id                  = Column(Integer, primary_key=True, index=True)
    campaign_id         = Column(Integer, ForeignKey("campaigns.id"), unique=True)
    merchant_id         = Column(Integer, ForeignKey("merchants.id"))

    # Financial (JOD)
    gross_amount        = Column(Float, nullable=False)
    vat_amount          = Column(Float, nullable=False)
    platform_fee        = Column(Float, nullable=False)
    net_amount          = Column(Float, nullable=False)

    # Status Machine
    status              = Column(Enum(EscrowStatus),
                                 default=EscrowStatus.PENDING)

    # Timestamps
    created_at          = Column(DateTime, default=datetime.utcnow)
    funded_at           = Column(DateTime)
    released_at         = Column(DateTime)
    auto_release_at     = Column(DateTime)
    refunded_at         = Column(DateTime)

    # Release metadata
    released_by         = Column(String)           # "guardian_agent"|"admin"|"merchant"

    # Dispute fields
    dispute_reason      = Column(Text)
    dispute_raised_by   = Column(Integer, ForeignKey("users.id"))
    dispute_raised_at   = Column(DateTime)
    dispute_deadline    = Column(DateTime)
    dispute_resolved_at = Column(DateTime)
    dispute_resolution  = Column(Text)

    # Payment reference
    stripe_payment_id   = Column(String)
    stripe_transfer_id  = Column(String)

    # Relationships
    campaign            = relationship("Campaign", back_populates="escrow")
# ============================================================