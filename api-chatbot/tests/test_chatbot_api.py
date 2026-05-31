from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from urllib.error import HTTPError
from io import BytesIO
from datetime import UTC, datetime

from app.db.session import SessionLocal
from app.main import app
from app.model.cart import Cart, CartItem
from app.model.chat import ChatMessage, ChatSession
from app.model.customer import Customer, CustomerAddress
from app.model.order import Order, OrderItem
from app.model.payment import Payment
from app.model.product import Product
from app.model.shipping import ShippingQuote

client = TestClient(app)


class FakeWahaClient:
    def __init__(self) -> None:
        self.sent_messages: list[tuple[str, str]] = []
        self.sent_images: list[tuple[str, str, str | None]] = []

    def send_text(self, phone: str, message: str) -> dict[str, str]:
        self.sent_messages.append((phone, message))
        return {"status": "sent"}

    def send_image(self, chat_id: str, image_url: str, caption: str | None = None) -> dict[str, str]:
        self.sent_images.append((chat_id, image_url, caption))
        return {"status": "sent"}

class FailingImageWahaClient(FakeWahaClient):
    def send_image(self, chat_id: str, image_url: str, caption: str | None = None) -> dict[str, str]:
        raise HTTPError(image_url, 422, "Unprocessable Entity", hdrs=None, fp=BytesIO(b'{"message":"bad image"}'))


class FakeMidtransClient:
    def create_payment_link(self, order_number: str, gross_amount: str, customer: dict[str, str]) -> dict[str, str]:
        return {
            "provider_order_id": f"midtrans-{order_number}",
            "payment_url": f"https://pay.example.test/{order_number}",
            "snap_token": f"snap-{order_number}",
        }

class FakeShippingClient:
    def get_shipping_quotes(self, destination: dict[str, str], items: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "courier_code": "jne",
                "courier_name": "JNE",
                "service_code": "reg",
                "service_name": "REG",
                "price": "15000",
                "estimated_delivery": "2-3 hari",
                "raw_response": {"source": "fake"},
            }
        ]

class FakeMultiQuoteShippingClient:
    def get_shipping_quotes(self, destination: dict[str, str], items: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "courier_code": "jne",
                "courier_name": "JNE",
                "service_code": "reg",
                "service_name": "REG",
                "price": "18000",
                "estimated_delivery": "2-3 hari",
                "raw_response": {"source": "fake", "option": 1},
            },
            {
                "courier_code": "jnt",
                "courier_name": "J&T",
                "service_code": "ez",
                "service_name": "EZ",
                "price": "17000",
                "estimated_delivery": "1-2 hari",
                "raw_response": {"source": "fake", "option": 2},
            },
        ]

class UnavailableShippingClient:
    def get_shipping_quotes(self, destination: dict[str, str], items: list[dict[str, object]]) -> list[dict[str, object]]:
        from app.service.shipping_service import ShippingRateUnavailable

        raise ShippingRateUnavailable("Biteship tidak menemukan layanan kurir untuk kode pos 60111 ke 50158")


class FakeLlmClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "Siap kak, Hoodie Black L tersedia. Harganya Rp249000 dan stok ready 6 pcs."

class FakeConversationLlmClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        lowered = prompt.lower()
        if "json intent" in lowered and "pesan customer:\nsaya mau checkout" in lowered:
            return '{"intent":"checkout","product_name":"Hoodie Black L","quantity":2,"variant":null,"address":null,"order_number":null,"confidence":0.92,"notes":"customer wants checkout"}'
        if "json intent" in lowered and "tampilin keranjang" in lowered:
            return '{"intent":"view_cart","product_name":null,"quantity":null,"variant":null,"address":null,"order_number":null,"confidence":0.91,"notes":"customer wants cart"}'
        if "json intent" in lowered and "mau 2" in lowered:
            return '{"intent":"add_to_cart","product_name":null,"quantity":2,"variant":null,"address":null,"order_number":null,"confidence":0.91,"notes":"customer wants two of current product"}'
        if "json intent" in lowered and "mau 1" in lowered:
            return '{"intent":"add_to_cart","product_name":null,"quantity":1,"variant":null,"address":null,"order_number":null,"confidence":0.91,"notes":"customer wants one of current product"}'
        if "JSON INTENT" in prompt:
            return '{"intent":"ask_product","product_name":"Hoodie Black L","quantity":null,"variant":"black L","address":null,"order_number":null,"confidence":0.94,"notes":null}'
        if "KERANJANG" in prompt:
            return "Siap kak, 2 Hoodie Black L saya masukkan ke keranjang. Total sementara Rp498000."
        return "Siap kak, Hoodie Black L ready stok 6 pcs. Mau pesan berapa?"

class FakeCheckoutAddressLlmClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        lowered = prompt.lower()
        if "json intent" in lowered and "ada hoodie black l" in lowered:
            return '{"intent":"ask_product","product_name":"Hoodie Black L","quantity":null,"variant":"black L","address":null,"order_number":null,"confidence":0.94,"notes":null}'
        if "json intent" in lowered and "checkout" in lowered:
            return '{"intent":"checkout","product_name":"Hoodie Black L","quantity":6,"variant":null,"address":null,"order_number":null,"confidence":0.92,"notes":"checkout cart"}'
        if "json intent" in lowered and ("kode pos" in lowered or "nomor hp" in lowered):
            return '{"intent":"checkout","product_name":"Hoodie Black L","quantity":60111,"variant":null,"address":null,"order_number":null,"confidence":0.91,"notes":"bad numeric parse"}'
        if "keranjang" in prompt:
            return "Siap kak, Hoodie Black L saya masukkan ke keranjang."
        return "Siap kak, Hoodie Black L ready stok 6 pcs. Mau pesan berapa?"

class FakeLowConfidenceLlmClient:
    def generate(self, prompt: str) -> str:
        if "JSON INTENT" in prompt:
            return '{"intent":"unknown","product_name":null,"quantity":null,"variant":null,"address":null,"order_number":null,"confidence":0.42,"notes":"unclear"}'
        return "Ini tidak boleh dipakai"

class FakeHumanHelpLlmClient:
    def generate(self, prompt: str) -> str:
        if "JSON INTENT" in prompt:
            return '{"intent":"human_help","product_name":null,"quantity":null,"variant":null,"address":null,"order_number":null,"confidence":0.93,"notes":"needs admin"}'
        return "Ini tidak boleh dipakai"


def cleanup_phone(phone: str) -> None:
    with SessionLocal() as session:
        customer_ids = list(session.scalars(select(Customer.id).where(Customer.phone == phone)))
        chat_ids = list(
            session.scalars(select(ChatSession.id).where(ChatSession.customer_id.in_(customer_ids)))
        )
        if customer_ids:
            order_ids = list(session.scalars(select(Order.id).where(Order.customer_id.in_(customer_ids))))
            cart_ids = list(session.scalars(select(Cart.id).where(Cart.customer_id.in_(customer_ids))))
            if cart_ids:
                session.execute(delete(CartItem).where(CartItem.cart_id.in_(cart_ids)))
                session.execute(delete(Cart).where(Cart.id.in_(cart_ids)))
            if order_ids:
                session.execute(delete(ShippingQuote).where(ShippingQuote.order_id.in_(order_ids)))
                session.execute(delete(Payment).where(Payment.order_id.in_(order_ids)))
                session.execute(delete(OrderItem).where(OrderItem.order_id.in_(order_ids)))
                session.execute(delete(Order).where(Order.id.in_(order_ids)))
            session.execute(delete(CustomerAddress).where(CustomerAddress.customer_id.in_(customer_ids)))
        if chat_ids:
            session.execute(delete(ChatMessage).where(ChatMessage.chat_session_id.in_(chat_ids)))
            session.execute(delete(ChatSession).where(ChatSession.id.in_(chat_ids)))
        if customer_ids:
            session.execute(delete(Customer).where(Customer.id.in_(customer_ids)))
        session.commit()


def cleanup_product(slug: str) -> None:
    with SessionLocal() as session:
        session.execute(delete(Product).where(Product.slug == slug))
        session.commit()


def create_active_product(slug: str) -> None:
    cleanup_product(slug)
    with SessionLocal() as session:
        session.add(
            Product(
                name="Hoodie Black L",
                slug=slug,
                description="Hoodie oversized warna hitam ukuran L",
                image_url="https://drive.google.com/file/d/example/view",
                price="249000",
                stock_qty=8,
                reserved_qty=2,
                color="black",
                size="L",
                gender="unisex",
                material="cotton fleece",
                weight_gram=600,
                status="active",
            )
        )
        session.commit()

