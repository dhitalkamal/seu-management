"""Tests for ReactToCommentUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.community.application.use_cases.react_to_comment import ReactToCommentUseCase
from apps.community.domain.entities import CommentReactionEntity, PostCommentEntity
from apps.community.domain.exceptions import CommentNotFoundError
from apps.community.domain.repositories import ICommentReactionRepository, IPostCommentRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_comment(post_id: uuid.UUID | None = None) -> PostCommentEntity:
    now = _now()
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=post_id or uuid.uuid4(),
        user_id=uuid.uuid4(),
        content="A comment",
        is_hidden=False,
        created_at=now,
        updated_at=now,
    )


class FakePostCommentRepository(IPostCommentRepository):
    """In-memory comment store for testing."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, PostCommentEntity] = {}

    def create(self, comment: PostCommentEntity) -> PostCommentEntity:
        self._store[comment.id] = comment
        return comment

    def get_by_id(self, comment_id: uuid.UUID) -> PostCommentEntity:
        c = self._store.get(comment_id)
        if c is None:
            raise CommentNotFoundError("Not found.")
        return c

    def list_by_post(self, post_id: uuid.UUID) -> list[PostCommentEntity]:
        return [c for c in self._store.values() if c.post_id == post_id and c.deleted_at is None]

    def update(self, comment: PostCommentEntity) -> None:
        self._store[comment.id] = comment


class FakeCommentReactionRepository(ICommentReactionRepository):
    """In-memory comment reaction store keyed by (comment_id, user_id)."""

    def __init__(self) -> None:
        self._store: dict[tuple[uuid.UUID, uuid.UUID], CommentReactionEntity] = {}

    def upsert(self, reaction: CommentReactionEntity) -> CommentReactionEntity:
        self._store[(reaction.comment_id, reaction.user_id)] = reaction
        return reaction

    def delete(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        from apps.community.domain.exceptions import CommentReactionNotFoundError

        key = (comment_id, user_id)
        if key not in self._store:
            raise CommentReactionNotFoundError("No reaction.")
        del self._store[key]

    def get_by_comment_and_user(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> CommentReactionEntity | None:
        return self._store.get((comment_id, user_id))

    def list_by_comment(self, comment_id: uuid.UUID) -> list[CommentReactionEntity]:
        return [r for r in self._store.values() if r.comment_id == comment_id]


class TestReactToComment:
    """Unit tests for ReactToCommentUseCase."""

    def test_returns_comment_reaction_entity(self) -> None:
        """Happy path returns a CommentReactionEntity."""
        comment = _make_comment()
        comment_repo = FakePostCommentRepository()
        comment_repo.create(comment)
        reaction_repo = FakeCommentReactionRepository()
        sut = ReactToCommentUseCase(comment_repo=comment_repo, reaction_repo=reaction_repo)
        result = sut.execute(comment_id=comment.id, user_id=uuid.uuid4(), reaction_type="like")
        assert isinstance(result, CommentReactionEntity)
        assert result.reaction_type == "like"

    def test_reaction_replaces_existing(self) -> None:
        """Reacting again replaces the previous reaction for same user."""
        comment = _make_comment()
        user_id = uuid.uuid4()
        comment_repo = FakePostCommentRepository()
        comment_repo.create(comment)
        reaction_repo = FakeCommentReactionRepository()
        sut = ReactToCommentUseCase(comment_repo=comment_repo, reaction_repo=reaction_repo)
        sut.execute(comment_id=comment.id, user_id=user_id, reaction_type="like")
        sut.execute(comment_id=comment.id, user_id=user_id, reaction_type="love")
        reactions = reaction_repo.list_by_comment(comment.id)
        assert len(reactions) == 1
        assert reactions[0].reaction_type == "love"

    def test_raises_if_comment_not_found(self) -> None:
        """CommentNotFoundError raised if comment does not exist."""
        comment_repo = FakePostCommentRepository()
        reaction_repo = FakeCommentReactionRepository()
        sut = ReactToCommentUseCase(comment_repo=comment_repo, reaction_repo=reaction_repo)
        with pytest.raises(CommentNotFoundError):
            sut.execute(comment_id=uuid.uuid4(), user_id=uuid.uuid4(), reaction_type="like")
