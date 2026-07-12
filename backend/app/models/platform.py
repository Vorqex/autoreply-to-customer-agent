from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlatformConnection(Base):
    __tablename__ = "platform_connections"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    encrypted_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    encrypted_refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scopes: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True, default=list
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    platform_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
