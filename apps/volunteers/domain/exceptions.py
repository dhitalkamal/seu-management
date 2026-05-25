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


class ApplicationNotFoundError(DomainError):
    """No volunteer application matches the given identifier."""

    http_status = 404
    code = "ERR_VOLUNTEER_APPLICATION_NOT_FOUND"


class InvalidStatusTransitionError(DomainError):
    """The requested status change is not permitted from the current state."""

    http_status = 409
    code = "ERR_VOLUNTEER_INVALID_STATUS_TRANSITION"


class AlreadyCheckedInError(DomainError):
    """The volunteer has already checked in to this event."""

    http_status = 409
    code = "ERR_VOLUNTEER_ALREADY_CHECKED_IN"


class NotCheckedInError(DomainError):
    """Cannot check out because the volunteer has not yet checked in."""

    http_status = 409
    code = "ERR_VOLUNTEER_NOT_CHECKED_IN"


class AttendeeConflictError(DomainError):
    """User is already registered as an attendee for this event."""

    http_status = 409
    code = "ERR_VOLUNTEER_ATTENDEE_CONFLICT"


class ApplicationNotRatableError(DomainError):
    """Application cannot be rated because the volunteer has not completed check-out."""

    http_status = 409
    code = "ERR_VOLUNTEER_APPLICATION_NOT_RATABLE"


class InvalidRatingError(DomainError):
    """Rating value is outside the permitted range of 1 to 5."""

    http_status = 422
    code = "ERR_VOLUNTEER_INVALID_RATING"
