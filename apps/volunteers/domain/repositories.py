"""Abstract repository interfaces for the volunteers module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.volunteers.domain.entities import VolunteerApplicationEntity, VolunteerRoleEntity


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
