"""Unit tests for DeclineInviteUseCase - see test_invite_use_cases.py for full suite."""

from apps.orgs.tests.unit.test_invite_use_cases import (
    test_decline_invite_marks_declined,
    test_decline_invite_raises_when_not_pending,
)

__all__ = [
    "test_decline_invite_marks_declined",
    "test_decline_invite_raises_when_not_pending",
]
