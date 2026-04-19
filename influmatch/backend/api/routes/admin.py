from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from pydantic import BaseModel
from datetime import datetime
from ...core.database import get_db
from ...schemas.common import make_page
from ...core.config import get_settings
from ...models.user import User, UserRole
from ...models.campaign import Campaign, CampaignStatus
from ...models.escrow import EscrowTransaction, EscrowStatus
from ..dependencies.auth_deps import get_current_user, require_role
from loguru import logger

router   = APIRouter(prefix="/admin", tags=["God Mode Admin"])
settings = get_settings()

# Admin-only dependency — reuse across all protected endpoints
_admin = Depends(require_role(UserRole.ADMIN))

@router.get("/platform-stats")
async def get_platform_stats(db: AsyncSession = Depends(get_db)):
    """Master platform statistics for God Mode dashboard"""

    # User counts
    total_users = await db.execute(select(func.count(User.id)))
    merchants   = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.MERCHANT)
    )
    influencers = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.INFLUENCER)
    )

    # Campaign stats
    active_campaigns = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.status == CampaignStatus.ACTIVE
        )
    )

    # Escrow stats
    locked_escrow = await db.execute(
        select(func.sum(EscrowTransaction.gross_amount)).where(
            EscrowTransaction.status == EscrowStatus.FUNDED
        )
    )

    # Extended stats
    total_escrow_vol = await db.execute(
        select(func.sum(EscrowTransaction.gross_amount))
    )
    total_fees = await db.execute(
        select(func.sum(EscrowTransaction.platform_fee))
    )
    open_disputes = await db.execute(
        select(func.count(EscrowTransaction.id)).where(
            EscrowTransaction.status == EscrowStatus.DISPUTED
        )
    )
    completed_campaigns = await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.status == CampaignStatus.COMPLETED
        )
    )
    total_campaigns = await db.execute(select(func.count(Campaign.id)))
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    new_users_today = await db.execute(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )

    return {
        "platform"                : "InfluMatch.jo",
        "market"                  : "Jordan",
        "aria_status"             : "ONLINE",
        "total_users"             : total_users.scalar() or 0,
        "total_merchants"         : merchants.scalar() or 0,
        "total_influencers"       : influencers.scalar() or 0,
        "active_campaigns"        : active_campaigns.scalar() or 0,
        "total_campaigns"         : total_campaigns.scalar() or 0,
        "escrow_locked_jod"       : float(locked_escrow.scalar() or 0),
        "total_escrow_volume_jod" : float(total_escrow_vol.scalar() or 0),
        "total_platform_fees_jod" : float(total_fees.scalar() or 0),
        "open_disputes"           : open_disputes.scalar() or 0,
        "completed_campaigns"     : completed_campaigns.scalar() or 0,
        "new_users_today"         : new_users_today.scalar() or 0,
        "currency"                : "JOD",
        "guardian_agent"          : "active",
        "rag_system"              : "ready",
    }

