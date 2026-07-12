from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.utils.helpers import now

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        business_id: UUID,
        user_id: Optional[UUID],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            id=uuid4(),
            business_id=business_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip,
            user_agent=user_agent,
        )
        self.db.add(log_entry)
        await self.db.flush()
        await self.db.refresh(log_entry)
        return log_entry

    async def get_logs(
        self,
        business_id: UUID,
        filters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        filters = filters or {}
        query = select(AuditLog).where(AuditLog.business_id == business_id)

        if "action" in filters and filters["action"]:
            query = query.where(AuditLog.action == filters["action"])
        if "resource_type" in filters and filters["resource_type"]:
            query = query.where(AuditLog.resource_type == filters["resource_type"])
        if "user_id" in filters and filters["user_id"]:
            query = query.where(AuditLog.user_id == filters["user_id"])
        if "date_from" in filters and filters["date_from"]:
            query = query.where(AuditLog.created_at >= filters["date_from"])
        if "date_to" in filters and filters["date_to"]:
            query = query.where(AuditLog.created_at <= filters["date_to"])

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        page = int(filters.get("page", 1))
        page_size = int(filters.get("page_size", 50))
        offset = (page - 1) * page_size

        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return {
            "items": logs,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }

    async def log_ai_decision(
        self,
        business_id: UUID,
        review_id: UUID,
        action: str,
        details: dict[str, Any],
    ) -> AuditLog:
        return await self.log(
            business_id=business_id,
            user_id=None,
            action=f"ai_{action}",
            resource_type="review",
            resource_id=str(review_id),
            details={
                "source": "ai_orchestrator",
                **details,
            },
        )
