"""Webhook management endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.webhook import Webhook, WebhookLog
from app.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookLogResponse
)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=WebhookResponse, status_code=201)
@limiter.limit("10/minute")
async def create_webhook(
    request: Request,
    webhook_data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new webhook."""
    # Validate events
    valid_events = [
        "job.completed",
        "job.failed",
        "batch.completed",
        "batch.failed"
    ]
    for event in webhook_data.events:
        if event not in valid_events:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event type: {event}. Valid events: {valid_events}"
            )

    # Create webhook
    webhook = Webhook(
        user_id=current_user.id,
        url=str(webhook_data.url),
        events=webhook_data.events,
        secret=webhook_data.secret,
        description=webhook_data.description,
        is_active=webhook_data.is_active
    )

    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)

    return webhook


@router.get("", response_model=List[WebhookResponse])
@limiter.limit("60/minute")
async def list_webhooks(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all webhooks for current user."""
    result = await db.execute(
        select(Webhook)
        .where(Webhook.user_id == current_user.id)
        .order_by(desc(Webhook.created_at))
    )
    webhooks = result.scalars().all()
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
@limiter.limit("60/minute")
async def get_webhook(
    request: Request,
    webhook_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook by ID."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id
        )
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    return webhook


@router.patch("/{webhook_id}", response_model=WebhookResponse)
@limiter.limit("20/minute")
async def update_webhook(
    request: Request,
    webhook_id: UUID,
    webhook_data: WebhookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update webhook."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id
        )
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Update fields
    if webhook_data.url is not None:
        webhook.url = str(webhook_data.url)
    if webhook_data.events is not None:
        # Validate events
        valid_events = ["job.completed", "job.failed", "batch.completed", "batch.failed"]
        for event in webhook_data.events:
            if event not in valid_events:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event type: {event}"
                )
        webhook.events = webhook_data.events
    if webhook_data.secret is not None:
        webhook.secret = webhook_data.secret
    if webhook_data.description is not None:
        webhook.description = webhook_data.description
    if webhook_data.is_active is not None:
        webhook.is_active = webhook_data.is_active

    await db.commit()
    await db.refresh(webhook)

    return webhook


@router.delete("/{webhook_id}", status_code=204)
@limiter.limit("20/minute")
async def delete_webhook(
    request: Request,
    webhook_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete webhook."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id
        )
    )
    webhook = result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    await db.delete(webhook)
    await db.commit()


@router.get("/{webhook_id}/logs", response_model=List[WebhookLogResponse])
@limiter.limit("60/minute")
async def get_webhook_logs(
    request: Request,
    webhook_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get webhook delivery logs."""
    # Verify webhook ownership
    webhook_result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.user_id == current_user.id
        )
    )
    webhook = webhook_result.scalar_one_or_none()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Get logs
    result = await db.execute(
        select(WebhookLog)
        .where(WebhookLog.webhook_id == webhook_id)
        .order_by(desc(WebhookLog.created_at))
        .limit(min(limit, 100))
    )
    logs = result.scalars().all()

    return logs
