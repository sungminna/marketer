"""S3 storage service for generated assets."""
import uuid
import base64
import io
from typing import List, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from app.config import settings


class StorageService:
    """Service for storing generated assets in S3."""

    def __init__(self):
        """Initialize S3/MinIO client."""
        # Configure S3 client with MinIO support
        s3_config = {
            'aws_access_key_id': settings.aws_access_key_id,
            'aws_secret_access_key': settings.aws_secret_access_key,
            'region_name': settings.s3_region,
        }

        # Add endpoint_url for MinIO (if configured)
        if settings.s3_endpoint_url:
            s3_config['endpoint_url'] = settings.s3_endpoint_url

        self.s3_client = boto3.client('s3', **s3_config)
        self.bucket_name = settings.s3_bucket_name
        self.endpoint_url = settings.s3_endpoint_url

    async def upload_image(
        self,
        image_data: str,
        user_id: str,
        job_id: str,
        format: str = "png",
    ) -> str:
        """
        Upload image to S3.

        Args:
            image_data: Base64-encoded image or raw bytes
            user_id: User ID for organizing files
            job_id: Job ID for organizing files
            format: Image format (png, jpeg, etc.)

        Returns:
            S3 URL of uploaded image
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        key = f"images/{user_id}/{job_id}/{timestamp}_{file_id}.{format}"

        # Decode base64 if needed
        if isinstance(image_data, str):
            if image_data.startswith('data:'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {str(e)}")
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")

        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType=f"image/{format}",
            )

            # Generate URL
            url = self._generate_url(key)
            return url

        except ClientError as e:
            raise Exception(f"Failed to upload image to S3/MinIO: {str(e)}")

    async def upload_video(
        self,
        video_data: bytes,
        user_id: str,
        job_id: str,
        format: str = "mp4",
    ) -> str:
        """
        Upload video to S3.

        Args:
            video_data: Video bytes
            user_id: User ID for organizing files
            job_id: Job ID for organizing files
            format: Video format (mp4, webm, mov)

        Returns:
            S3 URL of uploaded video
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        key = f"videos/{user_id}/{job_id}/{timestamp}_{file_id}.{format}"

        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=video_data,
                ContentType=f"video/{format}",
            )

            # Generate URL
            url = self._generate_url(key)
            return url

        except ClientError as e:
            raise Exception(f"Failed to upload video to S3/MinIO: {str(e)}")

    async def upload_multiple_images(
        self,
        images_data: List[str],
        user_id: str,
        job_id: str,
        format: str = "png",
    ) -> List[str]:
        """
        Upload multiple images to S3.

        Args:
            images_data: List of base64-encoded images
            user_id: User ID
            job_id: Job ID
            format: Image format

        Returns:
            List of S3 URLs
        """
        urls = []
        for image_data in images_data:
            url = await self.upload_image(image_data, user_id, job_id, format)
            urls.append(url)
        return urls

    async def download_from_url(self, url: str) -> bytes:
        """
        Download file from URL (for processing external URLs).

        Args:
            url: URL to download from

        Returns:
            File bytes
        """
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def delete_file(self, url: str) -> bool:
        """
        Delete file from S3/MinIO.

        Args:
            url: S3/MinIO URL of file to delete

        Returns:
            True if successful
        """
        try:
            # Extract key from URL
            if self.endpoint_url and self.endpoint_url in url:
                # MinIO URL format: http://minio:9000/bucket-name/key
                key = url.split(f"{self.bucket_name}/", 1)[1]
            else:
                # AWS S3 URL format: https://bucket-name.s3.region.amazonaws.com/key
                key = url.split(f"{self.bucket_name}.s3.{settings.s3_region}.amazonaws.com/")[1]

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True

        except (ClientError, IndexError) as e:
            raise Exception(f"Failed to delete file from S3/MinIO: {str(e)}")

    def _generate_url(self, key: str) -> str:
        """
        Generate URL for uploaded file (MinIO or AWS S3).

        Args:
            key: S3/MinIO object key

        Returns:
            Public URL for the file
        """
        if self.endpoint_url:
            # MinIO URL format
            return f"{self.endpoint_url}/{self.bucket_name}/{key}"
        else:
            # AWS S3 URL format
            return f"https://{self.bucket_name}.s3.{settings.s3_region}.amazonaws.com/{key}"

    def get_signed_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for temporary access.

        Args:
            key: S3 object key
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")


# Global instance
storage_service = StorageService()
