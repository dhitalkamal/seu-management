"""DRF serializers for the compliance controls API."""

from __future__ import annotations

from rest_framework import serializers


class ComplianceControlCreateSerializer(serializers.Serializer):
    """Payload for creating a new compliance control."""

    category = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(default="", allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=["pass", "fail", "na"])
    last_checked = serializers.DateTimeField(required=False, allow_null=True, default=None)


class ComplianceControlPatchSerializer(serializers.Serializer):
    """Payload for partially updating a compliance control (all fields optional)."""

    category = serializers.CharField(max_length=50, required=False)
    name = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    status = serializers.ChoiceField(choices=["pass", "fail", "na"], required=False)
    last_checked = serializers.DateTimeField(required=False, allow_null=True)


class ComplianceControlResponseSerializer(serializers.Serializer):
    """Public shape of a compliance control resource."""

    id = serializers.UUIDField()
    category = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    status = serializers.CharField()
    last_checked = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
