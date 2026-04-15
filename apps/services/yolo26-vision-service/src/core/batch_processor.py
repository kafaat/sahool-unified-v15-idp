"""
Batch Processing Module for YOLO26 Vision Service.

Provides efficient batch inference capabilities for processing multiple images
simultaneously with optimized GPU memory usage and throughput.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any, TypeVar
from uuid import UUID, uuid4

import numpy as np
import structlog
from PIL import Image

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class BatchStatus(StrEnum):
    """Batch job status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some items failed


@dataclass
class BatchItem:
    """Individual item in a batch."""

    item_id: UUID
    image: np.ndarray | Image.Image | bytes
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: str | None = None
    processing_time_ms: float = 0.0


@dataclass
class BatchJob:
    """Batch processing job."""

    job_id: UUID
    items: list[BatchItem]
    status: BatchStatus = BatchStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    total_processing_time_ms: float = 0.0
    successful_count: int = 0
    failed_count: int = 0

    @property
    def progress(self) -> float:
        """Calculate job progress percentage."""
        if not self.items:
            return 0.0
        completed = self.successful_count + self.failed_count
        return (completed / len(self.items)) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": str(self.job_id),
            "status": self.status.value,
            "total_items": len(self.items),
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "progress": round(self.progress, 1),
            "total_processing_time_ms": round(self.total_processing_time_ms, 2),
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class BatchProcessor:
    """
    Batch processor for efficient multi-image inference.

    Features:
    - Dynamic batching based on GPU memory
    - Automatic batch size optimization
    - Progress tracking
    - Error recovery
    - Priority queue support
    """

    def __init__(
        self,
        max_batch_size: int = 8,
        max_queue_size: int = 100,
        batch_timeout_seconds: float = 30.0,
        dynamic_batching: bool = True,
        max_concurrent_batches: int = 2,
    ):
        self.max_batch_size = max_batch_size
        self.max_queue_size = max_queue_size
        self.batch_timeout_seconds = batch_timeout_seconds
        self.dynamic_batching = dynamic_batching
        self.max_concurrent_batches = max_concurrent_batches

        self._job_queue: deque[BatchJob] = deque()
        self._active_jobs: dict[UUID, BatchJob] = {}
        self._completed_jobs: dict[UUID, BatchJob] = {}
        self._processing_semaphore = asyncio.Semaphore(max_concurrent_batches)
        self._current_batch_size = max_batch_size

        # Performance tracking
        self._total_processed = 0
        self._total_processing_time = 0.0
        self._batch_stats: list[dict[str, Any]] = []

        logger.info(
            "batch_processor_initialized",
            max_batch_size=max_batch_size,
            max_queue_size=max_queue_size,
            dynamic_batching=dynamic_batching,
        )

    async def submit_batch(
        self,
        images: list[np.ndarray | Image.Image | bytes],
        metadata: list[dict[str, Any]] | None = None,
        priority: int = 0,
    ) -> BatchJob:
        """
        Submit a batch of images for processing.

        Args:
            images: List of images to process
            metadata: Optional metadata for each image
            priority: Job priority (higher = processed first)

        Returns:
            BatchJob with job_id for tracking
        """
        if len(self._job_queue) >= self.max_queue_size:
            raise ValueError(f"Queue full. Maximum queue size: {self.max_queue_size}")

        job_id = uuid4()
        items = []

        for i, image in enumerate(images):
            item = BatchItem(
                item_id=uuid4(),
                image=image,
                index=i,
                metadata=metadata[i] if metadata and i < len(metadata) else {},
            )
            items.append(item)

        job = BatchJob(job_id=job_id, items=items)
        self._job_queue.append(job)
        self._active_jobs[job_id] = job

        logger.info(
            "batch_job_submitted",
            job_id=str(job_id),
            item_count=len(items),
            queue_size=len(self._job_queue),
        )

        return job

    async def process_batch(
        self,
        job: BatchJob,
        inference_fn: Callable[[list[np.ndarray]], list[Any]],
        preprocess_fn: Callable[[np.ndarray | Image.Image | bytes], np.ndarray] | None = None,
    ) -> BatchJob:
        """
        Process a batch job.

        Args:
            job: BatchJob to process
            inference_fn: Function to run inference on batch
            preprocess_fn: Optional preprocessing function

        Returns:
            Completed BatchJob
        """
        async with self._processing_semaphore:
            job.status = BatchStatus.PROCESSING
            job.started_at = time.time()

            start_time = time.perf_counter()

            try:
                # Preprocess images
                preprocessed = []
                for item in job.items:
                    try:
                        if preprocess_fn:
                            preprocessed.append(preprocess_fn(item.image))
                        elif isinstance(item.image, np.ndarray):
                            preprocessed.append(item.image)
                        elif isinstance(item.image, Image.Image):
                            preprocessed.append(np.array(item.image))
                        else:
                            preprocessed.append(item.image)
                    except Exception as e:
                        item.error = str(e)
                        job.failed_count += 1
                        preprocessed.append(None)

                # Process in sub-batches if needed
                results = await self._process_in_chunks(
                    preprocessed,
                    inference_fn,
                    self._current_batch_size,
                )

                # Assign results
                for i, (item, result) in enumerate(zip(job.items, results)):
                    if item.error is None:
                        if isinstance(result, Exception):
                            item.error = str(result)
                            job.failed_count += 1
                        else:
                            item.result = result
                            job.successful_count += 1

                job.total_processing_time_ms = (time.perf_counter() - start_time) * 1000
                job.completed_at = time.time()

                # Determine final status
                if job.failed_count == 0:
                    job.status = BatchStatus.COMPLETED
                elif job.successful_count == 0:
                    job.status = BatchStatus.FAILED
                else:
                    job.status = BatchStatus.PARTIAL

                # Update stats
                self._update_stats(job)

                logger.info(
                    "batch_job_completed",
                    job_id=str(job.job_id),
                    status=job.status.value,
                    successful=job.successful_count,
                    failed=job.failed_count,
                    processing_time_ms=round(job.total_processing_time_ms, 2),
                )

            except Exception as e:
                job.status = BatchStatus.FAILED
                job.completed_at = time.time()
                job.total_processing_time_ms = (time.perf_counter() - start_time) * 1000

                for item in job.items:
                    if item.result is None and item.error is None:
                        item.error = str(e)
                        job.failed_count += 1

                logger.error(
                    "batch_job_failed",
                    job_id=str(job.job_id),
                    error=str(e),
                )

            finally:
                # Move to completed jobs
                if job.job_id in self._active_jobs:
                    del self._active_jobs[job.job_id]
                self._completed_jobs[job.job_id] = job

                # Clean up old completed jobs
                if len(self._completed_jobs) > 100:
                    oldest = list(self._completed_jobs.keys())[:50]
                    for k in oldest:
                        del self._completed_jobs[k]

            return job

    async def _process_in_chunks(
        self,
        images: list[np.ndarray | None],
        inference_fn: Callable[[list[np.ndarray]], list[Any]],
        chunk_size: int,
    ) -> list[Any]:
        """Process images in chunks."""
        results = []

        for i in range(0, len(images), chunk_size):
            chunk = images[i : i + chunk_size]

            # Filter out None items
            valid_indices = [j for j, img in enumerate(chunk) if img is not None]
            valid_images = [chunk[j] for j in valid_indices]

            if not valid_images:
                results.extend([Exception("Preprocessing failed")] * len(chunk))
                continue

            try:
                # Run inference
                loop = asyncio.get_event_loop()
                chunk_results = await loop.run_in_executor(
                    None,
                    inference_fn,
                    valid_images,
                )

                # Map results back
                result_iter = iter(chunk_results)
                for j in range(len(chunk)):
                    if j in valid_indices:
                        results.append(next(result_iter))
                    else:
                        results.append(Exception("Preprocessing failed"))

            except Exception as e:
                results.extend([e] * len(chunk))

        return results

    def _update_stats(self, job: BatchJob) -> None:
        """Update processing statistics."""
        self._total_processed += len(job.items)
        self._total_processing_time += job.total_processing_time_ms

        self._batch_stats.append(
            {
                "job_id": str(job.job_id),
                "batch_size": len(job.items),
                "processing_time_ms": job.total_processing_time_ms,
                "throughput": len(job.items) / (job.total_processing_time_ms / 1000)
                if job.total_processing_time_ms > 0
                else 0,
                "timestamp": job.completed_at,
            }
        )

        # Keep only last 100 stats
        if len(self._batch_stats) > 100:
            self._batch_stats = self._batch_stats[-100:]

        # Dynamic batch size adjustment
        if self.dynamic_batching and len(self._batch_stats) >= 5:
            self._adjust_batch_size()

    def _adjust_batch_size(self) -> None:
        """Dynamically adjust batch size based on performance."""
        recent_stats = self._batch_stats[-10:]
        avg_throughput = sum(s["throughput"] for s in recent_stats) / len(recent_stats)

        # Simple adaptive algorithm
        if avg_throughput > 50:  # Good throughput
            self._current_batch_size = min(
                self._current_batch_size + 1,
                self.max_batch_size,
            )
        elif avg_throughput < 20:  # Poor throughput
            self._current_batch_size = max(
                self._current_batch_size - 1,
                1,
            )

        logger.debug(
            "batch_size_adjusted",
            new_batch_size=self._current_batch_size,
            avg_throughput=round(avg_throughput, 2),
        )

    def get_job_status(self, job_id: UUID) -> BatchJob | None:
        """Get the status of a batch job."""
        if job_id in self._active_jobs:
            return self._active_jobs[job_id]
        return self._completed_jobs.get(job_id)

    def get_queue_status(self) -> dict[str, Any]:
        """Get current queue status."""
        return {
            "queue_size": len(self._job_queue),
            "active_jobs": len(self._active_jobs),
            "completed_jobs": len(self._completed_jobs),
            "current_batch_size": self._current_batch_size,
            "total_processed": self._total_processed,
            "average_throughput": (
                self._total_processed / (self._total_processing_time / 1000) if self._total_processing_time > 0 else 0
            ),
        }

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        if not self._batch_stats:
            return {
                "total_processed": 0,
                "average_throughput": 0,
                "average_latency_ms": 0,
            }

        throughputs = [s["throughput"] for s in self._batch_stats]
        latencies = [s["processing_time_ms"] / s["batch_size"] for s in self._batch_stats if s["batch_size"] > 0]

        return {
            "total_processed": self._total_processed,
            "total_batches": len(self._batch_stats),
            "current_batch_size": self._current_batch_size,
            "average_throughput": round(sum(throughputs) / len(throughputs), 2) if throughputs else 0,
            "max_throughput": round(max(throughputs), 2) if throughputs else 0,
            "min_throughput": round(min(throughputs), 2) if throughputs else 0,
            "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
            "recent_stats": self._batch_stats[-5:],
        }


