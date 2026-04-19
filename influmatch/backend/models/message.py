from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id          = Column(Integer, primary_key=True, index=True)
    booking_id  = Column(Integer, ForeignKey("bookings.id"), nullable=False, index=True)
    sender_id   = Column(Integer, ForeignKey("users.id"),   nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"),   nullable=False)
    content     = Column(Text,    nullable=False)
    is_read     = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    sender   = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
