"""DRF serializers for community request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateCommunitySerializer(serializers.Serializer):
    """Request body for creating a community."""

    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=300)
    privacy = serializers.ChoiceField(choices=["public", "private", "secret"], default="public")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    organization_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class CommunityResponseSerializer(serializers.Serializer):
    """Public shape of a community resource."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    privacy = serializers.CharField()
    member_count = serializers.IntegerField()
    organization_id = serializers.UUIDField(allow_null=True)
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    # computed per-request: True if the calling user is a member
    is_member = serializers.BooleanField(default=False)


class CreatePostSerializer(serializers.Serializer):
    """Request body for creating a community post."""

    content = serializers.CharField()
    post_type = serializers.ChoiceField(choices=["text", "image", "video", "link", "poll"], default="text")
    media_urls = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class CommunityPostResponseSerializer(serializers.Serializer):
    """Public shape of a community post resource."""

    id = serializers.UUIDField()
    community_id = serializers.UUIDField()
    author_id = serializers.UUIDField()
    author_name = serializers.CharField()
    content = serializers.CharField()
    post_type = serializers.CharField()
    status = serializers.CharField()
    like_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()
    is_pinned = serializers.BooleanField()
    media_urls = serializers.ListField(child=serializers.CharField())
    is_liked = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField()


class PostLikeResponseSerializer(serializers.Serializer):
    """Public shape of a post like record."""

    id = serializers.UUIDField()
    post_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    created_at = serializers.DateTimeField()


class PostCommentSerializer(serializers.Serializer):
    """Request body for creating a comment or reply."""

    content = serializers.CharField()
    # omit parent_id for top-level comments; provide it to create a reply
    parent_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class PostCommentResponseSerializer(serializers.Serializer):
    """Public shape of a comment, including any nested replies."""

    id = serializers.UUIDField()
    post_id = serializers.UUIDField()
    author_id = serializers.UUIDField()
    author_name = serializers.CharField()
    content = serializers.CharField()
    parent_id = serializers.UUIDField(allow_null=True)
    like_count = serializers.IntegerField()
    reply_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    # nested replies are included only on top-level comments
    replies = serializers.ListField(child=serializers.DictField(), default=list)


class PostRepostSerializer(serializers.Serializer):
    """Request body for reposting a post into another community."""

    community_id = serializers.UUIDField()
    caption = serializers.CharField(required=False, allow_blank=True, default="")


class PostRepostResponseSerializer(serializers.Serializer):
    """Public shape of a repost record."""

    id = serializers.UUIDField()
    original_post_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    community_id = serializers.UUIDField()
    caption = serializers.CharField()
    created_at = serializers.DateTimeField()


class HashtagResponseSerializer(serializers.Serializer):
    """Public shape of a hashtag."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    post_count = serializers.IntegerField()


class PollSerializer(serializers.Serializer):
    """Request body for creating a poll."""

    question = serializers.CharField()
    # list of option strings; converted to [{text, votes: 0}] in the view
    options = serializers.ListField(child=serializers.CharField(), min_length=2)
    expires_at = serializers.DateTimeField(required=False, allow_null=True, default=None)


class PollResponseSerializer(serializers.Serializer):
    """Public shape of a poll, including whether the calling user has voted."""

    id = serializers.UUIDField()
    community_id = serializers.UUIDField()
    author_id = serializers.UUIDField()
    author_name = serializers.CharField()
    question = serializers.CharField()
    options = serializers.ListField(child=serializers.DictField())
    total_votes = serializers.IntegerField()
    expires_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    # null when the user has not voted; integer index otherwise
    user_voted_index = serializers.IntegerField(allow_null=True, default=None)


class PollVoteSerializer(serializers.Serializer):
    """Request body for casting a vote on a poll."""

    option_index = serializers.IntegerField(min_value=0)


class ActivityFeedResponseSerializer(serializers.Serializer):
    """Public shape of a single activity feed entry."""

    id = serializers.UUIDField()
    user_name = serializers.CharField()
    user_avatar = serializers.CharField()
    activity_type = serializers.CharField()
    target_title = serializers.CharField()
    target_id = serializers.CharField()
    created_at = serializers.DateTimeField()


class EventWallResponseSerializer(serializers.Serializer):
    """Public shape of an event wall record."""

    id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    event_title = serializers.CharField()
    event_date = serializers.DateTimeField()
    post_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class EventWallCreateSerializer(serializers.Serializer):
    """Request body for creating an event wall."""

    event_id = serializers.UUIDField()
    event_title = serializers.CharField(max_length=500)
    event_date = serializers.DateTimeField()


class MemberDirectorySerializer(serializers.Serializer):
    """Public shape of a member directory entry with engagement stats and badge."""

    user_id = serializers.UUIDField()
    user_name = serializers.CharField()
    user_avatar = serializers.CharField()
    badge_type = serializers.CharField()
    events_attended = serializers.IntegerField()
    posts_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    joined_at = serializers.DateTimeField()
