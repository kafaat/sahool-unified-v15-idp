"""
Idempotency Usage Examples
===========================

Practical examples showing how to use idempotency in SAHOOL event processing.
"""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from shared.libs.events import (
    EventEnvelope,
    idempotent_event_handler,
    IdempotentEventProcessor,
    get_idempotency_checker,
    DuplicateEventError,
    ProcessingStatus,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Example 1: Simple Decorator Pattern (Recommended)
# ═══════════════════════════════════════════════════════════════════════════════


@idempotent_event_handler()
def handle_field_created(envelope: EventEnvelope) -> dict:
    """
    Process field.created event with automatic idempotency.

    The decorator handles:
    - Duplicate detection
    - Result caching
    - Error handling
    - Concurrent processing prevention
    """
    print(f"Processing field.created event: {envelope.event_id}")

    # Extract payload
    field_id = envelope.payload["field_id"]
    farm_id = envelope.payload["farm_id"]
    name = envelope.payload["name"]

    # Simulate database operation (this only runs once)
    print(f"Creating field in database: {field_id}")
    # create_field_in_db(field_id, farm_id, name)

    # Return result (will be cached for replay)
    return {
        "status": "created",
        "field_id": field_id,
        "timestamp": datetime.utcnow().isoformat()
    }


def example_simple_decorator():
    """Example: Simple decorator usage"""
    print("\n" + "="*80)
    print("Example 1: Simple Decorator Pattern")
    print("="*80)

    # Create event envelope
    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="field.created",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.field.created:v1",
        producer="field-service",
        payload={
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "name": "Test Field"
        },
        idempotency_key="field-create-123"  # Custom idempotency key
    )

    # First call - processes event
    print("\n1️⃣ First call (should process):")
    result1 = handle_field_created(envelope)
    print(f"Result: {result1}")

    # Second call - returns cached result
    print("\n2️⃣ Second call (should return cached result):")
    result2 = handle_field_created(envelope)
    print(f"Result: {result2}")
    print(f"Results match: {result1 == result2}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 2: Decorator with Error Raising on Duplicate
# ═══════════════════════════════════════════════════════════════════════════════


@idempotent_event_handler(
    skip_on_duplicate=False,  # Raise error instead of skipping
    ttl_seconds=3600  # 1 hour TTL
)
def handle_payment_charged(envelope: EventEnvelope) -> dict:
    """
    Process payment.charged event.
    Raises DuplicateEventError if event was already processed.
    """
    print(f"Processing payment: {envelope.event_id}")

    payment_id = envelope.payload["payment_id"]
    amount = envelope.payload["amount"]

    # Process payment (critical operation)
    print(f"Charging payment: {payment_id} for {amount}")

    return {
        "status": "charged",
        "payment_id": payment_id,
        "amount": amount,
        "transaction_id": str(uuid4())
    }


def example_error_on_duplicate():
    """Example: Raise error on duplicate"""
    print("\n" + "="*80)
    print("Example 2: Error on Duplicate")
    print("="*80)

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="payment.charged",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.payment.charged:v1",
        producer="payment-service",
        payload={
            "payment_id": str(uuid4()),
            "amount": 100.00,
            "currency": "SAR"
        },
        idempotency_key="payment-charge-456"
    )

    # First call - processes
    print("\n1️⃣ First call:")
    result1 = handle_payment_charged(envelope)
    print(f"Result: {result1}")

    # Second call - raises error
    print("\n2️⃣ Second call (should raise DuplicateEventError):")
    try:
        result2 = handle_payment_charged(envelope)
    except DuplicateEventError as e:
        print(f"Caught DuplicateEventError: {e}")
        print(f"Cached result: {e.cached_result}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 3: Context Manager Pattern
# ═══════════════════════════════════════════════════════════════════════════════


def handle_order_completed_with_context(envelope: EventEnvelope) -> dict:
    """
    Process order.completed event using context manager.
    Provides more control over the idempotency flow.
    """
    processor = IdempotentEventProcessor()

    with processor.process(envelope) as ctx:
        # Check if duplicate
        if ctx.is_duplicate:
            print(f"Duplicate detected! Returning cached result.")
            return ctx.cached_result

        # Process event
        print(f"Processing order completion: {envelope.event_id}")

        order_id = envelope.payload["order_id"]
        total = envelope.payload["total"]

        # Simulate processing
        print(f"Finalizing order {order_id} with total {total}")

        result = {
            "status": "completed",
            "order_id": order_id,
            "confirmation": str(uuid4())
        }

        # Mark as completed
        ctx.mark_completed(result)

        return result


def example_context_manager():
    """Example: Context manager usage"""
    print("\n" + "="*80)
    print("Example 3: Context Manager Pattern")
    print("="*80)

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="order.completed",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.order.completed:v1",
        producer="order-service",
        payload={
            "order_id": str(uuid4()),
            "total": 250.00
        },
        idempotency_key="order-complete-789"
    )

    # First call
    print("\n1️⃣ First call:")
    result1 = handle_order_completed_with_context(envelope)
    print(f"Result: {result1}")

    # Second call
    print("\n2️⃣ Second call:")
    result2 = handle_order_completed_with_context(envelope)
    print(f"Result: {result2}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 4: Manual Idempotency Control
# ═══════════════════════════════════════════════════════════════════════════════


def handle_inventory_updated_manual(envelope: EventEnvelope) -> dict:
    """
    Process inventory.updated event with manual idempotency control.
    Useful for advanced scenarios.
    """
    checker = get_idempotency_checker()

    # Get idempotency key
    key = checker.get_or_create_idempotency_key(
        envelope.event_id,
        envelope.idempotency_key
    )

    print(f"Processing with idempotency key: {key}")

    # Check for duplicate
    is_dup, record = checker.is_duplicate(key)

    if is_dup and record:
        if record.status == ProcessingStatus.COMPLETED:
            print("Event already processed, returning cached result")
            return record.result
        elif record.status == ProcessingStatus.PROCESSING:
            print("Event is being processed by another instance")
            return {"status": "processing"}

    # Mark as processing (atomic operation)
    success = checker.mark_processing(
        key,
        envelope.event_id,
        envelope.event_type
    )

    if not success:
        print("Lost race to process event")
        return {"status": "concurrent_processing"}

    try:
        # Process event
        print(f"Updating inventory: {envelope.payload['product_id']}")

        result = {
            "status": "updated",
            "product_id": envelope.payload["product_id"],
            "new_quantity": envelope.payload["quantity"]
        }

        # Mark as completed
        checker.mark_completed(key, result)

        return result

    except Exception as e:
        # Mark as failed
        checker.mark_failed(key, str(e))
        raise


def example_manual_control():
    """Example: Manual idempotency control"""
    print("\n" + "="*80)
    print("Example 4: Manual Idempotency Control")
    print("="*80)

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="inventory.updated",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.inventory.updated:v1",
        producer="inventory-service",
        payload={
            "product_id": str(uuid4()),
            "quantity": 100
        },
        idempotency_key="inventory-update-abc"
    )

    # First call
    print("\n1️⃣ First call:")
    result1 = handle_inventory_updated_manual(envelope)
    print(f"Result: {result1}")

    # Second call
    print("\n2️⃣ Second call:")
    result2 = handle_inventory_updated_manual(envelope)
    print(f"Result: {result2}")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 5: NATS Integration with Idempotency
