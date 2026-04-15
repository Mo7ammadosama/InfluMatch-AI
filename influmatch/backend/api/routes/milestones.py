from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from datetime import datetime

from ...core.database import get_db
from ...models.milestone import CampaignMilestone, MilestoneStatus
from ...models.campaign import Campaign
from ...services.escrow.escrow_engine import EscrowEngine
from loguru import logger

router = APIRouter(prefix="/milestones", tags=["Milestones"])
escrow_engine = EscrowEngine()


def validate_milestone_percentages(percentages: List[float]) -> None:
    total = sum(percentages)
    if abs(total - 100.0) > 0.01:
        raise ValueError(f"Milestone percentages must sum to 100%, got {total:.1f}%")


class MilestoneIn(BaseModel):
    title      : str
    percentage : float
    due_date   : datetime


class MilestoneOut(BaseModel):
    id          : int
    campaign_id : int
    title       : str
    percentage  : float
    amount_jod  : float
    status      : MilestoneStatus
    due_date    : datetime
    released_at : datetime | None = None

    class Config:
        from_attributes = True


@router.post("/{campaign_id}/create", response_model=List[MilestoneOut], status_code=201)
async def create_milestones(
    campaign_id : int,
    items       : List[MilestoneIn],
    db          : AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    try:
        validate_milestone_percentages([m.percentage for m in items])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    milestones = []
    for item in items:
        amount = round(campaign.total_budget * item.percentage / 100, 3)
        ms = CampaignMilestone(
            campaign_id = campaign_id,
            title       = item.title,
            percentage  = item.percentage,
            amount_jod  = amount,
            due_date    = item.due_date,
        )
        db.add(ms)
        milestones.append(ms)

    await db.flush()
    logger.success(f"[ARIA::MILESTONES] Created {len(milestones)} milestones for campaign={campaign_id}")
    return milestones


@router.get("/{campaign_id}", response_model=List[MilestoneOut])
async def list_milestones(campaign_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CampaignMilestone).where(CampaignMilestone.campaign_id == campaign_id)
    )
    return result.scalars().all()


@router.post("/{milestone_id}/release")
async def release_milestone(milestone_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CampaignMilestone).where(CampaignMilestone.id == milestone_id))
    ms = result.scalar_one_or_none()
    if not ms:
        raise HTTPException(status_code=404, detail="Milestone not found")
    if ms.status != MilestoneStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Milestone status is {ms.status}, only PENDING can be released")

    ms.status      = MilestoneStatus.RELEASED
    ms.released_at = datetime.utcnow()
    await db.flush()

    logger.success(f"[ARIA::MILESTONES] Released milestone={milestone_id} | {ms.amount_jod} JOD")

    try:
        from ...services.notifications.notification_service import NotificationService
        ns = NotificationService()
        ns.notify_milestone_released("influencer@platform.jo", ms.title, ms.amount_jod)
    except Exception as exc:
        logger.warning(f"[ARIA::MILESTONES] Notification failed: {exc}")

    return {
        "milestone_id" : milestone_id,
        "title"        : ms.title,
        "status"       : "RELEASED",
        "amount_jod"   : ms.amount_jod,
        "released_at"  : ms.released_at.isoformat(),
        "currency"     : "JOD",
    }


@router.post("/{milestone_id}/dispute")
async def dispute_milestone(milestone_id: int, reason: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CampaignMilestone).where(CampaignMilestone.id == milestone_id))
    ms = result.scalar_one_or_none()
    if not ms:
        raise HTTPException(status_code=404, detail="Milestone not found")
    if ms.status != MilestoneStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Cannot dispute milestone in status: {ms.status}")

    ms.status = MilestoneStatus.DISPUTED
    await db.flush()
    logger.warning(f"[ARIA::MILESTONES] Disputed milestone={milestone_id} | reason={reason}")
    return {"milestone_id": milestone_id, "status": "DISPUTED", "reason": reason}
