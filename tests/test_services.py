"""Service layer tests."""
import pytest
from app.services.cost_calculator import CostCalculator


def test_calculate_image_cost_gemini():
    """Test image cost calculation for Gemini."""
    cost = CostCalculator.calculate_image_cost(
        provider="gemini",
        model="gemini-2.5-flash-image",
        quantity=4,
    )
    assert cost == 4 * 0.039  # $0.156


def test_calculate_image_cost_openai():
    """Test image cost calculation for OpenAI."""
    cost = CostCalculator.calculate_image_cost(
        provider="openai",
        model="gpt-image-1",
        quantity=1,
        size="1024x1024",
        quality="medium",
    )
    assert cost == 0.042


def test_calculate_video_cost_veo():
    """Test video cost calculation for Veo."""
    cost = CostCalculator.calculate_video_cost(
        provider="veo",
        model="veo-3.1-fast",
        duration_seconds=10,
    )
    assert cost == 10 * 0.15  # $1.50


def test_calculate_video_cost_sora():
    """Test video cost calculation for Sora."""
    cost = CostCalculator.calculate_video_cost(
        provider="sora",
        model="sora-2",
        duration_seconds=8,
        resolution="720x1280",
    )
    assert cost == 8 * 0.10  # $0.80


def test_recommend_provider_cost_priority():
    """Test provider recommendation with cost priority."""
    provider = CostCalculator.recommend_provider({
        "resource_type": "image",
        "priority": "cost",
    })
    assert provider == "imagen"  # Cheapest option


def test_recommend_provider_quality_priority():
    """Test provider recommendation with quality priority."""
    provider = CostCalculator.recommend_provider({
        "resource_type": "image",
        "priority": "quality",
    })
    assert provider == "openai"


def test_estimate_cost():
    """Test cost estimation."""
    cost = CostCalculator.estimate_cost({
        "provider": "gemini",
        "model": "gemini-2.5-flash-image",
        "resource_type": "image",
        "number_of_images": 2,
    })
    assert cost == 2 * 0.039
