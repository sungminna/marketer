# GTM Asset Generator

B2B SaaS platform for generating marketing and design assets using AI. Generate images and videos for your marketing campaigns with consistent branding using Gemini, OpenAI, Imagen, Veo, and Sora.

## Features

### Image Generation
- **Text-to-Image**: Generate images from text prompts
- **Image Editing**: Style transfer, pose changes, color adjustments, background replacement
- **Prototype Generation**: Create app screens, icons, logos, and banners
- **Providers**: Gemini 2.5 Flash Image, OpenAI GPT Image 1, Imagen 4

### Video Generation
- **Text-to-Video**: Generate videos from text descriptions
- **Image-to-Video**: Create videos from reference images
- **Video Background Removal**: Remove or replace video backgrounds
- **Providers**: Veo 3.1, Sora 2

### Key Capabilities
- Multi-provider support with automatic cost optimization
- Design tokens and brand guidelines
- Asynchronous job processing with Celery
- S3 storage for generated assets with CDN integration
- Usage tracking and cost calculation
- Rate limiting and security
- RESTful API with OpenAPI documentation
- Webhook notifications for job events
- Batch processing for multiple jobs
- Template management for reusable configurations
- Team collaboration with role-based access
- Advanced analytics and reporting
- API usage quotas by plan tier
- Multi-region support

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Package Manager**: uv (fast Python package installer)
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery
- **Storage**: MinIO (local) / AWS S3 (production)
- **Container**: Docker + Docker Compose
- **Deployment**: AWS ECS/Fargate (recommended)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API keys for providers (required for generation):
  - Google AI (Gemini/Imagen/Veo)
  - OpenAI (GPT Image/Sora)

**Note**: For local development, MinIO is used for storage (no AWS account needed). For production, configure AWS S3.

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd marketer
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your credentials:
```env
# Database (using Docker defaults)
DATABASE_URL=postgresql+asyncpg://gtmuser:gtmpassword@db:5432/gtm_assets

# Security (generate secure keys)
ENCRYPTION_KEY=<generate-32-byte-base64-key>
JWT_SECRET_KEY=<generate-secure-random-key>

# MinIO Storage (local development - uses Docker defaults)
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
S3_BUCKET_NAME=gtm-assets
S3_ENDPOINT_URL=http://minio:9000
S3_REGION=us-east-1

# For production with AWS S3, set:
# AWS_ACCESS_KEY_ID=<your-aws-key>
# AWS_SECRET_ACCESS_KEY=<your-aws-secret>
# S3_BUCKET_NAME=<your-s3-bucket>
# S3_ENDPOINT_URL=  # Leave empty for AWS S3
# S3_REGION=us-east-1
```

4. Generate encryption key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

5. Start services:
```bash
docker-compose up -d
```

6. Run database migrations:
```bash
make migrate
# Or directly:
docker-compose exec api uv run alembic upgrade head
```

7. Access the services:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Celery monitoring): http://localhost:5555
- MinIO Console: http://localhost:9001 (login: minioadmin / minioadmin123)

## Usage

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "company_name": "Acme Inc"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Save the `access_token` from the response.

### 3. Add API Keys

```bash
curl -X POST http://localhost:8000/api/v1/users/api-keys \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "api_key": "<your-gemini-api-key>"
  }'
```

### 4. Generate Images

```bash
curl -X POST http://localhost:8000/api/v1/images/generate \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "model": "gemini-2.5-flash-image",
    "prompt": "A modern tech startup office with blue and white brand colors",
    "style_preset": "photoreal",
    "design_tokens": {
      "primary_color": "#0066FF",
      "secondary_color": "#FFFFFF",
      "tone": "professional"
    },
    "image_config": {
      "aspect_ratio": "16:9",
      "number_of_images": 4
    }
  }'
```

### 5. Check Job Status

```bash
curl -X GET http://localhost:8000/api/v1/images/jobs/<job-id> \
  -H "Authorization: Bearer <your-access-token>"
```

### 6. Generate Videos

```bash
curl -X POST http://localhost:8000/api/v1/videos/generate \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "veo",
    "model": "veo-3.1-fast-generate-preview-001",
    "prompt": "A product showcase video with smooth camera movement",
    "video_config": {
      "length": 8,
      "resolution": "720p",
      "aspect_ratio": "16:9",
      "audio": true
    },
    "cinematography": {
      "camera_movement": "pan",
      "shot_type": "medium",
      "lighting": "natural"
    }
  }'
```

## API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Endpoints

#### Core Features
- **Users**: `/api/v1/users` - User registration, authentication, API key management
- **Images**: `/api/v1/images` - Image generation and editing
- **Videos**: `/api/v1/videos` - Video generation and processing

