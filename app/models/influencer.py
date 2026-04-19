"""
WaslAI.jo — Influencer Model
Content creator entity — Jordan & MENA region
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Profile
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Amman")

    # Social Platforms (JSON: {platform: {handle, followers, engagement_rate}})
    social_platforms: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metrics
    total_followers: Mapped[int] = mapped_column(Integer, default=0)
    avg_engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    content_categories: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=lambda: ["ar", "en"])

    # Pricing (JOD)
    rate_per_post_jod: Mapped[float] = mapped_column(Float, default=0.0)
    rate_per_story_jod: Mapped[float] = mapped_column(Float, default=0.0)
    rate_per_reel_jod: Mapped[float] = mapped_column(Float, default=0.0)

    # AI Embedding reference
    embedding_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Performance
    total_earned_jod: Mapped[float] = mapped_column(Float, default=0.0)
    completed_deals: Mapped[int] = mapped_column(Integer, default=0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="influencer_profile")
    deals: Mapped[list["Deal"]] = relationship("Deal", back_populates="influencer")

    def __repr__(self) -> str:
        return f"<Influencer {self.display_name} | {self.total_followers:,} followers>"
