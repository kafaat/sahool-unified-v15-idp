"""
Batch Operations Module
=======================
وحدة عمليات الدفعات

Comprehensive batch operations module for the SAHOOL agricultural platform.
Provides batch field operations, bulk data entry, equipment assignments,
and alert management with progress tracking and rollback capabilities.

Author: SAHOOL Platform Team
Updated: January 2026

Features:
    - Batch field operations (irrigation, spraying, fertilization)
    - Bulk harvest data entry
    - Multi-equipment task assignment
    - Batch alert acknowledgment
    - Progress callbacks and tracking
    - Partial failure handling
    - Rollback capabilities
    - Priority queue management
    - Scheduled and recurring execution
    - Bilingual messages (English/Arabic)

Example Usage:
    from shared.batch_operations import (
        BatchOperation,
        BatchOperationType,
        BatchExecutor,
        BatchScheduler,
        FieldOperationItem,
        IrrigationParams,
    )

    # Create a batch irrigation operation
    batch = BatchOperation(
        tenant_id="farm_001",
        operation_type=BatchOperationType.IRRIGATION,
        name="Morning Irrigation",
        name_ar="ري الصباح",
        irrigation_params=IrrigationParams(
            water_amount_mm=25.0,
            method="drip"
        ),
        field_items=[
            FieldOperationItem(field_id="field_001", field_name="Field A"),
            FieldOperationItem(field_id="field_002", field_name="Field B"),
        ],
    )

    # Execute with progress tracking
    executor = BatchExecutor()

    async def on_progress(progress):
        print(f"Progress: {progress.percent_complete}%")

    executor.set_progress_callback(on_progress)
    result = await executor.execute(batch)

    print(f"Completed: {result.completed_items}/{result.total_items}")

    # Or use the scheduler for queued execution
    scheduler = BatchScheduler(max_concurrent_batches=3)
    await scheduler.start()

    schedule = scheduler.schedule_batch(
        batch,
        schedule_type=ScheduleType.SCHEDULED,
        scheduled_time=datetime.now(timezone.utc) + timedelta(hours=1)
    )

    await scheduler.stop()
"""

from .executor import (
    AlertAcknowledgmentProcessor,
    BatchCancelledException,
    # Exceptions
    BatchExecutionError,
    # Executor
    BatchExecutor,
    BatchRollbackError,
    BatchThresholdExceededError,
    EquipmentAssignmentProcessor,
    FieldOperationProcessor,
    HarvestEntryProcessor,
    ItemCallback,
    # Processors
    ItemProcessor,
    # Callback types
    ProgressCallback,
    StatusCallback,
    # Convenience functions
    execute_batch,
    execute_irrigation_batch,
)
from .models import (
    BATCH_MESSAGES,
    AlertAcknowledgment,
    BatchConfig,
    BatchOperation,
    # Enums
    BatchOperationType,
    BatchPriority,
    # Batch models
    BatchProgress,
    BatchResult,
    BatchStatus,
    # Bilingual messages
    BilingualMessage,
    EquipmentAssignment,
    FertilizationParams,
    # Item models
    FieldOperationItem,
    HarvestEntry,
    # Parameter models
    IrrigationParams,
    ItemStatus,
    RollbackStrategy,
    SprayingParams,
)
from .scheduler import (
    # Models
    BatchSchedule,
    # Scheduler
    BatchScheduler,
    QueuedBatch,
    QueuePosition,
    RecurrencePattern,
    SchedulerCallback,
    SchedulerEvent,
    # Enums
    ScheduleType,
    # Convenience functions
    get_scheduler,
    schedule_batch,
    start_scheduler,
    stop_scheduler,
)

__all__ = [
    # === Models (models.py) ===
    # Enums
    "BatchOperationType",
    "BatchPriority",
    "BatchStatus",
    "ItemStatus",
    "RollbackStrategy",
    # Bilingual
    "BilingualMessage",
    "BATCH_MESSAGES",
    # Parameters
    "IrrigationParams",
    "SprayingParams",
    "FertilizationParams",
    # Items
    "FieldOperationItem",
    "HarvestEntry",
    "EquipmentAssignment",
    "AlertAcknowledgment",
    # Batch
    "BatchProgress",
    "BatchConfig",
    "BatchOperation",
    "BatchResult",
    # === Executor (executor.py) ===
    # Exceptions
    "BatchExecutionError",
    "BatchRollbackError",
    "BatchCancelledException",
    "BatchThresholdExceededError",
    # Processors
    "ItemProcessor",
    "FieldOperationProcessor",
    "HarvestEntryProcessor",
    "EquipmentAssignmentProcessor",
    "AlertAcknowledgmentProcessor",
    # Executor
    "BatchExecutor",
    # Callbacks
    "ProgressCallback",
    "ItemCallback",
    "StatusCallback",
    # Functions
    "execute_batch",
    "execute_irrigation_batch",
    # === Scheduler (scheduler.py) ===
    # Enums
    "ScheduleType",
    "RecurrencePattern",
    "QueuePosition",
    # Models
    "BatchSchedule",
    "QueuedBatch",
    "SchedulerEvent",
    # Scheduler
    "BatchScheduler",
    "SchedulerCallback",
    # Functions
    "get_scheduler",
    "schedule_batch",
    "start_scheduler",
    "stop_scheduler",
]

__version__ = "16.0.0"