#### Phase 2 Features
- **Webhooks**: `/api/v1/webhooks` - Webhook management and delivery logs
- **Batches**: `/api/v1/batches` - Batch job processing
- **Templates**: `/api/v1/templates` - Template CRUD and usage
- **Teams**: `/api/v1/teams` - Team collaboration and invitations

#### Phase 3 Features
- **Analytics**: `/api/v1/analytics` - Usage analytics and reporting
  - GET `/summary` - Usage summary
  - GET `/cost-breakdown` - Cost breakdown by provider
  - GET `/daily` - Daily statistics
  - GET `/quota` - Current quota usage

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│  PostgreSQL │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ├────▶ Redis (Queue)
                           │
                           ├────▶ Celery Workers
                           │           │
                           │           ├────▶ Gemini API
                           │           ├────▶ OpenAI API
                           │           ├────▶ Imagen API
                           │           ├────▶ Veo API
                           │           └────▶ Sora API
                           │
                           └────▶ MinIO/S3 (Storage)
```

## Cost Estimation

### Images
- Gemini 2.5 Flash: $0.039/image
- Imagen 4 Fast: $0.02/image
- OpenAI GPT Image 1 Medium: $0.042/image
- OpenAI GPT Image 1 High: $0.167/image

### Videos
- Veo 3.1 Fast: $0.15/second
- Veo 3.1 Standard: $0.40/second
- Sora 2 (720p): $0.10/second
- Sora 2 Pro (1080p): $0.50/second

## Development

### Local Development (without Docker)

Install dependencies using uv:
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload
```

### Run Tests

```bash
make test
# Or directly:
docker-compose exec api uv run pytest
```

### Database Migrations

Create new migration:
```bash
docker-compose exec api uv run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
make migrate
# Or directly:
docker-compose exec api uv run alembic upgrade head
```

Rollback:
```bash
docker-compose exec api uv run alembic downgrade -1
```

### Code Quality

```bash
# Format code
make format
# Or directly:
docker-compose exec api uv run black app/

# Lint
make lint
# Or directly:
docker-compose exec api uv run flake8 app/

# Type checking
docker-compose exec api uv run mypy app/
```

## Deployment

### Docker Production Build

```bash
docker build -t gtm-asset-generator:latest .
```

### AWS ECS Deployment

1. Create ECR repository
2. Push Docker image to ECR
3. Create ECS cluster with Fargate
4. Configure task definitions for:
   - API service
   - Worker service
5. Set up Application Load Balancer
6. Configure RDS PostgreSQL
7. Configure ElastiCache Redis
8. Set environment variables in task definition

### Environment Variables (Production)

Ensure these are set securely in production:
- Use AWS Secrets Manager for sensitive data
- Rotate encryption keys regularly
- Use IAM roles for AWS access instead of keys when possible

## Security

- All API keys are encrypted at rest using Fernet (AES-256)
- JWT tokens for authentication
- Rate limiting on all endpoints
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- Parameterized queries

## Monitoring

### Celery Task Monitoring

Access Flower dashboard:
- URL: http://localhost:5555
- View active workers, tasks, and queue status

### Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# All services
docker-compose logs -f
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U gtmuser -d gtm_assets
```

### Celery Worker Not Processing Tasks

```bash
# Check worker status
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis connection
docker-compose exec api redis-cli -h redis ping
```

### Storage Upload Failures

**MinIO (local development):**
```bash
# Check MinIO container status
docker-compose ps minio

# View MinIO logs
docker-compose logs minio

# Access MinIO console
# http://localhost:9001 (minioadmin / minioadmin123)

# Verify bucket exists
docker-compose exec api python -c "from app.services.storage_service import storage_service; print(storage_service.s3_client.list_buckets())"
```

**AWS S3 (production):**
- Verify AWS credentials in `.env`
- Check S3 bucket permissions
- Ensure bucket exists in specified region
- Verify IAM role has PutObject and GetObject permissions

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Email: support@example.com

## Roadmap

### Phase 1 ✅ Complete
- ✅ Image generation (Gemini, OpenAI, Imagen)
- ✅ Video generation (Veo, Sora)
- ✅ User management and authentication
- ✅ Cost tracking and usage logs

### Phase 2 ✅ Complete
- ✅ Webhook notifications
- ✅ Batch processing
- ✅ Template management
- ✅ Team collaboration features

### Phase 3 ✅ Complete
- ✅ Advanced analytics
- ✅ API usage quotas
- ✅ Multi-region support
- ✅ CDN integration
- 🔨 Dashboard UI (configuration ready)

### Future Enhancements
- [ ] Real-time collaboration
- [ ] AI-powered template suggestions
- [ ] Custom model fine-tuning
- [ ] Advanced workflow automation
- [ ] Enterprise SSO integration

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Celery](https://docs.celeryproject.org/)
- [Google Generative AI](https://ai.google.dev/)
- [OpenAI](https://platform.openai.com/)
