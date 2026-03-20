"""Unit tests for MarketingEventPublisher."""

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


def test_publish_campaign_sent_uses_correct_routing_key() -> None:
    """publish_campaign_sent sends to routing key marketing.campaign.sent."""
    with patch("apps.marketing.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher

        MarketingEventPublisher().publish_campaign_sent(
            campaign_id=uuid.uuid4(),
            subject="Hello",
            body="<p>Hi</p>",
            org_id=uuid.uuid4(),
            segment_id=None,
            user_emails=["a@example.com"],
        )

        kwargs = mock_channel.basic_publish.call_args.kwargs
        assert kwargs["routing_key"] == "marketing.campaign.sent"


def test_publish_campaign_sent_includes_user_emails() -> None:
    """publish_campaign_sent payload includes the resolved user_emails list."""
    with patch("apps.marketing.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher

        campaign_id = uuid.uuid4()
        org_id = uuid.uuid4()
        segment_id = uuid.uuid4()
        emails = ["alice@example.com", "bob@example.com"]

        MarketingEventPublisher().publish_campaign_sent(
            campaign_id=campaign_id,
            subject="Newsletter",
            body="<p>Hello</p>",
            org_id=org_id,
            segment_id=segment_id,
            user_emails=emails,
        )

        payload = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert payload["campaign_id"] == str(campaign_id)
        assert payload["subject"] == "Newsletter"
        assert payload["org_id"] == str(org_id)
        assert payload["segment_id"] == str(segment_id)
        assert payload["user_emails"] == emails


def test_publish_campaign_sent_handles_none_org_and_segment() -> None:
    """publish_campaign_sent with no org_id or segment_id serialises them as None."""
    with patch("apps.marketing.infrastructure.event_publisher.pika") as mock_pika:
        mock_channel = _make_channel_mock(mock_pika)
        from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher

        MarketingEventPublisher().publish_campaign_sent(
            campaign_id=uuid.uuid4(),
            subject="Blast",
            body="<p>Hi</p>",
            org_id=None,
            segment_id=None,
            user_emails=["x@example.com"],
        )

        payload = json.loads(mock_channel.basic_publish.call_args.kwargs["body"])
        assert payload["org_id"] is None
        assert payload["segment_id"] is None
