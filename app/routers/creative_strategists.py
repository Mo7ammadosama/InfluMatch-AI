"""
WaslAI.jo — Creative Strategists Router
Creative Strategists are Influencer-role users who publish campaign ideas
rather than taking brand deals. This router aliases into the Influencer model.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.influencer import Influencer
from app.schemas.influencer import InfluencerCreate, InfluencerRead, InfluencerUpdate
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


@router.get("/profile/me", response_model=InfluencerRead)
async def get_my_strategist_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=404, detail="Strategist profile not found")
    return influencer


@router.post("/profile", response_model=InfluencerRead, status_code=201)
async def create_strategist_profile(
    payload: InfluencerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Profile already exists")
    data = payload.model_dump()
    total_followers = sum(
        p.get("followers", 0) for p in data.get("social_platforms", {}).values()
        if isinstance(p, dict)
    )
    influencer = Influencer(user_id=current_user.id, total_followers=total_followers, **data)
    db.add(influencer)
    await db.flush()
    return influencer


@router.put("/profile/me", response_model=InfluencerRead)
async def update_strategist_profile(
    payload: InfluencerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(influencer, field, value)
    await db.flush()
    await db.refresh(influencer)
    return influencer


@router.get("", response_model=list[InfluencerRead])
@router.get("/", response_model=list[InfluencerRead])
async def list_strategists(
    skip: int = 0,
    limit: int = 20,
    city: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Influencer)
    if city:
        query = query.where(Influencer.city == city)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()
