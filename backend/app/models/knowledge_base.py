from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.utils.helpers import now


class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base_entries"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        JSON, nullable=True
    )
    extra_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", JSON, nullable=True, default=dict
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, onupdate=now
    )
