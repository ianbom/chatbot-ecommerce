from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.model.enums import ShippingProvider
from app.model.base import Base, TimestampMixin
from app.model.types import pg_enum


class ShippingQuote(Base):
    __tablename__ = "shipping_quotes"
    __table_args__ = (
        Index("ix_shipping_quotes_order_id", "order_id"),
        Index("ix_shipping_quotes_courier_code", "courier_code"),
        Index("ix_shipping_quotes_service_code", "service_code"),
        Index("ix_shipping_quotes_is_selected", "is_selected"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    courier_code: Mapped[str] = mapped_column(String(50), nullable=False)
    courier_name: Mapped[str] = mapped_column(String(100), nullable=False)
    service_code: Mapped[str | None] = mapped_column(String(50))
    service_name: Mapped[str | None] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estimated_delivery: Mapped[str | None] = mapped_column(String(100))
    is_selected: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    raw_response: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Shipment(TimestampMixin, Base):
    __tablename__ = "shipments"
    __table_args__ = (
        Index("ix_shipments_order_id", "order_id"),
        Index("ix_shipments_biteship_order_id", "biteship_order_id"),
        Index("ix_shipments_tracking_id", "tracking_id"),
        Index("ix_shipments_waybill_id", "waybill_id"),
        Index("ix_shipments_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    provider: Mapped[ShippingProvider] = mapped_column(
        pg_enum(ShippingProvider, "shipping_provider"),
        server_default=ShippingProvider.biteship.value,
        nullable=False,
    )
    biteship_order_id: Mapped[str | None] = mapped_column(String(150))
    courier_company: Mapped[str | None] = mapped_column(String(100))
    courier_type: Mapped[str | None] = mapped_column(String(100))
    courier_service_name: Mapped[str | None] = mapped_column(String(100))
    tracking_id: Mapped[str | None] = mapped_column(String(150))
    waybill_id: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(50), server_default="pending", nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), server_default="0", nullable=False)
    address_snapshot: Mapped[dict | None] = mapped_column(JSONB)
    raw_response: Mapped[dict | None] = mapped_column(JSONB)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ShipmentTrackingLog(Base):
    __tablename__ = "shipment_tracking_logs"
    __table_args__ = (
        Index("ix_shipment_tracking_logs_shipment_id", "shipment_id"),
        Index("ix_shipment_tracking_logs_status", "status"),
        Index("ix_shipment_tracking_logs_checkpoint_time", "checkpoint_time"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    shipment_id: Mapped[int] = mapped_column(ForeignKey("shipments.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(200))
    checkpoint_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)



