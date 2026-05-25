"""RabbitMQ event publisher for volunteer domain events."""

from __future__ import annotations

import json

from apps.volunteers.domain.repositories import IEventPublisher


class RabbitMQEventPublisher(IEventPublisher):
    """Publishes domain events to a RabbitMQ topic exchange."""

    def __init__(self, connection_url: str, exchange: str = "sansaar.events") -> None:
        import pika  # type: ignore[import-untyped]

        self._exchange = exchange
        params = pika.URLParameters(connection_url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

    def publish(self, event_type: str, payload: dict) -> None:
        """Publish a JSON message with the event_type as routing key."""
        import pika  # type: ignore[import-untyped]

        body = json.dumps({"type": event_type, "data": payload}).encode()
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=event_type,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
