"""Sora provider implementation."""
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.services.providers.base import BaseProvider


class SoraProvider(BaseProvider):
    """Sora 2 video generation provider (part of OpenAI)."""

    PRICING = {
        "sora-2": {
            "720x1280": 0.10,  # $0.10 per second
            "1024x1792": 0.50,  # $0.50 per second (pro)
        },
    }

    def __init__(self, api_key: str):
        """Initialize Sora provider."""
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """Sora doesn't support image generation."""
        raise NotImplementedError("Sora doesn't support image generation")

    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """Sora doesn't support image editing."""
        raise NotImplementedError("Sora doesn't support image editing")

    async def generate_video(self, params: Dict[str, Any]) -> str:
        """
        Generate video using Sora 2.

        Args:
            params: Dictionary with prompt, length, resolution, aspect_ratio, etc.

        Returns:
            Video URL
        """
        prompt = params.get("prompt", "")
        length = params.get("length", 4)
        aspect_ratio = params.get("aspect_ratio", "16:9")
        resolution = params.get("resolution", "720p")
        model = params.get("model", "sora-2")

        # Enhance prompt with cinematography
        enhanced_prompt = self._enhance_video_prompt(prompt, params)

        # Map resolution and aspect ratio to size
        size_map = {
            ("16:9", "720p"): "720x1280",
            ("16:9", "1080p"): "1024x1792",
            ("9:16", "720p"): "1280x720",
            ("9:16", "1080p"): "1792x1024",
            ("1:1", "720p"): "720x720",
            ("1:1", "1080p"): "1024x1024",
        }
        size = size_map.get((aspect_ratio, resolution), "720x1280")

        # Generate video with Sora
        response = await self.client.videos.generate(
            model=model,
            prompt=enhanced_prompt,
            length=length,
            size=size,
        )

        # Return video URL
        return response.url if hasattr(response, 'url') else ""

    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """
        Generate video from reference images using Sora.

        Args:
            params: Dictionary with input_images, video_config, etc.

        Returns:
            Video URL
        """
        input_images = params.get("input_images", [])
        length = params.get("length", 8)
        aspect_ratio = params.get("aspect_ratio", "16:9")
        resolution = params.get("resolution", "720p")
        motion_type = params.get("motion_type", "camera_pan")
        transition_style = params.get("transition_style", "fade")

        # Build prompt from images and motion
        prompt = f"Create smooth video with {motion_type} and {transition_style} transitions"

        # Map resolution
        size_map = {
            ("16:9", "720p"): "720x1280",
            ("16:9", "1080p"): "1024x1792",
        }
        size = size_map.get((aspect_ratio, resolution), "720x1280")

        # Extract image URLs
        image_refs = [img.get("url") for img in input_images]

        # Generate with Sora (image-to-video)
        response = await self.client.videos.generate(
            model="sora-2",
            prompt=prompt,
            length=length,
            size=size,
            images=image_refs,  # Reference images
        )

        return response.url if hasattr(response, 'url') else ""

    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """Calculate cost for Sora usage."""
        if resource_type == "video":
            model = kwargs.get("model", "sora-2")
            resolution = kwargs.get("resolution", "720x1280")

            # Determine pricing tier
            if "1024x1792" in resolution or "1792x1024" in resolution:
                # Pro resolution
                cost_per_sec = self.PRICING["sora-2"]["1024x1792"]
            else:
                # Standard resolution
                cost_per_sec = self.PRICING["sora-2"]["720x1280"]

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
                parts.append(f"{cinematography['shot_type']} shot")
            if "lighting" in cinematography:
                parts.append(f"{cinematography['lighting']} lighting")
            if "color_grading" in cinematography:
                parts.append(f"{cinematography['color_grading']} color grading")

            if parts:
                enhanced += f". {', '.join(parts)}"

        # Add brand elements if specified
        brand_elements = params.get("brand_elements", {})
        if brand_elements:
            if brand_elements.get("intro_text"):
                enhanced = f"Start with text: {brand_elements['intro_text']}. " + enhanced
            if brand_elements.get("outro_text"):
                enhanced += f". End with text: {brand_elements['outro_text']}"

        return enhanced
