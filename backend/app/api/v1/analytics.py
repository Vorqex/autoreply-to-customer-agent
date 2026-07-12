from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_business, get_current_user, get_db
from app.models.business import Business
from app.models.user import User
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = AnalyticsService(db)
        stats = await service.get_dashboard_stats(business_id=business.id)
        return stats
    except Exception as exc:
        logger.exception("Failed to fetch dashboard stats")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch dashboard stats")


@router.get("/sentiment-trends")
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = AnalyticsService(db)
        trends = await service.get_sentiment_trends(business_id=business.id, days=days)
        return trends
    except Exception as exc:
        logger.exception("Failed to fetch sentiment trends")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch sentiment trends")


@router.get("/platform-performance")
async def get_platform_performance(
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = AnalyticsService(db)
        performance = await service.get_platform_performance(business_id=business.id)
        return performance
    except Exception as exc:
        logger.exception("Failed to fetch platform performance")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch platform performance")


@router.get("/monthly-activity")
async def get_monthly_activity(
    months: int = Query(12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = AnalyticsService(db)
        activity = await service.get_monthly_activity(business_id=business.id, months=months)
        return activity
    except Exception as exc:
        logger.exception("Failed to fetch monthly activity")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch monthly activity")
