from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.models.escrow import EscrowTransaction, EscrowStatus
from backend.core.config import get_settings

settings = get_settings()
PLATFORM_COMMISSION = 0.10
_STRIPE_DUMMY_VALUES = ("", "sk_test_your_key", "sk_test_placeholder")


def _stripe_enabled() -> bool:
    key = settings.stripe_test_key or ""
    return key not in _STRIPE_DUMMY_VALUES and key.startswith("sk_")


def _stripe_charge(amount_jod: float, description: str) -> Optional[str]:
    """
    Attempt Stripe PaymentIntent. Returns payment_intent_id or None on failure.
    Gracefully skips if Stripe not configured.
    """
    if not _stripe_enabled():
        return None
    try:
        import stripe
        stripe.api_key = settings.stripe_test_key
        # Stripe uses smallest currency unit — JOD has 3 decimal places (fils)
        amount_fils = int(round(amount_jod * 1000))
        intent = stripe.PaymentIntent.create(
            amount      = amount_fils,
            currency    = "jod",
            description = description,
            metadata    = {"platform": "WaslAI.jo"},
        )
        logger.success(f"[ARIA::STRIPE] PaymentIntent created: {intent.id} | {amount_jod} JOD")
        return intent.id
    except Exception as exc:
        logger.warning(f"[ARIA::STRIPE] Charge failed (non-fatal): {exc}")
        return None


