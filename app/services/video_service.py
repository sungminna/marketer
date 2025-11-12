"""Video generation service."""
import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.job import GenerationJob
from app.models.usage import UsageLog
from app.services.providers import VeoProvider, SoraProvider, OpenAIProvider
from app.services.cost_calculator import CostCalculator
from app.services.storage_service import storage_service
from app.core.security import api_key_manager
import httpx


class VideoService:
    """Service for video generation operations."""

    def __init__(self, db: AsyncSession):
        """Initialize video service."""
        self.db = db

    async def create_job(
        self,
        user_id: uuid.UUID,
        job_type: str,
        provider: str,
        model: str,
        input_params: Dict[str, Any],
    ) -> GenerationJob:
        """Create a new video generation job."""
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
        """Process a video generation job."""
        # Get job
        result = await self.db.execute(
            select(GenerationJob).where(GenerationJob.id == job_id)
        )
        job = result.scalar_one()

        try:
            # Update status to processing
            job.status = "processing"
            await self.db.commit()

            # Decrypt API key
            decrypted_key = api_key_manager.decrypt_key(user_api_key)

            # Get provider
            provider = self._get_provider(job.provider, decrypted_key)

            # Generate video
            if job.job_type == "video_generate":
                video_url = await provider.generate_video(job.input_params)
            elif job.job_type == "image_to_video":
                video_url = await provider.video_from_images(job.input_params)
            elif job.job_type == "video_bg_remove":
                video_url = await self._remove_video_background(job.input_params)
            else:
                raise ValueError(f"Unsupported job type: {job.job_type}")

            # Download and upload to S3 if needed
            if video_url.startswith("http"):
                video_bytes = await self._download_video(video_url)
                s3_url = await storage_service.upload_video(
                    video_bytes,
                    str(job.user_id),
                    str(job.id),
                    format="mp4",
                )
            else:
                s3_url = video_url

            # Calculate cost
            duration = job.input_params.get("length", 4)
            resolution = job.input_params.get("resolution", "720p")

            cost = provider.calculate_cost(
                "video",
                duration,
                resolution=resolution,
                model=job.model,
            )

            # Update job
            job.output_urls = [s3_url]
            job.cost_usd = cost
            job.status = "completed"
            job.completed_at = datetime.utcnow()

            # Extract metadata
            job.metadata = {
                "duration_seconds": duration,
                "resolution": resolution,
                "aspect_ratio": job.input_params.get("aspect_ratio", "16:9"),
                "has_audio": job.input_params.get("audio", True),
                "generated_at": job.completed_at.isoformat(),
            }

            await self.db.commit()

            # Log usage
            await self._log_usage(job, duration, cost)

            return job

        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.error_message = str(e)
            await self.db.commit()
            raise

    async def _remove_video_background(self, params: Dict[str, Any]) -> str:
        """
        Remove video background using external API.

        Args:
            params: Dictionary with video_url, output_background, etc.

        Returns:
            Processed video URL
        """
        # This is a placeholder for video background removal
        # Actual implementation would use a service like videobgremover.com

        video_url = params.get("video_url")
        output_bg = params.get("output_background", {})

        # Example API call (adjust based on actual service)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.videobgremover.com/v1/remove",
                json={
                    "video_url": video_url,
                    "background_type": output_bg.get("type", "transparent"),
                    "background_color": output_bg.get("color"),
                },
                headers={
                    "Authorization": f"Bearer {params.get('api_key', '')}",
                },
            )
            response.raise_for_status()
            result = response.json()

            return result.get("output_url", "")

    async def _download_video(self, url: str) -> bytes:
        """Download video from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def _log_usage(
        self,
        job: GenerationJob,
        duration: int,
        cost: float,
    ):
        """Log usage for billing."""
        usage_log = UsageLog(
            id=uuid.uuid4(),
            user_id=job.user_id,
            job_id=job.id,
            provider=job.provider,
            resource_type="video",
            quantity=duration,
            cost_usd=cost,
        )

        self.db.add(usage_log)
        await self.db.commit()

    def _get_provider(self, provider_name: str, api_key: str):
        """Get provider instance."""
        if provider_name == "veo":
            return VeoProvider(api_key)
        elif provider_name == "sora":
            return SoraProvider(api_key)
        elif provider_name == "openai":
            return OpenAIProvider(api_key)
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
