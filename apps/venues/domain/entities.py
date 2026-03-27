"""Pure Python domain entities for the venues module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class VenueEntity:
    """A physical venue owned by an organisation."""

    id: uuid.UUID
    organisation_id: uuid.UUID
    created_by: uuid.UUID
    name: str
    address: str
    city: str
    country: str
    capacity: int
    created_at: datetime
    description: str = ""
    website: str = ""
    deleted_at: datetime | None = None
    # populated by geocoder after save; None when API key is absent or geocoding fails
    latitude: float | None = None
    longitude: float | None = None


@dataclass(slots=True)
class VenueSpaceEntity:
    """A named sub-space within a venue (e.g. Main Hall, Room A)."""

    id: uuid.UUID
    venue_id: uuid.UUID
    name: str
    capacity: int
    floor: str
    created_at: datetime


@dataclass(slots=True)
class VenueBookingEntity:
    """A time-bound booking of a venue for a specific event."""

    id: uuid.UUID
    venue_id: uuid.UUID
    event_id: uuid.UUID
    booked_by: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
