"""In-memory fakes for community unit tests. No DB, no mocks."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import (
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
)
from apps.community.domain.exceptions import CommunityNotFoundError, CommunityPostNotFoundError
from apps.community.domain.repositories import (
    ICommunityMemberRepository,
    ICommunityPostRepository,
    ICommunityRepository,
)


def make_community(
    *,
    status: str = "active",
    privacy: str = "public",
    member_count: int = 0,
    slug: str | None = None,
) -> CommunityEntity:
    """Build a CommunityEntity with sensible defaults for testing."""
    _id = uuid.uuid4()
    return CommunityEntity(
        id=_id,
        created_by=uuid.uuid4(),
        name="Test Community",
        slug=slug or str(_id)[:8],
        privacy=privacy,
        member_count=member_count,
        created_at=datetime.now(timezone.utc),
    )


def make_post(community_id: uuid.UUID | None = None) -> CommunityPostEntity:
    """Build a CommunityPostEntity with sensible defaults for testing."""
    return CommunityPostEntity(
        id=uuid.uuid4(),
        community_id=community_id or uuid.uuid4(),
        author_id=uuid.uuid4(),
        content="Hello world",
        post_type="text",
        status="published",
        like_count=0,
        comment_count=0,
        report_count=0,
        is_pinned=False,
        created_at=datetime.now(timezone.utc),
    )


class FakeCommunityRepository(ICommunityRepository):
    """In-memory community store for unit tests."""

    def __init__(self, communities: list[CommunityEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, CommunityEntity] = {c.id: c for c in (communities or [])}
        self._slugs: set[str] = {c.slug for c in (communities or [])}

    def list_all(self) -> list[CommunityEntity]:
        """Return all non-deleted communities."""
        return [c for c in self._store.values() if c.deleted_at is None]

    def get_by_id(self, community_id: uuid.UUID) -> CommunityEntity:
        """Raise CommunityNotFoundError if not found or soft-deleted."""
        c = self._store.get(community_id)
        if c is None or c.deleted_at is not None:
            raise CommunityNotFoundError("Not found.")
        return c

    def create(self, community: CommunityEntity) -> None:
        """Store the community."""
        self._store[community.id] = community
        self._slugs.add(community.slug)

    def update(self, community: CommunityEntity) -> None:
        """Update an existing community."""
        self._store[community.id] = community

    def slug_exists(self, slug: str) -> bool:
        """Return True if the slug is taken."""
        return slug in self._slugs


class FakeCommunityMemberRepository(ICommunityMemberRepository):
    """In-memory membership store for unit tests."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], CommunityMemberEntity] = {}

    def get_membership(self, community_id: uuid.UUID, user_id: uuid.UUID) -> CommunityMemberEntity | None:
        """Return membership or None."""
        return self._store.get((community_id, user_id))

    def create(self, member: CommunityMemberEntity) -> None:
        """Store the membership."""
        self._store[(member.community_id, member.user_id)] = member

    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityMemberEntity]:
        """Return all members of a community."""
        return [m for m in self._store.values() if m.community_id == community_id]


class FakeCommunityPostRepository(ICommunityPostRepository):
    """In-memory post store for unit tests."""

    def __init__(self, posts: list[CommunityPostEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, CommunityPostEntity] = {p.id: p for p in (posts or [])}

    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityPostEntity]:
        """Return published posts for a community."""
        return [p for p in self._store.values() if p.community_id == community_id and p.status == "published"]

    def get_by_id(self, post_id: uuid.UUID) -> CommunityPostEntity:
        """Raise CommunityPostNotFoundError if not found."""
        p = self._store.get(post_id)
        if p is None:
            raise CommunityPostNotFoundError("Not found.")
        return p

    def create(self, post: CommunityPostEntity) -> None:
        """Store the post."""
        self._store[post.id] = post

    def update(self, post: CommunityPostEntity) -> None:
        """Update an existing post."""
        self._store[post.id] = post