def _stripe_transfer(amount_jod: float, connect_account: str, description: str) -> Optional[str]:
    """
    Attempt Stripe Transfer to influencer Connect account. Returns transfer_id or None.
    """
    if not _stripe_enabled() or not connect_account:
        return None
    try:
        import stripe
        stripe.api_key = settings.stripe_test_key
        amount_fils = int(round(amount_jod * 1000))
        transfer = stripe.Transfer.create(
            amount      = amount_fils,
            currency    = "jod",
            destination = connect_account,
            description = description,
        )
        logger.success(f"[ARIA::STRIPE] Transfer created: {transfer.id} | {amount_jod} JOD → {connect_account}")
        return transfer.id
    except Exception as exc:
        logger.warning(f"[ARIA::STRIPE] Transfer failed (non-fatal): {exc}")
        return None

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
    PLATFORM_COMMISSION = PLATFORM_COMMISSION  # expose as class attr for tests

    async def fund_escrow(self, db: AsyncSession, campaign_id: int, merchant_id: int, amount_jod: float) -> EscrowTransaction:
        vat = round(amount_jod * settings.vat_rate, 3)
        fee = round(amount_jod * PLATFORM_COMMISSION, 3)
        net = round(amount_jod - fee, 3)

        # Attempt Stripe charge (non-blocking — ledger works regardless)
        stripe_payment_id = _stripe_charge(
            amount_jod  = amount_jod,
            description = f"WaslAI Escrow — campaign={campaign_id} merchant={merchant_id}",
        )

        escrow = EscrowTransaction(
            campaign_id       = campaign_id,
            merchant_id       = merchant_id,
            gross_amount      = amount_jod,
            vat_amount        = vat,
            platform_fee      = fee,
            net_amount        = net,
            status            = EscrowStatus.FUNDED,
            funded_at         = datetime.utcnow(),
            auto_release_at   = datetime.utcnow() + timedelta(days=settings.escrow_release_days),
            stripe_payment_id = stripe_payment_id,
        )
        db.add(escrow)
        await db.flush()
        mode = "Stripe+Ledger" if stripe_payment_id else "Ledger-only"
        logger.success(f"[ARIA::ESCROW] Funded campaign={campaign_id} | {amount_jod} JOD | net={net} JOD | mode={mode}")
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

        # Attempt Stripe transfer to influencer's Connect account (non-blocking)
        stripe_transfer_id = None
        if escrow.campaign_id:
            try:
                from backend.models.campaign import Campaign
                from backend.models.influencer import Influencer
                from backend.models.campaign import CampaignInfluencer
                from sqlalchemy import select as _select
                # Try to find influencer's Stripe account via booking
                from backend.models.booking import Booking
                booking_r = await db.execute(
                    _select(Booking).where(Booking.escrow_id == escrow_id)
                )
                booking = booking_r.scalar_one_or_none()
                if booking:
                    inf_r = await db.execute(_select(Influencer).where(Influencer.id == booking.influencer_id))
                    inf   = inf_r.scalar_one_or_none()
                    if inf and getattr(inf, "stripe_connect_account_id", None):
                        stripe_transfer_id = _stripe_transfer(
                            amount_jod      = float(escrow.net_amount),
                            connect_account = inf.stripe_connect_account_id,
                            description     = f"WaslAI payout escrow={escrow_id}",
                        )
            except Exception as exc:
                logger.warning(f"[ARIA::STRIPE] Transfer lookup failed (non-fatal): {exc}")

        escrow.status             = EscrowStatus.RELEASED
        escrow.released_at        = datetime.utcnow()
        escrow.released_by        = released_by
        if stripe_transfer_id:
            escrow.stripe_transfer_id = stripe_transfer_id

        # Credit influencer's loyalty wallet (100 points per JOD)
        try:
            from backend.models.booking import Booking
            from backend.models.wallet import LoyaltyWallet, WalletTransaction, TransactionType
            booking_r = await db.execute(select(Booking).where(Booking.escrow_id == escrow_id))
            booking   = booking_r.scalar_one_or_none()
            if booking:
                from backend.models.influencer import Influencer as _Inf
                inf_r   = await db.execute(select(_Inf).where(_Inf.id == booking.influencer_id))
                inf_obj = inf_r.scalar_one_or_none()
                if inf_obj:
                    wallet_r = await db.execute(select(LoyaltyWallet).where(LoyaltyWallet.user_id == inf_obj.user_id))
                    wallet   = wallet_r.scalar_one_or_none()
                    if wallet:
                        pts_earned          = int(float(escrow.net_amount) * 100)
                        wallet.total_points = (wallet.total_points or 0) + pts_earned
                        wallet.updated_at   = datetime.utcnow()
                        balance_after       = (wallet.total_points or 0) - (wallet.redeemed_points or 0) - (wallet.expired_points or 0)
                        db.add(WalletTransaction(
                            wallet_id        = wallet.id,
                            points           = pts_earned,
                            transaction_type = "EARN_CAMPAIGN_COMPLETED",
                            balance_after    = balance_after,
                            description_en   = f"Earned from booking #{booking.id} — {escrow.net_amount} JOD",
                            description_ar   = f"مكاسب من الحجز #{booking.id} — {escrow.net_amount} دينار",
                            reference_id     = str(booking.id),
                        ))
                        logger.success(f"[ARIA::WALLET] Credited {pts_earned} pts to user={inf_obj.user_id} for escrow={escrow_id}")
        except Exception as wallet_exc:
            logger.warning(f"[ARIA::WALLET] Wallet credit failed (non-fatal): {wallet_exc}")

        # No commit here — caller owns the transaction boundary
        mode = "Stripe+Ledger" if stripe_transfer_id else "Ledger-only"
        logger.success(f"[ARIA::ESCROW] Released escrow={escrow_id} | by={released_by} | net={escrow.net_amount} JOD | mode={mode}")
        return {
            "escrow_id"          : escrow_id,
            "status"             : "RELEASED",
            "net_amount"         : escrow.net_amount,
            "released_by"        : released_by,
            "released_at"        : escrow.released_at.isoformat(),
            "stripe_transfer_id" : stripe_transfer_id,
            "payment_mode"       : mode,
            "currency"           : "JOD",
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
        # No commit here — caller owns the transaction boundary
        logger.warning(f"[ARIA::ESCROW] Dispute raised escrow={escrow_id} | by={raised_by_id}")
        return escrow

escrow_engine = EscrowEngine()