# ═══════════════════════════════════════════════════════════════════════════════


@idempotent_event_handler()
async def handle_crop_planted_async(envelope: EventEnvelope) -> dict:
    """
    Async event handler with idempotency.
    Perfect for NATS message handlers.
    """
    print(f"Processing crop.planted event: {envelope.event_id}")

    field_id = envelope.payload["field_id"]
    crop_type = envelope.payload["crop_type"]

    # Simulate async database operation
    await asyncio.sleep(0.1)
    print(f"Recorded crop planting: {crop_type} in field {field_id}")

    return {
        "status": "planted",
        "field_id": field_id,
        "crop_type": crop_type,
        "planting_date": datetime.utcnow().isoformat()
    }


async def nats_message_handler_example(msg_data: bytes):
    """
    Example NATS message handler with idempotency.

    This shows how you'd integrate idempotency in a NATS consumer.
    """
    # Parse event envelope
    envelope = EventEnvelope.model_validate_json(msg_data)

    # Process with idempotency
    result = await handle_crop_planted_async(envelope)

    print(f"Event processed: {result}")

    # In real NATS, you'd acknowledge here
    # await msg.ack()


async def example_nats_integration():
    """Example: NATS integration"""
    print("\n" + "="*80)
    print("Example 5: NATS Integration with Idempotency")
    print("="*80)

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="crop.planted",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.crop.planted:v1",
        producer="crop-service",
        payload={
            "field_id": str(uuid4()),
            "crop_type": "Wheat",
            "planting_date": datetime.utcnow().isoformat()
        },
        idempotency_key=f"crop-plant-{uuid4()}"
    )

    # Simulate NATS message
    msg_data = envelope.model_dump_json().encode()

    # First message
    print("\n1️⃣ First message:")
    await nats_message_handler_example(msg_data)

    # Duplicate message (network retry, etc.)
    print("\n2️⃣ Duplicate message:")
    await nats_message_handler_example(msg_data)


