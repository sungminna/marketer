"""Template management service."""
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.template import Template
from app.models.job import GenerationJob
from app.services.image_service import ImageService
from app.services.video_service import VideoService


class TemplateService:
    """Service for template management operations."""

    def __init__(self, db: AsyncSession):
        """Initialize template service."""
        self.db = db
        self.image_service = ImageService(db)
        self.video_service = VideoService(db)

    async def create_template(
        self,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str],
        template_type: str,
        job_type: str,
        provider: str,
        model: str,
        config: Dict[str, Any],
        is_public: bool = False,
        is_active: bool = True,
        tags: List[str] = None,
    ) -> Template:
        """Create a new template."""
        template = Template(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            template_type=template_type,
            job_type=job_type,
            provider=provider,
            model=model,
            config=config,
            is_public=is_public,
            is_active=is_active,
            tags=tags or [],
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def get_template(
        self,
        template_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Template]:
        """Get template by ID."""
        query = select(Template).where(Template.id == template_id)

        # If user_id provided, check ownership or public access
        if user_id:
            query = query.where(
                or_(
                    Template.user_id == user_id,
                    Template.is_public == True
                )
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        user_id: uuid.UUID,
        include_public: bool = True,
        template_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Template], int]:
        """List templates with filters."""
        # Build query
        query = select(Template).where(Template.is_active == True)

        # Filter by ownership or public
        if include_public:
            query = query.where(
                or_(
                    Template.user_id == user_id,
                    Template.is_public == True
                )
            )
        else:
            query = query.where(Template.user_id == user_id)

        # Filter by template type
        if template_type:
            query = query.where(Template.template_type == template_type)

        # Filter by tags
        if tags:
            for tag in tags:
                query = query.where(Template.tags.contains([tag]))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Get templates
        query = query.order_by(Template.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        templates = result.scalars().all()

        return templates, total

    async def update_template(
        self,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
        **updates
    ) -> Optional[Template]:
        """Update template."""
        template = await self.get_template(template_id, user_id)

        if not template or template.user_id != user_id:
            return None

        # Update fields
        for field, value in updates.items():
            if value is not None and hasattr(template, field):
                setattr(template, field, value)

        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def delete_template(
        self,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete template (soft delete by setting is_active=False)."""
        template = await self.get_template(template_id, user_id)

        if not template or template.user_id != user_id:
            return False

        template.is_active = False
        await self.db.commit()

        return True

    async def use_template(
        self,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
        overrides: Dict[str, Any] = None,
    ) -> GenerationJob:
        """
        Use a template to create a new generation job.

        Args:
            template_id: Template ID to use
            user_id: User ID creating the job
            overrides: Optional overrides for template config

        Returns:
            Created GenerationJob
        """
        # Get template
        template = await self.get_template(template_id, user_id)

        if not template:
            raise ValueError("Template not found")

        # Merge template config with overrides
        config = {**template.config}
        if overrides:
            config.update(overrides)

        # Create job based on template type
        if template.template_type == "image" or template.job_type.startswith("image"):
            job = await self.image_service.create_job(
                user_id=user_id,
                job_type=template.job_type,
                provider=template.provider,
                model=template.model,
                input_params=config,
            )
        elif template.template_type == "video" or template.job_type.startswith("video"):
            job = await self.video_service.create_job(
                user_id=user_id,
                job_type=template.job_type,
                provider=template.provider,
                model=template.model,
                input_params=config,
            )
        else:
            raise ValueError(f"Unsupported template type: {template.template_type}")

        # Increment usage count
        template.usage_count += 1
        await self.db.commit()

        return job

    async def get_popular_templates(
        self,
        limit: int = 10,
        template_type: Optional[str] = None,
    ) -> List[Template]:
        """Get most popular public templates."""
        query = select(Template).where(
            Template.is_public == True,
            Template.is_active == True,
        )

        if template_type:
            query = query.where(Template.template_type == template_type)

        query = query.order_by(Template.usage_count.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
