"""Batch processing endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.batch import (
    BatchJobCreate,
    BatchJobResponse,
    BatchJobProgress,
    BatchJobListResponse,
)
from app.schemas.image import ImageJobResponse
from app.services.batch_service import BatchService
from app.workers.batch_worker import process_batch_job_task

router = APIRouter(prefix="/api/v1/batches", tags=["batches"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=BatchJobResponse, status_code=201)
@limiter.limit("10/minute")
async def create_batch(
    request: Request,
    batch_data: BatchJobCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new batch job.

    This endpoint allows you to submit multiple generation jobs at once.
    All jobs will be processed asynchronously.
    """
    service = BatchService(db)

    # Validate batch type
    if batch_data.batch_type not in ["image", "video", "mixed"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid batch_type. Must be 'image', 'video', or 'mixed'"
        )

    # Create batch
    batch = await service.create_batch(
        user_id=current_user.id,
        name=batch_data.name,
        description=batch_data.description,
        batch_type=batch_data.batch_type,
        jobs_data=[job.model_dump() for job in batch_data.jobs],
        batch_config=batch_data.batch_config,
    )

    # Queue batch processing as background task
    # Use Celery for production, BackgroundTasks for simplicity
    try:
        # Try to use Celery if available
        process_batch_job_task.delay(str(batch.id))
    except Exception:
        # Fallback to background tasks
        background_tasks.add_task(
            _process_batch_background,
            batch.id,
            db
        )

    return batch


async def _process_batch_background(batch_id: UUID, db: AsyncSession):
    """Background task to process batch."""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        service = BatchService(session)
        await service.process_batch(batch_id)


@router.get("", response_model=BatchJobListResponse)
@limiter.limit("60/minute")
async def list_batches(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all batch jobs for current user with pagination."""
    service = BatchService(db)
    batches, total = await service.list_batches(
        user_id=current_user.id,
        limit=min(limit, 100),
        offset=offset,
    )

    return BatchJobListResponse(
        items=batches,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{batch_id}", response_model=BatchJobResponse)
@limiter.limit("60/minute")
async def get_batch(
    request: Request,
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get batch job by ID."""
    service = BatchService(db)
    batch = await service.get_batch(batch_id, current_user.id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    return batch


@router.get("/{batch_id}/progress", response_model=BatchJobProgress)
@limiter.limit("120/minute")
async def get_batch_progress(
    request: Request,
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get batch job progress."""
    service = BatchService(db)
    batch = await service.get_batch(batch_id, current_user.id)

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    progress_percentage = 0.0
    if batch.total_jobs > 0:
        progress_percentage = (
            (batch.completed_jobs + batch.failed_jobs) / batch.total_jobs
        ) * 100

    return BatchJobProgress(
        id=batch.id,
        status=batch.status,
        total_jobs=batch.total_jobs,
        completed_jobs=batch.completed_jobs,
        failed_jobs=batch.failed_jobs,
        progress_percentage=round(progress_percentage, 2),
        estimated_cost_usd=float(batch.total_cost_usd) if batch.total_cost_usd else None,
    )


@router.get("/{batch_id}/jobs", response_model=List[ImageJobResponse])
@limiter.limit("60/minute")
async def get_batch_jobs(
    request: Request,
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all jobs in a batch."""
    service = BatchService(db)
    jobs = await service.get_batch_jobs(batch_id, current_user.id)

    return jobs


@router.post("/{batch_id}/cancel", response_model=BatchJobResponse)
@limiter.limit("20/minute")
async def cancel_batch(
    request: Request,
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a batch job."""
    service = BatchService(db)

    try:
        batch = await service.cancel_batch(batch_id, current_user.id)
        return batch
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
