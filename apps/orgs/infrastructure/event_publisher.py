"""RabbitMQ event publisher for org membership domain events."""

from __future__ import annotations

import json
import logging
import uuid

import pika
from django.conf import settings

logger = logging.getLogger(__name__)

# exchange name matches the rest of the sansaar platform
_EXCHANGE = "sansaar"
_EXCHANGE_TYPE = "topic"


class OrgEventPublisher:
    """Publishes org.member.* events to the sansaar topic exchange."""

    def _publish(self, routing_key: str, payload: dict) -> None:
        """
        Open a fresh connection, declare the exchange, publish the message, then close.

        Fresh connection per publish -- acceptable for low-frequency membership events.
        If RabbitMQ is unavailable the failure is logged and swallowed so the
        caller's DB transaction is not rolled back.

        @param routing_key - the topic routing key, e.g. "org.member.added"
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
            # ! do not block the caller -- RabbitMQ is observability infrastructure,
            # not part of the primary write path
            logger.warning(
                "Failed to publish %s to RabbitMQ.",
                routing_key,
                exc_info=True,
            )

    def publish_member_added(
        self,
        *,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
    ) -> None:
        """
        Publish an org.member.added event after a new membership is created.

        @param org_id  - the organisation the user joined
        @param user_id - the user who was added
        @param role    - the role assigned (owner | admin | manager | member)
        """
        self._publish(
            "org.member.added",
            {
                "org_id": str(org_id),
                "user_id": str(user_id),
                "role": role,
            },
        )

    def publish_member_removed(
        self,
        *,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Publish an org.member.removed event after a membership is deactivated.

        @param org_id  - the organisation the user left
        @param user_id - the user who was removed
        """
        self._publish(
            "org.member.removed",
            {
                "org_id": str(org_id),
                "user_id": str(user_id),
            },
        )

    def publish_member_role_changed(
        self,
        *,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        old_role: str,
        new_role: str,
    ) -> None:
        """
        Publish an org.member.role_changed event after a member's role is updated.

        @param org_id   - the organisation the change occurred in
        @param user_id  - the user whose role changed
        @param old_role - the previous role value
        @param new_role - the new role value
        """
        self._publish(
            "org.member.role_changed",
            {
                "org_id": str(org_id),
                "user_id": str(user_id),
                "old_role": old_role,
                "new_role": new_role,
            },
        )
