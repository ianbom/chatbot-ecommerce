from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schemas import AuthResponse, RegisterRequest
from app.modules.users.models import User


def register_user(session: Session, payload: RegisterRequest) -> AuthResponse | None:
    existing_user = session.scalar(select(User).where(User.email == str(payload.email)))
    if existing_user is not None:
        return None

    user = User(
        name=payload.name,
        email=str(payload.email),
        password=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _auth_response(user)


def authenticate_user(session: Session, email: str, password: str) -> AuthResponse | None:
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password):
        return None

    user.last_login_at = datetime.now(UTC)
    session.commit()
    session.refresh(user)
    return _auth_response(user)


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(str(user.id)), user=user)
