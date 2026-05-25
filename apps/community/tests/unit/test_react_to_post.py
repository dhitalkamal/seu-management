"""Tests for ReactToPostUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.community.application.use_cases.react_to_post import ReactToPostUseCase
from apps.community.domain.entities import PostReactionEntity
from apps.community.domain.exceptions import CommunityPostNotFoundError
from apps.community.domain.repositories import IPostReactionRepository
from apps.community.tests.unit.fakes import FakeCommunityPostRepository, make_post


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_reaction(post_id: uuid.UUID, user_id: uuid.UUID, reaction_type: str = "like") -> PostReactionEntity:
    return PostReactionEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id,
        reaction_type=reaction_type,
        created_at=_now(),
    )


class FakePostReactionRepository(IPostReactionRepository):
    """In-memory reaction store keyed by (post_id, user_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], PostReactionEntity] = {}

    def upsert(self, reaction: PostReactionEntity) -> PostReactionEntity:
        self._store[(reaction.post_id, reaction.user_id)] = reaction
        return reaction

    def delete(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        from apps.community.domain.exceptions import ReactionNotFoundError

        key = (post_id, user_id)
        if key not in self._store:
            raise ReactionNotFoundError("No reaction found.")
        del self._store[key]

    def get_by_post_and_user(self, post_id: uuid.UUID, user_id: uuid.UUID) -> PostReactionEntity | None:
        return self._store.get((post_id, user_id))

    def list_by_post(self, post_id: uuid.UUID) -> list[PostReactionEntity]:
        return [r for r in self._store.values() if r.post_id == post_id]


def _make_sut(
    post_repo: FakeCommunityPostRepository,
    reaction_repo: FakePostReactionRepository | None = None,
) -> ReactToPostUseCase:
    return ReactToPostUseCase(
        post_repo=post_repo,
        reaction_repo=reaction_repo or FakePostReactionRepository(),
    )


class TestReactToPost:
    """Unit tests for ReactToPostUseCase."""

    def test_returns_reaction_entity(self) -> None:
        """Happy path returns a PostReactionEntity."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        sut = _make_sut(post_repo)
        result = sut.execute(post_id=post.id, user_id=uuid.uuid4(), reaction_type="like")
        assert isinstance(result, PostReactionEntity)
        assert result.reaction_type == "like"

    def test_reaction_count_incremented_on_post(self) -> None:
        """After reacting, the post's reaction_counts[reaction_type] increases by 1."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        sut = _make_sut(post_repo)
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="fire")
        updated = post_repo.get_by_id(post.id)
        assert updated.reaction_counts.get("fire") == 1

    def test_replaces_existing_reaction_type(self) -> None:
        """User changing reaction type replaces the old one."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        reaction_repo = FakePostReactionRepository()
        sut = _make_sut(post_repo, reaction_repo)
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="like")
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="love")
        result = reaction_repo.get_by_post_and_user(post.id, user_id)
        assert result is not None
        assert result.reaction_type == "love"

    def test_old_count_decremented_on_replacement(self) -> None:
        """Switching from like to love decrements like and increments love."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        sut = _make_sut(post_repo)
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="like")
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="love")
        updated = post_repo.get_by_id(post.id)
        assert updated.reaction_counts.get("like", 0) == 0
        assert updated.reaction_counts.get("love", 0) == 1

    def test_multiple_users_same_type(self) -> None:
        """Two users adding same reaction each increment the count by 1."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        sut = _make_sut(post_repo)
        sut.execute(post_id=post.id, user_id=uuid.uuid4(), reaction_type="like")
        sut.execute(post_id=post.id, user_id=uuid.uuid4(), reaction_type="like")
        updated = post_repo.get_by_id(post.id)
        assert updated.reaction_counts.get("like", 0) == 2

    def test_raises_if_post_not_found(self) -> None:
        """CommunityPostNotFoundError raised if post does not exist."""
        post_repo = FakeCommunityPostRepository()
        sut = _make_sut(post_repo)
        with pytest.raises(CommunityPostNotFoundError):
            sut.execute(post_id=uuid.uuid4(), user_id=uuid.uuid4(), reaction_type="like")
