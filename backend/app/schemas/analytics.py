from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_reviews: int = 0
    pending_replies: int = 0
    auto_replied: int = 0
    manual_replies: int = 0
    avg_rating: float = 0.0
    ai_usage: int = 0
    avg_response_time: float = 0.0
    connected_platforms: int = 0


class SentimentTrend(BaseModel):
    date: str
    positive: int = 0
    neutral: int = 0
    negative: int = 0
    very_negative: int = 0


class PlatformPerformance(BaseModel):
    platform: str
    total: int = 0
    avg_rating: float = 0.0
    replied: int = 0
    pending: int = 0


class MonthlyActivity(BaseModel):
    month: str
    reviews: int = 0
    replies: int = 0
    ai_generations: int = 0
