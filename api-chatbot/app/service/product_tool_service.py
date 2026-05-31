from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.enums import ProductStatus
from app.model.product import Product
from app.service.embedding_service import OllamaProductEmbeddingProvider


def find_active_products_for_message(session: Session, message: str, limit: int = 5) -> list[Product]:
    keyword_products = find_active_products_by_keywords(session, message, limit)
    vector_products = find_active_products_by_embedding(session, message, limit)
    products_by_id: dict[int, Product] = {}
    product_signatures: set[tuple[str, str | None, str | None, str]] = set()
    for product in [*keyword_products, *vector_products]:
        signature = (product.name.lower(), product.color, product.size, f"{product.price:.2f}")
        if signature in product_signatures:
            continue
        product_signatures.add(signature)
        products_by_id.setdefault(product.id, product)
        if len(products_by_id) >= limit:
            break
    return list(products_by_id.values())


def find_active_product_by_id(session: Session, product_id: int | None) -> Product | None:
    if product_id is None:
        return None
    return session.scalar(
        select(Product).where(Product.id == product_id).where(Product.status == ProductStatus.active)
    )


def find_best_active_product(session: Session, message: str) -> Product | None:
    products = find_active_products_for_message(session, message, limit=1)
    return products[0] if products else None


def find_active_products_by_embedding(session: Session, message: str, limit: int = 5) -> list[Product]:
    try:
        embedding = OllamaProductEmbeddingProvider().embed_product(message)
        return list(
            session.scalars(
                select(Product)
                .where(Product.status == ProductStatus.active)
                .where(Product.embedding.is_not(None))
                .order_by(Product.embedding.cosine_distance(embedding))
                .limit(limit)
            )
        )
    except Exception:
        return []


def find_active_products_by_keywords(session: Session, message: str, limit: int = 5) -> list[Product]:
    products = list(
        session.scalars(
            select(Product)
            .where(Product.status == ProductStatus.active)
            .order_by(Product.is_featured.desc(), Product.created_at.desc(), Product.id.desc())
            .limit(25)
        )
    )
    terms = {term for term in message.lower().replace("?", " ").split() if len(term) > 2}
    scored: list[tuple[int, int, Product]] = []
    for product in products:
        haystack = " ".join(
            str(value or "")
            for value in [
                product.name,
                product.slug,
                product.description,
                product.color,
                product.size,
                product.gender,
                product.material,
            ]
        ).lower()
        score = sum(1 for term in terms if term in haystack)
        available_stock = max(product.stock_qty - product.reserved_qty, 0)
        scored.append((score, available_stock, product))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    matches = [product for score, _available_stock, product in scored if score > 0]
    return (matches or products)[:limit]


def format_product_answer(products: list[Product]) -> str:
    if not products:
        return "Belum ada produk aktif yang bisa saya tampilkan sekarang."

    lines = ["Produk yang tersedia:"]
    for product in products:
        available_stock = max(product.stock_qty - product.reserved_qty, 0)
        details = [
            product.name,
            f"harga Rp{format_rupiah(product.price)}",
            f"stok tersedia {available_stock}",
        ]
        if product.color:
            details.append(f"warna {product.color}")
        if product.size:
            details.append(f"ukuran {product.size}")
        lines.append(" - " + ", ".join(details))
    return "\n".join(lines)


def build_product_rag_answer(
    products: list[Product],
    message: str,
    llm_client,
    chat_history: str = "",
) -> str:
    fallback = format_product_answer(products)
    if llm_client is None or not products:
        return fallback

    prompt = build_product_rag_prompt(products, message, chat_history)
    try:
        answer = llm_client.generate(prompt).strip()
    except Exception:
        return fallback
    return answer or fallback


def build_product_rag_prompt(products: list[Product], message: str, chat_history: str = "") -> str:
    history_block = chat_history or "Belum ada riwayat chat sebelumnya."
    return (
        "Kamu adalah admin WhatsApp toko online. Jawab natural, ramah, singkat, dan variatif dalam Bahasa Indonesia.\n"
        "Gunakan hanya KONTEXT PRODUK di bawah. Jangan karang harga, stok, warna, ukuran, atau foto.\n"
        "Gunakan RIWAYAT CHAT untuk memahami kata seperti tadi, itu, yang sebelumnya, atau produk tersebut.\n"
        "Jangan tulis URL foto. Foto akan dikirim oleh sistem sebagai media WhatsApp.\n"
        "Kalau data tidak ada di konteks, bilang belum ada datanya dan tawarkan bantuan.\n\n"
        f"RIWAYAT CHAT:\n{history_block}\n\n"
        f"PERTANYAAN CUSTOMER:\n{message}\n\n"
        f"KONTEXT PRODUK:\n{build_product_context(products)}\n\n"
        "JAWABAN WHATSAPP:"
    )


def build_product_context(products: list[Product]) -> str:
    lines: list[str] = []
    for index, product in enumerate(products, start=1):
        available_stock = max(product.stock_qty - product.reserved_qty, 0)
        lines.append(
            "\n".join(
                [
                    f"Produk {index}:",
                    f"nama: {product.name}",
                    f"slug: {product.slug}",
                    f"deskripsi: {product.description or '-'}",
                    f"harga: Rp{format_rupiah(product.price)}",
                    f"stok tersedia: {available_stock}",
                    f"warna: {product.color or '-'}",
                    f"ukuran: {product.size or '-'}",
                    f"gender: {product.gender}",
                    f"material: {product.material or '-'}",
                    f"berat gram: {product.weight_gram}",
                    f"foto tersedia: {'ya' if product.image_url else 'tidak'}",
                ]
            )
        )
    return "\n\n".join(lines)


def product_image_messages(products: list[Product]) -> list[tuple[str, str]]:
    return [(product.image_url, product.name) for product in products if product.image_url]


def update_product_state_from_results(chat_session, products: list[Product], intent: str) -> None:
    if not products:
        return
    product = products[0]
    metadata = dict(chat_session.metadata_ or {})
    metadata.update(
        {
            "stage": "product_inquiry",
            "last_intent": intent,
            "current_product_id": product.id,
            "current_product_name": product.name,
            "current_variant": " ".join(value for value in [product.color, product.size] if value) or None,
        }
    )
    chat_session.metadata_ = metadata


def format_rupiah(value: Decimal) -> str:
    return f"{value:.0f}"
