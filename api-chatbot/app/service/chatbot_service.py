from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import get_settings
from app.model.enums import ChatIntent, ChatSenderType
from app.model.order import Order
from app.model.shipping import ShippingQuote
from app.schemas.chatbot_schema import CheckoutItemRequest, CheckoutRequest
from app.service import cart_service, chat_service, intent_service, order_service, product_tool_service
from app.service.intent_service import ParsedIntent
from app.service.llm_service import LlmClient
from app.service.midtrans_service import MidtransClient
from app.service.shipping_service import ShippingClient, ShippingRateUnavailable


PRODUCT_KEYWORDS = {
    "produk",
    "product",
    "stok",
    "stock",
    "warna",
    "ukuran",
    "size",
    "harga",
    "hoodie",
    "baju",
}
CHECKOUT_KEYWORDS = {"beli", "checkout", "pesan", "order", "bayar"}
ORDER_KEYWORDS = {"status", "resi", "order id", "order number", "pesanan"}


def handle_incoming_message(
    session: Session,
    phone: str,
    message: str,
    llm_client: LlmClient | None = None,
    midtrans_client: MidtransClient | None = None,
    shipping_client: ShippingClient | None = None,
    external_message_id: str | None = None,
) -> tuple[str, str, bool]:
    if chat_service.has_external_message(session, external_message_id):
        return "", "unknown", True

    customer = chat_service.get_or_create_whatsapp_customer(session, phone)
    chat_session = chat_service.get_or_create_open_session(session, customer)
    chat_history = chat_service.get_recent_chat_history(session, chat_session)
    state = chat_service.get_session_state(chat_session)
    parsed = intent_service.parse_customer_message(message, chat_history, state, llm_client)
    storage_intent = intent_service.to_chat_intent(parsed.intent)
    try:
        chat_service.store_message(
            session,
            chat_session,
            ChatSenderType.customer,
            message,
            storage_intent,
            external_message_id,
        )
    except IntegrityError as exc:
        if is_duplicate_external_message_error(exc):
            session.rollback()
            return "", "unknown", True
        raise

    if parsed.confidence < 0.6:
        reply = "Maaf kak, saya kurang paham. Kakak mau tanya produk, pesan barang, atau cek pesanan?"
        parsed.intent = "unknown"
        storage_intent = ChatIntent.unknown
    else:
        reply = build_reply(
            session,
            message,
            parsed,
            llm_client,
            chat_history,
            chat_session,
            customer.id,
            customer.phone,
            midtrans_client,
            shipping_client,
        )
    chat_service.update_session_state(chat_session, {"last_intent": parsed.intent})
    chat_service.store_message(session, chat_session, ChatSenderType.bot, reply, storage_intent)
    session.commit()
    return reply, parsed.intent, False


def is_duplicate_external_message_error(exc: IntegrityError) -> bool:
    return "ux_chat_messages_external_message_id" in str(exc.orig)


def detect_intent(message: str) -> ChatIntent:
    normalized = message.lower()
    if any(keyword in normalized for keyword in CHECKOUT_KEYWORDS):
        return ChatIntent.checkout
    if any(keyword in normalized for keyword in ORDER_KEYWORDS):
        return ChatIntent.track_order
    if any(keyword in normalized for keyword in PRODUCT_KEYWORDS):
        return ChatIntent.ask_product
    if any(keyword in normalized for keyword in ["halo", "hai", "hello", "pagi", "siang"]):
        return ChatIntent.greeting
    return ChatIntent.unknown


