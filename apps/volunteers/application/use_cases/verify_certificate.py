"""Use case: verify a certificate by its public ID."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import CertificateEntity
from apps.volunteers.domain.repositories import ICertificateRepository


class VerifyCertificateUseCase:
    """Fetches a certificate by ID for public verification."""

    def __init__(self, certificate_repo: ICertificateRepository) -> None:
        self._cert_repo = certificate_repo

    def execute(self, certificate_id: uuid.UUID) -> CertificateEntity:
        """Return the certificate. Raises CertificateNotFoundError if absent."""
        return self._cert_repo.get_by_id(certificate_id)
