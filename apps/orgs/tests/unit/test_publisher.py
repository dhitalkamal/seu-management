"""Unit test: verify publish_event calls pika correctly."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


@patch("apps.orgs.infrastructure.publisher.pika")
def test_publish_event_sends_message(mock_pika: MagicMock) -> None:
    """publish_event should open a connection, publish, and close."""
    from apps.orgs.infrastructure.publisher import publish_event

    mock_conn = MagicMock()
    mock_channel = MagicMock()
    mock_pika.BlockingConnection.return_value = mock_conn
    mock_conn.channel.return_value = mock_channel

    publish_event(routing_key="org.created", payload={"org_id": "123"})

    mock_channel.basic_publish.assert_called_once()
    call_kwargs = mock_channel.basic_publish.call_args
    assert call_kwargs[1]["routing_key"] == "org.created"
    mock_conn.close.assert_called_once()
