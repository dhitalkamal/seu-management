"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerApplicationEntity, VolunteerRoleEntity
from apps.volunteers.domain.exceptions import RoleNotFoundError
from apps.volunteers.domain.repositories import (
    IVolunteerApplicationRepository,
    IVolunteerRoleRepository,
)
from apps.volunteers.infrastructure.models import VolunteerApplication, VolunteerRole


class DjangoVolunteerRoleRepository(IVolunteerRoleRepository):
    """Persists VolunteerRole entities using the Django ORM."""

    def create(self, entity: VolunteerRoleEntity) -> VolunteerRoleEntity:
        """Persist a new role and return the saved entity."""
        obj = VolunteerRole.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, role_id: uuid.UUID) -> VolunteerRoleEntity:
        """Fetch by id. Raises RoleNotFoundError if absent."""
        try:
            return VolunteerRole.objects.get(id=role_id).to_entity()
        except VolunteerRole.DoesNotExist:
            raise RoleNotFoundError("Volunteer role not found.")

    def count_approved(self, role_id: uuid.UUID) -> int:
        """Count approved applications for this role (used for capacity check)."""
        return VolunteerApplication.objects.filter(
            volunteer_role_id=role_id, status="approved"
        ).count()


class DjangoVolunteerApplicationRepository(IVolunteerApplicationRepository):
    """Persists VolunteerApplication entities using the Django ORM."""

    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Persist a new application and return the saved entity."""
        obj = VolunteerApplication.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if a non-cancelled application exists for this (role, user) pair."""
        return (
            VolunteerApplication.objects.filter(volunteer_role_id=role_id, user_id=user_id)
            .exclude(status="cancelled")
            .exists()
        )
