from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base
# ── NOTE: audience_gender_split, audience_age_split, available_from/until added v2

class Influencer(Base):
    __tablename__ = "influencers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio_ar = Column(String)
    bio_en = Column(String)
    niche = Column(String)
    city = Column(String, default="Amman")
    avatar_url = Column(String)
    instagram_handle = Column(String)
    instagram_followers = Column(Integer, default=0)
    instagram_following = Column(Integer, default=0)
    instagram_engagement_rate = Column(Float, default=0.0)
    tiktok_handle = Column(String)
    tiktok_followers = Column(Integer, default=0)
    tiktok_engagement_rate = Column(Float, default=0.0)
    youtube_handle = Column(String)
    youtube_subscribers = Column(Integer, default=0)
    youtube_engagement_rate = Column(Float, default=0.0)
    aria_score = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    delivery_score = Column(Float, default=0.0)
    aria_tier = Column(String, default="UNRANKED")
    rate_per_post = Column(Float, default=0.0)
    rate_per_story = Column(Float, default=0.0)
    rate_per_reel = Column(Float, default=0.0)
    campaigns_completed = Column(Integer, default=0)
    campaigns_total = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    disputes_raised = Column(Integer, default=0)
    monthly_growth_rate = Column(Float, default=0.0)
    account_age_days = Column(Integer, default=365)
    score_metadata = Column(JSON, default=dict)
    last_scored_at = Column(DateTime)
    is_available           = Column(Boolean, default=True)
    audience_gender_split  = Column(JSON, nullable=True)   # {"female":70,"male":30}
    audience_age_split     = Column(JSON, nullable=True)   # {"18-24":40,"25-34":35,"35+":25}
    available_from         = Column(DateTime, nullable=True)
    available_until        = Column(DateTime, nullable=True)
    stripe_connect_account_id = Column(String, nullable=True)   # Stripe Connect acct_xxx
    content_quality_score     = Column(Float, default=70.0)     # last AI audit score (0-100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="influencer_profile")
    campaign_assignments = relationship("CampaignInfluencer", back_populates="influencer")
    def __repr__(self): return f"<Influencer {self.instagram_handle} aria={self.aria_score}>"
