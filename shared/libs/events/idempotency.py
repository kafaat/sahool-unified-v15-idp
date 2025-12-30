"""
SAHOOL Event Idempotency Handler
==================================

Provides idempotency guarantees for event processing using Redis.
Prevents duplicate event processing by tracking processed events
and storing their results for replay.

Author: Sahool Platform Team
License: MIT
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from shared.cache.redis_sentinel import RedisSentinelClient, get_redis_client

logger = logging.getLogger(__name__)


class ProcessingStatus(str, Enum):
    """Status of event processing"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IdempotencyRecord(BaseModel):
    """
    Record of a processed event stored in Redis.

    Stores the processing status and result to enable
    idempotent event processing and result replay.
    """
    idempotency_key: str
    event_id: str
    event_type: str
    status: ProcessingStatus
    result: dict[str, Any] | None = None
    error: str | None = None
    first_seen_at: datetime
    completed_at: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class IdempotencyChecker:
    """
    Redis-based idempotency checker for event processing.

    Features:
        - Detects duplicate events using idempotency keys
        - Stores processing results for replay
        - Configurable TTL (default: 24 hours)
        - Automatic cleanup of old records

    Example:
        >>> checker = IdempotencyChecker()
        >>> # Check if event was already processed
        >>> record = await checker.get_processing_record("my-key")
        >>> if record and record.status == ProcessingStatus.COMPLETED:
        >>>     return record.result  # Return cached result
        >>>
        >>> # Mark as processing
        >>> await checker.mark_processing("my-key", event_id, event_type)
        >>>
        >>> # Process event...
        >>> result = process_event()
        >>>
        >>> # Mark as completed
        >>> await checker.mark_completed("my-key", result)
    """

    def __init__(
        self,
        redis_client: RedisSentinelClient | None = None,
        ttl_seconds: int = 86400,  # 24 hours
        key_prefix: str = "idempotency:events:"
    ):
        """
        Initialize idempotency checker.

        Args:
            redis_client: Redis client instance (uses singleton if not provided)
            ttl_seconds: Time-to-live for idempotency records in seconds (default: 24h)
            key_prefix: Redis key prefix for idempotency records
        """
        self.redis = redis_client or get_redis_client()
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix

    def _get_redis_key(self, idempotency_key: str) -> str:
        """Generate Redis key for idempotency record"""
        return f"{self.key_prefix}{idempotency_key}"

    def get_processing_record(self, idempotency_key: str) -> IdempotencyRecord | None:
        """
        Get existing processing record for an idempotency key.

        Args:
            idempotency_key: The idempotency key to check

        Returns:
            IdempotencyRecord if exists, None otherwise
        """
        try:
            redis_key = self._get_redis_key(idempotency_key)
            data = self.redis.get(redis_key, use_slave=True)

            if not data:
                return None

            record_dict = json.loads(data)
            return IdempotencyRecord(**record_dict)

        except Exception as e:
            logger.error(f"Failed to get idempotency record for {idempotency_key}: {e}")
            # On error, assume not processed to avoid blocking event processing
            return None

    def mark_processing(
        self,
        idempotency_key: str,
        event_id: str | UUID,
        event_type: str
    ) -> bool:
        """
        Mark an event as currently being processed.

        This creates a lock to prevent concurrent processing of the same event.
        Uses Redis SET with NX (only set if not exists) for atomic operation.

        Args:
            idempotency_key: The idempotency key
            event_id: Event ID
            event_type: Event type

        Returns:
            True if successfully marked as processing (first time seeing this event),
            False if already being processed
        """
        try:
            record = IdempotencyRecord(
                idempotency_key=idempotency_key,
                event_id=str(event_id),
                event_type=event_type,
                status=ProcessingStatus.PROCESSING,
                first_seen_at=datetime.now(timezone.utc),
            )

            redis_key = self._get_redis_key(idempotency_key)
            record_json = record.model_dump_json()

            # Use NX flag to only set if key doesn't exist (atomic check-and-set)
            success = self.redis.set(
                redis_key,
                record_json,
                ex=self.ttl_seconds,
                nx=True  # Only set if not exists
            )

            if success:
                logger.info(
                    f"Marked event as processing: {event_type} "
                    f"(key={idempotency_key}, event_id={event_id})"
                )
            else:
                logger.warning(
                    f"Event already being processed: {event_type} "
                    f"(key={idempotency_key}, event_id={event_id})"
                )

            return bool(success)

        except Exception as e:
            logger.error(f"Failed to mark event as processing: {e}")
            # On error, allow processing to continue to avoid blocking
            return True

    def mark_completed(
        self,
        idempotency_key: str,
        result: dict[str, Any] | None = None
    ) -> bool:
        """
        Mark an event as successfully processed and store the result.

        Args:
            idempotency_key: The idempotency key
            result: Processing result to store for replay

        Returns:
            True if successfully updated
        """
        try:
            # Get existing record
            existing_record = self.get_processing_record(idempotency_key)
            if not existing_record:
                logger.warning(f"No processing record found for {idempotency_key}")
                return False

            # Update record
            existing_record.status = ProcessingStatus.COMPLETED
            existing_record.result = result
            existing_record.completed_at = datetime.now(timezone.utc)

            redis_key = self._get_redis_key(idempotency_key)
            record_json = existing_record.model_dump_json()

            # Update record with new TTL
            self.redis.set(redis_key, record_json, ex=self.ttl_seconds)

            logger.info(f"Marked event as completed: {idempotency_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to mark event as completed: {e}")
            return False

    def mark_failed(
        self,
        idempotency_key: str,
        error: str
    ) -> bool:
        """
        Mark an event processing as failed.

        Args:
            idempotency_key: The idempotency key
            error: Error message or description

        Returns:
            True if successfully updated
        """
        try:
            # Get existing record
            existing_record = self.get_processing_record(idempotency_key)
            if not existing_record:
                logger.warning(f"No processing record found for {idempotency_key}")
                return False

            # Update record
            existing_record.status = ProcessingStatus.FAILED
            existing_record.error = error
            existing_record.completed_at = datetime.now(timezone.utc)

            redis_key = self._get_redis_key(idempotency_key)
            record_json = existing_record.model_dump_json()

            # Update record with new TTL
            self.redis.set(redis_key, record_json, ex=self.ttl_seconds)

            logger.info(f"Marked event as failed: {idempotency_key}, error: {error}")
            return True

        except Exception as e:
            logger.error(f"Failed to mark event as failed: {e}")
            return False

    def delete_record(self, idempotency_key: str) -> bool:
        """
        Delete an idempotency record.

        Useful for manual cleanup or retry of failed events.

        Args:
            idempotency_key: The idempotency key to delete

        Returns:
            True if record was deleted
        """
        try:
            redis_key = self._get_redis_key(idempotency_key)
            deleted_count = self.redis.delete(redis_key)

            if deleted_count > 0:
                logger.info(f"Deleted idempotency record: {idempotency_key}")
                return True
            else:
                logger.warning(f"No idempotency record found to delete: {idempotency_key}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete idempotency record: {e}")
            return False

    def is_duplicate(self, idempotency_key: str) -> tuple[bool, IdempotencyRecord | None]:
        """
        Check if an event is a duplicate (already processed or being processed).

        Args:
            idempotency_key: The idempotency key to check

        Returns:
            Tuple of (is_duplicate, record)
            - is_duplicate: True if event was already processed or is being processed
            - record: The existing record if found, None otherwise
        """
        record = self.get_processing_record(idempotency_key)

        if not record:
            return False, None

        # Event is duplicate if it's already completed or currently processing
        is_duplicate = record.status in [ProcessingStatus.COMPLETED, ProcessingStatus.PROCESSING]

        return is_duplicate, record

    def get_or_create_idempotency_key(
        self,
        event_id: UUID | str,
        idempotency_key: str | None = None
    ) -> str:
        """
        Get idempotency key from event, or generate from event_id if not provided.

        Args:
            event_id: Event ID
            idempotency_key: Optional explicit idempotency key

        Returns:
            Idempotency key to use
        """
        if idempotency_key:
            return idempotency_key

        # Use event_id as idempotency key if not provided
        return str(event_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Instance
# ═══════════════════════════════════════════════════════════════════════════════

_idempotency_checker: IdempotencyChecker | None = None


def get_idempotency_checker(
    ttl_seconds: int = 86400
) -> IdempotencyChecker:
    """
    Get idempotency checker singleton instance.

    Args:
        ttl_seconds: TTL for idempotency records (default: 24 hours)

    Returns:
        IdempotencyChecker instance
    """
    global _idempotency_checker

    if _idempotency_checker is None:
        _idempotency_checker = IdempotencyChecker(ttl_seconds=ttl_seconds)

    return _idempotency_checker
