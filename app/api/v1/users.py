"""User management API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import get_password_hash, verify_password, create_access_token, api_key_manager
from app.models.user import User, UserAPIKey
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    APIKeyCreate,
    APIKeyResponse,
    APIKeyListResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        company_name=user_data.company_name,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    # Find user
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information."""
    return current_user


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update an API key for a provider."""
    # Check if key already exists
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider == api_key_data.provider,
        )
    )
    existing_key = result.scalar_one_or_none()

    # Encrypt API key
    encrypted_key = api_key_manager.encrypt_key(api_key_data.api_key)

    if existing_key:
        # Update existing key
        existing_key.api_key_encrypted = encrypted_key
        existing_key.is_active = True
        await db.commit()
        await db.refresh(existing_key)
        return existing_key
    else:
        # Create new key
        user_api_key = UserAPIKey(
            user_id=current_user.id,
            provider=api_key_data.provider,
            api_key_encrypted=encrypted_key,
        )
        db.add(user_api_key)
        await db.commit()
        await db.refresh(user_api_key)
        return user_api_key


@router.get("/api-keys", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's API keys."""
    result = await db.execute(
        select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()

    return {"api_keys": api_keys}


@router.delete("/api-keys/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an API key."""
    result = await db.execute(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.provider == provider,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.commit()
