"""Batch processing schemas."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class BatchJobItemRequest(BaseModel):
    """Single job request in a batch."""
    provider: str = Field(..., description="Provider name (gemini, openai, etc.)")
    model: str = Field(..., description="Model identifier")
    job_type: str = Field(..., description="Job type (image_generate, video_generate, etc.)")
    input_params: Dict[str, Any] = Field(..., description="Job parameters")


class BatchJobCreate(BaseModel):
    """Schema for creating a batch job."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    batch_type: str = Field(..., description="Batch type (image, video, or mixed)")
    jobs: List[BatchJobItemRequest] = Field(..., min_items=1, max_items=100, description="List of jobs to process")
    batch_config: Dict[str, Any] = Field(default={}, description="Configuration applied to all jobs")


class BatchJobResponse(BaseModel):
    """Schema for batch job response."""
    id: UUID
    user_id: UUID
    name: Optional[str]
    description: Optional[str]
    batch_type: str
    status: str
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_cost_usd: Optional[float]
    job_ids: List[UUID]
    error_message: Optional[str]
    batch_config: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchJobProgress(BaseModel):
    """Batch job progress information."""
    id: UUID
    status: str
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    progress_percentage: float
    estimated_cost_usd: Optional[float]


class BatchJobListResponse(BaseModel):
    """List of batch jobs."""
    items: List[BatchJobResponse]
    total: int
    limit: int
    offset: int
