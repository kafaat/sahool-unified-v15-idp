# shared/mobile_sync

Mobile Offline Sync Engine
وحدة المزامنة للأجهزة المحمولة بدون اتصال

A comprehensive offline-first synchronization module for the SAHOOL mobile
application, providing priority-based queue management, multi-strategy conflict
resolution, and delta sync for bandwidth-constrained environments.

Version: 1.0.0 | License: Proprietary - KAFAAT

---

## Overview

The `shared/mobile_sync` module is the backend counterpart to the Flutter
offline-first sync engine in `apps/mobile/`. It defines the data models,
queue management, conflict resolution strategies, and delta-compression
utilities consumed by mobile services when reconciling local (Drift/SQLite)
changes with the central PostgreSQL database. All status messages and error
strings are bilingual (Arabic/English) via `BilingualMessage`.

---

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Package entry point; exports all public symbols |
| `models.py` | Core dataclasses and enums: `SyncItem`, `SyncConflict`, `SyncSession`, `DeltaPacket`, status messages |
| `queue.py` | `SyncQueue` (heap-based priority queue) and `SyncQueueManager` (upload/download queues + sessions) |
| `resolver.py` | Conflict resolution strategies: last-write-wins, server-wins, client-wins, field-level merge, manual merge |
| `delta.py` | Delta computation, `DeltaPacketBuilder`, `DeltaSyncManager` for bandwidth-efficient sync |

---

## Core Concepts

### SyncItem

The atomic unit of synchronization. Each item carries:
- `entity_id` / `entity_type` — what is being synced (field, crop, irrigation, task, etc.)
- `operation` — `CREATE`, `UPDATE`, `DELETE`, `PARTIAL_UPDATE`
- `direction` — `UPLOAD` (device → server), `DOWNLOAD` (server → device), `BIDIRECTIONAL`
- `priority` — `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `BACKGROUND`
- `local_data` / `server_data` / `delta_data` — data payloads
- Retry tracking with exponential backoff (60s, 120s, 240s, ...)
- `metadata` — version, schema version, checksum, encryption flag

### Supported Entity Types

`FIELD`, `CROP`, `IRRIGATION`, `SPRAY`, `HARVEST`, `OBSERVATION`, `TASK`,
`ALERT`, `EQUIPMENT`, `SENSOR_READING`, `WEATHER`, `USER_PREFERENCE`

### Priority Weights

| Priority | Weight | Use Case |
|----------|--------|----------|
| CRITICAL | 0 | Alerts, emergency data |
| HIGH | 1 | Field readings, sensor data |
| MEDIUM | 2 | Normal operations |
| LOW | 3 | Historical data |
| BACKGROUND | 4 | Idle-time sync |

---

## Components

### SyncQueue

Heap-based priority queue with deduplication, batching, retry handling, and
event callbacks. Items with the same entity can be auto-merged to avoid
redundant uploads.

Key methods: `enqueue()`, `enqueue_batch()`, `dequeue()`, `dequeue_batch()`,
`mark_completed()`, `mark_failed()`, `mark_conflict()`, `cancel()`.

### SyncQueueManager

Manages separate upload and download `SyncQueue` instances plus session
lifecycle (`start_session()` / `end_session()`). Returns a `SyncResult`
with counts, duration, and conflict details on session close.

### Conflict Resolution Strategies

| Strategy | Class | Behavior |
|----------|-------|----------|
| `LAST_WRITE_WINS` | `LastWriteWinsResolver` | Newer timestamp wins automatically |
| `SERVER_WINS` | `ServerWinsResolver` | Server data always takes precedence |
| `CLIENT_WINS` | `ClientWinsResolver` | Local device data always takes precedence |
| `FIELD_LEVEL_MERGE` | `FieldLevelMergeResolver` | Per-field rules determine winner |
| `MANUAL_MERGE` | `ManualMergeResolver` | Farmer selects value for each field |
| `CUSTOM` | `CustomResolver` | Caller-supplied resolution function |

---

## Usage Examples

### Basic Sync Queue

```python
from shared.mobile_sync import (
    SyncQueue, SyncQueueConfig, SyncItem,
    SyncPriority, SyncDirection, SyncOperationType, EntityType,
)

config = SyncQueueConfig(max_queue_size=5000, max_batch_size=25)
queue = SyncQueue(config, tenant_id="tenant_001", device_id="device_001")

item = SyncItem(
    entity_id="field_123",
    entity_type=EntityType.FIELD,
    operation=SyncOperationType.UPDATE,
    priority=SyncPriority.HIGH,
    direction=SyncDirection.UPLOAD,
    local_data={"name": "North Field", "area_hectares": 5.5},
    user_id="user_001",
)

success, message = await queue.enqueue(item)
print(message.get("ar"))  # التغييرات في قائمة انتظار المزامنة

batch = await queue.dequeue_batch(max_size=10)
for sync_item in batch:
    # send to server ...
    await queue.mark_completed(sync_item.id)
```

### Conflict Detection and Resolution

```python
from shared.mobile_sync import (
    ConflictResolutionManager, ConflictResolutionStrategy,
    ResolutionConfig, ManualMergeChoice, detect_conflict,
)

config = ResolutionConfig(
    default_strategy=ConflictResolutionStrategy.LAST_WRITE_WINS,
    auto_resolve_simple=True,
)
manager = ConflictResolutionManager(config)

conflict = manager.detect_conflict(
    local_item=item,
    server_data=server_response,
    server_modified_at=server_timestamp,
)

if conflict:
    resolved, success = manager.auto_resolve(conflict)
    if not success:
        # Present field-level choices to the farmer
        choices = [
            ManualMergeChoice(
                field_name="area_hectares",
                chosen_value=6.0,
                source="custom",
                custom_value=6.0,
            )
        ]
        resolved, success, msg = manager.manual_resolve(
            conflict.id, choices, user_id="user_001"
        )
```

### Delta Sync (Bandwidth Optimization)

```python
from shared.mobile_sync import DeltaSyncManager, DeltaSyncConfig

config = DeltaSyncConfig(min_savings_percent=20.0)
delta_manager = DeltaSyncManager(config)

prepared_item, is_delta = delta_manager.prepare_upload(item)
if is_delta:
    stats = delta_manager.get_stats()
    print(f"Bandwidth saved: {stats['total_bytes_saved']} bytes")
```

### Session-Based Sync

```python
from shared.mobile_sync import SyncQueueManager, SyncDirection, EntityType

manager = SyncQueueManager(tenant_id="t1", device_id="d1")
session = await manager.start_session(
    user_id="user_001",
    direction=SyncDirection.BIDIRECTIONAL,
    entity_types=[EntityType.FIELD, EntityType.IRRIGATION],
)

# process items ...

result = await manager.end_session(session.id)
print(f"Synced: {result.synced_items}/{result.total_items}")
print(f"Conflicts: {result.conflict_items}")
```

---

## SyncQueueConfig Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_queue_size` | 10000 | Maximum items in queue |
| `max_retries` | 3 | Retries before permanent failure |
| `max_batch_size` | 50 | Items per dequeue batch |
| `max_concurrent_syncs` | 5 | Parallel sync operations |
| `retry_base_delay_seconds` | 60 | Base delay for exponential backoff |
| `auto_expire_hours` | 72 | Discard items older than N hours |
| `deduplicate_pending` | True | Merge duplicate entity updates |

---

## Environment Variables

No module-specific environment variables. The consuming mobile sync service
uses the standard platform variables: `DATABASE_URL`, `NATS_URL`, and
`REDIS_URL` for session state caching.
