"""Tests for ListCommentsUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.application.use_cases.list_comments import ListCommentsUseCase
from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.repositories import IPostCommentRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_comment(post_id: uuid.UUID, parent_id: uuid.UUID | None = None, deleted: bool = False) -> PostCommentEntity:
    now = _now()
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=uuid.uuid4(),
        content="A comment",
        is_hidden=False,
        parent_id=parent_id,
        created_at=now,
        updated_at=now,
        deleted_at=now if deleted else None,
    )


class FakePostCommentRepository(IPostCommentRepository):
    """In-memory comment store for testing."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, PostCommentEntity] = {}

    def create(self, comment: PostCommentEntity) -> PostCommentEntity:
        self._store[comment.id] = comment
        return comment

    def get_by_id(self, comment_id: uuid.UUID) -> PostCommentEntity:
        from apps.community.domain.exceptions import CommentNotFoundError

        c = self._store.get(comment_id)
        if c is None:
            raise CommentNotFoundError("Not found.")
        return c

    def list_by_post(self, post_id: uuid.UUID) -> list[PostCommentEntity]:
        return [c for c in self._store.values() if c.post_id == post_id and c.deleted_at is None]

    def update(self, comment: PostCommentEntity) -> None:
        self._store[comment.id] = comment


class TestListComments:
    """Unit tests for ListCommentsUseCase."""

    def test_returns_empty_list_when_no_comments(self) -> None:
        """Returns empty list for a post with no comments."""
        repo = FakePostCommentRepository()
        sut = ListCommentsUseCase(comment_repo=repo)
        result = sut.execute(post_id=uuid.uuid4())
        assert result == []

    def test_returns_comments_for_post(self) -> None:
        """Returns all non-deleted comments for the given post."""
        post_id = uuid.uuid4()
        repo = FakePostCommentRepository()
        repo.create(_make_comment(post_id))
        repo.create(_make_comment(post_id))
        sut = ListCommentsUseCase(comment_repo=repo)
        result = sut.execute(post_id=post_id)
        assert len(result) == 2

    def test_does_not_return_deleted_comments(self) -> None:
        """Soft-deleted comments are excluded."""
        post_id = uuid.uuid4()
        repo = FakePostCommentRepository()
        repo.create(_make_comment(post_id, deleted=True))
        repo.create(_make_comment(post_id))
        sut = ListCommentsUseCase(comment_repo=repo)
        result = sut.execute(post_id=post_id)
        assert len(result) == 1

    def test_does_not_return_other_post_comments(self) -> None:
        """Comments from other posts are not included."""
        post_id = uuid.uuid4()
        other_post_id = uuid.uuid4()
        repo = FakePostCommentRepository()
        repo.create(_make_comment(post_id))
        repo.create(_make_comment(other_post_id))
        sut = ListCommentsUseCase(comment_repo=repo)
        result = sut.execute(post_id=post_id)
        assert len(result) == 1
        assert result[0].post_id == post_id
