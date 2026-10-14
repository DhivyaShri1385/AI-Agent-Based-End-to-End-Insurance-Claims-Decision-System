"""User account model."""
import enum

from sqlalchemy import Boolean, Enum, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, enum.Enum):
    POLICYHOLDER = "POLICYHOLDER"
    ADJUSTER = "ADJUSTER"
    ADMIN = "ADMIN"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False, length=20),
        nullable=False,
        default=UserRole.POLICYHOLDER,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    policies: Mapped[list["Policy"]] = relationship(back_populates="holder")  # noqa: F821
