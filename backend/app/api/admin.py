"""Admin endpoints. Every route on this router requires the ADMIN role."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.auth import AdminCreateUserRequest, UserListResponse, UserOut

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)


@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> UserListResponse:
    total = db.scalar(select(func.count()).select_from(User)) or 0
    items = db.scalars(
        select(User)
        .order_by(User.created_at.desc(), User.email)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return UserListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: AdminCreateUserRequest, db: Session = Depends(get_db)) -> User:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "An account with this email already exists"
        ) from None
    db.refresh(user)
    logger.info("Admin created user: id=%s role=%s", user.id, user.role.value)
    return user
