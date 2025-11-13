"""Template schemas."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class TemplateBase(BaseModel):
    """Base template schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_type: str = Field(..., description="Template type (image or video)")
    job_type: str = Field(..., description="Job type (image_generate, video_generate, etc.)")
    provider: str = Field(..., description="Provider name")
    model: str = Field(..., description="Model identifier")
    config: Dict[str, Any] = Field(..., description="Template configuration")
    is_public: bool = Field(default=False, description="Make template public for other users")
    is_active: bool = Field(default=True)
    tags: List[str] = Field(default=[], description="Tags for categorization")


class TemplateCreate(TemplateBase):
    """Schema for creating a template."""
    pass


class TemplateUpdate(BaseModel):
    """Schema for updating a template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class TemplateResponse(TemplateBase):
    """Schema for template response."""
    id: UUID
    user_id: UUID
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """List of templates."""
    items: List[TemplateResponse]
    total: int
    limit: int
    offset: int


class TemplateUsageRequest(BaseModel):
    """Request to use a template."""
    template_id: UUID = Field(..., description="Template ID to use")
    overrides: Dict[str, Any] = Field(default={}, description="Override template config values")