def build_reply(
    session: Session,
    message: str,
    parsed: ParsedIntent,
    llm_client: LlmClient | None = None,
    chat_history: str = "",
    chat_session=None,
    customer_id: int | None = None,
    customer_phone: str | None = None,
    midtrans_client: MidtransClient | None = None,
    shipping_client: ShippingClient | None = None,
) -> str:
    if parsed.intent in {"ask_product", "ask_price", "ask_stock", "ask_variant", "ask_color", "ask_size"}:
        search_text = parsed.product_name or parsed.variant or message
        products = product_tool_service.find_active_products_for_message(session, search_text)
        if chat_session is not None:
            product_tool_service.update_product_state_from_results(chat_session, products, parsed.intent)
        return product_tool_service.build_product_rag_answer(products, message, llm_client, chat_history)

    if parsed.intent == "add_to_cart":
        return add_to_cart_reply(session, parsed, message, llm_client, chat_history, chat_session, customer_id)

    if parsed.intent == "view_cart":
        return view_cart_reply(session, customer_id)

    if parsed.intent == "confirm_address":
        return confirm_address_reply(session, parsed, message, chat_session, customer_id, shipping_client)

    if parsed.intent == "create_payment":
        return create_payment_reply(session, parsed, chat_session, customer_id, customer_phone, midtrans_client)

    if parsed.intent in {"checkout", "ask_how_to_order"}:
        return checkout_reply(session, parsed, message, chat_session, customer_id)
    if parsed.intent in {"order_status", "payment_status"}:
        return order_status_reply(session, parsed)
    if parsed.intent == "greeting":
        return "Halo, saya bisa bantu info produk, stok, warna, ukuran, pesanan, dan pembayaran."
    if parsed.intent in {"complaint", "human_help"}:
        if chat_session is not None:
            chat_service.update_session_state(chat_session, {"needs_human": True, "stage": "human_help"})
        return "Maaf ya kak. Saya teruskan ke admin manusia supaya bisa dibantu lebih tepat."
    if llm_client is not None:
        try:
            generated = llm_client.generate(
                "Jawab singkat sebagai admin toko online. Jangan karang stok, harga, atau status pesanan.\n"
                "Gunakan RIWAYAT CHAT untuk memahami konteks percakapan.\n\n"
                f"RIWAYAT CHAT:\n{chat_history or 'Belum ada riwayat chat sebelumnya.'}\n\n"
                f"PESAN CUSTOMER:\n{message}\n\n"
                "JAWABAN WHATSAPP:"
            )
            if generated:
                return generated
        except Exception:
            pass
    return "Saya bisa bantu info produk, stok, warna, ukuran, checkout, pembayaran, dan cek pesanan."


def add_to_cart_reply(
    session: Session,
    parsed: ParsedIntent,
    message: str,
    llm_client: LlmClient | None,
    chat_history: str,
    chat_session,
    customer_id: int | None,
) -> str:
    if chat_session is None or customer_id is None:
        return "Maaf kak, saya belum bisa membuat keranjang dari chat ini."
    state = chat_service.get_session_state(chat_session)
    product = None
    if parsed.product_name:
        product = product_tool_service.find_best_active_product(session, parsed.product_name)
    if product is None:
        product = product_tool_service.find_active_product_by_id(session, state.get("current_product_id"))
    if product is None:
        return "Produk yang mau dipesan yang mana ya kak? Bisa sebut nama atau warna produknya."

    quantity = parsed.quantity or 1
    available_stock = max(product.stock_qty - product.reserved_qty, 0)
    if available_stock < quantity:
        return f"Maaf kak, stok {product.name} tinggal {available_stock} pcs. Mau pesan jumlah yang tersedia?"

    cart_item = cart_service.add_product_to_cart(session, customer_id, chat_session.id, product, quantity)
    chat_service.update_session_state(
        chat_session,
        {
            "stage": "cart_active",
            "current_product_id": product.id,
            "current_product_name": product.name,
            "pending_quantity": quantity,
        },
    )
    total = cart_service.cart_total(session, cart_item.cart_id)
    fallback = f"Siap kak, {quantity} {product.name} saya masukkan ke keranjang. Total sementara Rp{total:.0f}."
    if llm_client is None:
        return fallback
    try:
        generated = llm_client.generate(
            "Kamu admin WhatsApp toko online. Buat jawaban natural dan singkat.\n"
            "Gunakan hanya FAKTA KERANJANG. Jangan karang harga/stok.\n\n"
            f"RIWAYAT CHAT:\n{chat_history or 'Belum ada riwayat chat sebelumnya.'}\n\n"
            f"PESAN CUSTOMER:\n{message}\n\n"
            "FAKTA KERANJANG:\n"
            f"produk: {product.name}\n"
            f"quantity ditambahkan: {quantity}\n"
            f"quantity di keranjang: {cart_item.quantity}\n"
            f"harga satuan: Rp{product.price:.0f}\n"
            f"total sementara: Rp{total:.0f}\n\n"
            "JAWABAN WHATSAPP:"
        ).strip()
        return generated or fallback
    except Exception:
        return fallback


