from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.modules.users.models import User

client = TestClient(app)


def cleanup_user(email: str) -> None:
    with SessionLocal() as session:
        session.execute(delete(User).where(User.email == email))
        session.commit()


def test_register_creates_user_and_returns_access_token() -> None:
    email = f"new-user-{uuid4().hex}@example.com"
    cleanup_user(email)

    response = client.post(
        "/api/auth/register",
        json={"name": "New User", "email": email, "password": "secret12345"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == email
    assert data["user"]["name"] == "New User"
    assert data["user"]["role"] == "admin"

    with SessionLocal() as session:
        user = session.query(User).filter(User.email == email).one()
        assert user.password != "secret12345"
        assert user.password.startswith("pbkdf2_sha256$")

    cleanup_user(email)


def test_login_accepts_email_and_password_only() -> None:
    email = f"login-user-{uuid4().hex}@example.com"
    cleanup_user(email)
    register_response = client.post(
        "/api/auth/register",
        json={"name": "Login User", "email": email, "password": "secret12345"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "secret12345"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == email

    cleanup_user(email)


def test_login_rejects_wrong_password() -> None:
    email = f"wrong-password-{uuid4().hex}@example.com"
    cleanup_user(email)
    register_response = client.post(
        "/api/auth/register",
        json={"name": "Wrong Password", "email": email, "password": "secret12345"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "bad-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

    cleanup_user(email)


def test_register_rejects_duplicate_email() -> None:
    email = f"duplicate-{uuid4().hex}@example.com"
    cleanup_user(email)
    first_response = client.post(
        "/api/auth/register",
        json={"name": "Duplicate", "email": email, "password": "secret12345"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/auth/register",
        json={"name": "Duplicate", "email": email, "password": "secret12345"},
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"

    cleanup_user(email)
