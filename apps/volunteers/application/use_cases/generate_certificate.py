"""Use case: generate and issue a participation certificate."""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import datetime, timezone

from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.exceptions import (
    CertificateAlreadyIssuedError,
    CertificateNotEligibleError,
)
from apps.volunteers.domain.repositories import (
    ICertificatePdfGenerator,
    ICertificateRepository,
    ICertificateStorage,
    IEventPublisher,
    IVolunteerApplicationRepository,
    IVolunteerProfileRepository,
)

_VERIFY_BASE = "http://localhost:5173/verify/cert"


class GenerateCertificateUseCase:
    """Generates a PDF certificate, persists it, and publishes a domain event."""

    def __init__(
        self,
        application_repo: IVolunteerApplicationRepository,
        certificate_repo: ICertificateRepository,
        pdf_generator: ICertificatePdfGenerator,
        storage: ICertificateStorage,
        publisher: IEventPublisher,
        profile_repo: IVolunteerProfileRepository,
    ) -> None:
        self._app_repo = application_repo
        self._cert_repo = certificate_repo
        self._pdf = pdf_generator
        self._storage = storage
        self._publisher = publisher
        self._profile_repo = profile_repo

    def execute(self, application_id: uuid.UUID) -> CertificateEntity:
        """Generate the certificate. Raises if not eligible or already issued."""
        app = self._app_repo.get_by_id(application_id)

        if app.check_in_at is None or app.check_out_at is None:
            raise CertificateNotEligibleError("Certificate requires both check-in and check-out to be recorded.")

        if app.certificate_issued:
            raise CertificateAlreadyIssuedError("A certificate has already been issued for this application.")

        cert_id = uuid.uuid4()
        verify_url = f"{_VERIFY_BASE}/{cert_id}"
        pdf_bytes = self._pdf.generate(
            CertificateEntity(
                id=cert_id,
                application_id=app.id,
                user_id=app.user_id,
                event_id=app.event_id,
                pdf_url="",
                verify_url=verify_url,
                issued_at=datetime.now(timezone.utc),
            ),
            volunteer_name="",
            event_name="",
        )
        pdf_url = self._storage.upload(cert_id, pdf_bytes)
        now = datetime.now(timezone.utc)
        cert = CertificateEntity(
            id=cert_id,
            application_id=app.id,
            user_id=app.user_id,
            event_id=app.event_id,
            pdf_url=pdf_url,
            verify_url=verify_url,
            issued_at=now,
        )
        saved_cert = self._cert_repo.create(cert)

        updated_app = replace(app, certificate_issued=True)
        self._app_repo.update(updated_app)

        profile = self._profile_repo.get_or_create(app.user_id)
        updated_profile = replace(
            profile,
            certificate_count=profile.certificate_count + 1,
            updated_at=now,
        )
        self._profile_repo.update(updated_profile)

        self._publisher.publish(
            "volunteers.certificate.generated",
            {
                "certificate_id": str(cert_id),
                "application_id": str(app.id),
                "user_id": str(app.user_id),
                "event_id": str(app.event_id),
                "pdf_url": pdf_url,
                "verify_url": verify_url,
            },
        )

        return saved_cert
