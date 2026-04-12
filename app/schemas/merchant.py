from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


class MerchantCreate(BaseModel):
    business_name: str = Field(..., min_length=2)
    business_name_ar: str | None = None
    business_category: str
    description: str | None = None
    description_ar: str | None = None
    commercial_registration: str | None = None
    tax_number: str | None = None
    city: str = "Amman"
    website: str | None = None


class MerchantUpdate(BaseModel):
    business_name: str | None = None
    business_name_ar: str | None = None
    business_category: str | None = None
    description: str | None = None
    description_ar: str | None = None
    city: str | None = None
    website: str | None = None


class MerchantRead(BaseModel):
    id: str
    user_id: str
    business_name: str
    business_name_ar: str | None
    business_category: str
    description: str | None
    city: str
    website: str | None
    total_spent_jod: float
    active_campaigns: int
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
