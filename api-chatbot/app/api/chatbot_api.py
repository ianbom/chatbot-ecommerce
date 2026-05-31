from typing import Annotated, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controller import chatbot_controller
from app.db.session import get_db
from app.schemas.chatbot_schema import (
    ChatbotMessageRequest,
    ChatbotMessageResponse,
    CheckoutRequest,
    CheckoutResponse,
    MidtransWebhookResponse,
    OrderStatusResponse,
    WahaWebhookRequest,
    WhatsAppSendMessageRequest,
    WhatsAppSendMessageResponse,
)
from app.service.llm_service import LlmClient, OllamaLlmClient
from app.service.midtrans_service import ConfiguredMidtransClient, MidtransClient
from app.service.order_service import CheckoutError
from app.service import product_tool_service
from app.service.shipping_service import BiteshipShippingClient, ShippingClient
from app.service.waha_service import HttpWahaClient, WahaClient, extract_phone

router = APIRouter(tags=["chatbot"])
logger = logging.getLogger(__name__)
SessionDep = Annotated[Session, Depends(get_db)]


def get_llm_client() -> LlmClient:
    return OllamaLlmClient()


def get_waha_client() -> WahaClient:
    return HttpWahaClient()


def get_midtrans_client() -> MidtransClient:
    return ConfiguredMidtransClient()

def get_shipping_client() -> ShippingClient:
    return BiteshipShippingClient()


LlmDep = Annotated[LlmClient, Depends(get_llm_client)]
WahaDep = Annotated[WahaClient, Depends(get_waha_client)]
MidtransDep = Annotated[MidtransClient, Depends(get_midtrans_client)]
ShippingDep = Annotated[ShippingClient, Depends(get_shipping_client)]


@router.post("/api/chatbot/message", response_model=ChatbotMessageResponse)
def chatbot_message(
    payload: ChatbotMessageRequest,
    session: SessionDep,
    llm_client: LlmDep,
    midtrans_client: MidtransDep,
    shipping_client: ShippingDep,
) -> ChatbotMessageResponse:
    return chatbot_controller.reply_to_message(
        payload_phone=payload.phone,
        payload_message=payload.message,
        session=session,
        llm_client=llm_client,
        midtrans_client=midtrans_client,
        shipping_client=shipping_client,
    )


@router.post("/api/webhooks/waha/messages", response_model=ChatbotMessageResponse)
def waha_messages(
    payload: WahaWebhookRequest,
    session: SessionDep,
    waha_client: WahaDep,
    llm_client: LlmDep,
    midtrans_client: MidtransDep,
    shipping_client: ShippingDep,
) -> ChatbotMessageResponse:
    if payload.payload.from_me or not payload.payload.from_ or not payload.payload.body:
        return ChatbotMessageResponse(phone="", reply="", intent="unknown", duplicate=True)

    phone = extract_phone(payload.payload.from_)
    response = chatbot_controller.reply_to_message(
        payload_phone=phone,
        payload_message=payload.payload.body,
        session=session,
        llm_client=llm_client,
        midtrans_client=midtrans_client,
        shipping_client=shipping_client,
        external_message_id=payload.payload.id,
    )
    if not response.duplicate:
        chat_id = payload.payload.from_
        waha_client.send_text(chat_id, response.reply)
        if response.intent in {"ask_product", "ask_price", "ask_stock", "ask_color", "ask_size"}:
            products = product_tool_service.find_active_products_for_message(session, payload.payload.body)
            for image_url, caption in product_tool_service.product_image_messages(products):
                try:
                    waha_client.send_image(chat_id, image_url, caption)
                except Exception as exc:
                    logger.warning(
                        "Failed to send WhatsApp product image",
                        extra={"chat_id": chat_id, "image_url": image_url, "error": str(exc)},
                    )
    return response


@router.post("/api/whatsapp/send-message", response_model=WhatsAppSendMessageResponse)
def send_whatsapp_message(payload: WhatsAppSendMessageRequest, waha_client: WahaDep) -> WhatsAppSendMessageResponse:
    waha_client.send_text(payload.phone, payload.message)
    return WhatsAppSendMessageResponse(status="sent")


@router.post("/api/chatbot/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def chatbot_checkout(
    payload: CheckoutRequest,
    session: SessionDep,
    midtrans_client: MidtransDep,
) -> CheckoutResponse:
    try:
        return chatbot_controller.checkout(payload, session, midtrans_client)
    except CheckoutError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/api/chatbot/orders/{order_number}", response_model=OrderStatusResponse)
def chatbot_order_status(order_number: str, session: SessionDep) -> OrderStatusResponse:
    order_status = chatbot_controller.order_status(order_number, session)
    if order_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order_status


@router.post(
    "/api/webhooks/midtrans",
    response_model=MidtransWebhookResponse,
    status_code=status.HTTP_200_OK,
)
def midtrans_webhook(payload: dict[str, Any], session: SessionDep) -> MidtransWebhookResponse:
    chatbot_controller.process_midtrans_webhook(payload, session)
    return MidtransWebhookResponse(processed=True)
