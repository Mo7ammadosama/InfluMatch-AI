"""
InfluMatch.jo — Wallet & Points Loyalty Engine Model
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    ESCROW_LOCK = "escrow_lock"
    ESCROW_RELEASE = "escrow_release"
    ESCROW_REFUND = "escrow_refund"
    POINTS_EARNED = "points_earned"
    POINTS_REDEEMED = "points_redeemed"
    PLATFORM_FEE = "platform_fee"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Balances (JOD)
    available_balance_jod: Mapped[float] = mapped_column(Float, default=0.0)
    locked_balance_jod: Mapped[float] = mapped_column(Float, default=0.0)

    # Loyalty Points
    points_balance: Mapped[int] = mapped_column(Integer, default=0)
    total_points_earned: Mapped[int] = mapped_column(Integer, default=0)
    points_to_jod_rate: Mapped[float] = mapped_column(Float, default=0.01)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wallet")
    transactions: Mapped[list["WalletTransaction"]] = relationship("WalletTransaction", back_populates="wallet")

    @property
    def total_balance_jod(self) -> float:
        return self.available_balance_jod + self.locked_balance_jod

    def __repr__(self) -> str:
        return f"<Wallet user={self.user_id} | {self.available_balance_jod} JOD available>"


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    wallet_id: Mapped[str] = mapped_column(String(36), ForeignKey("wallets.id"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)

    amount_jod: Mapped[float] = mapped_column(Float, nullable=False)
    points_delta: Mapped[int] = mapped_column(Integer, default=0)
    balance_after_jod: Mapped[float] = mapped_column(Float, nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<WalletTx {self.transaction_type} | {self.amount_jod} JOD>"
