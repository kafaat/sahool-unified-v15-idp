# Dead Letter Queue (DLQ) Implementation Summary

## Implementation Date
2025-12-29

## Overview
Implemented a comprehensive Dead Letter Queue (DLQ) system for NATS event processing in the SAHOOL platform. Failed messages are now automatically routed to DLQ subjects after max retries, with complete error context preservation.

## Problem Statement
**Before:**
- Failed messages were only logged
- No retry mechanism
- Lost events on processing failures
- No visibility into failure patterns
- No way to recover from transient failures

**After:**
- Automatic retry with exponential backoff
- Failed messages routed to DLQ after max retries
- Complete error context preserved
- Database storage for failure analysis
- DLQ monitoring consumer for alerts
- Manual and automatic retry capabilities

## Architecture

### Subject Pattern
```
Publisher → sahool.analysis.{event_type}
          → sahool.actions.{event_type}

Consumer → Process (Success ✅)
         → Retry (3x with backoff)
         → DLQ: sahool.dlq.{event_type}

DLQ Consumer → Monitor sahool.dlq.>
             → Store in database
             → Alert on critical errors
             → Enable retry workflows
```

## Files Created

### Core Components

1. **`nats_consumer.py`** (540 lines)
   - NATS consumer with DLQ support
   - Automatic retry with exponential backoff
   - Routes failed messages to DLQ
   - Pull-based consumer with explicit ACK
   - Preserves full error context

2. **`dlq_consumer.py`** (377 lines)
   - DLQ monitoring consumer
   - Subscribes to `sahool.dlq.>` subjects
   - Stores failed events in database
   - Alerts on critical failures
   - Enables retry workflows

3. **`dlq_models.py`** (293 lines)
   - SQLAlchemy model for `failed_events` table
   - Complete schema with indexes
   - Database migration SQL
   - Query helpers

### Documentation

4. **`DLQ_README.md`** (Comprehensive guide)
   - Architecture overview
   - Usage examples
   - Configuration reference
   - Best practices
   - Troubleshooting guide

5. **`DLQ_IMPLEMENTATION_SUMMARY.md`** (This file)
   - Implementation summary
   - File inventory
   - Integration guide

### Examples

6. **`examples/consumer_example.py`**
   - Complete consumer implementation
   - Shows different failure scenarios
   - Demonstrates retry logic

7. **`examples/dlq_monitor_example.py`**
   - DLQ monitoring service
   - Database storage
   - Alert integration

8. **`examples/simple_test.py`**
   - End-to-end test
   - Publishes test events
   - Verifies DLQ flow

### Database

9. **`migrations/001_create_failed_events_table.sql`**
   - PostgreSQL migration
   - Creates `failed_events` table
   - Indexes for performance
   - Triggers for auto-update

### Integration

10. **Updated `__init__.py`**
    - Exports all DLQ components
    - Optional imports (graceful degradation)
    - Availability flags

## Features Implemented

### 1. Automatic Retry
- ✅ Configurable max retries (default: 3)
- ✅ Exponential backoff
- ✅ Per-message retry tracking
- ✅ Retry state preservation

### 2. DLQ Routing
- ✅ Subject pattern: `sahool.dlq.{event_type}`
- ✅ Routes after max retries
- ✅ Immediate routing for validation errors
- ✅ Preserves original subject

### 3. Error Context
- ✅ Error message and type
- ✅ Stack traces
- ✅ Retry count and timing
- ✅ Original event data
- ✅ Original headers

### 4. Database Storage
- ✅ `failed_events` table
- ✅ JSONB for event data
- ✅ Indexes for queries
- ✅ Status tracking (pending/resolved)
- ✅ Alert tracking

### 5. DLQ Monitoring
- ✅ Subscribe to all DLQ subjects
- ✅ Store in database
- ✅ Alert on critical errors
- ✅ Retry capabilities
- ✅ Customizable handlers

### 6. Processing Results
- ✅ `SUCCESS` - ACK and continue
- ✅ `RETRY` - Retry with backoff
- ✅ `DEAD_LETTER` - Route to DLQ immediately

### 7. DLQ Actions
- ✅ `STORE` - Save for analysis
- ✅ `RETRY` - Republish to original subject
- ✅ `ALERT` - Send to operations team
- ✅ `DISCARD` - Permanently discard

## Database Schema

```sql
CREATE TABLE failed_events (
    id UUID PRIMARY KEY,
    event_id VARCHAR(255),
    event_type VARCHAR(100),
    original_subject VARCHAR(255),
    source_service VARCHAR(100),
    tenant_id VARCHAR(255),
    field_id VARCHAR(255),
    farmer_id VARCHAR(255),

    error_message TEXT,
    error_type VARCHAR(100),
    stack_trace TEXT,

    retry_count INTEGER,
    max_retries INTEGER,
    first_attempt_at TIMESTAMPTZ,
    last_attempt_at TIMESTAMPTZ,

    original_data JSONB,
    original_headers JSONB,

    dlq_timestamp TIMESTAMPTZ,
    dlq_reason VARCHAR(100),

    status VARCHAR(50),
    resolved_at TIMESTAMPTZ,
    alert_sent BOOLEAN,

    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

## Usage Examples

### Basic Consumer
```python
from shared.libs.events import (
    NATSConsumer,
    NATSConsumerConfig,
    ConsumerContext,
    ProcessingResult,
)

async def my_handler(ctx: ConsumerContext) -> ProcessingResult:
    try:
        event = json.loads(ctx.data)
        # Process event...
        return ProcessingResult.SUCCESS
    except ValueError:
        return ProcessingResult.DEAD_LETTER
    except Exception:
        return ProcessingResult.RETRY

