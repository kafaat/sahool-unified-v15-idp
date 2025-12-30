"""
Simple Test: DLQ System End-to-End

This script demonstrates and tests the complete DLQ flow:
1. Publish test events to NATS
2. Consumer processes events (some succeed, some fail)
3. Failed events route to DLQ after retries
4. DLQ consumer monitors and stores failures

Usage:
    # Start NATS server first:
    docker run -p 4222:4222 nats:latest -js

    # Run test:
    python simple_test.py
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from shared.libs.events import (
    NATSPublisher,
    NATSConfig,
    NATSConsumer,
    NATSConsumerConfig,
    ConsumerContext,
    ProcessingResult,
    DLQConsumer,
    DLQConsumerConfig,
    DLQEvent,
    DLQAction,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.success_count = 0
        self.retry_count = 0
        self.dlq_count = 0
        self.dlq_events = []


results = TestResults()


async def test_publisher():
    """Publish test events to NATS"""
    logger.info("=" * 60)
    logger.info("STEP 1: Publishing test events")
    logger.info("=" * 60)

    config = NATSConfig(servers=["nats://localhost:4222"])
    publisher = NATSPublisher(config)

    connected = await publisher.connect()
    if not connected:
        logger.error("Failed to connect publisher")
        return False

    # Test events
    test_events = [
        {
            "name": "Success Event",
            "subject": "sahool.analysis.ndvi_computed",
            "data": {
                "event_id": "event-1",
                "event_type": "ndvi.computed",
                "source_service": "test-service",
                "field_id": "field-success",
                "data": {"ndvi_value": 0.75},
            }
        },
        {
            "name": "Retry Event",
            "subject": "sahool.analysis.ndvi_computed",
            "data": {
                "event_id": "event-2",
                "event_type": "ndvi.computed",
                "source_service": "test-service",
                "field_id": "field-retry",
                "data": {"ndvi_value": 0.65},
            }
        },
        {
            "name": "DLQ Event (Invalid)",
            "subject": "sahool.analysis.ndvi_computed",
            "data": {
                "event_id": "event-3",
                "event_type": "ndvi.computed",
                "source_service": "test-service",
                "field_id": "field-invalid",
                # Missing required data
            }
        },
    ]

    for event in test_events:
        data = json.dumps(event["data"]).encode('utf-8')
        success = await publisher.publish(event["subject"], data)
        if success:
            logger.info(f"✅ Published: {event['name']}")
        else:
            logger.error(f"❌ Failed to publish: {event['name']}")

    await publisher.close()
    logger.info("")
    return True


async def test_consumer_handler(ctx: ConsumerContext) -> ProcessingResult:
    """Test consumer handler with different behaviors"""
    try:
        event = json.loads(ctx.data.decode('utf-8'))
        field_id = event.get('field_id')

        logger.info(f"Processing event: field_id={field_id}, attempt={ctx.attempt + 1}")

        # Success case
        if field_id == "field-success":
            logger.info(f"  ✅ Success: {field_id}")
            results.success_count += 1
            return ProcessingResult.SUCCESS

        # Retry case (will retry 3 times then go to DLQ)
        if field_id == "field-retry":
            results.retry_count += 1
            logger.warning(f"  ⚠️  Retry: {field_id} (attempt {ctx.attempt + 1})")
            return ProcessingResult.RETRY

        # Invalid data - straight to DLQ
        if field_id == "field-invalid" or 'data' not in event:
            logger.error(f"  ❌ Invalid data: {field_id}")
            return ProcessingResult.DEAD_LETTER

        return ProcessingResult.SUCCESS

    except json.JSONDecodeError as e:
        logger.error(f"  ❌ JSON decode error: {e}")
        return ProcessingResult.DEAD_LETTER
    except Exception as e:
        logger.error(f"  ❌ Unexpected error: {e}")
        return ProcessingResult.RETRY


async def test_dlq_handler(event: DLQEvent) -> DLQAction:
    """Test DLQ handler"""
    logger.info(
        f"DLQ Event received: "
        f"event_id={event.event_id}, "
        f"field_id={event.field_id}, "
        f"error={event.error_type}, "
        f"retries={event.retry_count}"
    )

    results.dlq_count += 1
    results.dlq_events.append(event)

    return DLQAction.STORE


async def run_consumer_test():
    """Run consumer test"""
    logger.info("=" * 60)
    logger.info("STEP 2: Starting consumer with DLQ support")
    logger.info("=" * 60)

    config = NATSConsumerConfig(
        servers=["nats://localhost:4222"],
        stream_name="SAHOOL_EVENTS",
        consumer_name="test-consumer",
        subject_filter="sahool.analysis.*",
        max_retries=2,  # Retry 2 times before DLQ
        retry_delay_seconds=1,
        exponential_backoff=False,
        dlq_enabled=True,
    )

    consumer = NATSConsumer(config)
    connected = await consumer.connect()

    if not connected:
        logger.error("Failed to connect consumer")
        return False

    await consumer.subscribe(test_consumer_handler)

    logger.info("✅ Consumer started")
    logger.info("")

    # Process messages for 15 seconds
    try:
        task = asyncio.create_task(consumer.start())
        await asyncio.sleep(15)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    finally:
        await consumer.close()

    return True


async def run_dlq_consumer_test():
    """Run DLQ consumer test"""
    logger.info("=" * 60)
    logger.info("STEP 3: Starting DLQ consumer")
    logger.info("=" * 60)

    config = DLQConsumerConfig(
        servers=["nats://localhost:4222"],
        dlq_subject="sahool.dlq.>",
    )

    consumer = DLQConsumer(config)
    connected = await consumer.connect()

    if not connected:
        logger.error("Failed to connect DLQ consumer")
        return False

    await consumer.subscribe(test_dlq_handler)

    logger.info("✅ DLQ Consumer started")
    logger.info("")

    # Monitor DLQ for 10 seconds
    try:
        task = asyncio.create_task(consumer.start())
        await asyncio.sleep(10)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    finally:
        await consumer.close()

    return True


async def main():
    """Main test function"""
    logger.info("")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "DLQ SYSTEM TEST" + " " * 28 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    try:
        # Step 1: Publish test events
        await test_publisher()
        await asyncio.sleep(2)

        # Step 2: Start consumer (processes events, some go to DLQ)
        await run_consumer_test()
        await asyncio.sleep(2)

        # Step 3: Start DLQ consumer (monitors DLQ)
        await run_dlq_consumer_test()

        # Print results
        logger.info("")
        logger.info("=" * 60)
        logger.info("TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Successful processes: {results.success_count}")
        logger.info(f"🔄 Retry attempts: {results.retry_count}")
        logger.info(f"💀 DLQ events: {results.dlq_count}")
        logger.info("")

        if results.dlq_count > 0:
            logger.info("DLQ Events Details:")
            for i, event in enumerate(results.dlq_events, 1):
                logger.info(f"  {i}. Event ID: {event.event_id}")
                logger.info(f"     Field ID: {event.field_id}")
                logger.info(f"     Error: {event.error_type} - {event.error_message}")
                logger.info(f"     Retries: {event.retry_count}/{event.max_retries}")
                logger.info("")

        logger.info("=" * 60)
        logger.info("✅ TEST COMPLETED")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\nTest interrupted")
    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
