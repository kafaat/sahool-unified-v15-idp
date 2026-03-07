"""
SAHOOL Terrain Batch Processing Module
======================================
Provides batch processing utilities for terrain-related services.

مودول المعالجة الدفعية للتضاريس

Features:
- Concurrent batch processing with configurable limits
- Progress tracking and reporting
- Error handling and partial failure support
- Async batch processing with rate limiting

Usage:
    from shared.terrain.batch import (
        BatchProcessor,
        BatchRequest,
        BatchResult,
        process_batch,
    )

    processor = BatchProcessor(max_concurrent=5)
    results = await processor.process(requests, handler_func)

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, Coroutine, Generic, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


# =============================================================================
# Batch Configuration
# =============================================================================

# Default batch processing limits
DEFAULT_MAX_CONCURRENT = 5
DEFAULT_BATCH_SIZE = 100
DEFAULT_TIMEOUT_SECONDS = 300  # 5 minutes per item
MAX_BATCH_SIZE = 1000


# =============================================================================
# Batch Status Enum
# =============================================================================


class BatchItemStatus(StrEnum):
    """Status of individual batch item processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class BatchStatus(StrEnum):
    """Overall batch processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"  # Some items failed
    FAILED = "failed"  # All items failed
    CANCELLED = "cancelled"


# =============================================================================
# Batch Data Classes
# =============================================================================


@dataclass
class BatchRequest(Generic[T]):
    """
    A single request in a batch.
    طلب واحد في دفعة.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: T | None = None
    priority: int = 0  # Higher = more priority
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchItemResult(Generic[R]):
    """
    Result of processing a single batch item.
    نتيجة معالجة عنصر دفعة واحد.
    """

    request_id: str
    status: BatchItemStatus
    result: R | None = None
    error: str | None = None
    error_ar: str | None = None
    processing_time_ms: float = 0.0
    completed_at: float = field(default_factory=time.time)


@dataclass
class BatchResult(Generic[R]):
    """
    Overall result of batch processing.
    النتيجة الإجمالية للمعالجة الدفعية.
    """

    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: BatchStatus = BatchStatus.PENDING
    total_items: int = 0
    success_count: int = 0
    error_count: int = 0
    skipped_count: int = 0
    results: list[BatchItemResult[R]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    total_processing_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0

    def add_result(self, item_result: BatchItemResult[R]) -> None:
        """Add an item result to the batch."""
        self.results.append(item_result)

        if item_result.status == BatchItemStatus.SUCCESS:
            self.success_count += 1
        elif item_result.status == BatchItemStatus.ERROR:
            self.error_count += 1
        elif item_result.status == BatchItemStatus.SKIPPED:
            self.skipped_count += 1

    def finalize(self) -> None:
        """Finalize batch processing and calculate statistics."""
        self.completed_at = time.time()
        self.total_processing_time_ms = (self.completed_at - self.started_at) * 1000
        self.total_items = len(self.results)

        if self.total_items > 0:
            total_item_time = sum(r.processing_time_ms for r in self.results)
            self.average_processing_time_ms = total_item_time / self.total_items

        # Determine overall status
        if self.error_count == self.total_items:
            self.status = BatchStatus.FAILED
        elif self.error_count > 0:
            self.status = BatchStatus.PARTIAL
        else:
            self.status = BatchStatus.COMPLETED


# =============================================================================
# Pydantic Models for API
# =============================================================================


class BatchRequestModel(BaseModel):
    """API model for batch request."""

    items: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=MAX_BATCH_SIZE,
        description="List of items to process | قائمة العناصر للمعالجة",
    )
    options: dict[str, Any] = Field(
        default_factory=dict, description="Batch processing options | خيارات المعالجة الدفعية"
    )


class BatchItemResultModel(BaseModel):
    """API model for batch item result."""

    request_id: str = Field(..., description="Request identifier | معرف الطلب")
    status: str = Field(..., description="Processing status | حالة المعالجة")
    result: Any = Field(None, description="Processing result | نتيجة المعالجة")
    error: str | None = Field(None, description="Error message | رسالة الخطأ")
    error_ar: str | None = Field(None, description="Error message (Arabic) | رسالة الخطأ بالعربية")
    processing_time_ms: float = Field(0.0, description="Processing time in milliseconds | وقت المعالجة بالمللي ثانية")


