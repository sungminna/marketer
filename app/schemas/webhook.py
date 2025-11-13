"""Webhook schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID


class WebhookBase(BaseModel):
    """Base webhook schema."""
    url: HttpUrl = Field(..., description="Webhook URL to call")
    events: List[str] = Field(..., description="List of events to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for HMAC signature")
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)


class WebhookCreate(WebhookBase):
    """Schema for creating a webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookLogResponse(BaseModel):
    """Schema for webhook log response."""
    id: UUID
    webhook_id: UUID
    event_type: str
    payload: dict
    response_status_code: Optional[int]
    response_body: Optional[str]
    error_message: Optional[str]
    delivered: bool
    retry_count: int
    created_at: datetime
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


class WebhookEventPayload(BaseModel):
    """Base schema for webhook event payloads."""
    event: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: dict = Field(..., description="Event data")


class JobCompletedPayload(BaseModel):
    """Payload for job.completed event."""
    event: str = "job.completed"
    timestamp: datetime
    data: dict = Field(..., description="Job data including id, status, output_urls, cost_usd")


class JobFailedPayload(BaseModel):
    """Payload for job.failed event."""
    event: str = "job.failed"
    timestamp: datetime
    data: dict = Field(..., description="Job data including id, status, error_message")
