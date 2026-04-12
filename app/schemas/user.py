from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    full_name_ar: str | None = None
    role: UserRole
    phone: str | None = None


class UserRead(BaseModel):
    id: str
    email: str
    full_name: str
    full_name_ar: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
