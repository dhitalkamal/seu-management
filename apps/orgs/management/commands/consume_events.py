"""Management command: management service RabbitMQ event consumer."""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def _parse_dt(val: str | None) -> datetime | None:
    """Parse an ISO datetime string or return None."""
    if not val:
        return None
    return datetime.fromisoformat(val)


def _handle_subscription_activated(payload: dict) -> None:
    """Update the org's plan when a subscription payment is confirmed."""
    from apps.orgs.application.use_cases.change_plan import ChangePlanUseCase
    from apps.orgs.infrastructure.repositories import DjangoOrgRepository

    org_id = payload.get("org_id", "")
    plan = payload.get("plan", "")
    expires_at = _parse_dt(payload.get("plan_expires_at"))

    if not org_id or not plan:
        logger.warning("subscription.activated missing org_id or plan: %s", payload)
        return

    try:
        ChangePlanUseCase(DjangoOrgRepository()).execute(
            org_id=uuid.UUID(org_id),
            plan=plan,
            plan_expires_at=expires_at,
        )
        logger.info("Plan updated: org=%s plan=%s expires=%s", org_id, plan, expires_at)
    except Exception:
        logger.exception("Failed to update plan for org %s", org_id)


def _handle_subscription_cancelled(payload: dict) -> None:
    """Revert the org back to the free plan when a subscription is cancelled."""
    from apps.orgs.application.use_cases.change_plan import ChangePlanUseCase
    from apps.orgs.infrastructure.repositories import DjangoOrgRepository

    org_id = payload.get("org_id", "")
    if not org_id:
        logger.warning("subscription.cancelled missing org_id: %s", payload)
        return

    try:
        ChangePlanUseCase(DjangoOrgRepository()).execute(
            org_id=uuid.UUID(org_id),
            plan="free",
            plan_expires_at=None,
        )
        logger.info("Plan reverted to free: org=%s", org_id)
    except Exception:
        logger.exception("Failed to revert plan for org %s", org_id)


# * routing key → handler function
_HANDLERS: dict[str, object] = {
    "subscription.activated": _handle_subscription_activated,
    "subscription.cancelled": _handle_subscription_cancelled,
}


class Command(BaseCommand):
    """
    Listen for domain events relevant to the management service.

    Handles subscription.activated and subscription.cancelled events
    from the payment service to keep org plans in sync.
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
            # * bind to management events and subscription events from payment service
            channel.queue_bind(queue="management.events", exchange="sansaar", routing_key="management.#")
            channel.queue_bind(queue="management.events", exchange="sansaar", routing_key="subscription.#")
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
        """Route events to their handler or log for observability."""
        try:
            payload = json.loads(body)
            routing_key = getattr(method, "routing_key", "")
            handler = _HANDLERS.get(routing_key)
            if handler:
                handler(payload)
            else:
                logger.info("Management event (unhandled): %s — %s", routing_key, payload)
        except Exception:
            logger.exception("Management consumer error processing message.")
