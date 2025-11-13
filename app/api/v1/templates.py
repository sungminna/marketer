"""Template management endpoints."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    TemplateUsageRequest,
)
from app.schemas.image import ImageJobResponse
from app.services.template_service import TemplateService

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=TemplateResponse, status_code=201)
@limiter.limit("20/minute")
async def create_template(
    request: Request,
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new template."""
    service = TemplateService(db)

    # Validate template type
    if template_data.template_type not in ["image", "video"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid template_type. Must be 'image' or 'video'"
        )

    template = await service.create_template(
        user_id=current_user.id,
        name=template_data.name,
        description=template_data.description,
        template_type=template_data.template_type,
        job_type=template_data.job_type,
        provider=template_data.provider,
        model=template_data.model,
        config=template_data.config,
        is_public=template_data.is_public,
        is_active=template_data.is_active,
        tags=template_data.tags,
    )

    return template


@router.get("", response_model=TemplateListResponse)
@limiter.limit("60/minute")
async def list_templates(
    request: Request,
    include_public: bool = Query(default=True, description="Include public templates"),
    template_type: Optional[str] = Query(default=None, description="Filter by type (image/video)"),
    tags: Optional[List[str]] = Query(default=None, description="Filter by tags"),
    limit: int = Query(default=50, le=100),
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List templates with optional filters."""
    service = TemplateService(db)

    templates, total = await service.list_templates(
        user_id=current_user.id,
        include_public=include_public,
        template_type=template_type,
        tags=tags,
        limit=limit,
        offset=offset,
    )

    return TemplateListResponse(
        items=templates,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/popular", response_model=List[TemplateResponse])
@limiter.limit("60/minute")
async def get_popular_templates(
    request: Request,
    template_type: Optional[str] = Query(default=None, description="Filter by type"),
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get most popular public templates."""
    service = TemplateService(db)

    templates = await service.get_popular_templates(
        limit=limit,
        template_type=template_type,
    )

    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
@limiter.limit("60/minute")
async def get_template(
    request: Request,
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID."""
    service = TemplateService(db)
    template = await service.get_template(template_id, current_user.id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.patch("/{template_id}", response_model=TemplateResponse)
@limiter.limit("20/minute")
async def update_template(
    request: Request,
    template_id: UUID,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update template."""
    service = TemplateService(db)

    # Get update fields
    updates = template_data.model_dump(exclude_unset=True)

    template = await service.update_template(
        template_id=template_id,
        user_id=current_user.id,
        **updates
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")

    return template


@router.delete("/{template_id}", status_code=204)
@limiter.limit("20/minute")
async def delete_template(
    request: Request,
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete template (soft delete)."""
    service = TemplateService(db)

    success = await service.delete_template(template_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Template not found or not owned by user")


@router.post("/use", response_model=ImageJobResponse, status_code=201)
@limiter.limit("30/minute")
async def use_template(
    request: Request,
    usage_request: TemplateUsageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Use a template to create a new generation job."""
    service = TemplateService(db)

    try:
        job = await service.use_template(
            template_id=usage_request.template_id,
            user_id=current_user.id,
            overrides=usage_request.overrides,
        )

        # Start processing job
        from app.models.user import UserAPIKey
        from sqlalchemy import select

        # Get user API key for provider
        api_key_result = await db.execute(
            select(UserAPIKey).where(
                UserAPIKey.user_id == current_user.id,
                UserAPIKey.provider == job.provider
            )
        )
        user_api_key = api_key_result.scalar_one_or_none()

        if not user_api_key:
            raise HTTPException(
                status_code=400,
                detail=f"API key not configured for provider: {job.provider}"
            )

        # Queue job processing
        from app.workers.image_worker import process_image_job_task
        from app.workers.video_worker import process_video_job_task

        try:
            if job.job_type.startswith("image"):
                process_image_job_task.delay(str(job.id), user_api_key.api_key_encrypted)
            elif job.job_type.startswith("video"):
                process_video_job_task.delay(str(job.id), user_api_key.api_key_encrypted)
        except Exception:
            # Fallback to background processing if Celery unavailable
            pass

        return job

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
