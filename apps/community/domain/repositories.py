"""Abstract repository interfaces for the community module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.community.domain.entities import (
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
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
