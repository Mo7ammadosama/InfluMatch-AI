from pydantic import BaseModel, Field
from datetime import datetime


class InfluencerCreate(BaseModel):
    display_name: str = Field(..., min_length=2)
    bio: str | None = None
    bio_ar: str | None = None
    city: str = "Amman"
    social_platforms: dict = Field(default_factory=dict)
    content_categories: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["ar", "en"])
    rate_per_post_jod: float = Field(default=0.0, ge=0)
    rate_per_story_jod: float = Field(default=0.0, ge=0)
    rate_per_reel_jod: float = Field(default=0.0, ge=0)


class InfluencerUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    bio_ar: str | None = None
    city: str | None = None
    social_platforms: dict | None = None
    content_categories: list[str] | None = None
    rate_per_post_jod: float | None = None
    rate_per_story_jod: float | None = None
    rate_per_reel_jod: float | None = None
    is_available: bool | None = None


class InfluencerRead(BaseModel):
    id: str
    user_id: str
    display_name: str
    bio: str | None
    bio_ar: str | None
    city: str
    social_platforms: dict
    total_followers: int
    avg_engagement_rate: float
    content_categories: list
    languages: list
    rate_per_post_jod: float
    rate_per_story_jod: float
    rate_per_reel_jod: float
    total_earned_jod: float
    completed_deals: int
    avg_rating: float
    is_verified: bool
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
