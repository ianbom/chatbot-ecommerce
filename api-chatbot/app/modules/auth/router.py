from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest
from app.modules.auth.service import authenticate_user, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: SessionDep) -> AuthResponse:
    auth_response = register_user(session, payload)
    if auth_response is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return auth_response


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, session: SessionDep) -> AuthResponse:
    auth_response = authenticate_user(session, str(payload.email), payload.password)
    if auth_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return auth_response
