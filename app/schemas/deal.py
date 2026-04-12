from pydantic import BaseModel, Field
from datetime import datetime
from app.models.deal import DealStatus


class DealCreate(BaseModel):
    campaign_id: str
    influencer_id: str
    agreed_amount_jod: float = Field(..., ge=1.0)
    deliverables: dict = Field(default_factory=dict)
    deadline: datetime | None = None
    notes: str | None = None


class DealUpdate(BaseModel):
    status: DealStatus | None = None
    content_urls: list[str] | None = None
    merchant_rating: float | None = Field(default=None, ge=1, le=5)
    influencer_rating: float | None = Field(default=None, ge=1, le=5)
    notes: str | None = None


class DealRead(BaseModel):
    id: str
    campaign_id: str
    influencer_id: str
    agreed_amount_jod: float
    vat_amount_jod: float
    platform_fee_jod: float
    total_amount_jod: float
    deliverables: dict
    deadline: datetime | None
    status: DealStatus
    content_urls: list
    content_verified_by_ai: bool
    merchant_rating: float | None
    influencer_rating: float | None
    escrow_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
