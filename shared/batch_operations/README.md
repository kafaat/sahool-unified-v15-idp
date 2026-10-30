# Batch Operations Module | وحدة عمليات الدفعات

Async batch processing for agricultural field operations on the SAHOOL platform. Enables bulk execution of irrigation, spraying, fertilization, harvest entry, equipment assignments, and alert acknowledgments across multiple fields with real-time progress tracking, partial failure handling, and rollback support.

**Version**: 16.0.0 | **Python**: 3.11+

## File Structure

```
shared/batch_operations/
├── __init__.py       # Public API, version, and re-exports
├── models.py         # Data models: BatchOperation, BatchResult, item types, params
├── executor.py       # BatchExecutor with concurrency, retry, rollback logic
└── scheduler.py      # BatchScheduler with priority queue and recurring execution
```

## Key Components

### Operation Types (`BatchOperationType`)
| Value | Description |
|-------|-------------|
| `IRRIGATION` | Bulk irrigation across multiple fields |
| `SPRAYING` | Multi-field pesticide/herbicide/fungicide spraying |
| `FERTILIZATION` | Batch fertilizer application |
| `HARVEST` | Bulk harvest data entry |
| `EQUIPMENT_ASSIGN` | Multi-equipment task assignment |
| `ALERT_ACK` | Batch alert acknowledgment |

### Execution Config (`BatchConfig`)
| Field | Default | Description |
|-------|---------|-------------|
| `max_concurrent` | 5 | Parallel item processing limit |
| `timeout_per_item_seconds` | 60.0 | Per-item timeout |
| `retry_failed_items` | True | Auto-retry failed items |
| `max_retries` | 3 | Maximum retry attempts |
| `rollback_strategy` | NONE | `NONE`, `ON_FIRST_ERROR`, `ON_THRESHOLD`, `MANUAL` |
| `failure_threshold_percent` | 50.0 | Failure % to trigger threshold rollback |
| `dry_run` | False | Simulate without writing |

### `BatchExecutor`
Executes batches with sequential or concurrent item processing. Supports:
- Real-time progress via `ProgressCallback`, `ItemCallback`, `StatusCallback`
- Cancel (`request_cancel()`), pause (`request_pause()`), and resume (`request_resume()`)
- Automatic rollback in reverse item order on failure

### `BatchScheduler`
Priority queue-based scheduler (min-heap). Supports:
- `ScheduleType.IMMEDIATE`, `SCHEDULED`, `RECURRING`
- `RecurrencePattern.DAILY`, `WEEKLY`, `MONTHLY`, `CUSTOM`
- `BatchPriority.URGENT` > `HIGH` > `MEDIUM` > `LOW`
- `max_concurrent_batches` limit (default: 3)
- Per-batch cancel/pause/resume

## Usage Examples

### Direct Execution

```python
from shared.batch_operations import (
    BatchOperation, BatchOperationType, BatchExecutor,
    BatchConfig, FieldOperationItem, IrrigationParams,
    RollbackStrategy,
)

# Build the batch
batch = BatchOperation(
    tenant_id="farm_001",
    operation_type=BatchOperationType.IRRIGATION,
    name="Morning Irrigation",
    name_ar="ري الصباح",
    irrigation_params=IrrigationParams(water_amount_mm=25.0, method="drip"),
    field_items=[
        FieldOperationItem(field_id="FIELD-001", field_name="North Field", area_hectares=5.2),
        FieldOperationItem(field_id="FIELD-002", field_name="South Field", area_hectares=3.8),
        FieldOperationItem(field_id="FIELD-003", field_name="East Field", area_hectares=8.5),
    ],
    config=BatchConfig(max_concurrent=3, rollback_strategy=RollbackStrategy.ON_THRESHOLD),
)

# Execute with progress callback
executor = BatchExecutor()

async def on_progress(progress):
    print(f"Progress: {progress.percent_complete:.1f}% "
          f"({progress.completed_items}/{progress.total_items})")

executor.set_progress_callback(on_progress)
result = await executor.execute(batch)

print(f"Status: {result.status}, Success rate: {result.to_dict()['success_rate']}%")
```

### Convenience Function (Quick Irrigation)

```python
from shared.batch_operations import execute_irrigation_batch

result = await execute_irrigation_batch(
    field_ids=["FIELD-001", "FIELD-002", "FIELD-003"],
    water_amount_mm=30.0,
    tenant_id="farm_001",
)
```

### Scheduled and Recurring Execution

```python
from shared.batch_operations import (
    BatchScheduler, ScheduleType, RecurrencePattern, start_scheduler, stop_scheduler,
)
from datetime import datetime, timezone, timedelta

scheduler = BatchScheduler(max_concurrent_batches=2, check_interval_seconds=10.0)

# Schedule once, 1 hour from now
schedule = scheduler.schedule_batch(
    batch,
    schedule_type=ScheduleType.SCHEDULED,
    scheduled_time=datetime.now(timezone.utc) + timedelta(hours=1),
)

# Or schedule as daily recurring
schedule = scheduler.schedule_batch(
    batch,
    schedule_type=ScheduleType.RECURRING,
    scheduled_time=datetime.now(timezone.utc),
    recurrence_pattern=RecurrencePattern.DAILY,
    recurrence_interval=1,
    max_executions=7,  # Run for 7 days
)

await scheduler.start()
# ...
await scheduler.stop()
```

## Integration Notes

- `BatchOperation.audit_log` tracks all state transitions for compliance.
- All messages are bilingual via `BilingualMessage(en=..., ar=...)`.
- Custom item processors can override the default mock `process()` and `rollback()` by injecting callables into `FieldOperationProcessor`, `HarvestEntryProcessor`, etc.
- Global default scheduler available via `get_scheduler()`, `start_scheduler()`, `stop_scheduler()`.
