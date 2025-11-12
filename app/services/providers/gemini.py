"""Gemini provider implementation."""
import base64
import io
from typing import Dict, Any, List
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from app.services.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Gemini 2.5 Flash Image provider."""

    PRICING = {
        "image_generation": 0.039,  # $0.039 per image
    }

    def __init__(self, api_key: str):
        """Initialize Gemini provider."""
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-image")

    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Generate images using Gemini 2.5 Flash.

        Args:
            params: Dictionary with prompt, aspect_ratio, number_of_images, etc.

        Returns:
            List of base64-encoded images
        """
        prompt = params.get("prompt", "")
        aspect_ratio = params.get("aspect_ratio", "16:9")
        number_of_images = params.get("number_of_images", 4)

        # Build enhanced prompt with style and design tokens
        enhanced_prompt = self._enhance_prompt(prompt, params)

        # Configure generation
        config = types.GenerationConfig(
            aspect_ratio=aspect_ratio,
            numberOfImages=min(number_of_images, 4),  # Max 4
        )

        # Generate
        response = await self.model.generate_content_async(
            enhanced_prompt,
            generation_config=config,
        )

        # Extract images from response
        images = []
        if hasattr(response, "candidates"):
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data"):
                            # Image is in inline_data
                            image_data = part.inline_data.data
                            images.append(base64.b64encode(image_data).decode())

        return images

    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Edit image using Gemini (e.g., style transfer, transformations).

        Args:
            params: Dictionary with base_image, transformation, etc.

        Returns:
            List of edited image base64 strings
        """
        base_image = params.get("base_image", "")
        transformation = params.get("transformation", "")
        reference_image = params.get("reference_image")

        # Load base image
        if base_image.startswith("http"):
            # TODO: Download image from URL
            raise NotImplementedError("URL download not implemented yet")
        else:
            # Assume base64
            image_data = base64.b64decode(base_image)

        # Build prompt
        prompt_parts = [transformation]

        if reference_image:
            prompt_parts.append("Use the style from the reference image.")

        # Use Gemini's multimodal capabilities
        response = await self.model.generate_content_async(
            [prompt_parts[0], {"mime_type": "image/png", "data": image_data}]
        )

        # Extract result
        # Note: This is a simplified implementation
        # Actual implementation may vary based on Gemini's response format
        images = []
        if hasattr(response, "candidates"):
            for candidate in response.candidates:
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data"):
                            image_data = part.inline_data.data
                            images.append(base64.b64encode(image_data).decode())

        return images

    async def generate_video(self, params: Dict[str, Any]) -> str:
        """Gemini doesn't support video generation."""
        raise NotImplementedError("Gemini doesn't support video generation")

    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """Gemini doesn't support video generation."""
        raise NotImplementedError("Gemini doesn't support video generation")

    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """Calculate cost for Gemini usage."""
        if resource_type == "image":
            return quantity * self.PRICING["image_generation"]
        return 0.0

    def supports_feature(self, feature: str) -> bool:
        """Check feature support."""
        supported = {"image_generation", "image_editing"}
        return feature in supported

    def _enhance_prompt(self, prompt: str, params: Dict[str, Any]) -> str:
        """Enhance prompt with style preset and design tokens."""
        enhanced = prompt

        # Add style preset
        style_preset = params.get("style_preset")
        if style_preset:
            style_map = {
                "photoreal": "photorealistic, high detail, professional photography",
                "illustration": "digital illustration, artistic, hand-drawn style",
                "technical": "technical diagram, clean lines, precise",
                "minimal": "minimalist design, simple, clean aesthetic",
            }
            if style_preset in style_map:
                enhanced += f". Style: {style_map[style_preset]}"

        # Add design tokens
        design_tokens = params.get("design_tokens", {})
        if design_tokens:
            if "primary_color" in design_tokens:
                enhanced += f". Primary color: {design_tokens['primary_color']}"
            if "tone" in design_tokens:
                enhanced += f". Tone: {design_tokens['tone']}"
            if "lighting" in design_tokens:
                enhanced += f". Lighting: {design_tokens['lighting']}"

        return enhanced
