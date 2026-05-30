from decimal import Decimal

from pydantic import BaseModel, Field

from app.model.enums import ProductGender, ProductStatus


class ProductCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=220)
    description: str | None = None
    image_url: str | None = None
    price: Decimal = Field(gt=0)
    stock_qty: int = Field(default=0, ge=0)
    reserved_qty: int = Field(default=0, ge=0)
    color: str | None = Field(default=None, max_length=100)
    size: str | None = Field(default=None, max_length=50)
    gender: ProductGender = ProductGender.unisex
    material: str | None = Field(default=None, max_length=150)
    weight_gram: int = Field(default=0, ge=0)
    length_cm: Decimal | None = Field(default=None, ge=0)
    width_cm: Decimal | None = Field(default=None, ge=0)
    height_cm: Decimal | None = Field(default=None, ge=0)
    status: ProductStatus = ProductStatus.draft
    is_featured: bool = False
    created_by: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    price: Decimal
    stock_qty: int
    reserved_qty: int
    color: str | None
    size: str | None
    gender: ProductGender
    material: str | None
    weight_gram: int
    length_cm: Decimal | None
    width_cm: Decimal | None
    height_cm: Decimal | None
    status: ProductStatus
    is_featured: bool
    created_by: int | None
    embedding_dimensions: int

    model_config = {"from_attributes": True}
