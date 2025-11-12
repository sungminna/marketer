"""Video generation worker tasks."""
import uuid
import asyncio
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.video_service import VideoService


@celery_app.task(name="process_video_job", bind=True, max_retries=3)
def process_video_job_task(self, job_id: str, user_api_key: str):
    """
    Process video generation job (Celery task).

    Args:
        job_id: Job ID to process
        user_api_key: Encrypted user API key
    """
    try:
        # Run async code in sync context
        asyncio.run(_process_video_job_async(job_id, user_api_key))
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


async def _process_video_job_async(job_id: str, user_api_key: str):
    """Async implementation of video job processing."""
    async with AsyncSessionLocal() as db:
        service = VideoService(db)
        await service.process_generation_job(
            uuid.UUID(job_id),
            user_api_key,
        )


# Simplified non-Celery version for BackgroundTasks
async def process_video_job_background(job_id: str, user_api_key: str):
    """Process video job in FastAPI background task."""
    await _process_video_job_async(job_id, user_api_key)
