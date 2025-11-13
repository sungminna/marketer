"""Webhook models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Webhook(Base):
    """Webhook configuration model."""

    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(JSONB, nullable=False)  # List of events: ["job.completed", "job.failed", "batch.completed"]
    secret = Column(String(255), nullable=True)  # Secret for HMAC signature
    is_active = Column(Boolean, default=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="webhooks")
    webhook_logs = relationship("WebhookLog", back_populates="webhook", cascade="all, delete-orphan")


class WebhookLog(Base):
    """Webhook delivery log model."""

    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)  # job.completed, job.failed, etc.
    payload = Column(JSONB, nullable=False)
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    delivered = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    webhook = relationship("Webhook", back_populates="webhook_logs")
