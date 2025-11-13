"""Generation job model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class GenerationJob(Base):
    """Generation job model for tracking image and video generation tasks."""

    __tablename__ = "generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(String(50), nullable=False)  # image_generate|image_edit|video_generate|image_to_video|video_bg_remove|prototype_generate
    provider = Column(String(50), nullable=False)  # gemini|openai|imagen|veo|sora
    model = Column(String(100), nullable=False)
    input_params = Column(JSONB, nullable=False)
    status = Column(String(50), default="pending")  # pending|processing|completed|failed
    output_urls = Column(ARRAY(Text), default=[])
    cost_usd = Column(DECIMAL(10, 4), nullable=True)
    error_message = Column(Text, nullable=True)
    job_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="jobs")
    usage_logs = relationship("UsageLog", back_populates="job", cascade="all, delete-orphan")
