from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ...core.database import get_db
from ...schemas.common import make_page
from ...models.message import Message
from ...models.booking import Booking
from ...models.merchant import Merchant
from ...models.influencer import Influencer
from ...models.user import User
from ..dependencies.auth_deps import get_current_user
from loguru import logger

router = APIRouter(prefix="/messages", tags=["Messages"])


class SendMessage(BaseModel):
    booking_id : int
    content    : str


async def _resolve_receiver_id(db: AsyncSession, booking: Booking, sender_user_id: int) -> int:
    """Given a booking and the sender, return the other party's user_id."""
    merchant_r = await db.execute(select(Merchant).where(Merchant.id == booking.merchant_id))
    merchant   = merchant_r.scalar_one_or_none()
    if not merchant:
        raise HTTPException(404, "Merchant not found for booking")

    inf_r = await db.execute(select(Influencer).where(Influencer.id == booking.influencer_id))
    inf   = inf_r.scalar_one_or_none()
    if not inf:
        raise HTTPException(404, "Influencer not found for booking")

    if sender_user_id == merchant.user_id:
        return inf.user_id
    elif sender_user_id == inf.user_id:
        return merchant.user_id
    else:
        raise HTTPException(403, "You are not a party to this booking")


@router.post("/", status_code=201)
async def send_message(
    data         : SendMessage,
    db           : AsyncSession = Depends(get_db),
    current_user : User         = Depends(get_current_user),
):
    """Send a message on a booking thread."""
    if not data.content.strip():
        raise HTTPException(400, "Message content cannot be empty")

    booking_r = await db.execute(select(Booking).where(Booking.id == data.booking_id))
    booking   = booking_r.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, f"Booking {data.booking_id} not found")

    receiver_id = await _resolve_receiver_id(db, booking, current_user.id)

    msg = Message(
        booking_id  = data.booking_id,
        sender_id   = current_user.id,
        receiver_id = receiver_id,
        content     = data.content.strip(),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    logger.info(f"[MESSAGES] booking={data.booking_id} from={current_user.id} → {receiver_id}")
    return {
        "id"         : msg.id,
        "booking_id" : msg.booking_id,
        "sender_id"  : msg.sender_id,
        "content"    : msg.content,
        "is_read"    : msg.is_read,
        "created_at" : msg.created_at.isoformat(),
    }


@router.get("/{booking_id}")
async def get_thread(
    booking_id   : int,
    skip         : int          = 0,
    limit        : int          = 50,
    db           : AsyncSession = Depends(get_db),
    current_user : User         = Depends(get_current_user),
):
    """Get messages for a booking thread (paginated). Only parties to the booking can read."""
    booking_r = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking   = booking_r.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, f"Booking {booking_id} not found")

    # Access check
    await _resolve_receiver_id(db, booking, current_user.id)  # raises 403 if not a party

    # Total message count for this thread
    count_r = await db.execute(
        select(func.count(Message.id)).where(Message.booking_id == booking_id)
    )
    total = count_r.scalar_one()

    # Paginated messages
    result = await db.execute(
        select(Message)
        .where(Message.booking_id == booking_id)
        .order_by(Message.created_at.asc())
        .offset(skip).limit(limit)
    )
    messages = result.scalars().all()

    # Mark ALL unread incoming messages as read (not just current page)
    unread_r = await db.execute(
        select(Message).where(
            Message.booking_id == booking_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False,  # noqa: E712
        )
    )
    for m in unread_r.scalars().all():
        m.is_read = True
    await db.commit()

    data = [
        {
            "id"         : m.id,
            "sender_id"  : m.sender_id,
            "receiver_id": m.receiver_id,
            "content"    : m.content,
            "is_read"    : m.is_read,
            "created_at" : m.created_at.isoformat(),
            "is_mine"    : m.sender_id == current_user.id,
        }
        for m in messages
    ]
    return make_page(data, total, skip, limit)


@router.patch("/{message_id}/read")
async def mark_read(
    message_id   : int,
    db           : AsyncSession = Depends(get_db),
    current_user : User         = Depends(get_current_user),
):
    """Mark a single message as read."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    msg    = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")
    if msg.receiver_id != current_user.id:
        raise HTTPException(403, "Cannot mark someone else's message as read")
    msg.is_read = True
    await db.commit()
    return {"id": message_id, "is_read": True}


@router.get("/unread-count/me")
async def unread_count(
    db           : AsyncSession = Depends(get_db),
    current_user : User         = Depends(get_current_user),
):
    """Total unread message count for current user."""
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.receiver_id == current_user.id, Message.is_read == False)
    )
    count = result.scalar_one() or 0
    return {"unread_count": count}
