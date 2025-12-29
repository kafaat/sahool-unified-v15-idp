# Event Idempotency Guide

## Overview

This guide explains how to use the SAHOOL event idempotency system to prevent duplicate event processing.

The idempotency system provides:
- ✅ Automatic duplicate event detection
- ✅ Redis-based distributed tracking with 24-hour TTL
- ✅ Result caching for replay
- ✅ Concurrent processing prevention
- ✅ Multiple integration patterns (decorator, context manager, manual)

## Quick Start

### 1. Using the Decorator (Recommended)

The easiest way to add idempotency to your event handlers:

```python
from shared.libs.events import EventEnvelope, idempotent_event_handler

@idempotent_event_handler()
def handle_field_created(envelope: EventEnvelope) -> dict:
    """Process field.created event with automatic idempotency"""

    # Extract payload
    field_id = envelope.payload["field_id"]
    name = envelope.payload["name"]

    # Process event (this code only runs once per unique event)
    field = create_field_in_database(field_id, name)

    # Return result (will be cached for replay)
    return {
        "status": "created",
        "field_id": field_id,
        "timestamp": datetime.utcnow().isoformat()
    }

# First call - processes event
result1 = handle_field_created(envelope)
# {"status": "created", "field_id": "...", "timestamp": "..."}

# Second call with same event - returns cached result without processing
result2 = handle_field_created(envelope)
# Same result, no database call made
```

### 2. Using Context Manager

For more control over the idempotency flow:

```python
from shared.libs.events import EventEnvelope, IdempotentEventProcessor

processor = IdempotentEventProcessor()

def handle_event(envelope: EventEnvelope) -> dict:
    with processor.process(envelope) as ctx:
        # Check if duplicate
        if ctx.is_duplicate:
            return ctx.cached_result

        # Process event
        result = process_field_creation(envelope.payload)

        # Mark as completed with result
        ctx.mark_completed(result)

        return result
```

### 3. Manual Control

For advanced use cases:

```python
from shared.libs.events import EventEnvelope, get_idempotency_checker

checker = get_idempotency_checker()

def handle_event(envelope: EventEnvelope):
    # Get idempotency key
    key = checker.get_or_create_idempotency_key(
        envelope.event_id,
        envelope.idempotency_key
    )

    # Check for duplicate
    is_dup, record = checker.is_duplicate(key)
    if is_dup and record.status == ProcessingStatus.COMPLETED:
        return record.result

    # Mark as processing
    if not checker.mark_processing(key, envelope.event_id, envelope.event_type):
        # Another instance is processing
        return None

    try:
        # Process event
        result = do_work(envelope)

        # Mark as completed
        checker.mark_completed(key, result)

        return result
    except Exception as e:
        # Mark as failed
        checker.mark_failed(key, str(e))
        raise
```

## Idempotency Key

### Automatic Key Generation

If no `idempotency_key` is provided in the event envelope, the system uses `event_id`:

```python
envelope = EventEnvelope(
    event_id=uuid4(),
    event_type="field.created",
    # ... other fields ...
    idempotency_key=None  # Uses event_id
)
```

### Custom Idempotency Key

For better control, provide a custom idempotency key:

```python
envelope = EventEnvelope(
    event_id=uuid4(),
    event_type="field.created",
    # ... other fields ...
    idempotency_key=f"field-create:{tenant_id}:{field_id}"
)
```

**Best practices for idempotency keys:**
- Include business identifiers: `"order-process:{order_id}"`
- Include operation type: `"payment-charge:{payment_id}"`
- Keep them unique per operation: `"crop-plant:{field_id}:{planting_date}"`

## Configuration

### TTL (Time-to-Live)

Default TTL is 24 hours. You can customize it:

```python
# Using decorator
@idempotent_event_handler(ttl_seconds=3600)  # 1 hour
def handle_event(envelope: EventEnvelope):
    pass

# Using context manager
processor = IdempotentEventProcessor(ttl_seconds=7200)  # 2 hours

# Using checker directly
checker = IdempotencyChecker(ttl_seconds=86400)  # 24 hours
```

### Behavior on Duplicates

#### Skip and Return Cached Result (Default)

```python
@idempotent_event_handler(
    skip_on_duplicate=True,
    return_cached_result=True
)
def handle_event(envelope: EventEnvelope) -> dict:
    return {"status": "processed"}

# Duplicate events return cached result without processing
```

#### Raise Exception on Duplicate

```python
@idempotent_event_handler(
    skip_on_duplicate=False  # Raise DuplicateEventError
)
def handle_event(envelope: EventEnvelope) -> dict:
    return {"status": "processed"}

try:
    result = handle_event(envelope)
except DuplicateEventError as e:
    # Handle duplicate
    cached_result = e.cached_result
```

## Processing States

Events go through these states:

1. **PROCESSING** - Event is currently being processed
2. **COMPLETED** - Event was successfully processed
3. **FAILED** - Event processing failed

```python
from shared.libs.events import ProcessingStatus

record = checker.get_processing_record(key)

if record.status == ProcessingStatus.PROCESSING:
    print("Event is being processed")
elif record.status == ProcessingStatus.COMPLETED:
    print(f"Event completed with result: {record.result}")
elif record.status == ProcessingStatus.FAILED:
    print(f"Event failed: {record.error}")
```

## Error Handling

### Handling Processing Errors

The decorator automatically marks failed events:

```python
@idempotent_event_handler()
def handle_event(envelope: EventEnvelope) -> dict:
    if not validate_payload(envelope.payload):
        raise ValueError("Invalid payload")

    # Process event
    return {"status": "ok"}

# On error, event is marked as FAILED in Redis
# Failed events can be retried (not considered duplicates)
```

