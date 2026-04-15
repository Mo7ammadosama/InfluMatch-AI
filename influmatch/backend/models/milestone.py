from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class MilestoneStatus(str, enum.Enum):
    PENDING  = "pending"
    RELEASED = "released"
    DISPUTED = "disputed"


class CampaignMilestone(Base):
    __tablename__ = "campaign_milestones"

    id          = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    title       = Column(String, nullable=False)
    percentage  = Column(Float, nullable=False)
    amount_jod  = Column(Float, nullable=False)
    status      = Column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING)
    due_date    = Column(DateTime, nullable=False)
    released_at = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("Campaign", back_populates="milestones")

    def __repr__(self):
        return f"<Milestone {self.title} {self.percentage}% [{self.status}]>"
