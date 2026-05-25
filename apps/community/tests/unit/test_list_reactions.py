"""Tests for ListReactionsUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.application.use_cases.list_reactions import ListReactionsUseCase
from apps.community.domain.entities import PostReactionEntity
from apps.community.domain.repositories import IPostReactionRepository


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


class TestListReactions:
    """Unit tests for ListReactionsUseCase."""

    def test_returns_empty_list_when_no_reactions(self) -> None:
        """Returns empty list if no reactions exist for the post."""
        repo = FakePostReactionRepository()
        sut = ListReactionsUseCase(reaction_repo=repo)
        result = sut.execute(post_id=uuid.uuid4())
        assert result == []

    def test_returns_reactions_for_post(self) -> None:
        """Returns all reactions for the given post."""
        post_id = uuid.uuid4()
        repo = FakePostReactionRepository()
        repo.upsert(_make_reaction(post_id, uuid.uuid4(), "like"))
        repo.upsert(_make_reaction(post_id, uuid.uuid4(), "love"))
        sut = ListReactionsUseCase(reaction_repo=repo)
        result = sut.execute(post_id=post_id)
        assert len(result) == 2

    def test_does_not_return_reactions_for_other_post(self) -> None:
        """Reactions from other posts are not included."""
        post_id = uuid.uuid4()
        other_post_id = uuid.uuid4()
        repo = FakePostReactionRepository()
        repo.upsert(_make_reaction(post_id, uuid.uuid4(), "fire"))
        repo.upsert(_make_reaction(other_post_id, uuid.uuid4(), "like"))
        sut = ListReactionsUseCase(reaction_repo=repo)
        result = sut.execute(post_id=post_id)
        assert len(result) == 1
        assert result[0].post_id == post_id
