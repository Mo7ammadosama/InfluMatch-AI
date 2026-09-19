from pydantic import BaseModel
from typing import Optional

class InfluencerCreate(BaseModel):
    bio_ar: Optional[str] = None
    bio_en: Optional[str] = None
    niche: Optional[str] = None
    city: str = "Amman"
    instagram_handle: Optional[str] = None
    instagram_followers: int = 0
    tiktok_handle: Optional[str] = None
    tiktok_followers: int = 0
    youtube_handle: Optional[str] = None
    youtube_subscribers: int = 0
    rate_per_post: float = 0.0
    rate_per_story: float = 0.0
    rate_per_reel: float = 0.0

class InfluencerResponse(BaseModel):
    id: int
    user_id: int
    niche: Optional[str]
    city: str
    instagram_followers: int
    tiktok_followers: int
    youtube_subscribers: int
    aria_score: float
    aria_tier: str
    rate_per_post: float
    is_available: bool
    model_config = {"from_attributes": True}
