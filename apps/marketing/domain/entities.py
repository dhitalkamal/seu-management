"""Pure Python domain entities for the marketing module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CampaignEntity:
    """An email or push marketing campaign."""

    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    subject: str
    body: str
    status: str
    segment_id: uuid.UUID | None
    created_at: datetime
    sent_at: datetime | None = None


@dataclass(slots=True)
class AudienceSegmentEntity:
    """A named filter set that defines a group of recipients."""

    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    filters: dict
    created_at: datetime
