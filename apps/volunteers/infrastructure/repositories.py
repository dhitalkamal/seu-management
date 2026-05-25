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
        return VolunteerApplication.objects.filter(volunteer_role_id=role_id, status="approved").count()


class DjangoVolunteerApplicationRepository(IVolunteerApplicationRepository):
    """Persists VolunteerApplication entities using the Django ORM."""

    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Persist a new application and return the saved entity."""
        obj = VolunteerApplication.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if a non-cancelled application exists for this (role, user) pair."""
        return VolunteerApplication.objects.filter(volunteer_role_id=role_id, user_id=user_id).exclude(status="cancelled").exists()

    def get_by_id(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Fetch by ID. Raises ApplicationNotFoundError if absent."""
        try:
            return VolunteerApplication.objects.get(id=application_id).to_entity()
        except VolunteerApplication.DoesNotExist:
            from apps.volunteers.domain.exceptions import ApplicationNotFoundError

            raise ApplicationNotFoundError("Application not found.")

    def update(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Update mutable fields and return the entity."""
        VolunteerApplication.objects.filter(id=entity.id).update(status=entity.status)
        return entity

    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerApplicationEntity]:
        """Return all applications for the given role, newest first."""
        return [obj.to_entity() for obj in VolunteerApplication.objects.filter(volunteer_role_id=role_id).order_by("-created_at")]
