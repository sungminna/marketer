"""Image generation-related Pydantic schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class DesignTokens(BaseModel):
    """Design tokens for consistent branding."""

    primary_color: Optional[str] = Field(None, description="Primary brand color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color (hex)")
    tone: Optional[str] = Field(None, description="professional|friendly|bold")
    lighting: Optional[str] = Field(None, description="natural|studio|golden_hour|soft")


class ImageConfig(BaseModel):
    """Image generation configuration."""

    aspect_ratio: Optional[str] = Field(None, description="16:9|1:1|9:16|4:3|3:4")
    size: Optional[str] = Field(None, description="1024x1024|1024x1536|1536x1024")
    quality: Optional[str] = Field("medium", description="low|medium|high")
    background: Optional[str] = Field("auto", description="auto|transparent|solid:#FFFFFF")
    number_of_images: Optional[int] = Field(4, ge=1, le=4, description="Number of images to generate")


class ImageGenerateRequest(BaseModel):
    """Request schema for text-to-image generation."""

    provider: str = Field(..., description="gemini|openai|imagen")
    model: str = Field(..., description="Model identifier")
    prompt: str = Field(..., min_length=1, description="Text prompt for image generation")
    style_preset: Optional[str] = Field(None, description="photoreal|illustration|technical|minimal")
    design_tokens: Optional[DesignTokens] = None
    image_config: ImageConfig = Field(default_factory=ImageConfig)


class EditParams(BaseModel):
    """Parameters for image editing."""

    input_fidelity: Optional[str] = Field("high", description="low|high - preserve faces/logos")
    transformation: str = Field(..., description="Description of the transformation")
    preserve_elements: Optional[List[str]] = Field(default=[], description="Elements to preserve: face, logo, text")


class ImageEditRequest(BaseModel):
    """Request schema for image-to-image editing."""

    provider: str = Field(..., description="gemini|openai")
    base_image: str = Field(..., description="URL or base64 of original image")
    edit_type: str = Field(..., description="style_transfer|pose_change|color_adjust|background_replace")
    reference_image: Optional[str] = Field(None, description="URL or base64 of reference image")
    edit_params: EditParams
    output_config: Optional[ImageConfig] = None


class BrandGuidelines(BaseModel):
    """Brand guidelines for prototype generation."""

    color_palette: List[str] = Field(..., description="List of brand colors (hex)")
    design_system: Optional[str] = Field("material", description="material|ios|custom")
    typography: Optional[str] = Field("modern", description="modern|classic|playful")


class PrototypeContent(BaseModel):
    """Content configuration for prototype."""

    screen_type: Optional[str] = Field(None, description="login|dashboard|profile|settings")
    placeholder_text: bool = Field(True, description="Include placeholder text")
    icon_style: Optional[str] = Field("flat", description="flat|3d|gradient|line")


class PrototypeSpecs(BaseModel):
    """Specifications for prototype generation."""

    device: Optional[str] = Field("iphone14", description="iphone14|ipad|desktop")
    resolution: Optional[str] = Field("750x1334", description="Resolution in pixels")
    export_format: Optional[str] = Field("png", description="png|svg")


class PrototypeGenerateRequest(BaseModel):
    """Request schema for app prototype/icon generation."""

    provider: str = Field(..., description="gemini|openai|imagen")
    asset_type: str = Field(..., description="app_screen|icon|logo|banner")
    app_type: Optional[str] = Field("mobile", description="mobile|web|tablet")
    brand_guidelines: BrandGuidelines
    content: Optional[PrototypeContent] = None
    specifications: Optional[PrototypeSpecs] = None


class ImageGenerateResponse(BaseModel):
    """Response schema for image generation."""

    job_id: UUID
    status: str
    estimated_cost_usd: Optional[float] = None


class JobStatusResponse(BaseModel):
    """Response schema for job status."""

    job_id: UUID
    status: str
    provider: str
    model: str
    output_urls: List[str] = []
    cost_usd: Optional[float] = None
    metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
