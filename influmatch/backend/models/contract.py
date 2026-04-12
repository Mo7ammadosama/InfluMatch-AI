from sqlalchemy import (Column, Integer, String, Text,
                         ForeignKey, DateTime, Enum, Boolean)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class ContractStatus(str, enum.Enum):
    DRAFT       = "draft"
    SENT        = "sent"
    SIGNED      = "signed"
    ACTIVE      = "active"
    COMPLETED   = "completed"
    BREACHED    = "breached"
    EXPIRED     = "expired"

class Contract(Base):
    __tablename__ = "contracts"

    id                  = Column(Integer, primary_key=True, index=True)
    campaign_id         = Column(Integer, ForeignKey("campaigns.id"), unique=True)
    merchant_id         = Column(Integer, ForeignKey("merchants.id"))
    influencer_id       = Column(Integer, ForeignKey("influencers.id"))

    # Content (RAG-generated)
    contract_text_ar    = Column(Text)
    contract_text_en    = Column(Text)
    language_primary    = Column(String, default="ar")

    # Status
    status              = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)

    # Signatures (simple hash-based for local dev)
    merchant_signed     = Column(Boolean, default=False)
    merchant_signed_at  = Column(DateTime)
    merchant_sig_hash   = Column(String)

    influencer_signed   = Column(Boolean, default=False)
    influencer_signed_at= Column(DateTime)
    influencer_sig_hash = Column(String)

    # RAG Metadata
    rag_sources_used    = Column(String)           # JSON list of sources
    generated_by        = Column(String, default="ARIA_RAG_v1")

    # Timestamps
    created_at          = Column(DateTime, default=datetime.utcnow)
    activated_at        = Column(DateTime)
    completed_at        = Column(DateTime)
    expires_at          = Column(DateTime)

    # Relationships
    campaign            = relationship("Campaign", back_populates="contract")
# ============================================================