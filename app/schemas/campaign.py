from pydantic import BaseModel, Field
from datetime import datetime, date
from app.models.campaign import CampaignStatus


class CampaignCreate(BaseModel):
    title: str = Field(..., min_length=3)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    target_categories: list[str] = Field(default_factory=list)
    required_platforms: list[str] = Field(default_factory=list)
    min_followers: int = Field(default=1000, ge=0)
    min_engagement_rate: float = Field(default=0.01, ge=0, le=1)
    preferred_languages: list[str] = Field(default_factory=lambda: ["ar"])
    target_cities: list[str] = Field(default_factory=lambda: ["Amman"])
    deliverables: dict = Field(default_factory=dict)
    total_budget_jod: float = Field(..., ge=50.0)
    max_influencers: int = Field(default=1, ge=1)
    start_date: date | None = None
    end_date: date | None = None
    cc_engagement_id: str | None = None


class CampaignUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: CampaignStatus | None = None
    total_budget_jod: float | None = None
    end_date: date | None = None


class CampaignRead(BaseModel):
    id: str
    merchant_id: str
    title: str
    title_ar: str | None
    description: str | None
    target_categories: list
    required_platforms: list
    min_followers: int
    total_budget_jod: float
    spent_budget_jod: float
    max_influencers: int
    start_date: date | None
    end_date: date | None
    status: CampaignStatus
    ai_brief_summary: str | None
    cc_engagement_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
