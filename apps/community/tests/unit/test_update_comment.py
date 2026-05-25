"""Tests for UpdateCommentUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.community.application.use_cases.update_comment import UpdateCommentUseCase
from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.exceptions import CommentEditWindowExpiredError, CommentNotFoundError
from apps.community.domain.repositories import IPostCommentRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_comment(
    user_id: uuid.UUID | None = None,
    created_at: datetime | None = None,
) -> PostCommentEntity:
    now = _now()
    ts = created_at or now
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        content="Original",
        is_hidden=False,
        created_at=ts,
        updated_at=ts,
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


class TestUpdateComment:
    """Unit tests for UpdateCommentUseCase."""

    def test_updates_content(self) -> None:
        """Author can update comment content within 15 minutes."""
        user_id = uuid.uuid4()
        comment = _make_comment(user_id=user_id)
        repo = FakePostCommentRepository()
        repo.create(comment)
        sut = UpdateCommentUseCase(comment_repo=repo)
        result = sut.execute(comment_id=comment.id, user_id=user_id, content="Updated!")
        assert result.content == "Updated!"

    def test_raises_if_comment_not_found(self) -> None:
        """CommentNotFoundError raised if comment does not exist."""
        repo = FakePostCommentRepository()
        sut = UpdateCommentUseCase(comment_repo=repo)
        with pytest.raises(CommentNotFoundError):
            sut.execute(comment_id=uuid.uuid4(), user_id=uuid.uuid4(), content="Hi")

    def test_raises_if_edit_window_expired(self) -> None:
        """CommentEditWindowExpiredError raised if more than 15 minutes have passed."""
        user_id = uuid.uuid4()
        old_ts = _now() - timedelta(minutes=16)
        comment = _make_comment(user_id=user_id, created_at=old_ts)
        repo = FakePostCommentRepository()
        repo.create(comment)
        sut = UpdateCommentUseCase(comment_repo=repo)
        with pytest.raises(CommentEditWindowExpiredError):
            sut.execute(comment_id=comment.id, user_id=user_id, content="Late edit")

    def test_within_15_minutes_succeeds(self) -> None:
        """Edit within 14 minutes succeeds."""
        user_id = uuid.uuid4()
        recent_ts = _now() - timedelta(minutes=14)
        comment = _make_comment(user_id=user_id, created_at=recent_ts)
        repo = FakePostCommentRepository()
        repo.create(comment)
        sut = UpdateCommentUseCase(comment_repo=repo)
        result = sut.execute(comment_id=comment.id, user_id=user_id, content="In time")
        assert result.content == "In time"
