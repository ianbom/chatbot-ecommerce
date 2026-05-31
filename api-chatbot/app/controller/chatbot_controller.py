from typing import Any

from sqlalchemy.orm import Session

from app.schemas.chatbot_schema import ChatbotMessageResponse
from app.schemas.chatbot_schema import CheckoutRequest, CheckoutResponse, OrderStatusResponse
from app.service import chatbot_service, midtrans_service, order_service
from app.service.llm_service import LlmClient
from app.service.midtrans_service import MidtransClient
from app.service.shipping_service import ShippingClient


def reply_to_message(
    payload_phone: str,
    payload_message: str,
    session: Session,
    llm_client: LlmClient | None = None,
    midtrans_client: MidtransClient | None = None,
    shipping_client: ShippingClient | None = None,
    external_message_id: str | None = None,
) -> ChatbotMessageResponse:
    reply, intent, duplicate = chatbot_service.handle_incoming_message(
        session=session,
        phone=payload_phone,
        message=payload_message,
        llm_client=llm_client,
        midtrans_client=midtrans_client,
        shipping_client=shipping_client,
        external_message_id=external_message_id,
    )
    return ChatbotMessageResponse(
        phone=payload_phone,
        reply=reply,
        intent=intent,
        duplicate=duplicate,
    )


def process_midtrans_webhook(payload: dict[str, Any], session: Session) -> None:
    midtrans_service.record_webhook(session, payload)


def checkout(payload: CheckoutRequest, session: Session, midtrans_client: MidtransClient) -> CheckoutResponse:
    return order_service.create_checkout(session, payload, midtrans_client)


def order_status(order_number: str, session: Session) -> OrderStatusResponse | None:
    return order_service.get_order_status(session, order_number)
