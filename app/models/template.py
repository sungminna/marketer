"""Template models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Template(Base):
    """Template model for reusable generation configurations."""

    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # image|video
    job_type = Column(String(50), nullable=False)  # image_generate|video_generate|etc.
    provider = Column(String(50), nullable=False)  # gemini|openai|imagen|veo|sora
    model = Column(String(100), nullable=False)
    config = Column(JSONB, nullable=False)  # Template configuration (prompt template, design tokens, etc.)
    is_public = Column(Boolean, default=False)  # Public templates can be used by other users
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)  # Track how many times template has been used
    tags = Column(JSONB, default=[])  # Tags for categorization
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="templates")
