"""Tests for DeleteCommentUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.community.application.use_cases.delete_comment import DeleteCommentUseCase
from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.exceptions import CommentNotFoundError
from apps.community.domain.repositories import IPostCommentRepository
from apps.community.tests.unit.fakes import FakeCommunityPostRepository, make_post


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_comment(post_id: uuid.UUID, user_id: uuid.UUID | None = None) -> PostCommentEntity:
    now = _now()
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id or uuid.uuid4(),
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


class TestDeleteComment:
    """Unit tests for DeleteCommentUseCase."""

    def test_soft_deletes_comment(self) -> None:
        """Author can soft-delete their comment (deleted_at is set)."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        comment = _make_comment(post.id, user_id=user_id)
        comment_repo = FakePostCommentRepository()
        comment_repo.create(comment)
        sut = DeleteCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        sut.execute(comment_id=comment.id, user_id=user_id)
        deleted = comment_repo.get_by_id(comment.id)
        assert deleted.deleted_at is not None

    def test_raises_if_comment_not_found(self) -> None:
        """CommentNotFoundError raised if comment does not exist."""
        post_repo = FakeCommunityPostRepository()
        comment_repo = FakePostCommentRepository()
        sut = DeleteCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        with pytest.raises(CommentNotFoundError):
            sut.execute(comment_id=uuid.uuid4(), user_id=uuid.uuid4())

    def test_deleted_comment_excluded_from_list(self) -> None:
        """Soft-deleted comment no longer appears in list_by_post."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        comment = _make_comment(post.id, user_id=user_id)
        comment_repo = FakePostCommentRepository()
        comment_repo.create(comment)
        sut = DeleteCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        sut.execute(comment_id=comment.id, user_id=user_id)
        result = comment_repo.list_by_post(post.id)
        assert result == []

    def test_post_comment_count_decremented(self) -> None:
        """Post comment_count decreases by 1 after deletion."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        user_id = uuid.uuid4()
        comment = _make_comment(post.id, user_id=user_id)
        comment_repo = FakePostCommentRepository()
        comment_repo.create(comment)
        # manually bump count so deletion can decrement it
        post.comment_count = 1
        post_repo.update(post)
        sut = DeleteCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        sut.execute(comment_id=comment.id, user_id=user_id)
        updated = post_repo.get_by_id(post.id)
        assert updated.comment_count == 0
