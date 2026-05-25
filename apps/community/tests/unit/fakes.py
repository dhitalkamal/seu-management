"""In-memory fakes for community unit tests. No DB, no mocks."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import (
    CommentReactionEntity,
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
    PostCommentEntity,
    PostReactionEntity,
)
from apps.community.domain.exceptions import (
    CommentNotFoundError,
    CommentReactionNotFoundError,
    CommunityNotFoundError,
    CommunityPostNotFoundError,
    ReactionNotFoundError,
)
from apps.community.domain.repositories import (
    ICommentReactionRepository,
    ICommunityMemberRepository,
    ICommunityPostRepository,
    ICommunityRepository,
    IPostCommentRepository,
    IPostReactionRepository,
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


class FakePostReactionRepository(IPostReactionRepository):
    """In-memory reaction store keyed by (post_id, user_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], PostReactionEntity] = {}

    def upsert(self, reaction: PostReactionEntity) -> PostReactionEntity:
        """Insert or replace the reaction for (post_id, user_id)."""
        self._store[(reaction.post_id, reaction.user_id)] = reaction
        return reaction

    def delete(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove the reaction; raise ReactionNotFoundError if absent."""
        key = (post_id, user_id)
        if key not in self._store:
            raise ReactionNotFoundError("No reaction found.")
        del self._store[key]

    def get_by_post_and_user(self, post_id: uuid.UUID, user_id: uuid.UUID) -> PostReactionEntity | None:
        """Return the reaction if it exists, else None."""
        return self._store.get((post_id, user_id))

    def list_by_post(self, post_id: uuid.UUID) -> list[PostReactionEntity]:
        """Return all reactions for a given post."""
        return [r for r in self._store.values() if r.post_id == post_id]


def make_reaction(
    post_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    reaction_type: str = "like",
) -> PostReactionEntity:
    """Build a PostReactionEntity with sensible defaults for testing."""
    from datetime import datetime, timezone

    return PostReactionEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id or uuid.uuid4(),
        reaction_type=reaction_type,
        created_at=datetime.now(timezone.utc),
    )


def make_comment(
    post_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    parent_id: uuid.UUID | None = None,
    deleted: bool = False,
) -> PostCommentEntity:
    """Build a PostCommentEntity with sensible defaults for testing."""
    now = datetime.now(timezone.utc)
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=post_id or uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        content="A comment",
        is_hidden=False,
        parent_id=parent_id,
        created_at=now,
        updated_at=now,
        deleted_at=now if deleted else None,
    )


class FakePostCommentRepository(IPostCommentRepository):
    """In-memory comment store keyed by comment id."""

    def __init__(self, comments: list[PostCommentEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, PostCommentEntity] = {c.id: c for c in (comments or [])}

    def create(self, comment: PostCommentEntity) -> PostCommentEntity:
        """Store and return the comment."""
        self._store[comment.id] = comment
        return comment

    def get_by_id(self, comment_id: uuid.UUID) -> PostCommentEntity:
        """Raise CommentNotFoundError if absent."""
        c = self._store.get(comment_id)
        if c is None:
            raise CommentNotFoundError("Not found.")
        return c

    def list_by_post(self, post_id: uuid.UUID) -> list[PostCommentEntity]:
        """Return non-deleted comments for the post."""
        return [c for c in self._store.values() if c.post_id == post_id and c.deleted_at is None]

    def update(self, comment: PostCommentEntity) -> None:
        """Persist changes to an existing comment."""
        self._store[comment.id] = comment


class FakeCommentReactionRepository(ICommentReactionRepository):
    """In-memory comment reaction store keyed by (comment_id, user_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], CommentReactionEntity] = {}

    def upsert(self, reaction: CommentReactionEntity) -> CommentReactionEntity:
        """Insert or replace the reaction for (comment_id, user_id)."""
        self._store[(reaction.comment_id, reaction.user_id)] = reaction
        return reaction

    def delete(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove the reaction; raise CommentReactionNotFoundError if absent."""
        key = (comment_id, user_id)
        if key not in self._store:
            raise CommentReactionNotFoundError("No reaction.")
        del self._store[key]

    def get_by_comment_and_user(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> CommentReactionEntity | None:
        """Return the reaction if it exists, else None."""
        return self._store.get((comment_id, user_id))

    def list_by_comment(self, comment_id: uuid.UUID) -> list[CommentReactionEntity]:
        """Return all reactions for a given comment."""
        return [r for r in self._store.values() if r.comment_id == comment_id]
