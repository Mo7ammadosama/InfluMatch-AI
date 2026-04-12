from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from ...core.database import get_db
from ...services.escrow.escrow_engine import EscrowEngine
from ...models.escrow import EscrowTransaction, EscrowStatus
from loguru import logger

router = APIRouter(prefix="/escrow", tags=["Escrow"])
engine = EscrowEngine()

class FundRequest(BaseModel):
    campaign_id : int
    merchant_id : int
    amount_jod  : float

class DisputeRequest(BaseModel):
    reason      : str
    raised_by_id: int

@router.post("/fund")
async def fund_escrow(req: FundRequest, db: AsyncSession = Depends(get_db)):
    """Fund escrow for a campaign — locks payment"""
    tx = await engine.fund_escrow(
        db, req.campaign_id, req.merchant_id, req.amount_jod
    )
    return {
        "escrow_id"     : tx.id,
        "gross_amount"  : tx.gross_amount,
        "net_amount"    : tx.net_amount,
        "vat_amount"    : tx.vat_amount,
        "platform_fee"  : tx.platform_fee,
        "status"        : tx.status,
        "auto_release_at": tx.auto_release_at.isoformat(),
        "currency"      : "JOD"
    }

@router.post("/{escrow_id}/release")
async def release_escrow(
    escrow_id   : int,
    released_by : str = "merchant",
    db          : AsyncSession = Depends(get_db)
):
    """Release escrow funds to influencer"""
    try:
        result = await engine.release_to_influencer(db, escrow_id, released_by)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{escrow_id}/dispute")
async def raise_dispute(
    escrow_id: int,
    req      : DisputeRequest,
    db       : AsyncSession = Depends(get_db)
):
    """Raise a dispute — freezes escrow funds"""
    try:
        tx = await engine.raise_dispute(db, escrow_id, req.raised_by_id, req.reason)
        return {
            "escrow_id"       : escrow_id,
            "status"          : "DISPUTED",
            "dispute_deadline": tx.dispute_deadline.isoformat(),
            "message"         : "Dispute received. ARIA will review within 48 hours."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{escrow_id}")
async def get_escrow_status(escrow_id: int, db: AsyncSession = Depends(get_db)):
    """Get current escrow transaction status"""
    result = await db.execute(
        select(EscrowTransaction).where(EscrowTransaction.id == escrow_id)
    )
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Escrow not found")
    return {
        "id"            : tx.id,
        "campaign_id"   : tx.campaign_id,
        "status"        : tx.status,
        "gross_amount"  : tx.gross_amount,
        "net_amount"    : tx.net_amount,
        "currency"      : "JOD",
        "funded_at"     : tx.funded_at.isoformat() if tx.funded_at else None,
        "auto_release_at": tx.auto_release_at.isoformat() if tx.auto_release_at else None
    }
# ============================================================