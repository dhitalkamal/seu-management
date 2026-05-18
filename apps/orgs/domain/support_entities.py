"""Pure Python domain entities for support tickets."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SupportTicketEntity:
    """A support ticket submitted by or on behalf of an organisation."""

    id: uuid.UUID
    subject: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    org_id: uuid.UUID | None = None
    org_name: str = ""
    submitted_by: uuid.UUID | None = None
    message: str = ""
