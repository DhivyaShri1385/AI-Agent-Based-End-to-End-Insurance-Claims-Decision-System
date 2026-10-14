"""Policy endpoints. Policyholders only ever see their own policies."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.policy import Policy
from app.models.user import User, UserRole
from app.schemas.policy import PolicyDetail, PolicyListResponse

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=PolicyListResponse)
def list_policies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PolicyListResponse:
    stmt = select(Policy)
    count_stmt = select(func.count()).select_from(Policy)
    if user.role == UserRole.POLICYHOLDER:
        stmt = stmt.where(Policy.holder_id == user.id)
        count_stmt = count_stmt.where(Policy.holder_id == user.id)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(Policy.created_at.desc(), Policy.policy_number)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PolicyListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{policy_id}", response_model=PolicyDetail)
def get_policy(
    policy_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Policy:
    policy = db.scalar(
        select(Policy).options(selectinload(Policy.rules)).where(Policy.id == policy_id)
    )
    # 404 (not 403) for other people's policies, so existence is not revealed.
    if policy is None or (
        user.role == UserRole.POLICYHOLDER and policy.holder_id != user.id
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Policy not found")
    return policy
