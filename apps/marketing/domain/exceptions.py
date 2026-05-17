"""Domain errors raised by marketing use cases and never swallowed silently."""

from __future__ import annotations


class CampaignNotFoundError(Exception):
    """Raised when a campaign cannot be found."""


class SegmentNotFoundError(Exception):
    """Raised when an audience segment cannot be found."""


class CampaignAlreadySentError(Exception):
    """Raised when attempting to send a campaign that is already sent."""
