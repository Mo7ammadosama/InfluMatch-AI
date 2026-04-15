"""Booking API — InfluMatch.jo | Merchant books Influencer directly"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from loguru import logger
from ...core.database import get_db
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

    # Fund escrow — campaign_id may be None for direct bookings (SQLite allows NULL in UNIQUE)
    engine    = EscrowEngine()
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
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    if role == "merchant":
        merch_q  = await db.execute(select(Merchant).where(Merchant.user_id == current_user.id))
        merchant = merch_q.scalar_one_or_none()
        if not merchant:
            return []
        result = await db.execute(
            select(Booking).where(Booking.merchant_id == merchant.id)
            .order_by(Booking.created_at.desc())
        )
    elif role == "influencer":
        inf_q      = await db.execute(select(Influencer).where(Influencer.user_id == current_user.id))
        influencer = inf_q.scalar_one_or_none()
        if not influencer:
            return []
        result = await db.execute(
            select(Booking).where(Booking.influencer_id == influencer.id)
            .order_by(Booking.created_at.desc())
        )
    else:
        result = await db.execute(select(Booking).order_by(Booking.created_at.desc()))

    bookings = result.scalars().all()
    return [
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
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(400, "يجب تأكيد الحجز أولاً / Booking must be confirmed first")

    content_url = payload.get("content_url", "").strip()
    if not content_url:
        raise HTTPException(400, "content_url is required")

    booking.content_url          = content_url
    booking.content_submitted_at = datetime.utcnow()
    booking.status               = BookingStatus.CONTENT_SUBMITTED

    ai_result = {"approved": False, "score": 0, "notes": "Review pending"}
    if settings.anthropic_api_key and settings.anthropic_api_key not in ("", "your_key_here"):
        try:
            from anthropic import Anthropic
            import json as _json
            client = Anthropic(api_key=settings.anthropic_api_key)
            review_prompt = f"""أنت مراجع محتوى لمنصة InfluMatch.jo.
رابط المحتوى: {content_url}
ملخص الحملة: {booking.brief or 'لا يوجد'}
المطلوب: {booking.deliverables or []}

قيّم المحتوى من 0-100 وحدد:
1. هل المحتوى مناسب؟ (نعم/لا)
2. درجة الجودة (0-100)
3. ملاحظات قصيرة

أجب بـ JSON فقط: {{"approved": true/false, "score": 0-100, "notes": "..."}}"""
            resp = client.messages.create(
                model=settings.claude_model, max_tokens=256,
                messages=[{"role": "user", "content": review_prompt}]
            )
            ai_result = _json.loads(resp.content[0].text)
            if ai_result.get("approved") and ai_result.get("score", 0) >= 70:
                booking.status              = BookingStatus.CONTENT_APPROVED
                booking.content_approved_at = datetime.utcnow()
        except Exception as exc:
            logger.warning(f"[BOOKING] AI review failed: {exc}")

    booking.ai_review_result = ai_result
    db.add(booking)
    await db.commit()
    logger.success(f"[BOOKING] Content submitted #{booking_id} | AI score={ai_result.get('score', 0)}")
    return {"booking_id": booking_id, "status": booking.status, "ai_review": ai_result}


# ── POST /bookings/{id}/release — Release escrow after approval ───────────────
@router.post("/{booking_id}/release")
async def release_booking(
    booking_id   : int,
    current_user : User         = Depends(get_current_user),
    db           : AsyncSession = Depends(get_db),
):
    b_q     = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = b_q.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.status not in (BookingStatus.CONTENT_APPROVED,):
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