### Manual Error Handling

```python
with processor.process(envelope) as ctx:
    if ctx.is_duplicate:
        return ctx.cached_result

    try:
        result = process_event(envelope)
        ctx.mark_completed(result)
        return result
    except Exception as e:
        ctx.mark_failed(str(e))
        raise
```

## Advanced Patterns

### Conditional Idempotency

Only use idempotency for certain event types:

```python
def handle_event(envelope: EventEnvelope):
    # Only use idempotency for critical events
    if envelope.event_type in ["payment.charged", "order.completed"]:
        @idempotent_event_handler()
        def process():
            return do_work(envelope)
        return process()
    else:
        # Process without idempotency
        return do_work(envelope)
```

### Clearing Failed Events for Retry

```python
from shared.libs.events import get_idempotency_checker

checker = get_idempotency_checker()

# Check if event failed
record = checker.get_processing_record(idempotency_key)
if record and record.status == ProcessingStatus.FAILED:
    # Delete failed record to allow retry
    checker.delete_record(idempotency_key)

    # Retry processing
    result = handle_event(envelope)
```

### Multi-Tenant Idempotency

Include tenant_id in idempotency key:

```python
def create_idempotency_key(envelope: EventEnvelope) -> str:
    """Create tenant-scoped idempotency key"""
    return f"{envelope.tenant_id}:{envelope.event_type}:{envelope.payload['resource_id']}"

envelope.idempotency_key = create_idempotency_key(envelope)
```

## NATS Integration Example

```python
import asyncio
import nats
from shared.libs.events import EventEnvelope, idempotent_event_handler

@idempotent_event_handler()
async def handle_field_created(envelope: EventEnvelope):
    """Process field.created event from NATS"""
    field_id = envelope.payload["field_id"]

    # Create field in database
    field = await create_field(field_id, envelope.payload)

    # Publish downstream events
    await publish_field_analytics_triggered(field_id)

    return {"field_id": field_id, "status": "created"}

async def subscribe_to_events():
    nc = await nats.connect("nats://localhost:4222")

    async def message_handler(msg):
        # Parse envelope
        envelope = EventEnvelope.model_validate_json(msg.data)

        # Process with idempotency
        result = await handle_field_created(envelope)

        # Acknowledge message
        await msg.ack()

    await nc.subscribe("field.created", cb=message_handler)

asyncio.run(subscribe_to_events())
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import MagicMock
from shared.libs.events import IdempotencyChecker, EventEnvelope

def test_event_handler_with_mock_redis():
    # Create mock Redis
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    # Create checker with mock
    checker = IdempotencyChecker(redis_client=mock_redis)

    # Test your handler
    envelope = EventEnvelope(...)

    # First call should process
    is_dup, record = checker.is_duplicate("test-key")
    assert is_dup is False
```

### Integration Tests

```python
import pytest
from shared.cache import get_redis_client
from shared.libs.events import get_idempotency_checker

@pytest.fixture
def redis_client():
    """Use real Redis for integration tests"""
    return get_redis_client()

def test_idempotency_with_real_redis(redis_client):
    checker = get_idempotency_checker()

    # Process event
    success = checker.mark_processing("test-key", "event-123", "test.event")
    assert success is True

    # Verify duplicate detection
    is_dup, record = checker.is_duplicate("test-key")
    assert is_dup is True

    # Cleanup
    checker.delete_record("test-key")
```

## Monitoring

### Check Processing Status

```python
from shared.libs.events import get_idempotency_checker

checker = get_idempotency_checker()

# Get processing record
record = checker.get_processing_record("my-idempotency-key")

if record:
    print(f"Status: {record.status}")
    print(f"First seen: {record.first_seen_at}")
    print(f"Completed: {record.completed_at}")
    print(f"Result: {record.result}")
else:
    print("Event not processed yet")
```

### Redis Keys

Idempotency records are stored with prefix: `idempotency:events:`

```bash
# List all idempotency keys
redis-cli KEYS "idempotency:events:*"

# Get specific record
redis-cli GET "idempotency:events:my-key"

# Check TTL
redis-cli TTL "idempotency:events:my-key"
```

## Best Practices

1. **Always use idempotency for critical operations**
   - Payments, order processing, data mutations

2. **Choose meaningful idempotency keys**
   - Include business identifiers, not just technical IDs
   - Example: `payment-charge:{payment_id}` not just `{event_id}`

3. **Set appropriate TTL**
   - Match your business requirements
   - Longer TTL = more memory usage
   - Shorter TTL = higher risk of duplicate processing

4. **Handle failed events**
   - Failed events are not considered duplicates
   - Implement retry logic with backoff
   - Monitor failed event metrics

5. **Store meaningful results**
   - Return dictionaries from handlers for caching
   - Include enough information for result replay
   - Don't store sensitive data in results

6. **Test idempotency behavior**
   - Test duplicate detection
   - Test concurrent processing prevention
   - Test error handling

## Troubleshooting

### Event processed multiple times

- Check if idempotency_key is unique per operation
- Verify Redis connectivity
- Check if TTL expired between processing attempts

### Events not being marked as completed

- Ensure handler returns successfully
- Check for exceptions in handler
- Verify Redis write permissions

### Memory usage growing

- Review TTL settings
- Check for orphaned PROCESSING records
- Implement cleanup job for old records

### Concurrent processing issues

- Verify Redis is using NX flag (atomic operations)
- Check network latency between services
- Review Redis connection pool settings

## Support

For questions or issues:
- Check Redis connectivity: `redis-cli PING`
- Review logs for idempotency errors
- Monitor Redis memory usage
- Contact platform team for assistance
