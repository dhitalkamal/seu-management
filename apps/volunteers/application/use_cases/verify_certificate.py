"""Use case: verify a volunteer certificate by its unique ID."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.repositories import ICertificateRepository


class VerifyCertificateUseCase:
    """Return the certificate record for public QR verification."""

    def __init__(self, cert_repo: ICertificateRepository) -> None:
        self._certs = cert_repo

    def execute(self, *, certificate_id: uuid.UUID) -> CertificateEntity:
        """
        Fetch and return the certificate, or raise if not found.

        @raises CertificateNotFoundError if the certificate does not exist
        """
        return self._certs.get_by_id(certificate_id)
