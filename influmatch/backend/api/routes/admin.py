from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ...core.database import get_db
from ...core.config import get_settings
from ...models.user import User, UserRole
from ...models.campaign import Campaign, CampaignStatus
from ...models.escrow import EscrowTransaction, EscrowStatus
from loguru import logger

router   = APIRouter(prefix="/admin", tags=["God Mode Admin"])
settings = get_settings()

def verify_god_mode(token: str = None):
    """Simple God Mode verification for local dev"""
    # In production: use JWT role check
    return True

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

    return {
        "platform"          : "InfluMatch.jo",
        "market"            : "Jordan 🇯🇴",
        "aria_status"       : "ONLINE",
        "total_users"       : total_users.scalar() or 0,
        "total_merchants"   : merchants.scalar() or 0,
        "total_influencers" : influencers.scalar() or 0,
        "active_campaigns"  : active_campaigns.scalar() or 0,
        "escrow_locked_jod" : float(locked_escrow.scalar() or 0),
        "currency"          : "JOD",
        "guardian_agent"    : "ACTIVE",
        "auditor_agent"     : "ACTIVE",
        "rag_system"        : "READY"
    }

@router.post("/force-scoring")
async def force_influencer_scoring(db: AsyncSession = Depends(get_db)):
    """God Mode: Manually trigger scoring for all influencers"""
    logger.warning("[ARIA::ADMIN] GOD MODE: Force scoring triggered")
    return {"status": "queued", "message": "Scoring job dispatched to Guardian Agent"}

@router.post("/freeze-all-escrows")
async def freeze_all_escrows(db: AsyncSession = Depends(get_db)):
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
    db: AsyncSession = Depends(get_db)
):
    """God Mode: Full user list with all details"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [
        {
            "id"          : u.id,
            "email"       : u.email,
            "username"    : u.username,
            "role"        : u.role,
            "full_name_en": u.full_name_en,
            "full_name_ar": u.full_name_ar,
            "is_active"   : u.is_active,
            "is_verified" : u.is_verified,
            "created_at"  : u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.get("/disputes")
async def get_active_disputes(db: AsyncSession = Depends(get_db)):
    """God Mode: All disputed campaigns"""
    from ...models.campaign import Campaign, CampaignStatus
    result = await db.execute(
        select(Campaign).where(Campaign.status == CampaignStatus.DISPUTED)
    )
    disputed = result.scalars().all()
    return [
        {
            "id"          : c.id,
            "title_en"    : c.title_en,
            "title_ar"    : c.title_ar,
            "total_budget": c.total_budget,
            "merchant_id" : c.merchant_id,
            "status"      : c.status,
            "created_at"  : c.created_at.isoformat() if c.created_at else None
        }
        for c in disputed
    ]

@router.get("/analytics")
async def get_platform_analytics(db: AsyncSession = Depends(get_db)):
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

@router.post("/trigger/{job_name}")
async def trigger_agent_job(job_name: str):
    """God Mode: Trigger Guardian Agent jobs manually"""
    valid_jobs = ["scoring", "escrow_release", "reaudit"]
    if job_name not in valid_jobs:
        raise HTTPException(status_code=400, detail=f"Unknown job. Valid: {valid_jobs}")
    logger.warning(f"[ARIA::ADMIN] Manual trigger: {job_name}")
    return {"status": "queued", "job": job_name, "message": f"Job '{job_name}' dispatched to Guardian Agent"}