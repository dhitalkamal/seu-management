"""DRF serializers for venues request deserialization and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class CreateVenueSerializer(serializers.Serializer):
    """Request body for creating a venue."""

    name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=500)
    city = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    capacity = serializers.IntegerField(min_value=1)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    website = serializers.URLField(required=False, allow_blank=True, default="")
    organisation_id = serializers.UUIDField()


class UpdateVenueSerializer(serializers.Serializer):
    """Partial-update payload for a venue."""

    name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=500, required=False)
    city = serializers.CharField(max_length=100, required=False)
    country = serializers.CharField(max_length=100, required=False)
    capacity = serializers.IntegerField(min_value=1, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)


class VenueResponseSerializer(serializers.Serializer):
    """Public shape of a venue resource."""

    id = serializers.UUIDField()
    organisation_id = serializers.UUIDField()
    name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    capacity = serializers.IntegerField()
    description = serializers.CharField()
    website = serializers.CharField()
    created_by = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)


class CreateVenueSpaceSerializer(serializers.Serializer):
    """Request body for adding a venue space."""

    name = serializers.CharField(max_length=255)
    capacity = serializers.IntegerField(min_value=1)
    floor = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")


class VenueSpaceResponseSerializer(serializers.Serializer):
    """Public shape of a venue space resource."""

    id = serializers.UUIDField()
    venue_id = serializers.UUIDField()
    name = serializers.CharField()
    capacity = serializers.IntegerField()
    floor = serializers.CharField()
    created_at = serializers.DateTimeField()


class CreateVenueBookingSerializer(serializers.Serializer):
    """Request body for creating a venue booking."""

    event_id = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class VenueBookingResponseSerializer(serializers.Serializer):
    """Public shape of a venue booking resource."""

    id = serializers.UUIDField()
    venue_id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    booked_by = serializers.UUIDField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
