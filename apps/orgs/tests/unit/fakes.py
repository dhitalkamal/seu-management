"""Hand-rolled in-memory fakes for orgs repository interfaces."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import OrgNotFoundError
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgMemberRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_org(**kwargs: object) -> OrgEntity:
    """Build an OrgEntity with sensible defaults for testing."""
    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "created_by": uuid.uuid4(),
        "name": "Test Organisation",
        "slug": "test-org",
        "contact_email": "org@example.com",
        "status": "pending_review",
        "is_verified": False,
        "created_at": now,
        "updated_at": now,
        "description": "",
        "website": "",
        "logo_url": "",
        "deleted_at": None,
    }
    defaults.update(kwargs)
    return OrgEntity(**defaults)  # type: ignore[arg-type]


class FakeOrgRepository(IOrganisationRepository):
    """In-memory organisation store."""

    def __init__(self, orgs: Sequence[OrgEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, OrgEntity] = {o.id: o for o in (orgs or [])}

    def create(self, entity: OrgEntity) -> OrgEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity:
        """Raise OrgNotFoundError if absent or soft-deleted."""
        entity = self._store.get(org_id)
        if entity is None or entity.deleted_at is not None:
            raise OrgNotFoundError("Organisation not found.")
        return entity

    def get_by_slug(self, slug: str) -> OrgEntity | None:
        """Return the org with this slug or None."""
        for o in self._store.values():
            if o.slug == slug:
                return o
        return None

    def update(self, entity: OrgEntity) -> OrgEntity:
        """Overwrite the stored entity and return it."""
        self._store[entity.id] = entity
        return entity

    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]:
        """Return all non-deleted orgs in the store."""
        return [o for o in self._store.values() if o.deleted_at is None]


class FakeOrgMemberRepository(IOrgMemberRepository):
    """In-memory org member store."""

    def __init__(self, members: Sequence[OrgMemberEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, OrgMemberEntity] = {m.id: m for m in (members or [])}

    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if an active membership exists for this (org, user) pair."""
        return any(m.organisation_id == org_id and m.user_id == user_id and m.is_active for m in self._store.values())
