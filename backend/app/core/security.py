"""Password hashing and JWT helpers."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

MAX_PASSWORD_BYTES = 72  # bcrypt limit


class TokenError(Exception):
    """Raised when a JWT is missing claims, expired, malformed, or badly signed."""


def hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raise ValueError("Password must be at most 72 bytes")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode("ascii")


def verify_password(password: str, hashed_password: str) -> bool:
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(raw, hashed_password.encode("ascii"))
    except ValueError:  # malformed hash
        return False


# Verified against when the email is unknown, so unknown-email and wrong-password
# logins take similar time (limits account enumeration by timing).
DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-only")


def create_access_token(
    user_id: uuid.UUID, role: str, expires_delta: timedelta | None = None
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes)),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
