"""
Example: NATS Consumer with Dead Letter Queue

This example shows how to implement a NATS consumer service
that automatically routes failed messages to a DLQ after retries.

Usage:
    python consumer_example.py
"""

import asyncio
import json
import logging
from typing import Optional

# Import NATS consumer components
from shared.libs.events import (
    NATSConsumer,
    NATSConsumerConfig,
    ConsumerContext,
    ProcessingResult,
    CONSUMER_AVAILABLE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_ndvi_event(ctx: ConsumerContext) -> ProcessingResult:
    """
    Process NDVI analysis events

    This handler demonstrates:
    - Successful processing
    - Retry on transient failures
    - DLQ routing on critical failures
    """
    try:
        # Parse event data
        event = json.loads(ctx.data.decode('utf-8'))

        logger.info(
            f"Processing NDVI event: "
            f"field_id={event.get('field_id')}, "
            f"attempt={ctx.attempt + 1}/{ctx.max_retries + 1}"
        )

        # Extract event data
        field_id = event.get('field_id')
        ndvi_value = event.get('data', {}).get('ndvi_value')

        if not field_id or ndvi_value is None:
            logger.error("Invalid event data - missing required fields")
            # Return DEAD_LETTER for validation errors (no point retrying)
            return ProcessingResult.DEAD_LETTER

        # Simulate processing
        # In real implementation: store in database, trigger notifications, etc.
        logger.info(f"NDVI value for field {field_id}: {ndvi_value}")

        # Simulate transient failure (database connection issue)
        if ctx.attempt == 0 and field_id == "transient-fail":
            logger.warning("Simulating transient failure - will retry")
            return ProcessingResult.RETRY

        # Simulate permanent failure (validation error)
        if field_id == "invalid-field":
            raise ValueError("Invalid field_id format")

        # Success!
        logger.info(f"✅ Successfully processed NDVI event for field {field_id}")
        return ProcessingResult.SUCCESS

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse event JSON: {e}")
        # JSON errors won't be fixed by retry
        return ProcessingResult.DEAD_LETTER

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        # Validation errors go straight to DLQ
        return ProcessingResult.DEAD_LETTER

    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)
        # Unknown errors - retry before DLQ
        return ProcessingResult.RETRY


async def process_irrigation_event(ctx: ConsumerContext) -> ProcessingResult:
    """Process irrigation recommendation events"""
    try:
        event = json.loads(ctx.data.decode('utf-8'))

        logger.info(
            f"Processing irrigation event: "
            f"field_id={event.get('field_id')}, "
            f"recommendation={event.get('data', {}).get('action')}"
        )

        # Process irrigation recommendation
        # In real implementation: update irrigation schedule, send to IoT devices, etc.

        return ProcessingResult.SUCCESS

    except Exception as e:
        logger.error(f"Error processing irrigation event: {e}", exc_info=True)
        return ProcessingResult.RETRY


async def main():
    """
    Main function to start NATS consumers with DLQ support
    """
    if not CONSUMER_AVAILABLE:
        logger.error("NATS consumer not available. Install nats-py: pip install nats-py")
        return

    # Configure NATS consumer
    config = NATSConsumerConfig(
        servers=["nats://localhost:4222"],
        name="sahool-analysis-consumer",
        stream_name="SAHOOL_EVENTS",
        consumer_name="analysis-consumer",
        subject_filter="sahool.analysis.*",
        # Retry configuration
        max_retries=3,
        retry_delay_seconds=5,
        exponential_backoff=True,
        # DLQ configuration
        dlq_enabled=True,
        dlq_subject_prefix="sahool.dlq",
    )

    # Create consumer
    consumer = NATSConsumer(config)

    # Connect to NATS
    connected = await consumer.connect()
    if not connected:
        logger.error("Failed to connect to NATS")
        return

    logger.info("✅ Connected to NATS")

    # Subscribe to analysis events
    await consumer.subscribe(
        handler=process_ndvi_event,
        subject="sahool.analysis.ndvi_computed",
    )

    await consumer.subscribe(
        handler=process_irrigation_event,
        subject="sahool.analysis.irrigation_recommended",
    )

    logger.info("🚀 Consumer started - listening for events...")

    try:
        # Start consuming
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await consumer.close()


if __name__ == "__main__":
    asyncio.run(main())
