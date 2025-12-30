"""
Tests for Event Idempotency Handling
=====================================

Tests for idempotency checker, decorators, and context managers.
"""

import time
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

import pytest

from .envelope import EventEnvelope
from .idempotency import (
    IdempotencyChecker,
    IdempotencyRecord,
    ProcessingStatus,
)
from .idempotent_handler import (
    DuplicateEventError,
    idempotent_event_handler,
    IdempotentEventProcessor,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


@pytest.fixture
def idempotency_checker(mock_redis):
    """Create IdempotencyChecker with mocked Redis"""
    return IdempotencyChecker(redis_client=mock_redis, ttl_seconds=3600)


@pytest.fixture
def sample_envelope():
    """Create a sample event envelope"""
    return EventEnvelope(
        event_id=uuid4(),
        event_type="field.created",
        event_version=1,
        tenant_id=uuid4(),
        correlation_id=uuid4(),
        schema_ref="events.field.created:v1",
        producer="field-service",
        payload={"field_id": str(uuid4()), "name": "Test Field"},
        idempotency_key="test-idempotency-key-123"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# IdempotencyChecker Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdempotencyChecker:
    """Test IdempotencyChecker functionality"""

    def test_get_processing_record_not_found(self, idempotency_checker, mock_redis):
        """Test getting a record that doesn't exist"""
        mock_redis.get.return_value = None

        record = idempotency_checker.get_processing_record("nonexistent-key")

        assert record is None
        mock_redis.get.assert_called_once()

    def test_get_processing_record_exists(self, idempotency_checker, mock_redis):
        """Test getting an existing record"""
        test_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.COMPLETED,
            result={"status": "success"},
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )

        mock_redis.get.return_value = test_record.model_dump_json()

        record = idempotency_checker.get_processing_record("test-key")

        assert record is not None
        assert record.idempotency_key == "test-key"
        assert record.status == ProcessingStatus.COMPLETED
        assert record.result == {"status": "success"}

    def test_mark_processing_success(self, idempotency_checker, mock_redis):
        """Test marking an event as processing (first time)"""
        mock_redis.set.return_value = True

        success = idempotency_checker.mark_processing(
            "test-key",
            uuid4(),
            "test.event"
        )

        assert success is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args.kwargs['nx'] is True  # Should use NX flag
        assert call_args.kwargs['ex'] == 3600  # TTL

    def test_mark_processing_duplicate(self, idempotency_checker, mock_redis):
        """Test marking an event that's already being processed"""
        mock_redis.set.return_value = False  # NX flag fails

        success = idempotency_checker.mark_processing(
            "test-key",
            uuid4(),
            "test.event"
        )

        assert success is False

    def test_mark_completed(self, idempotency_checker, mock_redis):
        """Test marking an event as completed"""
        # Setup existing record
        existing_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.PROCESSING,
            first_seen_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = existing_record.model_dump_json()

        result = {"status": "success", "field_id": "123"}
        success = idempotency_checker.mark_completed("test-key", result)

        assert success is True
        # Should update the record
        assert mock_redis.set.call_count == 1

    def test_mark_failed(self, idempotency_checker, mock_redis):
        """Test marking an event as failed"""
        # Setup existing record
        existing_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.PROCESSING,
            first_seen_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = existing_record.model_dump_json()

        success = idempotency_checker.mark_failed("test-key", "Processing error")

        assert success is True
        mock_redis.set.assert_called_once()

    def test_is_duplicate_new_event(self, idempotency_checker, mock_redis):
        """Test checking if a new event is duplicate (should be False)"""
        mock_redis.get.return_value = None

        is_dup, record = idempotency_checker.is_duplicate("new-key")

        assert is_dup is False
        assert record is None

    def test_is_duplicate_completed_event(self, idempotency_checker, mock_redis):
        """Test checking a completed event (should be duplicate)"""
        completed_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.COMPLETED,
            result={"status": "success"},
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = completed_record.model_dump_json()

        is_dup, record = idempotency_checker.is_duplicate("test-key")

        assert is_dup is True
        assert record is not None
        assert record.status == ProcessingStatus.COMPLETED

    def test_is_duplicate_processing_event(self, idempotency_checker, mock_redis):
        """Test checking an event currently being processed"""
        processing_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.PROCESSING,
            first_seen_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = processing_record.model_dump_json()

        is_dup, record = idempotency_checker.is_duplicate("test-key")

        assert is_dup is True
        assert record is not None
        assert record.status == ProcessingStatus.PROCESSING

    def test_is_duplicate_failed_event(self, idempotency_checker, mock_redis):
        """Test checking a failed event (should NOT be duplicate - allow retry)"""
        failed_record = IdempotencyRecord(
            idempotency_key="test-key",
            event_id=str(uuid4()),
            event_type="test.event",
            status=ProcessingStatus.FAILED,
            error="Previous error",
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = failed_record.model_dump_json()

        is_dup, record = idempotency_checker.is_duplicate("test-key")

        # Failed events should not be considered duplicates (allow retry)
        assert is_dup is False
        assert record is not None
        assert record.status == ProcessingStatus.FAILED

    def test_delete_record(self, idempotency_checker, mock_redis):
        """Test deleting an idempotency record"""
        mock_redis.delete.return_value = 1

        success = idempotency_checker.delete_record("test-key")

        assert success is True
        mock_redis.delete.assert_called_once()

    def test_get_or_create_idempotency_key_with_key(self, idempotency_checker):
        """Test getting idempotency key when provided"""
        key = idempotency_checker.get_or_create_idempotency_key(
            uuid4(),
            "custom-key"
        )

        assert key == "custom-key"

    def test_get_or_create_idempotency_key_without_key(self, idempotency_checker):
        """Test generating idempotency key from event_id"""
        event_id = uuid4()
        key = idempotency_checker.get_or_create_idempotency_key(event_id, None)

        assert key == str(event_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Decorator Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdempotentEventHandler:
    """Test idempotent_event_handler decorator"""

    def test_decorator_first_processing(self, sample_envelope, mock_redis):
        """Test decorator on first event processing"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        @idempotent_event_handler(checker=IdempotencyChecker(mock_redis))
        def handle_event(envelope: EventEnvelope) -> dict:
            return {"status": "processed", "field_id": "123"}

        result = handle_event(sample_envelope)

        assert result == {"status": "processed", "field_id": "123"}
        # Should mark as processing and completed
        assert mock_redis.set.call_count == 2

    def test_decorator_duplicate_skip(self, sample_envelope, mock_redis):
        """Test decorator skips duplicate events"""
        # Setup completed record
        completed_record = IdempotencyRecord(
            idempotency_key=sample_envelope.idempotency_key,
            event_id=str(sample_envelope.event_id),
            event_type=sample_envelope.event_type,
            status=ProcessingStatus.COMPLETED,
            result={"status": "cached", "field_id": "123"},
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = completed_record.model_dump_json()

        call_count = 0

        @idempotent_event_handler(
            skip_on_duplicate=True,
            return_cached_result=True,
            checker=IdempotencyChecker(mock_redis)
        )
        def handle_event(envelope: EventEnvelope) -> dict:
            nonlocal call_count
            call_count += 1
            return {"status": "processed", "field_id": "456"}

        result = handle_event(sample_envelope)

        # Should return cached result
        assert result == {"status": "cached", "field_id": "123"}
        # Handler should not be called
        assert call_count == 0

    def test_decorator_duplicate_raise_error(self, sample_envelope, mock_redis):
        """Test decorator raises error on duplicate"""
        # Setup completed record
        completed_record = IdempotencyRecord(
            idempotency_key=sample_envelope.idempotency_key,
            event_id=str(sample_envelope.event_id),
            event_type=sample_envelope.event_type,
            status=ProcessingStatus.COMPLETED,
            result={"status": "cached"},
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = completed_record.model_dump_json()

        @idempotent_event_handler(
            skip_on_duplicate=False,
            checker=IdempotencyChecker(mock_redis)
        )
        def handle_event(envelope: EventEnvelope) -> dict:
            return {"status": "processed"}

        with pytest.raises(DuplicateEventError) as exc_info:
            handle_event(sample_envelope)

        assert exc_info.value.cached_result == {"status": "cached"}

    def test_decorator_processing_error(self, sample_envelope, mock_redis):
        """Test decorator handles processing errors"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        @idempotent_event_handler(checker=IdempotencyChecker(mock_redis))
        def handle_event(envelope: EventEnvelope) -> dict:
            raise ValueError("Processing failed")

        with pytest.raises(ValueError, match="Processing failed"):
            handle_event(sample_envelope)

        # Should mark as failed
        assert mock_redis.set.call_count >= 2

    def test_decorator_without_envelope(self, mock_redis):
        """Test decorator with non-envelope argument"""
        @idempotent_event_handler(checker=IdempotencyChecker(mock_redis))
        def handle_event(data: dict) -> dict:
            return {"status": "processed"}

        # Should skip idempotency check and process normally
        result = handle_event({"test": "data"})
        assert result == {"status": "processed"}


# ═══════════════════════════════════════════════════════════════════════════════
# Context Manager Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdempotentEventProcessor:
    """Test IdempotentEventProcessor context manager"""

    def test_context_manager_first_processing(self, sample_envelope, mock_redis):
        """Test context manager on first processing"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        processor = IdempotentEventProcessor(checker=IdempotencyChecker(mock_redis))

        with processor.process(sample_envelope) as ctx:
            assert not ctx.is_duplicate
            assert ctx.cached_result is None

            # Process event
            result = {"status": "processed"}
            ctx.mark_completed(result)

        # Should mark as processing and completed
        assert mock_redis.set.call_count == 2

    def test_context_manager_duplicate(self, sample_envelope, mock_redis):
        """Test context manager with duplicate event"""
        # Setup completed record
        completed_record = IdempotencyRecord(
            idempotency_key=sample_envelope.idempotency_key,
            event_id=str(sample_envelope.event_id),
            event_type=sample_envelope.event_type,
            status=ProcessingStatus.COMPLETED,
            result={"status": "cached"},
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = completed_record.model_dump_json()

        processor = IdempotentEventProcessor(checker=IdempotencyChecker(mock_redis))

        with processor.process(sample_envelope) as ctx:
            assert ctx.is_duplicate
            assert ctx.cached_result == {"status": "cached"}

    def test_context_manager_error_handling(self, sample_envelope, mock_redis):
        """Test context manager handles errors properly"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        processor = IdempotentEventProcessor(checker=IdempotencyChecker(mock_redis))

        try:
            with processor.process(sample_envelope) as ctx:
                assert not ctx.is_duplicate
                raise ValueError("Processing error")
        except ValueError:
            pass

        # Should mark as failed
        assert mock_redis.set.call_count >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdempotencyIntegration:
    """Integration tests for idempotency system"""

    def test_end_to_end_event_processing(self, sample_envelope, mock_redis):
        """Test complete event processing flow"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True

        processed_events = []

        @idempotent_event_handler(
            skip_on_duplicate=True,
            return_cached_result=True,
            checker=IdempotencyChecker(mock_redis)
        )
        def handle_event(envelope: EventEnvelope) -> dict:
            processed_events.append(envelope.event_id)
            return {
                "status": "processed",
                "event_id": str(envelope.event_id),
                "field_id": envelope.payload.get("field_id")
            }

        # First call - should process
        result1 = handle_event(sample_envelope)
        assert len(processed_events) == 1
        assert result1["status"] == "processed"

        # Setup mock to return completed record for second call
        completed_record = IdempotencyRecord(
            idempotency_key=sample_envelope.idempotency_key,
            event_id=str(sample_envelope.event_id),
            event_type=sample_envelope.event_type,
            status=ProcessingStatus.COMPLETED,
            result=result1,
            first_seen_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        mock_redis.get.return_value = completed_record.model_dump_json()

        # Second call - should skip and return cached result
        result2 = handle_event(sample_envelope)
        assert len(processed_events) == 1  # No new processing
        assert result2 == result1  # Same result

    def test_concurrent_processing_prevention(self, sample_envelope, mock_redis):
        """Test that concurrent processing is prevented"""
        mock_redis.get.return_value = None

        # First call succeeds
        mock_redis.set.return_value = True
        checker = IdempotencyChecker(mock_redis)
        success1 = checker.mark_processing(
            sample_envelope.idempotency_key,
            sample_envelope.event_id,
            sample_envelope.event_type
        )
        assert success1 is True

        # Second call fails (NX flag prevents overwrite)
        mock_redis.set.return_value = False
        success2 = checker.mark_processing(
            sample_envelope.idempotency_key,
            sample_envelope.event_id,
            sample_envelope.event_type
        )
        assert success2 is False

    def test_event_without_idempotency_key_uses_event_id(self, mock_redis):
        """Test that event_id is used when idempotency_key is not provided"""
        envelope = EventEnvelope(
            event_id=uuid4(),
            event_type="test.event",
            event_version=1,
            tenant_id=uuid4(),
            correlation_id=uuid4(),
            schema_ref="events.test:v1",
            producer="test-service",
            payload={},
            idempotency_key=None  # No idempotency key
        )

        checker = IdempotencyChecker(mock_redis)
        key = checker.get_or_create_idempotency_key(
            envelope.event_id,
            envelope.idempotency_key
        )

        # Should use event_id as key
        assert key == str(envelope.event_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
