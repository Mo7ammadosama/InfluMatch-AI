"""
WaslAI.jo — Messages Router
In-deal messages and unread-count badge for the navbar.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.middleware.auth_middleware import get_current_user

router = APIRouter()


class MessageCreate(BaseModel):
    deal_id: str
    content: str


def _msg(m: Message, sender: User | None = None) -> dict:
    name = None
    if sender:
        name = sender.full_name_en or sender.username or sender.email
    return {
        "id": m.id,
        "booking_id": m.deal_id,
        "sender_id": m.sender_id,
        "sender_name": name,
        "content": m.content,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "read_at": m.read_at.isoformat() if m.read_at else None,
    }


@router.get("/unread-count/me")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(sql_func.count(Message.id)).where(
            Message.sender_id != current_user.id,
            Message.read_at.is_(None),
        )
    )
    count = result.scalar_one_or_none() or 0
    return {"unread_count": count, "count": count}


@router.get("/booking/{booking_id}")
async def get_booking_messages(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Message)
        .where(Message.deal_id == booking_id)
        .order_by(Message.created_at)
    )
    msgs = result.scalars().all()
    sender_ids = list({m.sender_id for m in msgs})
    users_result = await db.execute(select(User).where(User.id.in_(sender_ids)))
    users_map = {u.id: u for u in users_result.scalars().all()}
    return [_msg(m, users_map.get(m.sender_id)) for m in msgs]


@router.post("/")
@router.post("")
async def send_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = Message(deal_id=payload.deal_id, sender_id=current_user.id, content=payload.content)
    db.add(msg)
    await db.flush()
    return _msg(msg, current_user)
