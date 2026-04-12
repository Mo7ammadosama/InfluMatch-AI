"""InfluMatch.jo User Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class UserRole(str, enum.Enum):
    MERCHANT = "merchant"
    INFLUENCER = "influencer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    full_name_ar = Column(String)
    full_name_en = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    merchant_profile = relationship("Merchant", back_populates="user", uselist=False)
    influencer_profile = relationship("Influencer", back_populates="user", uselist=False)
    wallet = relationship("LoyaltyWallet", back_populates="user", uselist=False)
    def __repr__(self): return f"<User {self.email}>"