def create_waiting_address_cart(phone: str, slug: str) -> None:
    with SessionLocal() as session:
        customer = Customer(
            phone=phone,
            source="whatsapp",
            first_seen_at=datetime.now(UTC),
            last_seen_at=datetime.now(UTC),
        )
        session.add(customer)
        session.flush()
        chat_session = ChatSession(
            customer_id=customer.id,
            channel="whatsapp",
            started_at=datetime.now(UTC),
            last_message_at=datetime.now(UTC),
            metadata_={"stage": "waiting_address"},
        )
        session.add(chat_session)
        session.flush()
        product = session.scalar(select(Product).where(Product.slug == slug))
        assert product is not None
        cart = Cart(customer_id=customer.id, chat_session_id=chat_session.id, status="active")
        session.add(cart)
        session.flush()
        session.add(
            CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=1,
                unit_price=product.price,
                subtotal=product.price,
            )
        )
        session.commit()


def test_chatbot_message_answers_product_question_and_stores_conversation() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62812{uuid4().hex[:10]}"
    slug = f"hoodie-chat-{uuid4().hex}"
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_llm_client] = lambda: FakeLlmClient()

    response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Ada hoodie black ukuran L?"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == phone
    assert "Hoodie Black L" in data["reply"]
    assert "249000" in data["reply"]
    assert "6" in data["reply"]

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        messages = list(
            session.scalars(
                select(ChatMessage)
                .join(ChatSession, ChatSession.id == ChatMessage.chat_session_id)
                .where(ChatSession.customer_id == customer.id)
                .order_by(ChatMessage.id)
            )
        )
        assert [message.sender_type for message in messages] == ["customer", "bot"]

    cleanup_phone(phone)
    cleanup_product(slug)


def test_chatbot_product_question_uses_rag_context_with_llm() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62817{uuid4().hex[:10]}"
    slug = f"rag-product-{uuid4().hex}"
    fake_llm = FakeLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm

    response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Ada hoodie black ukuran L?"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Siap kak, Hoodie Black L tersedia. Harganya Rp249000 dan stok ready 6 pcs."
    assert fake_llm.prompts
    prompt = next(prompt for prompt in fake_llm.prompts if "KONTEXT PRODUK" in prompt)
    assert "KONTEXT PRODUK" in prompt
    assert "Hoodie Black L" in prompt
    assert "stok tersedia: 6" in prompt
    assert "Jangan karang harga, stok, warna, ukuran, atau foto" in prompt

    cleanup_phone(phone)
    cleanup_product(slug)


