from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import OrderStatus, PaymentStatus, ShippingStatus
from app.db.model_base import Base, SoftDeleteMixin, TimestampMixin
from app.db.types import pg_enum


class Order(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_order_number", "order_number"),
        Index("ix_orders_customer_id", "customer_id"),
        Index("ix_orders_chat_session_id", "chat_session_id"),
        Index("ix_orders_customer_address_id", "customer_address_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_payment_status", "payment_status"),
        Index("ix_orders_shipping_status", "shipping_status"),
        Index("ix_orders_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    chat_session_id: Mapped[int | None] = mapped_column(ForeignKey("chat_sessions.id"))
    customer_address_id: Mapped[int | None] = mapped_column(ForeignKey("customer_addresses.id"))
    status: Mapped[OrderStatus] = mapped_column(
        pg_enum(OrderStatus, "order_status"), server_default=OrderStatus.draft.value, nullable=False
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        pg_enum(PaymentStatus, "payment_status"),
        server_default=PaymentStatus.unpaid.value,
        nullable=False,
    )
    shipping_status: Mapped[ShippingStatus] = mapped_column(
        pg_enum(ShippingStatus, "shipping_status"),
        server_default=ShippingStatus.not_created.value,
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    service_fee: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), server_default="IDR", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    product_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    weight_total_gram: Mapped[int] = mapped_column(server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

