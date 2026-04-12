from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    title_ar = Column(String, nullable=False)
    title_en = Column(String)
    description_ar = Column(String)
    description_en = Column(String)
    niche = Column(String)
    total_budget = Column(Float, nullable=False)
    budget_per_influencer = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    submission_deadline = Column(DateTime)
    required_deliverables = Column(JSON, default=list)
    target_audience = Column(JSON, default=dict)
    hashtags = Column(JSON, default=list)
    target_cities = Column(JSON, default=list)
    min_followers = Column(Integer, default=1000)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    guardian_job_id = Column(String)
    ai_audit_result = Column(JSON)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    merchant = relationship("Merchant", back_populates="campaigns")
    influencer_assignments = relationship("CampaignInfluencer", back_populates="campaign")
    escrow = relationship("EscrowTransaction", back_populates="campaign", uselist=False)
    contract = relationship("Contract", back_populates="campaign", uselist=False)
    def __repr__(self): return f"<Campaign {self.title_en} [{self.status}]>"

class CampaignInfluencer(Base):
    __tablename__ = "campaign_influencers"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    status = Column(String, default="invited")
    agreed_rate_jod = Column(Float)
    content_url = Column(String)
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    audit_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="influencer_assignments")
    influencer = relationship("Influencer", back_populates="campaign_assignments")
