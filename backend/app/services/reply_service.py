from __future__ import annotations

import logging
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reply import Reply
from app.models.review import Review
from app.utils.helpers import now

logger = logging.getLogger(__name__)


class ReplyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def generate_reply(
        self, business_id: UUID, review_id: UUID, custom_instructions: Optional[str] = None
    ) -> Reply:
        from app.agents.orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator(self.db)
        result = await orchestrator.process_review(
            business_id, review_id, custom_instructions=custom_instructions
        )
        await self.db.flush()
        await self.db.refresh(result.reply)
        return result.reply

    async def update_reply(self, business_id: UUID, reply_id: UUID, content: str) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply).where(Reply.business_id == business_id, Reply.id == reply_id)
        )
        reply = result.scalar_one_or_none()
        if not reply:
            return None
        reply.content = content
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    async def approve_reply(self, business_id: UUID, reply_id: UUID) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply).where(Reply.business_id == business_id, Reply.id == reply_id)
        )
        reply = result.scalar_one_or_none()
        if not reply:
            return None
        reply.status = "approved"
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    async def reject_reply(self, business_id: UUID, reply_id: UUID, reason: str) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply).where(Reply.business_id == business_id, Reply.id == reply_id)
        )
        reply = result.scalar_one_or_none()
        if not reply:
            return None
        reply.status = "rejected"
        reply.rejection_reason = reason
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    async def publish_reply(self, business_id: UUID, reply_id: UUID) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply)
            .where(Reply.business_id == business_id, Reply.id == reply_id)
            .options(selectinload(Reply.review))
        )
        reply = result.scalar_one_or_none()
        if not reply:
            return None

        review = reply.review
        if review:
            try:
                from app.services.platform_service import PlatformService

                platform_service = PlatformService(self.db)
                connections = await platform_service.get_connections(business_id)
                platform_conn = next(
                    (c for c in connections if c.platform == review.platform and c.is_active),
                    None,
                )
                if platform_conn:
                    platform_reply_id = await platform_service.publish_to_platform(
                        business_id, platform_conn.id, review, reply.content
                    )
                    reply.platform_reply_id = platform_reply_id
            except Exception as exc:
                logger.warning("Platform publish failed for reply %s: %s", reply_id, exc)

        reply.status = "published"
        reply.published_at = now()
        await self.db.flush()
        await self.db.refresh(reply)
        return reply

    async def regenerate_reply(self, business_id: UUID, review_id: UUID) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply).where(
                Reply.business_id == business_id, Reply.review_id == review_id
            )
        )
        existing = result.scalar_one_or_none()

        from app.agents.orchestrator import AIOrchestrator

        orchestrator = AIOrchestrator(self.db)
        new_result = await orchestrator.process_review(
            business_id, review_id, custom_instructions=None
        )

        if existing:
            existing.content = new_result.reply.content
            existing.quality_score = new_result.reply.quality_score
            existing.safety_score = new_result.reply.safety_score
            existing.ai_metadata = new_result.reply.ai_metadata
            existing.status = "pending_approval"
            await self.db.flush()
            await self.db.refresh(existing)
            return existing

        return new_result.reply

    async def get_pending_replies(self, business_id: UUID) -> list[Reply]:
        result = await self.db.execute(
            select(Reply)
            .where(
                Reply.business_id == business_id,
                Reply.status.in_(["pending", "pending_approval"]),
            )
            .options(selectinload(Reply.review))
            .order_by(Reply.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_reply(self, business_id: UUID, reply_id: UUID) -> Optional[Reply]:
        result = await self.db.execute(
            select(Reply)
            .where(Reply.business_id == business_id, Reply.id == reply_id)
            .options(selectinload(Reply.review))
        )
        return result.scalar_one_or_none()