def view_cart_reply(session: Session, customer_id: int | None) -> str:
    if customer_id is None:
        return "Maaf kak, saya belum bisa membuka keranjang dari chat ini."
    items = cart_service.active_cart_items(session, customer_id)
    if not items:
        return "Keranjang kakak masih kosong. Mau saya bantu pilih produk dulu?"
    lines = ["Keranjang kakak:"]
    for item, product in items:
        lines.append(f"- {product.name} x{item.quantity} = Rp{item.subtotal:.0f}")
    total = cart_service.active_cart_total(session, customer_id)
    lines.append(f"Total sementara Rp{total:.0f}.")
    lines.append("Kalau sudah sesuai, kirim alamat lengkap untuk checkout ya kak.")
    return "\n".join(lines)


def order_status_reply(session: Session, parsed: ParsedIntent) -> str:
    if not parsed.order_number:
        return "Kirim order number, nanti saya cek status pesanan dan pembayaran. Contoh: ORD-20260531-ABCDEFGH"
    status = order_service.get_order_status(session, parsed.order_number)
    if status is None:
        return f"Maaf kak, pesanan {parsed.order_number} belum saya temukan. Coba cek lagi order number-nya ya."
    lines = [
        f"Status pesanan {status.order_number}:",
        f"Order: {status.order_status}",
        f"Pembayaran: {status.payment_status}",
        f"Pengiriman: {status.shipping_status}",
        f"Total: Rp{status.grand_total:.0f}",
    ]
    if status.payment_url:
        lines.append(f"Link pembayaran: {status.payment_url}")
    return "\n".join(lines)

def checkout_reply(
    session: Session,
    parsed: ParsedIntent,
    message: str,
    chat_session,
    customer_id: int | None,
) -> str:
    if chat_session is None or customer_id is None:
        return "Maaf kak, saya belum bisa checkout dari chat ini."

    product = None
    if parsed.product_name:
        product = product_tool_service.find_best_active_product(session, parsed.product_name)
    if product is not None and parsed.quantity:
        available_stock = max(product.stock_qty - product.reserved_qty, 0)
        if available_stock < parsed.quantity:
            return f"Maaf kak, stok {product.name} tinggal {available_stock} pcs. Mau checkout jumlah yang tersedia?"
        cart_service.set_product_quantity(session, customer_id, chat_session.id, product, parsed.quantity)
        chat_service.update_session_state(
            chat_session,
            {
                "stage": "waiting_address",
                "current_product_id": product.id,
                "current_product_name": product.name,
                "pending_quantity": parsed.quantity,
            },
        )
    else:
        chat_service.update_session_state(chat_session, {"stage": "waiting_address"})

    items = cart_service.active_cart_items(session, customer_id)
    if not items:
        return "Boleh sebut produk dan jumlah yang mau di-checkout dulu kak?"
    total = cart_service.active_cart_total(session, customer_id)
    return (
        f"Siap kak, keranjang total sementara Rp{total:.0f}. "
        "Untuk checkout, kirim nama penerima, nomor HP, alamat lengkap, kota, dan kode pos ya kak."
    )

def confirm_address_reply(
    session: Session,
    parsed: ParsedIntent,
    message: str,
    chat_session,
    customer_id: int | None,
    shipping_client: ShippingClient | None,
) -> str:
    if chat_session is None or customer_id is None:
        return "Maaf kak, saya belum bisa checkout dari chat ini."
    if shipping_client is None:
        return "Maaf kak, sistem ongkir belum siap. Coba lagi sebentar ya."

    state = chat_service.get_session_state(chat_session)
    address_data = collect_checkout_address_data(parsed.address or message, state)
    missing = missing_checkout_address_fields(address_data)
    chat_service.update_session_state(
        chat_session,
        {"stage": "waiting_address", "checkout_address": address_data},
    )
    if missing:
        return "Data checkout hampir lengkap kak. Mohon kirim " + ", ".join(missing) + "."

    items = cart_service.active_cart_items(session, customer_id)
    if not items:
        return "Keranjang kakak masih kosong. Sebut produk dan jumlah yang mau dibeli dulu ya."

    for cart_item, product in items:
        available_stock = max(product.stock_qty - product.reserved_qty, 0)
        if available_stock < cart_item.quantity:
            return f"Maaf kak, stok {product.name} tinggal {available_stock} pcs. Mau pesan jumlah yang tersedia?"

    try:
        quotes = shipping_client.get_shipping_quotes(address_data, build_shipping_rate_items(items))
    except ShippingRateUnavailable as exc:
        return (
            "Maaf kak, ongkir belum tersedia dari Biteship. "
            f"{exc}. Coba cek ulang kota/kode pos atau coba lagi sebentar ya."
        )
    if not quotes:
        return "Maaf kak, ongkir belum bisa dihitung. Coba kirim ulang kota dan kode pos ya."
    normalized_quotes = normalize_shipping_quotes(quotes)
    subtotal = cart_service.active_cart_total(session, customer_id)
    customer_address = format_customer_address(address_data)
    settings = get_settings()
    chat_service.update_session_state(
        chat_session,
        {
            "stage": "waiting_shipping_confirmation",
            "checkout_address": address_data,
            "shipping_quotes": normalized_quotes,
            "selected_shipping_quote": normalized_quotes[0] if len(normalized_quotes) == 1 else {},
            "store_address": settings.store_address,
            "store_origin_postal_code": settings.store_origin_postal_code,
        },
    )
    return build_shipping_confirmation_reply(
        store_address=settings.store_address,
        customer_address=customer_address,
        subtotal=subtotal,
        quotes=normalized_quotes,
    )

