"""
WaslAI.jo — Portfolio Items Router
Content Creator portfolio management and public discovery
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.content_creator import ContentCreator
from app.models.portfolio_item import PortfolioItem
from app.schemas.content_creator import PortfolioItemCreate, PortfolioItemUpdate, PortfolioItemRead
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


async def _get_creator(user: User, db: AsyncSession) -> ContentCreator:
    r = await db.execute(select(ContentCreator).where(ContentCreator.user_id == user.id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=400, detail="Complete your Content Creator profile first")
    return c


@router.post("/", response_model=PortfolioItemRead, status_code=201)
async def create_portfolio_item(
    payload: PortfolioItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator(current_user, db)
    item = PortfolioItem(content_creator_id=creator.id, **payload.model_dump())
    db.add(item)
    await db.flush()
    return item


@router.get("/", response_model=list[PortfolioItemRead])
async def list_portfolio_items(
    category: str | None = Query(default=None),
    platform: str | None = Query(default=None),
    campaign_type: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(PortfolioItem).where(PortfolioItem.is_published == True)  # noqa: E712
    if campaign_type:
        q = q.where(PortfolioItem.campaign_type == campaign_type)
    q = q.order_by(PortfolioItem.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(q)
    items = result.scalars().all()

    if category:
        items = [i for i in items if category in (i.business_categories or [])]
    if platform:
        items = [i for i in items if platform in (i.platforms or [])]

    # Increment view_count for each returned item
    for item in items:
        item.view_count += 1

    return items


@router.get("/mine", response_model=list[PortfolioItemRead])
async def get_my_portfolio(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    result = await db.execute(select(ContentCreator).where(ContentCreator.user_id == current_user.id))
    creator = result.scalar_one_or_none()
    if not creator:
        return []
    r = await db.execute(
        select(PortfolioItem)
        .where(PortfolioItem.content_creator_id == creator.id)
        .order_by(PortfolioItem.created_at.desc())
    )
    return r.scalars().all()


@router.get("/{item_id}", response_model=PortfolioItemRead)
async def get_portfolio_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    r = await db.execute(select(PortfolioItem).where(PortfolioItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    item.view_count += 1
    return item


@router.put("/{item_id}", response_model=PortfolioItemRead)
async def update_portfolio_item(
    item_id: str,
    payload: PortfolioItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator(current_user, db)

    r = await db.execute(select(PortfolioItem).where(PortfolioItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    if item.content_creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not your portfolio item")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_portfolio_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator(current_user, db)

    r = await db.execute(select(PortfolioItem).where(PortfolioItem.id == item_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")
    if item.content_creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not your portfolio item")

    await db.delete(item)
