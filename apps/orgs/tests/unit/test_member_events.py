"""Unit tests for OrgEventPublisher."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch


def test_publish_member_added() -> None:
    """publish_member_added sends a message with routing_key org.member.added."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel

        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        publisher = OrgEventPublisher()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        publisher.publish_member_added(org_id=org_id, user_id=user_id, role="member")

        mock_channel.basic_publish.assert_called_once()
        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.member.added"


def test_publish_member_removed() -> None:
    """publish_member_removed sends a message with routing_key org.member.removed."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel

        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        publisher = OrgEventPublisher()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        publisher.publish_member_removed(org_id=org_id, user_id=user_id)

        mock_channel.basic_publish.assert_called_once()
        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.member.removed"


def test_publish_member_role_changed() -> None:
    """publish_member_role_changed sends a message with routing_key org.member.role_changed."""
    with patch("apps.orgs.infrastructure.event_publisher.pika") as mock_pika:
        mock_conn = MagicMock()
        mock_channel = MagicMock()
        mock_pika.BlockingConnection.return_value = mock_conn
        mock_conn.channel.return_value = mock_channel

        from apps.orgs.infrastructure.event_publisher import OrgEventPublisher

        publisher = OrgEventPublisher()
        org_id = uuid.uuid4()
        user_id = uuid.uuid4()
        publisher.publish_member_role_changed(
            org_id=org_id,
            user_id=user_id,
            old_role="member",
            new_role="admin",
        )

        mock_channel.basic_publish.assert_called_once()
        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "org.member.role_changed"
