"""Pure Python domain entities for the volunteers module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class VolunteerRoleEntity:
    """A volunteer position for an event."""

    id: uuid.UUID
    event_id: uuid.UUID
    name: str
    capacity: int
    is_active: bool
    created_at: datetime
    organisation_id: uuid.UUID | None = None
    description: str = ""


@dataclass(slots=True)
class VolunteerApplicationEntity:
    """A user's application to fill a volunteer role."""

    id: uuid.UUID
    volunteer_role_id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    rating: int | None = None
    certificate_issued: bool = False
    feedback: str | None = None

    @property
    def hours_worked(self) -> float | None:
        """Elapsed hours between check-in and check-out, or None if incomplete."""
        if self.check_in_at is None or self.check_out_at is None:
            return None
        delta = self.check_out_at - self.check_in_at
        return delta.total_seconds() / 3600


@dataclass(slots=True)
class CertificateEntity:
    """A volunteer participation certificate issued after event completion."""

    id: uuid.UUID
    application_id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    pdf_url: str
    verify_url: str
    issued_at: datetime


@dataclass(slots=True)
class VolunteerShiftEntity:
    """A time-boxed shift template attached to a volunteer role."""

    id: uuid.UUID
    role_id: uuid.UUID
    event_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    capacity: int
    created_at: datetime
    location: str | None = None
    description: str | None = None


@dataclass(slots=True)
class VolunteerProfileEntity:
    """Aggregate stats for a single volunteer user across all events."""

    id: uuid.UUID
    user_id: uuid.UUID
    total_ratings: int
    total_hours: float
    certificate_count: int
    updated_at: datetime
    average_rating: float | None = None
