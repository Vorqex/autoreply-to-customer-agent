from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.utils.helpers import now


class BrandVoice(Base):
    __tablename__ = "brand_voices"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    business_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tone: Mapped[str] = mapped_column(String(50), nullable=False, default="professional")
    style: Mapped[str] = mapped_column(String(50), nullable=False, default="formal")
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    personality: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    values: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    keywords: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    forbidden_terms: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    custom_rules: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    greeting_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closing_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sample_replies: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, onupdate=now
    )
