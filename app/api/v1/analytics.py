"""Analytics endpoints."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/summary")
@limiter.limit("60/minute")
async def get_usage_summary(
    request: Request,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage summary for last N days."""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    summary = await service.get_usage_summary(current_user.id, start_date, end_date)
    return summary


@router.get("/cost-breakdown")
@limiter.limit("60/minute")
async def get_cost_breakdown(
    request: Request,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get cost breakdown by provider."""
    service = AnalyticsService(db)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    breakdown = await service.get_cost_breakdown(current_user.id, start_date, end_date)
    return {'breakdown': breakdown}


@router.get("/daily")
@limiter.limit("60/minute")
async def get_daily_stats(
    request: Request,
    days: int = Query(default=30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily statistics."""
    service = AnalyticsService(db)
    stats = await service.get_daily_stats(current_user.id, days)
    return {'stats': stats}


@router.get("/quota")
@limiter.limit("120/minute")
async def get_quota_usage(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current quota usage."""
    service = QuotaService(db)
    usage = await service.get_current_usage(current_user.id)
    return usage
