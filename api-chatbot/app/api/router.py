from fastapi import APIRouter

from app.api.auth_api import router as auth_router
from app.api.product_api import router as product_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(product_router)
