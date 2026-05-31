"""Unit tests for AcceptInviteUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Sequence

import pytest

from apps.orgs.domain.entities import OrgInviteEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import InviteExpiredError, InviteNotFoundError, InviteNotPendingError
from apps.orgs.domain.repositories import IOrgInviteRepository, IOrgMemberRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_invite(**kwargs: object) -> OrgInviteEntity:
    """Build an OrgInviteEntity with sensible defaults for testing."""
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


class FakeMemberRepo(IOrgMemberRepository):
    """In-memory member store."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, OrgMemberEntity] = {}

    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity:
        self._store[entity.id] = entity
        return entity

    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return any(m.organization_id == org_id and m.user_id == user_id and m.is_active for m in self._store.values())

    def list_by_org(self, org_id: uuid.UUID) -> list[OrgMemberEntity]:
        return [m for m in self._store.values() if m.organization_id == org_id and m.is_active]


def test_accept_invite_creates_membership_and_marks_accepted() -> None:
    """Accepting a pending invite creates an org membership and sets status=accepted."""
    from apps.orgs.application.use_cases.accept_invite import AcceptInviteUseCase

    invite = _make_invite()
    invite_repo = FakeInviteRepo([invite])
    member_repo = FakeMemberRepo()
    user_id = uuid.uuid4()

    result = AcceptInviteUseCase(invite_repo, member_repo).execute(
        invite_id=invite.id,
        user_id=user_id,
    )

    assert result.status == "accepted"
    assert result.accepted_by == user_id
    assert member_repo.exists(invite.org_id, user_id)


def test_accept_invite_raises_when_not_pending() -> None:
    """InviteNotPendingError raised when the invite status is not pending."""
    from apps.orgs.application.use_cases.accept_invite import AcceptInviteUseCase

    invite = _make_invite(status="declined")
    invite_repo = FakeInviteRepo([invite])
    member_repo = FakeMemberRepo()

    with pytest.raises(InviteNotPendingError):
        AcceptInviteUseCase(invite_repo, member_repo).execute(
            invite_id=invite.id,
            user_id=uuid.uuid4(),
        )


def test_accept_invite_raises_when_expired() -> None:
    """InviteExpiredError raised when the invite has passed its expiry date."""
    from apps.orgs.application.use_cases.accept_invite import AcceptInviteUseCase

    past = _now() - timedelta(days=1)
    invite = _make_invite(expires_at=past)
    invite_repo = FakeInviteRepo([invite])
    member_repo = FakeMemberRepo()

    with pytest.raises(InviteExpiredError):
        AcceptInviteUseCase(invite_repo, member_repo).execute(
            invite_id=invite.id,
            user_id=uuid.uuid4(),
        )


def test_accept_invite_raises_when_invite_not_found() -> None:
    """InviteNotFoundError raised when the invite does not exist."""
    from apps.orgs.application.use_cases.accept_invite import AcceptInviteUseCase

    invite_repo = FakeInviteRepo()
    member_repo = FakeMemberRepo()

    with pytest.raises(InviteNotFoundError):
        AcceptInviteUseCase(invite_repo, member_repo).execute(
            invite_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
        )
