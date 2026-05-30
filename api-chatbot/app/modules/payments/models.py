from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import PaymentProvider
from app.db.model_base import Base, TimestampMixin
from app.db.types import pg_enum


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_order_id", "order_id"),
        Index("ix_payments_provider_order_id", "provider_order_id"),
        Index("ix_payments_transaction_id", "transaction_id"),
        Index("ix_payments_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    provider: Mapped[PaymentProvider] = mapped_column(
        pg_enum(PaymentProvider, "payment_provider"),
        server_default=PaymentProvider.midtrans.value,
        nullable=False,
    )
    provider_order_id: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(150))
    snap_token: Mapped[str | None] = mapped_column(Text)
    payment_url: Mapped[str | None] = mapped_column(Text)
    payment_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), server_default="pending", nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fraud_status: Mapped[str | None] = mapped_column(String(50))
    raw_response: Mapped[dict | None] = mapped_column(JSONB)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PaymentWebhookLog(Base):
    __tablename__ = "payment_webhook_logs"
    __table_args__ = (
        Index("ix_payment_webhook_logs_provider", "provider"),
        Index("ix_payment_webhook_logs_order_id", "order_id"),
        Index("ix_payment_webhook_logs_transaction_id", "transaction_id"),
        Index("ix_payment_webhook_logs_event_type", "event_type"),
        Index("ix_payment_webhook_logs_processed", "processed"),
        Index("ix_payment_webhook_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[PaymentProvider] = mapped_column(
        pg_enum(PaymentProvider, "payment_provider"),
        server_default=PaymentProvider.midtrans.value,
        nullable=False,
    )
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    transaction_id: Mapped[str | None] = mapped_column(String(150))
    event_type: Mapped[str | None] = mapped_column(String(100))
    signature_valid: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

