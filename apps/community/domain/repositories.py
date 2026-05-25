"""Abstract repository interfaces for the community module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.community.domain.entities import (
    CommentReactionEntity,
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
    PostCommentEntity,
    PostReactionEntity,
)


class ICommunityRepository(ABC):
    """Persistence interface for community aggregates."""

    @abstractmethod
    def list_all(self) -> list[CommunityEntity]:
        """Return all non-deleted communities."""

    @abstractmethod
    def get_by_id(self, community_id: uuid.UUID) -> CommunityEntity:
        """Return a community by primary key, raising CommunityNotFoundError if absent."""

    @abstractmethod
    def create(self, community: CommunityEntity) -> None:
        """Persist a new community."""

    @abstractmethod
    def update(self, community: CommunityEntity) -> None:
        """Persist changes to an existing community."""

    @abstractmethod
    def slug_exists(self, slug: str) -> bool:
        """Return True if the slug is already in use."""


class ICommunityMemberRepository(ABC):
    """Persistence interface for community memberships."""

    @abstractmethod
    def get_membership(self, community_id: uuid.UUID, user_id: uuid.UUID) -> CommunityMemberEntity | None:
        """Return the membership if it exists, else None."""

    @abstractmethod
    def create(self, member: CommunityMemberEntity) -> None:
        """Persist a new membership record."""

    @abstractmethod
    def delete(self, community_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove a membership record."""

    @abstractmethod
    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityMemberEntity]:
        """Return all members of a community."""


class ICommunityPostRepository(ABC):
    """Persistence interface for community posts."""

    @abstractmethod
    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityPostEntity]:
        """Return all published posts for a community."""

    @abstractmethod
    def get_by_id(self, post_id: uuid.UUID) -> CommunityPostEntity:
        """Return a post by primary key, raising CommunityPostNotFoundError if absent."""

    @abstractmethod
    def create(self, post: CommunityPostEntity) -> None:
        """Persist a new post."""

    @abstractmethod
    def update(self, post: CommunityPostEntity) -> None:
        """Persist changes to an existing post."""


class IPostReactionRepository(ABC):
    """Persistence interface for post reactions."""

    @abstractmethod
    def upsert(self, reaction: PostReactionEntity) -> PostReactionEntity:
        """Insert or replace the reaction for (post_id, user_id)."""

    @abstractmethod
    def delete(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove the reaction, raising ReactionNotFoundError if absent."""

    @abstractmethod
    def get_by_post_and_user(self, post_id: uuid.UUID, user_id: uuid.UUID) -> PostReactionEntity | None:
        """Return the reaction if it exists, else None."""

    @abstractmethod
    def list_by_post(self, post_id: uuid.UUID) -> list[PostReactionEntity]:
        """Return all reactions for a given post."""


class IPostCommentRepository(ABC):
    """Persistence interface for post comments."""

    @abstractmethod
    def create(self, comment: PostCommentEntity) -> PostCommentEntity:
        """Persist a new comment and return it."""

    @abstractmethod
    def get_by_id(self, comment_id: uuid.UUID) -> PostCommentEntity:
        """Return a comment by primary key, raising CommentNotFoundError if absent."""

    @abstractmethod
    def list_by_post(self, post_id: uuid.UUID) -> list[PostCommentEntity]:
        """Return all non-deleted comments for a post."""

    @abstractmethod
    def update(self, comment: PostCommentEntity) -> None:
        """Persist changes to an existing comment."""


class ICommentReactionRepository(ABC):
    """Persistence interface for comment reactions."""

    @abstractmethod
    def upsert(self, reaction: CommentReactionEntity) -> CommentReactionEntity:
        """Insert or replace the reaction for (comment_id, user_id)."""

    @abstractmethod
    def delete(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove the reaction, raising CommentReactionNotFoundError if absent."""

    @abstractmethod
    def get_by_comment_and_user(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> CommentReactionEntity | None:
        """Return the reaction if it exists, else None."""

    @abstractmethod
    def list_by_comment(self, comment_id: uuid.UUID) -> list[CommentReactionEntity]:
        """Return all reactions for a given comment."""
