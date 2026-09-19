from pydantic import BaseModel
from ..models.escrow import EscrowStatus

class EscrowResponse(BaseModel):
    id: int
    campaign_id: int
    gross_amount: float
    vat_amount: float
    platform_fee: float
    net_amount: float
    status: EscrowStatus
    model_config = {"from_attributes": True}

class EscrowTransition(BaseModel):
    target_status: EscrowStatus
    reason: str | None = None