# ═══════════════════════════════════════════════════════════════════════════════
# Example 6: Error Handling and Retry
# ═══════════════════════════════════════════════════════════════════════════════


@idempotent_event_handler()
def handle_event_with_retry(envelope: EventEnvelope) -> dict:
    """
    Event handler that might fail.
    Failed events are not considered duplicates and can be retried.
    """
    print(f"Processing event: {envelope.event_id}")

    # Simulate random failure
    import random
    if random.random() < 0.5:
        raise Exception("Processing failed (simulated error)")

    return {"status": "success"}


def example_error_handling():
    """Example: Error handling and retry"""
    print("\n" + "="*80)
    print("Example 6: Error Handling and Retry")
    print("="*80)

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="test.event",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.test:v1",
        producer="test-service",
        payload={"test": "data"},
        idempotency_key="test-retry-123"
    )

    checker = get_idempotency_checker()
    key = envelope.idempotency_key

    # Try processing
    for attempt in range(3):
        print(f"\n🔄 Attempt {attempt + 1}:")

        try:
            result = handle_event_with_retry(envelope)
            print(f"✅ Success: {result}")
            break
        except Exception as e:
            print(f"❌ Failed: {e}")

            # Check if marked as failed
            record = checker.get_processing_record(key)
            if record and record.status == ProcessingStatus.FAILED:
                print("Event marked as FAILED in Redis")

                # Delete failed record to allow retry
                print("Deleting failed record to allow retry...")
                checker.delete_record(key)


# ═══════════════════════════════════════════════════════════════════════════════
# Example 7: Custom Idempotency Keys
# ═══════════════════════════════════════════════════════════════════════════════


def create_business_idempotency_key(tenant_id: str, operation: str, resource_id: str) -> str:
    """
    Create business-meaningful idempotency key.

    Best practice: Include business identifiers in the key.
    """
    return f"{tenant_id}:{operation}:{resource_id}"


@idempotent_event_handler()
def handle_with_business_key(envelope: EventEnvelope) -> dict:
    """Process event with business-meaningful idempotency key"""
    print(f"Processing with business key: {envelope.idempotency_key}")
    return {"status": "processed"}


def example_custom_keys():
    """Example: Custom idempotency keys"""
    print("\n" + "="*80)
    print("Example 7: Custom Idempotency Keys")
    print("="*80)

    tenant_id = str(uuid4())
    resource_id = str(uuid4())

    # Create envelope with business key
    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="resource.updated",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.resource.updated:v1",
        producer="resource-service",
        payload={"resource_id": resource_id},
        idempotency_key=create_business_idempotency_key(
            tenant_id,
            "resource-update",
            resource_id
        )
    )

    print(f"\nIdempotency key: {envelope.idempotency_key}")

    # Process
    result = handle_with_business_key(envelope)
    print(f"Result: {result}")

    # Same operation (duplicate)
    duplicate_envelope = EventEnvelope(
        event_id=uuid4(),  # Different event_id
        event_type="resource.updated",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.resource.updated:v1",
        producer="resource-service",
        payload={"resource_id": resource_id},
        idempotency_key=create_business_idempotency_key(
            tenant_id,
            "resource-update",
            resource_id  # Same resource
        )
    )

    print("\nProcessing duplicate operation (same resource):")
    result2 = handle_with_business_key(duplicate_envelope)
    print(f"Result: {result2} (cached)")


# ═══════════════════════════════════════════════════════════════════════════════
# Main Runner
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("SAHOOL Event Idempotency Examples")
    print("="*80)

    # Run synchronous examples
    example_simple_decorator()
    example_error_on_duplicate()
    example_context_manager()
    example_manual_control()
    example_custom_keys()
    example_error_handling()

    # Run async examples
    print("\nRunning async examples...")
    asyncio.run(example_nats_integration())

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    main()
