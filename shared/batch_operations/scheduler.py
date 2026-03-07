"""
Batch Operations Scheduler
==========================
مجدول عمليات الدفعات

Batch scheduling and queue management for agricultural operations.
Supports scheduled execution, priority queuing, and concurrent batch management.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Callable, Coroutine
from uuid import uuid4

from .executor import BatchExecutor, BatchResult, ProgressCallback
from .models import (
    BATCH_MESSAGES,
    BatchOperation,
    BatchPriority,
    BatchStatus,
    BilingualMessage,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class ScheduleType(StrEnum):
    """Types of batch schedules."""

    IMMEDIATE = "immediate"  # فوري
    SCHEDULED = "scheduled"  # مجدول
    RECURRING = "recurring"  # متكرر


class RecurrencePattern(StrEnum):
    """Recurrence patterns for scheduled batches."""

    DAILY = "daily"  # يومي
    WEEKLY = "weekly"  # أسبوعي
    MONTHLY = "monthly"  # شهري
    CUSTOM = "custom"  # مخصص


class QueuePosition(StrEnum):
    """Position of a batch in the queue."""

    FRONT = "front"  # مقدمة القائمة
    BACK = "back"  # نهاية القائمة


# ─────────────────────────────────────────────────────────────────────────────
# Schedule Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BatchSchedule:
    """Schedule configuration for a batch operation."""

    id: str = field(default_factory=lambda: str(uuid4()))
    batch_id: str = ""
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE
    scheduled_time: datetime | None = None
    recurrence_pattern: RecurrencePattern | None = None
    recurrence_interval: int = 1  # عدد الأيام/الأسابيع/الأشهر
    recurrence_end_date: datetime | None = None
    max_executions: int | None = None
    execution_count: int = 0
    last_execution: datetime | None = None
    next_execution: datetime | None = None
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def calculate_next_execution(self) -> datetime | None:
        """Calculate the next execution time based on recurrence pattern."""
        if self.schedule_type == ScheduleType.IMMEDIATE:
            return datetime.now(UTC)

        if self.schedule_type == ScheduleType.SCHEDULED:
            if self.scheduled_time and self.scheduled_time > datetime.now(UTC):
                return self.scheduled_time
            return None

        if self.schedule_type == ScheduleType.RECURRING:
            if not self.recurrence_pattern:
                return None

            if self.max_executions and self.execution_count >= self.max_executions:
                return None

            base_time = self.last_execution or self.scheduled_time or datetime.now(UTC)

            if self.recurrence_pattern == RecurrencePattern.DAILY:
                next_time = base_time + timedelta(days=self.recurrence_interval)
            elif self.recurrence_pattern == RecurrencePattern.WEEKLY:
                next_time = base_time + timedelta(weeks=self.recurrence_interval)
            elif self.recurrence_pattern == RecurrencePattern.MONTHLY:
                # Approximate month as 30 days
                next_time = base_time + timedelta(days=30 * self.recurrence_interval)
            else:
                next_time = base_time + timedelta(days=self.recurrence_interval)

            if self.recurrence_end_date and next_time > self.recurrence_end_date:
                return None

            return next_time

        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "schedule_type": self.schedule_type.value,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "recurrence_pattern": self.recurrence_pattern.value if self.recurrence_pattern else None,
            "recurrence_interval": self.recurrence_interval,
            "recurrence_end_date": self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            "max_executions": self.max_executions,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(order=True)
class QueuedBatch:
    """A batch in the priority queue."""

    priority_value: int = field(compare=True)  # Lower value = higher priority
    scheduled_time: datetime = field(compare=True)
    batch: BatchOperation = field(compare=False)
    schedule: BatchSchedule = field(compare=False)
    enqueued_at: datetime = field(default_factory=lambda: datetime.now(UTC), compare=False)

    @classmethod
    def create(
        cls,
        batch: BatchOperation,
        schedule: BatchSchedule,
    ) -> QueuedBatch:
        """Create a queued batch with calculated priority."""
        priority_map = {
            BatchPriority.URGENT: 0,
            BatchPriority.HIGH: 1,
            BatchPriority.MEDIUM: 2,
            BatchPriority.LOW: 3,
        }
        priority_value = priority_map.get(batch.priority, 2)
        scheduled_time = schedule.next_execution or datetime.now(UTC)

        return cls(
            priority_value=priority_value,
            scheduled_time=scheduled_time,
            batch=batch,
            schedule=schedule,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Scheduler Events
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SchedulerEvent:
    """An event from the scheduler."""

    event_type: str
    batch_id: str
    message: BilingualMessage
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = field(default_factory=dict)


SchedulerCallback = Callable[[SchedulerEvent], Coroutine[Any, Any, None] | None]


# ─────────────────────────────────────────────────────────────────────────────
# Batch Scheduler
# ─────────────────────────────────────────────────────────────────────────────


class BatchScheduler:
    """
    Batch operation scheduler with priority queue management.

    مجدول عمليات الدفعات مع إدارة قائمة الأولويات

    Features:
        - Priority-based queue management
        - Scheduled and recurring batch execution
        - Concurrent batch limit control
        - Pause/resume functionality
        - Event callbacks for monitoring

    Example:
        scheduler = BatchScheduler(max_concurrent_batches=3)

        # Schedule a batch
        schedule = scheduler.schedule_batch(
            batch,
            schedule_type=ScheduleType.SCHEDULED,
            scheduled_time=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        # Start scheduler
        await scheduler.start()

        # Stop scheduler
        await scheduler.stop()
    """

    def __init__(
        self,
        executor: BatchExecutor | None = None,
        max_concurrent_batches: int = 3,
        check_interval_seconds: float = 5.0,
    ):
        """
        Initialize BatchScheduler.

        Args:
            executor: BatchExecutor instance (created if None)
            max_concurrent_batches: Maximum batches to run concurrently
            check_interval_seconds: Interval for checking scheduled batches
        """
        self._executor = executor or BatchExecutor()
        self._max_concurrent = max_concurrent_batches
        self._check_interval = check_interval_seconds

        self._queue: list[QueuedBatch] = []
        self._running_batches: dict[str, asyncio.Task] = {}
        self._schedules: dict[str, BatchSchedule] = {}
        self._batches: dict[str, BatchOperation] = {}
        self._results: dict[str, BatchResult] = {}

        self._running = False
        self._paused = False
        self._scheduler_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

        self._event_callback: SchedulerCallback | None = None
        self._progress_callback: ProgressCallback | None = None

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    @property
    def is_paused(self) -> bool:
        """Check if scheduler is paused."""
        return self._paused

    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return len(self._queue)

    @property
    def running_count(self) -> int:
        """Get number of running batches."""
        return len(self._running_batches)

    def set_event_callback(self, callback: SchedulerCallback):
        """Set callback for scheduler events."""
        self._event_callback = callback

    def set_progress_callback(self, callback: ProgressCallback):
        """Set callback for batch progress updates."""
        self._progress_callback = callback
        self._executor.set_progress_callback(callback)

    async def _emit_event(
        self,
        event_type: str,
        batch_id: str,
        message: BilingualMessage,
        details: dict[str, Any] | None = None,
    ):
        """Emit a scheduler event."""
        event = SchedulerEvent(
            event_type=event_type,
            batch_id=batch_id,
            message=message,
            details=details or {},
        )

        if self._event_callback:
            result = self._event_callback(event)
            if asyncio.iscoroutine(result):
                await result

    def schedule_batch(
        self,
        batch: BatchOperation,
        schedule_type: ScheduleType = ScheduleType.IMMEDIATE,
        scheduled_time: datetime | None = None,
        recurrence_pattern: RecurrencePattern | None = None,
        recurrence_interval: int = 1,
        recurrence_end_date: datetime | None = None,
        max_executions: int | None = None,
    ) -> BatchSchedule:
        """
        Schedule a batch operation.

        جدولة عملية دفعة

        Args:
            batch: The batch operation to schedule
            schedule_type: Type of schedule (immediate, scheduled, recurring)
            scheduled_time: When to execute (for scheduled/recurring)
            recurrence_pattern: Recurrence pattern (for recurring)
            recurrence_interval: Interval for recurrence
            recurrence_end_date: End date for recurring schedule
            max_executions: Maximum number of executions

        Returns:
            BatchSchedule object
        """
        schedule = BatchSchedule(
            batch_id=batch.id,
            schedule_type=schedule_type,
            scheduled_time=scheduled_time,
            recurrence_pattern=recurrence_pattern,
            recurrence_interval=recurrence_interval,
            recurrence_end_date=recurrence_end_date,
            max_executions=max_executions,
        )

        schedule.next_execution = schedule.calculate_next_execution()

        # Store batch and schedule
        self._batches[batch.id] = batch
        self._schedules[schedule.id] = schedule

        # Add to queue
        queued = QueuedBatch.create(batch, schedule)
        heapq.heappush(self._queue, queued)

        batch.status = BatchStatus.QUEUED
        batch.add_audit_entry(
            "batch_scheduled",
            {
                "schedule_id": schedule.id,
                "schedule_type": schedule_type.value,
                "next_execution": schedule.next_execution.isoformat() if schedule.next_execution else None,
            },
        )

        logger.info(f"Batch {batch.id} scheduled: type={schedule_type.value}, next={schedule.next_execution}")

        return schedule

    async def enqueue_batch(
        self,
        batch: BatchOperation,
        position: QueuePosition = QueuePosition.BACK,
    ) -> BatchSchedule:
        """
        Enqueue a batch for immediate execution.

        إضافة دفعة للتنفيذ الفوري

        Args:
            batch: The batch to enqueue
            position: Where to add in queue (front/back)

        Returns:
            BatchSchedule object
        """
        async with self._lock:
            schedule = BatchSchedule(
                batch_id=batch.id,
                schedule_type=ScheduleType.IMMEDIATE,
            )
            schedule.next_execution = datetime.now(UTC)

            self._batches[batch.id] = batch
            self._schedules[schedule.id] = schedule

            queued = QueuedBatch.create(batch, schedule)

            if position == QueuePosition.FRONT:
                # Force high priority for front position
                queued.priority_value = -1
                queued.scheduled_time = datetime.min

            heapq.heappush(self._queue, queued)
            batch.status = BatchStatus.QUEUED

            await self._emit_event(
                "batch_enqueued",
                batch.id,
                BilingualMessage(
                    en=f"Batch enqueued at {position.value}",
                    ar=f"تمت إضافة الدفعة في {position.value}",
                ),
                {"position": position.value},
            )

            return schedule

    async def start(self):
        """
        Start the scheduler.

        بدء المجدول
        """
        if self._running:
            logger.warning("Scheduler is already running")
            return

        self._running = True
        self._paused = False
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

        logger.info("Batch scheduler started")
        await self._emit_event(
            "scheduler_started",
            "",
            BilingualMessage(en="Scheduler started", ar="بدأ المجدول"),
        )

    async def stop(self, wait_for_running: bool = True):
        """
        Stop the scheduler.

        إيقاف المجدول

        Args:
            wait_for_running: Wait for running batches to complete
        """
        self._running = False

        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

        if wait_for_running:
            # Wait for all running batches to complete
            if self._running_batches:
                logger.info(f"Waiting for {len(self._running_batches)} running batches")
                await asyncio.gather(*self._running_batches.values(), return_exceptions=True)

        logger.info("Batch scheduler stopped")
        await self._emit_event(
            "scheduler_stopped",
            "",
            BilingualMessage(en="Scheduler stopped", ar="توقف المجدول"),
        )

    def pause(self):
        """
        Pause the scheduler (stop processing new batches).

        إيقاف المجدول مؤقتاً
        """
        self._paused = True
        logger.info("Batch scheduler paused")

    def resume(self):
        """
        Resume the scheduler.

        استئناف المجدول
        """
        self._paused = False
        logger.info("Batch scheduler resumed")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                if not self._paused:
                    await self._process_queue()
                await asyncio.sleep(self._check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self._check_interval)

    async def _process_queue(self):
        """Process the batch queue."""
        async with self._lock:
            now = datetime.now(UTC)

            # Check for batches ready to run
            while self._queue and len(self._running_batches) < self._max_concurrent:
                # Peek at the highest priority batch
                if not self._queue:
                    break

                queued = self._queue[0]

                # Check if it's time to run
                if queued.scheduled_time and queued.scheduled_time > now:
                    break

                # Pop from queue
                heapq.heappop(self._queue)

                # Start execution
                batch = queued.batch
                schedule = queued.schedule

                if not schedule.enabled:
                    continue

                # Create execution task
                task = asyncio.create_task(self._execute_batch(batch, schedule))
                self._running_batches[batch.id] = task

                logger.info(f"Started batch {batch.id}")
                await self._emit_event(
                    "batch_started",
                    batch.id,
                    BATCH_MESSAGES["started"],
                )

    async def _execute_batch(self, batch: BatchOperation, schedule: BatchSchedule):
        """Execute a batch and handle completion."""
        try:
            result = await self._executor.execute(batch)
            self._results[batch.id] = result

            # Update schedule
            schedule.execution_count += 1
            schedule.last_execution = datetime.now(UTC)

            # Handle recurring schedule
            if schedule.schedule_type == ScheduleType.RECURRING:
                schedule.next_execution = schedule.calculate_next_execution()
                if schedule.next_execution:
                    # Re-queue for next execution
                    # Create a fresh batch copy for recurring
                    new_batch = BatchOperation(
                        tenant_id=batch.tenant_id,
                        operation_type=batch.operation_type,
                        name=batch.name,
                        name_ar=batch.name_ar,
                        description=batch.description,
                        description_ar=batch.description_ar,
                        priority=batch.priority,
                        config=batch.config,
                        irrigation_params=batch.irrigation_params,
                        spraying_params=batch.spraying_params,
                        fertilization_params=batch.fertilization_params,
                    )
                    # Copy items (reset status)
                    for item in batch.field_items:
                        from .models import FieldOperationItem

                        new_batch.field_items.append(
                            FieldOperationItem(
                                field_id=item.field_id,
                                field_name=item.field_name,
                                field_name_ar=item.field_name_ar,
                                area_hectares=item.area_hectares,
                            )
                        )

                    new_schedule = BatchSchedule(
                        batch_id=new_batch.id,
                        schedule_type=ScheduleType.RECURRING,
                        scheduled_time=schedule.next_execution,
                        recurrence_pattern=schedule.recurrence_pattern,
                        recurrence_interval=schedule.recurrence_interval,
                        recurrence_end_date=schedule.recurrence_end_date,
                        max_executions=schedule.max_executions,
                        execution_count=schedule.execution_count,
                    )
                    new_schedule.next_execution = schedule.next_execution

                    self._batches[new_batch.id] = new_batch
                    self._schedules[new_schedule.id] = new_schedule

                    queued = QueuedBatch.create(new_batch, new_schedule)
                    heapq.heappush(self._queue, queued)

                    logger.info(f"Recurring batch re-queued for {schedule.next_execution}")

            await self._emit_event(
                "batch_completed",
                batch.id,
                result.message or BATCH_MESSAGES["completed"],
                {
                    "status": result.status.value,
                    "completed": result.completed_items,
                    "failed": result.failed_items,
                    "duration": result.duration_seconds,
                },
            )

        except Exception as e:
            logger.error(f"Batch execution error: {e}")
            await self._emit_event(
                "batch_failed",
                batch.id,
                BATCH_MESSAGES["failed"],
                {"error": str(e)},
            )

        finally:
            # Remove from running batches
            if batch.id in self._running_batches:
                del self._running_batches[batch.id]

    async def cancel_batch(self, batch_id: str) -> bool:
        """
        Cancel a batch operation.

        إلغاء عملية دفعة

        Args:
            batch_id: ID of the batch to cancel

        Returns:
            True if cancelled successfully
        """
        async with self._lock:
            # Check if running
            if batch_id in self._running_batches:
                self._executor.request_cancel()
                task = self._running_batches[batch_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

                if batch_id in self._batches:
                    self._batches[batch_id].status = BatchStatus.CANCELLED
                    self._batches[batch_id].cancelled_at = datetime.now(UTC)

                await self._emit_event(
                    "batch_cancelled",
                    batch_id,
                    BATCH_MESSAGES["cancelled"],
                )
                return True

            # Check if queued
            for i, queued in enumerate(self._queue):
                if queued.batch.id == batch_id:
                    self._queue.pop(i)
                    heapq.heapify(self._queue)
                    queued.batch.status = BatchStatus.CANCELLED
                    queued.batch.cancelled_at = datetime.now(UTC)

                    await self._emit_event(
                        "batch_cancelled",
                        batch_id,
                        BATCH_MESSAGES["cancelled"],
                    )
                    return True

            return False

    async def pause_batch(self, batch_id: str) -> bool:
        """
        Pause a running batch.

        إيقاف دفعة مؤقتاً

        Args:
            batch_id: ID of the batch to pause

        Returns:
            True if paused successfully
        """
        if batch_id in self._running_batches:
            self._executor.request_pause()
            if batch_id in self._batches:
                self._batches[batch_id].status = BatchStatus.PAUSED

            await self._emit_event(
                "batch_paused",
                batch_id,
                BATCH_MESSAGES["paused"],
            )
            return True
        return False

    async def resume_batch(self, batch_id: str) -> bool:
        """
        Resume a paused batch.

        استئناف دفعة متوقفة

        Args:
            batch_id: ID of the batch to resume

        Returns:
            True if resumed successfully
        """
        if batch_id in self._batches and self._batches[batch_id].status == BatchStatus.PAUSED:
            self._executor.request_resume()
            self._batches[batch_id].status = BatchStatus.IN_PROGRESS

            await self._emit_event(
                "batch_resumed",
                batch_id,
                BATCH_MESSAGES["resumed"],
            )
            return True
        return False

    def get_batch(self, batch_id: str) -> BatchOperation | None:
        """Get a batch by ID."""
        return self._batches.get(batch_id)

    def get_schedule(self, schedule_id: str) -> BatchSchedule | None:
        """Get a schedule by ID."""
        return self._schedules.get(schedule_id)

    def get_result(self, batch_id: str) -> BatchResult | None:
        """Get a batch result by batch ID."""
        return self._results.get(batch_id)

    def get_queue_status(self) -> list[dict[str, Any]]:
        """
        Get status of all queued batches.

        الحصول على حالة جميع الدفعات في القائمة

        Returns:
            List of queue status dictionaries
        """
        status = []
        for queued in sorted(self._queue):
            status.append(
                {
                    "batch_id": queued.batch.id,
                    "name": queued.batch.name,
                    "name_ar": queued.batch.name_ar,
                    "priority": queued.batch.priority.value,
                    "scheduled_time": queued.scheduled_time.isoformat() if queued.scheduled_time else None,
                    "enqueued_at": queued.enqueued_at.isoformat(),
                    "item_count": queued.batch.get_item_count(),
                }
            )
        return status

    def get_running_status(self) -> list[dict[str, Any]]:
        """
        Get status of all running batches.

        الحصول على حالة جميع الدفعات الجارية

        Returns:
            List of running batch status dictionaries
        """
        status = []
        for batch_id in self._running_batches:
            batch = self._batches.get(batch_id)
            if batch:
                status.append(
                    {
                        "batch_id": batch.id,
                        "name": batch.name,
                        "name_ar": batch.name_ar,
                        "status": batch.status.value,
                        "progress": batch.progress.to_dict(),
                        "started_at": batch.started_at.isoformat() if batch.started_at else None,
                    }
                )
        return status

    def get_scheduler_stats(self) -> dict[str, Any]:
        """
        Get scheduler statistics.

        الحصول على إحصائيات المجدول

        Returns:
            Dictionary with scheduler statistics
        """
        return {
            "is_running": self._running,
            "is_paused": self._paused,
            "queue_size": self.queue_size,
            "running_count": self.running_count,
            "max_concurrent": self._max_concurrent,
            "total_batches": len(self._batches),
            "total_schedules": len(self._schedules),
            "completed_results": len(self._results),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions
# ─────────────────────────────────────────────────────────────────────────────


_default_scheduler: BatchScheduler | None = None


async def get_scheduler() -> BatchScheduler:
    """
    Get or create the default scheduler instance.

    الحصول على المجدول الافتراضي
    """
    global _default_scheduler
    if _default_scheduler is None:
        _default_scheduler = BatchScheduler()
    return _default_scheduler


async def schedule_batch(
    batch: BatchOperation,
    schedule_type: ScheduleType = ScheduleType.IMMEDIATE,
    scheduled_time: datetime | None = None,
) -> BatchSchedule:
    """
    Schedule a batch using the default scheduler.

    جدولة دفعة باستخدام المجدول الافتراضي

    Args:
        batch: The batch to schedule
        schedule_type: Type of schedule
        scheduled_time: When to execute

    Returns:
        BatchSchedule
    """
    scheduler = await get_scheduler()
    return scheduler.schedule_batch(
        batch,
        schedule_type=schedule_type,
        scheduled_time=scheduled_time,
    )


async def start_scheduler():
    """Start the default scheduler."""
    scheduler = await get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """Stop the default scheduler."""
    global _default_scheduler
    if _default_scheduler:
        await _default_scheduler.stop()
        _default_scheduler = None
