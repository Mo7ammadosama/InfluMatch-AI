"""
WaslAI.jo — Deal Model
Binding agreement between Merchant and Influencer
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DealStatus(str, enum.Enum):
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    CONTENT_SUBMITTED = "content_submitted"
    CONTENT_APPROVED = "content_approved"
    AMOUNT_TRANSFERRED = "amount_transferred"
    PUBLISHED = "published"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=True)
    influencer_id: Mapped[str] = mapped_column(String(36), ForeignKey("influencers.id"), nullable=False)

    # Terms
    agreed_amount_jod: Mapped[float] = mapped_column(Float, nullable=False)
    vat_amount_jod: Mapped[float] = mapped_column(Float, default=0.0)
    platform_fee_jod: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount_jod: Mapped[float] = mapped_column(Float, nullable=False)
    deliverables: Mapped[dict] = mapped_column(JSON, default=dict)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status & Content
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus), default=DealStatus.PROPOSED)
    content_urls: Mapped[list] = mapped_column(JSON, default=list)
    content_verified_by_ai: Mapped[bool] = mapped_column(default=False)
    merchant_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    influencer_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Escrow reference
    escrow_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("escrow_transactions.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="deals")
    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="deals")
    escrow: Mapped["EscrowTransaction"] = relationship("EscrowTransaction", back_populates="deal", foreign_keys=[escrow_id])

    def __repr__(self) -> str:
        return f"<Deal {self.id[:8]} | {self.status} | {self.total_amount_jod} JOD>"
