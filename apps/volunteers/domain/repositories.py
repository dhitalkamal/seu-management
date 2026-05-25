"""Abstract repository interfaces for the volunteers module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from apps.volunteers.domain.entities import CertificateEntity, VolunteerApplicationEntity, VolunteerRoleEntity


class IVolunteerRoleRepository(ABC):
    """Persistence contract for VolunteerRole aggregates."""

    @abstractmethod
    def create(self, entity: VolunteerRoleEntity) -> VolunteerRoleEntity: ...

    @abstractmethod
    def get_by_id(self, role_id: uuid.UUID) -> VolunteerRoleEntity: ...

    @abstractmethod
    def count_approved(self, role_id: uuid.UUID) -> int: ...


class IVolunteerApplicationRepository(ABC):
    """Persistence contract for VolunteerApplication records."""

    @abstractmethod
    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity: ...

    @abstractmethod
    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    @abstractmethod
    def get_by_id(self, application_id: uuid.UUID) -> VolunteerApplicationEntity: ...

    @abstractmethod
    def update(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity: ...

    @abstractmethod
    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerApplicationEntity]: ...


class IParticipationContextClient(ABC):
    """Port for checking and recording participation context in participation-service."""

    @abstractmethod
    def is_attendee(self, event_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    @abstractmethod
    def set_volunteer(self, event_id: uuid.UUID, user_id: uuid.UUID) -> None: ...


class ICertificateRepository(ABC):
    """Persistence contract for Certificate records."""

    @abstractmethod
    def create(self, entity: CertificateEntity) -> CertificateEntity: ...

    @abstractmethod
    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity: ...


class ICertificatePdfGenerator(ABC):
    """Port for generating certificate PDF bytes, decoupled from reportlab."""

    @abstractmethod
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
    ) -> bytes: ...


class ICertificateStorage(ABC):
    """Port for uploading certificate PDFs to object storage."""

    @abstractmethod
    def upload(self, *, file_bytes: bytes, certificate_id: uuid.UUID) -> str: ...
