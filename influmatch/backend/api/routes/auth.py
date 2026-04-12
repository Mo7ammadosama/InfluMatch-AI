from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from ...core.database import get_db
from ...core.security import verify_password, create_access_token, get_password_hash
from ...models.user import User
from ...models.wallet import LoyaltyWallet
from ...schemas.auth import Token, UserCreate, UserResponse
from ..dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

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
