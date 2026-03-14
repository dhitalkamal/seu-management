"""Use case: create a new moderation case when content is reported."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.exceptions import InvalidContentTypeError
from apps.moderation.domain.repositories import IModerationCaseRepository

# ! these are the only accepted content types - anything else is a client error
VALID_CONTENT_TYPES = {"event", "post", "comment"}


class CreateModerationCaseUseCase:
    """Create a new moderation case in pending status."""

    def __init__(self, repo: IModerationCaseRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        content_type: str,
        content_id: uuid.UUID,
        content_title: str,
        reason: str,
        reporter_id: uuid.UUID | None = None,
        organisation_id: uuid.UUID | None = None,
    ) -> ModerationCaseEntity:
        """
        Validate and persist a new moderation case.

        @param content_type - one of "event", "post", "comment"
        @param content_id - uuid of the flagged content
        @param content_title - human-readable title for the case list
        @param reason - reporter's stated reason for the flag
        @param reporter_id - uuid of the reporting user, optional for system flags
        @param organisation_id - org the content belongs to, optional
        @returns the persisted ModerationCaseEntity with status=pending
        @raises InvalidContentTypeError if content_type is not recognised
        """
        if content_type not in VALID_CONTENT_TYPES:
            raise InvalidContentTypeError(
                f"'{content_type}' is not a valid content type. Must be one of: {', '.join(sorted(VALID_CONTENT_TYPES))}."
            )

        now = datetime.now(timezone.utc)
        entity = ModerationCaseEntity(
            id=uuid.uuid4(),
            content_type=content_type,
            content_id=content_id,
            content_title=content_title,
            reporter_id=reporter_id,
            organisation_id=organisation_id,
            reason=reason,
            status="pending",
            reviewer_id=None,
            reviewer_notes="",
            created_at=now,
            resolved_at=None,
        )
        return self._repo.save(entity)
