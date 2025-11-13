"""Image generation API endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserAPIKey
from app.models.job import GenerationJob
from app.services.image_service import ImageService
from app.schemas.image import (
    ImageGenerateRequest,
    ImageEditRequest,
    PrototypeGenerateRequest,
    ImageGenerateResponse,
    JobStatusResponse,
)
from app.workers.image_worker import process_image_job_background

router = APIRouter(prefix="/api/v1/images", tags=["images"])


@router.post("/generate", response_model=ImageGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_images(
    request: ImageGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate images from text prompt.

    This endpoint creates an async job and returns immediately with a job_id.
    Use the /jobs/{job_id} endpoint to check the status.
    """
    # Check if user has API key for provider
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
    service = ImageService(db)

    # Prepare input params
    input_params = request.model_dump()
    input_params["resource_type"] = "image"

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="image_generate",
        provider=request.provider,
        model=request.model,
        input_params=input_params,
    )

    # Estimate cost
    estimated_cost = service.estimate_cost(input_params)

    # Queue background task
    background_tasks.add_task(
        process_image_job_background,
        str(job.id),
        api_key.api_key_encrypted,
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": estimated_cost,
    }


@router.post("/edit", response_model=ImageGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def edit_image(
    request: ImageEditRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edit an existing image.

    Supports style transfer, pose changes, color adjustments, and background replacement.
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
    service = ImageService(db)

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="image_edit",
        provider=request.provider,
        model="default",  # Model determined by provider
        input_params=request.model_dump(),
    )

    # Queue background task
    background_tasks.add_task(
        process_image_job_background,
        str(job.id),
        api_key.api_key_encrypted,
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": 0.05,  # Rough estimate
    }


@router.post("/prototype", response_model=ImageGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_prototype(
    request: PrototypeGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate app prototype, icon, logo, or banner.

    Designed for creating mockups and design assets with brand guidelines.
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

    # Build enhanced prompt for prototype
    prompt = _build_prototype_prompt(request)

    # Create service
    service = ImageService(db)

    # Prepare input params
    input_params = request.model_dump()
    input_params["prompt"] = prompt
    input_params["resource_type"] = "image"

    # Create job
    job = await service.create_job(
        user_id=current_user.id,
        job_type="prototype_generate",
        provider=request.provider,
        model="default",
        input_params=input_params,
    )

    # Queue background task
    background_tasks.add_task(
        process_image_job_background,
        str(job.id),
        api_key.api_key_encrypted,
    )

    return {
        "job_id": job.id,
        "status": "pending",
        "estimated_cost_usd": 0.04,
    }


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the status of an image generation job."""
    service = ImageService(db)
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
    """List user's image generation jobs."""
    service = ImageService(db)
    jobs = await service.list_jobs(current_user.id, limit, offset)

    return jobs


def _build_prototype_prompt(request: PrototypeGenerateRequest) -> str:
    """Build enhanced prompt for prototype generation."""
    asset_type = request.asset_type
    app_type = request.app_type
    brand = request.brand_guidelines

    prompt_parts = []

    # Asset type
    if asset_type == "app_screen":
        prompt_parts.append(f"Modern {app_type} app screen")
        if request.content and request.content.screen_type:
            prompt_parts.append(f"for {request.content.screen_type}")
    elif asset_type == "icon":
        prompt_parts.append("App icon design")
    elif asset_type == "logo":
        prompt_parts.append("Professional logo design")
    elif asset_type == "banner":
        prompt_parts.append("Marketing banner design")

    # Brand guidelines
    if brand.color_palette:
        colors = ", ".join(brand.color_palette)
        prompt_parts.append(f"using colors: {colors}")

    if brand.design_system:
        prompt_parts.append(f"following {brand.design_system} design system")

    if brand.typography:
        prompt_parts.append(f"with {brand.typography} typography")

    # Icon style
    if request.content and request.content.icon_style:
        prompt_parts.append(f"{request.content.icon_style} style")

    return ". ".join(prompt_parts)
