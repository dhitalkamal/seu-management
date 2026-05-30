"""RabbitMQ event publisher for marketing domain events."""

from __future__ import annotations

import json
import logging
import uuid

import pika
from django.conf import settings

logger = logging.getLogger(__name__)

_EXCHANGE = "sansaar"
_EXCHANGE_TYPE = "topic"


class MarketingEventPublisher:
    """Publishes marketing.* events to the sansaar topic exchange."""

    def _publish(self, routing_key: str, payload: dict) -> None:
        """
        Open a fresh connection, publish the event, then close.

        Failure is logged and swallowed so the caller's DB transaction is not
        rolled back -- RabbitMQ is observability infrastructure, not primary path.

        @param routing_key - topic routing key, e.g. "marketing.campaign.sent"
        @param payload     - JSON-serialisable dict sent as the message body
        """
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(
                exchange=_EXCHANGE,
                exchange_type=_EXCHANGE_TYPE,
                durable=True,
            )
            channel.basic_publish(
                exchange=_EXCHANGE,
                routing_key=routing_key,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
            )
            connection.close()
        except Exception:
            logger.warning(
                "Failed to publish %s to RabbitMQ.",
                routing_key,
                exc_info=True,
            )

    def publish_campaign_sent(
        self,
        *,
        campaign_id: uuid.UUID,
        subject: str,
        body: str,
        org_id: uuid.UUID | None,
        segment_id: uuid.UUID | None,
        user_emails: list[str],
    ) -> None:
        """
        Publish marketing.campaign.sent after a campaign is dispatched.

        The notification-service consumer iterates user_emails and sends each one.

        @param campaign_id  - the sent campaign's UUID
        @param subject      - email subject line
        @param body         - HTML email body
        @param org_id       - the owning organization's UUID (None for system campaigns)
        @param segment_id   - the audience segment's UUID (None when audience is all)
        @param user_emails  - resolved list of recipient email addresses
        """
        self._publish(
            "marketing.campaign.sent",
            {
                "campaign_id": str(campaign_id),
                "subject": subject,
                "body": body,
                "org_id": str(org_id) if org_id else None,
                "segment_id": str(segment_id) if segment_id else None,
                "user_emails": user_emails,
            },
        )
