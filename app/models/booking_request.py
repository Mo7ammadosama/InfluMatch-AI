"""
WaslAI.jo — Booking Request Model
Merchant → Content Creator booking initiation (Discovery Path A)
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class BookingRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    content_creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_creators.id"), nullable=False, index=True)
    portfolio_item_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("portfolio_items.id"), nullable=True)

    # Merchant business brief
    business_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    campaign_goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_jod: Mapped[float | None] = mapped_column(Float, nullable=True)
    timeline_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status & communication
    status: Mapped[BookingRequestStatus] = mapped_column(Enum(BookingRequestStatus), default=BookingRequestStatus.PENDING)
    merchant_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant")
    content_creator: Mapped["ContentCreator"] = relationship("ContentCreator", back_populates="booking_requests")
    portfolio_item: Mapped["PortfolioItem"] = relationship("PortfolioItem")
    engagement: Mapped["CCEngagement"] = relationship("CCEngagement", back_populates="booking_request", uselist=False)

    def __repr__(self) -> str:
        return f"<BookingRequest {self.id[:8]} [{self.status}]>"
