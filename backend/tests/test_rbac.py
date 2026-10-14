from app.models.user import UserRole
from tests.conftest import DEFAULT_PASSWORD


def test_policyholder_cannot_list_users(client, make_user, auth_headers):
    make_user("ph@example.com", role=UserRole.POLICYHOLDER)
    assert client.get("/api/admin/users", headers=auth_headers("ph@example.com")).status_code == 403


def test_adjuster_cannot_list_users(client, make_user, auth_headers):
    make_user("adj@example.com", role=UserRole.ADJUSTER)
    assert client.get("/api/admin/users", headers=auth_headers("adj@example.com")).status_code == 403


def test_unauthenticated_admin_access_is_401(client):
    assert client.get("/api/admin/users").status_code == 401


def test_admin_can_list_users(client, make_user, auth_headers):
    make_user("admin@example.com", role=UserRole.ADMIN)
    make_user("other@example.com")
    r = client.get("/api/admin/users", headers=auth_headers("admin@example.com"))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert all("hashed_password" not in item for item in body["items"])


def test_admin_creates_adjuster_who_can_log_in(client, make_user, auth_headers):
    make_user("admin@example.com", role=UserRole.ADMIN)
    r = client.post(
        "/api/admin/users",
        headers=auth_headers("admin@example.com"),
        json={
            "email": "new.adjuster@example.com",
            "full_name": "New Adjuster",
            "password": DEFAULT_PASSWORD,
            "role": "ADJUSTER",
        },
    )
    assert r.status_code == 201
    assert r.json()["role"] == "ADJUSTER"
    login = client.post(
        "/api/auth/login",
        json={"email": "new.adjuster@example.com", "password": DEFAULT_PASSWORD},
    )
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "ADJUSTER"


def test_policyholder_cannot_create_users(client, make_user, auth_headers):
    make_user("ph@example.com")
    r = client.post(
        "/api/admin/users",
        headers=auth_headers("ph@example.com"),
        json={
            "email": "evil@example.com",
            "full_name": "Evil Admin",
            "password": DEFAULT_PASSWORD,
            "role": "ADMIN",
        },
    )
    assert r.status_code == 403


def test_admin_create_duplicate_email_conflicts(client, make_user, auth_headers):
    make_user("admin@example.com", role=UserRole.ADMIN)
    make_user("taken@example.com")
    r = client.post(
        "/api/admin/users",
        headers=auth_headers("admin@example.com"),
        json={
            "email": "taken@example.com",
            "full_name": "Taken User",
            "password": DEFAULT_PASSWORD,
            "role": "ADJUSTER",
        },
    )
    assert r.status_code == 409


def test_role_change_applies_to_existing_token(client, db_session, make_user, auth_headers):
    user = make_user("promoted@example.com")
    headers = auth_headers("promoted@example.com")
    assert client.get("/api/admin/users", headers=headers).status_code == 403

    user.role = UserRole.ADMIN
    db_session.commit()

    assert client.get("/api/admin/users", headers=headers).status_code == 200
