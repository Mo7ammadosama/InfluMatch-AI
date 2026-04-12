from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.models.escrow import EscrowTransaction, EscrowStatus
from backend.core.config import get_settings

settings = get_settings()
PLATFORM_COMMISSION = 0.05

VALID_TRANSITIONS = {
    EscrowStatus.PENDING:      [EscrowStatus.FUNDED, EscrowStatus.REFUNDED],
    EscrowStatus.FUNDED:       [EscrowStatus.IN_PROGRESS, EscrowStatus.REFUNDED],
    EscrowStatus.IN_PROGRESS:  [EscrowStatus.UNDER_REVIEW, EscrowStatus.DISPUTED],
    EscrowStatus.UNDER_REVIEW: [EscrowStatus.RELEASED, EscrowStatus.DISPUTED],
    EscrowStatus.DISPUTED:     [EscrowStatus.CANCELLED, EscrowStatus.REFUNDED, EscrowStatus.RELEASED],
    EscrowStatus.RELEASED:     [],
    EscrowStatus.REFUNDED:     [],
    EscrowStatus.CANCELLED:    [],
}

class EscrowEngine:
    async def fund_escrow(self, db: AsyncSession, campaign_id: int, merchant_id: int, amount_jod: float) -> EscrowTransaction:
        vat = round(amount_jod * settings.vat_rate, 3)
        fee = round(amount_jod * PLATFORM_COMMISSION, 3)
        net = round(amount_jod - fee, 3)
        escrow = EscrowTransaction(
            campaign_id=campaign_id, merchant_id=merchant_id,
            gross_amount=amount_jod, vat_amount=vat, platform_fee=fee, net_amount=net,
            status=EscrowStatus.FUNDED, funded_at=datetime.utcnow(),
            auto_release_at=datetime.utcnow() + timedelta(days=settings.escrow_release_days),
        )
        db.add(escrow)
        await db.flush()
        logger.success(f"[ARIA::ESCROW] Funded campaign={campaign_id} | {amount_jod} JOD | net={net} JOD")
        return escrow

    async def transition(self, db: AsyncSession, escrow_id: int, target: EscrowStatus, reason: str = None, by: str = "system") -> Dict:
        result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise ValueError(f"Escrow {escrow_id} not found")
        if target not in VALID_TRANSITIONS[escrow.status]:
            raise ValueError(f"Invalid transition: {escrow.status} -> {target}")
        prev = escrow.status
        escrow.status = target
        if target == EscrowStatus.RELEASED:
            escrow.released_at = datetime.utcnow()
            escrow.released_by = by
        if target == EscrowStatus.DISPUTED:
            escrow.dispute_reason = reason
            escrow.dispute_raised_at = datetime.utcnow()
            escrow.dispute_deadline = datetime.utcnow() + timedelta(hours=48)
        logger.success(f"[ARIA::ESCROW] Transition {escrow_id}: {prev} -> {target}")
        return {"escrow_id": escrow_id, "prev_status": prev, "new_status": target, "amount": escrow.net_amount}

    async def release_to_influencer(self, db: AsyncSession, escrow_id: int, released_by: str = "merchant") -> Dict:
        """Release escrow funds to influencer after content approval"""
        result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise ValueError(f"Escrow {escrow_id} not found")
        if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.IN_PROGRESS, EscrowStatus.UNDER_REVIEW]:
            raise ValueError(f"Cannot release escrow in status: {escrow.status}")
        escrow.status = EscrowStatus.RELEASED
        escrow.released_at = datetime.utcnow()
        escrow.released_by = released_by
        await db.commit()
        logger.success(f"[ARIA::ESCROW] Released escrow={escrow_id} | by={released_by} | net={escrow.net_amount} JOD")
        return {
            "escrow_id"   : escrow_id,
            "status"      : "RELEASED",
            "net_amount"  : escrow.net_amount,
            "released_by" : released_by,
            "released_at" : escrow.released_at.isoformat(),
            "currency"    : "JOD"
        }

    async def raise_dispute(self, db: AsyncSession, escrow_id: int, raised_by_id: int, reason: str) -> EscrowTransaction:
        """Raise a dispute — freezes escrow funds"""
        result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise ValueError(f"Escrow {escrow_id} not found")
        if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.IN_PROGRESS, EscrowStatus.UNDER_REVIEW]:
            raise ValueError(f"Cannot dispute escrow in status: {escrow.status}")
        escrow.status = EscrowStatus.DISPUTED
        escrow.dispute_reason = reason
        escrow.dispute_raised_by = raised_by_id
        escrow.dispute_raised_at = datetime.utcnow()
        escrow.dispute_deadline = datetime.utcnow() + timedelta(hours=48)
        await db.commit()
        logger.warning(f"[ARIA::ESCROW] Dispute raised escrow={escrow_id} | by={raised_by_id}")
        return escrow

escrow_engine = EscrowEngine()
