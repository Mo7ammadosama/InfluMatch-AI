"""
WaslAI.jo — Campaign Idea & Creative Engagement Models
Creative Strategists publish ideas; Merchants hire them through engagements.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, DateTime, JSON, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class IdeaStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class CreativeEngagementStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignIdea(Base):
    __tablename__ = "campaign_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_platforms: Mapped[list] = mapped_column(JSON, default=list)
    content_format: Mapped[list] = mapped_column(JSON, default=list)
    influencer_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_budget_jod: Mapped[float | None] = mapped_column(Float, nullable=True)
    timeline_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[IdeaStatus] = mapped_column(Enum(IdeaStatus), default=IdeaStatus.OPEN)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    adoption_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    engagements: Mapped[list["CreativeEngagement"]] = relationship("CreativeEngagement", back_populates="idea")

    def __repr__(self) -> str:
        return f"<CampaignIdea {self.id[:8]} [{self.status}]>"


class CreativeEngagement(Base):
    __tablename__ = "creative_engagements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_idea_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaign_ideas.id"), nullable=False, index=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    strategist_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    status: Mapped[CreativeEngagementStatus] = mapped_column(Enum(CreativeEngagementStatus), default=CreativeEngagementStatus.PENDING)
    agreed_fee_jod: Mapped[float] = mapped_column(Float, default=0.0)
    merchant_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategist_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    idea: Mapped["CampaignIdea"] = relationship("CampaignIdea", back_populates="engagements")

    def __repr__(self) -> str:
        return f"<CreativeEngagement {self.id[:8]} [{self.status}]>"