def create_payment_reply(
    session: Session,
    parsed: ParsedIntent,
    chat_session,
    customer_id: int | None,
    customer_phone: str | None,
    midtrans_client: MidtransClient | None,
) -> str:
    if chat_session is None or customer_id is None or customer_phone is None:
        return "Maaf kak, saya belum bisa checkout dari chat ini."
    if midtrans_client is None:
        return "Maaf kak, sistem pembayaran belum siap. Coba lagi sebentar ya."
    state = chat_service.get_session_state(chat_session)
    address_data = dict(state.get("checkout_address") or {})
    selected_quote = dict(state.get("selected_shipping_quote") or {})
    if not address_data:
        chat_service.update_session_state(chat_session, {"stage": "waiting_address"})
        return "Sebelum bayar, saya perlu hitung ongkir dulu. Kirim alamat lengkap dan kode pos ya kak."
    quotes = list(state.get("shipping_quotes") or [])
    if parsed.quantity and quotes:
        quote_index = parsed.quantity - 1
        if quote_index < 0 or quote_index >= len(quotes):
            return "Pilihan ongkirnya belum ada kak. Balas pilih nomor ongkir yang tersedia ya."
        selected_quote = dict(quotes[quote_index])
    elif len(quotes) > 1:
        return "Pilih nomor ongkir dulu ya kak, misalnya balas pilih 1 atau pilih 2."
    elif len(quotes) == 1 and not selected_quote:
        selected_quote = dict(quotes[0])

    items = cart_service.active_cart_items(session, customer_id)
    if not items:
        return "Keranjang kakak masih kosong. Sebut produk dan jumlah yang mau dibeli dulu ya."

    checkout_payload = CheckoutRequest(
        phone=customer_phone,
        recipient_name=address_data["recipient_name"],
        recipient_phone=address_data["recipient_phone"],
        address_line=address_data["address_line"],
        city=address_data.get("city"),
        postal_code=address_data.get("postal_code"),
        biteship_area_id=address_data.get("biteship_area_id"),
        shipping_cost=Decimal(str(selected_quote["price"])),
        items=[CheckoutItemRequest(slug=product.slug, quantity=cart_item.quantity) for cart_item, product in items],
    )
    checkout = order_service.create_checkout(session, checkout_payload, midtrans_client)
    order = session.scalar(select(Order).where(Order.order_number == checkout.order_number))
    if order is not None:
        session.add(
            ShippingQuote(
                order_id=order.id,
                courier_code=str(selected_quote["courier_code"]),
                courier_name=str(selected_quote["courier_name"]),
                service_code=selected_quote.get("service_code"),
                service_name=selected_quote.get("service_name"),
                price=Decimal(str(selected_quote["price"])),
                estimated_delivery=selected_quote.get("estimated_delivery"),
                is_selected=True,
                raw_response=selected_quote.get("raw_response"),
            )
        )
    cart_service.mark_active_cart_ordered(session, customer_id)
    chat_service.update_session_state(
        chat_session,
        {"stage": "waiting_payment", "order_number": checkout.order_number, "payment_url": checkout.payment_url},
    )
    return (
        "Checkout berhasil dibuat kak.\n"
        f"Order: {checkout.order_number}\n"
        f"Total: Rp{checkout.grand_total:.0f}\n"
        f"Link pembayaran: {checkout.payment_url}"
    )

