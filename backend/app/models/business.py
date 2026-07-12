from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.utils.helpers import now

if TYPE_CHECKING:
    from app.models.user import User


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    plan: Mapped[str] = mapped_column(
        String(50), nullable=False, default="starter"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now, onupdate=now
    )

    users: Mapped[List["User"]] = relationship("User", back_populates="business")
