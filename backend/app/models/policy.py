"""Insurance policy and coverage rule models (synthetic demo data only)."""
import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class InsuranceType(str, enum.Enum):
    HEALTH = "HEALTH"
    ACCIDENT = "ACCIDENT"
    THEFT = "THEFT"


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    SUSPENDED = "SUSPENDED"


class RuleType(str, enum.Enum):
    COVERAGE = "COVERAGE"
    EXCLUSION = "EXCLUSION"


class Policy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "policies"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_policies_date_order"),
        CheckConstraint("copay_percent >= 0 AND copay_percent <= 100", name="ck_policies_copay_range"),
    )

    policy_number: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    holder_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    insurance_type: Mapped[InsuranceType] = mapped_column(
        Enum(InsuranceType, native_enum=False, length=20), nullable=False
    )
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, native_enum=False, length=20), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    coverage_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    deductible: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    copay_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    waiting_period_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    holder: Mapped["User"] = relationship(back_populates="policies")  # noqa: F821
    rules: Mapped[list["PolicyCoverageRule"]] = relationship(
        back_populates="policy",
        cascade="all, delete-orphan",
        order_by="PolicyCoverageRule.clause_reference",
    )


class PolicyCoverageRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "policy_coverage_rules"
    __table_args__ = (
        UniqueConstraint("policy_id", "clause_reference", name="uq_rule_policy_clause"),
    )

    policy_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("policies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Policy-pack key, e.g. "ACCIDENT_HOSPITALIZATION"
    claim_category: Mapped[str] = mapped_column(String(50), nullable=False)
    rule_type: Mapped[RuleType] = mapped_column(
        Enum(RuleType, native_enum=False, length=20), nullable=False
    )
    clause_reference: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sub_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    policy: Mapped[Policy] = relationship(back_populates="rules")
