"""Hand-rolled in-memory fakes for volunteers repository interfaces."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from apps.volunteers.domain.entities import (
    CertificateEntity,
    VolunteerApplicationEntity,
    VolunteerProfileEntity,
    VolunteerRoleEntity,
    VolunteerShiftEntity,
)
from apps.volunteers.domain.exceptions import (
    ApplicationNotFoundError,
    CertificateNotFoundError,
    RoleNotFoundError,
    ShiftNotFoundError,
)
from apps.volunteers.domain.repositories import (
    ICertificatePdfGenerator,
    ICertificateRepository,
    ICertificateStorage,
    IEventPublisher,
    IVolunteerApplicationRepository,
    IVolunteerProfileRepository,
    IVolunteerRoleRepository,
    IVolunteerShiftRepository,
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
        "feedback": None,
    }
    defaults.update(kwargs)
    return VolunteerApplicationEntity(**defaults)  # type: ignore[arg-type]


def make_certificate(**kwargs: object) -> CertificateEntity:
    """Build a CertificateEntity with sensible defaults for testing."""
    defaults: dict = {
        "id": uuid.uuid4(),
        "application_id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "pdf_url": "https://example.com/certs/test.pdf",
        "verify_url": "https://sansaar.com/verify/cert/test",
        "issued_at": _now(),
    }
    defaults.update(kwargs)
    return CertificateEntity(**defaults)  # type: ignore[arg-type]


def make_shift(**kwargs: object) -> VolunteerShiftEntity:
    """Build a VolunteerShiftEntity with sensible defaults for testing."""
    from datetime import timedelta

    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "role_id": uuid.uuid4(),
        "event_id": uuid.uuid4(),
        "starts_at": now + timedelta(hours=1),
        "ends_at": now + timedelta(hours=4),
        "capacity": 10,
        "created_at": now,
        "location": None,
        "description": None,
    }
    defaults.update(kwargs)
    return VolunteerShiftEntity(**defaults)  # type: ignore[arg-type]


def make_profile(**kwargs: object) -> VolunteerProfileEntity:
    """Build a VolunteerProfileEntity with sensible defaults for testing."""
    defaults: dict = {
        "id": uuid.uuid4(),
        "user_id": uuid.uuid4(),
        "average_rating": None,
        "total_ratings": 0,
        "total_hours": 0.0,
        "certificate_count": 0,
        "updated_at": _now(),
    }
    defaults.update(kwargs)
    return VolunteerProfileEntity(**defaults)  # type: ignore[arg-type]


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
        self._store: dict[uuid.UUID, VolunteerApplicationEntity] = {a.id: a for a in (applications or [])}

    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if a non-cancelled application exists for this (role, user) pair."""
        return any(a.volunteer_role_id == role_id and a.user_id == user_id and a.status != "cancelled" for a in self._store.values())

    def get_by_id(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Return the application or raise ApplicationNotFoundError."""
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


class FakeCertificateRepository(ICertificateRepository):
    """In-memory certificate store."""

    def __init__(self, certificates: Sequence[CertificateEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, CertificateEntity] = {c.id: c for c in (certificates or [])}

    def create(self, entity: CertificateEntity) -> CertificateEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity:
        """Return the certificate or raise CertificateNotFoundError."""
        entity = self._store.get(certificate_id)
        if entity is None:
            raise CertificateNotFoundError("Certificate not found.")
        return entity


class FakeVolunteerShiftRepository(IVolunteerShiftRepository):
    """In-memory volunteer shift store."""

    def __init__(self, shifts: Sequence[VolunteerShiftEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, VolunteerShiftEntity] = {s.id: s for s in (shifts or [])}

    def create(self, entity: VolunteerShiftEntity) -> VolunteerShiftEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, shift_id: uuid.UUID) -> VolunteerShiftEntity:
        """Return the shift or raise ShiftNotFoundError."""
        entity = self._store.get(shift_id)
        if entity is None:
            raise ShiftNotFoundError("Volunteer shift not found.")
        return entity

    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerShiftEntity]:
        """Return all shifts for the given role."""
        return [s for s in self._store.values() if s.role_id == role_id]


class FakeVolunteerProfileRepository(IVolunteerProfileRepository):
    """In-memory volunteer profile store."""

    def __init__(self, profiles: Sequence[VolunteerProfileEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, VolunteerProfileEntity] = {p.user_id: p for p in (profiles or [])}

    def get_or_create(self, user_id: uuid.UUID) -> VolunteerProfileEntity:
        """Return existing profile or create a blank one."""
        if user_id not in self._store:
            self._store[user_id] = make_profile(user_id=user_id)
        return self._store[user_id]

    def get_by_user_id(self, user_id: uuid.UUID) -> VolunteerProfileEntity:
        """Return the profile for this user."""
        return self.get_or_create(user_id)

    def update(self, entity: VolunteerProfileEntity) -> VolunteerProfileEntity:
        """Overwrite the stored profile and return it."""
        self._store[entity.user_id] = entity
        return entity


class FakeCertificatePdfGenerator(ICertificatePdfGenerator):
    """Returns a fixed bytes stub instead of a real PDF."""

    def generate(self, certificate: CertificateEntity, volunteer_name: str, event_name: str) -> bytes:
        """Return stub bytes."""
        return b"%PDF-stub"


class FakeCertificateStorage(ICertificateStorage):
    """Stores PDF bytes in memory and returns a deterministic URL."""

    def __init__(self) -> None:
        self.uploads: dict[uuid.UUID, bytes] = {}

    def upload(self, certificate_id: uuid.UUID, pdf_bytes: bytes) -> str:
        """Store and return a fake URL."""
        self.uploads[certificate_id] = pdf_bytes
        return f"https://fake-storage.example.com/certs/{certificate_id}.pdf"


class FakeEventPublisher(IEventPublisher):
    """Captures published events for assertion."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def publish(self, event_type: str, payload: dict) -> None:
        """Record the event."""
        self.events.append({"type": event_type, "payload": payload})
