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
    """The requested status change is not allowed from the current status."""

    http_status = 422
    code = "ERR_VOLUNTEER_INVALID_STATUS_TRANSITION"


class AlreadyCheckedInError(DomainError):
    """The volunteer has already checked in to this event."""

    http_status = 409
    code = "ERR_VOLUNTEER_ALREADY_CHECKED_IN"


class NotCheckedInError(DomainError):
    """Check-out attempted before check-in, or check-in data is missing."""

    http_status = 422
    code = "ERR_VOLUNTEER_NOT_CHECKED_IN"


class ApplicationNotRatableError(DomainError):
    """Application cannot be rated because attendance timestamps are incomplete."""

    http_status = 422
    code = "ERR_VOLUNTEER_APPLICATION_NOT_RATABLE"


class InvalidRatingError(DomainError):
    """Rating value is outside the allowed 1-5 range."""

    http_status = 422
    code = "ERR_VOLUNTEER_INVALID_RATING"


class CertificateNotEligibleError(DomainError):
    """Application does not meet the requirements for certificate generation."""

    http_status = 422
    code = "ERR_VOLUNTEER_CERTIFICATE_NOT_ELIGIBLE"


class CertificateAlreadyIssuedError(DomainError):
    """A certificate has already been issued for this application."""

    http_status = 409
    code = "ERR_VOLUNTEER_CERTIFICATE_ALREADY_ISSUED"


class CertificateNotFoundError(DomainError):
    """No certificate matches the given identifier."""

    http_status = 404
    code = "ERR_VOLUNTEER_CERTIFICATE_NOT_FOUND"


class ShiftNotFoundError(DomainError):
    """No volunteer shift matches the given identifier."""

    http_status = 404
    code = "ERR_VOLUNTEER_SHIFT_NOT_FOUND"
