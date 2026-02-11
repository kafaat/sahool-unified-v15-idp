"""
SAHOOL Task Service - NATS Publisher
Publishes task-related events to NATS event bus

REFACTORED: Now uses shared EventPublisher for consistency across services
"""

import logging
from datetime import UTC, datetime, timezone
from typing import Any
from uuid import uuid4

# Use the shared EventPublisher from shared/events/
from shared.events.publisher import EventPublisher, PublisherConfig

logger = logging.getLogger(__name__)


class NatsPublisher:
    """
    NATS Event Publisher for Task Service

    This is an adapter that wraps the shared EventPublisher to provide
    backward-compatible API for the task-service.
    """

    def __init__(self, service_name: str = "task-service"):
        self._publisher: EventPublisher | None = None
        self._service_name = service_name
        self.connected = False

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS"""
        return self._publisher is not None and self._publisher.is_connected

    async def connect(self, nats_url: str) -> bool:
        """
        Connect to NATS server

        Args:
            nats_url: NATS server URL

        Returns:
            bool: Connection success status
        """
        try:
            config = PublisherConfig(
                servers=[nats_url],
                name=self._service_name,
            )
            self._publisher = EventPublisher(
                config=config,
                service_name=self._service_name,
            )
            success = await self._publisher.connect()
            self.connected = success
            if success:
                # Sanitize URL for logging
                safe_url = str(nats_url).replace("\n", "").replace("\r", "")
                logger.info("✅ NATS connected: %s", safe_url)
            return success
        except Exception as e:
            logger.error("❌ NATS connection failed: %s", type(e).__name__)
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS server"""
        if self._publisher:
            try:
                await self._publisher.close()
                self.connected = False
                logger.info("NATS disconnected")
            except Exception as e:
                logger.error("Error disconnecting from NATS: %s", type(e).__name__)

    async def publish_event(
        self,
        subject: str,
        event_type: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Publish event to NATS

        Args:
            subject: NATS subject/topic
            event_type: Type of event
            payload: Event data
            metadata: Additional metadata

        Returns:
            bool: Publish success status
        """
        if not self.is_connected:
            logger.warning(f"NATS not connected, skipping event publish: {event_type}")
            return False

        try:
            # Ensure subject has sahool. prefix for security compliance
            if not subject.startswith("sahool."):
                subject = f"sahool.{subject}"

            event = {
                "eventId": str(uuid4()),
                "eventType": event_type,
                "timestamp": datetime.now(UTC).isoformat(),
                "version": "1.0",
                "sourceService": self._service_name,
                "payload": payload,
                "metadata": metadata or {},
            }

            success = await self._publisher.publish_json(subject, event)

            if success:
                logger.info(f"📤 Event published: {event_type} to {subject}")
            return success

        except Exception as e:
            logger.error("Error publishing event %s: %s", event_type, type(e).__name__)
            return False


# Global publisher instance
_publisher: NatsPublisher | None = None


def get_publisher() -> NatsPublisher | None:
    """Get global NATS publisher instance"""
    return _publisher


def set_publisher(publisher: NatsPublisher):
    """Set global NATS publisher instance"""
    global _publisher
    _publisher = publisher


# ============================================================================
# Task Event Publishers
# ============================================================================


async def publish_task_created(
    task_id: str,
    tenant_id: str,
    task_type: str,
    priority: str,
    field_id: str | None = None,
    assigned_to: str | None = None,
    due_date: str | None = None,
) -> bool:
    """
    Publish task created event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        task_type: Type of task (irrigation, fertilization, etc.)
        priority: Task priority (low, medium, high, urgent)
        field_id: Field identifier
        assigned_to: User assigned to the task
        due_date: Task due date (ISO format)

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.created",
        event_type="task.created",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "taskType": task_type,
            "priority": priority,
            "fieldId": field_id,
            "assignedTo": assigned_to,
            "dueDate": due_date,
            "createdAt": datetime.now(UTC).isoformat(),
        },
    )


async def publish_task_updated(
    task_id: str,
    tenant_id: str,
    changes: dict[str, Any],
) -> bool:
    """
    Publish task updated event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        changes: Dictionary of changed fields

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.updated",
        event_type="task.updated",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "changes": changes,
            "updatedAt": datetime.now(UTC).isoformat(),
        },
    )


async def publish_task_assigned(
    task_id: str,
    tenant_id: str,
    assigned_to: str,
    assigned_by: str | None = None,
) -> bool:
    """
    Publish task assigned event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        assigned_to: User assigned to the task
        assigned_by: User who assigned the task

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.assigned",
        event_type="task.assigned",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "assignedTo": assigned_to,
            "assignedBy": assigned_by,
            "assignedAt": datetime.now(UTC).isoformat(),
        },
    )


async def publish_task_started(
    task_id: str,
    tenant_id: str,
    started_by: str,
) -> bool:
    """
    Publish task started event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        started_by: User who started the task

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.started",
        event_type="task.started",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "startedBy": started_by,
            "startedAt": datetime.now(UTC).isoformat(),
        },
    )


async def publish_task_completed(
    task_id: str,
    tenant_id: str,
    completed_by: str,
    actual_duration_minutes: int | None = None,
) -> bool:
    """
    Publish task completed event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        completed_by: User who completed the task
        actual_duration_minutes: Actual time taken to complete

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.completed",
        event_type="task.completed",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "completedBy": completed_by,
            "actualDurationMinutes": actual_duration_minutes,
            "completedAt": datetime.now(UTC).isoformat(),
        },
    )


async def publish_task_cancelled(
    task_id: str,
    tenant_id: str,
    cancelled_by: str,
    reason: str | None = None,
) -> bool:
    """
    Publish task cancelled event

    Args:
        task_id: Task identifier
        tenant_id: Tenant identifier
        cancelled_by: User who cancelled the task
        reason: Cancellation reason

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="sahool.task.cancelled",
        event_type="task.cancelled",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "cancelledBy": cancelled_by,
            "reason": reason,
            "cancelledAt": datetime.now(UTC).isoformat(),
        },
    )
