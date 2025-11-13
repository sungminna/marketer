"""Imagen provider implementation."""
from typing import Dict, Any, List
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from app.services.providers.base import BaseProvider


class ImagenProvider(BaseProvider):
    """Imagen 4 provider."""

    PRICING = {
        "imagen-4.0-fast-generate-001": 0.02,  # $0.02 per image
    }

    def __init__(self, api_key: str, project_id: str = None, location: str = "us-central1"):
        """Initialize Imagen provider."""
        super().__init__(api_key)

        # project_id is required for Imagen
        if not project_id:
            raise ValueError("project_id is required for Imagen provider")

        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Generate images using Imagen 4.

        Args:
            params: Dictionary with prompt, aspect_ratio, number_of_images, etc.

        Returns:
            List of base64-encoded images
        """
        prompt = params.get("prompt", "")
        aspect_ratio = params.get("aspect_ratio", "16:9")
        number_of_images = params.get("number_of_images", 4)

        # Enhance prompt
        enhanced_prompt = self._enhance_prompt(prompt, params)

        # Map aspect ratio to image size
        size_map = {
            "16:9": "1792x1024",
            "1:1": "1024x1024",
            "9:16": "1024x1792",
            "4:3": "1024x768",
            "3:4": "768x1024",
        }
        image_size = size_map.get(aspect_ratio, "1024x1024")

        # Generate using Imagen 4
        model = aiplatform.ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-001")

        response = await model.generate_images_async(
            prompt=enhanced_prompt,
            number_of_images=min(number_of_images, 4),
            aspect_ratio=aspect_ratio,
            safety_filter_level="block_some",
            person_generation="allow_adult",
        )

        # Extract images
        images = []
        for image in response.images:
            # Convert to base64
            images.append(image._image_bytes.decode() if hasattr(image, '_image_bytes') else "")

        return images

    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Edit image using Imagen.

        Args:
            params: Dictionary with base_image, transformation, etc.

        Returns:
            List of edited image URLs
        """
        # Imagen 4 supports image editing via the edit endpoint
        base_image = params.get("base_image", "")
        transformation = params.get("transformation", "")

        model = aiplatform.ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-001")

        # Use Imagen's edit capabilities
        response = await model.edit_image_async(
            base_image=base_image,
            prompt=transformation,
            edit_mode="inpainting-insert",
        )

        images = []
        for image in response.images:
            images.append(image._image_bytes.decode() if hasattr(image, '_image_bytes') else "")

        return images

    async def generate_video(self, params: Dict[str, Any]) -> str:
        """Imagen doesn't support video generation."""
        raise NotImplementedError("Imagen doesn't support video generation. Use Veo instead.")

    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """Imagen doesn't support video generation."""
        raise NotImplementedError("Imagen doesn't support video generation. Use Veo instead.")

    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """Calculate cost for Imagen usage."""
        if resource_type == "image":
            return quantity * self.PRICING["imagen-4.0-fast-generate-001"]
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
                "photoreal": "photorealistic, highly detailed",
                "illustration": "digital illustration, artistic",
                "technical": "technical diagram, precise",
                "minimal": "minimalist, clean design",
            }
            if style_preset in style_map:
                enhanced += f", {style_map[style_preset]}"

        # Add design tokens
        design_tokens = params.get("design_tokens", {})
        if design_tokens:
            token_parts = []
            if "primary_color" in design_tokens:
                token_parts.append(f"primary color {design_tokens['primary_color']}")
            if "tone" in design_tokens:
                token_parts.append(f"{design_tokens['tone']} tone")
            if "lighting" in design_tokens:
                token_parts.append(f"{design_tokens['lighting']} lighting")

            if token_parts:
                enhanced += f", {', '.join(token_parts)}"

        return enhanced
