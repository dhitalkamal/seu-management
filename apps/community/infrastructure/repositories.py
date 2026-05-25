"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.community.domain.entities import (
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
)
from apps.community.domain.exceptions import CommunityNotFoundError, CommunityPostNotFoundError
from apps.community.domain.repositories import (
    ICommunityMemberRepository,
    ICommunityPostRepository,
    ICommunityRepository,
)
from apps.community.infrastructure.models import Community, CommunityMember, CommunityPost


class DjangoCommunityRepository(ICommunityRepository):
    """PostgreSQL-backed community repository."""

    def list_all(self) -> list[CommunityEntity]:
        """Return all non-deleted communities."""
        return [c.to_entity() for c in Community.objects.filter(deleted_at__isnull=True)]

    def get_by_id(self, community_id: uuid.UUID) -> CommunityEntity:
        """Raise CommunityNotFoundError if the community is not found."""
        try:
            return Community.objects.get(id=community_id, deleted_at__isnull=True).to_entity()
        except Community.DoesNotExist:
            raise CommunityNotFoundError(f"Community {community_id} not found.")

    def create(self, community: CommunityEntity) -> None:
        """Persist a new community."""
        Community.from_entity(community).save()

    def update(self, community: CommunityEntity) -> None:
        """Persist changes to an existing community."""
        Community.objects.filter(id=community.id).update(
            name=community.name,
            description=community.description,
            privacy=community.privacy,
            member_count=community.member_count,
            deleted_at=community.deleted_at,
        )

    def slug_exists(self, slug: str) -> bool:
        """Return True if the slug is already in use."""
        return Community.objects.filter(slug=slug).exists()


class DjangoCommunityMemberRepository(ICommunityMemberRepository):
    """PostgreSQL-backed community membership repository."""

    def get_membership(self, community_id: uuid.UUID, user_id: uuid.UUID) -> CommunityMemberEntity | None:
        """Return the membership if it exists, else None."""
        try:
            return CommunityMember.objects.get(community_id=community_id, user_id=user_id).to_entity()
        except CommunityMember.DoesNotExist:
            return None

    def create(self, member: CommunityMemberEntity) -> None:
        """Persist a new membership record."""
        CommunityMember.from_entity(member).save()

    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityMemberEntity]:
        """Return all members of a community."""
        return [m.to_entity() for m in CommunityMember.objects.filter(community_id=community_id)]


class DjangoCommunityPostRepository(ICommunityPostRepository):
    """PostgreSQL-backed community post repository."""

    def list_by_community(self, community_id: uuid.UUID) -> list[CommunityPostEntity]:
        """Return all published posts for a community."""
        return [p.to_entity() for p in CommunityPost.objects.filter(community_id=community_id, status="published")]

    def get_by_id(self, post_id: uuid.UUID) -> CommunityPostEntity:
        """Raise CommunityPostNotFoundError if not found."""
        try:
            return CommunityPost.objects.get(id=post_id).to_entity()
        except CommunityPost.DoesNotExist:
            raise CommunityPostNotFoundError(f"Post {post_id} not found.")

    def create(self, post: CommunityPostEntity) -> None:
        """Persist a new post."""
        CommunityPost.from_entity(post).save()

    def update(self, post: CommunityPostEntity) -> None:
        """Persist changes to an existing post."""
        CommunityPost.objects.filter(id=post.id).update(
            content=post.content,
            status=post.status,
            like_count=post.like_count,
            comment_count=post.comment_count,
            report_count=post.report_count,
            is_pinned=post.is_pinned,
            deleted_at=post.deleted_at,
        )
