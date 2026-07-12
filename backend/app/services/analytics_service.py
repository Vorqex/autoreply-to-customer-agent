from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform import PlatformConnection
from app.models.reply import Reply
from app.models.review import Review
from app.models.usage import UsageMetric
from app.utils.helpers import now


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_dashboard_stats(self, business_id: UUID) -> dict[str, Any]:
        total_reviews_result = await self.db.execute(
            select(func.count()).where(Review.business_id == business_id)
        )
        total_reviews = total_reviews_result.scalar() or 0

        pending_replies_result = await self.db.execute(
            select(func.count()).where(
                Reply.business_id == business_id,
                Reply.status.in_(["pending", "pending_approval"]),
            )
        )
        pending_replies = pending_replies_result.scalar() or 0

        auto_replied_result = await self.db.execute(
            select(func.count()).where(
                Reply.business_id == business_id, Reply.status == "published"
            )
        )
        auto_replied = auto_replied_result.scalar() or 0

        avg_rating_result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.business_id == business_id)
        )
        avg_rating = round(float(avg_rating_result.scalar() or 0.0), 2)

        now_utc = now()
        month_start = now_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ai_usage_result = await self.db.execute(
            select(func.count()).where(
                UsageMetric.business_id == business_id,
                UsageMetric.metric_type == "ai_generation",
                UsageMetric.created_at >= month_start,
            )
        )
        ai_usage = ai_usage_result.scalar() or 0

        response_time_result = await self.db.execute(
            select(func.avg(
                func.extract("epoch", Reply.published_at - Review.created_at)
            )).select_from(
                Reply.__table__.join(
                    Review.__table__,
                    Reply.review_id == Review.id,
                )
            ).where(
                Review.business_id == business_id,
                Reply.published_at.isnot(None),
            )
        )
        avg_seconds = response_time_result.scalar()
        avg_response_time = round(avg_seconds / 3600, 2) if avg_seconds else 0.0

        platforms_result = await self.db.execute(
            select(func.count()).where(
                PlatformConnection.business_id == business_id,
                PlatformConnection.is_active == True,
            )
        )
        connected_platforms = platforms_result.scalar() or 0

        return {
            "total_reviews": total_reviews,
            "pending_replies": pending_replies,
            "auto_replied": auto_replied,
            "manual_replies": max(0, total_reviews - auto_replied),
            "avg_rating": avg_rating,
            "ai_usage": ai_usage,
            "avg_response_time": avg_response_time,
            "connected_platforms": connected_platforms,
        }

    async def get_sentiment_trends(
        self, business_id: UUID, days: int = 30
    ) -> list[dict[str, Any]]:
        cutoff = now() - timedelta(days=days)
        rows = await self.db.execute(
            select(
                cast(Review.review_date, Date).label("date"),
                Review.sentiment,
                func.count().label("cnt"),
            )
            .where(
                Review.business_id == business_id,
                Review.review_date >= cutoff,
                Review.sentiment.isnot(None),
            )
            .group_by(cast(Review.review_date, Date), Review.sentiment)
            .order_by(cast(Review.review_date, Date))
        )

        trends: dict[str, dict[str, int]] = {}
        sentiments = ["positive", "neutral", "negative", "very_negative"]
        for i in range(days):
            day = (cutoff + timedelta(days=i)).strftime("%Y-%m-%d")
            trends[day] = {s: 0 for s in sentiments}

        for row in rows:
            day_str = str(row.date)
            if day_str in trends:
                trends[day_str][row.sentiment] = row.cnt

        return [
            {"date": day, **counts} for day, counts in sorted(trends.items())
        ]

    async def get_platform_performance(self, business_id: UUID) -> list[dict[str, Any]]:
        subq = (
            select(
                Review.platform,
                func.count().label("total"),
                func.avg(Review.rating).label("avg_rating"),
            )
            .where(Review.business_id == business_id)
            .group_by(Review.platform)
        ).subquery()

        replied_subq = (
            select(
                Review.platform,
                func.count().label("replied"),
            )
            .where(
                Review.business_id == business_id,
                Review.id.in_(
                    select(Reply.review_id).where(Reply.business_id == business_id)
                ),
            )
            .group_by(Review.platform)
        ).subquery()

        query = (
            select(
                subq.c.platform,
                subq.c.total,
                subq.c.avg_rating,
                func.coalesce(replied_subq.c.replied, 0).label("replied"),
            )
            .outerjoin(
                replied_subq,
                subq.c.platform == replied_subq.c.platform,
            )
        )

        rows = await self.db.execute(query)
        results = []
        for row in rows:
            results.append({
                "platform": row.platform,
                "total": row.total,
                "avg_rating": round(float(row.avg_rating or 0.0), 2),
                "replied": row.replied,
                "pending": row.total - row.replied,
            })
        return results

    async def get_monthly_activity(
        self, business_id: UUID, months: int = 12
    ) -> list[dict[str, Any]]:
        cutoff = now() - timedelta(days=30 * months)
        reviews_result = await self.db.execute(
            select(
                func.date_trunc("month", Review.created_at).label("month"),
                func.count().label("cnt"),
            )
            .where(
                Review.business_id == business_id,
                Review.created_at >= cutoff,
            )
            .group_by(func.date_trunc("month", Review.created_at))
        )
        reviews_map = {str(row.month): row.cnt for row in reviews_result}

        replies_result = await self.db.execute(
            select(
                func.date_trunc("month", Reply.created_at).label("month"),
                func.count().label("cnt"),
            )
            .where(
                Reply.business_id == business_id,
                Reply.created_at >= cutoff,
            )
            .group_by(func.date_trunc("month", Reply.created_at))
        )
        replies_map = {str(row.month): row.cnt for row in replies_result}

        ai_result = await self.db.execute(
            select(
                func.date_trunc("month", UsageMetric.created_at).label("month"),
                func.count().label("cnt"),
            )
            .where(
                UsageMetric.business_id == business_id,
                UsageMetric.metric_type == "ai_generation",
                UsageMetric.created_at >= cutoff,
            )
            .group_by(func.date_trunc("month", UsageMetric.created_at))
        )
        ai_map = {str(row.month): row.cnt for row in ai_result}

        results = []
        for i in range(months - 1, -1, -1):
            month_start = (cutoff.replace(day=1) + timedelta(days=30 * i)).replace(
                day=1
            )
            key = month_start.strftime("%Y-%m-%d")
            month_label = month_start.strftime("%Y-%m")
            results.append({
                "month": month_label,
                "reviews": reviews_map.get(key, 0),
                "replies": replies_map.get(key, 0),
                "ai_generations": ai_map.get(key, 0),
            })

        return results
