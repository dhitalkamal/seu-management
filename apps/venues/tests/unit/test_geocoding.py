"""Unit tests for venue geocoding use cases."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from apps.venues.tests.unit.fakes import FakeVenueRepository, make_venue


def test_create_venue_geocodes_address_when_key_configured():
    """CreateVenueUseCase populates lat/lng when geocoder returns coordinates."""
    from apps.venues.application.use_cases.create_venue import CreateVenueUseCase

    repo = FakeVenueRepository()
    with patch("apps.venues.application.use_cases.create_venue.geocode_address") as mock_geo:
        mock_geo.return_value = (27.7172, 85.3240)
        result = CreateVenueUseCase(repo).execute(
            organisation_id=uuid.uuid4(),
            created_by=uuid.uuid4(),
            name="Grand Hall",
            address="Thamel",
            city="Kathmandu",
            country="Nepal",
            capacity=300,
        )
    assert result.latitude == 27.7172
    assert result.longitude == 85.3240


def test_create_venue_geocode_returns_none_leaves_coords_null():
    """CreateVenueUseCase leaves lat/lng as None when geocoder returns None."""
    from apps.venues.application.use_cases.create_venue import CreateVenueUseCase

    repo = FakeVenueRepository()
    with patch("apps.venues.application.use_cases.create_venue.geocode_address") as mock_geo:
        mock_geo.return_value = None
        result = CreateVenueUseCase(repo).execute(
            organisation_id=uuid.uuid4(),
            created_by=uuid.uuid4(),
            name="Grand Hall",
            address="Unknown Place",
            city="Kathmandu",
            country="Nepal",
            capacity=300,
        )
    assert result.latitude is None
    assert result.longitude is None


def test_update_venue_geocodes_when_address_changes():
    """UpdateVenueUseCase re-geocodes when address is updated."""
    from apps.venues.application.use_cases.update_venue import UpdateVenueUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    with patch("apps.venues.application.use_cases.update_venue.geocode_address") as mock_geo:
        mock_geo.return_value = (27.7000, 85.3000)
        result = UpdateVenueUseCase(repo).execute(
            venue_id=venue.id,
            address="New Address",
            city="Pokhara",
        )
    assert result.latitude == 27.7000
    assert result.longitude == 85.3000


def test_update_venue_does_not_geocode_when_address_unchanged():
    """UpdateVenueUseCase does not call geocoder when address is not part of the update."""
    from apps.venues.application.use_cases.update_venue import UpdateVenueUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    with patch("apps.venues.application.use_cases.update_venue.geocode_address") as mock_geo:
        UpdateVenueUseCase(repo).execute(venue_id=venue.id, name="New Name")
    mock_geo.assert_not_called()


def test_geocode_address_returns_none_without_api_key():
    """geocode_address returns None immediately when GOOGLE_MAPS_API_KEY is not set."""
    from apps.venues.infrastructure.geocoder import geocode_address

    with patch("apps.venues.infrastructure.geocoder.getattr", return_value=""):
        result = geocode_address("Thamel, Kathmandu")
    assert result is None


def test_venue_entity_has_lat_lng_fields():
    """VenueEntity has nullable latitude and longitude fields."""

    venue = make_venue()
    assert hasattr(venue, "latitude")
    assert hasattr(venue, "longitude")
    assert venue.latitude is None
    assert venue.longitude is None
