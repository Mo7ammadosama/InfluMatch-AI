from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from loguru import logger
from ...core.database import get_db
from ...core.security import verify_password, create_access_token, get_password_hash
from ...models.user import User, UserRole
from ...models.wallet import LoyaltyWallet
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...schemas.auth import Token, UserCreate, UserResponse
from ..dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserUpdate(BaseModel):
    full_name_ar: Optional[str] = None
    full_name_en: Optional[str] = None
    phone       : Optional[str] = None

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email, username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role, full_name_ar=payload.full_name_ar,
        full_name_en=payload.full_name_en, phone=payload.phone,
    )
    db.add(user)
    await db.flush()
    db.add(LoyaltyWallet(user_id=user.id))

    # Auto-create role-specific profile so the platform works immediately after signup
    if user.role == UserRole.MERCHANT:
        db.add(Merchant(
            user_id          = user.id,
            business_name_ar = payload.full_name_ar or payload.username or "تاجر",
            business_name_en = payload.full_name_en or payload.username,
            city             = "Amman",
        ))
    elif user.role == UserRole.INFLUENCER:
        db.add(Influencer(user_id=user.id, city="Amman"))

    await db.commit()
    await db.refresh(user)
    logger.success(f"[ARIA::AUTH] Registered: {user.email} [{user.role}]")
    return user

@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.success(f"[ARIA::AUTH] Login: {user.email}")
    return Token(access_token=token, role=user.role)

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's name / phone"""
    if data.full_name_ar is not None:
        current_user.full_name_ar = data.full_name_ar
    if data.full_name_en is not None:
        current_user.full_name_en = data.full_name_en
    if data.phone is not None:
        current_user.phone = data.phone
    await db.commit()
    await db.refresh(current_user)
    logger.info(f"[ARIA::AUTH] Profile updated: {current_user.email}")
    return current_user
