"""Unit tests for OrgEventPublisher org lifecycle methods."""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch


def _make_channel_mock(mock_pika: MagicMock) -> MagicMock:
    """Wire up pika mock and return the channel mock."""
    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_pika.BlockingConnection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel
    return mock_channel


def test_publish_org_created_sends_correct_routing_key() -> None:
    """publish_org_created sends a message with routing_key org.created."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        OrgEventPublisher().publish_org_created(
            org_id=uuid.uuid4(),
            org_name="Acme Corp",
            creator_id=uuid.uuid4(),
            contact_email="acme@example.com",
        )

        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.created"


def test_publish_org_created_includes_contact_email() -> None:
    """publish_org_created payload contains org_id, org_name, creator_id, and contact_email."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        org_id = uuid.uuid4()
        creator_id = uuid.uuid4()
        OrgEventPublisher().publish_org_created(
            org_id=org_id,
            org_name="Acme Corp",
            creator_id=creator_id,
            contact_email="acme@example.com",
        )

        payload = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert payload["org_id"] == str(org_id)
        assert payload["org_name"] == "Acme Corp"
        assert payload["creator_id"] == str(creator_id)
        assert payload["contact_email"] == "acme@example.com"


def test_publish_org_approved_sends_correct_routing_key() -> None:
    """publish_org_approved sends a message with routing_key org.approved."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        OrgEventPublisher().publish_org_approved(
            org_id=uuid.uuid4(),
            org_name="Acme Corp",
            contact_email="acme@example.com",
        )

        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.approved"


def test_publish_org_approved_includes_contact_email() -> None:
    """publish_org_approved payload contains org_id, org_name, and contact_email."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        org_id = uuid.uuid4()
        OrgEventPublisher().publish_org_approved(
            org_id=org_id,
            org_name="Acme Corp",
            contact_email="acme@example.com",
        )

        payload = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert payload["org_id"] == str(org_id)
        assert payload["org_name"] == "Acme Corp"
        assert payload["contact_email"] == "acme@example.com"


def test_publish_org_rejected_sends_correct_routing_key() -> None:
    """publish_org_rejected sends a message with routing_key org.rejected."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        OrgEventPublisher().publish_org_rejected(
            org_id=uuid.uuid4(),
            org_name="Dodgy Ltd",
            reason="Incomplete documentation.",
            contact_email="dodgy@example.com",
        )

        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.rejected"


def test_publish_org_rejected_includes_all_fields() -> None:
    """publish_org_rejected payload contains org_id, org_name, reason, and contact_email."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        org_id = uuid.uuid4()
        OrgEventPublisher().publish_org_rejected(
            org_id=org_id,
            org_name="Dodgy Ltd",
            reason="Incomplete documentation.",
            contact_email="dodgy@example.com",
        )

        payload = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert payload["org_id"] == str(org_id)
        assert payload["org_name"] == "Dodgy Ltd"
        assert payload["reason"] == "Incomplete documentation."
        assert payload["contact_email"] == "dodgy@example.com"
