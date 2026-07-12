from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from celery import Task
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.review import Review
from app.models.usage import UsageMetric
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class DatabaseTask(Task):
    _db: AsyncSession | None = None

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._db is not None:
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self._db.close())
                loop.close()
            except Exception:
                pass


@celery_app.task(base=DatabaseTask, bind=True, name="process_review_task")
def process_review_task(self, business_id: str, review_id: str):
    from app.agents.orchestrator import AIOrchestrator

    async def _process():
        async with AsyncSessionLocal() as db:
            orchestrator = AIOrchestrator(db)
            result = await orchestrator.process_review(
                business_id=UUID(business_id),
                review_id=UUID(review_id),
            )
            await db.commit()
            return {
                "reply_id": str(result.reply.id),
                "status": result.reply.status,
                "decisions": result.decisions,
            }

    try:
        result = _run_async(_process())
        logger.info("Processed review %s — reply status: %s", review_id, result.get("status"))
        return result
    except Exception as exc:
        logger.exception("Failed to process review %s: %s", review_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(base=DatabaseTask, bind=True, name="publish_reply_task")
def publish_reply_task(self, business_id: str, reply_id: str):
    from app.services.reply_service import ReplyService

    async def _publish():
        async with AsyncSessionLocal() as db:
            service = ReplyService(db)
            reply = await service.publish_reply(
                business_id=UUID(business_id),
                reply_id=UUID(reply_id),
            )
            if reply:
                await db.commit()
                return {"reply_id": str(reply.id), "status": reply.status}
            return None

    try:
        result = _run_async(_publish())
        logger.info("Published reply %s", reply_id)
        return result
    except Exception as exc:
        logger.exception("Failed to publish reply %s: %s", reply_id, exc)
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(base=DatabaseTask, bind=True, name="generate_embeddings_task")
def generate_embeddings_task(self, business_id: str, entry_id: str):
    from app.models.knowledge_base import KnowledgeBaseEntry
    from app.services.knowledge_service import KnowledgeService

    async def _generate():
        async with AsyncSessionLocal() as db:
            service = KnowledgeService(db)
            result = await db.execute(
                select(KnowledgeBaseEntry).where(
                    KnowledgeBaseEntry.id == UUID(entry_id),
                    KnowledgeBaseEntry.business_id == UUID(business_id),
                )
            )
            entry = result.scalar_one_or_none()
            if not entry:
                raise ValueError(f"Knowledge base entry {entry_id} not found")

            embedding = await service._generate_embedding(f"{entry.title}\n\n{entry.content}")
            entry.embedding = embedding
            await db.commit()
            return {"entry_id": entry_id, "embedding_length": len(embedding)}

    try:
        result = _run_async(_generate())
        logger.info("Generated embeddings for entry %s", entry_id)
        return result
    except Exception as exc:
        logger.exception("Failed to generate embeddings for entry %s: %s", entry_id, exc)
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(base=DatabaseTask, bind=True, name="aggregate_usage_metrics_task")
def aggregate_usage_metrics_task(self):
    async def _aggregate():
        async with AsyncSessionLocal() as db:
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

            result = await db.execute(
                select(
                    UsageMetric.business_id,
                    func.count().label("total_requests"),
                    func.sum(UsageMetric.total_tokens).label("total_tokens"),
                    func.sum(UsageMetric.cost).label("total_cost"),
                )
                .where(
                    UsageMetric.created_at >= start,
                    UsageMetric.created_at < end,
                )
                .group_by(UsageMetric.business_id)
            )
            rows = result.all()

            logger.info("Aggregated usage metrics for %d businesses on %s", len(rows), start.date())
            return {
                "date": start.isoformat(),
                "businesses_aggregated": len(rows),
                "rows": [
                    {
                        "business_id": str(row.business_id),
                        "total_requests": row.total_requests,
                        "total_tokens": row.total_tokens or 0,
                        "total_cost": float(row.total_cost or 0.0),
                    }
                    for row in rows
                ],
            }

    try:
        return _run_async(_aggregate())
    except Exception as exc:
        logger.exception("Failed to aggregate usage metrics: %s", exc)
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(base=DatabaseTask, bind=True, name="sync_platform_reviews_task")
def sync_platform_reviews_task(self, business_id: str, platform: str):
    async def _sync():
        async with AsyncSessionLocal() as db:
            from app.services.platform_service import PlatformService
            service = PlatformService(db)
            connections = await service.get_connections(business_id=UUID(business_id))
            platform_conns = [c for c in connections if c.platform == platform and c.is_active]

            synced = 0
            for conn in platform_conns:
                adapter = service._get_adapter(conn.platform)
                if adapter and hasattr(adapter, "fetch_reviews"):
                    try:
                        reviews_data = await adapter.fetch_reviews(conn)
                        from app.services.review_service import ReviewService
                        review_service = ReviewService(db)
                        for review_data in reviews_data:
                            try:
                                await review_service.ingest_review(
                                    business_id=UUID(business_id),
                                    platform=conn.platform,
                                    review_data={"platform_review_id": review_data.get("id"), **review_data},
                                )
                                synced += 1
                            except ValueError:
                                pass
                        conn.last_sync_at = datetime.now(timezone.utc)
                    except Exception as exc:
                        logger.warning("Failed to sync reviews from %s: %s", conn.platform, exc)
                else:
                    logger.info("No adapter for %s, skipping sync", conn.platform)

            await db.commit()
            return {"business_id": business_id, "platform": platform, "synced": synced}

    try:
        result = _run_async(_sync())
        logger.info("Synced %d reviews from %s for business %s", result["synced"], platform, business_id)
        return result
    except Exception as exc:
        logger.exception("Failed to sync platform reviews: %s", exc)
        raise self.retry(exc=exc, countdown=300)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        timedelta(hours=1),
        aggregate_usage_metrics_task.s(),
        name="aggregate-usage-metrics-hourly",
    )
