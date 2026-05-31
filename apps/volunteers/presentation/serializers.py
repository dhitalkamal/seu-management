"""DRF serializers for volunteers request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateRoleSerializer(serializers.Serializer):
    """Payload for creating a volunteer role."""

    event_id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="")
    capacity = serializers.IntegerField(min_value=1, default=1)
    organization_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class ApplySerializer(serializers.Serializer):
    """Payload for applying to a volunteer role."""

    event_id = serializers.UUIDField()


class RateApplicationSerializer(serializers.Serializer):
    """Payload for submitting a volunteer rating."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)


class CreateShiftSerializer(serializers.Serializer):
    """Payload for creating a shift under a volunteer role."""

    event_id = serializers.UUIDField()
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()
    capacity = serializers.IntegerField(min_value=1, default=1)
    location = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)


class VolunteerRoleResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer role resource."""

    id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    organization_id = serializers.UUIDField(allow_null=True)
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
    check_in_at = serializers.DateTimeField(allow_null=True)
    check_out_at = serializers.DateTimeField(allow_null=True)
    rating = serializers.IntegerField(allow_null=True)
    feedback = serializers.CharField(allow_null=True)
    certificate_issued = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class VolunteerShiftResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer shift resource."""

    id = serializers.UUIDField()
    role_id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()
    capacity = serializers.IntegerField()
    location = serializers.CharField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()


class CertificateResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer certificate resource."""

    id = serializers.UUIDField()
    application_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    pdf_url = serializers.CharField()
    verify_url = serializers.CharField()
    issued_at = serializers.DateTimeField()


class VolunteerProfileResponseSerializer(serializers.Serializer):
    """Public shape of a volunteer profile resource."""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    average_rating = serializers.FloatField(allow_null=True)
    total_ratings = serializers.IntegerField()
    total_hours = serializers.FloatField()
    certificate_count = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
