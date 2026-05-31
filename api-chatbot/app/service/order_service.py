from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.model.customer import CustomerAddress
from app.model.enums import OrderStatus, PaymentStatus, ProductStatus, ShippingStatus
from app.model.order import Order, OrderItem
from app.model.payment import Payment
from app.model.product import Product
from app.schemas.chatbot_schema import CheckoutRequest, CheckoutResponse, OrderStatusResponse
from app.service import chat_service
from app.service.midtrans_service import MidtransClient


class CheckoutError(ValueError):
    pass


def create_checkout(
    session: Session,
    payload: CheckoutRequest,
    midtrans_client: MidtransClient,
) -> CheckoutResponse:
    customer = chat_service.get_or_create_whatsapp_customer(session, payload.phone)
    chat_session = chat_service.get_or_create_open_session(session, customer)
    address = CustomerAddress(
        customer_id=customer.id,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        province=payload.province,
        city=payload.city,
        district=payload.district,
        subdistrict=payload.subdistrict,
        postal_code=payload.postal_code,
        address_line=payload.address_line,
        biteship_area_id=payload.biteship_area_id,
        is_default=True,
    )
    session.add(address)
    session.flush()

    products_by_slug = _load_products_by_slug(session, [item.slug for item in payload.items])
    subtotal = Decimal("0")
    order = Order(
        order_number=_generate_order_number(),
        customer_id=customer.id,
        chat_session_id=chat_session.id,
        customer_address_id=address.id,
        status=OrderStatus.waiting_payment,
        payment_status=PaymentStatus.pending,
        shipping_status=ShippingStatus.not_created,
        shipping_cost=payload.shipping_cost,
        notes=payload.notes,
        expired_at=datetime.now(UTC) + timedelta(minutes=get_settings().order_payment_expire_minutes),
    )
    session.add(order)
    session.flush()

    for item in payload.items:
        product = products_by_slug.get(item.slug)
        if product is None:
            raise CheckoutError(f"Product not found: {item.slug}")
        available_stock = product.stock_qty - product.reserved_qty
        if available_stock < item.quantity:
            raise CheckoutError(f"Stock not enough for: {product.name}")
        line_subtotal = product.price * item.quantity
        subtotal += line_subtotal
        product.reserved_qty += item.quantity
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                product_snapshot={"slug": product.slug, "image_url": product.image_url},
                quantity=item.quantity,
                unit_price=product.price,
                subtotal=line_subtotal,
                weight_total_gram=product.weight_gram * item.quantity,
            )
        )

    order.subtotal = subtotal
    order.grand_total = subtotal + payload.shipping_cost
    payment_payload = midtrans_client.create_payment_link(
        order.order_number,
        str(order.grand_total),
        {"phone": payload.phone, "name": payload.recipient_name},
    )
    payment = Payment(
        order_id=order.id,
        provider_order_id=payment_payload["provider_order_id"],
        snap_token=payment_payload.get("snap_token"),
        payment_url=payment_payload["payment_url"],
        status=PaymentStatus.pending.value,
        gross_amount=order.grand_total,
        expired_at=order.expired_at,
        raw_response=payment_payload,
    )
    session.add(payment)
    session.commit()
    session.refresh(order)
    return CheckoutResponse(
        order_number=order.order_number,
        payment_url=payment.payment_url or "",
        subtotal=order.subtotal,
        shipping_cost=order.shipping_cost,
        grand_total=order.grand_total,
        order_status=order.status.value,
        payment_status=order.payment_status.value,
    )


def get_order_status(session: Session, order_number: str) -> OrderStatusResponse | None:
    order = session.scalar(select(Order).where(Order.order_number == order_number))
    if order is None:
        return None
    payment = session.scalar(select(Payment).where(Payment.order_id == order.id).order_by(Payment.id.desc()))
    return OrderStatusResponse(
        order_number=order.order_number,
        order_status=order.status.value,
        payment_status=order.payment_status.value,
        shipping_status=order.shipping_status.value,
        grand_total=order.grand_total,
        payment_url=None if payment is None else payment.payment_url,
    )


def _load_products_by_slug(session: Session, slugs: list[str]) -> dict[str, Product]:
    products = session.scalars(
        select(Product).where(Product.slug.in_(slugs)).where(Product.status == ProductStatus.active)
    )
    return {product.slug: product for product in products}


def _generate_order_number() -> str:
    return f"ORD-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:8].upper()}"
