"""Unit tests for venue use cases."""

from __future__ import annotations

import uuid

import pytest

from apps.venues.domain.exceptions import VenueNotFoundError
from apps.venues.tests.unit.fakes import FakeVenueRepository, FakeVenueSpaceRepository, make_venue


def test_list_venues_returns_org_venues():
    """ListVenuesUseCase returns only venues belonging to the org."""
    from apps.venues.application.use_cases.list_venues import ListVenuesUseCase

    org_id = uuid.uuid4()
    mine = make_venue(organization_id=org_id)
    other = make_venue()
    repo = FakeVenueRepository([mine, other])
    results = ListVenuesUseCase(repo).execute(organization_id=org_id)
    assert len(results) == 1
    assert results[0].id == mine.id


def test_create_venue_success():
    """CreateVenueUseCase persists and returns a new VenueEntity."""
    from apps.venues.application.use_cases.create_venue import CreateVenueUseCase

    repo = FakeVenueRepository()
    result = CreateVenueUseCase(repo).execute(
        organization_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        name="Grand Hall",
        address="123 Street",
        city="Kathmandu",
        country="Nepal",
        capacity=300,
    )
    assert result.name == "Grand Hall"
    assert result.capacity == 300


def test_get_venue_success():
    """GetVenueUseCase returns the venue when it exists."""
    from apps.venues.application.use_cases.get_venue import GetVenueUseCase

    venue = make_venue()
    result = GetVenueUseCase(FakeVenueRepository([venue])).execute(venue_id=venue.id)
    assert result.id == venue.id


def test_get_venue_missing_raises():
    """GetVenueUseCase raises VenueNotFoundError for missing venue."""
    from apps.venues.application.use_cases.get_venue import GetVenueUseCase

    with pytest.raises(VenueNotFoundError):
        GetVenueUseCase(FakeVenueRepository()).execute(venue_id=uuid.uuid4())


def test_update_venue_changes_name():
    """UpdateVenueUseCase persists updated name."""
    from apps.venues.application.use_cases.update_venue import UpdateVenueUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    UpdateVenueUseCase(repo).execute(venue_id=venue.id, name="New Name")
    assert repo.get_by_id(venue.id).name == "New Name"


def test_delete_venue_soft_deletes():
    """DeleteVenueUseCase sets deleted_at on the venue."""
    from apps.venues.application.use_cases.delete_venue import DeleteVenueUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    DeleteVenueUseCase(repo).execute(venue_id=venue.id)
    with pytest.raises(VenueNotFoundError):
        repo.get_by_id(venue.id)


def test_add_space_success():
    """AddVenueSpaceUseCase persists a new space and returns it."""
    from apps.venues.application.use_cases.add_space import AddVenueSpaceUseCase

    venue = make_venue()
    space_repo = FakeVenueSpaceRepository()
    result = AddVenueSpaceUseCase(FakeVenueRepository([venue]), space_repo).execute(
        venue_id=venue.id, name="Main Hall", capacity=200, floor="Ground"
    )
    assert result.name == "Main Hall"
    assert len(space_repo.list_by_venue(venue.id)) == 1


def test_list_spaces_returns_venue_spaces():
    """ListVenueSpacesUseCase returns all spaces for a venue."""
    from apps.venues.application.use_cases.list_spaces import ListVenueSpacesUseCase
    from apps.venues.tests.unit.fakes import make_space

    venue = make_venue()
    space = make_space(venue_id=venue.id)
    space_repo = FakeVenueSpaceRepository()
    space_repo.create(space)
    results = ListVenueSpacesUseCase(FakeVenueRepository([venue]), space_repo).execute(venue_id=venue.id)
    assert len(results) == 1
    assert results[0].id == space.id
