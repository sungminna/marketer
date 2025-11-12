"""Video generation API endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserAPIKey
from app.services.video_service import VideoService
from app.schemas.video import (
    VideoGenerateRequest,
    VideoFromImageRequest,
    VideoBackgroundRemoveRequest,
    VideoGenerateResponse,
)
from app.schemas.image import JobStatusResponse
from app.workers.video_worker import process_video_job_task

router = APIRouter(prefix="/api/v1/videos", tags=["videos"])


@router.post("/generate", response_model=VideoGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate video from text prompt.

    Supports Veo 3.1 and Sora 2 models with various cinematography options.
    """
    # Check API key
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider == request.provider,
            UserAPIKey.is_active == True,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active API key found for provider: {request.provider}",
        )

    # Create service
    service = VideoService(db)

    # Prepare input params
    input_params = request.dict()
    input_params["resource_type"] = "video"

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="video_generate",
        provider=request.provider,
        model=request.model,
        input_params=input_params,
    )

    # Estimate cost
    estimated_cost = service.estimate_cost(input_params)

    # Queue background task
    background_tasks.add_task(
        process_video_job_task,
        str(job.id),
        api_key.api_key_encrypted,
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": estimated_cost,
    }


@router.post("/from-image", response_model=VideoGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video_from_images(
    request: VideoFromImageRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate video from reference images.

    Supports up to 3 reference images with smooth transitions.
    """
    # Check API key
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider == request.provider,
            UserAPIKey.is_active == True,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No active API key found for provider: {request.provider}",
        )

    # Validate image count
    if len(request.input_images) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 reference images allowed",
        )

    # Create service
    service = VideoService(db)

    # Prepare input params
    input_params = request.dict()
    input_params["resource_type"] = "video"

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="image_to_video",
        provider=request.provider,
        model=request.model,
        input_params=input_params,
    )

    # Estimate cost
    estimated_cost = service.estimate_cost(input_params)

    # Queue background task
    background_tasks.add_task(
        process_video_job_task,
        str(job.id),
        api_key.api_key_encrypted,
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": estimated_cost,
    }


@router.post("/remove-background", response_model=VideoGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def remove_video_background(
    request: VideoBackgroundRemoveRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove background from video.

    Uses external video background removal service.
    """
    # Create service
    service = VideoService(db)

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="video_bg_remove",
        provider="external",
        model="videobgremover",
        input_params=request.dict(),
    )

    # Queue background task
    background_tasks.add_task(
        process_video_job_task,
        str(job.id),
        "",  # No API key needed for this provider
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": 0.50,  # Rough estimate
    }


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the status of a video generation job."""
    service = VideoService(db)
    job = await service.get_job(job_id, current_user.id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's video generation jobs."""
    service = VideoService(db)
    jobs = await service.list_jobs(current_user.id, limit, offset)

    return jobs
