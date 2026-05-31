from typing import Any

from pydantic import BaseModel, Field

class ShippingRateItem(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    value: int = Field(ge=1)
    length: int | None = Field(default=None, ge=1)
    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)
    weight: int = Field(ge=1)
    quantity: int = Field(ge=1)

class ShippingRateCheckRequest(BaseModel):
    origin_postal_code: int = Field(ge=10000, le=99999)
    destination_postal_code: int = Field(ge=10000, le=99999)
    couriers: str = Field(min_length=1)
    items: list[ShippingRateItem] = Field(min_length=1)

class ShippingRateCheckResponse(BaseModel):
    result: dict[str, Any]
