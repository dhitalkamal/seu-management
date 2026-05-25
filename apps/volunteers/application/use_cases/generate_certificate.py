"""Use case: generate a QR-verified PDF certificate for a completed volunteer application."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.exceptions import CertificateAlreadyIssuedError, CertificateNotEligibleError
from apps.volunteers.domain.repositories import (
    ICertificatePdfGenerator,
    ICertificateRepository,
    ICertificateStorage,
    IVolunteerApplicationRepository,
)

# base URL for the public certificate verification page
_VERIFY_BASE_URL = "https://sansaar.com/verify/cert"


class GenerateCertificateUseCase:
    """Generate, store, and record a PDF certificate for a rated and checked-out volunteer."""

    def __init__(
        self,
        app_repo: IVolunteerApplicationRepository,
        cert_repo: ICertificateRepository,
        pdf_generator: ICertificatePdfGenerator,
        storage: ICertificateStorage,
    ) -> None:
        self._apps = app_repo
        self._certs = cert_repo
        self._pdf = pdf_generator
        self._storage = storage

    def execute(
        self,
        *,
        application_id: uuid.UUID,
        volunteer_name: str,
        event_name: str,
        role_name: str,
        org_id: uuid.UUID | None,
    ) -> CertificateEntity:
        """
        Validate eligibility, generate PDF, upload to storage, and persist the certificate record.

        @raises CertificateNotEligibleError if the volunteer has not checked in, out, and been rated
        @raises CertificateAlreadyIssuedError if a certificate was already generated for this application
        """
        app = self._apps.get_by_id(application_id)

        # ! certificate requires completed shift (both check-in and check-out) and a rating
        if app.check_in_at is None or app.check_out_at is None or app.rating is None:
            raise CertificateNotEligibleError("Certificate requires a completed shift (check-in and check-out) and a rating.")

        if app.certificate_issued:
            raise CertificateAlreadyIssuedError("A certificate has already been issued for this application.")

        certificate_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        verify_url = f"{_VERIFY_BASE_URL}/{certificate_id}"

        pdf_bytes = self._pdf.generate(
            certificate_id=certificate_id,
            volunteer_name=volunteer_name,
            event_name=event_name,
            role_name=role_name,
            hours_worked=app.hours_worked,
            rating=app.rating,
            issued_at=now,
            verify_url=verify_url,
        )

        pdf_url = self._storage.upload(file_bytes=pdf_bytes, certificate_id=certificate_id)

        certificate = CertificateEntity(
            id=certificate_id,
            application_id=application_id,
            volunteer_id=app.user_id,
            event_id=app.event_id,
            org_id=org_id,
            volunteer_name=volunteer_name,
            event_name=event_name,
            role_name=role_name,
            pdf_url=pdf_url,
            issued_at=now,
            hours_worked=app.hours_worked,
            rating=app.rating,
        )

        self._certs.create(certificate)

        app.certificate_issued = True
        self._apps.update(app)

        return certificate
