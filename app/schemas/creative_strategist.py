from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.campaign_idea import CampaignIdeaStatus
from app.models.creative_engagement import CreativeEngagementStatus


# --- Creative Strategist Profile ---

class CreativeStrategistCreate(BaseModel):
    display_name: str = Field(..., min_length=2)
    display_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    portfolio_url: Optional[str] = None
    specializations: list[str] = []
    languages: list[str] = ["Arabic", "English"]
    consultation_rate_jod: float = Field(default=0.0, ge=0)


class CreativeStrategistUpdate(BaseModel):
    display_name: Optional[str] = None
    display_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    portfolio_url: Optional[str] = None
    specializations: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    consultation_rate_jod: Optional[float] = Field(default=None, ge=0)
    is_available: Optional[bool] = None


class CreativeStrategistRead(BaseModel):
    id: str
    user_id: str
    display_name: str
    display_name_ar: Optional[str]
    bio: Optional[str]
    bio_ar: Optional[str]
    avatar_url: Optional[str]
    city: Optional[str]
    portfolio_url: Optional[str]
    specializations: list
    languages: list
    consultation_rate_jod: float
    completed_engagements: int
    milestone_count: int
    total_earned_jod: float
    avg_rating: float
    is_verified: bool
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Campaign Idea ---

class CampaignIdeaCreate(BaseModel):
    title: str = Field(..., min_length=3)
    title_ar: Optional[str] = None
    description: str = Field(..., min_length=10)
    description_ar: Optional[str] = None
    target_audience: Optional[str] = None
    suggested_platforms: list[str] = []
    content_format: list[str] = []
    influencer_type: Optional[str] = None
    business_category: Optional[str] = None
    estimated_budget_jod: Optional[float] = Field(default=None, ge=0)
    timeline_days: Optional[int] = Field(default=None, ge=1)


class CampaignIdeaUpdate(BaseModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    target_audience: Optional[str] = None
    suggested_platforms: Optional[list[str]] = None
    content_format: Optional[list[str]] = None
    influencer_type: Optional[str] = None
    business_category: Optional[str] = None
    estimated_budget_jod: Optional[float] = None
    timeline_days: Optional[int] = None


class CampaignIdeaRead(BaseModel):
    id: str
    creative_strategist_id: str
    title: str
    title_ar: Optional[str]
    description: str
    description_ar: Optional[str]
    target_audience: Optional[str]
    suggested_platforms: list
    content_format: list
    influencer_type: Optional[str]
    business_category: Optional[str]
    estimated_budget_jod: Optional[float]
    timeline_days: Optional[int]
    status: CampaignIdeaStatus
    view_count: int
    adoption_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Creative Engagement ---

class CreativeEngagementCreate(BaseModel):
    campaign_idea_id: str
    agreed_fee_jod: float = Field(default=0.0, ge=0)
    merchant_notes: Optional[str] = None


class CreativeEngagementRead(BaseModel):
    id: str
    campaign_idea_id: str
    merchant_id: str
    creative_strategist_id: str
    status: CreativeEngagementStatus
    agreed_fee_jod: float
    merchant_notes: Optional[str]
    strategist_notes: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
