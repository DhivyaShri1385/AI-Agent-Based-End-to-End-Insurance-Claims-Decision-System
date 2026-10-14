r"""Seed SYNTHETIC demo data. Idempotent: safe to run repeatedly.

Run from the backend directory (so .env and the SQLite path resolve correctly):
    cd backend
    python ..\scripts\seed_database.py
"""
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.policy import (  # noqa: E402
    InsuranceType,
    Policy,
    PolicyCoverageRule,
    PolicyStatus,
    RuleType,
)
from app.models.user import User, UserRole  # noqa: E402

DEMO_PASSWORD = "Demo@12345"  # synthetic demo accounts only

DEMO_USERS = [
    ("admin@example.com", "Demo Admin", UserRole.ADMIN),
    ("adjuster1@example.com", "Demo Adjuster One", UserRole.ADJUSTER),
    ("adjuster2@example.com", "Demo Adjuster Two", UserRole.ADJUSTER),
    ("alice@example.com", "Alice Demo", UserRole.POLICYHOLDER),
    ("bob@example.com", "Bob Demo", UserRole.POLICYHOLDER),
]

# Synthetic demo clauses. NOT real insurance wording.
ACCIDENT_RULES = [
    (RuleType.COVERAGE, "ACC-3.1", Decimal("300000.00"),
     "Reimbursement of in-patient hospitalization expenses arising from an accidental bodily injury."),
    (RuleType.EXCLUSION, "ACC-7.2", None,
     "Injuries that are intentionally self-inflicted are not covered."),
    (RuleType.EXCLUSION, "ACC-7.4", None,
     "Injuries sustained while under the influence of alcohol or non-prescribed drugs are not covered."),
    (RuleType.EXCLUSION, "ACC-7.6", None,
     "Cosmetic or elective procedures not required because of the accident are not covered."),
]

# (policy_number, holder_email, type, status, start, end, limit, deductible, copay %, waiting days)
DEMO_POLICIES = [
    ("CIQ-ACC-1001", "alice@example.com", InsuranceType.ACCIDENT, PolicyStatus.ACTIVE,
     date(2026, 1, 1), date(2026, 12, 31), "500000.00", "5000.00", "10.00", 30),
    ("CIQ-HLT-2001", "alice@example.com", InsuranceType.HEALTH, PolicyStatus.ACTIVE,
     date(2026, 1, 1), date(2026, 12, 31), "300000.00", "2000.00", "20.00", 30),
    ("CIQ-ACC-1002", "bob@example.com", InsuranceType.ACCIDENT, PolicyStatus.EXPIRED,
     date(2024, 1, 1), date(2024, 12, 31), "400000.00", "5000.00", "10.00", 30),
    ("CIQ-THF-3001", "bob@example.com", InsuranceType.THEFT, PolicyStatus.ACTIVE,
     date(2026, 1, 1), date(2026, 12, 31), "150000.00", "1000.00", "0.00", 0),
]


def main() -> None:
    if settings.environment != "development":
        sys.exit("Refusing to seed demo data outside ENVIRONMENT=development.")

    created_users = created_policies = 0
    with SessionLocal() as db:
        users: dict[str, User] = {}
        for email, full_name, role in DEMO_USERS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password=hash_password(DEMO_PASSWORD),
                    role=role,
                )
                db.add(user)
                created_users += 1
            users[email] = user
        db.flush()

        for (number, holder, itype, status, start, end, limit, ded, copay, wait) in DEMO_POLICIES:
            if db.scalar(select(Policy).where(Policy.policy_number == number)) is not None:
                continue
            policy = Policy(
                policy_number=number,
                holder_id=users[holder].id,
                insurance_type=itype,
                status=status,
                start_date=start,
                end_date=end,
                coverage_limit=Decimal(limit),
                deductible=Decimal(ded),
                copay_percent=Decimal(copay),
                waiting_period_days=wait,
            )
            # Only the ACCIDENT policy pack has demo rules. HEALTH and THEFT have none,
            # so later stages must answer NOT_SUPPORTED / HUMAN_REVIEW_REQUIRED for them.
            if itype == InsuranceType.ACCIDENT:
                policy.rules = [
                    PolicyCoverageRule(
                        claim_category="ACCIDENT_HOSPITALIZATION",
                        rule_type=rtype,
                        clause_reference=clause,
                        description=desc,
                        sub_limit=sub_limit,
                    )
                    for (rtype, clause, sub_limit, desc) in ACCIDENT_RULES
                ]
            db.add(policy)
            created_policies += 1
        db.commit()

    print(f"Seed complete: {created_users} users and {created_policies} policies created.")
    print(f"Demo password for all demo accounts: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
