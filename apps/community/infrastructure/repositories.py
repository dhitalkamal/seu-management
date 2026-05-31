"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from django.db import models

from apps.community.domain.entities import (
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
    HashtagEntity,
    PostCommentEntity,
    PostLikeEntity,
    PostRepostEntity,
)
from apps.community.domain.exceptions import CommunityNotFoundError, CommunityPostNotFoundError
from apps.community.domain.repositories import (
    ICommunityMemberRepository,
    ICommunityPostRepository,
    ICommunityRepository,
)
from apps.community.infrastructure.models import (
    Community,
    CommunityMember,
    CommunityPost,
    Hashtag,
    PostComment,
    PostHashtag,
    PostLike,
    PostRepost,
)


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


class DjangoPostLikeRepository:
    """PostgreSQL-backed repository for post likes."""

    def get(self, post_id: uuid.UUID, user_id: uuid.UUID) -> PostLikeEntity | None:
        """Return the like if it exists, else None."""
        try:
            return PostLike.objects.get(post_id=post_id, user_id=user_id).to_entity()
        except PostLike.DoesNotExist:
            return None

    def create(self, like: PostLikeEntity) -> None:
        """Persist a new like record."""
        PostLike.from_entity(like).save()

    def delete(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove the like record if it exists."""
        PostLike.objects.filter(post_id=post_id, user_id=user_id).delete()


class DjangoPostCommentRepository:
    """PostgreSQL-backed repository for post comments and replies."""

    def list_top_level(self, post_id: uuid.UUID) -> list[PostCommentEntity]:
        """Return all top-level comments (no parent) for a post."""
        return [c.to_entity() for c in PostComment.objects.filter(post_id=post_id, parent__isnull=True)]

    def list_replies(self, parent_id: uuid.UUID) -> list[PostCommentEntity]:
        """Return all direct replies to a comment."""
        return [c.to_entity() for c in PostComment.objects.filter(parent_id=parent_id)]

    def get_by_id(self, comment_id: uuid.UUID) -> PostCommentEntity | None:
        """Return a comment by primary key, or None if absent."""
        try:
            return PostComment.objects.get(id=comment_id).to_entity()
        except PostComment.DoesNotExist:
            return None

    def create(self, comment: PostCommentEntity) -> None:
        """Persist a new comment record."""
        PostComment.from_entity(comment).save()

    def increment_reply_count(self, comment_id: uuid.UUID) -> None:
        """Atomically increment the reply count on a parent comment."""
        PostComment.objects.filter(id=comment_id).update(reply_count=models.F("reply_count") + 1)

    def increment_post_comment_count(self, post_id: uuid.UUID) -> None:
        """Atomically increment the comment count on the parent post."""
        CommunityPost.objects.filter(id=post_id).update(comment_count=models.F("comment_count") + 1)


class DjangoPostRepostRepository:
    """PostgreSQL-backed repository for post reposts."""

    def get(self, original_post_id: uuid.UUID, user_id: uuid.UUID) -> PostRepostEntity | None:
        """Return the repost if it exists, else None."""
        try:
            return PostRepost.objects.get(original_post_id=original_post_id, user_id=user_id).to_entity()
        except PostRepost.DoesNotExist:
            return None

    def create(self, repost: PostRepostEntity) -> None:
        """Persist a new repost record."""
        PostRepost.from_entity(repost).save()


class DjangoHashtagRepository:
    """PostgreSQL-backed repository for hashtags."""

    def list_by_popularity(self) -> list[HashtagEntity]:
        """Return all hashtags ordered by post_count descending."""
        return [h.to_entity() for h in Hashtag.objects.order_by("-post_count")]

    def get_by_name(self, name: str) -> HashtagEntity | None:
        """Return a hashtag by its name (without #), or None if absent."""
        try:
            return Hashtag.objects.get(name=name).to_entity()
        except Hashtag.DoesNotExist:
            return None

    def get_or_create(self, name: str) -> HashtagEntity:
        """Return existing hashtag or create a new one, then return the entity."""
        import uuid as uuid_mod

        obj, _ = Hashtag.objects.get_or_create(
            name=name,
            defaults={"id": uuid_mod.uuid4()},
        )
        return obj.to_entity()

    def increment_post_count(self, name: str) -> None:
        """Atomically increment post_count for the named hashtag."""
        Hashtag.objects.filter(name=name).update(post_count=models.F("post_count") + 1)

    def link_post(self, post_id: uuid.UUID, hashtag_id: uuid.UUID) -> None:
        """Create the post-hashtag junction row if not already present."""
        import uuid as uuid_mod

        PostHashtag.objects.get_or_create(
            post_id=post_id,
            hashtag_id=hashtag_id,
            defaults={"id": uuid_mod.uuid4()},
        )

    def list_posts_by_hashtag(self, name: str) -> list[CommunityPostEntity]:
        """Return all posts tagged with the given hashtag name."""
        return [ph.post.to_entity() for ph in PostHashtag.objects.select_related("post").filter(hashtag__name=name)]
