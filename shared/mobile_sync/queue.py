"""
Sync Queue Management
=====================
إدارة قائمة انتظار المزامنة

Queue management for offline sync operations with priority-based
scheduling, batching, and retry handling.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import heapq
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .models import (
    SYNC_ERRORS,
    SYNC_MESSAGES,
    BilingualMessage,
    EntityType,
    SyncDirection,
    SyncItem,
    SyncPriority,
    SyncProgress,
    SyncResult,
    SyncSession,
    SyncStatus,
)

# ─────────────────────────────────────────────────────────────────────────────
# Priority Queue Item
# ─────────────────────────────────────────────────────────────────────────────


# Priority weights (lower number = higher priority)
PRIORITY_WEIGHTS = {
    SyncPriority.CRITICAL: 0,
    SyncPriority.HIGH: 1,
    SyncPriority.MEDIUM: 2,
    SyncPriority.LOW: 3,
    SyncPriority.BACKGROUND: 4,
}


@dataclass(order=True)
class PriorityQueueItem:
    """A wrapper for SyncItem with priority ordering."""

    priority_weight: int
    timestamp: float  # For FIFO within same priority
    item: SyncItem = field(compare=False)

    @classmethod
    def from_sync_item(cls, item: SyncItem) -> PriorityQueueItem:
        """Create from a SyncItem."""
        return cls(
            priority_weight=PRIORITY_WEIGHTS.get(item.priority, 2),
            timestamp=item.created_at.timestamp(),
            item=item,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Sync Queue Configuration
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SyncQueueConfig:
    """Configuration for the sync queue."""

    # Queue limits
    max_queue_size: int = 10000  # الحد الأقصى لحجم القائمة
    max_retries: int = 3  # الحد الأقصى لمحاولات الإعادة
    max_batch_size: int = 50  # الحد الأقصى لحجم الدفعة
    max_concurrent_syncs: int = 5  # الحد الأقصى للمزامنات المتزامنة

    # Timeouts
    item_timeout_seconds: float = 60.0  # مهلة كل عنصر
    batch_timeout_seconds: float = 300.0  # مهلة الدفعة

    # Retry configuration
    retry_base_delay_seconds: float = 60.0  # تأخير أساسي للإعادة
    retry_max_delay_seconds: float = 3600.0  # تأخير أقصى للإعادة
    retry_exponential_base: float = 2.0  # أساس التراجع الأسي

    # Batching configuration
    batch_by_entity_type: bool = True  # تجميع حسب نوع الكيان
    batch_by_direction: bool = True  # تجميع حسب الاتجاه

    # Priority configuration
    priority_boost_on_retry: bool = False  # رفع الأولوية عند الإعادة
    auto_expire_hours: int = 72  # انتهاء صلاحية تلقائي

    # Deduplication
    deduplicate_pending: bool = True  # إزالة المكرر في الانتظار
    merge_pending_updates: bool = True  # دمج التحديثات المنتظرة

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_queue_size": self.max_queue_size,
            "max_retries": self.max_retries,
            "max_batch_size": self.max_batch_size,
            "max_concurrent_syncs": self.max_concurrent_syncs,
            "item_timeout_seconds": self.item_timeout_seconds,
            "batch_timeout_seconds": self.batch_timeout_seconds,
            "retry_base_delay_seconds": self.retry_base_delay_seconds,
            "retry_max_delay_seconds": self.retry_max_delay_seconds,
            "retry_exponential_base": self.retry_exponential_base,
            "batch_by_entity_type": self.batch_by_entity_type,
            "batch_by_direction": self.batch_by_direction,
            "priority_boost_on_retry": self.priority_boost_on_retry,
            "auto_expire_hours": self.auto_expire_hours,
            "deduplicate_pending": self.deduplicate_pending,
            "merge_pending_updates": self.merge_pending_updates,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Sync Queue
# ─────────────────────────────────────────────────────────────────────────────


class SyncQueue:
    """
    Priority-based sync queue with batching and retry support.

    قائمة انتظار المزامنة القائمة على الأولوية مع دعم التجميع والإعادة.
    """

    def __init__(
        self,
        config: SyncQueueConfig | None = None,
        tenant_id: str = "",
        device_id: str = "",
    ):
        """Initialize the sync queue."""
        if not tenant_id:
            raise ValueError("tenant_id is required for SyncQueue")
        self.config = config or SyncQueueConfig()
        self.tenant_id = tenant_id
        self.device_id = device_id

        # Priority queue (heap)
        self._queue: list[PriorityQueueItem] = []
        self._queue_lock = asyncio.Lock()

        # Item tracking
        self._items_by_id: dict[str, SyncItem] = {}
        self._items_by_entity: dict[str, list[str]] = defaultdict(list)

        # Status tracking
        self._processing: set[str] = set()
        self._completed: dict[str, SyncItem] = {}
        self._failed: dict[str, SyncItem] = {}
        self._conflicts: dict[str, SyncItem] = {}

        # Statistics
        self._stats = {
            "total_enqueued": 0,
            "total_processed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "total_conflicts": 0,
            "total_retries": 0,
        }

        # Event callbacks
        self._on_item_added: list[Callable[[SyncItem], Awaitable[None]]] = []
        self._on_item_processed: list[Callable[[SyncItem, bool], Awaitable[None]]] = []
        self._on_conflict_detected: list[Callable[[SyncItem], Awaitable[None]]] = []
        self._on_queue_empty: list[Callable[[], Awaitable[None]]] = []

    @property
    def size(self) -> int:
        """Get current queue size."""
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    @property
    def is_full(self) -> bool:
        """Check if queue is at capacity."""
        return len(self._queue) >= self.config.max_queue_size

    @property
    def pending_count(self) -> int:
        """Get count of pending items."""
        return len(self._queue)

    @property
    def processing_count(self) -> int:
        """Get count of items being processed."""
        return len(self._processing)

    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        return {
            **self._stats,
            "current_queue_size": len(self._queue),
            "processing_count": len(self._processing),
            "completed_count": len(self._completed),
            "failed_count": len(self._failed),
            "conflict_count": len(self._conflicts),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Enqueue Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def enqueue(self, item: SyncItem) -> tuple[bool, BilingualMessage]:
        """
        Add an item to the sync queue.

        إضافة عنصر إلى قائمة انتظار المزامنة.

        Returns:
            Tuple of (success, message)
        """
        async with self._queue_lock:
            # Check queue capacity
            if self.is_full:
                return False, SYNC_ERRORS["quota_exceeded"]

            # Check for duplicates
            if self.config.deduplicate_pending:
                existing = self._find_pending_item(item.entity_id, item.entity_type)
                if existing:
                    if self.config.merge_pending_updates:
                        # Merge the updates
                        self._merge_items(existing, item)
                        return True, SYNC_MESSAGES["queued_for_sync"]
                    else:
                        # Skip duplicate
                        return True, SYNC_MESSAGES["queued_for_sync"]

            # Reject items without tenant_id (H-06: tenant isolation)
            if not item.tenant_id:
                raise ValueError("tenant_id is required for sync items")

            # Set queue metadata
            item.status = SyncStatus.QUEUED
            item.queued_at = datetime.now(UTC)
            item.tenant_id = self.tenant_id
            item.device_id = self.device_id

            # Add to heap
            priority_item = PriorityQueueItem.from_sync_item(item)
            heapq.heappush(self._queue, priority_item)

            # Track by ID and entity
            self._items_by_id[item.id] = item
            self._items_by_entity[f"{item.entity_type.value}:{item.entity_id}"].append(item.id)

            # Update stats
            self._stats["total_enqueued"] += 1

            # Notify listeners
            for callback in self._on_item_added:
                try:
                    await callback(item)
                except Exception:
                    pass  # Don't fail on callback errors

            return True, SYNC_MESSAGES["queued_for_sync"]

    async def enqueue_batch(
        self,
        items: list[SyncItem],
    ) -> tuple[int, int, BilingualMessage]:
        """
        Add multiple items to the queue.

        إضافة عناصر متعددة إلى القائمة.

        Returns:
            Tuple of (success_count, failed_count, message)
        """
        success_count = 0
        failed_count = 0

        for item in items:
            success, _ = await self.enqueue(item)
            if success:
                success_count += 1
            else:
                failed_count += 1

        if failed_count == 0:
            message = SYNC_MESSAGES["queued_for_sync"]
        elif success_count == 0:
            message = SYNC_ERRORS["quota_exceeded"]
        else:
            message = SYNC_MESSAGES["sync_partial"]

        return success_count, failed_count, message

    # ─────────────────────────────────────────────────────────────────────────
    # Dequeue Operations
    # ─────────────────────────────────────────────────────────────────────────

    async def dequeue(self) -> SyncItem | None:
        """
        Get the next item from the queue.

        الحصول على العنصر التالي من القائمة.
        """
        async with self._queue_lock:
            while self._queue:
                priority_item = heapq.heappop(self._queue)
                item = priority_item.item

                # Skip if already processed or cancelled
                if item.id not in self._items_by_id:
                    continue

                # Skip expired items
                if item.is_expired(self.config.auto_expire_hours):
                    self._remove_item(item.id)
                    continue

                # Skip if not ready for retry
                if item.next_retry_at and item.next_retry_at > datetime.now(UTC):
                    # Re-add to queue
                    heapq.heappush(self._queue, priority_item)
                    continue

                # Mark as processing
                item.status = SyncStatus.SYNCING
                self._processing.add(item.id)

                return item

            return None

    async def dequeue_batch(
        self,
        max_size: int | None = None,
        entity_type: EntityType | None = None,
        direction: SyncDirection | None = None,
        priority: SyncPriority | None = None,
    ) -> list[SyncItem]:
        """
        Get a batch of items from the queue.

        الحصول على دفعة من العناصر من القائمة.
        """
        batch_size = min(max_size or self.config.max_batch_size, self.config.max_batch_size)
        batch: list[SyncItem] = []

        while len(batch) < batch_size:
            item = await self.dequeue()
            if item is None:
                break

            # Filter by criteria
            if entity_type and item.entity_type != entity_type:
                await self._requeue_item(item)
                continue
            if direction and item.direction != direction:
                await self._requeue_item(item)
                continue
            if priority and PRIORITY_WEIGHTS[item.priority] > PRIORITY_WEIGHTS[priority]:
                await self._requeue_item(item)
                continue

            batch.append(item)

        return batch

    async def peek(self) -> SyncItem | None:
        """
        Peek at the next item without removing it.

        عرض العنصر التالي دون إزالته.
        """
        async with self._queue_lock:
            if self._queue:
                return self._queue[0].item
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Item Completion
    # ─────────────────────────────────────────────────────────────────────────

    async def mark_completed(self, item_id: str) -> None:
        """
        Mark an item as successfully synced.

        وضع علامة على عنصر كمتزامن بنجاح.
        """
        async with self._queue_lock:
            if item_id in self._items_by_id:
                item = self._items_by_id[item_id]
                item.status = SyncStatus.SYNCED
                item.synced_at = datetime.now(UTC)

                self._processing.discard(item_id)
                self._completed[item_id] = item
                self._remove_item(item_id)

                self._stats["total_processed"] += 1
                self._stats["total_succeeded"] += 1

                # Notify listeners
                for callback in self._on_item_processed:
                    try:
                        await callback(item, True)
                    except Exception:
                        pass

    async def mark_failed(
        self,
        item_id: str,
        error: str,
        error_ar: str | None = None,
        retry: bool = True,
    ) -> None:
        """
        Mark an item as failed.

        وضع علامة على عنصر كفاشل.
        """
        async with self._queue_lock:
            if item_id not in self._items_by_id:
                return

            item = self._items_by_id[item_id]
            item.increment_retry(error, error_ar)
            self._processing.discard(item_id)

            # Check if can retry
            if retry and item.can_retry():
                # Boost priority on retry if configured
                if self.config.priority_boost_on_retry:
                    current_weight = PRIORITY_WEIGHTS[item.priority]
                    if current_weight > 0:
                        for priority, weight in PRIORITY_WEIGHTS.items():
                            if weight == current_weight - 1:
                                item.priority = priority
                                break

                # Re-add to queue with updated retry time
                item.status = SyncStatus.QUEUED
                priority_item = PriorityQueueItem.from_sync_item(item)
                heapq.heappush(self._queue, priority_item)

                self._stats["total_retries"] += 1
            else:
                # Max retries reached
                item.status = SyncStatus.FAILED
                self._failed[item_id] = item
                self._remove_item(item_id)

                self._stats["total_processed"] += 1
                self._stats["total_failed"] += 1

                # Notify listeners
                for callback in self._on_item_processed:
                    try:
                        await callback(item, False)
                    except Exception:
                        pass

    async def mark_conflict(self, item_id: str, conflict_id: str) -> None:
        """
        Mark an item as having a conflict.

        وضع علامة على عنصر كمتعارض.
        """
        async with self._queue_lock:
            if item_id not in self._items_by_id:
                return

            item = self._items_by_id[item_id]
            item.status = SyncStatus.CONFLICT
            item.has_conflict = True
            item.conflict_id = conflict_id

            self._processing.discard(item_id)
            self._conflicts[item_id] = item
            self._remove_item(item_id)

            self._stats["total_processed"] += 1
            self._stats["total_conflicts"] += 1

            # Notify listeners
            for callback in self._on_conflict_detected:
                try:
                    await callback(item)
                except Exception:
                    pass

    # ─────────────────────────────────────────────────────────────────────────
    # Queue Management
    # ─────────────────────────────────────────────────────────────────────────

    async def cancel(self, item_id: str) -> bool:
        """
        Cancel a pending sync item.

        إلغاء عنصر مزامنة منتظر.
        """
        async with self._queue_lock:
            if item_id in self._items_by_id:
                item = self._items_by_id[item_id]
                item.status = SyncStatus.CANCELLED
                self._processing.discard(item_id)
                self._remove_item(item_id)
                return True
            return False

    async def cancel_by_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> int:
        """
        Cancel all pending items for an entity.

        إلغاء جميع العناصر المنتظرة لكيان.
        """
        key = f"{entity_type.value}:{entity_id}"
        cancelled = 0

        async with self._queue_lock:
            item_ids = self._items_by_entity.get(key, []).copy()
            for item_id in item_ids:
                if item_id in self._items_by_id:
                    item = self._items_by_id[item_id]
                    item.status = SyncStatus.CANCELLED
                    self._processing.discard(item_id)
                    self._remove_item(item_id)
                    cancelled += 1

        return cancelled

    async def clear(self) -> int:
        """
        Clear all items from the queue.

        مسح جميع العناصر من القائمة.
        """
        async with self._queue_lock:
            count = len(self._queue)
            self._queue.clear()
            self._items_by_id.clear()
            self._items_by_entity.clear()
            self._processing.clear()
            return count

    async def get_pending_for_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> list[SyncItem]:
        """
        Get all pending items for an entity.

        الحصول على جميع العناصر المنتظرة لكيان.
        """
        key = f"{entity_type.value}:{entity_id}"
        items = []

        async with self._queue_lock:
            item_ids = self._items_by_entity.get(key, [])
            for item_id in item_ids:
                if item_id in self._items_by_id:
                    items.append(self._items_by_id[item_id])

        return items

    def get_progress(self) -> SyncProgress:
        """
        Get current sync progress.

        الحصول على تقدم المزامنة الحالي.
        """
        progress = SyncProgress(
            total_items=self._stats["total_enqueued"],
            pending_items=len(self._queue),
            syncing_items=len(self._processing),
            synced_items=len(self._completed),
            failed_items=len(self._failed),
            conflict_items=len(self._conflicts),
        )
        return progress

    # ─────────────────────────────────────────────────────────────────────────
    # Event Callbacks
    # ─────────────────────────────────────────────────────────────────────────

    def on_item_added(self, callback: Callable[[SyncItem], Awaitable[None]]) -> None:
        """Register callback for when items are added."""
        self._on_item_added.append(callback)

    def on_item_processed(
        self,
        callback: Callable[[SyncItem, bool], Awaitable[None]],
    ) -> None:
        """Register callback for when items are processed."""
        self._on_item_processed.append(callback)

    def on_conflict_detected(
        self,
        callback: Callable[[SyncItem], Awaitable[None]],
    ) -> None:
        """Register callback for when conflicts are detected."""
        self._on_conflict_detected.append(callback)

    def on_queue_empty(self, callback: Callable[[], Awaitable[None]]) -> None:
        """Register callback for when queue becomes empty."""
        self._on_queue_empty.append(callback)

    # ─────────────────────────────────────────────────────────────────────────
    # Internal Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _find_pending_item(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> SyncItem | None:
        """Find a pending item for an entity."""
        key = f"{entity_type.value}:{entity_id}"
        item_ids = self._items_by_entity.get(key, [])

        for item_id in item_ids:
            if item_id in self._items_by_id:
                item = self._items_by_id[item_id]
                if item.status in [SyncStatus.PENDING, SyncStatus.QUEUED]:
                    return item

        return None

    def _merge_items(self, existing: SyncItem, new: SyncItem) -> None:
        """Merge two sync items."""
        # Update local data with new changes
        existing.local_data.update(new.local_data)
        existing.local_modified_at = new.local_modified_at

        # Use higher priority
        if PRIORITY_WEIGHTS[new.priority] < PRIORITY_WEIGHTS[existing.priority]:
            existing.priority = new.priority

        # Update delta data
        if new.delta_data:
            if existing.delta_data:
                existing.delta_data.update(new.delta_data)
            else:
                existing.delta_data = new.delta_data

    def _remove_item(self, item_id: str) -> None:
        """Remove an item from tracking."""
        if item_id in self._items_by_id:
            item = self._items_by_id.pop(item_id)
            key = f"{item.entity_type.value}:{item.entity_id}"
            if key in self._items_by_entity:
                self._items_by_entity[key] = [id for id in self._items_by_entity[key] if id != item_id]

    async def _requeue_item(self, item: SyncItem) -> None:
        """Put an item back in the queue."""
        item.status = SyncStatus.QUEUED
        self._processing.discard(item.id)
        priority_item = PriorityQueueItem.from_sync_item(item)
        heapq.heappush(self._queue, priority_item)


# ─────────────────────────────────────────────────────────────────────────────
# Sync Queue Manager
# ─────────────────────────────────────────────────────────────────────────────


class SyncQueueManager:
    """
    Manager for multiple sync queues (upload/download).

    مدير لقوائم انتظار متعددة للمزامنة (رفع/تنزيل).
    """

    def __init__(
        self,
        config: SyncQueueConfig | None = None,
        tenant_id: str = "",
        device_id: str = "",
    ):
        """Initialize the queue manager."""
        self.config = config or SyncQueueConfig()
        self.tenant_id = tenant_id
        self.device_id = device_id

        # Separate queues for upload and download
        self.upload_queue = SyncQueue(config, tenant_id, device_id)
        self.download_queue = SyncQueue(config, tenant_id, device_id)

        # Active sessions
        self._sessions: dict[str, SyncSession] = {}

        # Processing state
        self._is_running = False
        self._process_task: asyncio.Task | None = None

    async def enqueue(self, item: SyncItem) -> tuple[bool, BilingualMessage]:
        """Add item to appropriate queue based on direction."""
        if item.direction == SyncDirection.UPLOAD:
            return await self.upload_queue.enqueue(item)
        elif item.direction == SyncDirection.DOWNLOAD:
            return await self.download_queue.enqueue(item)
        else:
            # Bidirectional - add to upload queue (server reconciliation)
            return await self.upload_queue.enqueue(item)

    async def start_session(
        self,
        user_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        entity_types: list[EntityType] | None = None,
        priority_threshold: SyncPriority = SyncPriority.LOW,
    ) -> SyncSession:
        """
        Start a new sync session.

        بدء جلسة مزامنة جديدة.
        """
        session = SyncSession(
            tenant_id=self.tenant_id,
            user_id=user_id,
            device_id=self.device_id,
            direction=direction,
            entity_types=entity_types or [],
            priority_threshold=priority_threshold,
            batch_size=self.config.max_batch_size,
        )
        session.started_at = datetime.now(UTC)
        session.status = SyncStatus.SYNCING

        self._sessions[session.id] = session
        return session

    async def end_session(
        self,
        session_id: str,
        status: SyncStatus = SyncStatus.SYNCED,
    ) -> SyncResult:
        """
        End a sync session and return results.

        إنهاء جلسة مزامنة وإرجاع النتائج.
        """
        session = self._sessions.get(session_id)
        if not session:
            return SyncResult(
                session_id=session_id,
                status=SyncStatus.FAILED,
                message=SYNC_ERRORS["invalid_entity"],
            )

        session.status = status
        session.completed_at = datetime.now(UTC)

        # Calculate duration
        duration = 0.0
        if session.started_at:
            duration = (session.completed_at - session.started_at).total_seconds()

        # Determine message
        if status == SyncStatus.SYNCED:
            message = SYNC_MESSAGES["sync_completed"]
        elif status == SyncStatus.CONFLICT:
            message = SYNC_MESSAGES["conflict_detected"]
        else:
            message = SYNC_MESSAGES["sync_failed"]

        result = SyncResult(
            session_id=session_id,
            status=status,
            message=message,
            total_items=session.progress.total_items,
            synced_items=session.progress.synced_items,
            failed_items=session.progress.failed_items,
            conflict_items=session.progress.conflict_items,
            duration_seconds=duration,
            errors=session.errors,
        )

        # Cleanup session
        del self._sessions[session_id]

        return result

    def get_session(self, session_id: str) -> SyncSession | None:
        """Get a sync session by ID."""
        return self._sessions.get(session_id)

    def get_combined_progress(self) -> SyncProgress:
        """Get combined progress from all queues."""
        upload_progress = self.upload_queue.get_progress()
        download_progress = self.download_queue.get_progress()

        return SyncProgress(
            total_items=upload_progress.total_items + download_progress.total_items,
            pending_items=upload_progress.pending_items + download_progress.pending_items,
            syncing_items=upload_progress.syncing_items + download_progress.syncing_items,
            synced_items=upload_progress.synced_items + download_progress.synced_items,
            failed_items=upload_progress.failed_items + download_progress.failed_items,
            conflict_items=upload_progress.conflict_items + download_progress.conflict_items,
            upload_count=upload_progress.total_items,
            download_count=download_progress.total_items,
        )

    def get_combined_stats(self) -> dict[str, Any]:
        """Get combined statistics from all queues."""
        upload_stats = self.upload_queue.get_stats()
        download_stats = self.download_queue.get_stats()

        return {
            "upload": upload_stats,
            "download": download_stats,
            "combined": {
                "total_enqueued": upload_stats["total_enqueued"] + download_stats["total_enqueued"],
                "total_processed": upload_stats["total_processed"] + download_stats["total_processed"],
                "total_succeeded": upload_stats["total_succeeded"] + download_stats["total_succeeded"],
                "total_failed": upload_stats["total_failed"] + download_stats["total_failed"],
                "total_conflicts": upload_stats["total_conflicts"] + download_stats["total_conflicts"],
                "current_queue_size": upload_stats["current_queue_size"] + download_stats["current_queue_size"],
            },
            "active_sessions": len(self._sessions),
        }

    async def clear_all(self) -> dict[str, int]:
        """Clear all queues."""
        upload_cleared = await self.upload_queue.clear()
        download_cleared = await self.download_queue.clear()

        return {
            "upload_cleared": upload_cleared,
            "download_cleared": download_cleared,
            "total_cleared": upload_cleared + download_cleared,
        }
