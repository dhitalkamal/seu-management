"""DRF serializers for volunteers request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateRoleSerializer(serializers.Serializer):
    """Payload for creating a volunteer role."""

    event_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="")
    capacity = serializers.IntegerField(min_value=1, default=1)
    organisation_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class ApplySerializer(serializers.Serializer):
    """Payload for applying to a volunteer role."""

    event_id = serializers.UUIDField()


class VolunteerRoleResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer role resource."""

    id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    organisation_id = serializers.UUIDField(allow_null=True)
    name = serializers.CharField()
    description = serializers.CharField()
    capacity = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class VolunteerApplicationResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer application resource."""

    id = serializers.UUIDField()
    volunteer_role_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
