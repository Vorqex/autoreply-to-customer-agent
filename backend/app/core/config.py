from __future__ import annotations

from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "AutoReply AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/autoreply"
    REDIS_URL: str = ""
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    VECTOR_DB_TYPE: str = "pinecone"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "autoreply"
    QDRANT_URL: Optional[str] = None

    SENTRY_DSN: Optional[str] = None

    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    RATE_LIMIT: str = "100/minute"

    AI_QUALITY_THRESHOLD: float = 0.85
    SAFETY_SCORE_THRESHOLD: float = 0.90
    ENABLE_AUDIT_LOG: bool = True
    DEFAULT_TENANT_PLAN: str = "starter"

    @property
    def compute_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.CELERY_BROKER_URL:
            return self.CELERY_BROKER_URL
        return "redis://localhost:6379/0"


settings = Settings()
