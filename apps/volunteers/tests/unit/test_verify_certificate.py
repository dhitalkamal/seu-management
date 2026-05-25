"""Unit tests for VerifyCertificateUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.volunteers.application.use_cases.verify_certificate import VerifyCertificateUseCase
from apps.volunteers.domain.exceptions import CertificateNotFoundError
from apps.volunteers.tests.unit.fakes import FakeCertificateRepository, make_certificate


def test_verify_returns_certificate() -> None:
    """Existing certificate is returned by its ID."""
    cert = make_certificate()
    repo = FakeCertificateRepository([cert])
    use_case = VerifyCertificateUseCase(repo)

    result = use_case.execute(cert.id)

    assert result.id == cert.id
    assert result.verify_url is not None


def test_verify_raises_if_not_found() -> None:
    """Non-existent certificate ID raises CertificateNotFoundError."""
    repo = FakeCertificateRepository()
    use_case = VerifyCertificateUseCase(repo)

    with pytest.raises(CertificateNotFoundError):
        use_case.execute(uuid.uuid4())
