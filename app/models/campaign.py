"""
InfluMatch.jo — Campaign Model
Marketing campaign lifecycle entity
"""
import enum
import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, JSON, Date, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)

    # Campaign Identity
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Requirements
    target_categories: Mapped[list] = mapped_column(JSON, default=list)
    required_platforms: Mapped[list] = mapped_column(JSON, default=list)
    min_followers: Mapped[int] = mapped_column(Integer, default=1000)
    min_engagement_rate: Mapped[float] = mapped_column(Float, default=0.01)
    preferred_languages: Mapped[list] = mapped_column(JSON, default=lambda: ["ar"])
    target_cities: Mapped[list] = mapped_column(JSON, default=lambda: ["Amman"])

    # Deliverables
    deliverables: Mapped[dict] = mapped_column(JSON, default=dict)

    # Finance (JOD)
    total_budget_jod: Mapped[float] = mapped_column(Float, nullable=False)
    spent_budget_jod: Mapped[float] = mapped_column(Float, default=0.0)
    max_influencers: Mapped[int] = mapped_column(Integer, default=1)

    # Timeline
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status & AI
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    ai_brief_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="campaigns")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates="campaign")

    def __repr__(self) -> str:
        return f"<Campaign '{self.title}' [{self.status}] {self.total_budget_jod} JOD>"
