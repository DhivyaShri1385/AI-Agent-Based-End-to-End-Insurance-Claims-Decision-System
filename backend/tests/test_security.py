import uuid
from datetime import timedelta

import pytest

from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("Passw0rdTest")
    assert hashed != "Passw0rdTest"
    assert verify_password("Passw0rdTest", hashed) is True
    assert verify_password("WrongPassw0rd", hashed) is False


def test_hash_rejects_passwords_over_72_bytes():
    with pytest.raises(ValueError):
        hash_password("a1" * 40)


def test_verify_handles_malformed_hash_and_oversized_input():
    assert verify_password("Passw0rdTest", "not-a-bcrypt-hash") is False
    assert verify_password("a1" * 40, hash_password("Passw0rdTest")) is False


def test_token_roundtrip():
    user_id = uuid.uuid4()
    token = create_access_token(user_id, "ADJUSTER")
    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADJUSTER"


def test_decode_rejects_garbage_and_expired_tokens():
    with pytest.raises(TokenError):
        decode_access_token("not.a.jwt")
    expired = create_access_token(uuid.uuid4(), "ADMIN", expires_delta=timedelta(seconds=-5))
    with pytest.raises(TokenError):
        decode_access_token(expired)
