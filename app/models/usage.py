"""Usage log model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class UsageLog(Base):
    """Usage log model for tracking resource usage and costs."""

    __tablename__ = "usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)  # image|video|edit
    quantity = Column(Integer, nullable=False)  # Number of images or video seconds
    cost_usd = Column(DECIMAL(10, 4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_logs")
    job = relationship("GenerationJob", back_populates="usage_logs")
