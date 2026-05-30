from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.product import Product
from app.schemas.product_schema import ProductCreateRequest, ProductResponse
from app.service.embedding_service import EmbeddingProvider


def create_product(
    session: Session,
    payload: ProductCreateRequest,
    embedding_provider: EmbeddingProvider,
) -> ProductResponse | None:
    existing_product = session.scalar(select(Product).where(Product.slug == payload.slug))
    if existing_product is not None:
        return None

    embedding_text = build_product_embedding_text(payload)
    embedding = embedding_provider.embed_product(embedding_text)
    product = Product(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        embedding=embedding,
        image_url=payload.image_url,
        price=payload.price,
        stock_qty=payload.stock_qty,
        reserved_qty=payload.reserved_qty,
        color=payload.color,
        size=payload.size,
        gender=payload.gender,
        material=payload.material,
        weight_gram=payload.weight_gram,
        length_cm=payload.length_cm,
        width_cm=payload.width_cm,
        height_cm=payload.height_cm,
        status=payload.status,
        is_featured=payload.is_featured,
        created_by=payload.created_by,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product_to_response(product)


def build_product_embedding_text(payload: ProductCreateRequest) -> str:
    data = payload.model_dump(mode="json")
    return "\n".join(f"{key}: {value}" for key, value in data.items())


def product_to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        image_url=product.image_url,
        price=product.price,
        stock_qty=product.stock_qty,
        reserved_qty=product.reserved_qty,
        color=product.color,
        size=product.size,
        gender=product.gender,
        material=product.material,
        weight_gram=product.weight_gram,
        length_cm=product.length_cm,
        width_cm=product.width_cm,
        height_cm=product.height_cm,
        status=product.status,
        is_featured=product.is_featured,
        created_by=product.created_by,
        embedding_dimensions=0 if product.embedding is None else len(product.embedding),
    )

