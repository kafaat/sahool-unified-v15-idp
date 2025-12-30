"""
Example: DLQ Monitoring Service

This example shows how to implement a DLQ monitoring service
that tracks failed events and stores them in a database.

Usage:
    python dlq_monitor_example.py
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

# Import DLQ consumer components
from shared.libs.events import (
    DLQConsumer,
    DLQConsumerConfig,
    DLQEvent,
    DLQAction,
    start_dlq_consumer,
    DLQ_AVAILABLE,
    FailedEventModel,
    DLQ_MODELS_AVAILABLE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def store_failed_event_in_db(event: DLQEvent):
    """
    Store failed event in database for analysis

    In production, this would use your actual database connection
    """
    if not DLQ_MODELS_AVAILABLE:
        logger.warning("DLQ models not available - skipping database storage")
        return

    try:
        # Example: Create database record
        # In production, use your actual database session
        logger.info(f"📦 Storing failed event in database: {event.event_id}")

        # Example code (requires database setup):
        # async with db.session() as session:
        #     failed_event = FailedEventModel.from_dlq_event(event)
        #     session.add(failed_event)
        #     await session.commit()

        # For now, just log the event details
        logger.info(
            f"Failed Event Details:\n"
            f"  Event ID: {event.event_id}\n"
            f"  Event Type: {event.event_type}\n"
            f"  Source Service: {event.source_service}\n"
            f"  Error Type: {event.error_type}\n"
            f"  Error Message: {event.error_message}\n"
            f"  Retry Count: {event.retry_count}/{event.max_retries}\n"
            f"  Field ID: {event.field_id}\n"
            f"  Farmer ID: {event.farmer_id}\n"
            f"  DLQ Timestamp: {event.dlq_timestamp}\n"
        )

    except Exception as e:
        logger.error(f"Failed to store event in database: {e}", exc_info=True)


async def send_critical_alert(event: DLQEvent):
    """
    Send alert for critical failures

    In production, this would integrate with:
    - Slack
    - PagerDuty
    - Email
    - SMS
    """
    logger.error(
        f"🚨 CRITICAL ALERT: DLQ Event\n"
        f"Event ID: {event.event_id}\n"
        f"Event Type: {event.event_type}\n"
        f"Error: {event.error_message}\n"
        f"Service: {event.source_service}\n"
    )

    # Example: Send Slack alert
    # await slack_client.send_message(
    #     channel="#alerts",
    #     message=f"🚨 DLQ Event: {event.event_type}\n"
    #             f"Error: {event.error_message}\n"
    #             f"Service: {event.source_service}"
    # )


async def custom_dlq_handler(event: DLQEvent) -> DLQAction:
    """
    Custom DLQ event handler with business logic

    This handler demonstrates different actions based on error type:
    - Store validation errors for review
    - Retry transient errors after delay
    - Alert on critical errors
    - Discard duplicate events
    """
    logger.warning(
        f"💀 DLQ Event received: {event.event_type} "
        f"(event_id={event.event_id}, error={event.error_type})"
    )

    # Store all failed events for analysis
    await store_failed_event_in_db(event)

    # Critical errors - alert immediately
    critical_errors = [
        "DatabaseError",
        "AuthenticationError",
        "PermissionError",
    ]

    if event.error_type in critical_errors:
        await send_critical_alert(event)
        return DLQAction.ALERT

    # Validation errors - store for manual review
    validation_errors = [
        "ValidationError",
        "ValueError",
        "JSONDecodeError",
    ]

    if event.error_type in validation_errors:
        logger.info(f"Validation error stored for manual review: {event.event_id}")
        return DLQAction.STORE

    # Transient errors - could retry later
    # (with auto-retry feature, this could be scheduled)
    transient_errors = [
        "ConnectionError",
        "TimeoutError",
        "ServiceUnavailable",
    ]

    if event.error_type in transient_errors:
        # Check if we've already retried this event from DLQ
        if event.retry_count < event.max_retries + 2:  # Allow 2 more retries from DLQ
            logger.info(f"Transient error - scheduling retry: {event.event_id}")
            # In production, schedule a delayed retry
            # await schedule_retry(event, delay_hours=1)
            return DLQAction.RETRY
        else:
            logger.warning(f"Max DLQ retries exceeded for {event.event_id}")
            return DLQAction.STORE

    # Unknown errors - store and monitor
    logger.warning(f"Unknown error type: {event.error_type}")
    return DLQAction.STORE


async def main():
    """
    Main function to start DLQ monitoring service
    """
    if not DLQ_AVAILABLE:
        logger.error("DLQ consumer not available. Install nats-py: pip install nats-py")
        return

    logger.info("🚀 Starting DLQ Monitoring Service...")

    # Configure DLQ consumer
    config = DLQConsumerConfig(
        servers=["nats://localhost:4222"],
        name="sahool-dlq-monitor",
        dlq_subject="sahool.dlq.>",  # Subscribe to all DLQ subjects
        store_in_db=True,
        alert_on_critical=True,
        critical_error_types=[
            "DatabaseError",
            "AuthenticationError",
            "PermissionError",
        ],
    )

    # Start DLQ consumer with custom handler
    consumer = await start_dlq_consumer(
        handler=custom_dlq_handler,
        config=config,
    )

    logger.info("✅ DLQ Monitoring Service started")
    logger.info("📥 Listening for failed events on sahool.dlq.>")

    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
