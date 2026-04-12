"""ARIA Model Writer — run from influmatch/ directory"""
import os

BASE = "C:/InfluMatch_AI/influmatch"

def w(rel_path, content):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  OK  {rel_path}  ({len(content)} bytes)")

w("backend/models/influencer.py", """from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

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
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="influencer_profile")
    campaign_assignments = relationship("CampaignInfluencer", back_populates="influencer")
    def __repr__(self): return f"<Influencer {self.instagram_handle} aria={self.aria_score}>"
""")

w("backend/models/campaign.py", """from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Enum, Boolean
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
""")

w("backend/models/escrow.py", """from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class EscrowStatus(str, enum.Enum):
    PENDING = "pending"
    FUNDED = "funded"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    RELEASED = "released"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    RESOLVED = "resolved"

class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), unique=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    gross_amount = Column(Float, nullable=False)
    vat_amount = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)
    status = Column(Enum(EscrowStatus), default=EscrowStatus.PENDING)
    stripe_payment_intent_id = Column(String)
    funded_at = Column(DateTime)
    auto_release_at = Column(DateTime)
    released_at = Column(DateTime)
    released_by = Column(String)
    dispute_reason = Column(Text)
    dispute_raised_by = Column(Integer)
    dispute_raised_at = Column(DateTime)
    dispute_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="escrow")
    def __repr__(self): return f"<Escrow {self.status} {self.gross_amount} JOD>"
""")

w("backend/models/contract.py", """from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), unique=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    content_ar = Column(Text)
    content_en = Column(Text)
    language = Column(String, default="ar")
    rag_context_used = Column(JSON, default=list)
    generated_by_model = Column(String, default="claude-opus-4-6")
    is_signed_merchant = Column(Boolean, default=False)
    is_signed_influencer = Column(Boolean, default=False)
    signed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="contract")
    def __repr__(self): return f"<Contract campaign={self.campaign_id}>"
""")

w("backend/models/wallet.py", """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class TransactionType(str, enum.Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    BONUS = "bonus"
    REFERRAL = "referral"

class LoyaltyWallet(Base):
    __tablename__ = "loyalty_wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    points_balance = Column(Integer, default=0)
    total_points_earned = Column(Integer, default=0)
    total_points_redeemed = Column(Integer, default=0)
    tier = Column(String, default="BRONZE")
    tier_emoji = Column(String, default="bronze")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("loyalty_wallets.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    points = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    event = Column(String)
    description = Column(Text)
    reference_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    wallet = relationship("LoyaltyWallet", back_populates="transactions")
""")

w("backend/models/__init__.py", """from .user import User, UserRole
from .merchant import Merchant
from .influencer import Influencer
from .campaign import Campaign, CampaignInfluencer, CampaignStatus
from .escrow import EscrowTransaction, EscrowStatus
from .contract import Contract
from .wallet import LoyaltyWallet, WalletTransaction, TransactionType

__all__ = [
    "User", "UserRole", "Merchant", "Influencer",
    "Campaign", "CampaignInfluencer", "CampaignStatus",
    "EscrowTransaction", "EscrowStatus", "Contract",
    "LoyaltyWallet", "WalletTransaction", "TransactionType",
]
""")

print("M03 ALL MODELS WRITTEN OK")
