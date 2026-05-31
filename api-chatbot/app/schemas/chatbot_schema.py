from decimal import Decimal

from pydantic import BaseModel, Field


class ChatbotMessageRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=30)
    message: str = Field(min_length=1)


class ChatbotMessageResponse(BaseModel):
    phone: str
    reply: str
    intent: str
    duplicate: bool = False


class WahaIncomingPayload(BaseModel):
    id: str | None = None
    from_: str | None = Field(default=None, alias="from")
    body: str | None = None
    from_me: bool = Field(default=False, alias="fromMe")


class WahaWebhookRequest(BaseModel):
    event: str
    payload: WahaIncomingPayload


class WhatsAppSendMessageRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=30)
    message: str = Field(min_length=1)


class WhatsAppSendMessageResponse(BaseModel):
    status: str


class MidtransWebhookResponse(BaseModel):
    processed: bool


class CheckoutItemRequest(BaseModel):
    slug: str = Field(min_length=1)
    quantity: int = Field(ge=1)


class CheckoutRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=30)
    recipient_name: str = Field(min_length=1, max_length=150)
    recipient_phone: str = Field(min_length=6, max_length=30)
    address_line: str = Field(min_length=5)
    province: str | None = None
    city: str | None = None
    district: str | None = None
    subdistrict: str | None = None
    postal_code: str | None = None
    biteship_area_id: str | None = None
    shipping_cost: Decimal = Decimal("0")
    notes: str | None = None
    items: list[CheckoutItemRequest] = Field(min_length=1)


class CheckoutResponse(BaseModel):
    order_number: str
    payment_url: str
    subtotal: Decimal
    shipping_cost: Decimal
    grand_total: Decimal
    order_status: str
    payment_status: str


class OrderStatusResponse(BaseModel):
    order_number: str
    order_status: str
    payment_status: str
    shipping_status: str
    grand_total: Decimal
    payment_url: str | None = None
