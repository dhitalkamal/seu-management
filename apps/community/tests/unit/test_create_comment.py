"""Tests for CreateCommentUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.community.application.use_cases.create_comment import CreateCommentUseCase
from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.exceptions import CommunityPostNotFoundError
from apps.community.domain.repositories import IPostCommentRepository
from apps.community.tests.unit.fakes import FakeCommunityPostRepository, make_post


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_comment(post_id: uuid.UUID, user_id: uuid.UUID | None = None, **kwargs: object) -> PostCommentEntity:
    now = _now()
    return PostCommentEntity(
        id=uuid.uuid4(),
        post_id=post_id,
        user_id=user_id or uuid.uuid4(),
        content="Test comment",
        is_hidden=False,
        created_at=now,
        updated_at=now,
        **kwargs,  # type: ignore[arg-type]
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


class TestCreateComment:
    """Unit tests for CreateCommentUseCase."""

    def test_returns_comment_entity(self) -> None:
        """Happy path returns a PostCommentEntity."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        comment_repo = FakePostCommentRepository()
        sut = CreateCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        result = sut.execute(post_id=post.id, user_id=uuid.uuid4(), content="Hello!")
        assert isinstance(result, PostCommentEntity)
        assert result.content == "Hello!"

    def test_comment_linked_to_post(self) -> None:
        """Created comment has the correct post_id."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        comment_repo = FakePostCommentRepository()
        user_id = uuid.uuid4()
        sut = CreateCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        result = sut.execute(post_id=post.id, user_id=user_id, content="Hello!")
        assert result.post_id == post.id
        assert result.user_id == user_id

    def test_reply_has_parent_id(self) -> None:
        """Reply comment stores the parent comment id."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        comment_repo = FakePostCommentRepository()
        parent = _make_comment(post.id)
        comment_repo.create(parent)
        sut = CreateCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        result = sut.execute(post_id=post.id, user_id=uuid.uuid4(), content="Reply!", parent_id=parent.id)
        assert result.parent_id == parent.id

    def test_raises_if_post_not_found(self) -> None:
        """CommunityPostNotFoundError raised if post does not exist."""
        post_repo = FakeCommunityPostRepository()
        comment_repo = FakePostCommentRepository()
        sut = CreateCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        with pytest.raises(CommunityPostNotFoundError):
            sut.execute(post_id=uuid.uuid4(), user_id=uuid.uuid4(), content="Hey!")

    def test_post_comment_count_incremented(self) -> None:
        """Post comment_count increases by 1 after a comment is created."""
        post = make_post()
        post_repo = FakeCommunityPostRepository([post])
        comment_repo = FakePostCommentRepository()
        sut = CreateCommentUseCase(post_repo=post_repo, comment_repo=comment_repo)
        sut.execute(post_id=post.id, user_id=uuid.uuid4(), content="Hi!")
        updated = post_repo.get_by_id(post.id)
        assert updated.comment_count == 1
