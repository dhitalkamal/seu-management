"""Django ORM models for the venues domain."""

from __future__ import annotations

import uuid

from django.db import models

from apps.venues.domain.entities import VenueEntity, VenueSpaceEntity


class Venue(models.Model):
    """A physical venue owned by an organisation."""

    class Meta:
        db_table = '"venues"."venue"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation_id = models.UUIDField()
    created_by = models.UUIDField()
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> VenueEntity:
        """Map this ORM row to a pure-Python VenueEntity."""
        return VenueEntity(
            id=self.id,
            organisation_id=self.organisation_id,
            created_by=self.created_by,
            name=self.name,
            address=self.address,
            city=self.city,
            country=self.country,
            capacity=self.capacity,
            created_at=self.created_at,
            description=self.description,
            website=self.website,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: VenueEntity) -> "Venue":
        """Build an unsaved ORM instance from a VenueEntity."""
        return cls(
            id=entity.id,
            organisation_id=entity.organisation_id,
            created_by=entity.created_by,
            name=entity.name,
            address=entity.address,
            city=entity.city,
            country=entity.country,
            capacity=entity.capacity,
            description=entity.description,
            website=entity.website,
            deleted_at=entity.deleted_at,
        )


class VenueSpace(models.Model):
    """A named sub-space within a venue."""

    class Meta:
        db_table = '"venues"."venue_space"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="spaces")
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    floor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> VenueSpaceEntity:
        """Map this ORM row to a pure-Python VenueSpaceEntity."""
        return VenueSpaceEntity(
            id=self.id,
            venue_id=self.venue_id,
            name=self.name,
            capacity=self.capacity,
            floor=self.floor,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: VenueSpaceEntity) -> "VenueSpace":
        """Build an unsaved ORM instance from a VenueSpaceEntity."""
        return cls(
            id=entity.id,
            venue_id=entity.venue_id,
            name=entity.name,
            capacity=entity.capacity,
            floor=entity.floor,
        )
