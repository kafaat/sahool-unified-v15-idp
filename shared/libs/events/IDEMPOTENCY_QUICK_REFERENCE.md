# Event Idempotency Quick Reference

## One-Minute Setup

```python
from shared.libs.events import EventEnvelope, idempotent_event_handler

@idempotent_event_handler()
def handle_event(envelope: EventEnvelope) -> dict:
    # Your processing code here
    return {"status": "processed"}
```

That's it! Your handler now has:
- ✅ Duplicate detection
- ✅ Result caching
- ✅ Concurrent processing prevention
- ✅ 24-hour TTL

## Common Patterns

### Pattern 1: Simple Decorator (Most Common)

```python
@idempotent_event_handler()
def handle_field_created(envelope: EventEnvelope) -> dict:
    field_id = envelope.payload["field_id"]
    # Process...
    return {"field_id": field_id, "status": "created"}
```

### Pattern 2: Custom Idempotency Key

```python
envelope = EventEnvelope(
    # ... other fields ...
    idempotency_key=f"order-process:{order_id}"  # Business key
)
```

### Pattern 3: Raise Error on Duplicate

```python
@idempotent_event_handler(skip_on_duplicate=False)
def handle_payment(envelope: EventEnvelope) -> dict:
    # Process payment...
    return {"status": "charged"}

try:
    result = handle_payment(envelope)
except DuplicateEventError as e:
    print(f"Duplicate! Cached result: {e.cached_result}")
```

### Pattern 4: Context Manager

```python
from shared.libs.events import IdempotentEventProcessor

processor = IdempotentEventProcessor()

with processor.process(envelope) as ctx:
    if ctx.is_duplicate:
        return ctx.cached_result

    result = do_work()
    ctx.mark_completed(result)
    return result
```

### Pattern 5: Custom TTL

```python
@idempotent_event_handler(ttl_seconds=3600)  # 1 hour
def handle_analytics(envelope: EventEnvelope) -> dict:
    # Process...
    return {"status": "ok"}
```

## NATS Integration

```python
import nats
from shared.libs.events import EventEnvelope, idempotent_event_handler

@idempotent_event_handler()
async def handle_message(envelope: EventEnvelope):
    # Process event (automatically idempotent)
    return {"status": "processed"}

async def main():
    nc = await nats.connect("nats://localhost:4222")

    async def msg_handler(msg):
        envelope = EventEnvelope.model_validate_json(msg.data)
        await handle_message(envelope)
        await msg.ack()

    await nc.subscribe("events.*", cb=msg_handler)
```

## Checking Status

```python
from shared.libs.events import get_idempotency_checker, ProcessingStatus

checker = get_idempotency_checker()

# Check if event was processed
record = checker.get_processing_record("my-key")

if record:
    if record.status == ProcessingStatus.COMPLETED:
        print(f"Completed! Result: {record.result}")
    elif record.status == ProcessingStatus.PROCESSING:
        print("Currently being processed")
    elif record.status == ProcessingStatus.FAILED:
        print(f"Failed: {record.error}")
```

## Retry Failed Events

```python
# Delete failed record to allow retry
checker.delete_record("my-failed-key")

# Now retry
result = handle_event(envelope)
```

## Best Practices

### ✅ DO

- Use custom idempotency keys with business identifiers
- Return dict from handlers for result caching
- Set appropriate TTL for your use case
- Handle DuplicateEventError if needed
- Test duplicate scenarios

### ❌ DON'T

- Store sensitive data in results
- Use very short TTLs (< 1 hour)
- Process events without idempotency for critical operations
- Ignore failed events
- Use technical IDs only in keys

## Troubleshooting

### Event processed twice?

```python
# Check idempotency key uniqueness
print(f"Key: {envelope.idempotency_key}")

# Verify Redis connection
from shared.cache import get_redis_client
redis = get_redis_client()
assert redis.ping()
```

### Stuck in PROCESSING?

```python
# Check record age and delete if stale
import time

record = checker.get_processing_record(key)
if record and record.status == ProcessingStatus.PROCESSING:
    age = time.time() - record.first_seen_at.timestamp()
    if age > 3600:  # 1 hour stale
        checker.delete_record(key)
```

## Configuration

### Default Settings
- **TTL:** 24 hours (86400 seconds)
- **Behavior:** Skip duplicates, return cached result
- **Redis Prefix:** `idempotency:events:`

### Custom Settings

```python
@idempotent_event_handler(
    ttl_seconds=7200,           # 2 hours
    skip_on_duplicate=False,    # Raise error
    return_cached_result=True   # Return cached result
)
def my_handler(envelope: EventEnvelope):
    pass
```

## Testing

```python
import pytest
from unittest.mock import MagicMock
from shared.libs.events import IdempotencyChecker

def test_my_handler():
    # Mock Redis
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    # Test with mock
    checker = IdempotencyChecker(redis_client=mock_redis)

    # Test your handler...
```

## Import Reference

```python
from shared.libs.events import (
    # Main decorator
    idempotent_event_handler,

    # Context manager
    IdempotentEventProcessor,

    # Manual control
    IdempotencyChecker,
    get_idempotency_checker,

    # Models
    IdempotencyRecord,
    ProcessingStatus,

    # Exceptions
    DuplicateEventError,
)
```

## CLI Commands (Redis)

```bash
# Count active idempotency records
redis-cli KEYS "idempotency:events:*" | wc -l

# Get specific record
redis-cli GET "idempotency:events:my-key"

# Check TTL
redis-cli TTL "idempotency:events:my-key"

# Delete record
redis-cli DEL "idempotency:events:my-key"

# Monitor Redis
redis-cli MONITOR
```

## Resources

- **Full Guide:** `IDEMPOTENCY_GUIDE.md`
- **Examples:** `examples_idempotency.py`
- **Tests:** `test_idempotency.py`
- **Implementation:** `IDEMPOTENCY_IMPLEMENTATION_SUMMARY.md`

## Support

Questions? Check the full guide or contact the platform team.

---

**TL;DR:** Add `@idempotent_event_handler()` to your event handlers. Done! 🎉
