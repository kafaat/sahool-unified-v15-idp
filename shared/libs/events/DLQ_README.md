# Dead Letter Queue (DLQ) Implementation

## Overview

This implementation provides a robust Dead Letter Queue (DLQ) system for NATS event processing in the SAHOOL platform. Failed messages are automatically routed to DLQ subjects after max retries, with comprehensive error context preservation.

## Architecture

```
┌─────────────┐
│  Publisher  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│    NATS JetStream                   │
│    sahool.analysis.*                │
│    sahool.actions.*                 │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    NATS Consumer                    │
│    - Process message                │
│    - Retry on failure (3x)          │
│    - Route to DLQ after max retries │
└──────┬──────────────────────────────┘
       │
       ├─────────────┐
       │ Success     │ Failure after max retries
       ▼             ▼
   ┌────────┐   ┌──────────────────────────┐
   │  ACK   │   │    DLQ Subject           │
   └────────┘   │    sahool.dlq.{type}     │
                └──────┬───────────────────┘
                       │
                       ▼
                ┌──────────────────────────┐
                │    DLQ Consumer          │
                │    - Store in database   │
                │    - Alert on critical   │
                │    - Enable retry        │
                └──────────────────────────┘
```

## Components

### 1. NATS Consumer (`nats_consumer.py`)

NATS consumer with automatic retry and DLQ routing.

**Features:**
- Automatic retry with exponential backoff
- Configurable max retries (default: 3)
- Routes failed messages to DLQ after max retries
- Preserves error context and metadata
- Pull-based consumer with explicit ACK

**Subject Format:**
- Input: `sahool.analysis.*`, `sahool.actions.*`
- DLQ: `sahool.dlq.{event_type}`

### 2. DLQ Consumer (`dlq_consumer.py`)

Monitors DLQ subjects and processes failed events.

**Features:**
- Subscribes to all DLQ subjects: `sahool.dlq.>`
- Stores failed events in database
- Sends alerts for critical failures
- Enables manual or automatic retry
- Customizable failure handling logic

### 3. DLQ Models (`dlq_models.py`)

SQLAlchemy models for storing failed events.

**Database Schema:**
- `failed_events` table with comprehensive error context
- Indexes for efficient querying
- Support for retry tracking and resolution workflow

### 4. Failed Event Structure

```json
{
  "event_id": "123e4567-e89b-12d3-a456-426614174000",
  "original_subject": "sahool.analysis.ndvi_computed",
  "event_type": "ndvi_computed",
  "source_service": "satellite-service",
  "tenant_id": "tenant-123",
  "field_id": "field-456",
  "farmer_id": "farmer-789",

  "error_message": "Database connection timeout",
  "error_type": "TimeoutError",
  "stack_trace": "...",

  "retry_count": 3,
  "max_retries": 3,
  "first_attempt_at": "2025-01-15T10:00:00Z",
  "last_attempt_at": "2025-01-15T10:15:00Z",

  "original_data": { ... },
  "original_headers": { ... },

  "dlq_timestamp": "2025-01-15T10:15:00Z",
  "dlq_reason": "max_retries_exceeded"
}
```

## Usage

### Basic Consumer with DLQ

```python
import asyncio
import json
from shared.libs.events import (
    NATSConsumer,
    NATSConsumerConfig,
    ConsumerContext,
    ProcessingResult,
)

async def my_handler(ctx: ConsumerContext) -> ProcessingResult:
    """Process NATS messages with automatic DLQ routing"""
    try:
        event = json.loads(ctx.data.decode('utf-8'))

        # Process event...

        return ProcessingResult.SUCCESS
    except ValueError as e:
        # Validation errors go straight to DLQ
        return ProcessingResult.DEAD_LETTER
    except Exception as e:
        # Other errors trigger retry
        return ProcessingResult.RETRY

async def main():
    # Configure consumer
    config = NATSConsumerConfig(
        servers=["nats://localhost:4222"],
        stream_name="SAHOOL_EVENTS",
        subject_filter="sahool.analysis.*",
        max_retries=3,
        retry_delay_seconds=5,
        exponential_backoff=True,
        dlq_enabled=True,
    )

    # Create and start consumer
    consumer = NATSConsumer(config)
    await consumer.connect()
    await consumer.subscribe(my_handler)
    await consumer.start()

asyncio.run(main())
```

