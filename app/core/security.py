"""Security utilities for authentication and encryption."""
from datetime import datetime, timedelta
from typing import Optional
import base64
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Pre-hash the password with SHA256 to avoid bcrypt's 72-byte limitation
    prehashed = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(prehashed, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage.

    Pre-hashes the password with SHA256 before bcrypt hashing to avoid
    bcrypt's 72-byte limitation while maintaining security.
    """
    # Pre-hash the password with SHA256 to avoid bcrypt's 72-byte limitation
    prehashed = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(prehashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


class APIKeyManager:
    """Manager for encrypting and decrypting API keys."""

    def __init__(self):
        """Initialize the cipher with the encryption key."""
        # Derive a valid Fernet key from the encryption key
        # Use SHA256 to hash the key to ensure it's 32 bytes, then base64 encode it
        key_bytes = settings.encryption_key.encode()
        hashed_key = hashlib.sha256(key_bytes).digest()
        fernet_key = base64.urlsafe_b64encode(hashed_key)
        self.cipher = Fernet(fernet_key)

    def encrypt_key(self, api_key: str) -> str:
        """Encrypt an API key."""
        return self.cipher.encrypt(api_key.encode()).decode()

    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt an API key."""
        return self.cipher.decrypt(encrypted_key.encode()).decode()


# Global instance
api_key_manager = APIKeyManager()
