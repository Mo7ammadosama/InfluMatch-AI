"""
WaslAI.jo — Creative Strategists Router
CRUD for Creative Strategist profiles
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.creative_strategist import CreativeStrategist
from app.schemas.creative_strategist import (
    CreativeStrategistCreate,
    CreativeStrategistUpdate,
    CreativeStrategistRead,
)
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


@router.post("/profile", response_model=CreativeStrategistRead, status_code=201)
async def create_profile(
    payload: CreativeStrategistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Creative Strategist profile already exists")

    strategist = CreativeStrategist(user_id=current_user.id, **payload.model_dump())
    db.add(strategist)
    await db.flush()
    return strategist


@router.get("/profile/me", response_model=CreativeStrategistRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=404, detail="Creative Strategist profile not found")
    return strategist


@router.put("/profile/me", response_model=CreativeStrategistRead)
async def update_my_profile(
    payload: CreativeStrategistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CREATIVE_STRATEGIST)),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.user_id == current_user.id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=404, detail="Creative Strategist profile not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(strategist, field, value)
    return strategist


@router.get("/{strategist_id}", response_model=CreativeStrategistRead)
async def get_public_profile(
    strategist_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(CreativeStrategist).where(CreativeStrategist.id == strategist_id))
    strategist = result.scalar_one_or_none()
    if not strategist:
        raise HTTPException(status_code=404, detail="Creative Strategist not found")
    return strategist


@router.get("/", response_model=list[CreativeStrategistRead])
async def list_strategists(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CreativeStrategist)
        .where(CreativeStrategist.is_available == True)  # noqa: E712
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