### DLQ Monitoring Service

```python
import asyncio
from shared.libs.events import (
    DLQEvent,
    DLQAction,
    start_dlq_consumer,
)

async def dlq_handler(event: DLQEvent) -> DLQAction:
    """Handle failed events from DLQ"""

    # Store in database
    await store_failed_event(event)

    # Alert on critical errors
    if event.error_type in ["DatabaseError", "AuthenticationError"]:
        await send_alert(event)
        return DLQAction.ALERT

    # Retry transient errors
    if event.error_type == "TimeoutError":
        return DLQAction.RETRY

    return DLQAction.STORE

async def main():
    # Start DLQ consumer
    consumer = await start_dlq_consumer(dlq_handler)

    # Keep running
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

### Database Storage

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from shared.libs.events import FailedEventModel

async def store_failed_event(event: DLQEvent):
    """Store failed event in database"""
    engine = create_async_engine("postgresql+asyncpg://...")

    async with AsyncSession(engine) as session:
        failed_event = FailedEventModel.from_dlq_event(event)
        session.add(failed_event)
        await session.commit()
```

## Configuration

### Consumer Configuration

```python
NATSConsumerConfig(
    # Connection
    servers=["nats://localhost:4222"],
    name="my-consumer",

    # Stream/Subject
    stream_name="SAHOOL_EVENTS",
    consumer_name="my-consumer",
    subject_filter="sahool.analysis.*",
    durable=True,

    # Retry
    max_retries=3,
    retry_delay_seconds=5,
    exponential_backoff=True,

    # DLQ
    dlq_enabled=True,
    dlq_subject_prefix="sahool.dlq",
)
```

### DLQ Configuration

```python
DLQConsumerConfig(
    # Connection
    servers=["nats://localhost:4222"],
    name="dlq-monitor",

    # DLQ subject pattern
    dlq_subject="sahool.dlq.>",

    # Storage
    store_in_db=True,

    # Alerting
    alert_on_critical=True,
    critical_error_types=["DatabaseError", "ValidationError"],
)
```

## Processing Results

Return from your message handler:

- **`ProcessingResult.SUCCESS`** - Message processed successfully, ACK
- **`ProcessingResult.RETRY`** - Transient failure, retry with backoff
- **`ProcessingResult.DEAD_LETTER`** - Permanent failure, route to DLQ immediately

## DLQ Actions

Return from your DLQ handler:

- **`DLQAction.STORE`** - Store in database for analysis
- **`DLQAction.RETRY`** - Republish to original subject for retry
- **`DLQAction.ALERT`** - Send alert to operations team
- **`DLQAction.DISCARD`** - Discard permanently

## Database Setup

### Create Table

```sql
-- Run the migration SQL from dlq_models.py
-- This creates the failed_events table with all necessary indexes

CREATE TABLE failed_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    original_subject VARCHAR(255) NOT NULL,
    source_service VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    original_data JSONB NOT NULL,
    dlq_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Query Failed Events

```sql
-- Recent failures
SELECT * FROM failed_events
ORDER BY dlq_timestamp DESC
LIMIT 100;

-- Failures by error type
SELECT error_type, COUNT(*)
FROM failed_events
GROUP BY error_type
ORDER BY COUNT(*) DESC;

-- Failures by service
SELECT source_service, COUNT(*)
FROM failed_events
WHERE dlq_timestamp > NOW() - INTERVAL '24 hours'
GROUP BY source_service;

