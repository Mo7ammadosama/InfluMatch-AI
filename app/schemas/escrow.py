from pydantic import BaseModel
from datetime import datetime
from app.models.escrow import EscrowState


class EscrowRead(BaseModel):
    id: str
    merchant_id: str
    influencer_id: str
    gross_amount_jod: float
    platform_fee_jod: float
    vat_on_fee_jod: float
    net_to_influencer_jod: float
    state: EscrowState
    stripe_payment_intent_id: str | None
    created_at: datetime
    funded_at: datetime | None
    released_at: datetime | None

    model_config = {"from_attributes": True}


class EscrowStateTransition(BaseModel):
    target_state: EscrowState
    reason: str | None = None
