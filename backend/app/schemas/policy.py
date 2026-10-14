"""Policy schemas. Decimal values serialize to JSON strings (e.g. "500000.00")."""
import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.policy import InsuranceType, PolicyStatus, RuleType


class PolicyRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    claim_category: str
    rule_type: RuleType
    clause_reference: str
    description: str
    sub_limit: Decimal | None


class PolicySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    policy_number: str
    holder_id: uuid.UUID
    insurance_type: InsuranceType
    status: PolicyStatus
    start_date: date
    end_date: date
    coverage_limit: Decimal
    deductible: Decimal
    copay_percent: Decimal
    waiting_period_days: int


class PolicyDetail(PolicySummary):
    rules: list[PolicyRuleOut]


class PolicyListResponse(BaseModel):
    items: list[PolicySummary]
    total: int
    page: int
    page_size: int
