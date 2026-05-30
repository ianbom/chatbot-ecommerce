from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest
from app.controller import auth_controller
from app.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: SessionDep) -> AuthResponse:
    return auth_controller.register(payload, session)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, session: SessionDep) -> AuthResponse:
    return auth_controller.login(payload, session)

