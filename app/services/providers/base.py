"""Base provider interface following Open-Closed Principle."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseProvider(ABC):
    """Base provider interface for AI generation services."""

    def __init__(self, api_key: str):
        """Initialize provider with API key."""
        self.api_key = api_key

    @abstractmethod
    async def generate_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Generate images from text prompt.

        Args:
            params: Dictionary containing:
                - prompt: Text description
                - aspect_ratio: Image aspect ratio (optional)
                - size: Image size (optional)
                - quality: Image quality (optional)
                - number_of_images: Number of images to generate
                - style_preset: Style preset (optional)
                - design_tokens: Design tokens (optional)

        Returns:
            List of image URLs or base64 strings
        """
        pass

    @abstractmethod
    async def edit_image(self, params: Dict[str, Any]) -> List[str]:
        """
        Edit an existing image.

        Args:
            params: Dictionary containing:
                - base_image: Original image URL or base64
                - edit_type: Type of edit to perform
                - transformation: Description of transformation
                - reference_image: Reference image (optional)
                - preserve_elements: Elements to preserve (optional)

        Returns:
            List of edited image URLs or base64 strings
        """
        pass

    @abstractmethod
    async def generate_video(self, params: Dict[str, Any]) -> str:
        """
        Generate video from text prompt.

        Args:
            params: Dictionary containing:
                - prompt: Text description
                - length: Video length in seconds
                - resolution: Video resolution
                - aspect_ratio: Video aspect ratio
                - cinematography: Cinematography settings (optional)

        Returns:
            Video URL or base64 string
        """
        pass

    @abstractmethod
    async def video_from_images(self, params: Dict[str, Any]) -> str:
        """
        Generate video from reference images.

        Args:
            params: Dictionary containing:
                - input_images: List of image URLs with positions
                - transition_style: Transition style
                - motion_type: Camera/object motion type
                - video_config: Video configuration

        Returns:
            Video URL or base64 string
        """
        pass

    @abstractmethod
    def calculate_cost(self, resource_type: str, quantity: int, **kwargs) -> float:
        """
        Calculate cost for resource usage.

        Args:
            resource_type: Type of resource (image|video|edit)
            quantity: Quantity (number of images or video seconds)
            **kwargs: Additional parameters (quality, resolution, etc.)

        Returns:
            Cost in USD
        """
        pass

    def supports_feature(self, feature: str) -> bool:
        """
        Check if provider supports a specific feature.

        Args:
            feature: Feature name (image_generation|image_editing|video_generation|video_from_images)

        Returns:
            True if supported, False otherwise
        """
        return False
