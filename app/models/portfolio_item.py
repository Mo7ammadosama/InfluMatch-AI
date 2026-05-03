"""
WaslAI.jo — Portfolio Item Model
Content Creator's published style samples and creative approach examples
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_creators.id"), nullable=False, index=True)

    # Bilingual title & description
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Campaign classification
    campaign_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_categories: Mapped[list] = mapped_column(JSON, default=list)
    platforms: Mapped[list] = mapped_column(JSON, default=list)
    content_formats: Mapped[list] = mapped_column(JSON, default=list)

    # Generalized example concept — NOT a tailored campaign idea
    example_concept: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_concept_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    content_creator: Mapped["ContentCreator"] = relationship("ContentCreator", back_populates="portfolio_items")

    def __repr__(self) -> str:
        return f"<PortfolioItem '{self.title}' | {'published' if self.is_published else 'draft'}>"
