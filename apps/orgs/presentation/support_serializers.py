"""Serializers for support ticket endpoints."""

from __future__ import annotations

from rest_framework import serializers


class CreateTicketSerializer(serializers.Serializer):
    """Payload for submitting a new support ticket."""

    subject = serializers.CharField(max_length=500)
    message = serializers.CharField(required=False, default="")
    priority = serializers.ChoiceField(choices=["low", "med", "high", "critical"], default="med")
    org_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    org_name = serializers.CharField(required=False, default="")


class UpdateTicketStatusSerializer(serializers.Serializer):
    """Payload for updating ticket status."""

    status = serializers.ChoiceField(choices=["open", "in_progress", "escalated", "resolved", "closed"])
    priority = serializers.ChoiceField(choices=["low", "med", "high", "critical"], required=False)


class TicketResponseSerializer(serializers.Serializer):
    """Response shape for a support ticket."""

    id = serializers.UUIDField()
    subject = serializers.CharField()
    message = serializers.CharField()
    priority = serializers.CharField()
    status = serializers.CharField()
    org_id = serializers.UUIDField(allow_null=True)
    org_name = serializers.CharField()
    submitted_by = serializers.UUIDField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
