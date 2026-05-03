"""
WaslAI.jo — Content Creator Model
Early-stage creative partner entity — Jordan B2B platform
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ContentCreator(Base):
    __tablename__ = "content_creators"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Profile
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Skills & metadata (JSON arrays)
    specializations: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=lambda: ["Arabic", "English"])
    content_categories: Mapped[list] = mapped_column(JSON, default=list)

    # Pricing
    consultation_rate_jod: Mapped[float] = mapped_column(Float, default=0.0)

    # Performance metrics
    completed_engagements: Mapped[int] = mapped_column(Integer, default=0)
    total_earned_jod: Mapped[float] = mapped_column(Float, default=0.0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # AI matching
    embedding_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="content_creator_profile")
    portfolio_items: Mapped[list["PortfolioItem"]] = relationship("PortfolioItem", back_populates="content_creator")
    booking_requests: Mapped[list["BookingRequest"]] = relationship("BookingRequest", back_populates="content_creator")
    engagements: Mapped[list["CCEngagement"]] = relationship("CCEngagement", back_populates="content_creator")

    def __repr__(self) -> str:
        return f"<ContentCreator {self.display_name} | {self.completed_engagements} engagements>"
