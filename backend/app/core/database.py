"""SQLAlchemy engine, session factory and declarative base."""
import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLite needs check_same_thread=False because FastAPI serves requests across threads.
_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all ORM models (models are added from Stage 2)."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection(db: Session) -> bool:
    """Return True if a trivial query succeeds. Never raises; logs the failure."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception("Database connectivity check failed")
        return False
