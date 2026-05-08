from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.booking_request import BookingRequestStatus
from app.models.cc_engagement import CCEngagementStatus


# ── Content Creator Profile ────────────────────────────────────────────────────

class ContentCreatorCreate(BaseModel):
    display_name: str = Field(..., min_length=2)
    display_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    portfolio_url: Optional[str] = None
    specializations: list[str] = []
    languages: list[str] = ["Arabic", "English"]
    content_categories: list[str] = []
    consultation_rate_jod: float = Field(default=0.0, ge=0)


class ContentCreatorUpdate(BaseModel):
    display_name: Optional[str] = None
    display_name_ar: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    portfolio_url: Optional[str] = None
    specializations: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    content_categories: Optional[list[str]] = None
    consultation_rate_jod: Optional[float] = Field(default=None, ge=0)
    is_available: Optional[bool] = None


class ContentCreatorRead(BaseModel):
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
    content_categories: list
    consultation_rate_jod: float
    completed_engagements: int
    total_earned_jod: float
    avg_rating: float
    is_verified: bool
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentCreatorSummary(BaseModel):
    id: str
    display_name: str
    display_name_ar: Optional[str]
    avatar_url: Optional[str]
    city: Optional[str]
    specializations: list
    avg_rating: float
    completed_engagements: int
    is_available: bool

    model_config = {"from_attributes": True}


# ── Portfolio Item ─────────────────────────────────────────────────────────────

class PortfolioItemCreate(BaseModel):
    title: str = Field(..., min_length=2)
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    campaign_type: Optional[str] = None
    business_categories: list[str] = []
    platforms: list[str] = []
    content_formats: list[str] = []
    example_concept: Optional[str] = None
    example_concept_ar: Optional[str] = None


class PortfolioItemUpdate(BaseModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    campaign_type: Optional[str] = None
    business_categories: Optional[list[str]] = None
    platforms: Optional[list[str]] = None
    content_formats: Optional[list[str]] = None
    example_concept: Optional[str] = None
    example_concept_ar: Optional[str] = None
    is_published: Optional[bool] = None


class PortfolioItemRead(BaseModel):
    id: str
    content_creator_id: str
    title: str
    title_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    campaign_type: Optional[str]
    business_categories: list
    platforms: list
    content_formats: list
    example_concept: Optional[str]
    example_concept_ar: Optional[str]
    view_count: int
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Booking Request ────────────────────────────────────────────────────────────

class BookingRequestCreate(BaseModel):
    content_creator_id: str
    portfolio_item_id: Optional[str] = None
    business_description: Optional[str] = None
    business_description_ar: Optional[str] = None
    campaign_goal: Optional[str] = None
    target_audience: Optional[str] = None
    budget_jod: Optional[float] = Field(default=None, ge=0)
    timeline_days: Optional[int] = Field(default=None, ge=1)
    merchant_notes: Optional[str] = None


class BookingRequestUpdate(BaseModel):
    creator_response: Optional[str] = None


class BookingRequestRead(BaseModel):
    id: str
    merchant_id: str
    content_creator_id: str
    portfolio_item_id: Optional[str]
    business_description: Optional[str]
    business_description_ar: Optional[str]
    campaign_goal: Optional[str]
    target_audience: Optional[str]
    budget_jod: Optional[float]
    timeline_days: Optional[int]
    status: BookingRequestStatus
    merchant_notes: Optional[str]
    creator_response: Optional[str]
    created_at: datetime
    # Enriched fields (populated at router layer)
    merchant_business_name: Optional[str] = None
    merchant_business_name_ar: Optional[str] = None
    creator_display_name: Optional[str] = None
    creator_display_name_ar: Optional[str] = None

    model_config = {"from_attributes": True}


# ── CC Engagement ──────────────────────────────────────────────────────────────

class CCEngagementUpdate(BaseModel):
    merchant_feedback: Optional[str] = None


class IdeaSubmit(BaseModel):
    idea_brief: str
    idea_brief_ar: Optional[str] = None


class RatingSubmit(BaseModel):
    creator_rating: float = Field(..., ge=1.0, le=5.0)
    merchant_feedback: Optional[str] = None


class CCEngagementRead(BaseModel):
    id: str
    booking_request_id: str
    merchant_id: str
    content_creator_id: str
    campaign_id: Optional[str]
    status: CCEngagementStatus
    agreed_fee_jod: float
    platform_share_percent: float
    # idea_brief stripped for non-participants at the router layer
    idea_brief: Optional[str] = None
    idea_brief_ar: Optional[str] = None
    merchant_feedback: Optional[str]
    creator_rating: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    # Enriched fields (populated at router layer)
    creator_display_name: Optional[str] = None
    merchant_business_name: Optional[str] = None

    model_config = {"from_attributes": True}
