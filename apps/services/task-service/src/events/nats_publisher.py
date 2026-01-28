"""
SAHOOL Task Service - NATS Publisher
Publishes task-related events to NATS event bus
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

import nats
from nats.aio.client import Client as NatsClient

logger = logging.getLogger(__name__)


class NatsPublisher:
    """NATS Event Publisher for Task Service"""

    def __init__(self):
        self.nc: NatsClient | None = None
        self.connected = False

    async def connect(self, nats_url: str) -> bool:
        """
        Connect to NATS server

        Args:
            nats_url: NATS server URL

        Returns:
            bool: Connection success status
        """
        try:
            self.nc = await nats.connect(nats_url)
            self.connected = True
            logger.info(f"✅ NATS connected: {nats_url}")
            return True
        except Exception as e:
            logger.error(f"❌ NATS connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS server"""
        if self.nc and self.connected:
            try:
                await self.nc.close()
                self.connected = False
                logger.info("NATS disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from NATS: {e}")

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
        if not self.nc or not self.connected:
            logger.warning(f"NATS not connected, skipping event publish: {event_type}")
            return False

        try:
            event = {
                "eventId": str(uuid4()),
                "eventType": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "payload": payload,
                "metadata": metadata or {},
            }

            message = json.dumps(event).encode()
            await self.nc.publish(subject, message)

            logger.info(f"📤 Event published: {event_type} to {subject}")
            return True

        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
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
        subject="task.created",
        event_type="task.created",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "taskType": task_type,
            "priority": priority,
            "fieldId": field_id,
            "assignedTo": assigned_to,
            "dueDate": due_date,
            "createdAt": datetime.utcnow().isoformat(),
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
        subject="task.updated",
        event_type="task.updated",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "changes": changes,
            "updatedAt": datetime.utcnow().isoformat(),
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
        subject="task.assigned",
        event_type="task.assigned",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "assignedTo": assigned_to,
            "assignedBy": assigned_by,
            "assignedAt": datetime.utcnow().isoformat(),
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
        subject="task.started",
        event_type="task.started",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "startedBy": started_by,
            "startedAt": datetime.utcnow().isoformat(),
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
        subject="task.completed",
        event_type="task.completed",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "completedBy": completed_by,
            "actualDurationMinutes": actual_duration_minutes,
            "completedAt": datetime.utcnow().isoformat(),
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
        subject="task.cancelled",
        event_type="task.cancelled",
        payload={
            "taskId": task_id,
            "tenantId": tenant_id,
            "cancelledBy": cancelled_by,
            "reason": reason,
            "cancelledAt": datetime.utcnow().isoformat(),
        },
    )
