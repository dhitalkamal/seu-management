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
    check_in_at = serializers.DateTimeField(allow_null=True)
    check_out_at = serializers.DateTimeField(allow_null=True)
    hours_worked = serializers.FloatField(allow_null=True)
    rating = serializers.IntegerField(allow_null=True)
    feedback = serializers.CharField(allow_null=True)
    certificate_issued = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class RateVolunteerSerializer(serializers.Serializer):
    """Payload for rating a completed volunteer."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback = serializers.CharField(required=False, allow_null=True, default=None)


class GenerateCertificateSerializer(serializers.Serializer):
    """Payload for triggering certificate generation."""

    volunteer_name = serializers.CharField(max_length=255)
    event_name = serializers.CharField(max_length=255)
    role_name = serializers.CharField(max_length=255)
    org_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class CertificateResponseSerializer(serializers.Serializer):
    """Public shape of a certificate resource."""

    id = serializers.UUIDField()
    application_id = serializers.UUIDField()
    volunteer_id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    org_id = serializers.UUIDField(allow_null=True)
    volunteer_name = serializers.CharField()
    event_name = serializers.CharField()
    role_name = serializers.CharField()
    pdf_url = serializers.CharField()
    issued_at = serializers.DateTimeField()
    hours_worked = serializers.FloatField(allow_null=True)
    rating = serializers.IntegerField(allow_null=True)
