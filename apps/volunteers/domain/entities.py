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
    feedback: str | None = None
    certificate_issued: bool = False

    @property
    def hours_worked(self) -> float | None:
        """Elapsed volunteer hours; None until the volunteer has checked out."""
        if self.check_in_at is None or self.check_out_at is None:
            return None
        delta = self.check_out_at - self.check_in_at
        return round(delta.total_seconds() / 3600, 2)


@dataclass(slots=True)
class CertificateEntity:
    """A generated volunteer participation certificate with a unique QR-verified ID."""

    id: uuid.UUID
    application_id: uuid.UUID
    volunteer_id: uuid.UUID
    event_id: uuid.UUID
    volunteer_name: str
    event_name: str
    role_name: str
    pdf_url: str
    issued_at: datetime
    org_id: uuid.UUID | None = None
    hours_worked: float | None = None
    rating: int | None = None
