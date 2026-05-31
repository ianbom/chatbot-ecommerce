from datetime import UTC, datetime
from decimal import Decimal
import base64
import json
from typing import Any, Protocol
from urllib import error, request

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import get_settings
from app.model.enums import OrderStatus, PaymentProvider, PaymentStatus
from app.model.order import Order
from app.model.payment import PaymentWebhookLog
from app.model.payment import Payment


class MidtransClient(Protocol):
    def create_payment_link(self, order_number: str, gross_amount: str, customer: dict[str, str]) -> dict[str, str]: ...


class MidtransClientError(RuntimeError):
    pass

class ConfiguredMidtransClient:
    def create_payment_link(self, order_number: str, gross_amount: str, customer: dict[str, str]) -> dict[str, str]:
        settings = get_settings()
        payload = {
            "transaction_details": {
                "order_id": order_number,
                "gross_amount": int(Decimal(gross_amount)),
            },
            "customer_details": {
                "first_name": customer.get("name") or "Customer",
                "phone": customer.get("phone") or "",
            },
        }
        response_payload = create_snap_transaction(
            payload,
            settings.midtrans_server_key.get_secret_value(),
            settings.midtrans_is_production,
        )
        token = response_payload.get("token")
        if not token:
            raise MidtransClientError("Midtrans Snap response missing token")
        return {
            "provider_order_id": order_number,
            "payment_url": response_payload.get("redirect_url") or snap_redirect_url(str(token), settings.midtrans_is_production),
            "snap_token": token,
            "raw_response": response_payload,
        }

def create_snap_transaction(payload: dict[str, Any], server_key: str, is_production: bool) -> dict[str, Any]:
    auth_token = base64.b64encode(f"{server_key}:".encode("utf-8")).decode("ascii")
    req = request.Request(
        snap_transaction_url(is_production),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Basic {auth_token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise MidtransClientError(f"Midtrans Snap error {exc.code}: {body}") from exc
    except Exception as exc:
        raise MidtransClientError(f"Midtrans Snap request failed: {exc}") from exc

def snap_transaction_url(is_production: bool) -> str:
    if is_production:
        return "https://app.midtrans.com/snap/v1/transactions"
    return "https://app.sandbox.midtrans.com/snap/v1/transactions"

def snap_redirect_url(token: str, is_production: bool) -> str:
    if is_production:
        return f"https://app.midtrans.com/snap/v2/vtweb/{token}"
    return f"https://app.sandbox.midtrans.com/snap/v2/vtweb/{token}"


def record_webhook(session: Session, payload: dict[str, Any]) -> None:
    payment = session.scalar(select(Payment).where(Payment.provider_order_id == payload.get("order_id")))
    if payment is not None:
        payment.transaction_id = payload.get("transaction_id")
        payment.payment_type = payload.get("payment_type")
        payment.status = map_payment_status(str(payload.get("transaction_status") or ""))
        payment.raw_response = payload
        if payment.status == PaymentStatus.paid.value:
            payment.paid_at = datetime.now(UTC)
            order = session.scalar(select(Order).where(Order.id == payment.order_id))
            if order is not None:
                order.status = OrderStatus.paid
                order.payment_status = PaymentStatus.paid
                order.paid_at = payment.paid_at

    log = PaymentWebhookLog(
        provider=PaymentProvider.midtrans,
        transaction_id=payload.get("transaction_id"),
        event_type=payload.get("transaction_status") or payload.get("event_type"),
        signature_valid=False,
        payload=payload,
        processed=True,
        processed_at=datetime.now(UTC),
    )
    session.add(log)
    session.commit()


def map_payment_status(transaction_status: str) -> str:
    if transaction_status in {"settlement", "capture"}:
        return PaymentStatus.paid.value
    if transaction_status in {"deny", "failure"}:
        return PaymentStatus.failed.value
    if transaction_status == "expire":
        return PaymentStatus.expired.value
    if transaction_status == "cancel":
        return PaymentStatus.cancelled.value
    return PaymentStatus.pending.value
