from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controller import product_controller
from app.db.session import get_db
from app.schemas.product_schema import ProductCreateRequest, ProductResponse
from app.service.embedding_service import EmbeddingProvider, OllamaProductEmbeddingProvider

router = APIRouter(prefix="/api/products", tags=["products"])
SessionDep = Annotated[Session, Depends(get_db)]


def get_embedding_provider() -> EmbeddingProvider:
    return OllamaProductEmbeddingProvider()


EmbeddingDep = Annotated[EmbeddingProvider, Depends(get_embedding_provider)]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreateRequest,
    session: SessionDep,
    embedding_provider: EmbeddingDep,
) -> ProductResponse:
    return product_controller.store(payload, session, embedding_provider)
