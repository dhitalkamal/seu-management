"""Management command: management service RabbitMQ event consumer."""

from __future__ import annotations

import json
import logging
import os

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Listen for domain events relevant to the management service.

    Currently handles:
    - volunteer.certificate.issued events (future extension point)
    - Stays connected for observability and future integrations
    """

    help = "Management service RabbitMQ consumer."

    def handle(self, *args: object, **options: object) -> None:
        """Connect to RabbitMQ and consume management-relevant events."""
        import pika

        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.stdout.write("Management consumer started.")
        try:
            params = pika.URLParameters(rabbitmq_url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(exchange="sansaar", exchange_type="topic", durable=True)
            channel.queue_declare(queue="management.events", durable=True)
            channel.queue_bind(
                queue="management.events", exchange="sansaar", routing_key="management.#"
            )
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue="management.events",
                on_message_callback=self._handle,
                auto_ack=True,
            )
            channel.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write("Management consumer stopped.")
        except Exception:
            logger.exception("Management consumer error.")

    @staticmethod
    def _handle(channel: object, method: object, props: object, body: bytes) -> None:
        """Log management events for observability."""
        try:
            payload = json.loads(body)
            logger.info("Management event received: %s", payload.get("event_type", "unknown"))
        except Exception:
            logger.warning("Management consumer received non-JSON message.")
