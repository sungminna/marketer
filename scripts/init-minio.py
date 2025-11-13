#!/usr/bin/env python3
"""Initialize MinIO bucket on startup."""
import sys
import time
import boto3
from botocore.exceptions import ClientError
import os

def wait_for_minio(client, max_retries=30):
    """Wait for MinIO to be ready."""
    for i in range(max_retries):
        try:
            client.list_buckets()
            print("✓ MinIO is ready")
            return True
        except Exception as e:
            print(f"Waiting for MinIO... ({i+1}/{max_retries})")
            time.sleep(2)
    return False

def create_bucket_if_not_exists(client, bucket_name):
    """Create bucket if it doesn't exist."""
    try:
        # Check if bucket exists
        client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket '{bucket_name}' already exists")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Bucket doesn't exist, create it
            try:
                client.create_bucket(Bucket=bucket_name)
                print(f"✓ Created bucket '{bucket_name}'")
                return True
            except ClientError as create_error:
                print(f"✗ Failed to create bucket: {create_error}")
                return False
        else:
            print(f"✗ Error checking bucket: {e}")
            return False

def set_bucket_policy(client, bucket_name):
    """Set bucket policy to allow public read access."""
    policy = f'''{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Principal": {{"AWS": "*"}},
            "Action": ["s3:GetObject"],
            "Resource": ["arn:aws:s3:::{bucket_name}/*"]
        }}
    ]
}}'''

    try:
        client.put_bucket_policy(Bucket=bucket_name, Policy=policy)
        print(f"✓ Set public read policy on bucket '{bucket_name}'")
        return True
    except ClientError as e:
        print(f"✗ Failed to set bucket policy: {e}")
        return False

def main():
    """Initialize MinIO bucket."""
    # Get configuration from environment
    endpoint_url = os.getenv('S3_ENDPOINT_URL', 'http://minio:9000')
    access_key = os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin123')
    bucket_name = os.getenv('S3_BUCKET_NAME', 'gtm-assets')
    region = os.getenv('S3_REGION', 'us-east-1')

    print(f"Initializing MinIO at {endpoint_url}")
    print(f"Bucket name: {bucket_name}")

    # Create S3 client
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )

    # Wait for MinIO to be ready
    if not wait_for_minio(s3_client):
        print("✗ MinIO is not ready after waiting")
        sys.exit(1)

    # Create bucket if it doesn't exist
    if not create_bucket_if_not_exists(s3_client, bucket_name):
        print("✗ Failed to create bucket")
        sys.exit(1)

    # Set bucket policy for public read access
    if not set_bucket_policy(s3_client, bucket_name):
        print("⚠ Warning: Failed to set bucket policy (continuing anyway)")

    print("✓ MinIO initialization complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
