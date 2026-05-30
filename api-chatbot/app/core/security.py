from datetime import UTC, datetime, timedelta
import base64
import hashlib
import hmac
import json
import secrets

from app.core.config import get_settings

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS
    ).hex()
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = hashed_password.split("$", 3)
    except ValueError:
        return False

    if algorithm != PASSWORD_ALGORITHM:
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations)
    ).hex()
    return hmac.compare_digest(actual_hash, expected_hash)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    payload = {"sub": subject, "exp": int(expires_at.timestamp())}
    signing_input = f"{_b64_json(header)}.{_b64_json(payload)}"
    signature = hmac.new(
        settings.jwt_secret.get_secret_value().encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64_bytes(signature)}"


def _b64_json(value: dict) -> str:
    return _b64_bytes(json.dumps(value, separators=(",", ":")).encode("utf-8"))


def _b64_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

