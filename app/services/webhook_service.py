"""Webhook notification service."""
import hmac
import hashlib
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.webhook import Webhook, WebhookLog
from app.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing and delivering webhooks."""

    def __init__(self):
        self.timeout = 30  # 30 seconds timeout
        self.max_retries = 3

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    async def send_webhook(
        self,
        db: AsyncSession,
        webhook: Webhook,
        event_type: str,
        payload: Dict[str, Any]
    ) -> WebhookLog:
        """Send webhook notification."""
        # Add timestamp to payload
        payload['timestamp'] = datetime.utcnow().isoformat()
        payload['event'] = event_type

        # Create webhook log
        webhook_log = WebhookLog(
            webhook_id=webhook.id,
            event_type=event_type,
            payload=payload,
            retry_count=0
        )

        try:
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'GTM-Asset-Generator-Webhook/1.0'
            }

            # Add signature if secret is configured
            if webhook.secret:
                import json
                payload_str = json.dumps(payload, sort_keys=True)
                signature = self._generate_signature(payload_str, webhook.secret)
                headers['X-Webhook-Signature'] = f'sha256={signature}'

            # Send webhook
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    str(webhook.url),
                    json=payload,
                    headers=headers
                )

                webhook_log.response_status_code = response.status_code
                webhook_log.response_body = response.text[:1000]  # Limit response body

                if 200 <= response.status_code < 300:
                    webhook_log.delivered = True
                    webhook_log.delivered_at = datetime.utcnow()
                else:
                    webhook_log.error_message = f"HTTP {response.status_code}: {response.text[:200]}"

        except httpx.TimeoutException:
            webhook_log.error_message = "Request timeout"
            logger.warning(f"Webhook timeout for {webhook.url}")
        except httpx.RequestError as e:
            webhook_log.error_message = f"Request error: {str(e)}"
            logger.error(f"Webhook request error for {webhook.url}: {e}")
        except Exception as e:
            webhook_log.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected webhook error for {webhook.url}: {e}")

        # Save log
        db.add(webhook_log)
        await db.commit()
        await db.refresh(webhook_log)

        return webhook_log

    async def send_event_to_user_webhooks(
        self,
        db: AsyncSession,
        user_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ):
        """Send event to all user webhooks subscribed to this event."""
        # Get active webhooks for this user and event
        result = await db.execute(
            select(Webhook).where(
                Webhook.user_id == user_id,
                Webhook.is_active == True,
                Webhook.events.contains([event_type])
            )
        )
        webhooks = result.scalars().all()

        # Send to each webhook
        for webhook in webhooks:
            try:
                await self.send_webhook(db, webhook, event_type, payload)
            except Exception as e:
                logger.error(f"Failed to send webhook {webhook.id}: {e}")

    async def retry_failed_webhooks(self, db: AsyncSession):
        """Retry failed webhooks (can be called by a periodic task)."""
        # Get failed webhooks from last 24 hours with retry count < max_retries
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        result = await db.execute(
            select(WebhookLog).join(Webhook).where(
                WebhookLog.delivered == False,
                WebhookLog.retry_count < self.max_retries,
                WebhookLog.created_at >= cutoff_time,
                Webhook.is_active == True
            )
        )
        failed_logs = result.scalars().all()

        for log in failed_logs:
            try:
                # Get webhook
                webhook_result = await db.execute(
                    select(Webhook).where(Webhook.id == log.webhook_id)
                )
                webhook = webhook_result.scalar_one_or_none()

                if webhook:
                    # Increment retry count
                    log.retry_count += 1

                    # Retry sending
                    await self.send_webhook(
                        db,
                        webhook,
                        log.event_type,
                        log.payload
                    )

            except Exception as e:
                logger.error(f"Failed to retry webhook log {log.id}: {e}")


webhook_service = WebhookService()
