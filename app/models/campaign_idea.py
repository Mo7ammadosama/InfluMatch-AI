"""
WaslAI.jo — Campaign Idea Model
Public creative pitch by a Creative Strategist
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, JSON, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CampaignIdeaStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class CampaignIdea(Base):
    __tablename__ = "campaign_ideas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creative_strategist_id: Mapped[str] = mapped_column(String(36), ForeignKey("creative_strategists.id"), nullable=False, index=True)

    # Bilingual content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campaign spec
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_platforms: Mapped[list] = mapped_column(JSON, default=list)
    content_format: Mapped[list] = mapped_column(JSON, default=list)
    influencer_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Estimates
    estimated_budget_jod: Mapped[float | None] = mapped_column(Float, nullable=True)
    timeline_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status & analytics
    status: Mapped[CampaignIdeaStatus] = mapped_column(Enum(CampaignIdeaStatus), default=CampaignIdeaStatus.OPEN)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    adoption_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    creative_strategist: Mapped["CreativeStrategist"] = relationship("CreativeStrategist", back_populates="ideas")
    engagements: Mapped[list["CreativeEngagement"]] = relationship("CreativeEngagement", back_populates="campaign_idea")

    def __repr__(self) -> str:
        return f"<CampaignIdea {self.title} [{self.status}]>"
