from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.auth_schema import AuthResponse, LoginRequest, RegisterRequest
from app.service.auth_service import authenticate_user, register_user


def register(payload: RegisterRequest, session: Session) -> AuthResponse:
    auth_response = register_user(session, payload)
    if auth_response is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    return auth_response


def login(payload: LoginRequest, session: Session) -> AuthResponse:
    auth_response = authenticate_user(session, str(payload.email), payload.password)
    if auth_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return auth_response

