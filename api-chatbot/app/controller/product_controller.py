from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.product_schema import ProductCreateRequest, ProductResponse
from app.service.embedding_service import EmbeddingProvider
from app.service.product_service import create_product


def store(
    payload: ProductCreateRequest,
    session: Session,
    embedding_provider: EmbeddingProvider,
) -> ProductResponse:
    try:
        product = create_product(session, payload, embedding_provider)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product slug already exists",
        )
    return product
