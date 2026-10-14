"""Shared fixtures: isolated in-memory database per test, user/policy factories."""
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.policy import (
    InsuranceType,
    Policy,
    PolicyCoverageRule,
    PolicyStatus,
    RuleType,
)
from app.models.user import User, UserRole

DEFAULT_PASSWORD = "Passw0rdTest"


@pytest.fixture(autouse=True)
def _fast_bcrypt(monkeypatch):
    monkeypatch.setattr(settings, "bcrypt_rounds", 4)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def make_user(db_session):
    def _make(
        email="user@example.com",
        role=UserRole.POLICYHOLDER,
        password=DEFAULT_PASSWORD,
        full_name="Test User",
        is_active=True,
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        return user

    return _make


@pytest.fixture()
def auth_headers(client):
    def _headers(email: str, password: str = DEFAULT_PASSWORD) -> dict[str, str]:
        response = client.post("/api/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _headers


@pytest.fixture()
def make_policy(db_session):
    def _make(
        holder: User,
        policy_number="CIQ-ACC-9001",
        insurance_type=InsuranceType.ACCIDENT,
        with_rules=True,
    ) -> Policy:
        policy = Policy(
            policy_number=policy_number,
            holder_id=holder.id,
            insurance_type=insurance_type,
            status=PolicyStatus.ACTIVE,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            coverage_limit=Decimal("500000.00"),
            deductible=Decimal("5000.00"),
            copay_percent=Decimal("10.00"),
            waiting_period_days=30,
        )
        if with_rules:
            policy.rules = [
                PolicyCoverageRule(
                    claim_category="ACCIDENT_HOSPITALIZATION",
                    rule_type=RuleType.COVERAGE,
                    clause_reference="ACC-3.1",
                    description="Synthetic coverage clause.",
                    sub_limit=Decimal("300000.00"),
                ),
                PolicyCoverageRule(
                    claim_category="ACCIDENT_HOSPITALIZATION",
                    rule_type=RuleType.EXCLUSION,
                    clause_reference="ACC-7.2",
                    description="Synthetic exclusion clause.",
                    sub_limit=None,
                ),
            ]
        db_session.add(policy)
        db_session.commit()
        return policy

    return _make
