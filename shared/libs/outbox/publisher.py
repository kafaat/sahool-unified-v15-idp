"""
SAHOOL Outbox Publisher
Worker for publishing events from the outbox to message bus
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import OutboxEvent

logger = logging.getLogger(__name__)


class EventBusClient(ABC):
    """
    Abstract base class for event bus clients.

    Implement this interface to connect to different message brokers:
    - NATS JetStream
    - Kafka
    - RabbitMQ
    - AWS SNS/SQS
    """

    @abstractmethod
    def publish(self, topic: str, message: str) -> None:
        """
        Publish a message to the event bus.

        Args:
            topic: Topic/subject to publish to
            message: JSON message to publish

        Raises:
            Exception: If publishing fails
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the event bus"""
        pass


class LoggingEventBusClient(EventBusClient):
    """
    Simple event bus client that logs events.
    Useful for development and testing.
    """

    def publish(self, topic: str, message: str) -> None:
        logger.info(f"[EVENT] topic={topic} message={message[:200]}...")

    def close(self) -> None:
        pass


def publish_pending(
    db: Session,
    bus: EventBusClient,
    batch_size: int = 100,
    max_retries: int = 3,
) -> int:
    """
    Publish pending events from the outbox.

    Args:
        db: SQLAlchemy session
        bus: Event bus client
        batch_size: Number of events to process per batch
        max_retries: Maximum retry attempts before giving up

    Returns:
        Number of events successfully published
    """
    # Select unpublished events, ordered by creation time
    stmt = (
        select(OutboxEvent)
        .where(OutboxEvent.published.is_(False))
        .where(OutboxEvent.retry_count < max_retries)
        .order_by(OutboxEvent.created_at.asc())
        .limit(batch_size)
    )
    events = list(db.execute(stmt).scalars())

    published_count = 0

    for event in events:
        try:
            # Publish to bus
            bus.publish(event.event_type, event.payload_json)

            # Mark as published
            event.published = True
            event.published_at = datetime.now(UTC)
            event.last_error = None

            published_count += 1
            logger.info(f"Published event {event.id} to {event.event_type}")

        except Exception as e:
            # Record failure
            event.retry_count += 1
            event.last_error = str(e)
            logger.error(
                f"Failed to publish event {event.id}: {e} "
                f"(attempt {event.retry_count}/{max_retries})"
            )

    return published_count


def get_pending_count(db: Session) -> int:
    """Get count of unpublished events"""
    stmt = select(OutboxEvent).where(OutboxEvent.published.is_(False))
    result = db.execute(stmt)
    return len(list(result.scalars()))


def get_failed_events(
    db: Session,
    max_retries: int = 3,
    limit: int = 100,
) -> list[OutboxEvent]:
    """Get events that have exceeded retry limit"""
    stmt = (
        select(OutboxEvent)
        .where(OutboxEvent.published.is_(False))
        .where(OutboxEvent.retry_count >= max_retries)
        .order_by(OutboxEvent.created_at.asc())
        .limit(limit)
    )
    return list(db.execute(stmt).scalars())


def retry_failed_events(db: Session, event_ids: list[str]) -> int:
    """Reset retry count for failed events to allow re-processing"""
    count = 0
    for event_id in event_ids:
        stmt = select(OutboxEvent).where(OutboxEvent.id == event_id)
        event = db.execute(stmt).scalar_one_or_none()
        if event:
            event.retry_count = 0
            event.last_error = None
            count += 1
    return count
