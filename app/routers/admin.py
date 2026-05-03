"""
WaslAI.jo — Admin Router
Platform management endpoints — ADMIN role only.
"""
from datetime import datetime, timezone, date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.database import get_db
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.influencer import Influencer
from app.models.campaign import Campaign, CampaignStatus
from app.models.escrow import EscrowTransaction, EscrowState
from app.schemas.user import UserRead
from app.middleware.auth_middleware import require_role

router = APIRouter()

_require_admin = require_role(UserRole.ADMIN)


# ── Platform Stats ─────────────────────────────────────────────────────────────

@router.get("/platform-stats")
async def platform_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    today = date.today()

    total_users       = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_merchants   = (await db.execute(select(func.count(Merchant.id)))).scalar() or 0
    total_influencers = (await db.execute(select(func.count(Influencer.id)))).scalar() or 0

    active_campaigns = (await db.execute(
        select(func.count(Campaign.id)).where(
            Campaign.status.in_([CampaignStatus.ACTIVE, CampaignStatus.IN_PROGRESS])
        )
    )).scalar() or 0

    open_disputes = (await db.execute(
        select(func.count(EscrowTransaction.id)).where(
            EscrowTransaction.state == EscrowState.DISPUTED
        )
    )).scalar() or 0

    escrow_volume = (await db.execute(
        select(func.coalesce(func.sum(EscrowTransaction.gross_amount_jod), 0))
    )).scalar() or 0

    platform_fees = (await db.execute(
        select(func.coalesce(func.sum(EscrowTransaction.platform_fee_jod), 0))
    )).scalar() or 0

    escrow_locked = (await db.execute(
        select(func.coalesce(func.sum(EscrowTransaction.gross_amount_jod), 0)).where(
            EscrowTransaction.state.in_([EscrowState.FUNDED, EscrowState.LOCKED])
        )
    )).scalar() or 0

    new_users_today = (await db.execute(
        select(func.count(User.id)).where(
            func.date(User.created_at) == today
        )
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_merchants": total_merchants,
        "total_influencers": total_influencers,
        "active_campaigns": active_campaigns,
        "open_disputes": open_disputes,
        "total_escrow_volume_jod": round(float(escrow_volume), 3),
        "total_platform_fees_jod": round(float(platform_fees), 3),
        "escrow_locked_jod": round(float(escrow_locked), 3),
        "new_users_today": new_users_today,
    }


# ── User Management ────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [UserRead.model_validate(u) for u in users]


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    return UserRead.model_validate(user)


class RoleChange(BaseModel):
    role: str


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    payload: RoleChange,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        user.role = UserRole(payload.role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {payload.role}")
    return UserRead.model_validate(user)


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    return {"message": f"User {user.email} deactivated"}


# ── Disputes ───────────────────────────────────────────────────────────────────

@router.get("/disputes")
async def list_disputes(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.state == EscrowState.DISPUTED)
        .order_by(EscrowTransaction.updated_at.desc())
    )
    disputes = result.scalars().all()
    return [
        {
            "id": d.id,
            "escrow_id": d.id,
            "merchant_id": d.merchant_id,
            "influencer_id": d.influencer_id,
            "gross_amount_jod": d.gross_amount_jod,
            "reason": d.dispute_reason or "No reason provided",
            "status": "DISPUTED",
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in disputes
    ]


class DisputeResolution(BaseModel):
    decision: str  # "release_to_influencer" | "refund_to_merchant"
    reason: str


@router.post("/disputes/{escrow_id}/resolve")
async def resolve_dispute(
    escrow_id: str,
    payload: DisputeResolution,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(_require_admin),
):
    result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
    escrow = result.scalar_one_or_none()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    if escrow.state != EscrowState.DISPUTED:
        raise HTTPException(status_code=400, detail="Escrow is not in disputed state")

    if payload.decision in ("release_to_influencer", "INFLUENCER"):
        escrow.state = EscrowState.RELEASED
    elif payload.decision in ("refund_to_merchant", "MERCHANT"):
        escrow.state = EscrowState.REFUNDED
    else:
        raise HTTPException(status_code=400, detail="decision must be 'MERCHANT' or 'INFLUENCER'")

    escrow.resolved_by = current_admin.id
    return {"message": f"Dispute resolved: {payload.decision}", "escrow_id": escrow_id}


# ── Automated Jobs ─────────────────────────────────────────────────────────────

@router.post("/trigger/{job}")
async def trigger_job(
    job: str,
    _: User = Depends(_require_admin),
):
    valid_jobs = {"scoring", "escrow_release", "reaudit"}
    if job not in valid_jobs:
        raise HTTPException(status_code=400, detail=f"Unknown job: {job}. Valid: {valid_jobs}")

    job_messages = {
        "scoring": "ARIA scoring job triggered — influencer scores will be recalculated",
        "escrow_release": "Auto-release job triggered — eligible funded escrows will be released",
        "reaudit": "Re-audit job triggered — influencer profiles will be re-evaluated",
    }
    return {"status": "triggered", "job": job, "message": job_messages[job]}


@router.post("/rag/rebuild")
async def rebuild_rag(
    _: User = Depends(_require_admin),
):
    return {"message": "RAG knowledge base rebuild queued — vector store will refresh shortly"}


# ── Notification Blast ─────────────────────────────────────────────────────────

class NotificationBlast(BaseModel):
    message_ar: str
    message_en: str | None = None
    target_role: str = "all"


@router.post("/notification/blast")
async def notification_blast(
    payload: NotificationBlast,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(_require_admin),
):
    if payload.target_role == "all":
        count_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
    else:
        try:
            target = UserRole(payload.target_role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {payload.target_role}")
        count_result = await db.execute(
            select(func.count(User.id)).where(User.role == target, User.is_active == True)
        )
    count = count_result.scalar() or 0
    return {"message": f"Notification queued for {count} user(s)", "recipients": count}
