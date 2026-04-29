"""
WaslAI.jo — Creative Engagement Model
Contract between a Merchant and a Creative Strategist (equivalent to a Deal)
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CreativeEngagementStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CreativeEngagement(Base):
    __tablename__ = "creative_engagements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_idea_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaign_ideas.id"), nullable=False)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    creative_strategist_id: Mapped[str] = mapped_column(String(36), ForeignKey("creative_strategists.id"), nullable=False)

    status: Mapped[CreativeEngagementStatus] = mapped_column(Enum(CreativeEngagementStatus), default=CreativeEngagementStatus.PENDING)
    agreed_fee_jod: Mapped[float] = mapped_column(Float, default=0.0)

    merchant_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategist_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    campaign_idea: Mapped["CampaignIdea"] = relationship("CampaignIdea", back_populates="engagements")
    creative_strategist: Mapped["CreativeStrategist"] = relationship("CreativeStrategist", back_populates="engagements")
    merchant: Mapped["Merchant"] = relationship("Merchant")

    def __repr__(self) -> str:
        return f"<CreativeEngagement {self.id[:8]} [{self.status}]>"
