"""User-related Pydantic schemas."""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    email: str
    company_name: Optional[str]
    plan_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class APIKeyCreate(BaseModel):
    """Schema for creating/updating API key."""

    provider: str = Field(..., description="Provider name: gemini|openai|imagen|veo|sora")
    api_key: str = Field(..., description="The API key to store")


class APIKeyResponse(BaseModel):
    """Schema for API key response."""

    id: UUID
    provider: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """Schema for list of API keys."""

    api_keys: List[APIKeyResponse]
