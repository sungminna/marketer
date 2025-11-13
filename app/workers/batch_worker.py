"""Batch processing worker tasks."""
import uuid
import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.batch_service import BatchService


@celery_app.task(name="process_batch_job", bind=True, max_retries=3)
def process_batch_job_task(self, batch_id: str):
    """
    Process batch job (Celery task).

    Args:
        batch_id: Batch ID to process
    """
    try:
        # Run async code in sync context
        asyncio.run(_process_batch_async(batch_id))
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _process_batch_async(batch_id: str):
    """Async implementation of batch job processing."""
    async with AsyncSessionLocal() as db:
        service = BatchService(db)
        await service.process_batch(uuid.UUID(batch_id))


# Simplified non-Celery version for BackgroundTasks
async def process_batch_job_background(batch_id: str):
    """Process batch job in FastAPI background task."""
    await _process_batch_async(batch_id)
