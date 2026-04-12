from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: UserRole
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    is_active: bool
    is_verified: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
