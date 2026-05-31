"""DRF serializers for orgs request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateOrgSerializer(serializers.Serializer):
    """Payload for creating a new organization."""

    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=100)
    contact_email = serializers.EmailField()
    description = serializers.CharField(min_length=20)
    website = serializers.URLField(required=False, default="", allow_blank=True)
    logo_url = serializers.URLField(required=False, default="", allow_blank=True)
    phone = serializers.RegexField(
        regex=r"^\+?\d{7,15}$",
        max_length=20,
        error_messages={"invalid": "Phone must contain only digits (7-15), optionally starting with +."},
    )
    address = serializers.CharField(max_length=500, min_length=5)
    city = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    org_type = serializers.ChoiceField(
        choices=["company", "ngo", "community", "educational", "government", "individual"],
        required=False,
        default="company",
    )
    facebook_url = serializers.URLField(required=False, default="", allow_blank=True)
    twitter_url = serializers.URLField(required=False, default="", allow_blank=True)
    instagram_url = serializers.URLField(required=False, default="", allow_blank=True)
    linkedin_url = serializers.URLField(required=False, default="", allow_blank=True)

    def validate(self, attrs: dict) -> dict:
        """Ensure at least one social link is provided."""
        social_fields = ["facebook_url", "twitter_url", "instagram_url", "linkedin_url"]
        has_social = any(attrs.get(f) for f in social_fields)
        if not has_social:
            raise serializers.ValidationError({"facebook_url": "At least one social media link is required."})
        return attrs


class OrgResponseSerializer(serializers.Serializer):
    """Public shape of an organization resource."""

    id = serializers.UUIDField()
    created_by = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    contact_email = serializers.EmailField()
    description = serializers.CharField()
    website = serializers.CharField()
    logo_url = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    org_type = serializers.CharField()
    facebook_url = serializers.CharField()
    twitter_url = serializers.CharField()
    instagram_url = serializers.CharField()
    linkedin_url = serializers.CharField()
    status = serializers.CharField()
    is_verified = serializers.BooleanField()
    plan = serializers.CharField()
    plan_expires_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class UpdateOrgSerializer(serializers.Serializer):
    """Partial update payload - every field is optional."""

    name = serializers.CharField(max_length=255, required=False)
    contact_email = serializers.EmailField(required=False)
    description = serializers.CharField(required=False)
    website = serializers.URLField(required=False, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country = serializers.CharField(max_length=100, required=False, allow_blank=True)
    org_type = serializers.ChoiceField(
        choices=["company", "ngo", "community", "educational", "government", "individual"],
        required=False,
    )
    facebook_url = serializers.URLField(required=False, allow_blank=True)
    twitter_url = serializers.URLField(required=False, allow_blank=True)
    instagram_url = serializers.URLField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)


class AddMemberSerializer(serializers.Serializer):
    """Payload for adding a member to an organization."""

    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=["owner", "admin", "manager", "member"])


class OrgMemberResponseSerializer(serializers.Serializer):
    """Public shape of an org membership resource."""

    id = serializers.UUIDField()
    organization_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    joined_at = serializers.DateTimeField()


class OrgDocumentResponseSerializer(serializers.Serializer):
    """Public shape of an organization document resource."""

    id = serializers.UUIDField()
    organization_id = serializers.UUIDField(source="organization.id")
    doc_type = serializers.CharField()
    file_url = serializers.URLField()
    file_name = serializers.CharField()
    file_size = serializers.IntegerField()
    uploaded_at = serializers.DateTimeField()


class UploadOrgDocumentSerializer(serializers.Serializer):
    """Payload for uploading a document to an organization."""

    doc_type = serializers.ChoiceField(
        choices=["registration_cert", "pan_card", "tax_clearance", "logo", "other"],
    )
    file_url = serializers.URLField()
    file_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField(required=False, default=0)


class CreateInviteSerializer(serializers.Serializer):
    """Payload for inviting a user to an organization."""

    invitee_email = serializers.EmailField()
    role = serializers.ChoiceField(choices=["owner", "admin", "manager", "member"])


class AcceptInviteSerializer(serializers.Serializer):
    """Payload for accepting an organization invite."""

    user_id = serializers.UUIDField()


class OrgInviteResponseSerializer(serializers.Serializer):
    """Public shape of an organization invite resource."""

    id = serializers.UUIDField()
    org_id = serializers.UUIDField()
    inviter_id = serializers.UUIDField()
    invitee_email = serializers.EmailField()
    role = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    expires_at = serializers.DateTimeField()
    accepted_by = serializers.UUIDField(allow_null=True)
