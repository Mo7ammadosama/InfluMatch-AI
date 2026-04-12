"""
InfluMatch.jo — Merchants Router
CRUD for Merchant profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantRead, MerchantUpdate
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


@router.post("/profile", response_model=MerchantRead, status_code=201)
async def create_profile(
    payload: MerchantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Merchant profile already exists")

    merchant = Merchant(user_id=current_user.id, **payload.model_dump())
    db.add(merchant)
    await db.flush()
    return merchant


@router.get("/profile", response_model=MerchantRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")
    return merchant


@router.patch("/profile", response_model=MerchantRead)
async def update_profile(
    payload: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant profile not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(merchant, field, value)
    return merchant


@router.get("/", response_model=list[MerchantRead])
async def list_merchants(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Merchant).offset(skip).limit(limit))
    return result.scalars().all()
