"""
Unit tests for apps/kernel/common/queue/task_queue.py
Tests task queue management with mocked Redis.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import json

from apps.kernel.common.queue.task_queue import (
    TaskQueue,
    Task,
    TaskType,
    TaskStatus,
    TaskPriority,
)


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock()
    redis.hgetall.return_value = {}
    redis.zrangebyscore.return_value = []
    redis.scan_iter.return_value = []
    return redis


@pytest.fixture
def task_queue(mock_redis):
    """Create a TaskQueue instance with mocked Redis."""
    return TaskQueue(redis_client=mock_redis, namespace="test")


class TestTaskDataModel:
    """Tests for Task data model."""

    def test_task_creation(self):
        """Test task creation with required fields."""
        now = datetime.utcnow()
        task = Task(
            task_id="task123",
            task_type=TaskType.NDVI_CALCULATION,
            payload={"field_id": "field456"},
            priority=5,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

        assert task.task_id == "task123"
        assert task.task_type == TaskType.NDVI_CALCULATION
        assert task.priority == 5
        assert task.status == TaskStatus.PENDING

    def test_task_to_dict(self):
        """Test task serialization to dictionary."""
        now = datetime.utcnow()
        task = Task(
            task_id="task123",
            task_type=TaskType.DISEASE_DETECTION,
            payload={"image_url": "https://example.com/img.jpg"},
            priority=8,
            status=TaskStatus.PROCESSING,
            created_at=now,
            updated_at=now,
        )

        task_dict = task.to_dict()

        assert task_dict["task_id"] == "task123"
        assert task_dict["task_type"] == "disease_detection"
        assert task_dict["status"] == "processing"
        assert isinstance(task_dict["created_at"], str)  # ISO format

    def test_task_from_dict(self):
        """Test task deserialization from dictionary."""
        now = datetime.utcnow()
        task_dict = {
            "task_id": "task789",
            "task_type": "notification_send",
            "payload": {"user_id": "user123", "message": "Hello"},
            "priority": 3,
            "status": "completed",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "retry_count": 0,
            "max_retries": 3,
            "timeout_seconds": 300,
        }

        task = Task.from_dict(task_dict)

        assert task.task_id == "task789"
        assert task.task_type == TaskType.NOTIFICATION_SEND
        assert task.status == TaskStatus.COMPLETED
        assert isinstance(task.created_at, datetime)


class TestTaskTypes:
    """Tests for TaskType enum."""

    def test_all_task_types_exist(self):
        """Test that all expected task types are defined."""
        expected_types = [
            "satellite_image_processing",
            "ndvi_calculation",
            "disease_detection",
            "report_generation",
            "notification_send",
            "data_export",
            "model_inference",
        ]

        for type_value in expected_types:
            assert TaskType(type_value) is not None

    def test_task_type_values(self):
        """Test task type values."""
        assert TaskType.NDVI_CALCULATION.value == "ndvi_calculation"
        assert TaskType.DISEASE_DETECTION.value == "disease_detection"


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_all_statuses_exist(self):
        """Test that all expected statuses are defined."""
        expected_statuses = [
            "pending",
            "processing",
            "completed",
            "failed",
            "cancelled",
            "timeout",
        ]

        for status_value in expected_statuses:
            assert TaskStatus(status_value) is not None


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_priority_values(self):
        """Test priority level values."""
        assert TaskPriority.LOW.value == 3
        assert TaskPriority.NORMAL.value == 5
        assert TaskPriority.HIGH.value == 8
        assert TaskPriority.CRITICAL.value == 10

    def test_priority_ordering(self):
        """Test that priorities are in correct order."""
        assert TaskPriority.LOW.value < TaskPriority.NORMAL.value
        assert TaskPriority.NORMAL.value < TaskPriority.HIGH.value
        assert TaskPriority.HIGH.value < TaskPriority.CRITICAL.value


class TestTaskQueueEnqueue:
    """Tests for TaskQueue.enqueue method."""

    def test_enqueue_returns_task_id(self, task_queue, mock_redis):
        """Test that enqueue returns a task ID."""
        task_id = task_queue.enqueue(
            task_type=TaskType.NDVI_CALCULATION,
            payload={"field_id": "field123"},
        )

        assert task_id is not None
        assert len(task_id) == 36  # UUID format

    def test_enqueue_saves_task_data(self, task_queue, mock_redis):
        """Test that task data is saved to Redis."""
        task_queue.enqueue(
            task_type=TaskType.REPORT_GENERATION,
            payload={"report_type": "monthly"},
        )

        assert mock_redis.hset.called

    def test_enqueue_adds_to_priority_queue(self, task_queue, mock_redis):
        """Test that task is added to priority queue."""
        task_queue.enqueue(
            task_type=TaskType.DISEASE_DETECTION,
            payload={"image_id": "img123"},
            priority=TaskPriority.HIGH.value,
        )

        assert mock_redis.zadd.called
        # Verify the queue key includes priority
        call_args = mock_redis.zadd.call_args
        assert "queue:8" in str(call_args)

    def test_enqueue_updates_statistics(self, task_queue, mock_redis):
        """Test that statistics are updated on enqueue."""
        task_queue.enqueue(
            task_type=TaskType.NOTIFICATION_SEND,
            payload={"user_id": "user123"},
        )

        # Should update total_enqueued and type-specific counter
        assert mock_redis.hincrby.call_count >= 2

    def test_enqueue_with_custom_priority(self, task_queue, mock_redis):
        """Test enqueue with custom priority."""
        task_queue.enqueue(
            task_type=TaskType.DATA_EXPORT,
            payload={"format": "csv"},
            priority=10,
        )

        assert mock_redis.zadd.called

    def test_enqueue_with_scheduled_time(self, task_queue, mock_redis):
        """Test enqueue with scheduled time."""
        scheduled = datetime.utcnow() + timedelta(hours=1)

        task_queue.enqueue(
            task_type=TaskType.MODEL_INFERENCE,
            payload={"model": "crop_health"},
            scheduled_at=scheduled,
        )

        assert mock_redis.zadd.called


class TestTaskQueueProcessNext:
    """Tests for TaskQueue.process_next method."""

    def test_process_next_returns_none_on_empty_queue(self, task_queue, mock_redis):
        """Test that None is returned when queue is empty."""
        mock_redis.zrangebyscore.return_value = []

        task = task_queue.process_next(worker_id="worker1")

        assert task is None

    def test_process_next_updates_task_status(self, task_queue, mock_redis):
        """Test that task status is updated to processing."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"ndvi_calculation"',
            b"payload": b'{"field_id": "field123"}',
            b"priority": b"5",
            b"status": b'"pending"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.zrangebyscore.return_value = [b"task123"]
        mock_redis.hgetall.return_value = task_data

        task = task_queue.process_next(worker_id="worker1")

        if task:
            assert task.status == TaskStatus.PROCESSING
            assert task.worker_id == "worker1"

    def test_process_next_removes_from_queue(self, task_queue, mock_redis):
        """Test that task is removed from queue when processing starts."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"disease_detection"',
            b"payload": b'{}',
            b"priority": b"5",
            b"status": b'"pending"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.zrangebyscore.return_value = [b"task123"]
        mock_redis.hgetall.return_value = task_data

        task_queue.process_next(worker_id="worker1")

        assert mock_redis.zrem.called


class TestTaskQueueCompleteTask:
    """Tests for TaskQueue.complete_task method."""

    def test_complete_task_updates_status(self, task_queue, mock_redis):
        """Test that task status is updated to completed."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"ndvi_calculation"',
            b"payload": b'{}',
            b"priority": b"5",
            b"status": b'"processing"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"started_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        result = task_queue.complete_task(
            task_id="task123",
            result={"ndvi_value": 0.75},
        )

        assert result is True
        assert mock_redis.hset.called

    def test_complete_task_returns_false_for_missing_task(self, task_queue, mock_redis):
        """Test that False is returned for missing task."""
        mock_redis.hgetall.return_value = {}

        result = task_queue.complete_task(task_id="nonexistent")

        assert result is False


