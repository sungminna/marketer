"""Veo provider implementation."""
from typing import Dict, Any, List
from google.cloud import aiplatform
from app.services.providers.base import BaseProvider


class VeoProvider(BaseProvider):
    """Veo 3.1 video generation provider."""

    PRICING = {
        "veo-3.1-standard": 0.40,  # $0.40 per second (with audio)
        "veo-3.1-fast": 0.15,  # $0.15 per second (with audio)
    }

    def __init__(self, api_key: str, project_id: str = None, location: str = "us-central1"):
        """Initialize Veo provider."""
        super().__init__(api_key)
        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI
        if project_id:
            aiplatform.init(project=project_id, location=location)

    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """Veo doesn't support image generation."""
        raise NotImplementedError("Veo doesn't support image generation")

    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """Veo doesn't support image editing."""
        raise NotImplementedError("Veo doesn't support image editing")

    async def generate_video(self, params: Dict[str, Any]) -> str:
        """
        Generate video using Veo 3.1.

        Args:
            params: Dictionary with prompt, resolution, audio, etc.

        Returns:
            Video URL or base64 string
        """
        prompt = params.get("prompt", "")
        resolution = params.get("resolution", "720p")
        audio = params.get("audio", True)
        model = params.get("model", "veo-3.1-fast-generate-preview-001")

        # Enhance prompt with cinematography
        enhanced_prompt = self._enhance_video_prompt(prompt, params)

        # Map resolution to size
        size_map = {
            "720p": "720x1280",  # 9:16 aspect ratio
            "1080p": "1280x720",  # 16:9 aspect ratio
        }
        video_size = size_map.get(resolution, "720x1280")

        # Generate video with Veo
        veo_model = aiplatform.VideoGenerationModel.from_pretrained(model)

        response = await veo_model.generate_video_async(
            prompt=enhanced_prompt,
            resolution=video_size,
            include_audio=audio,
        )

        # Extract video URL or bytes
        video_url = response.video_url if hasattr(response, 'video_url') else ""

        return video_url

    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """
        Generate video from reference images using Veo.

        Args:
            params: Dictionary with input_images, video_config, etc.

        Returns:
            Video URL
        """
        input_images = params.get("input_images", [])
        resolution = params.get("resolution", "720p")
        audio = params.get("audio", True)
        motion_type = params.get("motion_type", "camera_pan")

        # Veo supports up to 3 reference images
        if len(input_images) > 3:
            input_images = input_images[:3]

        # Build prompt
        prompt = f"Generate smooth video with {motion_type}"

        # Map resolution
        size_map = {
            "720p": "720x1280",
            "1080p": "1280x720",
        }
        video_size = size_map.get(resolution, "720x1280")

        # Generate with reference images
        veo_model = aiplatform.VideoGenerationModel.from_pretrained(
            "veo-3.1-fast-generate-preview-001"
        )

        # Extract image URLs
        image_refs = [img.get("url") for img in input_images]

        response = await veo_model.generate_video_async(
            prompt=prompt,
            resolution=video_size,
            reference_images=image_refs,
            include_audio=audio,
        )

        video_url = response.video_url if hasattr(response, 'video_url') else ""

        return video_url

    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """Calculate cost for Veo usage."""
        if resource_type == "video":
            model = kwargs.get("model", "veo-3.1-fast")
            audio = kwargs.get("audio", True)

            # Get base cost per second
            if "standard" in model:
                cost_per_sec = self.PRICING["veo-3.1-standard"]
            else:
                cost_per_sec = self.PRICING["veo-3.1-fast"]

            # Quantity is video seconds
            return quantity * cost_per_sec

        return 0.0

    def supports_feature(self, feature: str) -> bool:
        """Check feature support."""
        supported = {"video_generation", "video_from_images"}
        return feature in supported

    def _enhance_video_prompt(self, prompt: str, params: Dict[str, Any]) -> str:
        """Enhance video prompt with cinematography settings."""
        enhanced = prompt

        cinematography = params.get("cinematography", {})
        if cinematography:
            parts = []
            if "camera_movement" in cinematography:
                parts.append(f"camera movement: {cinematography['camera_movement']}")
            if "shot_type" in cinematography:
                parts.append(f"shot type: {cinematography['shot_type']}")
            if "lighting" in cinematography:
                parts.append(f"lighting: {cinematography['lighting']}")
            if "color_grading" in cinematography:
                parts.append(f"color grading: {cinematography['color_grading']}")

            if parts:
                enhanced += f". {', '.join(parts)}"

        return enhanced
