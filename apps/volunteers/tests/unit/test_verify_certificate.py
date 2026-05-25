"""Tests for VerifyCertificateUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.volunteers.application.use_cases.verify_certificate import VerifyCertificateUseCase
from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.exceptions import CertificateNotFoundError
from apps.volunteers.domain.repositories import ICertificateRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_cert(**kwargs: object) -> CertificateEntity:
    defaults: dict = {
        "id": uuid.uuid4(),
        "application_id": uuid.uuid4(),
        "volunteer_id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "org_id": None,
        "volunteer_name": "Jane Doe",
        "event_name": "Tech Fest",
        "role_name": "Stage Manager",
        "pdf_url": "https://storage.example.com/cert.pdf",
        "issued_at": _now(),
        "hours_worked": 4.0,
        "rating": 5,
    }
    defaults.update(kwargs)
    return CertificateEntity(**defaults)  # type: ignore[arg-type]


class _FakeCertRepo(ICertificateRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, CertificateEntity] = {}

    def create(self, entity: CertificateEntity) -> CertificateEntity:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity:
        entity = self._store.get(certificate_id)
        if entity is None:
            raise CertificateNotFoundError("Certificate not found.")
        return entity


class TestVerifyCertificate:
    """Unit tests for VerifyCertificateUseCase."""

    def test_returns_certificate_for_valid_id(self) -> None:
        cert = _make_cert()
        repo = _FakeCertRepo()
        repo.create(cert)
        sut = VerifyCertificateUseCase(cert_repo=repo)
        result = sut.execute(certificate_id=cert.id)
        assert result.id == cert.id

    def test_raises_if_certificate_not_found(self) -> None:
        sut = VerifyCertificateUseCase(cert_repo=_FakeCertRepo())
        with pytest.raises(CertificateNotFoundError):
            sut.execute(certificate_id=uuid.uuid4())
