"""Hand-rolled in-memory fakes for volunteers repository interfaces."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from apps.volunteers.domain.entities import VolunteerApplicationEntity, VolunteerRoleEntity
from apps.volunteers.domain.exceptions import RoleNotFoundError
from apps.volunteers.domain.repositories import (
    IVolunteerApplicationRepository,
    IVolunteerRoleRepository,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_role(**kwargs: object) -> VolunteerRoleEntity:
    """Build a VolunteerRoleEntity with sensible defaults for testing."""
    defaults: dict = {
        "id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "name": "Stage Manager",
        "capacity": 5,
        "is_active": True,
        "created_at": _now(),
        "organisation_id": None,
        "description": "",
    }
    defaults.update(kwargs)
    return VolunteerRoleEntity(**defaults)  # type: ignore[arg-type]


def make_application(**kwargs: object) -> VolunteerApplicationEntity:
    """Build a VolunteerApplicationEntity with sensible defaults for testing."""
    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "volunteer_role_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "status": "pending",
        "created_at": now,
        "updated_at": now,
        "check_in_at": None,
        "check_out_at": None,
        "rating": None,
        "certificate_issued": False,
    }
    defaults.update(kwargs)
    return VolunteerApplicationEntity(**defaults)  # type: ignore[arg-type]


class FakeVolunteerRoleRepository(IVolunteerRoleRepository):
    """In-memory volunteer role store with configurable approved counts."""

    def __init__(
        self,
        roles: Sequence[VolunteerRoleEntity] | None = None,
        approved_count: dict[uuid.UUID, int] | None = None,
    ) -> None:
        self._store: dict[uuid.UUID, VolunteerRoleEntity] = {r.id: r for r in (roles or [])}
        self._approved: dict[uuid.UUID, int] = approved_count or {}

    def create(self, entity: VolunteerRoleEntity) -> VolunteerRoleEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, role_id: uuid.UUID) -> VolunteerRoleEntity:
        """Raise RoleNotFoundError if absent."""
        entity = self._store.get(role_id)
        if entity is None:
            raise RoleNotFoundError("Volunteer role not found.")
        return entity

    def count_approved(self, role_id: uuid.UUID) -> int:
        """Return the configured approved count for this role."""
        return self._approved.get(role_id, 0)


class FakeVolunteerApplicationRepository(IVolunteerApplicationRepository):
    """In-memory volunteer application store."""

    def __init__(self, applications: Sequence[VolunteerApplicationEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, VolunteerApplicationEntity] = {
            a.id: a for a in (applications or [])
        }

    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if a non-cancelled application exists for this (role, user) pair."""
        return any(
            a.volunteer_role_id == role_id and a.user_id == user_id and a.status != "cancelled"
            for a in self._store.values()
        )

    def get_by_id(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Return the application or raise ApplicationNotFoundError."""
        from apps.volunteers.domain.exceptions import ApplicationNotFoundError
        entity = self._store.get(application_id)
        if entity is None:
            raise ApplicationNotFoundError("Application not found.")
        return entity

    def update(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Overwrite the stored entity and return it."""
        self._store[entity.id] = entity
        return entity

    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerApplicationEntity]:
        """Return all applications for the given role."""
        return [a for a in self._store.values() if a.volunteer_role_id == role_id]
