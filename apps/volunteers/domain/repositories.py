"""Abstract repository interfaces for the volunteers module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.volunteers.domain.entities import (
    CertificateEntity,
    VolunteerApplicationEntity,
    VolunteerProfileEntity,
    VolunteerRoleEntity,
    VolunteerShiftEntity,
)


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


class ICertificateRepository(ABC):
    """Persistence contract for Certificate records."""

    @abstractmethod
    def create(self, entity: CertificateEntity) -> CertificateEntity: ...

    @abstractmethod
    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity: ...


class IVolunteerShiftRepository(ABC):
    """Persistence contract for VolunteerShift records."""

    @abstractmethod
    def create(self, entity: VolunteerShiftEntity) -> VolunteerShiftEntity: ...

    @abstractmethod
    def get_by_id(self, shift_id: uuid.UUID) -> VolunteerShiftEntity: ...

    @abstractmethod
    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerShiftEntity]: ...


class IVolunteerProfileRepository(ABC):
    """Persistence contract for VolunteerProfile aggregates."""

    @abstractmethod
    def get_or_create(self, user_id: uuid.UUID) -> VolunteerProfileEntity: ...

    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID) -> VolunteerProfileEntity: ...

    @abstractmethod
    def update(self, entity: VolunteerProfileEntity) -> VolunteerProfileEntity: ...


class ICertificatePdfGenerator(ABC):
    """Port for generating a certificate PDF as bytes."""

    @abstractmethod
    def generate(self, certificate: CertificateEntity, volunteer_name: str, event_name: str) -> bytes: ...


class ICertificateStorage(ABC):
    """Port for storing certificate PDFs and returning a public URL."""

    @abstractmethod
    def upload(self, certificate_id: uuid.UUID, pdf_bytes: bytes) -> str: ...


class IEventPublisher(ABC):
    """Port for publishing domain events to an external message bus."""

    @abstractmethod
    def publish(self, event_type: str, payload: dict) -> None: ...
