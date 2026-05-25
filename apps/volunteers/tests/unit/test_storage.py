"""Smoke test for S3CertificateStorage - verifies the adapter calls boto3 correctly."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from apps.volunteers.infrastructure.storage import S3CertificateStorage


class TestS3CertificateStorage:
    """Verifies the storage adapter calls boto3 upload_fileobj and returns a URL."""

    def test_returns_url_string(self) -> None:
        """upload() returns a non-empty string URL."""
        with patch("apps.volunteers.infrastructure.storage.get_s3_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client
            sut = S3CertificateStorage(bucket="test-bucket", base_url="https://storage.example.com")
            cert_id = uuid.uuid4()
            result = sut.upload(file_bytes=b"%PDF-stub", certificate_id=cert_id)
            assert isinstance(result, str)
            assert str(cert_id) in result

    def test_calls_upload_fileobj(self) -> None:
        """upload() invokes upload_fileobj on the s3 client exactly once."""
        with patch("apps.volunteers.infrastructure.storage.get_s3_client") as mock_client_fn:
            mock_client = MagicMock()
            mock_client_fn.return_value = mock_client
            sut = S3CertificateStorage(bucket="test-bucket", base_url="https://storage.example.com")
            sut.upload(file_bytes=b"%PDF-stub", certificate_id=uuid.uuid4())
            mock_client.upload_fileobj.assert_called_once()