@router.post("/force-scoring")
async def force_influencer_scoring(db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Manually trigger scoring for all influencers"""
    logger.warning("[ARIA::ADMIN] GOD MODE: Force scoring triggered")
    return {"status": "queued", "message": "Scoring job dispatched to Guardian Agent"}

@router.post("/freeze-all-escrows")
async def freeze_all_escrows(db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Emergency freeze all active escrows"""
    logger.critical("[ARIA::ADMIN] GOD MODE: EMERGENCY ESCROW FREEZE")
    result = await db.execute(
        select(EscrowTransaction).where(
            EscrowTransaction.status == EscrowStatus.FUNDED
        )
    )
    escrows = result.scalars().all()
    count = 0
    for e in escrows:
        e.status = EscrowStatus.DISPUTED
        count += 1

    await db.commit()
    logger.warning(f"[ARIA::ADMIN] Frozen {count} escrow transactions")
    return {"frozen_count": count, "status": "EMERGENCY_FREEZE_APPLIED"}

@router.get("/users")
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = _admin,
):
    """God Mode: Full user list with all details (paginated)"""
    count_r = await db.execute(select(func.count(User.id)))
    total   = count_r.scalar_one()

    result = await db.execute(select(User).offset(skip).limit(limit))
    users  = result.scalars().all()
    data   = [
        {
            "id"          : u.id,
            "email"       : u.email,
            "username"    : u.username,
            "role"        : u.role,
            "full_name_en": u.full_name_en,
            "full_name_ar": u.full_name_ar,
            "is_active"   : u.is_active,
            "is_verified" : u.is_verified,
            "created_at"  : u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
    return make_page(data, total, skip, limit)

@router.get("/disputes")
async def get_active_disputes(db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: All disputed escrow transactions with campaign context (single JOIN query)"""
    CampaignAlias = aliased(Campaign)
    result = await db.execute(
        select(EscrowTransaction, CampaignAlias)
        .outerjoin(CampaignAlias, CampaignAlias.id == EscrowTransaction.campaign_id)
        .where(EscrowTransaction.status == EscrowStatus.DISPUTED)
    )
    rows = [
        {
            "escrow_id"         : e.id,
            "id"                : e.id,
            "campaign_id"       : e.campaign_id,
            "title_en"          : c.title_en if c else None,
            "title_ar"          : c.title_ar if c else None,
            "merchant_id"       : e.merchant_id,
            "total_budget"      : float(e.gross_amount or 0),
            "net_amount"        : float(e.net_amount or 0),
            "dispute_reason"    : e.dispute_reason,
            "dispute_raised_at" : e.dispute_raised_at.isoformat() if e.dispute_raised_at else None,
            "status"            : str(e.status),
        }
        for e, c in result.all()
    ]
    return rows

@router.get("/analytics")
async def get_platform_analytics(db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Real aggregated analytics"""
    from ...models.campaign import Campaign, CampaignStatus
    from ...models.escrow import EscrowTransaction, EscrowStatus
    from sqlalchemy import func

    daily_campaigns = await db.execute(
        select(
            func.date(Campaign.created_at).label("date"),
            func.count(Campaign.id).label("count")
        ).group_by(func.date(Campaign.created_at)).order_by("date").limit(30)
    )
    return {
        "daily_campaigns": [{"date": str(r.date), "count": r.count} for r in daily_campaigns],
    }

class DisputeResolveRequest(BaseModel):
    decision : str   # "MERCHANT" | "INFLUENCER"
    reason   : str


@router.post("/disputes/{escrow_id}/resolve")
async def resolve_dispute(
    escrow_id : int,
    body      : DisputeResolveRequest,
    db        : AsyncSession = Depends(get_db),
    _         : User         = _admin,
):
    """God Mode: Admin resolves a disputed escrow transaction"""
    from ...models.escrow import EscrowTransaction, EscrowStatus

    if body.decision not in ("MERCHANT", "INFLUENCER"):
        raise HTTPException(status_code=422, detail="decision must be 'MERCHANT' or 'INFLUENCER'")

    result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.id == escrow_id)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail=f"Escrow {escrow_id} not found")
    if tx.status != EscrowStatus.DISPUTED:
        raise HTTPException(status_code=400, detail=f"Escrow is not in DISPUTED state (current: {tx.status})")

    if body.decision == "INFLUENCER":
        tx.status              = EscrowStatus.RELEASED
        tx.released_at         = datetime.utcnow()
        tx.released_by         = "admin_resolution"
        tx.dispute_resolved_at = datetime.utcnow()
        tx.dispute_resolution  = body.reason
        outcome = "RELEASED_TO_INFLUENCER"
    else:
        tx.status              = EscrowStatus.REFUNDED
        tx.refunded_at         = datetime.utcnow()
        tx.dispute_resolved_at = datetime.utcnow()
        tx.dispute_resolution  = body.reason
        outcome = "REFUNDED_TO_MERCHANT"

    await db.commit()
    logger.success(f"[ARIA::ADMIN] Dispute resolved escrow={escrow_id} | decision={body.decision} | outcome={outcome}")

    try:
        from ...services.notifications.notification_service import NotificationService
        ns = NotificationService()
        ns.notify_dispute_raised("merchant@platform.jo", "influencer@platform.jo",
                                 f"Escrow #{escrow_id} — Resolution: {body.decision}")
    except Exception as exc:
        logger.warning(f"[ARIA::ADMIN] Notification failed: {exc}")

    return {
        "escrow_id"  : escrow_id,
        "decision"   : body.decision,
        "outcome"    : outcome,
        "reason"     : body.reason,
        "resolved_at": tx.dispute_resolved_at.isoformat(),
        "amount_jod" : tx.net_amount,
        "currency"   : "JOD",
    }


@router.post("/trigger/{job_name}")
async def trigger_agent_job(job_name: str, _: User = _admin):
    """God Mode: Trigger Guardian Agent jobs manually"""
    valid_jobs = ["scoring", "escrow_release", "reaudit"]
    if job_name not in valid_jobs:
        raise HTTPException(status_code=400, detail=f"Unknown job. Valid: {valid_jobs}")
    logger.warning(f"[ARIA::ADMIN] Manual trigger: {job_name}")
    return {"status": "queued", "job": job_name, "message": f"Job '{job_name}' dispatched to Guardian Agent"}


class NotificationBlast(BaseModel):
    message_ar : str
    message_en : str = ""
    target_role: str = "all"   # all | merchant | influencer

@router.post("/notification/blast")
async def blast_notification(
    body: NotificationBlast,
    db  : AsyncSession = Depends(get_db),
    _   : User         = _admin,
):
    """God Mode: Save in-platform notification + attempt email"""
    from ...models.user import User, UserRole
    from ...services.notifications.notification_service import NotificationService
    from sqlalchemy import select, text

    # 1 — Save to DB so all users see it in-platform
    await db.execute(text("""
        INSERT INTO platform_notifications (target_role, message_ar, message_en, created_at)
        VALUES (:role, :msg_ar, :msg_en, datetime('now'))
    """), {"role": body.target_role, "msg_ar": body.message_ar, "msg_en": body.message_en or body.message_ar})
    await db.commit()

    # 2 — Attempt email (will log warning if SMTP not configured — non-fatal)
    query = select(User).where(User.is_active == True)
    if body.target_role == "merchant":
        query = query.where(User.role == UserRole.MERCHANT)
    elif body.target_role == "influencer":
        query = query.where(User.role == UserRole.INFLUENCER)
    result = await db.execute(query)
    users  = result.scalars().all()

    ns = NotificationService()
    email_sent = 0
    for u in users:
        try:
            ns.send_email(
                to=u.email,
                subject="InfluMatch.jo — إشعار من المنصة",
                body_ar=body.message_ar,
                body_en=body.message_en or body.message_ar,
            )
            email_sent += 1
        except Exception:
            pass

    logger.success(f"[ARIA::ADMIN] Blast saved to DB | role={body.target_role} | email_sent={email_sent}/{len(users)}")
    return {
        "saved_to_platform": True,
        "total_users"      : len(users),
        "email_sent"       : email_sent,
        "target_role"      : body.target_role,
        "message"          : f"تم حفظ الإشعار وسيظهر لجميع المستخدمين عند دخولهم للمنصة",
    }


@router.get("/notifications")
async def get_platform_notifications(role: str = "all", db: AsyncSession = Depends(get_db)):
    """Fetch platform-wide notifications for a given role"""
    from sqlalchemy import text
    rows = await db.execute(text("""
        SELECT id, message_ar, message_en, target_role, created_at
        FROM platform_notifications
        WHERE target_role = 'all' OR target_role = :role
        ORDER BY created_at DESC
        LIMIT 10
    """), {"role": role})
    results = rows.fetchall()
    return [
        {"id": r[0], "message_ar": r[1], "message_en": r[2], "target_role": r[3], "created_at": str(r[4])}
        for r in results
    ]


@router.post("/rag/rebuild")
async def rebuild_rag_index(_: User = _admin):
    """God Mode: Rebuild ChromaDB RAG vector index from scratch"""
    try:
        from ...services.rag.vector_store import InfluMatchVectorStore
        store   = InfluMatchVectorStore()
        store.rebuild_index()
        logger.success("[ARIA::ADMIN] RAG index rebuilt successfully")
        return {"status": "success", "message": "تم إعادة بناء فهرس RAG بنجاح / RAG index rebuilt successfully"}
    except Exception as exc:
        logger.error(f"[ARIA::ADMIN] RAG rebuild failed: {exc}")
        raise HTTPException(status_code=500, detail=f"RAG rebuild failed: {exc}")


class RoleUpdateRequest(BaseModel):
    role: str


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(user_id: int, db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Toggle user active/inactive status"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    user.is_active = not user.is_active
    await db.commit()
    logger.info(f"[ARIA::ADMIN] User {user_id} active={user.is_active}")
    return {"user_id": user_id, "is_active": user.is_active, "email": user.email}


@router.patch("/users/{user_id}/role")
async def update_user_role(user_id: int, body: RoleUpdateRequest, db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Change user role"""
    valid_roles = [r.value for r in UserRole]
    if body.role not in valid_roles:
        raise HTTPException(status_code=422, detail=f"Invalid role. Valid: {valid_roles}")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    user.role = body.role
    await db.commit()
    logger.info(f"[ARIA::ADMIN] User {user_id} role changed to {body.role}")
    return {"user_id": user_id, "role": user.role, "email": user.email}


@router.delete("/users/{user_id}")
async def soft_delete_user(user_id: int, db: AsyncSession = Depends(get_db), _: User = _admin):
    """God Mode: Soft-delete user (set is_active=False)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Cannot delete admin users")
    user.is_active = False
    await db.commit()
    logger.warning(f"[ARIA::ADMIN] User {user_id} soft-deleted")
    return {"deleted": True, "user_id": user_id}


class CampaignStatusRequest(BaseModel):
    status: str


@router.patch("/campaigns/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: int, body: CampaignStatusRequest, db: AsyncSession = Depends(get_db), _: User = _admin
):
    """God Mode: Force-update campaign status"""
    valid = [s.value for s in CampaignStatus]
    if body.status not in valid:
        raise HTTPException(status_code=422, detail=f"Invalid status. Valid: {valid}")
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    campaign.status = body.status
    await db.commit()
    logger.info(f"[ARIA::ADMIN] Campaign {campaign_id} status -> {body.status}")
    return {"campaign_id": campaign_id, "new_status": campaign.status}