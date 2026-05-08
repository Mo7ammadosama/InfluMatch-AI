"""
WaslAI.jo — Content Creators Router
Profile, booking requests, and creative engagements for Content Creator role.
idea_brief is NEVER returned to non-participants.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.content_creator import ContentCreator
from app.models.booking_request import BookingRequest, BookingRequestStatus
from app.models.cc_engagement import CCEngagement, CCEngagementStatus
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.schemas.content_creator import (
    ContentCreatorCreate,
    ContentCreatorUpdate,
    ContentCreatorRead,
    ContentCreatorSummary,
    BookingRequestCreate,
    BookingRequestRead,
    CCEngagementRead,
    IdeaSubmit,
    RatingSubmit,
)
from app.middleware.auth_middleware import get_current_user, require_role

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_idea_brief(eng: CCEngagement, viewer_merchant_id: str | None, viewer_creator_id: str | None) -> CCEngagementRead:
    """Return engagement read model, zeroing idea_brief for non-participants."""
    is_participant = (
        (viewer_merchant_id and eng.merchant_id == viewer_merchant_id)
        or (viewer_creator_id and eng.content_creator_id == viewer_creator_id)
    )
    data = CCEngagementRead.model_validate(eng)
    if not is_participant:
        data.idea_brief = None
        data.idea_brief_ar = None
    return data


async def _get_merchant(user: User, db: AsyncSession) -> Merchant:
    r = await db.execute(select(Merchant).where(Merchant.user_id == user.id))
    m = r.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=400, detail="Merchant profile not found")
    return m


async def _get_creator_profile(user: User, db: AsyncSession) -> ContentCreator:
    r = await db.execute(select(ContentCreator).where(ContentCreator.user_id == user.id))
    c = r.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Content Creator profile not found")
    return c


async def process_creator_payout(engagement: CCEngagement, db: AsyncSession) -> None:
    """Credit the creator's wallet with their share of the agreed fee."""
    earned = float(engagement.agreed_fee_jod) * float(engagement.platform_share_percent) / 100

    # Always do explicit async query — never access lazy relationship in async context
    r = await db.execute(select(ContentCreator).where(ContentCreator.id == engagement.content_creator_id))
    creator = r.scalar_one_or_none()
    if not creator:
        return

    creator.total_earned_jod += earned
    creator.completed_engagements += 1

    r = await db.execute(select(Wallet).where(Wallet.user_id == creator.user_id))
    wallet = r.scalar_one_or_none()
    if wallet:
        wallet.available_balance_jod += earned
        tx = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=TransactionType.CREDIT,
            amount_jod=earned,
            balance_after_jod=wallet.available_balance_jod,
            reference_id=engagement.id,
            description=f"You earned {earned:.2f} JOD from engagement {engagement.id[:8]}",
        )
        db.add(tx)


# ── Profile endpoints ──────────────────────────────────────────────────────────

