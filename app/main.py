"""FastAPI main application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.core.database import init_db
from app.api.v1 import users, images, videos

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="B2B SaaS platform for generating marketing and design assets",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    import logging
    import traceback

    logger = logging.getLogger(__name__)

    # Log full error details server-side
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        }
    )

    # Return safe error message to client
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and storage on startup."""
    await init_db()

    # Initialize MinIO bucket if using MinIO
    if settings.s3_endpoint_url:
        try:
            from app.services.storage_service import storage_service
            import boto3
            from botocore.exceptions import ClientError

            # Check if bucket exists, create if not
            try:
                storage_service.s3_client.head_bucket(Bucket=settings.s3_bucket_name)
                print(f"✓ Bucket '{settings.s3_bucket_name}' already exists")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    # Create bucket
                    storage_service.s3_client.create_bucket(Bucket=settings.s3_bucket_name)
                    print(f"✓ Created bucket '{settings.s3_bucket_name}'")

                    # Set bucket policy for public read
                    policy = f'''{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Principal": {{"AWS": "*"}},
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::{settings.s3_bucket_name}/*"]
        }}
    ]
}}'''
                    try:
                        storage_service.s3_client.put_bucket_policy(
                            Bucket=settings.s3_bucket_name,
                            Policy=policy
                        )
                        print(f"✓ Set public read policy on bucket '{settings.s3_bucket_name}'")
                    except ClientError:
                        print(f"⚠ Warning: Could not set bucket policy (continuing anyway)")
        except Exception as e:
            print(f"⚠ Warning: MinIO initialization failed: {e}")


# Health check endpoint
@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Health check endpoint with dependency verification."""
    from app.core.database import engine
    import redis.asyncio as redis_async

    health_status = {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "checks": {}
    }

    # Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        redis_client = redis_async.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GTM Asset Generator API",
        "version": settings.app_version,
        "docs": "/docs",
    }


# Include routers
app.include_router(users.router)
app.include_router(images.router)
app.include_router(videos.router)


# Note: Rate limiting is handled by slowapi decorators on individual endpoints
# No additional middleware needed


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