class BatchResultModel(BaseModel):
    """API model for batch result."""

    batch_id: str = Field(..., description="Batch identifier | معرف الدفعة")
    status: str = Field(..., description="Overall status | الحالة الإجمالية")
    total_items: int = Field(..., description="Total items processed | إجمالي العناصر المعالجة")
    success_count: int = Field(..., description="Successful items | العناصر الناجحة")
    error_count: int = Field(..., description="Failed items | العناصر الفاشلة")
    results: list[BatchItemResultModel] = Field(
        default_factory=list, description="Individual results | النتائج الفردية"
    )
    total_processing_time_ms: float = Field(0.0, description="Total processing time | إجمالي وقت المعالجة")
    average_processing_time_ms: float = Field(
        0.0, description="Average processing time per item | متوسط وقت المعالجة لكل عنصر"
    )


# =============================================================================
# Batch Processor
# =============================================================================


class BatchProcessor(Generic[T, R]):
    """
    Async batch processor with concurrency control.
    معالج دفعي غير متزامن مع التحكم في التزامن.

    Args:
        max_concurrent: Maximum concurrent operations
        timeout_seconds: Timeout per item in seconds
        on_progress: Optional progress callback

    Usage:
        processor = BatchProcessor(max_concurrent=5)

        async def process_item(item):
            # ... processing logic ...
            return result

        batch_result = await processor.process(items, process_item)
    """

    def __init__(
        self,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        on_progress: Callable[[int, int, BatchItemStatus], None] | None = None,
    ):
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.on_progress = on_progress
        self._semaphore: asyncio.Semaphore | None = None

    async def process(
        self,
        requests: list[BatchRequest[T]],
        handler: Callable[[T], Coroutine[Any, Any, R]],
    ) -> BatchResult[R]:
        """
        Process a batch of requests concurrently.
        معالجة دفعة من الطلبات بشكل متزامن.

        Args:
            requests: List of batch requests
            handler: Async function to process each item

        Returns:
            BatchResult with all item results
        """
        batch_result = BatchResult[R]()
        batch_result.total_items = len(requests)

        if not requests:
            batch_result.status = BatchStatus.COMPLETED
            batch_result.finalize()
            return batch_result

        batch_result.status = BatchStatus.PROCESSING
        self._semaphore = asyncio.Semaphore(self.max_concurrent)

        # Sort by priority (higher first)
        sorted_requests = sorted(requests, key=lambda r: -r.priority)

        # Create tasks for all requests
        tasks = [self._process_item(request, handler, batch_result) for request in sorted_requests]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        batch_result.finalize()
        return batch_result

    async def _process_item(
        self,
        request: BatchRequest[T],
        handler: Callable[[T], Coroutine[Any, Any, R]],
        batch_result: BatchResult[R],
    ) -> None:
        """Process a single item with semaphore control."""
        if self._semaphore is None:
            return

        item_result = BatchItemResult[R](
            request_id=request.id,
            status=BatchItemStatus.PROCESSING,
        )

        start_time = time.time()

        async with self._semaphore:
            try:
                if request.data is None:
                    item_result.status = BatchItemStatus.SKIPPED
                    item_result.error = "No data provided"
                    item_result.error_ar = "لم يتم تقديم بيانات"
                else:
                    # Process with timeout
                    result = await asyncio.wait_for(
                        handler(request.data),
                        timeout=self.timeout_seconds,
                    )
                    item_result.result = result
                    item_result.status = BatchItemStatus.SUCCESS

            except TimeoutError:
                item_result.status = BatchItemStatus.TIMEOUT
                item_result.error = f"Processing timed out after {self.timeout_seconds}s"
                item_result.error_ar = f"انتهت مهلة المعالجة بعد {self.timeout_seconds} ثانية"
                logger.warning(f"Batch item {request.id} timed out")

            except Exception as e:
                item_result.status = BatchItemStatus.ERROR
                item_result.error = str(e)
                item_result.error_ar = "خطأ في معالجة الطلب"
                logger.error(f"Batch item {request.id} failed: {e}")

            finally:
                item_result.processing_time_ms = (time.time() - start_time) * 1000
                item_result.completed_at = time.time()
                batch_result.add_result(item_result)

                # Call progress callback if provided
                if self.on_progress:
                    processed = batch_result.success_count + batch_result.error_count
                    self.on_progress(processed, batch_result.total_items, item_result.status)


# =============================================================================
# Convenience Functions
# =============================================================================


