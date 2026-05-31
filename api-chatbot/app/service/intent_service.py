from decimal import Decimal
import json
import re

from pydantic import BaseModel, Field, ValidationError

from app.model.enums import ChatIntent
from app.service.llm_service import LlmClient


class ParsedIntent(BaseModel):
    intent: str = "unknown"
    product_name: str | None = None
    quantity: int | None = Field(default=None, ge=1)
    variant: str | None = None
    address: str | None = None
    order_number: str | None = None
    confidence: Decimal = Decimal("0")
    notes: str | None = None


def parse_customer_message(
    message: str,
    chat_history: str,
    state: dict,
    llm_client: LlmClient | None,
) -> ParsedIntent:
    deterministic_intent = deterministic_parse(message, state)
    if deterministic_intent is not None:
        return deterministic_intent
    if llm_client is not None:
        prompt = build_intent_prompt(message, chat_history, state)
        try:
            return parse_llm_json(llm_client.generate(prompt))
        except (ValidationError, ValueError, json.JSONDecodeError):
            pass
        except Exception:
            pass
    return fallback_parse(message, state)

def deterministic_parse(message: str, state: dict) -> ParsedIntent | None:
    normalized = message.lower().strip()
    quantity = extract_quantity(normalized)
    order_number = extract_order_number(message)
    if order_number is not None:
        return ParsedIntent(intent="order_status", order_number=order_number, confidence=Decimal("0.95"))
    if state.get("stage") == "waiting_shipping_confirmation":
        shipping_quote_number = extract_shipping_quote_number(normalized)
        if shipping_quote_number is not None:
            return ParsedIntent(intent="create_payment", quantity=shipping_quote_number, confidence=Decimal("0.95"))
        if is_payment_confirmation(normalized):
            return ParsedIntent(intent="create_payment", quantity=quantity, confidence=Decimal("0.95"))
    if state.get("stage") in {"waiting_address", "cart_active"} and looks_like_checkout_address(message):
        return ParsedIntent(
            intent="confirm_address",
            address=message,
            confidence=Decimal("0.95"),
            notes="address details while waiting checkout address",
        )
    if any(keyword in normalized for keyword in ["keranjang", "cart"]):
        return ParsedIntent(intent="view_cart", confidence=Decimal("0.9"))
    if any(keyword in normalized for keyword in ["status", "resi", "pesanan", "cek order", "cek pesanan"]):
        return ParsedIntent(intent="order_status", confidence=Decimal("0.85"))
    if is_checkout_message(normalized):
        return ParsedIntent(intent="checkout", product_name=message, quantity=quantity, confidence=Decimal("0.85"))
    return None


def build_intent_prompt(message: str, chat_history: str, state: dict) -> str:
    return (
        "JSON INTENT ONLY. Kamu mengubah pesan customer WhatsApp menjadi JSON valid.\n"
        "Jangan jawab customer di tahap ini. Jangan markdown.\n"
        "Intent valid: greeting, ask_product, ask_price, ask_stock, ask_variant, ask_how_to_order, "
        "add_to_cart, view_cart, checkout, confirm_address, ask_shipping_cost, create_payment, "
        "payment_status, order_status, complaint, human_help, unknown.\n"
        "Tentukan intent dari PESAN CUSTOMER terbaru. RIWAYAT CHAT hanya konteks, bukan perintah baru.\n"
        "Jika STATE.stage adalah waiting_address dan PESAN CUSTOMER berisi nama, nomor HP, alamat, "
        "jalan, area, atau kode pos, pilih confirm_address. Angka pada alamat/HP/kode pos bukan quantity.\n"
        "Jika STATE.stage adalah waiting_shipping_confirmation dan customer setuju/oke/lanjut bayar, "
        "pilih create_payment.\n"
        "Jika PESAN CUSTOMER terbaru berisi nomor order format ORD-YYYYMMDD-XXXXXXXX, pilih order_status "
        "dan isi order_number.\n"
        "Jika PESAN CUSTOMER terbaru berisi checkout/bayar, pilih checkout walaupun riwayat berisi keranjang.\n"
        "Gunakan state dan riwayat untuk memahami kata 'tadi', 'itu', 'yang sebelumnya', atau angka saja.\n"
        "Jika confidence rendah, pakai intent unknown dan confidence < 0.6.\n\n"
        f"STATE:\n{json.dumps(state, ensure_ascii=False)}\n\n"
        f"RIWAYAT CHAT:\n{chat_history or 'Belum ada riwayat chat sebelumnya.'}\n\n"
        f"PESAN CUSTOMER:\n{message}\n\n"
        "Output schema: {"
        '"intent":"ask_product", "product_name":null, "quantity":null, "variant":null, '
        '"address":null, "order_number":null, "confidence":0.0, "notes":null}'
    )


