"""DRF serializers for marketing request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateCampaignSerializer(serializers.Serializer):
    """Request body for creating a campaign."""

    name = serializers.CharField(max_length=255)
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    segment_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class CampaignResponseSerializer(serializers.Serializer):
    """Public shape of a campaign resource."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    subject = serializers.CharField()
    status = serializers.CharField()
    segment_id = serializers.UUIDField(allow_null=True)
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    sent_at = serializers.DateTimeField(allow_null=True)


class CreateSegmentSerializer(serializers.Serializer):
    """Request body for creating an audience segment."""

    name = serializers.CharField(max_length=255)
    filters = serializers.JSONField(default=dict)


class SegmentResponseSerializer(serializers.Serializer):
    """Public shape of an audience segment resource."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    filters = serializers.JSONField()
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
