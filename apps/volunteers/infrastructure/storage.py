"""S3-backed storage for volunteer certificate PDFs."""

from __future__ import annotations

import uuid

from django.conf import settings

from apps.volunteers.domain.repositories import ICertificateStorage


class S3CertificateStorage(ICertificateStorage):
    """Uploads certificate PDFs to S3 and returns a public URL."""

    def __init__(self) -> None:
        import boto3  # type: ignore[import-untyped]

        self._bucket: str = settings.CERTIFICATE_S3_BUCKET
        self._client = boto3.client(
            "s3",
            region_name=getattr(settings, "AWS_REGION", "us-east-1"),
        )

    def upload(self, certificate_id: uuid.UUID, pdf_bytes: bytes) -> str:
        """Upload the PDF and return its public URL."""
        key = f"certificates/{certificate_id}.pdf"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        region = getattr(settings, "AWS_REGION", "us-east-1")
        return f"https://{self._bucket}.s3.{region}.amazonaws.com/{key}"
