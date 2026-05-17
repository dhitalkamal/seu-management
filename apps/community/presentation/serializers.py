"""DRF serializers for community request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateCommunitySerializer(serializers.Serializer):
    """Request body for creating a community."""

    name = serializers.CharField(max_length=255)
    slug = serializers.CharField(max_length=300)
    privacy = serializers.ChoiceField(choices=["public", "private", "secret"], default="public")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    organisation_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class CommunityResponseSerializer(serializers.Serializer):
    """Public shape of a community resource."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    privacy = serializers.CharField()
    member_count = serializers.IntegerField()
    organisation_id = serializers.UUIDField(allow_null=True)
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()


class CreatePostSerializer(serializers.Serializer):
    """Request body for creating a community post."""

    content = serializers.CharField()
    post_type = serializers.ChoiceField(
        choices=["text", "image", "video", "link", "poll"], default="text"
    )
    media_urls = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class CommunityPostResponseSerializer(serializers.Serializer):
    """Public shape of a community post resource."""

    id = serializers.UUIDField()
    community_id = serializers.UUIDField()
    author_id = serializers.UUIDField()
    content = serializers.CharField()
    post_type = serializers.CharField()
    status = serializers.CharField()
    like_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()
    is_pinned = serializers.BooleanField()
    media_urls = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()
