"""
WaslAI.jo — Content Creator Engagement Model
Private creative engagement between a Merchant and a Content Creator.
idea_brief is strictly private — only the two participants may ever read it.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CCEngagementStatus(str, enum.Enum):
    ACTIVE = "active"
    IDEA_SUBMITTED = "idea_submitted"
    IDEA_APPROVED = "idea_approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CCEngagement(Base):
    __tablename__ = "cc_engagements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_request_id: Mapped[str] = mapped_column(String(36), ForeignKey("booking_requests.id"), nullable=False, unique=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    content_creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_creators.id"), nullable=False, index=True)
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)

    status: Mapped[CCEngagementStatus] = mapped_column(Enum(CCEngagementStatus), default=CCEngagementStatus.ACTIVE)

    # Finance — platform collects agreed_fee from merchant; creator receives their share from commission
    agreed_fee_jod: Mapped[float] = mapped_column(Float, default=0.0)
    platform_share_percent: Mapped[float] = mapped_column(Float, default=15.00)

    # PRIVATE — only visible to direct participants (merchant + creator)
    idea_brief: Mapped[str | None] = mapped_column(Text, nullable=True)
    idea_brief_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    merchant_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator_rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    booking_request: Mapped["BookingRequest"] = relationship("BookingRequest", back_populates="engagement")
    merchant: Mapped["Merchant"] = relationship("Merchant")
    content_creator: Mapped["ContentCreator"] = relationship("ContentCreator", back_populates="engagements")
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="cc_engagement", foreign_keys="Campaign.cc_engagement_id")

    def __repr__(self) -> str:
        return f"<CCEngagement {self.id[:8]} [{self.status}]>"