async def process_batch(
    items: list[T],
    handler: Callable[[T], Coroutine[Any, Any, R]],
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> BatchResult[R]:
    """
    Convenience function for batch processing.
    دالة مساعدة للمعالجة الدفعية.

    Args:
        items: List of items to process
        handler: Async function to process each item
        max_concurrent: Maximum concurrent operations
        timeout_seconds: Timeout per item

    Returns:
        BatchResult with all results
    """
    requests = [BatchRequest(data=item, id=str(i)) for i, item in enumerate(items)]

    processor = BatchProcessor[T, R](
        max_concurrent=max_concurrent,
        timeout_seconds=timeout_seconds,
    )

    return await processor.process(requests, handler)


async def process_batch_with_priority(
    items: list[tuple[T, int]],
    handler: Callable[[T], Coroutine[Any, Any, R]],
    max_concurrent: int = DEFAULT_MAX_CONCURRENT,
) -> BatchResult[R]:
    """
    Process batch with priority ordering.
    معالجة دفعة مع ترتيب الأولوية.

    Args:
        items: List of (item, priority) tuples
        handler: Async function to process each item
        max_concurrent: Maximum concurrent operations

    Returns:
        BatchResult with all results
    """
    requests = [BatchRequest(data=item, priority=priority, id=str(i)) for i, (item, priority) in enumerate(items)]

    processor = BatchProcessor[T, R](max_concurrent=max_concurrent)
    return await processor.process(requests, handler)


def create_batch_requests(
    items: list[dict[str, Any]],
    field_id_key: str = "field_id",
) -> list[BatchRequest[dict[str, Any]]]:
    """
    Create batch requests from a list of dictionaries.
    إنشاء طلبات دفعية من قائمة قواميس.

    Args:
        items: List of request data dictionaries
        field_id_key: Key to use for request ID

    Returns:
        List of BatchRequest objects
    """
    requests = []
    for item in items:
        request_id = item.get(field_id_key, str(uuid.uuid4()))
        requests.append(
            BatchRequest(
                id=request_id,
                data=item,
                metadata={"source_field_id": request_id},
            )
        )
    return requests


# =============================================================================
# Batch Result Formatting
# =============================================================================


def format_batch_result(
    batch_result: BatchResult[Any],
    include_all_results: bool = True,
) -> dict[str, Any]:
    """
    Format batch result for API response.
    تنسيق نتيجة الدفعة لاستجابة API.

    Args:
        batch_result: BatchResult object
        include_all_results: Include all individual results

    Returns:
        Formatted response dictionary
    """
    response = {
        "batch_id": batch_result.batch_id,
        "status": batch_result.status.value,
        "summary": {
            "total_items": batch_result.total_items,
            "success_count": batch_result.success_count,
            "error_count": batch_result.error_count,
            "skipped_count": batch_result.skipped_count,
        },
        "timing": {
            "started_at": datetime.fromtimestamp(batch_result.started_at).isoformat(),
            "completed_at": (
                datetime.fromtimestamp(batch_result.completed_at).isoformat() if batch_result.completed_at else None
            ),
            "total_processing_time_ms": batch_result.total_processing_time_ms,
            "average_processing_time_ms": batch_result.average_processing_time_ms,
        },
    }

    if include_all_results:
        response["results"] = [
            {
                "request_id": r.request_id,
                "status": r.status.value,
                "result": r.result,
                "error": r.error,
                "error_ar": r.error_ar,
                "processing_time_ms": r.processing_time_ms,
            }
            for r in batch_result.results
        ]
    else:
        # Only include errors
        response["errors"] = [
            {
                "request_id": r.request_id,
                "error": r.error,
                "error_ar": r.error_ar,
            }
            for r in batch_result.results
            if r.status in (BatchItemStatus.ERROR, BatchItemStatus.TIMEOUT)
        ]

    return response


# =============================================================================
# Export all
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_MAX_CONCURRENT",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_BATCH_SIZE",
    # Enums
    "BatchItemStatus",
    "BatchStatus",
    # Data classes
    "BatchRequest",
    "BatchItemResult",
    "BatchResult",
    # Pydantic models
    "BatchRequestModel",
    "BatchItemResultModel",
    "BatchResultModel",
    # Processor
    "BatchProcessor",
    # Convenience functions
    "process_batch",
    "process_batch_with_priority",
    "create_batch_requests",
    "format_batch_result",
]
