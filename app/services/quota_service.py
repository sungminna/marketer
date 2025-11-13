"""Quota management service."""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.quota import UserQuota, QuotaUsage
from app.models.usage import UsageLog
import uuid


class QuotaService:
    """Service for quota management."""

    PLAN_LIMITS = {
        'free': {'images': 100, 'video_seconds': 60, 'cost': 10.00},
        'starter': {'images': 1000, 'video_seconds': 600, 'cost': 100.00},
        'pro': {'images': 10000, 'video_seconds': 6000, 'cost': 1000.00},
        'enterprise': {'images': 100000, 'video_seconds': 60000, 'cost': 10000.00},
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_quota(self, user_id: uuid.UUID, plan_type: str = 'free') -> UserQuota:
        """Initialize quota for new user."""
        limits = self.PLAN_LIMITS.get(plan_type, self.PLAN_LIMITS['free'])

        quota = UserQuota(
            user_id=user_id,
            plan_type=plan_type,
            monthly_image_limit=limits['images'],
            monthly_video_seconds_limit=limits['video_seconds'],
            monthly_cost_limit_usd=limits['cost'],
        )

        self.db.add(quota)
        await self.db.commit()
        return quota

    async def get_current_usage(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get current month usage."""
        # Get current month start
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        # Get or create quota usage
        result = await self.db.execute(
            select(QuotaUsage).where(
                QuotaUsage.user_id == user_id,
                QuotaUsage.month == month_start,
            )
        )
        usage = result.scalar_one_or_none()

        if not usage:
            usage = QuotaUsage(
                user_id=user_id,
                month=month_start,
            )
            self.db.add(usage)
            await self.db.commit()

        # Get quota limits
        quota_result = await self.db.execute(
            select(UserQuota).where(UserQuota.user_id == user_id)
        )
        quota = quota_result.scalar_one_or_none()

        if not quota:
            quota = await self.initialize_quota(user_id)

        return {
            'images_used': usage.images_used,
            'images_limit': quota.monthly_image_limit,
            'images_remaining': quota.monthly_image_limit - usage.images_used,
            'video_seconds_used': usage.video_seconds_used,
            'video_seconds_limit': quota.monthly_video_seconds_limit,
            'video_seconds_remaining': quota.monthly_video_seconds_limit - usage.video_seconds_used,
            'cost_used_usd': float(usage.cost_used_usd),
            'cost_limit_usd': float(quota.monthly_cost_limit_usd),
            'cost_remaining_usd': float(quota.monthly_cost_limit_usd - usage.cost_used_usd),
        }

    async def check_quota(self, user_id: uuid.UUID, resource_type: str, quantity: int) -> tuple[bool, str]:
        """Check if user has quota available."""
        usage = await self.get_current_usage(user_id)

        if resource_type == 'image':
            if usage['images_used'] + quantity > usage['images_limit']:
                return False, f"Image quota exceeded. Limit: {usage['images_limit']}"
        elif resource_type == 'video':
            if usage['video_seconds_used'] + quantity > usage['video_seconds_limit']:
                return False, f"Video quota exceeded. Limit: {usage['video_seconds_limit']} seconds"

        return True, "Quota available"

    async def update_quota(self, user_id: uuid.UUID, plan_type: str) -> UserQuota:
        """Update user quota based on plan."""
        result = await self.db.execute(
            select(UserQuota).where(UserQuota.user_id == user_id)
        )
        quota = result.scalar_one_or_none()

        if not quota:
            return await self.initialize_quota(user_id, plan_type)

        limits = self.PLAN_LIMITS.get(plan_type, self.PLAN_LIMITS['free'])
        quota.plan_type = plan_type
        quota.monthly_image_limit = limits['images']
        quota.monthly_video_seconds_limit = limits['video_seconds']
        quota.monthly_cost_limit_usd = limits['cost']

        await self.db.commit()
        return quota
