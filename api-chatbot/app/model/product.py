from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.model.enums import ProductGender, ProductStatus
from app.model.base import Base, SoftDeleteMixin, TimestampMixin
from app.model.types import pg_enum


class Product(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_slug", "slug"),
        Index("ix_products_status", "status"),
        Index("ix_products_is_featured", "is_featured"),
        Index("ix_products_stock_qty", "stock_qty"),
        Index("ix_products_created_by", "created_by"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024))
    image_url: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    stock_qty: Mapped[int] = mapped_column(server_default="0", nullable=False)
    reserved_qty: Mapped[int] = mapped_column(server_default="0", nullable=False)
    color: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[ProductGender] = mapped_column(
        pg_enum(ProductGender, "product_gender"),
        server_default=ProductGender.unisex.value,
        nullable=False,
    )
    material: Mapped[str | None] = mapped_column(String(150))
    weight_gram: Mapped[int] = mapped_column(server_default="0", nullable=False)
    length_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    status: Mapped[ProductStatus] = mapped_column(
        pg_enum(ProductStatus, "product_status"),
        server_default=ProductStatus.draft.value,
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))


