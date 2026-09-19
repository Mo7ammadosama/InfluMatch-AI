from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from ..core.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_histories"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    role       = Column(String(16), nullable=False)   # "user" | "assistant"
    content    = Column(Text, nullable=False)
    language   = Column(String(8), default="ar")
    created_at = Column(DateTime, default=datetime.utcnow)
