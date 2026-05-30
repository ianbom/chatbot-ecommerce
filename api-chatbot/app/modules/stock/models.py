from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import StockMovementType
from app.db.model_base import Base
from app.db.types import pg_enum


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        Index("ix_stock_movements_product_id", "product_id"),
        Index("ix_stock_movements_movement_type", "movement_type"),
        Index("ix_stock_movements_reference_type", "reference_type"),
        Index("ix_stock_movements_reference_id", "reference_id"),
        Index("ix_stock_movements_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement_type: Mapped[StockMovementType] = mapped_column(
        pg_enum(StockMovementType, "stock_movement_type"), nullable=False
    )
    quantity_change: Mapped[int] = mapped_column(nullable=False)
    stock_before: Mapped[int] = mapped_column(nullable=False)
    stock_after: Mapped[int] = mapped_column(nullable=False)
    reserved_before: Mapped[int] = mapped_column(server_default="0", nullable=False)
    reserved_after: Mapped[int] = mapped_column(server_default="0", nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50))
    reference_id: Mapped[int | None] = mapped_column(BigInteger)
    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
