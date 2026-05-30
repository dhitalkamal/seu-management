"""Pure Python domain entities for the moderation module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ModerationCaseEntity:
    """A flagged content item under review by a superadmin."""

    id: uuid.UUID
    content_type: str  # "event", "post", "comment"
    content_id: uuid.UUID
    content_title: str
    reporter_id: uuid.UUID | None
    organization_id: uuid.UUID | None
    reason: str
    # pending -> under_review -> dismissed | warned | taken_down
    status: str
    reviewer_id: uuid.UUID | None
    reviewer_notes: str
    created_at: datetime
    resolved_at: datetime | None
