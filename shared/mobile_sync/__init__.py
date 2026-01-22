"""
Mobile Offline Sync Module
==========================
وحدة المزامنة للأجهزة المحمولة بدون اتصال

A comprehensive offline sync module for mobile applications providing:
- Sync queue management with priority-based scheduling
- Conflict resolution strategies (last-write-wins, manual merge, etc.)
- Delta sync for bandwidth efficiency
- Sync status tracking
- Bilingual Arabic/English support

Author: SAHOOL Platform Team
Updated: January 2026

Example Usage
-------------

Basic sync queue usage:

    from shared.mobile_sync import (
        SyncQueue,
        SyncQueueConfig,
        SyncItem,
        SyncPriority,
        SyncDirection,
        SyncOperationType,
        EntityType,
    )

    # Create a sync queue
    config = SyncQueueConfig(max_queue_size=5000)
    queue = SyncQueue(config, tenant_id="tenant_001", device_id="device_001")

    # Add an item to sync
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
    print(message.get("ar"))  # Arabic message

    # Process items
    batch = await queue.dequeue_batch(max_size=10)
    for sync_item in batch:
        # Sync with server
        # ...
        await queue.mark_completed(sync_item.id)


Conflict resolution:

    from shared.mobile_sync import (
        ConflictResolutionManager,
        ConflictResolutionStrategy,
        ResolutionConfig,
        ManualMergeChoice,
        detect_conflict,
    )

    # Configure resolution
    config = ResolutionConfig(
        default_strategy=ConflictResolutionStrategy.LAST_WRITE_WINS,
        auto_resolve_simple=True,
    )
    manager = ConflictResolutionManager(config)

    # Detect conflict
    conflict = manager.detect_conflict(
        local_item=item,
        server_data=server_response,
        server_modified_at=server_timestamp,
    )

    if conflict:
        # Auto-resolve if possible
        resolved, success = manager.auto_resolve(conflict)
        if not success:
            # Manual resolution needed
            choices = [
                ManualMergeChoice(
                    field_name="name",
                    chosen_value="My Field Name",
                    source="custom",
                    custom_value="My Field Name",
                )
            ]
            resolved, success, msg = manager.manual_resolve(
                conflict.id, choices, user_id="user_001"
            )


Delta sync for bandwidth efficiency:

    from shared.mobile_sync import (
        DeltaSyncManager,
        DeltaSyncConfig,
        compute_delta,
        apply_delta,
    )

    # Configure delta sync
    config = DeltaSyncConfig(min_savings_percent=20.0)
    delta_manager = DeltaSyncManager(config)

    # Prepare upload with delta optimization
    prepared_item, is_delta = delta_manager.prepare_upload(item)

    if is_delta:
        print(f"Using delta sync - saved bandwidth!")
        print(delta_manager.get_stats())

"""

# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

from .models import (
    # Enums
    SyncStatus,
    SyncPriority,
    SyncDirection,
    SyncOperationType,
    ConflictType,
    ConflictResolutionStrategy,
    EntityType,
    # Data models
    BilingualMessage,
    SyncMetadata,
    SyncItem,
    SyncConflict,
    SyncProgress,
    SyncSession,
    SyncResult,
    DeltaChange,
    DeltaPacket,
    # Message dictionaries
    SYNC_MESSAGES,
    SYNC_ERRORS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Queue Management
# ─────────────────────────────────────────────────────────────────────────────

from .queue import (
    SyncQueue,
    SyncQueueConfig,
    SyncQueueManager,
    PriorityQueueItem,
    PRIORITY_WEIGHTS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Conflict Resolution
# ─────────────────────────────────────────────────────────────────────────────

from .resolver import (
    # Detection
    detect_conflict,
    find_conflicting_fields,
    is_auto_resolvable,
    # Resolvers
    ConflictResolver,
    LastWriteWinsResolver,
    ServerWinsResolver,
    ClientWinsResolver,
    FieldLevelMergeResolver,
    ManualMergeResolver,
    CustomResolver,
    # Supporting classes
    FieldMergeRule,
    ManualMergeChoice,
    # Factory and Manager
    ConflictResolverFactory,
    ConflictResolutionManager,
    ResolutionConfig,
)

# ─────────────────────────────────────────────────────────────────────────────
# Delta Sync
# ─────────────────────────────────────────────────────────────────────────────

from .delta import (
    # Core functions
    compute_delta,
    apply_delta,
    compute_checksum,
    # Configuration
    DeltaSyncConfig,
    # Builder and Manager
    DeltaPacketBuilder,
    DeltaSyncManager,
    DeltaSyncStats,
    # Batch operations
    BatchDeltaResult,
    prepare_batch_upload,
)

# ─────────────────────────────────────────────────────────────────────────────
# Module Info
# ─────────────────────────────────────────────────────────────────────────────

__version__ = "1.0.0"
__author__ = "SAHOOL Platform Team"

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Enums
    "SyncStatus",
    "SyncPriority",
    "SyncDirection",
    "SyncOperationType",
    "ConflictType",
    "ConflictResolutionStrategy",
    "EntityType",
    # Core models
    "BilingualMessage",
    "SyncMetadata",
    "SyncItem",
    "SyncConflict",
    "SyncProgress",
    "SyncSession",
    "SyncResult",
    "DeltaChange",
    "DeltaPacket",
    # Messages
    "SYNC_MESSAGES",
    "SYNC_ERRORS",
    # Queue
    "SyncQueue",
    "SyncQueueConfig",
    "SyncQueueManager",
    "PriorityQueueItem",
    "PRIORITY_WEIGHTS",
    # Conflict resolution
    "detect_conflict",
    "find_conflicting_fields",
    "is_auto_resolvable",
    "ConflictResolver",
    "LastWriteWinsResolver",
    "ServerWinsResolver",
    "ClientWinsResolver",
    "FieldLevelMergeResolver",
    "ManualMergeResolver",
    "CustomResolver",
    "FieldMergeRule",
    "ManualMergeChoice",
    "ConflictResolverFactory",
    "ConflictResolutionManager",
    "ResolutionConfig",
    # Delta sync
    "compute_delta",
    "apply_delta",
    "compute_checksum",
    "DeltaSyncConfig",
    "DeltaPacketBuilder",
    "DeltaSyncManager",
    "DeltaSyncStats",
    "BatchDeltaResult",
    "prepare_batch_upload",
]
