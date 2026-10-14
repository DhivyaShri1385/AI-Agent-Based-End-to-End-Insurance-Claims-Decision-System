"""Health endpoint used by the frontend, Docker, and monitoring."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import check_database_connection, get_db

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded"
    app: str
    version: str
    environment: str
    database: str  # "connected" | "unavailable"
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
def health(response: Response, db: Session = Depends(get_db)) -> HealthResponse:
    db_ok = check_database_connection(db)
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        database="connected" if db_ok else "unavailable",
        timestamp=datetime.now(timezone.utc),
    )
