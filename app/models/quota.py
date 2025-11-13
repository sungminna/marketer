"""Quota models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserQuota(Base):
    """User quota model for usage limits."""

    __tablename__ = "user_quotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    plan_type = Column(String(50), nullable=False)  # free|starter|pro|enterprise
    monthly_image_limit = Column(Integer, default=100)  # Number of images per month
    monthly_video_seconds_limit = Column(Integer, default=60)  # Video seconds per month
    monthly_cost_limit_usd = Column(DECIMAL(10, 2), default=10.00)  # Cost limit per month
    reset_day = Column(Integer, default=1)  # Day of month when quota resets
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quota")


class QuotaUsage(Base):
    """Current month quota usage tracking."""

    __tablename__ = "quota_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    month = Column(DateTime, nullable=False, index=True)  # First day of the month
    images_used = Column(Integer, default=0)
    video_seconds_used = Column(Integer, default=0)
    cost_used_usd = Column(DECIMAL(10, 4), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quota_usage")
