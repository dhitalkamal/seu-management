"""Unit tests for GenerateCertificateUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.volunteers.application.use_cases.generate_certificate import GenerateCertificateUseCase
from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.exceptions import (
    ApplicationNotFoundError,
    CertificateAlreadyIssuedError,
    CertificateNotEligibleError,
)
from apps.volunteers.tests.unit.fakes import (
    FakeCertificatePdfGenerator,
    FakeCertificateRepository,
    FakeCertificateStorage,
    FakeEventPublisher,
    FakeVolunteerApplicationRepository,
    FakeVolunteerProfileRepository,
    make_application,
    make_profile,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_eligible(**kwargs: object) -> VolunteerApplicationEntity:
    return make_application(
        status="confirmed",
        check_in_at=_now(),
        check_out_at=_now(),
        certificate_issued=False,
        **kwargs,
    )


def test_certificate_is_created_and_issued() -> None:
    """Eligible application gets a certificate record and is flagged issued."""
    app = _make_eligible()
    app_repo = FakeVolunteerApplicationRepository([app])
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    cert = use_case.execute(app.id)

    assert cert.application_id == app.id
    assert cert.pdf_url is not None
    stored_app = app_repo.get_by_id(app.id)
    assert stored_app.certificate_issued is True


def test_certificate_event_published() -> None:
    """A volunteers.certificate.generated event is published."""
    app = _make_eligible()
    app_repo = FakeVolunteerApplicationRepository([app])
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    use_case.execute(app.id)

    assert len(publisher.events) == 1
    assert publisher.events[0]["type"] == "volunteers.certificate.generated"


def test_certificate_updates_profile_count() -> None:
    """Profile certificate_count is incremented after issuance."""
    app = _make_eligible()
    profile = make_profile(user_id=app.user_id, certificate_count=1)
    app_repo = FakeVolunteerApplicationRepository([app])
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository([profile])
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    use_case.execute(app.id)

    p = profile_repo.get_by_user_id(app.user_id)
    assert p.certificate_count == 2


def test_raises_if_not_eligible_missing_checkout() -> None:
    """Missing check_out_at raises CertificateNotEligibleError."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=None, certificate_issued=False)
    app_repo = FakeVolunteerApplicationRepository([app])
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    with pytest.raises(CertificateNotEligibleError):
        use_case.execute(app.id)


def test_raises_if_already_issued() -> None:
    """Already-issued application raises CertificateAlreadyIssuedError."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now(), certificate_issued=True)
    app_repo = FakeVolunteerApplicationRepository([app])
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    with pytest.raises(CertificateAlreadyIssuedError):
        use_case.execute(app.id)


def test_raises_if_not_found() -> None:
    """Non-existent application raises ApplicationNotFoundError."""
    app_repo = FakeVolunteerApplicationRepository()
    cert_repo = FakeCertificateRepository()
    pdf_gen = FakeCertificatePdfGenerator()
    storage = FakeCertificateStorage()
    publisher = FakeEventPublisher()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = GenerateCertificateUseCase(app_repo, cert_repo, pdf_gen, storage, publisher, profile_repo)

    with pytest.raises(ApplicationNotFoundError):
        use_case.execute(uuid.uuid4())