def collect_checkout_address_data(message: str, state: dict) -> dict[str, str]:
    data = dict(state.get("checkout_address") or {})
    for line in [line.strip() for line in message.splitlines() if line.strip()]:
        label, value = split_labeled_value(line)
        lowered = label.lower()
        if value:
            if "nama" in lowered and "penerima" in lowered:
                data["recipient_name"] = value
                continue
            if ("nomor" in lowered or "no" in lowered) and "hp" in lowered:
                data["recipient_phone"] = extract_phone_number(value) or value
                continue
            if "alamat" in lowered:
                data["address_line"] = value
                continue
            if "kota" in lowered:
                data["city"] = value
                continue
            if "kode pos" in lowered or "area" in lowered:
                postal_code = extract_postal_code(value)
                if postal_code:
                    data["postal_code"] = postal_code
                continue

        lowered_line = line.lower()
        if "alamat saya" in lowered_line:
            data["address_line"] = line[lowered_line.find("alamat saya") + len("alamat saya") :].strip(" :,-")
        elif lowered_line.startswith(("jl ", "jl.", "jalan")) or " jl " in lowered_line:
            data.setdefault("address_line", line)

        phone = extract_phone_number(line)
        if phone and ("hp" in lowered_line or "nomor" in lowered_line):
            data["recipient_phone"] = phone
        postal_code = extract_postal_code(line)
        if postal_code and ("kode pos" in lowered_line or "area" in lowered_line):
            data["postal_code"] = postal_code
    return {key: value for key, value in data.items() if value}

def split_labeled_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        return line, ""
    label, value = line.split(":", 1)
    return label.strip(), value.strip()

def extract_phone_number(text: str) -> str | None:
    digits = "".join(character for character in text if character.isdigit())
    if 8 <= len(digits) <= 15:
        return digits
    return None

def extract_postal_code(text: str) -> str | None:
    for token in text.replace(":", " ").replace(",", " ").split():
        if token.isdigit() and len(token) == 5:
            return token
    return None

def missing_checkout_address_fields(address_data: dict[str, str]) -> list[str]:
    labels = {
        "recipient_name": "nama penerima",
        "recipient_phone": "nomor HP",
        "address_line": "alamat lengkap",
        "city": "kota",
        "postal_code": "kode pos",
    }
    return [label for key, label in labels.items() if not address_data.get(key)]

def build_shipping_rate_items(items) -> list[dict[str, object]]:
    return [
        {
            "name": product.name,
            "value": int(product.price),
            "weight": max(product.weight_gram or 0, 1),
            "quantity": cart_item.quantity,
        }
        for cart_item, product in items
    ]

def normalize_shipping_quotes(quotes: list[dict[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for quote in quotes:
        normalized.append(
            {
                "courier_code": str(quote.get("courier_code") or "estimasi"),
                "courier_name": str(quote.get("courier_name") or "Estimasi Ongkir"),
                "service_code": None if quote.get("service_code") is None else str(quote.get("service_code")),
                "service_name": None if quote.get("service_name") is None else str(quote.get("service_name")),
                "price": str(Decimal(str(quote.get("price") or "0"))),
                "estimated_delivery": None
                if quote.get("estimated_delivery") is None
                else str(quote.get("estimated_delivery")),
                "raw_response": quote.get("raw_response") if isinstance(quote.get("raw_response"), dict) else quote,
            }
        )
    return normalized

def format_customer_address(address_data: dict[str, str]) -> str:
    parts = [address_data["address_line"]]
    if address_data.get("city"):
        parts.append(address_data["city"])
    if address_data.get("postal_code"):
        parts.append(address_data["postal_code"])
    return ", ".join(parts)

def build_shipping_confirmation_reply(
    store_address: str,
    customer_address: str,
    subtotal: Decimal,
    quotes: list[dict[str, object]],
) -> str:
    quote_lines = []
    for index, quote in enumerate(quotes, start=1):
        service_name = quote.get("service_name") or quote.get("service_code") or "Regular"
        estimate = quote.get("estimated_delivery") or "estimasi"
        price = Decimal(str(quote["price"]))
        quote_lines.append(
            f"{index}. {quote['courier_name']} {service_name} Rp{price:.0f} ({estimate}) - Total Rp{subtotal + price:.0f}"
        )
    return (
        "Ongkir sudah saya hitung kak.\n"
        f"Alamat toko: {store_address}\n"
        f"Alamat customer: {customer_address}\n"
        f"Produk: Rp{subtotal:.0f}\n"
        "Pilihan ongkir:\n"
        + "\n".join(quote_lines)
        + "\n"
        "Balas pilih nomor ongkir dulu ya kak, misalnya pilih 1."
    )
