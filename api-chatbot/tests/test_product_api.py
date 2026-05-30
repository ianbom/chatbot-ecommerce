from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.model.product import Product

client = TestClient(app)


def cleanup_product(slug: str) -> None:
    with SessionLocal() as session:
        session.execute(delete(Product).where(Product.slug == slug))
        session.commit()


class FakeEmbeddingProvider:
    def __init__(self) -> None:
        self.texts: list[str] = []

    def embed_product(self, text: str) -> list[float]:
        self.texts.append(text)
        return [0.1] * 1024


def test_create_product_generates_embedding_from_all_product_columns_and_persists_product() -> None:
    from app.api.product_api import get_embedding_provider

    slug = f"hoodie-black-l-{uuid4().hex}"
    fake_embedding_provider = FakeEmbeddingProvider()
    cleanup_product(slug)
    app.dependency_overrides[get_embedding_provider] = lambda: fake_embedding_provider

    response = client.post(
        "/api/products",
        json={
            "name": "Hoodie Black L",
            "slug": slug,
            "description": "Hoodie oversized warna hitam ukuran L",
            "image_url": "https://drive.google.com/file/d/example/view",
            "price": "249000",
            "stock_qty": 8,
            "reserved_qty": 0,
            "color": "black",
            "size": "L",
            "gender": "unisex",
            "material": "cotton fleece",
            "weight_gram": 600,
            "length_cm": "70.50",
            "width_cm": "55.00",
            "height_cm": "3.00",
            "status": "active",
            "is_featured": True,
            "created_by": None,
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == slug
    assert data["image_url"] == "https://drive.google.com/file/d/example/view"
    assert data["price"] == "249000.00"
    assert data["embedding_dimensions"] == 1024

    embedding_text = fake_embedding_provider.texts[0]
    for column in [
        "name",
        "slug",
        "description",
        "image_url",
        "price",
        "stock_qty",
        "reserved_qty",
        "color",
        "size",
        "gender",
        "material",
        "weight_gram",
        "length_cm",
        "width_cm",
        "height_cm",
        "status",
        "is_featured",
        "created_by",
    ]:
        assert f"{column}:" in embedding_text

    with SessionLocal() as session:
        product = session.scalar(select(Product).where(Product.slug == slug))
        assert product is not None
        assert product.name == "Hoodie Black L"
        assert product.price == Decimal("249000.00")
        assert product.embedding is not None
        assert len(product.embedding) == 1024

    cleanup_product(slug)


def test_create_product_rejects_duplicate_slug() -> None:
    from app.api.product_api import get_embedding_provider

    slug = f"duplicate-product-{uuid4().hex}"
    cleanup_product(slug)
    app.dependency_overrides[get_embedding_provider] = lambda: FakeEmbeddingProvider()
    payload = {
        "name": "Hoodie Black L",
        "slug": slug,
        "price": "249000",
    }
    first_response = client.post("/api/products", json=payload)
    second_response = client.post("/api/products", json=payload)

    app.dependency_overrides.clear()
    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Product slug already exists"

    cleanup_product(slug)