class TestTaskQueueFailTask:
    """Tests for TaskQueue.fail_task method."""

    def test_fail_task_with_retry(self, task_queue, mock_redis):
        """Test that failed task is re-queued with retry."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"disease_detection"',
            b"payload": b'{}',
            b"priority": b"5",
            b"status": b'"processing"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        result = task_queue.fail_task(
            task_id="task123",
            error_message="Processing failed",
            retry=True,
        )

        assert result is True
        # Should be re-queued
        assert mock_redis.zadd.called

    def test_fail_task_moves_to_dlq_after_max_retries(self, task_queue, mock_redis):
        """Test that task moves to DLQ after max retries."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"disease_detection"',
            b"payload": b'{}',
            b"priority": b"5",
            b"status": b'"processing"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"3",  # Already at max
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        result = task_queue.fail_task(
            task_id="task123",
            error_message="Max retries exceeded",
            retry=True,
        )

        assert result is True
        # Should be added to DLQ
        assert mock_redis.lpush.called


class TestTaskQueueCancelTask:
    """Tests for TaskQueue.cancel_task method."""

    def test_cancel_pending_task(self, task_queue, mock_redis):
        """Test cancellation of pending task."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"report_generation"',
            b"payload": b'{}',
            b"priority": b"3",
            b"status": b'"pending"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        result = task_queue.cancel_task(task_id="task123")

        assert result is True
        # Should be removed from queue
        assert mock_redis.zrem.called

    def test_cannot_cancel_processing_task(self, task_queue, mock_redis):
        """Test that processing task cannot be cancelled."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"ndvi_calculation"',
            b"payload": b'{}',
            b"priority": b"5",
            b"status": b'"processing"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        result = task_queue.cancel_task(task_id="task123")

        assert result is False


