"""Django ORM models for the community domain. Maps to the community schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.community.domain.entities import (
    ActivityFeedEntry,
    CommunityEntity,
    CommunityMemberEntity,
    CommunityPostEntity,
    EventWallEntity,
    HashtagEntity,
    PollEntity,
    PostCommentEntity,
    PostLikeEntity,
    PostRepostEntity,
)


class Community(models.Model):
    """A community group optionally linked to an organization."""

    class Privacy(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        SECRET = "secret", "Secret"

    class Meta:
        db_table = "community_community"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True)
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
            organization_id=self.organization_id,
            description=self.description,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: CommunityEntity) -> "Community":
        """Build an unsaved ORM instance from a CommunityEntity."""
        return cls(
            id=entity.id,
            organization_id=entity.organization_id,
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
        db_table = "community_community_member"
        constraints = [models.UniqueConstraint(fields=["community", "user_id"], name="unique_community_member")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="members")
    user_id = models.UUIDField()
    # avatar url stored at join time for display in the directory
    avatar_url = models.CharField(max_length=2048, blank=True, default="")
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
        db_table = "community_community_post"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    author_id = models.UUIDField()
    author_name = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=PostType.choices, default=PostType.TEXT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    media_urls = models.JSONField(default=list)
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
            author_name=self.author_name,
            content=self.content,
            post_type=self.post_type,
            status=self.status,
            like_count=self.like_count,
            comment_count=self.comment_count,
            report_count=self.report_count,
            is_pinned=self.is_pinned,
            created_at=self.created_at,
            media_urls=self.media_urls or [],
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: CommunityPostEntity) -> "CommunityPost":
        """Build an unsaved ORM instance from a CommunityPostEntity."""
        return cls(
            id=entity.id,
            community_id=entity.community_id,
            author_id=entity.author_id,
            author_name=entity.author_name,
            content=entity.content,
            post_type=entity.post_type,
            status=entity.status,
            media_urls=entity.media_urls,
            like_count=entity.like_count,
            comment_count=entity.comment_count,
            report_count=entity.report_count,
            is_pinned=entity.is_pinned,
            deleted_at=entity.deleted_at,
        )


class PostLike(models.Model):
    """A like on a community post, one per user per post."""

    class Meta:
        db_table = "community_post_like"
        constraints = [models.UniqueConstraint(fields=["post", "user_id"], name="unique_post_like")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="likes")
    user_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> PostLikeEntity:
        """Map this ORM row to a pure-Python PostLikeEntity."""
        return PostLikeEntity(
            id=self.id,
            post_id=self.post_id,
            user_id=self.user_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: PostLikeEntity) -> "PostLike":
        """Build an unsaved ORM instance from a PostLikeEntity."""
        return cls(
            id=entity.id,
            post_id=entity.post_id,
            user_id=entity.user_id,
        )


class PostComment(models.Model):
    """A comment or reply on a community post."""

    class Meta:
        db_table = "community_post_comment"
        ordering = ["created_at"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
    author_id = models.UUIDField()
    author_name = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField()
    # null = top-level; non-null = reply
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> PostCommentEntity:
        """Map this ORM row to a pure-Python PostCommentEntity."""
        return PostCommentEntity(
            id=self.id,
            post_id=self.post_id,
            author_id=self.author_id,
            author_name=self.author_name,
            content=self.content,
            parent_id=self.parent_id,
            like_count=self.like_count,
            reply_count=self.reply_count,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: PostCommentEntity) -> "PostComment":
        """Build an unsaved ORM instance from a PostCommentEntity."""
        return cls(
            id=entity.id,
            post_id=entity.post_id,
            author_id=entity.author_id,
            author_name=entity.author_name,
            content=entity.content,
            parent_id=entity.parent_id,
            like_count=entity.like_count,
            reply_count=entity.reply_count,
        )


class PostRepost(models.Model):
    """A repost of an original community post into another community."""

    class Meta:
        db_table = "community_post_repost"
        constraints = [models.UniqueConstraint(fields=["original_post", "user_id"], name="unique_post_repost")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    original_post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="reposts")
    user_id = models.UUIDField()
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="reposts")
    caption = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> PostRepostEntity:
        """Map this ORM row to a pure-Python PostRepostEntity."""
        return PostRepostEntity(
            id=self.id,
            original_post_id=self.original_post_id,
            user_id=self.user_id,
            community_id=self.community_id,
            caption=self.caption,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: PostRepostEntity) -> "PostRepost":
        """Build an unsaved ORM instance from a PostRepostEntity."""
        return cls(
            id=entity.id,
            original_post_id=entity.original_post_id,
            user_id=entity.user_id,
            community_id=entity.community_id,
            caption=entity.caption,
        )


class Hashtag(models.Model):
    """A unique hashtag extracted from post content."""

    class Meta:
        db_table = "community_hashtag"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # stored without the leading #
    name = models.CharField(max_length=100, unique=True)
    post_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> HashtagEntity:
        """Map this ORM row to a pure-Python HashtagEntity."""
        return HashtagEntity(
            id=self.id,
            name=self.name,
            post_count=self.post_count,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: HashtagEntity) -> "Hashtag":
        """Build an unsaved ORM instance from a HashtagEntity."""
        return cls(
            id=entity.id,
            name=entity.name,
            post_count=entity.post_count,
        )


class PostHashtag(models.Model):
    """Junction table linking posts to their hashtags."""

    class Meta:
        db_table = "community_post_hashtag"
        constraints = [models.UniqueConstraint(fields=["post", "hashtag"], name="unique_post_hashtag")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="hashtags")
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name="posts")


class Poll(models.Model):
    """A question with multiple options that community members can vote on."""

    class Meta:
        db_table = "community_poll"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="polls")
    author_id = models.UUIDField()
    author_name = models.CharField(max_length=255, blank=True, default="")
    question = models.TextField()
    # stored as [{"text": "Option A", "votes": 0}, ...]
    options = models.JSONField(default=list)
    total_votes = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> PollEntity:
        """Map this ORM row to a pure-Python PollEntity."""
        return PollEntity(
            id=self.id,
            community_id=self.community_id,
            author_id=self.author_id,
            author_name=self.author_name,
            question=self.question,
            options=self.options or [],
            total_votes=self.total_votes,
            expires_at=self.expires_at,
            created_at=self.created_at,
        )


class PollVote(models.Model):
    """One vote per user per poll, recording which option was chosen."""

    class Meta:
        db_table = "community_poll_vote"
        constraints = [models.UniqueConstraint(fields=["poll", "user_id"], name="unique_poll_vote")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    user_id = models.UUIDField()
    option_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ActivityFeed(models.Model):
    """A chronological log of notable actions taken by members in a community."""

    class Meta:
        db_table = "community_activity_feed"
        ordering = ["-created_at"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="activities")
    user_id = models.UUIDField()
    user_name = models.CharField(max_length=255, default="")
    user_avatar = models.URLField(blank=True, default="")
    # one of: registered, posted, joined, commented, liked, voted
    activity_type = models.CharField(max_length=50)
    target_title = models.CharField(max_length=500, default="")
    target_id = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> ActivityFeedEntry:
        """Map this ORM row to a pure-Python ActivityFeedEntry."""
        return ActivityFeedEntry(
            id=self.id,
            community_id=self.community_id,
            user_id=self.user_id,
            user_name=self.user_name,
            user_avatar=self.user_avatar,
            activity_type=self.activity_type,
            target_title=self.target_title,
            target_id=self.target_id,
            created_at=self.created_at,
        )


class EventWall(models.Model):
    """A named wall of posts tied to a specific event inside a community."""

    class Meta:
        db_table = "community_event_wall"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="event_walls")
    event_id = models.UUIDField()
    event_title = models.CharField(max_length=500)
    event_date = models.DateTimeField()
    post_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> EventWallEntity:
        """Map this ORM row to a pure-Python EventWallEntity."""
        return EventWallEntity(
            id=self.id,
            community_id=self.community_id,
            event_id=self.event_id,
            event_title=self.event_title,
            event_date=self.event_date,
            post_count=self.post_count,
            created_at=self.created_at,
        )
