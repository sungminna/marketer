"""Batch processing service."""
import uuid
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.batch import BatchJob
from app.models.job import GenerationJob
from app.models.user import UserAPIKey
from app.services.image_service import ImageService
from app.services.video_service import VideoService
from app.core.security import api_key_manager


class BatchService:
    """Service for batch processing operations."""

    def __init__(self, db: AsyncSession):
        """Initialize batch service."""
        self.db = db
        self.image_service = ImageService(db)
        self.video_service = VideoService(db)

    async def create_batch(
        self,
        user_id: uuid.UUID,
        name: str,
        description: str,
        batch_type: str,
        jobs_data: List[Dict[str, Any]],
        batch_config: Dict[str, Any],
    ) -> BatchJob:
        """
        Create a new batch job.

        Args:
            user_id: User ID
            name: Batch name
            description: Batch description
            batch_type: Type of batch (image, video, mixed)
            jobs_data: List of job specifications
            batch_config: Configuration applied to all jobs

        Returns:
            Created BatchJob
        """
        # Create batch record
        batch = BatchJob(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            batch_type=batch_type,
            status="pending",
            total_jobs=len(jobs_data),
            batch_config=batch_config,
        )

        self.db.add(batch)
        await self.db.commit()
        await self.db.refresh(batch)

        # Create individual jobs
        job_ids = []
        for job_data in jobs_data:
            # Merge batch config with job params
            input_params = {**batch_config, **job_data.get("input_params", {})}

            # Determine which service to use
            if job_data["job_type"].startswith("image"):
                job = await self.image_service.create_job(
                    user_id=user_id,
                    job_type=job_data["job_type"],
                    provider=job_data["provider"],
                    model=job_data["model"],
                    input_params=input_params,
                )
            elif job_data["job_type"].startswith("video"):
                job = await self.video_service.create_job(
                    user_id=user_id,
                    job_type=job_data["job_type"],
                    provider=job_data["provider"],
                    model=job_data["model"],
                    input_params=input_params,
                )
            else:
                raise ValueError(f"Unsupported job type: {job_data['job_type']}")

            job_ids.append(job.id)

        # Update batch with job IDs
        batch.job_ids = job_ids
        await self.db.commit()
        await self.db.refresh(batch)

        return batch

    async def process_batch(
        self,
        batch_id: uuid.UUID,
    ) -> BatchJob:
        """
        Process all jobs in a batch.

        Args:
            batch_id: Batch ID to process

        Returns:
            Updated BatchJob
        """
        # Get batch
        result = await self.db.execute(
            select(BatchJob).where(BatchJob.id == batch_id)
        )
        batch = result.scalar_one()

        try:
            # Update status to processing
            batch.status = "processing"
            await self.db.commit()

            # Get all jobs in batch
            jobs_result = await self.db.execute(
                select(GenerationJob).where(
                    GenerationJob.id.in_(batch.job_ids)
                )
            )
            jobs = jobs_result.scalars().all()

            # Process each job
            completed = 0
            failed = 0
            total_cost = 0.0

            for job in jobs:
                try:
                    # Get user API key for provider
                    api_key_result = await self.db.execute(
                        select(UserAPIKey).where(
                            UserAPIKey.user_id == batch.user_id,
                            UserAPIKey.provider == job.provider
                        )
                    )
                    user_api_key = api_key_result.scalar_one_or_none()

                    if not user_api_key:
                        job.status = "failed"
                        job.error_message = f"API key not found for provider: {job.provider}"
                        await self.db.commit()
                        failed += 1
                        continue

                    # Process job based on type
                    if job.job_type.startswith("image"):
                        await self.image_service.process_generation_job(
                            job.id,
                            user_api_key.api_key_encrypted
                        )
                    elif job.job_type.startswith("video"):
                        await self.video_service.process_generation_job(
                            job.id,
                            user_api_key.api_key_encrypted
                        )

                    # Refresh job to get updated status
                    await self.db.refresh(job)

                    if job.status == "completed":
                        completed += 1
                        if job.cost_usd:
                            total_cost += float(job.cost_usd)
                    else:
                        failed += 1

                except Exception as e:
                    failed += 1
                    # Update job with error
                    job.status = "failed"
                    job.error_message = str(e)
                    await self.db.commit()

            # Update batch status
            batch.completed_jobs = completed
            batch.failed_jobs = failed
            batch.total_cost_usd = total_cost

            if failed == 0:
                batch.status = "completed"
            elif completed == 0:
                batch.status = "failed"
            else:
                batch.status = "partial"

            batch.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(batch)

            # Send webhook notification
            await self._send_webhook_notification(batch)

            return batch

        except Exception as e:
            # Update batch with error
            batch.status = "failed"
            batch.error_message = str(e)
            await self.db.commit()

            # Send webhook notification
            await self._send_webhook_notification(batch)

            raise

    async def _send_webhook_notification(self, batch: BatchJob):
        """Send webhook notification for batch completion."""
        try:
            from app.services.webhook_service import webhook_service

            event_type = "batch.completed" if batch.status in ["completed", "partial"] else "batch.failed"

            payload = {
                "batch_id": str(batch.id),
                "batch_type": batch.batch_type,
                "status": batch.status,
                "total_jobs": batch.total_jobs,
                "completed_jobs": batch.completed_jobs,
                "failed_jobs": batch.failed_jobs,
                "total_cost_usd": float(batch.total_cost_usd) if batch.total_cost_usd else 0,
                "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            }

            if batch.error_message:
                payload["error_message"] = batch.error_message

            await webhook_service.send_event_to_user_webhooks(
                self.db,
                str(batch.user_id),
                event_type,
                payload
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send webhook for batch {batch.id}: {e}")

    async def get_batch(self, batch_id: uuid.UUID, user_id: uuid.UUID) -> BatchJob:
        """Get batch by ID."""
        result = await self.db.execute(
            select(BatchJob).where(
                BatchJob.id == batch_id,
                BatchJob.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_batches(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[BatchJob], int]:
        """List user's batch jobs with pagination."""
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(BatchJob).where(
                BatchJob.user_id == user_id
            )
        )
        total = count_result.scalar()

        # Get batches
        result = await self.db.execute(
            select(BatchJob)
            .where(BatchJob.user_id == user_id)
            .order_by(BatchJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        batches = result.scalars().all()

        return batches, total

    async def get_batch_jobs(
        self,
        batch_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> List[GenerationJob]:
        """Get all jobs in a batch."""
        # Verify batch ownership
        batch = await self.get_batch(batch_id, user_id)
        if not batch:
            return []

        # Get all jobs
        result = await self.db.execute(
            select(GenerationJob).where(
                GenerationJob.id.in_(batch.job_ids)
            ).order_by(GenerationJob.created_at)
        )
        return result.scalars().all()

    async def cancel_batch(self, batch_id: uuid.UUID, user_id: uuid.UUID) -> BatchJob:
        """Cancel a pending batch job."""
        batch = await self.get_batch(batch_id, user_id)

        if not batch:
            raise ValueError("Batch not found")

        if batch.status not in ["pending", "processing"]:
            raise ValueError(f"Cannot cancel batch with status: {batch.status}")

        batch.status = "failed"
        batch.error_message = "Cancelled by user"
        batch.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(batch)

        return batch
