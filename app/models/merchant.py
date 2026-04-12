"""
InfluMatch.jo — Merchant Model
Business entity in Jordan market
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Business Identity
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_name_ar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Jordan-specific
    commercial_registration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tax_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Amman")
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Finance
    total_spent_jod: Mapped[float] = mapped_column(Float, default=0.0)
    active_campaigns: Mapped[int] = mapped_column(default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="merchant_profile")
    campaigns: Mapped[list["Campaign"]] = relationship("Campaign", back_populates="merchant")

    def __repr__(self) -> str:
        return f"<Merchant {self.business_name}>"
