"""
WaslAI.jo — Influencers Router
CRUD + availability + search
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


@router.post("/profile", response_model=InfluencerRead, status_code=201)
async def create_profile(
    payload: InfluencerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Influencer profile already exists")

    data = payload.model_dump()
    total_followers = sum(
        p.get("followers", 0) for p in data.get("social_platforms", {}).values()
        if isinstance(p, dict)
    )
    influencer = Influencer(user_id=current_user.id, total_followers=total_followers, **data)
    db.add(influencer)
    await db.flush()
    return influencer


@router.get("/profile", response_model=InfluencerRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.INFLUENCER)),
):
    result = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer profile not found")
    return influencer


@router.patch("/profile", response_model=InfluencerRead)
async def update_profile(
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
    return influencer


@router.get("/", response_model=list[InfluencerRead])
async def list_influencers(
    skip: int = 0,
    limit: int = 20,
    city: str | None = Query(None),
    category: str | None = Query(None),
    available_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Influencer)
    if available_only:
        query = query.where(Influencer.is_available == True)
    if city:
        query = query.where(Influencer.city == city)
    result = await db.execute(query.offset(skip).limit(limit))
    influencers = result.scalars().all()
    if category:
        influencers = [i for i in influencers if category in (i.content_categories or [])]
    return influencers


@router.get("/{influencer_id}", response_model=InfluencerRead)
async def get_influencer(
    influencer_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Influencer).where(Influencer.id == influencer_id))
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return influencer
