"""MinIO/S3-compatible storage helper used across the management service."""

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
    """Return a boto3 S3 client pointed at the MinIO instance."""
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket_exists(client: "S3Client", bucket: str) -> None:
    """Create the bucket if it does not already exist."""
    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        # head_bucket raises ClientError with code 404 when the bucket is absent
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=bucket)
        else:
            raise


ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/svg+xml",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def upload_file(file_obj: BinaryIO, file_name: str, content_type: str = "application/octet-stream") -> str:
    """
    Upload a file to MinIO and return its public URL.

    Accepts PDF, PNG, JPG, WEBP, and SVG up to 10 MB.

    @param file_obj - file-like object to upload
    @param file_name - original file name (used to derive extension)
    @param content_type - MIME type of the file
    @returns public URL string
    @raises ValueError if the MIME type or file size is not allowed
    """
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"File type '{content_type}' is not allowed. Upload PDF, PNG, JPG, WEBP, or SVG.")
    client = get_s3_client()
    bucket = settings.MINIO_BUCKET
    ensure_bucket_exists(client, bucket)

    ext = file_name.rsplit(".", 1)[-1] if "." in file_name else "bin"
    key = f"org-docs/{uuid.uuid4()}.{ext}"

    # bucket policy already grants public-read; ACL param causes errors on some MinIO versions
    client.upload_fileobj(
        file_obj,
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    return f"{settings.MINIO_PUBLIC_BASE_URL}/{key}"
