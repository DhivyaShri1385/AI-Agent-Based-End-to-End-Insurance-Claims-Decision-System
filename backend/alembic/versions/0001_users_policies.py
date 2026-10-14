"""users, policies, policy_coverage_rules

Revision ID: 0001
Revises:
Create Date: 2026-10-13
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("POLICYHOLDER", "ADJUSTER", "ADMIN", name="userrole", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "policies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("policy_number", sa.String(30), nullable=False),
        sa.Column("holder_id", sa.Uuid(), nullable=False),
        sa.Column(
            "insurance_type",
            sa.Enum("HEALTH", "ACCIDENT", "THEFT", name="insurancetype", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE", "EXPIRED", "CANCELLED", "SUSPENDED",
                name="policystatus", native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("coverage_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("deductible", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("copay_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("waiting_period_days", sa.Integer(), nullable=False, server_default="0"),
        *_timestamps(),
        sa.ForeignKeyConstraint(["holder_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("end_date > start_date", name="ck_policies_date_order"),
        sa.CheckConstraint("copay_percent >= 0 AND copay_percent <= 100", name="ck_policies_copay_range"),
    )
    op.create_index("ix_policies_policy_number", "policies", ["policy_number"], unique=True)
    op.create_index("ix_policies_holder_id", "policies", ["holder_id"])

    op.create_table(
        "policy_coverage_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("policy_id", sa.Uuid(), nullable=False),
        sa.Column("claim_category", sa.String(50), nullable=False),
        sa.Column(
            "rule_type",
            sa.Enum("COVERAGE", "EXCLUSION", name="ruletype", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("clause_reference", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sub_limit", sa.Numeric(14, 2), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("policy_id", "clause_reference", name="uq_rule_policy_clause"),
    )
    op.create_index(
        "ix_policy_coverage_rules_policy_id", "policy_coverage_rules", ["policy_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_policy_coverage_rules_policy_id", table_name="policy_coverage_rules")
    op.drop_table("policy_coverage_rules")
    op.drop_index("ix_policies_holder_id", table_name="policies")
    op.drop_index("ix_policies_policy_number", table_name="policies")
    op.drop_table("policies")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
