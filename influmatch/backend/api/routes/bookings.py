"""Booking API — WaslAI.jo | Merchant books Influencer directly"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from loguru import logger
from ...core.database import get_db
from ...schemas.common import make_page
from ...agents.auditor_agent import auditor as aria_auditor
from ...models.user import User
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...models.booking import Booking, BookingStatus
from ...services.escrow.escrow_engine import EscrowEngine
from ...services.notifications.notification_service import NotificationService
from ..dependencies.auth_deps import get_current_user
from ...core.config import get_settings

router   = APIRouter(prefix="/bookings", tags=["Bookings"])
settings = get_settings()


# ── POST /bookings/ — Merchant creates booking ──────────────────────────────
@router.post("/", status_code=201)
async def create_booking(
    payload      : dict,
    current_user : User          = Depends(get_current_user),
    db           : AsyncSession  = Depends(get_db),
):
    merch_q  = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
    merchant = merch_q.scalar_one_or_none()
    if not merchant:
        raise HTTPException(403, "أنشئ ملف التاجر أولاً / Create merchant profile first")

    inf_q      = await db.execute(select(Influencer).where(Influencer.id == payload.get("influencer_id")))
    influencer = inf_q.scalar_one_or_none()
    if not influencer:
        raise HTTPException(404, "Influencer not found")
    if not influencer.is_available:
        raise HTTPException(409, "المؤثر غير متاح حالياً / Influencer is not available")

    rate = payload.get("agreed_rate_jod") or influencer.rate_per_post or 0
    if float(rate) <= 0:
        raise HTTPException(400, "يجب تحديد المبلغ / Rate must be greater than 0")
    rate = round(float(rate), 3)

    deadline_dt = None
    if payload.get("deadline"):
        try:
            deadline_dt = datetime.fromisoformat(payload["deadline"])
        except ValueError:
            raise HTTPException(400, "Invalid deadline format — use ISO 8601 (YYYY-MM-DD)")

    booking = Booking(
        merchant_id    = merchant.id,
        influencer_id  = influencer.id,
        campaign_id    = payload.get("campaign_id"),
        agreed_rate_jod= rate,
        brief          = payload.get("brief", ""),
        deliverables   = payload.get("deliverables", []),
        deadline       = deadline_dt,
        status         = BookingStatus.PENDING,
    )
    db.add(booking)
    await db.flush()  # get booking.id before escrow

    # Fund escrow — reuse existing escrow if one already exists for this campaign
    engine = EscrowEngine()
    existing_escrow = None
    if booking.campaign_id:
        from ...models.escrow import EscrowTransaction
        ex_res = await db.execute(
            select(EscrowTransaction).where(EscrowTransaction.campaign_id == booking.campaign_id)
        )
        existing_escrow = ex_res.scalar_one_or_none()
    if existing_escrow:
        escrow_tx = existing_escrow
    else:
        escrow_tx = await engine.fund_escrow(
            db          = db,
            campaign_id = booking.campaign_id,
            merchant_id = merchant.id,
            amount_jod  = rate,
        )
    booking.escrow_id = escrow_tx.id
    await db.commit()
    await db.refresh(booking)

    # Notify influencer (phone not on Influencer model — load user)
    try:
        user_q   = await db.execute(select(User).where(User.id == influencer.user_id))
        inf_user = user_q.scalar_one_or_none()
        ns = NotificationService()
        ns.send_whatsapp("", f"طلب حجز جديد من {merchant.business_name_ar or 'تاجر'} بقيمة {rate} JOD")
        ns.send_email(
            to      = inf_user.email if inf_user else "",
            subject = "طلب حجز جديد / New Booking Request",
            body_ar = f"وصلك طلب حجز من <b>{merchant.business_name_ar or 'تاجر'}</b> بقيمة <b>{rate} JOD</b>",
            body_en = f"New booking request: <b>{rate} JOD</b>",
        )
    except Exception as exc:
        logger.warning(f"[BOOKING] Notification failed: {exc}")

    logger.success(f"[BOOKING] Created #{booking.id} | merchant={merchant.id} | influencer={influencer.id} | {rate} JOD")
    return {
        "booking_id": booking.id,
        "status"    : booking.status,
        "rate_jod"  : rate,
        "escrow_id" : escrow_tx.id,
        "message"   : "تم إرسال طلب الحجز وتجميد المبلغ في Escrow",
    }


# ── GET /bookings/my — Role-based booking list ───────────────────────────────
@router.get("/my")
async def get_my_bookings(
    skip         : int          = 0,
    limit        : int          = 20,
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    base_q = select(Booking)
    if role == "merchant":
        merch_q  = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merchant = merch_q.scalar_one_or_none()
        if not merchant:
            return make_page([], 0, skip, limit)
        base_q = base_q.where(Booking.merchant_id == merchant.id)
    elif role == "influencer":
        inf_q      = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
        influencer = inf_q.scalar_one_or_none()
        if not influencer:
            return make_page([], 0, skip, limit)
        base_q = base_q.where(Booking.influencer_id == influencer.id)
    # else admin: no filter — sees all

    count_r = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total   = count_r.scalar_one()

    result   = await db.execute(base_q.order_by(Booking.created_at.desc()).offset(skip).limit(limit))
    bookings = result.scalars().all()

    data = [
        {
            "id"             : b.id,
            "status"         : b.status.value if hasattr(b.status, "value") else b.status,
            "agreed_rate_jod": round(b.agreed_rate_jod, 3),
            "brief"          : b.brief,
            "deliverables"   : b.deliverables,
            "deadline"       : b.deadline.isoformat() if b.deadline else None,
            "content_url"    : b.content_url,
            "ai_review_result": b.ai_review_result,
            "escrow_id"      : b.escrow_id,
            "merchant_id"    : b.merchant_id,
            "influencer_id"  : b.influencer_id,
            "created_at"     : b.created_at.isoformat() if b.created_at else None,
        }
        for b in bookings
    ]
    return make_page(data, total, skip, limit)


# ── POST /bookings/{id}/confirm — Influencer accepts ─────────────────────────
@router.post("/{booking_id}/confirm")
async def confirm_booking(
    booking_id   : int,
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    b_q     = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = b_q.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(400, f"Cannot confirm booking in status: {booking.status}")

    booking.status     = BookingStatus.CONFIRMED
    booking.updated_at = datetime.utcnow()

    inf = await db.get(Influencer, booking.influencer_id)
    if inf:
        inf.is_available = False

    db.add(booking)
    await db.commit()
    logger.success(f"[BOOKING] Confirmed #{booking_id}")
    return {"booking_id": booking_id, "status": "confirmed", "message": "تم قبول الحجز / Booking confirmed"}


# ── POST /bookings/{id}/submit-content — Influencer submits ──────────────────
@router.post("/{booking_id}/submit-content")
async def submit_content(
    booking_id   : int,
    payload      : dict,
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    b_q     = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = b_q.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Booking not found")
    # Allow resubmission when ARIA previously rejected the content
    raw_review = booking.ai_review_result or {}
    if isinstance(raw_review, str):
        import json as _json
        try:
            raw_review = _json.loads(raw_review)
        except Exception:
            raw_review = {}
    aria_rejected = raw_review.get("verdict") == "REJECTED"

    allowed = booking.status in (BookingStatus.CONFIRMED, BookingStatus.CONTENT_SUBMITTED)
    if not allowed or (booking.status == BookingStatus.CONTENT_SUBMITTED and not aria_rejected):
        raise HTTPException(400, "يجب تأكيد الحجز أولاً / Booking must be confirmed first")

    content_url = payload.get("content_url", "").strip()
    if not content_url:
        raise HTTPException(400, "content_url is required")

    booking.content_url          = content_url
    booking.content_submitted_at = datetime.utcnow()
    booking.status               = BookingStatus.CONTENT_SUBMITTED

    ai_result = {"approved": False, "score": 0, "notes": "Review pending", "verdict": "PENDING"}

    if settings.anthropic_api_key and settings.anthropic_api_key not in ("", "your_key_here"):
        try:
            # Build campaign requirements for the auditor
            campaign_requirements = {
                "brand_name_en": "",
                "hashtags"     : booking.deliverables or [],
                "niche"        : "general",
            }
            if booking.campaign_id:
                from ...models.campaign import Campaign
                camp_r = await db.execute(
                    select(Campaign).where(Campaign.id == booking.campaign_id)
                )
                camp = camp_r.scalar_one_or_none()
                if camp:
                    campaign_requirements["niche"] = camp.niche or "general"
                    campaign_requirements["brand_name_en"] = camp.title_en or camp.title_ar or ""

            caption_text = payload.get("caption", "").strip() or content_url
            submission = {
                "id"         : booking_id,
                "platform"   : "instagram",
                "caption"    : caption_text,
                "content_url": content_url,
            }
            audit = await aria_auditor.audit_content_submission(submission, campaign_requirements)
            final = audit.get("final_decision", {})
            combined_score = final.get("combined_score", 0)
            verdict        = final.get("verdict", "REJECTED")

            ai_result = {
                "approved"    : verdict == "APPROVED",
                "score"       : combined_score,
                "verdict"     : verdict,
                "notes"       : str(audit.get("text_audit", {}).get("recommendations", [])),
                "auto_approved": final.get("auto_approved", False),
            }

            if ai_result["approved"] and combined_score >= 70:
                booking.status              = BookingStatus.CONTENT_APPROVED
                booking.content_approved_at = datetime.utcnow()

                # Update influencer's content quality score for ARIA re-scoring
                inf = await db.get(Influencer, booking.influencer_id)
                if inf:
                    inf.content_quality_score = combined_score

        except Exception as exc:
            logger.warning(f"[BOOKING] AuditorAgent review failed: {exc}")

    booking.ai_review_result = ai_result
    db.add(booking)
    await db.commit()
    logger.success(f"[BOOKING] Content submitted #{booking_id} | score={ai_result.get('score', 0)} | verdict={ai_result.get('verdict')}")
    return {"booking_id": booking_id, "status": booking.status, "ai_review": ai_result}


# ── POST /bookings/{id}/release — Release escrow after approval ───────────────
@router.post("/{booking_id}/release")
async def release_booking(
    booking_id   : int,
    payload      : dict         = None,
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    if payload is None:
        payload = {}
    override = payload.get("override", False)

    b_q     = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = b_q.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Booking not found")

    allowed_statuses = (BookingStatus.CONTENT_APPROVED,)
    if override:
        # Merchant manually approves despite ARIA rejection
        allowed_statuses = (BookingStatus.CONTENT_APPROVED, BookingStatus.CONTENT_SUBMITTED)
        if booking.status == BookingStatus.CONTENT_SUBMITTED:
            booking.status              = BookingStatus.CONTENT_APPROVED
            booking.content_approved_at = datetime.utcnow()
            logger.info(f"[BOOKING] Merchant manual override #{booking_id}")

    if booking.status not in allowed_statuses:
        raise HTTPException(400, f"Cannot release in status: {booking.status}")
    if not booking.escrow_id:
        raise HTTPException(400, "No escrow linked to this booking")

    engine = EscrowEngine()
    result = await engine.release_to_influencer(
        db          = db,
        escrow_id   = booking.escrow_id,
        released_by = "platform_auto",
    )

    booking.status     = BookingStatus.RELEASED
    booking.updated_at = datetime.utcnow()

    inf = await db.get(Influencer, booking.influencer_id)
    if inf:
        inf.is_available = True

    db.add(booking)
    await db.commit()
    logger.success(f"[BOOKING] Released #{booking_id} | escrow={booking.escrow_id}")
    return {
        "booking_id": booking_id,
        "status"    : "released",
        "net_amount": result.get("net_amount"),
        "message"   : "تم تحويل المبلغ للمؤثر / Amount released to influencer",
    }