-- Pending failures for retry
SELECT * FROM failed_events
WHERE status = 'pending'
AND error_type IN ('TimeoutError', 'ConnectionError');
```

## Monitoring & Alerts

### Metrics to Track

1. **DLQ Rate** - Messages routed to DLQ per minute
2. **Error Types** - Distribution of error types
3. **Service Failures** - Which services have most failures
4. **Retry Success** - Success rate of DLQ retries
5. **Resolution Time** - Time to resolve DLQ events

### Alert Thresholds

- **High DLQ Rate** - More than 10 messages/minute
- **Critical Errors** - DatabaseError, AuthenticationError
- **Service Down** - All messages from service failing
- **Unresolved Events** - Events pending >24 hours

### Dashboards

Create dashboards showing:
- DLQ events over time
- Error type distribution
- Top failing services
- Resolution status
- Retry outcomes

## Best Practices

### 1. Return Appropriate Results

```python
# Good - specific error handling
try:
    validate_data(event)
    process_data(event)
    return ProcessingResult.SUCCESS
except ValidationError:
    return ProcessingResult.DEAD_LETTER  # Don't retry validation errors
except DatabaseError:
    return ProcessingResult.RETRY  # Retry database issues
```

### 2. Preserve Context

The DLQ system automatically preserves:
- Original event data
- Error messages and types
- Retry history
- Timing information

### 3. Configure Retries Appropriately

```python
# Transient failures - more retries
config = NATSConsumerConfig(
    max_retries=5,
    retry_delay_seconds=10,
    exponential_backoff=True,
)

# Critical path - fewer retries, faster failure
config = NATSConsumerConfig(
    max_retries=2,
    retry_delay_seconds=2,
    exponential_backoff=False,
)
```

### 4. Monitor DLQ

Always run a DLQ consumer to:
- Store failed events
- Alert on critical failures
- Enable retry workflows
- Track failure patterns

### 5. Handle DLQ Events

```python
async def smart_dlq_handler(event: DLQEvent) -> DLQAction:
    # Always store for analysis
    await store_in_db(event)

    # Alert on critical
    if is_critical(event):
        await send_alert(event)
        return DLQAction.ALERT

    # Auto-retry after delay
    if is_transient(event) and event.retry_count < 5:
        await schedule_retry(event, delay_hours=1)
        return DLQAction.RETRY

    return DLQAction.STORE
```

## Troubleshooting

### Messages Not Being Retried

- Check `max_retries` configuration
- Verify handler returns `ProcessingResult.RETRY`
- Check NATS connection status

### Messages Not Going to DLQ

- Verify `dlq_enabled=True`
- Check DLQ subject prefix
- Ensure max retries is reached

### DLQ Consumer Not Receiving Events

- Verify DLQ subject pattern: `sahool.dlq.>`
- Check NATS connection
- Verify DLQ events are being published

### Database Storage Failing

- Check database connection
- Verify table exists (run migration)
- Check SQLAlchemy configuration

## Examples

See the `examples/` directory for complete implementations:

- `consumer_example.py` - NATS consumer with DLQ
- `dlq_monitor_example.py` - DLQ monitoring service

## Dependencies

```bash
# Required
pip install nats-py

# Optional (for database storage)
pip install sqlalchemy asyncpg

# Optional (for validation)
pip install pydantic
```

## Migration Guide

### From Legacy Logging-Only

**Before:**
```python
try:
    process_event(event)
except Exception as e:
    logger.error(f"Failed to process: {e}")
    # Event lost!
```

**After:**
```python
async def handler(ctx: ConsumerContext) -> ProcessingResult:
    try:
        process_event(ctx.data)
        return ProcessingResult.SUCCESS
    except Exception as e:
        logger.error(f"Failed to process: {e}")
        return ProcessingResult.RETRY  # Automatically retries and routes to DLQ
```

## Future Enhancements

- [ ] Automatic retry scheduling from DLQ
- [ ] Dead letter queue expiration/archival
- [ ] Integration with monitoring systems (Grafana, Datadog)
- [ ] Admin UI for DLQ management
- [ ] Bulk retry operations
- [ ] Failure pattern detection

## Support

For questions or issues:
- Check examples in `shared/libs/events/examples/`
- Review test files for advanced usage
- Contact: SAHOOL Platform Team