config = NATSConsumerConfig(
    subject_filter="sahool.analysis.*",
    max_retries=3,
    dlq_enabled=True,
)

consumer = NATSConsumer(config)
await consumer.connect()
await consumer.subscribe(my_handler)
await consumer.start()
```

### DLQ Monitor
```python
from shared.libs.events import start_dlq_consumer, DLQEvent, DLQAction

async def dlq_handler(event: DLQEvent) -> DLQAction:
    await store_in_db(event)
    if event.error_type == "DatabaseError":
        await send_alert(event)
        return DLQAction.ALERT
    return DLQAction.STORE

consumer = await start_dlq_consumer(dlq_handler)
```

## Integration Steps

### 1. Install Dependencies
```bash
pip install nats-py pydantic sqlalchemy asyncpg
```

### 2. Setup Database
```bash
# Run migration
psql -h localhost -U postgres -d sahool -f migrations/001_create_failed_events_table.sql
```

### 3. Update Service
```python
# Replace existing event processing with DLQ-enabled consumer
from shared.libs.events import NATSConsumer, ProcessingResult

async def process_event(ctx: ConsumerContext) -> ProcessingResult:
    # Your processing logic
    return ProcessingResult.SUCCESS
```

### 4. Start DLQ Monitor
```python
# Run DLQ monitoring service
python examples/dlq_monitor_example.py
```

### 5. Monitor & Alert
```sql
-- Query failed events
SELECT * FROM failed_events WHERE status = 'pending';

-- Check failure patterns
SELECT error_type, COUNT(*)
FROM failed_events
GROUP BY error_type;
```

## Configuration

### Consumer Config
```python
NATSConsumerConfig(
    servers=["nats://localhost:4222"],
    stream_name="SAHOOL_EVENTS",
    subject_filter="sahool.analysis.*",
    max_retries=3,
    retry_delay_seconds=5,
    exponential_backoff=True,
    dlq_enabled=True,
    dlq_subject_prefix="sahool.dlq",
)
```

### DLQ Config
```python
DLQConsumerConfig(
    servers=["nats://localhost:4222"],
    dlq_subject="sahool.dlq.>",
    store_in_db=True,
    alert_on_critical=True,
)
```

## Testing

### Run Test Suite
```bash
# Start NATS with JetStream
docker run -p 4222:4222 nats:latest -js

# Run end-to-end test
cd shared/libs/events/examples
python simple_test.py
```

### Expected Output
```
✅ Successful processes: 1
🔄 Retry attempts: 6 (2 retries × 3 attempts)
💀 DLQ events: 2
```

## Monitoring Queries

```sql
-- Recent failures
SELECT * FROM failed_events
ORDER BY dlq_timestamp DESC
LIMIT 100;

-- Failures by type
SELECT error_type, COUNT(*)
FROM failed_events
GROUP BY error_type;

-- Failures by service
SELECT source_service, COUNT(*)
FROM failed_events
WHERE dlq_timestamp > NOW() - INTERVAL '24 hours'
GROUP BY source_service;

-- Pending retries
SELECT * FROM failed_events
WHERE status = 'pending'
AND error_type IN ('TimeoutError', 'ConnectionError');
```

## Metrics to Track

1. **DLQ Rate** - Messages/minute to DLQ
2. **Retry Success Rate** - Successful retries vs failures
3. **Error Distribution** - Types of errors
4. **Service Health** - Failures per service
5. **Resolution Time** - Time to resolve DLQ events

## Alerts

Set up alerts for:
- High DLQ rate (>10 msgs/min)
- Critical errors (DatabaseError, AuthenticationError)
- Service failures (all messages from service failing)
- Unresolved events (>24 hours old)

## Next Steps

1. **Deploy Database Migration**
   ```bash
   psql -f migrations/001_create_failed_events_table.sql
   ```

2. **Update Services**
   - Replace legacy event handlers with DLQ-enabled consumers
   - Configure retry policies per service

3. **Deploy DLQ Monitor**
   - Run DLQ consumer as a separate service
   - Configure database connection
   - Set up alerting integration

4. **Configure Monitoring**
   - Add Grafana dashboards
   - Set up alert rules
   - Configure notification channels

5. **Test & Validate**
   - Run integration tests
   - Simulate failures
   - Verify DLQ routing

## Benefits

### Reliability
- ✅ No lost events
- ✅ Automatic recovery from transient failures
- ✅ Failure isolation

### Observability
- ✅ Complete error visibility
- ✅ Failure pattern detection
- ✅ Historical analysis

### Operations
- ✅ Manual retry capability
- ✅ Critical error alerts
- ✅ Resolution tracking

### Development
- ✅ Easy integration
- ✅ Flexible configuration
- ✅ Clear error handling patterns

## Support

- **Documentation**: `DLQ_README.md`
- **Examples**: `examples/` directory
- **Tests**: `examples/simple_test.py`
- **Migration**: `migrations/001_create_failed_events_table.sql`

## Dependencies

Required:
- `nats-py` - NATS client
- `pydantic` - Data validation

Optional:
- `sqlalchemy` - Database ORM
- `asyncpg` - PostgreSQL async driver

## Version Compatibility

- Python: 3.9+
- NATS: 2.x with JetStream
- PostgreSQL: 12+
- SQLAlchemy: 2.0+

## Changelog

### 2025-12-29 - Initial Implementation
- Created NATS consumer with DLQ support
- Created DLQ consumer for monitoring
- Created database models and migrations
- Added comprehensive documentation
- Added usage examples and tests

## Contributors

SAHOOL Platform Team

---

**Status**: ✅ Ready for deployment
**Last Updated**: 2025-12-29
