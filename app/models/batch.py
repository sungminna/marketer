"""Batch processing models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class BatchJob(Base):
    """Batch job model for processing multiple generation requests."""

    __tablename__ = "batch_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    batch_type = Column(String(50), nullable=False)  # image|video|mixed
    status = Column(String(50), default="pending")  # pending|processing|completed|failed|partial
    total_jobs = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    total_cost_usd = Column(DECIMAL(10, 4), default=0)
    job_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])  # Array of GenerationJob IDs
    error_message = Column(Text, nullable=True)
    batch_config = Column(JSONB, default={})  # Configuration for all jobs in batch
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="batch_jobs")
