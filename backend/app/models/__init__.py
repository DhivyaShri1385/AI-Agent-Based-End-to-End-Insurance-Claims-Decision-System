"""Import all models so Base.metadata is complete (needed by Alembic and tests)."""
from app.models.policy import (
    InsuranceType,
    Policy,
    PolicyCoverageRule,
    PolicyStatus,
    RuleType,
)
from app.models.user import User, UserRole

__all__ = [
    "InsuranceType",
    "Policy",
    "PolicyCoverageRule",
    "PolicyStatus",
    "RuleType",
    "User",
    "UserRole",
]
