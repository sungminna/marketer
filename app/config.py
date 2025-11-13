"""Application configuration."""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = Field(default="GTM Asset Generator")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://gtmuser:gtmpassword@localhost:5432/gtm_assets"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Security
    encryption_key: str = Field(...)
    jwt_secret_key: str = Field(...)
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=1440)

    # S3 / MinIO Configuration
    aws_access_key_id: str = Field(...)
    aws_secret_access_key: str = Field(...)
    s3_bucket_name: str = Field(...)
    s3_endpoint_url: str = Field(default="")  # For MinIO: http://localhost:9000, for AWS S3: leave empty
    s3_region: str = Field(default="us-east-1")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)
    rate_limit_per_hour: int = Field(default=1000)

    # Webhook
    webhook_secret: str = Field(...)

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"]
    )

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/1")

    # Video Background Removal
    video_bg_remover_api_key: str = Field(default="")

    # Multi-region support
    region: str = Field(default="us-east-1")
    enable_multi_region: bool = Field(default=False)
    regions: List[str] = Field(default=["us-east-1", "us-west-2", "eu-west-1"])

    # CDN Configuration
    cdn_enabled: bool = Field(default=False)
    cdn_domain: str = Field(default="")
    cloudfront_distribution_id: str = Field(default="")

    # Dashboard UI
    dashboard_enabled: bool = Field(default=True)
    dashboard_url: str = Field(default="http://localhost:3000")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