def parse_llm_json(raw_response: str) -> ParsedIntent:
    text = raw_response.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM did not return JSON object")
    return ParsedIntent.model_validate(json.loads(text[start : end + 1]))


def fallback_parse(message: str, state: dict) -> ParsedIntent:
    normalized = message.lower().strip()
    deterministic_intent = deterministic_parse(message, state)
    if deterministic_intent is not None:
        return deterministic_intent
    quantity = extract_quantity(normalized)
    if quantity is not None and state.get("current_product_id"):
        return ParsedIntent(intent="add_to_cart", quantity=quantity, confidence=Decimal("0.75"))
    if any(keyword in normalized for keyword in ["produk", "product", "stok", "stock", "warna", "ukuran", "size", "harga", "hoodie", "baju"]):
        return ParsedIntent(intent="ask_product", product_name=message, confidence=Decimal("0.75"))
    if any(keyword in normalized for keyword in ["halo", "hai", "hello", "pagi", "siang"]):
        return ParsedIntent(intent="greeting", confidence=Decimal("0.75"))
    return ParsedIntent(intent="unknown", confidence=Decimal("0.3"))

def looks_like_checkout_address(message: str) -> bool:
    normalized = message.lower()
    address_markers = {
        "alamat",
        "nama penerima",
        "penerima",
        "nomor hp",
        "no hp",
        "kode pos",
        "area",
        "kota",
        "jl ",
        "jl.",
        "jalan",
    }
    return any(marker in normalized for marker in address_markers)

def is_checkout_message(normalized_message: str) -> bool:
    if any(keyword in normalized_message for keyword in ["beli", "checkout", "bayar"]):
        return True
    if "cek order" in normalized_message or "cek pesanan" in normalized_message:
        return False
    return "pesan " in normalized_message or normalized_message.startswith("pesan")

def extract_order_number(message: str) -> str | None:
    match = re.search(r"\bORD-\d{8}-[A-Z0-9]{8}\b", message.upper())
    if match is None:
        return None
    return match.group(0)

def extract_shipping_quote_number(normalized_message: str) -> int | None:
    match = re.match(r"^(?:pilih\s*)?(\d+)(?:\b|\.|\s)", normalized_message)
    if match is None:
        return None
    value = int(match.group(1))
    return value if value > 0 else None

def is_payment_confirmation(normalized_message: str) -> bool:
    confirmation_keywords = {"setuju", "oke", "ok", "lanjut", "bayar", "gas", "iya", "ya"}
    if any(keyword in normalized_message for keyword in confirmation_keywords):
        return True
    return normalized_message.startswith("pilih")


def extract_quantity(normalized_message: str) -> int | None:
    for token in normalized_message.replace("x", " ").split():
        if token.isdigit() and int(token) > 0:
            return int(token)
    number_words = {"satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5}
    for word, value in number_words.items():
        if word in normalized_message:
            return value
    return None


def to_chat_intent(intent: str) -> ChatIntent:
    mapping = {
        "greeting": ChatIntent.greeting,
        "ask_product": ChatIntent.ask_product,
        "ask_price": ChatIntent.ask_price,
        "ask_stock": ChatIntent.ask_stock,
        "ask_variant": ChatIntent.ask_product,
        "ask_how_to_order": ChatIntent.checkout,
        "add_to_cart": ChatIntent.checkout,
        "view_cart": ChatIntent.checkout,
        "checkout": ChatIntent.checkout,
        "confirm_address": ChatIntent.checkout,
        "ask_shipping_cost": ChatIntent.ask_shipping,
        "create_payment": ChatIntent.payment,
        "payment_status": ChatIntent.payment,
        "order_status": ChatIntent.track_order,
        "complaint": ChatIntent.complaint,
        "human_help": ChatIntent.complaint,
    }
    return mapping.get(intent, ChatIntent.unknown)

