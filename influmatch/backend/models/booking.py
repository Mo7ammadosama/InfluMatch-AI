from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class BookingStatus(str, enum.Enum):
    PENDING           = "pending"
    CONFIRMED         = "confirmed"
    CONTENT_SUBMITTED = "content_submitted"
    CONTENT_APPROVED  = "content_approved"
    RELEASED          = "released"
    DISPUTED          = "disputed"
    CANCELLED         = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id                   = Column(Integer, primary_key=True, index=True)
    merchant_id          = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    influencer_id        = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    campaign_id          = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    agreed_rate_jod      = Column(Float, nullable=False)
    brief                = Column(String, nullable=True)
    deliverables         = Column(JSON, nullable=True)
    deadline             = Column(DateTime, nullable=True)
    status               = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
    content_url          = Column(String, nullable=True)
    content_submitted_at = Column(DateTime, nullable=True)
    content_approved_at  = Column(DateTime, nullable=True)
    ai_review_result     = Column(JSON, nullable=True)
    escrow_id            = Column(Integer, ForeignKey("escrow_transactions.id"), nullable=True)
    created_at           = Column(DateTime, default=datetime.utcnow)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    merchant   = relationship("Merchant")
    influencer = relationship("Influencer")
