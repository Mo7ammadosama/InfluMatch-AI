"""
InfluMatch.jo — Escrow Service
State machine: PENDING → FUNDED → LOCKED → RELEASED / REFUNDED
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from loguru import logger
from app.models.escrow import EscrowTransaction, EscrowState
from app.config import settings

# Valid state transitions
VALID_TRANSITIONS: dict[EscrowState, list[EscrowState]] = {
    EscrowState.PENDING:   [EscrowState.FUNDED, EscrowState.REFUNDED],
    EscrowState.FUNDED:    [EscrowState.LOCKED, EscrowState.REFUNDED],
    EscrowState.LOCKED:    [EscrowState.RELEASED, EscrowState.DISPUTED, EscrowState.REFUNDED],
    EscrowState.DISPUTED:  [EscrowState.RESOLVED, EscrowState.REFUNDED, EscrowState.RELEASED],
    EscrowState.RELEASED:  [],
    EscrowState.REFUNDED:  [],
    EscrowState.RESOLVED:  [],
}


class EscrowService:

    def calculate_amounts(self, agreed_amount_jod: float) -> dict:
        fee = round(agreed_amount_jod * settings.escrow_fee_percent, 3)
        vat_on_fee = round(fee * settings.vat_rate, 3)
        net_to_influencer = round(agreed_amount_jod - fee - vat_on_fee, 3)
        return {
            "gross_amount_jod": agreed_amount_jod,
            "platform_fee_jod": fee,
            "vat_on_fee_jod": vat_on_fee,
            "net_to_influencer_jod": net_to_influencer,
        }

    async def create_escrow(
        self,
        merchant_id: str,
        influencer_id: str,
        agreed_amount_jod: float,
        db: AsyncSession,
    ) -> EscrowTransaction:
        amounts = self.calculate_amounts(agreed_amount_jod)
        escrow = EscrowTransaction(
            merchant_id=merchant_id,
            influencer_id=influencer_id,
            **amounts,
            state=EscrowState.PENDING,
            state_history=f"[{datetime.utcnow().isoformat()}] CREATED → PENDING",
        )
        db.add(escrow)
        await db.flush()
        logger.info(f"Escrow {escrow.id} created | {agreed_amount_jod} JOD | merchant={merchant_id}")
        return escrow

    async def transition(
        self,
        escrow_id: str,
        target_state: EscrowState,
        db: AsyncSession,
        reason: str | None = None,
    ) -> EscrowTransaction:
        result = await db.execute(select(EscrowTransaction).where(EscrowTransaction.id == escrow_id))
        escrow = result.scalar_one_or_none()
        if not escrow:
            raise HTTPException(status_code=404, detail=f"Escrow {escrow_id} not found")

        if target_state not in VALID_TRANSITIONS[escrow.state]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Invalid transition: {escrow.state} → {target_state}",
            )

        prev_state = escrow.state
        escrow.state = target_state
        history_entry = f"[{datetime.utcnow().isoformat()}] {prev_state} → {target_state}"
        if reason:
            history_entry += f" | reason: {reason}"
        escrow.state_history = (escrow.state_history or "") + "\n" + history_entry

        if target_state == EscrowState.FUNDED:
            escrow.funded_at = datetime.utcnow()
        elif target_state == EscrowState.RELEASED:
            escrow.released_at = datetime.utcnow()

        logger.info(f"Escrow {escrow_id}: {prev_state} → {target_state}")
        return escrow


escrow_service = EscrowService()
