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
    organization_id: uuid.UUID | None = None
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
