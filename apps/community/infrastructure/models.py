"""Django ORM models for the community domain. Maps to the community schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.community.domain.entities import (
    CommentReactionEntity,
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
    PostCommentEntity,
    PostReactionEntity,
)


class Community(models.Model):
    """A community group optionally linked to an organisation."""

    class Privacy(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        SECRET = "secret", "Secret"

    class Meta:
        db_table = '"community"."community"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation_id = models.UUIDField(null=True, blank=True)
    created_by = models.UUIDField()
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=20, choices=Privacy.choices, default=Privacy.PUBLIC)
    member_count = models.IntegerField(default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> CommunityEntity:
        """Map this ORM row to a pure-Python CommunityEntity."""
        return CommunityEntity(
            id=self.id,
            created_by=self.created_by,
            name=self.name,
            slug=self.slug,
            privacy=self.privacy,
            member_count=self.member_count,
            created_at=self.created_at,
            organisation_id=self.organisation_id,
            description=self.description,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: CommunityEntity) -> "Community":
        """Build an unsaved ORM instance from a CommunityEntity."""
        return cls(
            id=entity.id,
            organisation_id=entity.organisation_id,
            created_by=entity.created_by,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            privacy=entity.privacy,
            member_count=entity.member_count,
            deleted_at=entity.deleted_at,
        )


class CommunityMember(models.Model):
    """A membership record linking a user to a community."""

    class Meta:
        db_table = '"community"."community_member"'
        constraints = [models.UniqueConstraint(fields=["community", "user_id"], name="unique_community_member")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="members")
    user_id = models.UUIDField()
    joined_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> CommunityMemberEntity:
        """Map this ORM row to a pure-Python CommunityMemberEntity."""
        return CommunityMemberEntity(
            id=self.id,
            community_id=self.community_id,
            user_id=self.user_id,
            joined_at=self.joined_at,
        )

    @classmethod
    def from_entity(cls, entity: CommunityMemberEntity) -> "CommunityMember":
        """Build an unsaved ORM instance from a CommunityMemberEntity."""
        return cls(
            id=entity.id,
            community_id=entity.community_id,
            user_id=entity.user_id,
        )


class CommunityPost(models.Model):
    """A post authored inside a community."""

    class PostType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        LINK = "link", "Link"
        POLL = "poll", "Poll"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        REMOVED = "removed", "Removed"

    class Meta:
        db_table = '"community"."community_post"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    author_id = models.UUIDField()
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.TEXT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    media_urls = models.JSONField(default=list)
    reaction_counts = models.JSONField(default=dict)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> CommunityPostEntity:
        """Map this ORM row to a pure-Python CommunityPostEntity."""
        return CommunityPostEntity(
            id=self.id,
            community_id=self.community_id,
            author_id=self.author_id,
            content=self.content,
            post_type=self.post_type,
            status=self.status,
            like_count=self.like_count,
            comment_count=self.comment_count,
            report_count=self.report_count,
            is_pinned=self.is_pinned,
            created_at=self.created_at,
            media_urls=self.media_urls or [],
            reaction_counts=self.reaction_counts or {},
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: CommunityPostEntity) -> "CommunityPost":
        """Build an unsaved ORM instance from a CommunityPostEntity."""
        return cls(
            id=entity.id,
            community_id=entity.community_id,
            author_id=entity.author_id,
            content=entity.content,
            post_type=entity.post_type,
            status=entity.status,
            media_urls=entity.media_urls,
            reaction_counts=entity.reaction_counts,
            like_count=entity.like_count,
            comment_count=entity.comment_count,
            report_count=entity.report_count,
            is_pinned=entity.is_pinned,
            deleted_at=entity.deleted_at,
        )


class CommunityPostReaction(models.Model):
    """A single user reaction on a community post."""

    class ReactionType(models.TextChoices):
        LIKE = "like", "Like"
        LOVE = "love", "Love"
        FIRE = "fire", "Fire"
        LAUGH = "laugh", "Laugh"
        SAD = "sad", "Sad"
        ANGRY = "angry", "Angry"

    class Meta:
        db_table = '"community"."community_post_reaction"'
        constraints = [models.UniqueConstraint(fields=["post", "user_id"], name="unique_post_reaction_per_user")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="reactions")
    user_id = models.UUIDField()
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> PostReactionEntity:
        """Map this ORM row to a pure-Python PostReactionEntity."""
        return PostReactionEntity(
            id=self.id,
            post_id=self.post_id,
            user_id=self.user_id,
            reaction_type=self.reaction_type,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: PostReactionEntity) -> "CommunityPostReaction":
        """Build an unsaved ORM instance from a PostReactionEntity."""
        return cls(
            id=entity.id,
            post_id=entity.post_id,
            user_id=entity.user_id,
            reaction_type=entity.reaction_type,
        )


class PostComment(models.Model):
    """A comment on a community post, optionally nested under a parent comment."""

    class Meta:
        db_table = '"community"."post_comment"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
    user_id = models.UUIDField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.TextField()
    is_hidden = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> PostCommentEntity:
        """Map this ORM row to a pure-Python PostCommentEntity."""
        return PostCommentEntity(
            id=self.id,
            post_id=self.post_id,
            user_id=self.user_id,
            content=self.content,
            is_hidden=self.is_hidden,
            parent_id=self.parent_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: PostCommentEntity) -> "PostComment":
        """Build an unsaved ORM instance from a PostCommentEntity."""
        return cls(
            id=entity.id,
            post_id=entity.post_id,
            user_id=entity.user_id,
            parent_id=entity.parent_id,
            content=entity.content,
            is_hidden=entity.is_hidden,
            deleted_at=entity.deleted_at,
        )


class CommentReaction(models.Model):
    """A single user reaction on a comment."""

    class ReactionType(models.TextChoices):
        LIKE = "like", "Like"
        LOVE = "love", "Love"
        FIRE = "fire", "Fire"
        LAUGH = "laugh", "Laugh"
        SAD = "sad", "Sad"
        ANGRY = "angry", "Angry"

    class Meta:
        db_table = '"community"."comment_reaction"'
        constraints = [models.UniqueConstraint(fields=["comment", "user_id"], name="unique_comment_reaction_per_user")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name="reactions")
    user_id = models.UUIDField()
    reaction_type = models.CharField(max_length=10, choices=ReactionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> CommentReactionEntity:
        """Map this ORM row to a pure-Python CommentReactionEntity."""
        return CommentReactionEntity(
            id=self.id,
            comment_id=self.comment_id,
            user_id=self.user_id,
            reaction_type=self.reaction_type,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: CommentReactionEntity) -> "CommentReaction":
        """Build an unsaved ORM instance from a CommentReactionEntity."""
        return cls(
            id=entity.id,
            comment_id=entity.comment_id,
            user_id=entity.user_id,
            reaction_type=entity.reaction_type,
        )
