"""Image generation service."""
import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import GenerationJob
from app.models.usage import UsageLog
from app.models.user import UserAPIKey
from app.services.providers import GeminiProvider, OpenAIProvider, ImagenProvider
from app.services.cost_calculator import CostCalculator
from app.services.storage_service import storage_service
from app.core.security import api_key_manager


class ImageService:
    """Service for image generation operations."""

    def __init__(self, db: AsyncSession):
        """Initialize image service."""
        self.db = db

    async def create_job(
        self,
        user_id: uuid.UUID,
        job_type: str,
        provider: str,
        model: str,
        input_params: Dict[str, Any],
    ) -> GenerationJob:
        """
        Create a new generation job.

        Args:
            user_id: User ID
            job_type: Type of job (image_generate, image_edit, etc.)
            provider: Provider name
            model: Model identifier
            input_params: Job parameters

        Returns:
            Created GenerationJob
        """
        job = GenerationJob(
            id=uuid.uuid4(),
            user_id=user_id,
            job_type=job_type,
            provider=provider,
            model=model,
            input_params=input_params,
            status="pending",
        )

        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        return job

    async def process_generation_job(
        self,
        job_id: uuid.UUID,
        user_api_key: str,
    ) -> GenerationJob:
        """
        Process an image generation job.

        Args:
            job_id: Job ID to process
            user_api_key: Encrypted user API key for the provider

        Returns:
            Updated GenerationJob
        """
        # Get job
        result = await self.db.execute(
            select(GenerationJob).where(GenerationJob.id == job_id)
        )
        job = result.scalar_one()

        try:
            # Update status to processing
            job.status = "processing"
            await self.db.commit()

            # Validate and decrypt API key
            if not user_api_key or not user_api_key.strip():
                raise ValueError("Invalid or empty API key provided")

            try:
                decrypted_key = api_key_manager.decrypt_key(user_api_key)
            except Exception as e:
                raise ValueError(f"Failed to decrypt API key: {str(e)}")

            # Get provider
            provider = self._get_provider(job.provider, decrypted_key)

            # Generate images
            if job.job_type == "image_generate":
                image_data = await provider.generate_image(job.input_params)
            elif job.job_type == "image_edit":
                image_data = await provider.edit_image(job.input_params)
            elif job.job_type == "prototype_generate":
                # Use the same generate_image method with enhanced prompts
                image_data = await provider.generate_image(job.input_params)
            else:
                raise ValueError(f"Unsupported job type: {job.job_type}")

            # Upload to S3
            urls = await storage_service.upload_multiple_images(
                image_data,
                str(job.user_id),
                str(job.id),
                format="png",
            )

            # Calculate cost
            quantity = len(image_data)
            cost = provider.calculate_cost(
                "image",
                quantity,
                size=job.input_params.get("size", "1024x1024"),
                quality=job.input_params.get("quality", "medium"),
            )

            # Update job
            job.output_urls = urls
            job.cost_usd = cost
            job.status = "completed"
            job.completed_at = datetime.utcnow()

            # Extract metadata
            job.metadata = {
                "number_of_images": len(urls),
                "format": "png",
                "generated_at": job.completed_at.isoformat(),
            }

            await self.db.commit()

            # Log usage
            await self._log_usage(job, quantity, cost)

            return job

        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error_message = str(e)
            await self.db.commit()
            raise

    async def _log_usage(
        self,
        job: GenerationJob,
        quantity: int,
        cost: float,
    ):
        """Log usage for billing."""
        usage_log = UsageLog(
            id=uuid.uuid4(),
            user_id=job.user_id,
            job_id=job.id,
            provider=job.provider,
            resource_type="image",
            quantity=quantity,
            cost_usd=cost,
        )

        self.db.add(usage_log)
        await self.db.commit()

    def _get_provider(self, provider_name: str, api_key: str):
        """Get provider instance."""
        import json

        if provider_name == "gemini":
            return GeminiProvider(api_key)
        elif provider_name == "openai":
            return OpenAIProvider(api_key)
        elif provider_name == "imagen":
            # For Imagen, API key should be JSON with {api_key, project_id}
            try:
                key_data = json.loads(api_key)
                return ImagenProvider(
                    api_key=key_data.get("api_key", ""),
                    project_id=key_data.get("project_id")
                )
            except (json.JSONDecodeError, KeyError):
                raise ValueError("Imagen requires API key in JSON format: {\"api_key\": \"...\", \"project_id\": \"...\"}")
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def estimate_cost(self, params: Dict[str, Any]) -> float:
        """Estimate cost for job parameters."""
        return CostCalculator.estimate_cost(params)

    async def get_job(self, job_id: uuid.UUID, user_id: uuid.UUID) -> GenerationJob:
        """Get job by ID."""
        result = await self.db.execute(
            select(GenerationJob).where(
                GenerationJob.id == job_id,
                GenerationJob.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[GenerationJob]:
        """List user's jobs."""
        result = await self.db.execute(
            select(GenerationJob)
            .where(GenerationJob.user_id == user_id)
            .order_by(GenerationJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
