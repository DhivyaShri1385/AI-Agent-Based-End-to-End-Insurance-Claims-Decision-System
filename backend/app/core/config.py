"""Application configuration loaded from environment variables / .env file."""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEV_SECRET = "dev-only-insecure-secret-change-me-before-any-real-use"


class Settings(BaseSettings):
    app_name: str = "ClaimIQ"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = "sqlite:///./claimiq.db"

    # Stored as a plain comma-separated string to keep .env editing simple on Windows.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Authentication
    secret_key: str = DEFAULT_DEV_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    bcrypt_rounds: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_security_settings(self) -> "Settings":
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if self.environment != "development" and self.secret_key == DEFAULT_DEV_SECRET:
            raise ValueError("SECRET_KEY must be changed from the default outside development")
        if not 4 <= self.bcrypt_rounds <= 18:
            raise ValueError("BCRYPT_ROUNDS must be between 4 and 18")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
