"""Unit tests for create_invite, decline_invite, revoke_invite, and list_invites use cases."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence

import pytest

from apps.orgs.domain.entities import OrgEntity, OrgInviteEntity
from apps.orgs.domain.exceptions import (
    InviteAlreadyExistsError,
    InviteNotFoundError,
    InviteNotPendingError,
    OrgNotFoundError,
)
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgInviteRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_org(**kwargs: object) -> OrgEntity:
    """Build an OrgEntity with sensible defaults."""
    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "created_by": uuid.uuid4(),
        "name": "Test Org",
        "slug": "test-org",
        "contact_email": "org@example.com",
        "status": "active",
        "is_verified": True,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return OrgEntity(**defaults)  # type: ignore[arg-type]


def _make_invite(**kwargs: object) -> OrgInviteEntity:
    """Build an OrgInviteEntity with sensible defaults."""
    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "org_id": uuid.uuid4(),
        "inviter_id": uuid.uuid4(),
        "invitee_email": "invitee@example.com",
        "role": "member",
        "status": "pending",
        "created_at": now,
        "expires_at": now + timedelta(days=7),
        "accepted_by": None,
    }
    defaults.update(kwargs)
    return OrgInviteEntity(**defaults)  # type: ignore[arg-type]


class FakeOrgRepo(IOrganisationRepository):
    """Minimal in-memory org store."""

    def __init__(self, orgs: Sequence[OrgEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, OrgEntity] = {o.id: o for o in (orgs or [])}

    def create(self, entity: OrgEntity) -> OrgEntity:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity:
        entity = self._store.get(org_id)
        if entity is None:
            raise OrgNotFoundError("Organisation not found.")
        return entity

    def get_by_slug(self, slug: str) -> OrgEntity | None:
        return None

    def update(self, entity: OrgEntity) -> OrgEntity:
        self._store[entity.id] = entity
        return entity

    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]:
        return list(self._store.values())


class FakeInviteRepo(IOrgInviteRepository):
    """In-memory invite store."""

    def __init__(self, invites: Sequence[OrgInviteEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, OrgInviteEntity] = {i.id: i for i in (invites or [])}

    def create(self, entity: OrgInviteEntity) -> OrgInviteEntity:
        self._store[entity.id] = entity
        return entity

    def get_by_id(self, invite_id: uuid.UUID) -> OrgInviteEntity:
        entity = self._store.get(invite_id)
        if entity is None:
            raise InviteNotFoundError("Invite not found.")
        return entity

    def update(self, entity: OrgInviteEntity) -> OrgInviteEntity:
        self._store[entity.id] = entity
        return entity

    def list_pending_for_org(self, org_id: uuid.UUID) -> list[OrgInviteEntity]:
        return [i for i in self._store.values() if i.org_id == org_id and i.status == "pending"]

    def get_pending_by_email(self, org_id: uuid.UUID, email: str) -> OrgInviteEntity | None:
        for inv in self._store.values():
            if inv.org_id == org_id and inv.invitee_email.lower() == email.lower() and inv.status == "pending":
                return inv
        return None


# * CreateInviteUseCase tests


def test_create_invite_returns_entity() -> None:
    """CreateInviteUseCase persists and returns a pending invite."""
    from apps.orgs.application.use_cases.create_invite import CreateInviteUseCase

    org = _make_org()
    org_repo = FakeOrgRepo([org])
    invite_repo = FakeInviteRepo()

    result = CreateInviteUseCase(org_repo, invite_repo).execute(
        org_id=org.id,
        inviter_id=uuid.uuid4(),
        invitee_email="new@example.com",
        role="member",
    )

    assert result.status == "pending"
    assert result.org_id == org.id
    assert result.invitee_email == "new@example.com"


def test_create_invite_raises_when_org_not_found() -> None:
    """OrgNotFoundError raised when the org does not exist."""
    from apps.orgs.application.use_cases.create_invite import CreateInviteUseCase

    with pytest.raises(OrgNotFoundError):
        CreateInviteUseCase(FakeOrgRepo(), FakeInviteRepo()).execute(
            org_id=uuid.uuid4(),
            inviter_id=uuid.uuid4(),
            invitee_email="a@b.com",
            role="member",
        )


def test_create_invite_raises_when_duplicate_pending() -> None:
    """InviteAlreadyExistsError raised when a pending invite for this email already exists."""
    from apps.orgs.application.use_cases.create_invite import CreateInviteUseCase

    org = _make_org()
    existing = _make_invite(org_id=org.id, invitee_email="dup@example.com")
    org_repo = FakeOrgRepo([org])
    invite_repo = FakeInviteRepo([existing])

    with pytest.raises(InviteAlreadyExistsError):
        CreateInviteUseCase(org_repo, invite_repo).execute(
            org_id=org.id,
            inviter_id=uuid.uuid4(),
            invitee_email="dup@example.com",
            role="admin",
        )


# * DeclineInviteUseCase tests


def test_decline_invite_marks_declined() -> None:
    """DeclineInviteUseCase sets status=declined on a pending invite."""
    from apps.orgs.application.use_cases.decline_invite import DeclineInviteUseCase

    invite = _make_invite()
    invite_repo = FakeInviteRepo([invite])

    result = DeclineInviteUseCase(invite_repo).execute(invite_id=invite.id)

    assert result.status == "declined"


def test_decline_invite_raises_when_not_pending() -> None:
    """InviteNotPendingError raised when the invite is already accepted or revoked."""
    from apps.orgs.application.use_cases.decline_invite import DeclineInviteUseCase

    invite = _make_invite(status="accepted")
    invite_repo = FakeInviteRepo([invite])

    with pytest.raises(InviteNotPendingError):
        DeclineInviteUseCase(invite_repo).execute(invite_id=invite.id)


# * RevokeInviteUseCase tests


def test_revoke_invite_marks_revoked() -> None:
    """RevokeInviteUseCase sets status=revoked on a pending invite."""
    from apps.orgs.application.use_cases.revoke_invite import RevokeInviteUseCase

    invite = _make_invite()
    invite_repo = FakeInviteRepo([invite])

    result = RevokeInviteUseCase(invite_repo).execute(invite_id=invite.id)

    assert result.status == "revoked"


def test_revoke_invite_raises_when_not_pending() -> None:
    """InviteNotPendingError raised when trying to revoke an already-accepted invite."""
    from apps.orgs.application.use_cases.revoke_invite import RevokeInviteUseCase

    invite = _make_invite(status="accepted")
    invite_repo = FakeInviteRepo([invite])

    with pytest.raises(InviteNotPendingError):
        RevokeInviteUseCase(invite_repo).execute(invite_id=invite.id)


# * ListInvitesUseCase tests


def test_list_invites_returns_pending_only() -> None:
    """ListInvitesUseCase returns only pending invites for the given org."""
    from apps.orgs.application.use_cases.list_invites import ListInvitesUseCase

    org = _make_org()
    pending = _make_invite(org_id=org.id, status="pending")
    accepted = _make_invite(org_id=org.id, status="accepted")
    org_repo = FakeOrgRepo([org])
    invite_repo = FakeInviteRepo([pending, accepted])

    results = ListInvitesUseCase(org_repo, invite_repo).execute(org_id=org.id)

    assert len(results) == 1
    assert results[0].id == pending.id


def test_list_invites_raises_when_org_not_found() -> None:
    """OrgNotFoundError raised when the org does not exist."""
    from apps.orgs.application.use_cases.list_invites import ListInvitesUseCase

    with pytest.raises(OrgNotFoundError):
        ListInvitesUseCase(FakeOrgRepo(), FakeInviteRepo()).execute(org_id=uuid.uuid4())
