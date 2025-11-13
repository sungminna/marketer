"""Analytics service."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.analytics import DailyAnalytics
from app.models.usage import UsageLog
from app.models.job import GenerationJob
import uuid


class AnalyticsService:
    """Service for analytics and reporting."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_usage_summary(
        self,
        user_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get usage summary for date range."""
        result = await self.db.execute(
            select(
                func.count(GenerationJob.id).label('total_jobs'),
                func.count(GenerationJob.id).filter(GenerationJob.status == 'completed').label('successful_jobs'),
                func.count(GenerationJob.id).filter(GenerationJob.status == 'failed').label('failed_jobs'),
                func.sum(UsageLog.quantity).label('total_quantity'),
                func.sum(UsageLog.cost_usd).label('total_cost'),
            )
            .select_from(GenerationJob)
            .join(UsageLog, GenerationJob.id == UsageLog.job_id, isouter=True)
            .where(
                GenerationJob.user_id == user_id,
                GenerationJob.created_at >= start_date,
                GenerationJob.created_at <= end_date,
            )
        )
        row = result.first()

        return {
            'total_jobs': row.total_jobs or 0,
            'successful_jobs': row.successful_jobs or 0,
            'failed_jobs': row.failed_jobs or 0,
            'total_quantity': int(row.total_quantity or 0),
            'total_cost_usd': float(row.total_cost or 0),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }

    async def get_cost_breakdown(
        self,
        user_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Get cost breakdown by provider."""
        result = await self.db.execute(
            select(
                UsageLog.provider,
                UsageLog.resource_type,
                func.count(UsageLog.id).label('count'),
                func.sum(UsageLog.quantity).label('quantity'),
                func.sum(UsageLog.cost_usd).label('cost'),
            )
            .where(
                UsageLog.user_id == user_id,
                UsageLog.created_at >= start_date,
                UsageLog.created_at <= end_date,
            )
            .group_by(UsageLog.provider, UsageLog.resource_type)
        )

        breakdown = []
        for row in result:
            breakdown.append({
                'provider': row.provider,
                'resource_type': row.resource_type,
                'count': row.count,
                'quantity': int(row.quantity),
                'cost_usd': float(row.cost),
            })

        return breakdown

    async def get_daily_stats(
        self,
        user_id: uuid.UUID,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get daily statistics for last N days."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        result = await self.db.execute(
            select(
                func.date(GenerationJob.created_at).label('date'),
                func.count(GenerationJob.id).label('jobs'),
                func.sum(GenerationJob.cost_usd).label('cost'),
            )
            .where(
                GenerationJob.user_id == user_id,
                GenerationJob.created_at >= start_date,
                GenerationJob.status == 'completed',
            )
            .group_by(func.date(GenerationJob.created_at))
            .order_by(func.date(GenerationJob.created_at))
        )

        stats = []
        for row in result:
            stats.append({
                'date': row.date.isoformat(),
                'jobs': row.jobs,
                'cost_usd': float(row.cost or 0),
            })

        return stats