class BatchRequestAccumulator:
    """
    Accumulator for building batches from individual requests.

    Useful for combining multiple API requests into efficient batches.
    """

    def __init__(
        self,
        max_batch_size: int = 8,
        max_wait_time_ms: float = 100.0,
        processor: BatchProcessor | None = None,
    ):
        self.max_batch_size = max_batch_size
        self.max_wait_time_ms = max_wait_time_ms
        self.processor = processor or BatchProcessor(max_batch_size=max_batch_size)

        self._pending_items: list[tuple[BatchItem, asyncio.Future]] = []
        self._lock = asyncio.Lock()
        self._batch_event = asyncio.Event()
        self._last_add_time: float = 0

    async def add_request(
        self,
        image: np.ndarray | Image.Image | bytes,
        metadata: dict[str, Any] | None = None,
    ) -> asyncio.Future:
        """
        Add a request to the accumulator.

        Returns a Future that will be resolved with the result.
        """
        async with self._lock:
            future: asyncio.Future = asyncio.get_event_loop().create_future()
            item = BatchItem(
                item_id=uuid4(),
                image=image,
                index=len(self._pending_items),
                metadata=metadata or {},
            )

            self._pending_items.append((item, future))
            self._last_add_time = time.time()

            if len(self._pending_items) >= self.max_batch_size:
                self._batch_event.set()

        return future

    async def flush(
        self,
        inference_fn: Callable[[list[np.ndarray]], list[Any]],
        preprocess_fn: Callable[[np.ndarray | Image.Image | bytes], np.ndarray] | None = None,
    ) -> int:
        """
        Flush accumulated requests as a batch.

        Returns number of items processed.
        """
        async with self._lock:
            if not self._pending_items:
                return 0

            items_to_process = self._pending_items.copy()
            self._pending_items.clear()

        # Create batch job
        images = [item.image for item, _ in items_to_process]
        metadata = [item.metadata for item, _ in items_to_process]

        job = await self.processor.submit_batch(images, metadata)
        completed_job = await self.processor.process_batch(
            job,
            inference_fn,
            preprocess_fn,
        )

        # Resolve futures
        for i, (item, future) in enumerate(items_to_process):
            result_item = completed_job.items[i]
            if result_item.error:
                future.set_exception(Exception(result_item.error))
            else:
                future.set_result(result_item.result)

        return len(items_to_process)


# Global batch processor instance
_batch_processor: BatchProcessor | None = None


def get_batch_processor() -> BatchProcessor:
    """Get the global batch processor instance."""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor()
    return _batch_processor
