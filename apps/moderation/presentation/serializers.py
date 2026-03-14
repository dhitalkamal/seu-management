"""DRF serializers for moderation request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class ModerationCaseSerializer(serializers.Serializer):
    """Public shape of a moderation case resource."""

    id = serializers.UUIDField()
    content_type = serializers.CharField()
    content_id = serializers.UUIDField()
    content_title = serializers.CharField()
    reporter_id = serializers.UUIDField(allow_null=True)
    organisation_id = serializers.UUIDField(allow_null=True)
    reason = serializers.CharField()
    status = serializers.CharField()
    reviewer_id = serializers.UUIDField(allow_null=True)
    reviewer_notes = serializers.CharField()
    created_at = serializers.DateTimeField()
    resolved_at = serializers.DateTimeField(allow_null=True)


class CreateModerationCaseSerializer(serializers.Serializer):
    """Input payload for reporting content for moderation review."""

    content_type = serializers.ChoiceField(choices=["event", "post", "comment"])
    content_id = serializers.UUIDField()
    content_title = serializers.CharField(max_length=500)
    reason = serializers.CharField()
    organisation_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class UpdateCaseStatusSerializer(serializers.Serializer):
    """Input payload for updating the status of a moderation case."""

    status = serializers.ChoiceField(choices=["under_review", "dismissed", "warned", "taken_down"])
    reviewer_notes = serializers.CharField(required=False, default="", allow_blank=True)


class ModerationStatsSerializer(serializers.Serializer):
    """Shape of the moderation KPI stats response."""

    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    under_review = serializers.IntegerField()
    dismissed = serializers.IntegerField()
    warned = serializers.IntegerField()
    taken_down = serializers.IntegerField()
    decided = serializers.IntegerField()
    approval_rate = serializers.FloatField()
    avg_resolution_hours = serializers.FloatField()
