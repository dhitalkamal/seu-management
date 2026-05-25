"""Tests for generate_certificate and verify_certificate use cases."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

import pytest

from apps.volunteers.application.use_cases.generate_certificate import GenerateCertificateUseCase
from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.exceptions import (
    CertificateAlreadyIssuedError,
    CertificateNotEligibleError,
)
from apps.volunteers.domain.repositories import (
    ICertificatePdfGenerator,
    ICertificateRepository,
    ICertificateStorage,
)
from apps.volunteers.tests.unit.fakes import FakeVolunteerApplicationRepository, make_application


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_certificate(**kwargs: object) -> CertificateEntity:
    """Build a CertificateEntity with sensible defaults for testing."""
    defaults: dict = {
        "id": uuid.uuid4(),
        "application_id": uuid.uuid4(),
        "volunteer_id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "org_id": None,
        "volunteer_name": "John Doe",
        "event_name": "Tech Fest",
        "role_name": "Stage Manager",
        "pdf_url": "https://storage.example.com/cert.pdf",
        "issued_at": _now(),
        "hours_worked": 4.0,
        "rating": 4,
    }
    defaults.update(kwargs)
    return CertificateEntity(**defaults)  # type: ignore[arg-type]


class FakeCertificateRepository(ICertificateRepository):
    """In-memory certificate store for testing."""

    def __init__(self, certs: Sequence[CertificateEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, CertificateEntity] = {c.id: c for c in (certs or [])}

    def create(self, entity: CertificateEntity) -> CertificateEntity:
        """Persist and return the certificate."""
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity:
        """Return the certificate or raise CertificateNotFoundError."""
        from apps.volunteers.domain.exceptions import CertificateNotFoundError

        entity = self._store.get(certificate_id)
        if entity is None:
            raise CertificateNotFoundError("Certificate not found.")
        return entity


class FakePdfGenerator(ICertificatePdfGenerator):
    """Records calls and returns a dummy bytes payload."""

    def __init__(self) -> None:
        self.call_count = 0

    def generate(
        self,
        *,
        certificate_id: uuid.UUID,
        volunteer_name: str,
        event_name: str,
        role_name: str,
        hours_worked: float | None,
        rating: int | None,
        issued_at: datetime,
        verify_url: str,
    ) -> bytes:
        """Return stub PDF bytes and increment the call counter."""
        self.call_count += 1
        return b"%PDF-stub"


class FakeCertificateStorage(ICertificateStorage):
    """Records calls and returns a deterministic URL."""

    def __init__(self) -> None:
        self.call_count = 0

    def upload(self, *, file_bytes: bytes, certificate_id: uuid.UUID) -> str:
        """Return a stub URL and increment the call counter."""
        self.call_count += 1
        return f"https://storage.example.com/certificates/{certificate_id}.pdf"


def _make_sut(
    app_repo: FakeVolunteerApplicationRepository,
    cert_repo: FakeCertificateRepository | None = None,
    pdf_gen: FakePdfGenerator | None = None,
    storage: FakeCertificateStorage | None = None,
) -> GenerateCertificateUseCase:
    return GenerateCertificateUseCase(
        app_repo=app_repo,
        cert_repo=cert_repo or FakeCertificateRepository(),
        pdf_generator=pdf_gen or FakePdfGenerator(),
        storage=storage or FakeCertificateStorage(),
    )


_ORG_ID = uuid.uuid4()
_EXECUTE_KWARGS = {
    "volunteer_name": "John Doe",
    "event_name": "Tech Fest",
    "role_name": "Stage Manager",
    "org_id": _ORG_ID,
}


class TestGenerateCertificate:
    """Unit tests for GenerateCertificateUseCase."""

    def test_raises_if_check_out_missing(self) -> None:
        """Not checked out → CertificateNotEligibleError."""
        app = make_application(check_in_at=_now(), check_out_at=None, rating=4)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        with pytest.raises(CertificateNotEligibleError):
            sut.execute(application_id=app.id, **_EXECUTE_KWARGS)

    def test_raises_if_rating_missing(self) -> None:
        """No rating → CertificateNotEligibleError."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=None)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        with pytest.raises(CertificateNotEligibleError):
            sut.execute(application_id=app.id, **_EXECUTE_KWARGS)

    def test_raises_if_check_in_missing(self) -> None:
        """Never checked in (no check_in_at) → CertificateNotEligibleError."""
        now = _now()
        app = make_application(check_in_at=None, check_out_at=now, rating=4)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        with pytest.raises(CertificateNotEligibleError):
            sut.execute(application_id=app.id, **_EXECUTE_KWARGS)

    def test_raises_if_already_issued(self) -> None:
        """certificate_issued=True → CertificateAlreadyIssuedError."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=5, certificate_issued=True)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        with pytest.raises(CertificateAlreadyIssuedError):
            sut.execute(application_id=app.id, **_EXECUTE_KWARGS)

    def test_returns_certificate_entity(self) -> None:
        """Happy path returns a CertificateEntity with the right application_id."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=4)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        result = sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        assert isinstance(result, CertificateEntity)
        assert result.application_id == app.id
        assert result.rating == 4

    def test_marks_application_certificate_issued(self) -> None:
        """After generation, the application's certificate_issued flag is True."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=3)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        updated = repo.get_by_id(app.id)
        assert updated.certificate_issued is True

    def test_calls_pdf_generator_once(self) -> None:
        """PDF generator is invoked exactly once per certificate."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=5)
        repo = FakeVolunteerApplicationRepository([app])
        pdf_gen = FakePdfGenerator()
        sut = _make_sut(repo, pdf_gen=pdf_gen)
        sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        assert pdf_gen.call_count == 1

    def test_calls_storage_once(self) -> None:
        """Storage upload is invoked exactly once per certificate."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=2)
        repo = FakeVolunteerApplicationRepository([app])
        storage = FakeCertificateStorage()
        sut = _make_sut(repo, storage=storage)
        sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        assert storage.call_count == 1

    def test_persists_certificate_to_repo(self) -> None:
        """The generated certificate is saved to the certificate repository."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=4)
        repo = FakeVolunteerApplicationRepository([app])
        cert_repo = FakeCertificateRepository()
        sut = _make_sut(repo, cert_repo=cert_repo)
        result = sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        saved = cert_repo.get_by_id(result.id)
        assert saved.id == result.id

    def test_certificate_has_pdf_url(self) -> None:
        """Returned certificate carries a non-empty pdf_url from storage."""
        now = _now()
        app = make_application(check_in_at=now, check_out_at=now, rating=4)
        repo = FakeVolunteerApplicationRepository([app])
        sut = _make_sut(repo)
        result = sut.execute(application_id=app.id, **_EXECUTE_KWARGS)
        assert result.pdf_url
