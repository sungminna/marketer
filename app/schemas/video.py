"""Video generation-related Pydantic schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class VideoConfig(BaseModel):
    """Video generation configuration."""

    length: Optional[int] = Field(4, ge=4, le=20, description="Video length in seconds")
    resolution: Optional[str] = Field("720p", description="720p|1080p")
    aspect_ratio: Optional[str] = Field("16:9", description="16:9|9:16|1:1")
    fps: Optional[int] = Field(24, description="Frames per second")
    audio: Optional[bool] = Field(True, description="Include audio")


class Cinematography(BaseModel):
    """Cinematography settings for video."""

    camera_movement: Optional[str] = Field("static", description="static|pan|tilt|zoom|dolly")
    shot_type: Optional[str] = Field("medium", description="wide|medium|close_up|extreme_close_up")
    lighting: Optional[str] = Field("natural", description="natural|studio|cinematic|soft")
    color_grading: Optional[str] = Field("neutral", description="neutral|warm|cool|vibrant")


class BrandElements(BaseModel):
    """Brand elements for video overlay."""

    logo_overlay: Optional[bool] = Field(False, description="Add logo overlay")
    intro_text: Optional[str] = Field(None, description="Text for intro")
    outro_text: Optional[str] = Field(None, description="Text for outro")


class VideoGenerateRequest(BaseModel):
    """Request schema for text-to-video generation."""

    provider: str = Field(..., description="veo|sora")
    model: str = Field(..., description="Model identifier")
    prompt: str = Field(..., min_length=1, description="Text prompt for video generation")
    video_config: VideoConfig = Field(default_factory=VideoConfig)
    cinematography: Optional[Cinematography] = None
    brand_elements: Optional[BrandElements] = None


class InputImage(BaseModel):
    """Input image for image-to-video generation."""

    url: str = Field(..., description="Image URL or base64")
    position: str = Field(..., description="start|middle|end")


class VideoFromImageRequest(BaseModel):
    """Request schema for image-to-video generation."""

    provider: str = Field(..., description="veo|sora")
    model: str = Field(..., description="Model identifier")
    input_images: List[InputImage] = Field(..., max_items=3, description="Reference images (max 3)")
    transition_style: Optional[str] = Field("fade", description="fade|dissolve|cut|morph")
    motion_type: Optional[str] = Field("camera_pan", description="camera_pan|zoom_in|object_motion|parallax")
    video_config: VideoConfig = Field(default_factory=VideoConfig)


class OutputBackground(BaseModel):
    """Output background configuration for video."""

    type: str = Field(..., description="transparent|solid|custom")
    color: Optional[str] = Field(None, description="Background color (hex) if solid")
    custom_image: Optional[str] = Field(None, description="Custom background image URL if custom")


class VideoBackgroundRemoveRequest(BaseModel):
    """Request schema for video background removal."""

    video_url: str = Field(..., description="URL of the video to process")
    output_background: OutputBackground
    output_format: Optional[str] = Field("mp4", description="mp4|webm|mov")


class VideoGenerateResponse(BaseModel):
    """Response schema for video generation."""

    job_id: UUID
    status: str
    estimated_cost_usd: Optional[float] = None


class VideoMetadata(BaseModel):
    """Metadata for generated video."""

    duration_seconds: Optional[int] = None
    resolution: Optional[str] = None
    aspect_ratio: Optional[str] = None
    has_audio: Optional[bool] = None
    file_size_mb: Optional[float] = None
