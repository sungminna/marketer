"""Analytics models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class DailyAnalytics(Base):
    """Daily analytics aggregation model."""

    __tablename__ = "daily_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)  # image|video
    total_jobs = Column(Integer, default=0)
    successful_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    total_quantity = Column(Integer, default=0)  # Images or video seconds
    total_cost_usd = Column(DECIMAL(10, 4), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analytics")
