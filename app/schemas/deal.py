from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.models.deal import DealStatus


class DealCreate(BaseModel):
    campaign_id: str | None = None
    influencer_id: str
    agreed_amount_jod: float = Field(default=0.0, ge=0.0)
    agreed_rate_jod: float | None = None  # frontend alias
    brief: str | None = None              # frontend alias for notes
    deliverables: list | dict = Field(default_factory=dict)
    deadline: datetime | None = None
    notes: str | None = None

    def model_post_init(self, __context: object) -> None:
        if self.agreed_rate_jod and not self.agreed_amount_jod:
            self.agreed_amount_jod = self.agreed_rate_jod
        if self.brief and not self.notes:
            self.notes = self.brief
        if isinstance(self.deliverables, list):
            self.deliverables = {d: True for d in self.deliverables}


class DealUpdate(BaseModel):
    status: DealStatus | None = None
    content_urls: list[str] | None = None
    merchant_rating: float | None = Field(default=None, ge=1, le=5)
    influencer_rating: float | None = Field(default=None, ge=1, le=5)
    notes: str | None = None


class DealRead(BaseModel):
    id: str
    campaign_id: str | None
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

    @field_validator("deliverables", mode="before")
    @classmethod
    def coerce_deliverables(cls, v):
        if isinstance(v, list):
            return {item: True for item in v}
        return v or {}
