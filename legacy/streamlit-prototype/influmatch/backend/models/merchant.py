from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id                  = Column(Integer, primary_key=True, index=True)
    user_id             = Column(Integer, ForeignKey("users.id"), unique=True)

    # Business Identity
    business_name_ar    = Column(String, nullable=False)
    business_name_en    = Column(String)
    business_type       = Column(String)           # retail|restaurant|services|ecommerce
    industry            = Column(String)           # fashion|food|tech|beauty|etc
    commercial_reg_no   = Column(String)           # Jordan Commercial Registry Number
    tax_number          = Column(String)           # Jordan Tax Number

    # Contact & Location
    website             = Column(String)
    instagram_page      = Column(String)
    city                = Column(String, default="Amman")
    address_ar          = Column(String)
    address_en          = Column(String)

    # Financial
    total_spent_jod     = Column(Float, default=0.0)
    loyalty_tier        = Column(String, default="BRONZE")
    is_verified         = Column(Boolean, default=False)
    verified_at         = Column(DateTime)

    # Metadata
    profile_complete    = Column(Float, default=0.0)   # 0-100%
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow)

    # Relationships
    user                = relationship("User", back_populates="merchant_profile")
    campaigns           = relationship("Campaign", back_populates="merchant")
    wallet              = relationship("LoyaltyWallet", back_populates="merchant",
                                       uselist=False)
# ============================================================