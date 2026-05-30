from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.model.enums import CartStatus
from app.model.base import Base, TimestampMixin
from app.model.types import pg_enum


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"
    __table_args__ = (
        Index("ix_carts_customer_id", "customer_id"),
        Index("ix_carts_chat_session_id", "chat_session_id"),
        Index("ix_carts_status", "status"),
        Index("ix_carts_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    chat_session_id: Mapped[int | None] = mapped_column(ForeignKey("chat_sessions.id"))
    status: Mapped[CartStatus] = mapped_column(
        pg_enum(CartStatus, "cart_status"), server_default=CartStatus.active.value, nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        Index("ix_cart_items_cart_id", "cart_id"),
        Index("ix_cart_items_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)


