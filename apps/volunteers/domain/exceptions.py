"""Domain errors raised by volunteers use cases and never swallowed silently."""

from __future__ import annotations

from apps.common.api.exceptions import DomainError


class RoleNotFoundError(DomainError):
    """No volunteer role matches the given identifier or the role is inactive."""

    http_status = 404
    code = "ERR_VOLUNTEER_ROLE_NOT_FOUND"


class RoleAtCapacityError(DomainError):
    """The volunteer role has no remaining spots."""

    http_status = 409
    code = "ERR_VOLUNTEER_ROLE_AT_CAPACITY"


class AlreadyAppliedError(DomainError):
    """The user has already submitted a non-cancelled application to this role."""

    http_status = 409
    code = "ERR_VOLUNTEER_ALREADY_APPLIED"
