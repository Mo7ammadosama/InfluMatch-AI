"""
WaslAI.jo — Escrow Transaction Model
State-machine controlled fund management
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EscrowState(str, enum.Enum):
    PENDING = "pending"
    FUNDED = "funded"
    LOCKED = "locked"
    RELEASED = "released"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    RESOLVED = "resolved"


class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    influencer_id: Mapped[str] = mapped_column(String(36), ForeignKey("influencers.id"), nullable=False)

    # Amounts (JOD)
    gross_amount_jod: Mapped[float] = mapped_column(Float, nullable=False)
    platform_fee_jod: Mapped[float] = mapped_column(Float, nullable=False)
    vat_on_fee_jod: Mapped[float] = mapped_column(Float, nullable=False)
    net_to_influencer_jod: Mapped[float] = mapped_column(Float, nullable=False)

    # State Machine
    state: Mapped[EscrowState] = mapped_column(Enum(EscrowState), default=EscrowState.PENDING)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_transfer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Audit
    state_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    funded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    deal: Mapped["Deal"] = relationship("Deal", back_populates="escrow", foreign_keys="Deal.escrow_id")

    def __repr__(self) -> str:
        return f"<Escrow {self.id[:8]} | {self.state} | {self.gross_amount_jod} JOD>"
