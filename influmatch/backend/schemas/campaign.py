from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.campaign import CampaignStatus

class CampaignCreate(BaseModel):
    title_ar:               str
    title_en:               Optional[str]   = None
    description_ar:         Optional[str]   = None
    description_en:         Optional[str]   = None
    niche:                  str
    total_budget:           float
    budget_per_influencer:  Optional[float] = None
    start_date:             Optional[datetime] = None
    end_date:               Optional[datetime] = None
    submission_deadline:    Optional[datetime] = None
    required_deliverables:  List[str]       = []
    hashtags:               List[str]       = []

    model_config = {"from_attributes": True}

class CampaignResponse(BaseModel):
    id:                     int
    merchant_id:            int
    title_ar:               str
    title_en:               Optional[str]
    niche:                  str
    total_budget:           float
    status:                 CampaignStatus
    start_date:             Optional[datetime]
    end_date:               Optional[datetime]
    created_at:             datetime

    model_config = {"from_attributes": True}
# ============================================================