@router.post("/profile", response_model=ContentCreatorRead, status_code=201)
async def create_profile(
    payload: ContentCreatorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    r = await db.execute(select(ContentCreator).where(ContentCreator.user_id == current_user.id))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Content Creator profile already exists")

    creator = ContentCreator(user_id=current_user.id, **payload.model_dump())
    db.add(creator)
    await db.flush()
    return creator


@router.get("/profile/me", response_model=ContentCreatorRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    return await _get_creator_profile(current_user, db)


@router.put("/profile/me", response_model=ContentCreatorRead)
async def update_my_profile(
    payload: ContentCreatorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator_profile(current_user, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(creator, field, value)
    await db.flush()
    await db.refresh(creator)
    return creator


# ── Booking Request endpoints ──────────────────────────────────────────────────

@router.post("/booking-requests", response_model=BookingRequestRead, status_code=201)
async def create_booking_request(
    payload: BookingRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    merchant = await _get_merchant(current_user, db)

    r = await db.execute(select(ContentCreator).where(ContentCreator.id == payload.content_creator_id))
    creator = r.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Content Creator not found")
    if not creator.is_available:
        raise HTTPException(status_code=400, detail="Content Creator is not currently available")

    req = BookingRequest(
        merchant_id=merchant.id,
        **payload.model_dump(),
    )
    db.add(req)
    await db.flush()
    return req


@router.get("/booking-requests/received", response_model=list[BookingRequestRead])
async def get_received_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    result = await db.execute(select(ContentCreator).where(ContentCreator.user_id == current_user.id))
    creator = result.scalar_one_or_none()
    if not creator:
        return []
    r = await db.execute(
        select(BookingRequest)
        .where(BookingRequest.content_creator_id == creator.id)
        .order_by(BookingRequest.created_at.desc())
    )
    reqs = r.scalars().all()
    merchant_ids = {req.merchant_id for req in reqs}
    merchants_by_id: dict = {}
    if merchant_ids:
        mr = await db.execute(select(Merchant).where(Merchant.id.in_(merchant_ids)))
        merchants_by_id = {m.id: m for m in mr.scalars().all()}
    enriched = []
    for req in reqs:
        data = BookingRequestRead.model_validate(req)
        m = merchants_by_id.get(req.merchant_id)
        if m:
            data.merchant_business_name = m.business_name
            data.merchant_business_name_ar = m.business_name_ar
        enriched.append(data)
    return enriched


@router.get("/booking-requests/sent", response_model=list[BookingRequestRead])
async def get_sent_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    merchant = await _get_merchant(current_user, db)
    r = await db.execute(
        select(BookingRequest)
        .where(BookingRequest.merchant_id == merchant.id)
        .order_by(BookingRequest.created_at.desc())
    )
    reqs = r.scalars().all()

    creator_ids = {req.content_creator_id for req in reqs}
    creators_by_id: dict = {}
    if creator_ids:
        cr = await db.execute(select(ContentCreator).where(ContentCreator.id.in_(creator_ids)))
        creators_by_id = {c.id: c for c in cr.scalars().all()}

    enriched = []
    for req in reqs:
        data = BookingRequestRead.model_validate(req)
        c = creators_by_id.get(req.content_creator_id)
        if c:
            data.creator_display_name = c.display_name
            data.creator_display_name_ar = c.display_name_ar
        enriched.append(data)
    return enriched


@router.put("/booking-requests/{request_id}/accept", response_model=BookingRequestRead)
async def accept_booking_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator_profile(current_user, db)

    r = await db.execute(select(BookingRequest).where(BookingRequest.id == request_id))
    req = r.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Booking request not found")
    if req.content_creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not your booking request")
    if req.status != BookingRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot accept request in status: {req.status}")

    req.status = BookingRequestStatus.ACCEPTED

    # Auto-create CCEngagement
    engagement = CCEngagement(
        booking_request_id=req.id,
        merchant_id=req.merchant_id,
        content_creator_id=creator.id,
        agreed_fee_jod=req.budget_jod or 0.0,
        started_at=datetime.now(timezone.utc),
        status=CCEngagementStatus.ACTIVE,
    )
    db.add(engagement)
    await db.flush()
    return req


@router.put("/booking-requests/{request_id}/decline", response_model=BookingRequestRead)
async def decline_booking_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator_profile(current_user, db)

    r = await db.execute(select(BookingRequest).where(BookingRequest.id == request_id))
    req = r.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Booking request not found")
    if req.content_creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not your booking request")
    if req.status != BookingRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot decline request in status: {req.status}")

    req.status = BookingRequestStatus.DECLINED
    return req


# ── Engagement endpoints ───────────────────────────────────────────────────────

@router.get("/engagements", response_model=list[CCEngagementRead])
@router.get("/engagements/", response_model=list[CCEngagementRead])
async def list_my_engagements(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.CONTENT_CREATOR:
        result = await db.execute(select(ContentCreator).where(ContentCreator.user_id == current_user.id))
        creator = result.scalar_one_or_none()
        if not creator:
            return []
        r = await db.execute(
            select(CCEngagement)
            .where(CCEngagement.content_creator_id == creator.id)
            .order_by(CCEngagement.created_at.desc())
        )
        engagements = r.scalars().all()
        # Enrich with merchant business names
        merchant_ids = {e.merchant_id for e in engagements}
        merchants_by_id: dict = {}
        if merchant_ids:
            mr = await db.execute(select(Merchant).where(Merchant.id.in_(merchant_ids)))
            merchants_by_id = {m.id: m for m in mr.scalars().all()}
        result_list = []
        for e in engagements:
            data = _strip_idea_brief(e, None, creator.id)
            m = merchants_by_id.get(e.merchant_id)
            if m:
                data.merchant_business_name = m.business_name
            result_list.append(data)
        return result_list

    if current_user.role == UserRole.MERCHANT:
        result = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merchant = result.scalar_one_or_none()
        if not merchant:
            return []
        r = await db.execute(
            select(CCEngagement)
            .where(CCEngagement.merchant_id == merchant.id)
            .order_by(CCEngagement.created_at.desc())
        )
        engagements = r.scalars().all()
        # Enrich with creator display names
        creator_ids = {e.content_creator_id for e in engagements}
        creators_by_id: dict = {}
        if creator_ids:
            cr = await db.execute(select(ContentCreator).where(ContentCreator.id.in_(creator_ids)))
            creators_by_id = {c.id: c for c in cr.scalars().all()}
        result_list = []
        for e in engagements:
            data = _strip_idea_brief(e, merchant.id, None)
            c = creators_by_id.get(e.content_creator_id)
            if c:
                data.creator_display_name = c.display_name
            result_list.append(data)
        return result_list

    raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/engagements/{engagement_id}", response_model=CCEngagementRead)
async def get_engagement(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = await db.execute(select(CCEngagement).where(CCEngagement.id == engagement_id))
    eng = r.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")

    viewer_merchant_id = None
    viewer_creator_id = None

    if current_user.role == UserRole.MERCHANT:
        merchant = await _get_merchant(current_user, db)
        if eng.merchant_id != merchant.id:
            raise HTTPException(status_code=403, detail="Not your engagement")
        viewer_merchant_id = merchant.id
    elif current_user.role == UserRole.CONTENT_CREATOR:
        creator = await _get_creator_profile(current_user, db)
        if eng.content_creator_id != creator.id:
            raise HTTPException(status_code=403, detail="Not your engagement")
        viewer_creator_id = creator.id
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    return _strip_idea_brief(eng, viewer_merchant_id, viewer_creator_id)


@router.put("/engagements/{engagement_id}/submit-idea", response_model=CCEngagementRead)
async def submit_idea(
    engagement_id: str,
    payload: IdeaSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CONTENT_CREATOR)),
):
    creator = await _get_creator_profile(current_user, db)

    r = await db.execute(select(CCEngagement).where(CCEngagement.id == engagement_id))
    eng = r.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if eng.content_creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not your engagement")
    if eng.status != CCEngagementStatus.ACTIVE:
        raise HTTPException(status_code=400, detail=f"Cannot submit idea in status: {eng.status}")

    eng.idea_brief = payload.idea_brief
    eng.idea_brief_ar = payload.idea_brief_ar
    eng.status = CCEngagementStatus.IDEA_SUBMITTED
    return _strip_idea_brief(eng, None, creator.id)


@router.put("/engagements/{engagement_id}/approve-idea", response_model=CCEngagementRead)
async def approve_idea(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    merchant = await _get_merchant(current_user, db)

    r = await db.execute(select(CCEngagement).where(CCEngagement.id == engagement_id))
    eng = r.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if eng.merchant_id != merchant.id:
        raise HTTPException(status_code=403, detail="Not your engagement")
    if eng.status != CCEngagementStatus.IDEA_SUBMITTED:
        raise HTTPException(status_code=400, detail=f"Cannot approve idea in status: {eng.status}")

    eng.status = CCEngagementStatus.IDEA_APPROVED
    return _strip_idea_brief(eng, merchant.id, None)


@router.put("/engagements/{engagement_id}/complete", response_model=CCEngagementRead)
async def complete_engagement(
    engagement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    merchant = await _get_merchant(current_user, db)

    r = await db.execute(select(CCEngagement).where(CCEngagement.id == engagement_id))
    eng = r.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if eng.merchant_id != merchant.id:
        raise HTTPException(status_code=403, detail="Not your engagement")
    if eng.status == CCEngagementStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Engagement already completed")

    eng.status = CCEngagementStatus.COMPLETED
    eng.completed_at = datetime.now(timezone.utc)
    await process_creator_payout(eng, db)
    return _strip_idea_brief(eng, merchant.id, None)


@router.put("/engagements/{engagement_id}/rate", response_model=CCEngagementRead)
async def rate_creator(
    engagement_id: str,
    payload: RatingSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MERCHANT)),
):
    merchant = await _get_merchant(current_user, db)

    r = await db.execute(select(CCEngagement).where(CCEngagement.id == engagement_id))
    eng = r.scalar_one_or_none()
    if not eng:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if eng.merchant_id != merchant.id:
        raise HTTPException(status_code=403, detail="Not your engagement")
    if eng.status != CCEngagementStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only rate completed engagements")

    eng.creator_rating = payload.creator_rating
    if payload.merchant_feedback:
        eng.merchant_feedback = payload.merchant_feedback

    # Recalculate avg_rating across all completed engagements for this creator
    r2 = await db.execute(
        select(CCEngagement).where(
            CCEngagement.content_creator_id == eng.content_creator_id,
            CCEngagement.creator_rating.is_not(None),
        )
    )
    rated = r2.scalars().all()
    if rated:
        avg = sum(e.creator_rating for e in rated) / len(rated)
        r3 = await db.execute(select(ContentCreator).where(ContentCreator.id == eng.content_creator_id))
        creator = r3.scalar_one_or_none()
        if creator:
            creator.avg_rating = round(avg, 2)

    return _strip_idea_brief(eng, merchant.id, None)


# ── Discovery endpoints (must be AFTER all specific sub-paths) ─────────────────

@router.get("", response_model=list[ContentCreatorSummary])
@router.get("/", response_model=list[ContentCreatorSummary])
async def list_creators(
    city: str | None = Query(default=None),
    specialization: str | None = Query(default=None),
    category: str | None = Query(default=None),
    is_available: bool | None = Query(default=None),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(ContentCreator)
    if city:
        q = q.where(ContentCreator.city == city)
    if is_available is not None:
        q = q.where(ContentCreator.is_available == is_available)  # noqa: E712
    q = q.offset(skip).limit(limit)

    result = await db.execute(q)
    creators = result.scalars().all()

    if specialization:
        creators = [c for c in creators if specialization in (c.specializations or [])]
    if category:
        creators = [c for c in creators if category in (c.content_categories or [])]

    return creators


@router.get("/{creator_id}", response_model=ContentCreatorRead)
async def get_public_profile(
    creator_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    r = await db.execute(select(ContentCreator).where(ContentCreator.id == creator_id))
    creator = r.scalar_one_or_none()
    if not creator:
        raise HTTPException(status_code=404, detail="Content Creator not found")
    return creator
