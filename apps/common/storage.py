"""S3-compatible storage helper. Works with MinIO (local) and Supabase Storage (production)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def get_s3_client() -> "S3Client":
    """Return a boto3 S3 client pointed at the configured storage backend."""
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name=getattr(settings, "STORAGE_REGION", "us-east-1"),
    )


def ensure_bucket_exists(client: "S3Client", bucket: str) -> None:
    """Create the bucket if it does not already exist."""
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchBucket"):
            try:
                client.create_bucket(Bucket=bucket)
            except ClientError:
                pass
        else:
            raise


def upload_file(file_obj: BinaryIO, file_name: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file and return its public URL."""
    client = get_s3_client()
    bucket = settings.MINIO_BUCKET
    ensure_bucket_exists(client, bucket)

    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    key = f"org-docs/{uuid.uuid4()}.{ext}"

    extra_args: dict = {"ContentType": content_type}
    # only set ACL for MinIO; Supabase manages access via bucket policy
    if getattr(settings, "STORAGE_USE_ACL", True):
        extra_args["ACL"] = "public-read"

    client.upload_fileobj(file_obj, bucket, key, ExtraArgs=extra_args)

    return f"{settings.MINIO_PUBLIC_BASE_URL}/{key}"


def _get_public_s3_client() -> "S3Client":
    """Return a boto3 S3 client using the public-facing URL for presigned URLs."""
    public_endpoint = getattr(settings, "MINIO_PUBLIC_ENDPOINT", settings.MINIO_ENDPOINT)
    return boto3.client(
        "s3",
        endpoint_url=public_endpoint,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name=getattr(settings, "STORAGE_REGION", "us-east-1"),
    )


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a browser-accessible presigned URL for reading a file.

    @param key - object key inside the bucket (e.g. org-docs/uuid.png)
    @param expires_in - URL validity in seconds (default 1 hour)
    @returns presigned URL string
    """
    # if public base URL is set, files are publicly accessible; return direct URL
    public_base = getattr(settings, "MINIO_PUBLIC_BASE_URL", "")
    if public_base and not getattr(settings, "STORAGE_FORCE_PRESIGNED", False):
        return f"{public_base}/{key}"

    client = _get_public_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
