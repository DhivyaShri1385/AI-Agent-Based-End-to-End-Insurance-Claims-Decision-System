import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User, UserRole
from tests.conftest import DEFAULT_PASSWORD


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_register_creates_policyholder_and_returns_token(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "New.User@Example.com", "full_name": "New User", "password": DEFAULT_PASSWORD},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "POLICYHOLDER"
    assert body["user"]["email"] == "new.user@example.com"
    assert "hashed_password" not in body["user"]
    assert client.get("/api/auth/me", headers=_bearer(body["access_token"])).status_code == 200


def test_register_ignores_client_supplied_role(client):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "sneaky@example.com",
            "full_name": "Sneaky User",
            "password": DEFAULT_PASSWORD,
            "role": "ADMIN",
        },
    )
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "POLICYHOLDER"


def test_register_duplicate_email_conflicts_case_insensitively(client):
    payload = {"email": "dup@example.com", "full_name": "Dup User", "password": DEFAULT_PASSWORD}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    payload["email"] = "DUP@example.com"
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_register_rejects_weak_password_without_echoing_it(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "weak@example.com", "full_name": "Weak User", "password": "onlyletters"},
    )
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["message"] == "Validation failed"
    assert any(d["field"] == "password" for d in body["error"]["details"])
    assert "onlyletters" not in r.text


def test_register_rejects_short_password(client):
    r = client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "full_name": "Short User", "password": "a1"},
    )
    assert r.status_code == 422


def test_password_is_stored_hashed(client, db_session):
    client.post(
        "/api/auth/register",
        json={"email": "hash@example.com", "full_name": "Hash User", "password": DEFAULT_PASSWORD},
    )
    user = db_session.query(User).filter_by(email="hash@example.com").one()
    assert user.hashed_password != DEFAULT_PASSWORD
    assert verify_password(DEFAULT_PASSWORD, user.hashed_password)


def test_login_success(client, make_user):
    make_user("login@example.com")
    r = client.post("/api/auth/login", json={"email": "LOGIN@example.com", "password": DEFAULT_PASSWORD})
    assert r.status_code == 200
    assert r.json()["user"]["email"] == "login@example.com"


def test_login_wrong_password(client, make_user):
    make_user("wrong@example.com")
    r = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "WrongPassw0rd"})
    assert r.status_code == 401
    assert r.json()["error"]["message"] == "Invalid email or password"


def test_login_unknown_email_gives_same_error(client):
    r = client.post("/api/auth/login", json={"email": "ghost@example.com", "password": DEFAULT_PASSWORD})
    assert r.status_code == 401
    assert r.json()["error"]["message"] == "Invalid email or password"


def test_login_inactive_account_is_forbidden(client, make_user):
    make_user("inactive@example.com", is_active=False)
    r = client.post("/api/auth/login", json={"email": "inactive@example.com", "password": DEFAULT_PASSWORD})
    assert r.status_code == 403


def test_me_requires_token_and_uses_error_envelope(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
    assert r.json()["error"]["code"] == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_me_returns_current_user(client, make_user, auth_headers):
    make_user("me@example.com", role=UserRole.ADJUSTER)
    r = client.get("/api/auth/me", headers=auth_headers("me@example.com"))
    assert r.status_code == 200
    assert r.json()["role"] == "ADJUSTER"


def test_expired_token_rejected(client, make_user):
    user = make_user("expired@example.com")
    token = create_access_token(user.id, "POLICYHOLDER", expires_delta=timedelta(seconds=-5))
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 401


def test_token_signed_with_wrong_key_rejected(client, make_user):
    user = make_user("forged@example.com")
    forged = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "a-completely-different-secret-key-of-32-plus-chars",
        algorithm="HS256",
    )
    assert client.get("/api/auth/me", headers=_bearer(forged)).status_code == 401


def test_unsigned_alg_none_token_rejected(client, make_user):
    user = make_user("none@example.com")
    unsigned = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        None,
        algorithm="none",
    )
    assert client.get("/api/auth/me", headers=_bearer(unsigned)).status_code == 401


def test_token_for_unknown_user_rejected(client):
    token = create_access_token(uuid.uuid4(), "ADMIN")
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 401


def test_valid_token_of_inactive_user_rejected(client, make_user):
    user = make_user("disabled@example.com", is_active=False)
    token = create_access_token(user.id, "POLICYHOLDER")
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 403
    assert settings.jwt_algorithm == "HS256"
