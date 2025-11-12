"""Cost calculation service for different providers."""
from typing import Dict, Any


class CostCalculator:
    """Cost calculator for AI generation services."""

    # Pricing tables for all providers
    PROVIDER_PRICING = {
        "gemini": {
            "gemini-2.5-flash-image": 0.039,  # per image
        },
        "openai": {
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
        },
        "imagen": {
            "imagen-4.0-fast-generate-001": 0.02,  # per image
        },
        "veo": {
            "veo-3.1-standard": 0.40,  # per second with audio
            "veo-3.1-fast": 0.15,  # per second with audio
        },
        "sora": {
            "sora-2": {
                "720x1280": 0.10,  # per second
                "1024x1792": 0.50,  # per second (pro)
            },
        },
    }

    @classmethod
    def calculate_image_cost(
        cls,
        provider: str,
        model: str,
        quantity: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for image generation.

        Args:
            provider: Provider name (gemini, openai, imagen)
            model: Model identifier
            quantity: Number of images
            **kwargs: Additional parameters (size, quality)

        Returns:
            Cost in USD
        """
        if provider == "gemini":
            return quantity * cls.PROVIDER_PRICING["gemini"][model]

        elif provider == "openai":
            size = kwargs.get("size", "1024x1024")
            quality = kwargs.get("quality", "medium")
            pricing = cls.PROVIDER_PRICING["openai"]["gpt-image-1"]
            return quantity * pricing.get((size, quality), 0.042)

        elif provider == "imagen":
            return quantity * cls.PROVIDER_PRICING["imagen"][model]

        return 0.0

    @classmethod
    def calculate_video_cost(
        cls,
        provider: str,
        model: str,
        duration_seconds: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for video generation.

        Args:
            provider: Provider name (veo, sora, openai)
            model: Model identifier
            duration_seconds: Video duration in seconds
            **kwargs: Additional parameters (resolution, audio)

        Returns:
            Cost in USD
        """
        if provider == "veo":
            if "standard" in model:
                cost_per_sec = cls.PROVIDER_PRICING["veo"]["veo-3.1-standard"]
            else:
                cost_per_sec = cls.PROVIDER_PRICING["veo"]["veo-3.1-fast"]
            return duration_seconds * cost_per_sec

        elif provider == "sora" or provider == "openai":
            resolution = kwargs.get("resolution", "720x1280")
            pricing = cls.PROVIDER_PRICING["sora"]["sora-2"]

            if "1024x1792" in resolution or "1792x1024" in resolution:
                cost_per_sec = pricing["1024x1792"]
            else:
                cost_per_sec = pricing["720x1280"]

            return duration_seconds * cost_per_sec

        return 0.0

    @classmethod
    def recommend_provider(cls, requirements: Dict[str, Any]) -> str:
        """
        Recommend optimal provider based on requirements.

        Args:
            requirements: Dictionary with priority, resource_type, etc.

        Returns:
            Recommended provider name
        """
        resource_type = requirements.get("resource_type", "image")
        priority = requirements.get("priority", "balanced")

        if resource_type == "image":
            if priority == "cost":
                return "imagen"  # $0.02/image - cheapest
            elif priority == "quality":
                return "openai"  # GPT Image 1 high quality
            else:
                return "gemini"  # $0.039/image - balanced

        elif resource_type == "video":
            if priority == "cost":
                return "sora"  # $0.10/sec for standard
            elif priority == "quality":
                return "sora"  # Sora 2 Pro for highest quality
            else:
                return "veo"  # $0.15/sec fast - balanced

        return "gemini"

    @classmethod
    def estimate_cost(cls, job_params: Dict[str, Any]) -> float:
        """
        Estimate cost for a generation job.

        Args:
            job_params: Job parameters including provider, model, resource_type, etc.

        Returns:
            Estimated cost in USD
        """
        provider = job_params.get("provider", "")
        model = job_params.get("model", "")
        resource_type = job_params.get("resource_type", "image")

        if resource_type == "image":
            quantity = job_params.get("number_of_images", 1)
            size = job_params.get("size", "1024x1024")
            quality = job_params.get("quality", "medium")

            return cls.calculate_image_cost(
                provider, model, quantity, size=size, quality=quality
            )

        elif resource_type == "video":
            duration = job_params.get("length", 4)
            resolution = job_params.get("resolution", "720p")

            return cls.calculate_video_cost(
                provider, model, duration, resolution=resolution
            )

        return 0.0
