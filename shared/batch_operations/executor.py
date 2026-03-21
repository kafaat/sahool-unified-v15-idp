"""
Batch Operations Executor
=========================
منفذ عمليات الدفعات

Batch execution logic with progress tracking, partial failure handling,
and rollback capabilities for agricultural operations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Callable, Coroutine, Generic, TypeVar

from .models import (
    BATCH_MESSAGES,
    AlertAcknowledgment,
    BatchConfig,
    BatchOperation,
    BatchOperationType,
    BatchProgress,
    BatchResult,
    BatchStatus,
    BilingualMessage,
    EquipmentAssignment,
    FieldOperationItem,
    HarvestEntry,
    ItemStatus,
    RollbackStrategy,
)

logger = logging.getLogger(__name__)

# Type variable for generic item processing
T = TypeVar("T")

# Callback types
ProgressCallback = Callable[[BatchProgress], Coroutine[Any, Any, None] | None]
ItemCallback = Callable[[Any, ItemStatus, str | None], Coroutine[Any, Any, None] | None]
StatusCallback = Callable[[BatchStatus, BilingualMessage], Coroutine[Any, Any, None] | None]


# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class BatchExecutionError(Exception):
    """Base exception for batch execution errors."""

    def __init__(self, message: str, message_ar: str | None = None):
        super().__init__(message)
        self.message = message
        self.message_ar = message_ar or message


class BatchRollbackError(BatchExecutionError):
    """Exception raised when rollback fails."""

    pass


class BatchCancelledException(BatchExecutionError):
    """Exception raised when batch is cancelled."""

    pass


class BatchThresholdExceededError(BatchExecutionError):
    """Exception raised when failure threshold is exceeded."""

    pass


# ─────────────────────────────────────────────────────────────────────────────
# Item Processors (Abstract Base)
# ─────────────────────────────────────────────────────────────────────────────


class ItemProcessor(ABC, Generic[T]):
    """Abstract base class for item processors."""

    @abstractmethod
    async def process(self, item: T, batch: BatchOperation) -> tuple[bool, dict[str, Any] | None]:
        """
        Process a single item.

        Args:
            item: The item to process
            batch: The parent batch operation

        Returns:
            Tuple of (success: bool, result_data: dict | None)
        """
        pass

    @abstractmethod
    async def rollback(self, item: T, batch: BatchOperation) -> bool:
        """
        Rollback a processed item.

        Args:
            item: The item to rollback
            batch: The parent batch operation

        Returns:
            True if rollback successful
        """
        pass

    async def validate(self, item: T, batch: BatchOperation) -> tuple[bool, str | None]:
        """
        Validate an item before processing.

        Args:
            item: The item to validate
            batch: The parent batch operation

        Returns:
            Tuple of (valid: bool, error_message: str | None)
        """
        return True, None


class FieldOperationProcessor(ItemProcessor[FieldOperationItem]):
    """Processor for field operations (irrigation, spraying, fertilization)."""

    def __init__(
        self,
        execute_operation: Callable[[FieldOperationItem, BatchOperation], Coroutine[Any, Any, dict[str, Any]]]
        | None = None,
        rollback_operation: Callable[[FieldOperationItem, BatchOperation], Coroutine[Any, Any, bool]] | None = None,
    ):
        """
        Initialize processor with optional custom handlers.

        Args:
            execute_operation: Custom async function to execute the operation
            rollback_operation: Custom async function to rollback the operation
        """
        self._execute = execute_operation
        self._rollback = rollback_operation

    async def process(self, item: FieldOperationItem, batch: BatchOperation) -> tuple[bool, dict[str, Any] | None]:
        """Process a field operation item."""
        try:
            if self._execute:
                result_data = await self._execute(item, batch)
                return True, result_data

            # Default mock implementation
            logger.info(
                f"Processing field operation: field_id={item.field_id}, "
                f"type={batch.operation_type.value}, area={item.area_hectares}ha"
            )

            # Simulate processing
            await asyncio.sleep(0.1)

            result_data = {
                "processed_at": datetime.now(UTC).isoformat(),
                "field_id": item.field_id,
                "operation_type": batch.operation_type.value,
            }

            return True, result_data

        except Exception as e:
            logger.error(f"Field operation failed for {item.field_id}: {e}")
            return False, {"error": str(e)}

    async def rollback(self, item: FieldOperationItem, batch: BatchOperation) -> bool:
        """Rollback a field operation."""
        try:
            if self._rollback:
                return await self._rollback(item, batch)

            # Default mock implementation
            logger.info(f"Rolling back field operation: field_id={item.field_id}")
            await asyncio.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Rollback failed for {item.field_id}: {e}")
            return False


class HarvestEntryProcessor(ItemProcessor[HarvestEntry]):
    """Processor for harvest data entries."""

    def __init__(
        self,
        create_harvest_record: Callable[[HarvestEntry, BatchOperation], Coroutine[Any, Any, str]] | None = None,
        delete_harvest_record: Callable[[str], Coroutine[Any, Any, bool]] | None = None,
    ):
        """
        Initialize processor with optional custom handlers.

        Args:
            create_harvest_record: Custom async function to create harvest record
            delete_harvest_record: Custom async function to delete harvest record
        """
        self._create = create_harvest_record
        self._delete = delete_harvest_record

    async def process(self, item: HarvestEntry, batch: BatchOperation) -> tuple[bool, dict[str, Any] | None]:
        """Process a harvest entry."""
        try:
            if self._create:
                record_id = await self._create(item, batch)
                item.created_record_id = record_id
                return True, {"record_id": record_id}

            # Default mock implementation
            logger.info(
                f"Creating harvest entry: field_id={item.field_id}, crop={item.crop_type}, yield={item.yield_kg}kg"
            )

            await asyncio.sleep(0.1)

            # Mock record ID
            record_id = f"harvest_{item.id[:8]}"
            item.created_record_id = record_id

            return True, {
                "record_id": record_id,
                "created_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Harvest entry failed for {item.field_id}: {e}")
            return False, {"error": str(e)}

    async def rollback(self, item: HarvestEntry, batch: BatchOperation) -> bool:
        """Rollback a harvest entry by deleting the created record."""
        try:
            if not item.created_record_id:
                return True  # Nothing to rollback

            if self._delete:
                return await self._delete(item.created_record_id)

            # Default mock implementation
            logger.info(f"Deleting harvest record: {item.created_record_id}")
            await asyncio.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Rollback failed for harvest {item.id}: {e}")
            return False


class EquipmentAssignmentProcessor(ItemProcessor[EquipmentAssignment]):
    """Processor for equipment task assignments."""

    def __init__(
        self,
        create_assignment: Callable[[EquipmentAssignment, BatchOperation], Coroutine[Any, Any, str]] | None = None,
        delete_assignment: Callable[[str], Coroutine[Any, Any, bool]] | None = None,
    ):
        self._create = create_assignment
        self._delete = delete_assignment

    async def process(self, item: EquipmentAssignment, batch: BatchOperation) -> tuple[bool, dict[str, Any] | None]:
        """Process an equipment assignment."""
        try:
            if self._create:
                assignment_id = await self._create(item, batch)
                item.created_assignment_id = assignment_id
                return True, {"assignment_id": assignment_id}

            # Default mock implementation
            logger.info(f"Creating equipment assignment: equipment_id={item.equipment_id}, task_id={item.task_id}")

            await asyncio.sleep(0.1)

            assignment_id = f"assign_{item.id[:8]}"
            item.created_assignment_id = assignment_id

            return True, {
                "assignment_id": assignment_id,
                "created_at": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Equipment assignment failed for {item.equipment_id}: {e}")
            return False, {"error": str(e)}

    async def rollback(self, item: EquipmentAssignment, batch: BatchOperation) -> bool:
        """Rollback an equipment assignment."""
        try:
            if not item.created_assignment_id:
                return True

            if self._delete:
                return await self._delete(item.created_assignment_id)

            logger.info(f"Deleting equipment assignment: {item.created_assignment_id}")
            await asyncio.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Rollback failed for assignment {item.id}: {e}")
            return False


class AlertAcknowledgmentProcessor(ItemProcessor[AlertAcknowledgment]):
    """Processor for alert acknowledgments."""

    def __init__(
        self,
        acknowledge_alert: Callable[[AlertAcknowledgment, BatchOperation], Coroutine[Any, Any, bool]] | None = None,
        unacknowledge_alert: Callable[[str], Coroutine[Any, Any, bool]] | None = None,
    ):
        self._acknowledge = acknowledge_alert
        self._unacknowledge = unacknowledge_alert

    async def process(self, item: AlertAcknowledgment, batch: BatchOperation) -> tuple[bool, dict[str, Any] | None]:
        """Process an alert acknowledgment."""
        try:
            if self._acknowledge:
                success = await self._acknowledge(item, batch)
                if success:
                    item.acknowledged_at = datetime.now(UTC)
                return success, {"acknowledged_at": item.acknowledged_at.isoformat() if item.acknowledged_at else None}

            # Default mock implementation
            logger.info(
                f"Acknowledging alert: alert_id={item.alert_id}, type={item.alert_type}, severity={item.severity}"
            )

            await asyncio.sleep(0.05)
            item.acknowledged_at = datetime.now(UTC)

            return True, {
                "acknowledged_at": item.acknowledged_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Alert acknowledgment failed for {item.alert_id}: {e}")
            return False, {"error": str(e)}

    async def rollback(self, item: AlertAcknowledgment, batch: BatchOperation) -> bool:
        """Rollback an alert acknowledgment (unacknowledge)."""
        try:
            if self._unacknowledge:
                return await self._unacknowledge(item.alert_id)

            logger.info(f"Unacknowledging alert: {item.alert_id}")
            await asyncio.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Rollback failed for alert {item.alert_id}: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# Batch Executor
# ─────────────────────────────────────────────────────────────────────────────


class BatchExecutor:
    """
    Batch operation executor with progress tracking and rollback capabilities.

    منفذ عمليات الدفعات مع تتبع التقدم وإمكانية التراجع

    Features:
        - Progress callbacks for real-time updates
        - Partial failure handling
        - Configurable rollback strategies
        - Concurrent item processing
        - Bilingual messages (English/Arabic)

    Example:
        executor = BatchExecutor()

        # Set up callbacks
        async def on_progress(progress: BatchProgress):
            print(f"Progress: {progress.percent_complete}%")

        executor.set_progress_callback(on_progress)

        # Execute batch
        result = await executor.execute(batch)
        print(f"Completed: {result.completed_items}/{result.total_items}")
    """

    def __init__(
        self,
        field_processor: FieldOperationProcessor | None = None,
        harvest_processor: HarvestEntryProcessor | None = None,
        equipment_processor: EquipmentAssignmentProcessor | None = None,
        alert_processor: AlertAcknowledgmentProcessor | None = None,
    ):
        """
        Initialize BatchExecutor with item processors.

        Args:
            field_processor: Processor for field operations
            harvest_processor: Processor for harvest entries
            equipment_processor: Processor for equipment assignments
            alert_processor: Processor for alert acknowledgments
        """
        self._field_processor = field_processor or FieldOperationProcessor()
        self._harvest_processor = harvest_processor or HarvestEntryProcessor()
        self._equipment_processor = equipment_processor or EquipmentAssignmentProcessor()
        self._alert_processor = alert_processor or AlertAcknowledgmentProcessor()

        self._progress_callback: ProgressCallback | None = None
        self._item_callback: ItemCallback | None = None
        self._status_callback: StatusCallback | None = None

        self._cancel_requested = False
        self._pause_requested = False

    def set_progress_callback(self, callback: ProgressCallback):
        """Set callback for progress updates."""
        self._progress_callback = callback

    def set_item_callback(self, callback: ItemCallback):
        """Set callback for individual item completion."""
        self._item_callback = callback

    def set_status_callback(self, callback: StatusCallback):
        """Set callback for batch status changes."""
        self._status_callback = callback

    def request_cancel(self):
        """Request cancellation of the running batch."""
        self._cancel_requested = True
        logger.info("Batch cancellation requested")

    def request_pause(self):
        """Request pause of the running batch."""
        self._pause_requested = True
        logger.info("Batch pause requested")

    def request_resume(self):
        """Request resume of a paused batch."""
        self._pause_requested = False
        logger.info("Batch resume requested")

    async def _notify_progress(self, progress: BatchProgress):
        """Notify progress callback."""
        if self._progress_callback:
            result = self._progress_callback(progress)
            if asyncio.iscoroutine(result):
                await result

    async def _notify_item(self, item: Any, status: ItemStatus, error: str | None):
        """Notify item callback."""
        if self._item_callback:
            result = self._item_callback(item, status, error)
            if asyncio.iscoroutine(result):
                await result

    async def _notify_status(self, status: BatchStatus, message: BilingualMessage):
        """Notify status callback."""
        if self._status_callback:
            result = self._status_callback(status, message)
            if asyncio.iscoroutine(result):
                await result

    def _get_processor(self, operation_type: BatchOperationType) -> ItemProcessor:
        """Get the appropriate processor for an operation type."""
        if operation_type in [
            BatchOperationType.IRRIGATION,
            BatchOperationType.SPRAYING,
            BatchOperationType.FERTILIZATION,
        ]:
            return self._field_processor
        elif operation_type == BatchOperationType.HARVEST:
            return self._harvest_processor
        elif operation_type == BatchOperationType.EQUIPMENT_ASSIGN:
            return self._equipment_processor
        elif operation_type == BatchOperationType.ALERT_ACK:
            return self._alert_processor
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")

    async def execute(self, batch: BatchOperation) -> BatchResult:
        """
        Execute a batch operation.

        تنفيذ عملية دفعة

        Args:
            batch: The batch operation to execute

        Returns:
            BatchResult with execution statistics
        """
        self._cancel_requested = False
        self._pause_requested = False

        if not batch.tenant_id:
            raise BatchExecutionError(
                "tenant_id is required for batch execution",
                "معرف المستأجر مطلوب لتنفيذ الدفعة",
            )

        start_time = time.time()
        items = batch.get_items()
        total_items = len(items)

        if total_items == 0:
            return BatchResult(
                batch_id=batch.id,
                status=BatchStatus.COMPLETED,
                total_items=0,
                message=BilingualMessage(en="No items to process", ar="لا توجد عناصر للمعالجة"),
            )

        # Initialize batch state
        batch.status = BatchStatus.IN_PROGRESS
        batch.started_at = datetime.now(UTC)
        batch.progress = BatchProgress(total_items=total_items)
        batch.add_audit_entry("batch_started", {"total_items": total_items})

        await self._notify_status(BatchStatus.IN_PROGRESS, BATCH_MESSAGES["started"])

        processor = self._get_processor(batch.operation_type)
        config = batch.config
        errors: list[dict[str, Any]] = []

        completed = 0
        failed = 0
        skipped = 0

        try:
            # Process items with concurrency control
            if config.max_concurrent > 1:
                completed, failed, skipped, errors = await self._execute_concurrent(batch, items, processor, config)
            else:
                completed, failed, skipped, errors = await self._execute_sequential(batch, items, processor, config)

            # Check for cancellation
            if self._cancel_requested:
                batch.status = BatchStatus.CANCELLED
                batch.cancelled_at = datetime.now(UTC)
                raise BatchCancelledException("Batch operation was cancelled", "تم إلغاء عملية الدفعة")

            # Determine final status
            if failed == 0:
                batch.status = BatchStatus.COMPLETED
                message = BATCH_MESSAGES["completed"]
            elif completed > 0:
                batch.status = BatchStatus.PARTIALLY_COMPLETED
                message = BATCH_MESSAGES["partially_completed"]
            else:
                batch.status = BatchStatus.FAILED
                message = BATCH_MESSAGES["failed"]

            # Check if rollback is needed
            rollback_performed = False
            rollback_successful = None

            if failed > 0 and self._should_rollback(batch, failed, total_items):
                rollback_performed = True
                rollback_successful = await self._perform_rollback(batch, items, processor)
                if rollback_successful:
                    batch.status = BatchStatus.ROLLED_BACK
                    message = BATCH_MESSAGES["rolled_back"]

        except BatchCancelledException as e:
            message = BATCH_MESSAGES["cancelled"]
            batch.error_message = e.message
            batch.error_message_ar = e.message_ar
            rollback_performed = False
            rollback_successful = None

        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            batch.status = BatchStatus.FAILED
            batch.error_message = str(e)
            message = BATCH_MESSAGES["failed"]
            rollback_performed = False
            rollback_successful = None

        # Finalize
        batch.completed_at = datetime.now(UTC)
        duration = time.time() - start_time

        batch.add_audit_entry(
            "batch_completed",
            {
                "status": batch.status.value,
                "completed": completed,
                "failed": failed,
                "skipped": skipped,
                "duration_seconds": round(duration, 2),
            },
        )

        await self._notify_status(batch.status, message)

        return BatchResult(
            batch_id=batch.id,
            status=batch.status,
            total_items=total_items,
            completed_items=completed,
            failed_items=failed,
            skipped_items=skipped,
            duration_seconds=duration,
            errors=errors,
            rollback_performed=rollback_performed,
            rollback_successful=rollback_successful,
            message=message,
        )

    async def _execute_sequential(
        self,
        batch: BatchOperation,
        items: list[Any],
        processor: ItemProcessor,
        config: BatchConfig,
    ) -> tuple[int, int, int, list[dict[str, Any]]]:
        """Execute items sequentially."""
        completed = 0
        failed = 0
        skipped = 0
        errors: list[dict[str, Any]] = []

        for idx, item in enumerate(items):
            if self._cancel_requested:
                break

            # Handle pause
            while self._pause_requested:
                await asyncio.sleep(0.5)

            # Update progress
            batch.progress.current_item_index = idx
            batch.progress.current_item_id = item.id
            await self._notify_progress(batch.progress)

            # Process item with retry
            success, error = await self._process_item_with_retry(item, batch, processor, config)

            if success:
                completed += 1
                item.status = ItemStatus.COMPLETED
            else:
                failed += 1
                item.status = ItemStatus.FAILED
                item.error_message = error
                errors.append(
                    {
                        "item_id": item.id,
                        "error": error,
                    }
                )

                if config.stop_on_error:
                    # Mark remaining items as skipped
                    for remaining in items[idx + 1 :]:
                        remaining.status = ItemStatus.SKIPPED
                        skipped += 1
                    break

                # Check failure threshold
                if self._check_threshold_exceeded(failed, len(items), config):
                    # Mark remaining as skipped
                    for remaining in items[idx + 1 :]:
                        remaining.status = ItemStatus.SKIPPED
                        skipped += 1
                    break

            # Update progress
            batch.progress.update(len(items), completed, failed, skipped)
            await self._notify_progress(batch.progress)
            await self._notify_item(item, item.status, error if not success else None)

        return completed, failed, skipped, errors

    async def _execute_concurrent(
        self,
        batch: BatchOperation,
        items: list[Any],
        processor: ItemProcessor,
        config: BatchConfig,
    ) -> tuple[int, int, int, list[dict[str, Any]]]:
        """Execute items concurrently with semaphore control."""
        semaphore = asyncio.Semaphore(config.max_concurrent)
        completed = 0
        failed = 0
        skipped = 0
        errors: list[dict[str, Any]] = []
        lock = asyncio.Lock()

        async def process_with_semaphore(idx: int, item: Any):
            nonlocal completed, failed, skipped

            async with semaphore:
                if self._cancel_requested:
                    async with lock:
                        item.status = ItemStatus.SKIPPED
                        skipped += 1
                    return

                # Handle pause
                while self._pause_requested:
                    await asyncio.sleep(0.5)

                success, error = await self._process_item_with_retry(item, batch, processor, config)

                async with lock:
                    if success:
                        completed += 1
                        item.status = ItemStatus.COMPLETED
                    else:
                        failed += 1
                        item.status = ItemStatus.FAILED
                        item.error_message = error
                        errors.append(
                            {
                                "item_id": item.id,
                                "error": error,
                            }
                        )

                    # Update progress
                    batch.progress.update(len(items), completed, failed, skipped)

                await self._notify_progress(batch.progress)
                await self._notify_item(item, item.status, error if not success else None)

        # Create tasks for all items
        tasks = [process_with_semaphore(idx, item) for idx, item in enumerate(items)]

        # Execute all tasks
        await asyncio.gather(*tasks, return_exceptions=True)

        return completed, failed, skipped, errors

    async def _process_item_with_retry(
        self,
        item: Any,
        batch: BatchOperation,
        processor: ItemProcessor,
        config: BatchConfig,
    ) -> tuple[bool, str | None]:
        """Process an item with retry logic."""
        item.status = ItemStatus.IN_PROGRESS
        item.started_at = datetime.now(UTC)

        last_error: str | None = None
        max_attempts = config.max_retries + 1 if config.retry_failed_items else 1

        for attempt in range(max_attempts):
            try:
                # Apply timeout
                success, result_data = await asyncio.wait_for(
                    processor.process(item, batch),
                    timeout=config.timeout_per_item_seconds,
                )

                if success:
                    item.completed_at = datetime.now(UTC)
                    if result_data:
                        item.result_data = result_data
                        # Store rollback data
                        item.rollback_data = result_data.copy()
                    return True, None

                last_error = result_data.get("error", "Unknown error") if result_data else "Processing failed"

            except TimeoutError:
                last_error = f"Timeout after {config.timeout_per_item_seconds}s"
                logger.warning(f"Item {item.id} timed out on attempt {attempt + 1}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Item {item.id} failed on attempt {attempt + 1}: {e}")

            # Wait before retry
            if attempt < max_attempts - 1:
                await asyncio.sleep(config.retry_delay_seconds * (attempt + 1))

        return False, last_error

    def _should_rollback(self, batch: BatchOperation, failed: int, total: int) -> bool:
        """Determine if rollback should be performed."""
        config = batch.config
        strategy = config.rollback_strategy

        if strategy == RollbackStrategy.NONE:
            return False

        if strategy == RollbackStrategy.ON_FIRST_ERROR and failed > 0:
            return True

        if strategy == RollbackStrategy.ON_THRESHOLD:
            failure_percent = (failed / total) * 100 if total > 0 else 0
            return failure_percent >= config.failure_threshold_percent

        return config.rollback_on_failure and failed > 0

    def _check_threshold_exceeded(self, failed: int, total: int, config: BatchConfig) -> bool:
        """Check if failure threshold is exceeded."""
        if config.failure_threshold_percent <= 0:
            return False

        failure_percent = (failed / total) * 100 if total > 0 else 0
        return failure_percent >= config.failure_threshold_percent

    async def _perform_rollback(
        self,
        batch: BatchOperation,
        items: list[Any],
        processor: ItemProcessor,
    ) -> bool:
        """Perform rollback of completed items."""
        logger.info(f"Starting rollback for batch {batch.id}")
        batch.add_audit_entry("rollback_started")
        await self._notify_status(BatchStatus.IN_PROGRESS, BATCH_MESSAGES["rollback_started"])

        rollback_success = True

        # Rollback in reverse order
        for item in reversed(items):
            if item.status == ItemStatus.COMPLETED:
                try:
                    success = await processor.rollback(item, batch)
                    if success:
                        item.status = ItemStatus.ROLLED_BACK
                    else:
                        rollback_success = False
                        logger.error(f"Failed to rollback item {item.id}")
                except Exception as e:
                    rollback_success = False
                    logger.error(f"Rollback exception for item {item.id}: {e}")

        batch.add_audit_entry("rollback_completed", {"success": rollback_success})
        await self._notify_status(
            BatchStatus.ROLLED_BACK if rollback_success else BatchStatus.PARTIALLY_COMPLETED,
            BATCH_MESSAGES["rollback_completed"],
        )

        return rollback_success

    async def rollback(self, batch: BatchOperation) -> bool:
        """
        Manually rollback a batch operation.

        التراجع اليدوي عن عملية دفعة

        Args:
            batch: The batch to rollback

        Returns:
            True if rollback successful
        """
        if batch.status not in [
            BatchStatus.COMPLETED,
            BatchStatus.PARTIALLY_COMPLETED,
            BatchStatus.FAILED,
        ]:
            logger.warning(f"Cannot rollback batch in status {batch.status}")
            return False

        processor = self._get_processor(batch.operation_type)
        items = batch.get_items()

        return await self._perform_rollback(batch, items, processor)

    async def validate_batch(self, batch: BatchOperation) -> tuple[bool, list[dict[str, Any]]]:
        """
        Validate a batch before execution.

        التحقق من صحة الدفعة قبل التنفيذ

        Args:
            batch: The batch to validate

        Returns:
            Tuple of (valid: bool, validation_errors: list)
        """
        processor = self._get_processor(batch.operation_type)
        items = batch.get_items()
        validation_errors: list[dict[str, Any]] = []

        for item in items:
            valid, error = await processor.validate(item, batch)
            if not valid:
                validation_errors.append(
                    {
                        "item_id": item.id,
                        "error": error,
                    }
                )

        return len(validation_errors) == 0, validation_errors


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


async def execute_batch(
    batch: BatchOperation,
    progress_callback: ProgressCallback | None = None,
) -> BatchResult:
    """
    Convenience function to execute a batch operation.

    Args:
        batch: The batch to execute
        progress_callback: Optional callback for progress updates

    Returns:
        BatchResult
    """
    executor = BatchExecutor()
    if progress_callback:
        executor.set_progress_callback(progress_callback)
    return await executor.execute(batch)


async def execute_irrigation_batch(
    field_ids: list[str],
    water_amount_mm: float,
    tenant_id: str,
    progress_callback: ProgressCallback | None = None,
) -> BatchResult:
    """
    Convenience function to execute a batch irrigation operation.

    تنفيذ عملية ري جماعية

    Args:
        field_ids: List of field IDs to irrigate
        water_amount_mm: Water amount in mm
        tenant_id: Tenant ID
        progress_callback: Optional progress callback

    Returns:
        BatchResult
    """
    from .models import IrrigationParams

    batch = BatchOperation(
        tenant_id=tenant_id,
        operation_type=BatchOperationType.IRRIGATION,
        name="Batch Irrigation",
        name_ar="ري جماعي",
        irrigation_params=IrrigationParams(water_amount_mm=water_amount_mm),
        field_items=[FieldOperationItem(field_id=fid) for fid in field_ids],
    )

    return await execute_batch(batch, progress_callback)
