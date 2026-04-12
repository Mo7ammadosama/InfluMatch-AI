# + backend/schemas/auth.py
# ============================================================

# backend/schemas/auth.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.user import UserRole

class UserCreate(BaseModel):
    email:          EmailStr
    username:       str
    password:       str
    role:           UserRole
    full_name_ar:   Optional[str] = None
    full_name_en:   Optional[str] = None
    phone:          Optional[str] = None

    model_config = {"from_attributes": True}

class UserResponse(BaseModel):
    id:             int
    email:          str
    username:       str
    role:           UserRole
    full_name_ar:   Optional[str]
    full_name_en:   Optional[str]
    is_active:      bool
    is_verified:    bool

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token:   str
    token_type:     str
    role:           str

class TokenData(BaseModel):
    user_id:        Optional[int] = None
    role:           Optional[str] = None
# ============================================================