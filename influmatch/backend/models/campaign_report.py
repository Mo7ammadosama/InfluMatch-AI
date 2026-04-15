from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class ReportStatus(str, enum.Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CampaignReport(Base):
    __tablename__ = "campaign_reports"

    id            = Column(Integer, primary_key=True, index=True)
    campaign_id   = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    influencer_id = Column(Integer, ForeignKey("influencers.id"), nullable=False)
    file_path     = Column(String, nullable=False)
    status        = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    uploaded_at   = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CampaignReport campaign={self.campaign_id} [{self.status}]>"
