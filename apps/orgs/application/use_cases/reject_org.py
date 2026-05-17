"""Use case: reject a pending organisation application."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganisationRepository

_ALLOWED_FROM: frozenset[str] = frozenset({"pending_review"})


class RejectOrganisationUseCase:
    """Transition an organisation from pending_review to suspended."""

    def __init__(self, org_repo: IOrganisationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Validate current status then set status=suspended.

        @raises OrgNotFoundError if the org does not exist
        @raises InvalidOrgStatusTransitionError if status is not pending_review
        """
        org = self._orgs.get_by_id(org_id)
        if org.status not in _ALLOWED_FROM:
            raise InvalidOrgStatusTransitionError(
                f"Cannot reject an organisation with status '{org.status}'."
            )
        org.status = "suspended"
        return self._orgs.update(org)
