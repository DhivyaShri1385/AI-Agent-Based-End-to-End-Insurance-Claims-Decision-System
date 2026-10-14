import uuid

from app.models.user import UserRole


def test_policies_require_authentication(client):
    assert client.get("/api/policies").status_code == 401


def test_policyholder_sees_only_own_policies(client, make_user, make_policy, auth_headers):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    make_policy(alice, "CIQ-ACC-0001")
    make_policy(bob, "CIQ-ACC-0002")

    r = client.get("/api/policies", headers=auth_headers("alice@example.com"))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["policy_number"] == "CIQ-ACC-0001"
    assert body["items"][0]["coverage_limit"] == "500000.00"


def test_adjuster_sees_all_policies(client, make_user, make_policy, auth_headers):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    make_user("adj@example.com", role=UserRole.ADJUSTER)
    make_policy(alice, "CIQ-ACC-0001")
    make_policy(bob, "CIQ-ACC-0002")

    r = client.get("/api/policies", headers=auth_headers("adj@example.com"))
    assert r.json()["total"] == 2


def test_pagination(client, make_user, make_policy, auth_headers):
    alice = make_user("alice@example.com")
    for i in range(3):
        make_policy(alice, f"CIQ-ACC-000{i}")
    headers = auth_headers("alice@example.com")

    first = client.get("/api/policies?page=1&page_size=2", headers=headers).json()
    second = client.get("/api/policies?page=2&page_size=2", headers=headers).json()
    assert first["total"] == 3 and len(first["items"]) == 2
    assert len(second["items"]) == 1


def test_invalid_page_size_rejected(client, make_user, auth_headers):
    make_user("alice@example.com")
    r = client.get("/api/policies?page_size=1000", headers=auth_headers("alice@example.com"))
    assert r.status_code == 422


def test_policy_detail_includes_rules(client, make_user, make_policy, auth_headers):
    alice = make_user("alice@example.com")
    policy = make_policy(alice)
    r = client.get(f"/api/policies/{policy.id}", headers=auth_headers("alice@example.com"))
    assert r.status_code == 200
    clauses = [rule["clause_reference"] for rule in r.json()["rules"]]
    assert clauses == ["ACC-3.1", "ACC-7.2"]


def test_policyholder_cannot_view_another_holders_policy(client, make_user, make_policy, auth_headers):
    make_user("alice@example.com")
    bob = make_user("bob@example.com")
    bobs_policy = make_policy(bob)
    r = client.get(f"/api/policies/{bobs_policy.id}", headers=auth_headers("alice@example.com"))
    assert r.status_code == 404


def test_adjuster_can_view_any_policy(client, make_user, make_policy, auth_headers):
    bob = make_user("bob@example.com")
    make_user("adj@example.com", role=UserRole.ADJUSTER)
    policy = make_policy(bob)
    r = client.get(f"/api/policies/{policy.id}", headers=auth_headers("adj@example.com"))
    assert r.status_code == 200


def test_invalid_policy_id_rejected(client, make_user, auth_headers):
    make_user("alice@example.com")
    r = client.get("/api/policies/not-a-uuid", headers=auth_headers("alice@example.com"))
    assert r.status_code == 422


def test_unknown_policy_is_404(client, make_user, auth_headers):
    make_user("alice@example.com")
    r = client.get(f"/api/policies/{uuid.uuid4()}", headers=auth_headers("alice@example.com"))
    assert r.status_code == 404