def test_chatbot_product_question_includes_chat_history_in_rag_prompt() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62818{uuid4().hex[:10]}"
    slug = f"history-product-{uuid4().hex}"
    fake_llm = FakeLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm

    first_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Saya cari hoodie hitam ukuran L"},
    )
    second_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "kalau yang tadi stoknya berapa?"},
    )

    app.dependency_overrides.clear()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    rag_prompts = [prompt for prompt in fake_llm.prompts if "KONTEXT PRODUK" in prompt]
    assert len(rag_prompts) == 2
    second_prompt = rag_prompts[1]
    assert "RIWAYAT CHAT" in second_prompt
    assert "customer: Saya cari hoodie hitam ukuran L" in second_prompt
    assert "bot: Siap kak, Hoodie Black L tersedia" in second_prompt
    assert "PERTANYAAN CUSTOMER:\nkalau yang tadi stoknya berapa?" in second_prompt

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_uses_structured_intent_state_and_cart_for_followup_quantity() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62819{uuid4().hex[:10]}"
    slug = f"state-cart-product-{uuid4().hex}"
    fake_llm = FakeConversationLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm

    first_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Ada Hoodie Black L?"},
    )
    second_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "mau 2"},
    )

    app.dependency_overrides.clear()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["intent"] == "add_to_cart"
    assert "2 Hoodie Black L" in second_response.json()["reply"]

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        chat_session = session.scalar(select(ChatSession).where(ChatSession.customer_id == customer.id))
        assert chat_session is not None
        assert chat_session.metadata_["current_product_name"] == "Hoodie Black L"
        cart = session.scalar(select(Cart).where(Cart.customer_id == customer.id))
        assert cart is not None
        cart_item = session.scalar(select(CartItem).where(CartItem.cart_id == cart.id))
        assert cart_item is not None
        assert cart_item.quantity == 2
        assert cart_item.subtotal == 498000

    assert any("JSON INTENT" in prompt for prompt in fake_llm.prompts)

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_can_show_cart_and_enter_checkout_without_adding_duplicate_items() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62823{uuid4().hex[:10]}"
    slug = f"cart-checkout-product-{uuid4().hex}"
    fake_llm = FakeConversationLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm

    first_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "Ada Hoodie Black L?"})
    second_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "mau 1"})
    cart_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "Tampilin keranjang aku"})
    checkout_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Saya mau checkout kak 2 Hoodie Black L"},
    )

    app.dependency_overrides.clear()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert cart_response.status_code == 200
    assert checkout_response.status_code == 200
    assert cart_response.json()["intent"] == "view_cart"
    assert "Keranjang kakak" in cart_response.json()["reply"]
    assert "Hoodie Black L" in cart_response.json()["reply"]
    assert checkout_response.json()["intent"] == "checkout"
    assert "alamat" in checkout_response.json()["reply"].lower()

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        cart = session.scalar(select(Cart).where(Cart.customer_id == customer.id))
        assert cart is not None
        cart_item = session.scalar(select(CartItem).where(CartItem.cart_id == cart.id))
        assert cart_item is not None
        assert cart_item.quantity == 2

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_checkout_address_creates_payment_without_rereading_phone_as_quantity() -> None:
    from app.api.chatbot_api import get_llm_client, get_midtrans_client, get_shipping_client

    phone = f"62824{uuid4().hex[:10]}"
    slug = f"address-checkout-product-{uuid4().hex}"
    fake_llm = FakeCheckoutAddressLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    create_waiting_address_cart(phone, slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    app.dependency_overrides[get_midtrans_client] = lambda: FakeMidtransClient()
    app.dependency_overrides[get_shipping_client] = lambda: FakeShippingClient()

    product_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "Ada Hoodie Black L?"})
    checkout_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Saya mau checkout kak 6 Hoodie Black L"},
    )
    partial_address_response = client.post(
        "/api/chatbot/message",
        json={
            "phone": phone,
            "message": "Saya mau checkout, alamat saya jl keputih no 1\nArea/kode pos pengiriman : 60111",
        },
    )
    full_address_response = client.post(
        "/api/chatbot/message",
        json={
            "phone": phone,
            "message": "Nama Penerima: Ian Ale\nNomor HP : 081233914116\nAlamat lengkap: jl keputih no 1\nKota : Surabaya\nArea/kode pos pengiriman : 60111",
        },
    )
    payment_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": "Setuju kak, lanjut bayar"},
    )

    app.dependency_overrides.clear()
    assert product_response.status_code == 200
    assert checkout_response.status_code == 200
    assert partial_address_response.status_code == 200
    assert full_address_response.status_code == 200
    assert payment_response.status_code == 200
    assert partial_address_response.json()["intent"] == "confirm_address"
    assert "nama penerima" in partial_address_response.json()["reply"].lower()
    assert full_address_response.json()["intent"] == "confirm_address"
    assert "Ongkir" in full_address_response.json()["reply"]
    assert "Alamat toko" in full_address_response.json()["reply"]
    assert "Alamat customer" in full_address_response.json()["reply"]
    assert "https://pay.example.test/" not in full_address_response.json()["reply"]
    assert "stok" not in full_address_response.json()["reply"].lower()
    assert payment_response.json()["intent"] == "create_payment"
    assert "https://pay.example.test/" in payment_response.json()["reply"]

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        cart = session.scalar(select(Cart).where(Cart.customer_id == customer.id))
        assert cart is not None
        assert cart.status == "ordered"
        cart_item = session.scalar(select(CartItem).where(CartItem.cart_id == cart.id))
        assert cart_item is not None
        assert cart_item.quantity == 6
        order = session.scalar(select(Order).where(Order.customer_id == customer.id))
        assert order is not None
        assert order.shipping_cost == 15000
        assert order.grand_total == 1509000
        quote = session.scalar(select(ShippingQuote).where(ShippingQuote.order_id == order.id))
        assert quote is not None
        assert quote.is_selected is True

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_requires_customer_to_choose_biteship_quote_before_payment() -> None:
    from app.api.chatbot_api import get_llm_client, get_midtrans_client, get_shipping_client

    phone = f"62826{uuid4().hex[:10]}"
    slug = f"choose-biteship-quote-{uuid4().hex}"
    fake_llm = FakeCheckoutAddressLlmClient()
    cleanup_phone(phone)
    create_active_product(slug)
    create_waiting_address_cart(phone, slug)
    app.dependency_overrides[get_llm_client] = lambda: fake_llm
    app.dependency_overrides[get_midtrans_client] = lambda: FakeMidtransClient()
    app.dependency_overrides[get_shipping_client] = lambda: FakeMultiQuoteShippingClient()

    quote_response = client.post(
        "/api/chatbot/message",
        json={
            "phone": phone,
            "message": "Nama Penerima: Ian Ale\nNomor HP : 081233914116\nAlamat lengkap: JL Semarang anjay mabar\nKota : Semarang\nArea/kode pos pengiriman : 50158",
        },
    )
    setuju_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "setuju"})
    payment_response = client.post("/api/chatbot/message", json={"phone": phone, "message": "pilih 2"})

    app.dependency_overrides.clear()
    assert quote_response.status_code == 200
    assert "Estimasi Ongkir" not in quote_response.json()["reply"]
    assert "1. JNE REG Rp18000" in quote_response.json()["reply"]
    assert "2. J&T EZ Rp17000" in quote_response.json()["reply"]
    assert setuju_response.status_code == 200
    assert "pilih nomor ongkir" in setuju_response.json()["reply"].lower()
    assert payment_response.status_code == 200
    assert payment_response.json()["intent"] == "create_payment"
    assert "https://pay.example.test/" in payment_response.json()["reply"]

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        order = session.scalar(select(Order).where(Order.customer_id == customer.id))
        assert order is not None
        assert order.shipping_cost == 17000
        quote = session.scalar(select(ShippingQuote).where(ShippingQuote.order_id == order.id))
        assert quote is not None
        assert quote.courier_code == "jnt"

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_does_not_show_estimated_shipping_when_biteship_unavailable() -> None:
    from app.api.chatbot_api import get_llm_client, get_shipping_client

    phone = f"62827{uuid4().hex[:10]}"
    slug = f"biteship-unavailable-{uuid4().hex}"
    cleanup_phone(phone)
    create_active_product(slug)
    create_waiting_address_cart(phone, slug)
    app.dependency_overrides[get_llm_client] = lambda: FakeCheckoutAddressLlmClient()
    app.dependency_overrides[get_shipping_client] = lambda: UnavailableShippingClient()

    response = client.post(
        "/api/chatbot/message",
        json={
            "phone": phone,
            "message": "Nama Penerima: Ian Ale\nNomor HP : 081233914116\nAlamat lengkap: JL Semarang anjay mabar\nKota : Semarang\nArea/kode pos pengiriman : 50158",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "Estimasi Ongkir" not in response.json()["reply"]
    assert "ongkir belum tersedia" in response.json()["reply"].lower()
    assert "kode pos" in response.json()["reply"].lower()

    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        assert session.scalar(select(Order).where(Order.customer_id == customer.id)) is None

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_low_confidence_intent_asks_for_clarification() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62820{uuid4().hex[:10]}"
    cleanup_phone(phone)
    app.dependency_overrides[get_llm_client] = lambda: FakeLowConfidenceLlmClient()

    response = client.post("/api/chatbot/message", json={"phone": phone, "message": "hmmm itu gimana ya"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["intent"] == "unknown"
    assert "kurang paham" in response.json()["reply"]

    cleanup_phone(phone)

def test_chatbot_human_help_sets_session_state_for_admin_followup() -> None:
    from app.api.chatbot_api import get_llm_client

    phone = f"62821{uuid4().hex[:10]}"
    cleanup_phone(phone)
    app.dependency_overrides[get_llm_client] = lambda: FakeHumanHelpLlmClient()

    response = client.post("/api/chatbot/message", json={"phone": phone, "message": "mau bicara admin"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["intent"] == "human_help"
    assert "admin manusia" in response.json()["reply"]
    with SessionLocal() as session:
        customer = session.scalar(select(Customer).where(Customer.phone == phone))
        assert customer is not None
        chat_session = session.scalar(select(ChatSession).where(ChatSession.customer_id == customer.id))
        assert chat_session is not None
        assert chat_session.metadata_["needs_human"] is True
        assert chat_session.metadata_["stage"] == "human_help"

    cleanup_phone(phone)


def test_waha_webhook_ignores_duplicate_external_message_id() -> None:
    from app.api.chatbot_api import get_waha_client

    phone = f"62813{uuid4().hex[:10]}"
    message_id = f"wamid-{uuid4().hex}"
    fake_waha = FakeWahaClient()
    cleanup_phone(phone)
    app.dependency_overrides[get_waha_client] = lambda: fake_waha

    payload = {
        "event": "message",
        "payload": {
            "id": message_id,
            "from": f"{phone}@c.us",
            "body": "produk apa aja?",
            "fromMe": False,
        },
    }
    first_response = client.post("/api/webhooks/waha/messages", json=payload)
    second_response = client.post("/api/webhooks/waha/messages", json=payload)

    app.dependency_overrides.clear()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["duplicate"] is False
    assert second_response.json()["duplicate"] is True
    assert len(fake_waha.sent_messages) == 1

    cleanup_phone(phone)


def test_waha_webhook_replies_to_original_lid_chat_id() -> None:
    from app.api.chatbot_api import get_waha_client

    chat_id = f"243{uuid4().hex[:12]}@lid"
    phone = chat_id.split("@", 1)[0]
    message_id = f"false_{chat_id}_{uuid4().hex[:8]}"
    fake_waha = FakeWahaClient()
    cleanup_phone(phone)
    app.dependency_overrides[get_waha_client] = lambda: fake_waha

    response = client.post(
        "/api/webhooks/waha/messages",
        json={
            "event": "message",
            "payload": {
                "id": message_id,
                "from": chat_id,
                "body": "produk apa aja?",
                "fromMe": False,
            },
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake_waha.sent_messages[0][0] == chat_id

    cleanup_phone(phone)


def test_waha_webhook_sends_product_image_as_whatsapp_image_not_text_url() -> None:
    from app.api.chatbot_api import get_waha_client

    phone = f"62816{uuid4().hex[:10]}"
    slug = f"image-product-{uuid4().hex}"
    fake_waha = FakeWahaClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_waha_client] = lambda: fake_waha

    response = client.post(
        "/api/webhooks/waha/messages",
        json={
            "event": "message",
            "payload": {
                "id": f"wamid-image-{uuid4().hex}",
                "from": f"{phone}@c.us",
                "body": "Ada hoodie black ukuran L?",
                "fromMe": False,
            },
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "https://drive.google.com/file/d/example/view" not in fake_waha.sent_messages[0][1]
    assert (f"{phone}@c.us", "https://drive.google.com/file/d/example/view", "Hoodie Black L") in fake_waha.sent_images

    cleanup_phone(phone)
    cleanup_product(slug)

def test_waha_webhook_does_not_fail_when_product_image_rejected_by_waha() -> None:
    from app.api.chatbot_api import get_waha_client

    phone = f"62822{uuid4().hex[:10]}"
    slug = f"bad-image-product-{uuid4().hex}"
    fake_waha = FailingImageWahaClient()
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_waha_client] = lambda: fake_waha

    response = client.post(
        "/api/webhooks/waha/messages",
        json={
            "event": "message",
            "payload": {
                "id": f"wamid-bad-image-{uuid4().hex}",
                "from": f"{phone}@c.us",
                "body": "Ada hoodie black ukuran L?",
                "fromMe": False,
            },
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert fake_waha.sent_messages

    cleanup_phone(phone)
    cleanup_product(slug)

def test_waha_google_drive_image_url_is_normalized_for_send_image_payload() -> None:
    from app.service.waha_service import image_filename, normalize_image_url

    image_url = "https://drive.google.com/file/d/1QCf1XRsIJ9uyI-sE9rl8M8viubX8yog8/view?usp=sharing"

    normalized_url = normalize_image_url(image_url)

    assert normalized_url == "https://drive.google.com/uc?export=download&id=1QCf1XRsIJ9uyI-sE9rl8M8viubX8yog8"
    assert image_filename(normalized_url) == "1QCf1XRsIJ9uyI-sE9rl8M8viubX8yog8.jpg"


def test_shipping_fallback_uses_store_origin_postal_code() -> None:
    from app.service.shipping_service import fallback_postal_code_quotes

    quotes = fallback_postal_code_quotes({"postal_code": "60111"})

    assert quotes[0]["courier_code"] == "estimasi"
    assert quotes[0]["price"] == "10000"
    assert quotes[0]["raw_response"] == {
        "source": "postal_code_fallback",
        "origin": "60111",
        "destination": "60111",
    }

def test_waha_webhook_treats_external_message_unique_violation_as_duplicate(monkeypatch) -> None:
    from app.api.chatbot_api import get_waha_client
    from app.service import chat_service

    phone = f"62815{uuid4().hex[:10]}"
    message_id = f"wamid-race-{uuid4().hex}"
    fake_waha = FakeWahaClient()
    cleanup_phone(phone)
    app.dependency_overrides[get_waha_client] = lambda: fake_waha

    first_payload = {
        "event": "message",
        "payload": {
            "id": message_id,
            "from": f"{phone}@c.us",
            "body": "produk apa aja?",
            "fromMe": False,
        },
    }
    first_response = client.post("/api/webhooks/waha/messages", json=first_payload)
    assert first_response.status_code == 200

    monkeypatch.setattr(chat_service, "has_external_message", lambda session, external_message_id: False)
    duplicate_payload = {
        "event": "message",
        "payload": {
            "id": message_id,
            "from": f"{phone}@c.us",
            "body": "Kok ga ada jawaban",
            "fromMe": False,
        },
    }
    duplicate_response = client.post("/api/webhooks/waha/messages", json=duplicate_payload)

    app.dependency_overrides.clear()
    assert duplicate_response.status_code == 200
    assert duplicate_response.json()["duplicate"] is True
    assert len(fake_waha.sent_messages) == 1

    cleanup_phone(phone)


def test_checkout_creates_order_payment_link_and_status_lookup() -> None:
    from app.api.chatbot_api import get_midtrans_client

    phone = f"62814{uuid4().hex[:10]}"
    slug = f"checkout-product-{uuid4().hex}"
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_midtrans_client] = lambda: FakeMidtransClient()

    response = client.post(
        "/api/chatbot/checkout",
        json={
            "phone": phone,
            "recipient_name": "Buyer Test",
            "recipient_phone": phone,
            "address_line": "Jl Test No 1",
            "city": "Jakarta",
            "postal_code": "12345",
            "items": [{"slug": slug, "quantity": 2}],
            "shipping_cost": "15000",
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["order_number"].startswith("ORD-")
    assert data["payment_url"] == f"https://pay.example.test/{data['order_number']}"
    assert data["grand_total"] == "513000.00"

    status_response = client.get(f"/api/chatbot/orders/{data['order_number']}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["order_number"] == data["order_number"]
    assert status_data["order_status"] == "waiting_payment"
    assert status_data["payment_status"] == "pending"

    webhook_response = client.post(
        "/api/webhooks/midtrans",
        json={
            "order_id": f"midtrans-{data['order_number']}",
            "transaction_id": f"tx-{uuid4().hex}",
            "transaction_status": "settlement",
            "payment_type": "bank_transfer",
        },
    )
    assert webhook_response.status_code == 200

    paid_status_response = client.get(f"/api/chatbot/orders/{data['order_number']}")
    assert paid_status_response.status_code == 200
    paid_status_data = paid_status_response.json()
    assert paid_status_data["order_status"] == "paid"
    assert paid_status_data["payment_status"] == "paid"

    cleanup_phone(phone)
    cleanup_product(slug)

def test_chatbot_can_check_order_status_from_order_number_message() -> None:
    from app.api.chatbot_api import get_midtrans_client

    phone = f"62825{uuid4().hex[:10]}"
    slug = f"chat-order-status-product-{uuid4().hex}"
    cleanup_phone(phone)
    create_active_product(slug)
    app.dependency_overrides[get_midtrans_client] = lambda: FakeMidtransClient()

    checkout_response = client.post(
        "/api/chatbot/checkout",
        json={
            "phone": phone,
            "recipient_name": "Buyer Test",
            "recipient_phone": phone,
            "address_line": "Jl Test No 1",
            "city": "Surabaya",
            "postal_code": "60111",
            "items": [{"slug": slug, "quantity": 1}],
            "shipping_cost": "10000",
        },
    )
    order_number = checkout_response.json()["order_number"]

    first_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": f"Cek pesanan {order_number}"},
    )
    second_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": order_number},
    )
    third_response = client.post(
        "/api/chatbot/message",
        json={"phone": phone, "message": f"cek order {order_number}"},
    )

    app.dependency_overrides.clear()
    assert checkout_response.status_code == 201
    for response in [first_response, second_response, third_response]:
        assert response.status_code == 200
        assert response.json()["intent"] == "order_status"
        assert order_number in response.json()["reply"]
        assert "waiting_payment" in response.json()["reply"]
        assert "https://pay.example.test/" in response.json()["reply"]

    cleanup_phone(phone)
    cleanup_product(slug)