class TestTaskQueueGetTask:
    """Tests for TaskQueue.get_task method."""

    def test_get_existing_task(self, task_queue, mock_redis):
        """Test getting an existing task."""
        now = datetime.utcnow()
        task_data = {
            b"task_id": b'"task123"',
            b"task_type": b'"data_export"',
            b"payload": b'{"format": "csv"}',
            b"priority": b"3",
            b"status": b'"completed"',
            b"created_at": json.dumps(now.isoformat()).encode(),
            b"updated_at": json.dumps(now.isoformat()).encode(),
            b"retry_count": b"0",
            b"max_retries": b"3",
            b"timeout_seconds": b"300",
        }

        mock_redis.hgetall.return_value = task_data

        task = task_queue.get_task(task_id="task123")

        assert task is not None
        assert task.task_id == "task123"
        assert task.task_type == TaskType.DATA_EXPORT

    def test_get_nonexistent_task(self, task_queue, mock_redis):
        """Test getting a non-existent task."""
        mock_redis.hgetall.return_value = {}

        task = task_queue.get_task(task_id="nonexistent")

        assert task is None


class TestTaskQueueStatus:
    """Tests for TaskQueue.get_queue_status method."""

    def test_get_queue_status(self, task_queue, mock_redis):
        """Test getting queue status."""
        mock_redis.zcard.return_value = 5
        mock_redis.hgetall.return_value = {
            b"total_processing": b"2",
            b"total_completed": b"100",
            b"total_failed": b"5",
        }
        mock_redis.llen.return_value = 3

        status = task_queue.get_queue_status()

        assert "queues" in status
        assert "dlq_size" in status
        assert status["dlq_size"] == 3


class TestTaskQueueClearAll:
    """Tests for TaskQueue.clear_all method."""

    def test_clear_all(self, task_queue, mock_redis):
        """Test clearing all tasks."""
        result = task_queue.clear_all()

        assert result is True
        # Should delete multiple keys
        assert mock_redis.delete.call_count >= 2
