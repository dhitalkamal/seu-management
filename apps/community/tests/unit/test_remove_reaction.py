"""Tests for RemoveReactionUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.community.application.use_cases.remove_reaction import RemoveReactionUseCase
from apps.community.domain.entities import PostReactionEntity
from apps.community.domain.exceptions import ReactionNotFoundError
from apps.community.domain.repositories import IPostReactionRepository
from apps.community.tests.unit.fakes import FakeCommunityPostRepository, make_post


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FakePostReactionRepository(IPostReactionRepository):
    """In-memory reaction store keyed by (post_id, user_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], PostReactionEntity] = {}

    def upsert(self, reaction: PostReactionEntity) -> PostReactionEntity:
        self._store[(reaction.post_id, reaction.user_id)] = reaction
        return reaction

    def delete(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        key = (post_id, user_id)
        if key not in self._store:
            raise ReactionNotFoundError("No reaction found.")
        del self._store[key]

    def get_by_post_and_user(self, post_id: uuid.UUID, user_id: uuid.UUID) -> PostReactionEntity | None:
        return self._store.get((post_id, user_id))

    def list_by_post(self, post_id: uuid.UUID) -> list[PostReactionEntity]:
        return [r for r in self._store.values() if r.post_id == post_id]


def _seed_reaction(
    repo: FakePostReactionRepository,
    post_id: uuid.UUID,
    user_id: uuid.UUID,
    reaction_type: str = "like",
) -> PostReactionEntity:
    r = PostReactionEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id,
        reaction_type=reaction_type,
        created_at=_now(),
    )
    repo.upsert(r)
    return r


def _make_sut(
    post_repo: FakeCommunityPostRepository,
    reaction_repo: FakePostReactionRepository | None = None,
) -> RemoveReactionUseCase:
    return RemoveReactionUseCase(
        post_repo=post_repo,
        reaction_repo=reaction_repo or FakePostReactionRepository(),
    )


class TestRemoveReaction:
    """Unit tests for RemoveReactionUseCase."""

    def test_removes_existing_reaction(self) -> None:
        """Happy path - reaction is removed from the repo."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        reaction_repo = FakePostReactionRepository()
        user_id = uuid.uuid4()
        _seed_reaction(reaction_repo, post.id, user_id, "like")
        sut = _make_sut(post_repo, reaction_repo)
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="like")
        assert reaction_repo.get_by_post_and_user(post.id, user_id) is None

    def test_raises_if_no_reaction_exists(self) -> None:
        """ReactionNotFoundError raised if user has not reacted."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        sut = _make_sut(post_repo)
        with pytest.raises(ReactionNotFoundError):
            sut.execute(post_id=post.id, user_id=uuid.uuid4(), reaction_type="like")

    def test_decrements_reaction_count_on_post(self) -> None:
        """After removing, the post reaction count for that type decrements."""
        post = make_post()
        post.reaction_counts["like"] = 2
        post_repo = FakeCommunityPostRepository([post])
        reaction_repo = FakePostReactionRepository()
        user_id = uuid.uuid4()
        _seed_reaction(reaction_repo, post.id, user_id, "like")
        sut = _make_sut(post_repo, reaction_repo)
        sut.execute(post_id=post.id, user_id=user_id, reaction_type="like")
        updated = post_repo.get_by_id(post.id)
        assert updated.reaction_counts.get("like", 0) == 1
