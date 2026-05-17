"""DRF serializers for orgs request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateOrgSerializer(serializers.Serializer):
    """Payload for creating a new organisation."""

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=100)
    contact_email = serializers.EmailField()
    description = serializers.CharField(required=False, default="")
    website = serializers.URLField(required=False, default="")
    logo_url = serializers.URLField(required=False, default="")


class OrgResponseSerializer(serializers.Serializer):
    """Public shape of an organisation resource."""

    id = serializers.UUIDField()
    created_by = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    contact_email = serializers.EmailField()
    description = serializers.CharField()
    website = serializers.CharField()
    logo_url = serializers.CharField()
    status = serializers.CharField()
    is_verified = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class AddMemberSerializer(serializers.Serializer):
    """Payload for adding a member to an organisation."""

    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=["owner", "admin", "manager", "member"])


class OrgMemberResponseSerializer(serializers.Serializer):
    """Public shape of an org membership resource."""

    id = serializers.UUIDField()
    organisation_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    joined_at = serializers.DateTimeField()
