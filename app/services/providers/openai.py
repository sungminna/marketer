"""OpenAI provider implementation."""
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.services.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI GPT Image 1 and Sora provider."""

    PRICING = {
        "gpt-image-1": {
            ("1024x1024", "medium"): 0.042,
            ("1024x1024", "high"): 0.167,
            ("1024x1536", "medium"): 0.063,
            ("1024x1536", "high"): 0.250,
            ("1536x1024", "medium"): 0.063,
            ("1536x1024", "high"): 0.250,
        },
        "sora-2": {
            "720x1280": 0.10,  # per second
            "1024x1792": 0.50,  # per second (pro)
        },
    }

    def __init__(self, api_key: str):
        """Initialize OpenAI provider."""
        super().__init__(api_key)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Generate images using GPT Image 1.

        Args:
            params: Dictionary with prompt, size, quality, background, etc.

        Returns:
            List of image URLs
        """
        prompt = params.get("prompt", "")
        size = params.get("size", "1024x1024")
        quality = params.get("quality", "medium")
        background = params.get("background", "auto")
        n = params.get("number_of_images", 1)

        # Enhance prompt with style and design tokens
        enhanced_prompt = self._enhance_prompt(prompt, params)

        # Generate images
        response = await self.client.images.generate(
            model="gpt-image-1",
            prompt=enhanced_prompt,
            size=size,
            quality=quality,
            background=background,
            n=min(n, 4),  # Max 4 images
        )

        # Extract URLs
        return [img.url for img in response.data]

    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Edit image using OpenAI's image editing.

        Args:
            params: Dictionary with base_image, transformation, etc.

        Returns:
            List of edited image URLs
        """
        base_image = params.get("base_image", "")
        transformation = params.get("transformation", "")
        input_fidelity = params.get("input_fidelity", "high")
        size = params.get("size", "1024x1024")

        # Note: This uses OpenAI's image editing endpoint
        # For now, we'll use the variation endpoint as a placeholder
        # Actual implementation would depend on OpenAI's specific editing API

        # Build prompt with transformation
        prompt = transformation

        # Call edit endpoint (placeholder - adjust based on actual API)
        response = await self.client.images.edit(
            image=base_image,
            prompt=prompt,
            n=1,
            size=size,
        )

        return [img.url for img in response.data]

    async def generate_video(self, params: Dict[str, Any]) -> str:
        """
        Generate video using Sora.

        Args:
            params: Dictionary with prompt, length, resolution, etc.

        Returns:
            Video URL
        """
        prompt = params.get("prompt", "")
        length = params.get("length", 4)
        aspect_ratio = params.get("aspect_ratio", "16:9")
        resolution = params.get("resolution", "720p")

        # Map resolution and aspect ratio to size
        size_map = {
            ("16:9", "720p"): "720x1280",
            ("16:9", "1080p"): "1024x1792",
            ("9:16", "720p"): "1280x720",
            ("9:16", "1080p"): "1792x1024",
        }
        size = size_map.get((aspect_ratio, resolution), "720x1280")

        # Enhance prompt with cinematography settings
        enhanced_prompt = self._enhance_video_prompt(prompt, params)

        # Generate video with Sora
        # Note: Using Sora 2 model
        model = params.get("model", "sora-2")

        response = await self.client.videos.generate(
            model=model,
            prompt=enhanced_prompt,
            length=length,
            size=size,
        )

        # Return video URL
        return response.url

    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """
        Generate video from images using Sora.

        Args:
            params: Dictionary with input_images, video_config, etc.

        Returns:
            Video URL
        """
        input_images = params.get("input_images", [])
        length = params.get("length", 8)
        resolution = params.get("resolution", "720p")

        # Build prompt from images
        # Note: This is a simplified implementation
        # Actual implementation would depend on Sora's image-to-video API

        prompt = "Generate smooth video transitions between these images"
        if params.get("motion_type"):
            prompt += f" with {params['motion_type']}"

        # Call Sora with image references
        # (Placeholder - adjust based on actual API)
        response = await self.client.videos.generate(
            model="sora-2",
            prompt=prompt,
            length=length,
            images=input_images,
        )

        return response.url

    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """Calculate cost for OpenAI usage."""
        if resource_type == "image":
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "medium")
            return quantity * self.PRICING["gpt-image-1"].get(
                (size, quality), 0.042
            )
        elif resource_type == "video":
            resolution = kwargs.get("resolution", "720x1280")
            model = kwargs.get("model", "sora-2")

            if model == "sora-2-pro":
                return quantity * self.PRICING["sora-2"]["1024x1792"]
            else:
                return quantity * self.PRICING["sora-2"]["720x1280"]
        return 0.0

    def supports_feature(self, feature: str) -> bool:
        """Check feature support."""
        supported = {
            "image_generation",
            "image_editing",
            "video_generation",
            "video_from_images",
        }
        return feature in supported

    def _enhance_prompt(self, prompt: str, params: Dict[str, Any]) -> str:
        """Enhance image prompt with style and design tokens."""
        enhanced = prompt

        # Add style preset
        style_preset = params.get("style_preset")
        if style_preset:
            style_map = {
                "photoreal": "photorealistic, high detail, professional photography",
                "illustration": "digital illustration, artistic style",
                "technical": "technical diagram, clean lines",
                "minimal": "minimalist design, simple aesthetic",
            }
            if style_preset in style_map:
                enhanced += f". {style_map[style_preset]}"

        # Add design tokens
        design_tokens = params.get("design_tokens", {})
        if design_tokens:
            if "primary_color" in design_tokens:
                enhanced += f". Primary color: {design_tokens['primary_color']}"
            if "tone" in design_tokens:
                enhanced += f". {design_tokens['tone']} tone"

        return enhanced

    def _enhance_video_prompt(self, prompt: str, params: Dict[str, Any]) -> str:
        """Enhance video prompt with cinematography settings."""
        enhanced = prompt

        cinematography = params.get("cinematography", {})
        if cinematography:
            if "camera_movement" in cinematography:
                enhanced += f". Camera: {cinematography['camera_movement']}"
            if "shot_type" in cinematography:
                enhanced += f". Shot: {cinematography['shot_type']}"
            if "lighting" in cinematography:
                enhanced += f". Lighting: {cinematography['lighting']}"

        return enhanced
