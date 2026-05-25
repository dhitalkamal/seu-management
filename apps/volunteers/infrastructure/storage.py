"""S3/MinIO storage adapter for volunteer certificates."""

from __future__ import annotations

import io
import uuid

from apps.common.storage import get_s3_client
from apps.volunteers.domain.repositories import ICertificateStorage

_CONTENT_TYPE = "application/pdf"
_KEY_PREFIX = "certificates"


class S3CertificateStorage(ICertificateStorage):
    """Uploads certificate PDFs to the configured MinIO/S3 bucket."""

    def __init__(self, bucket: str, base_url: str) -> None:
        self._bucket = bucket
        self._base_url = base_url.rstrip("/")

    def upload(self, *, file_bytes: bytes, certificate_id: uuid.UUID) -> str:
        """Upload the PDF and return the public URL."""
        client = get_s3_client()
        key = f"{_KEY_PREFIX}/{certificate_id}.pdf"
        client.upload_fileobj(
            io.BytesIO(file_bytes),
            self._bucket,
            key,
            ExtraArgs={"ContentType": _CONTENT_TYPE, "ACL": "public-read"},
        )
        return f"{self._base_url}/{key}"
