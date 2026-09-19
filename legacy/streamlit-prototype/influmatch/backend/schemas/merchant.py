from pydantic import BaseModel
from typing import Optional

class MerchantCreate(BaseModel):
    business_name_ar: str
    business_name_en: Optional[str] = None
    business_category: Optional[str] = None
    description_ar: Optional[str] = None
    city: str = "Amman"

class MerchantResponse(BaseModel):
    id: int
    user_id: int
    business_name_ar: str
    business_name_en: Optional[str]
    business_category: Optional[str]
    city: str
    total_spent_jod: float
    loyalty_points: int
    is_verified: bool
    model_config = {"from_attributes": True}
