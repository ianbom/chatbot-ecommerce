from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import CustomerSource
from app.db.model_base import Base, SoftDeleteMixin, TimestampMixin
from app.db.types import pg_enum


class Customer(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customers_phone", "phone"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_source", "source"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(191))
    phone: Mapped[str | None] = mapped_column(String(30))
    source: Mapped[CustomerSource] = mapped_column(
        pg_enum(CustomerSource, "customer_source"),
        server_default=CustomerSource.chatbot_web.value,
        nullable=False,
    )
    first_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_orders: Mapped[int] = mapped_column(server_default="0", nullable=False)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)


class CustomerAddress(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "customer_addresses"
    __table_args__ = (
        Index("ix_customer_addresses_customer_id", "customer_id"),
        Index("ix_customer_addresses_biteship_area_id", "biteship_area_id"),
        Index("ix_customer_addresses_is_default", "is_default"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(100))
    recipient_name: Mapped[str] = mapped_column(String(150), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    province: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    district: Mapped[str | None] = mapped_column(String(100))
    subdistrict: Mapped[str | None] = mapped_column(String(100))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    address_line: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    biteship_area_id: Mapped[str | None] = mapped_column(String(100))
    is_default: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
