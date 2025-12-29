"""
SAHOOL Idempotent Event Handler Decorator
==========================================

Provides decorators and middleware for idempotent event processing.
Automatically handles duplicate detection and result replay.

Author: Sahool Platform Team
License: MIT
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar, ParamSpec

from .envelope import EventEnvelope
from .idempotency import (
    IdempotencyChecker,
    ProcessingStatus,
    get_idempotency_checker,
)

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


class DuplicateEventError(Exception):
    """
    Exception raised when a duplicate event is detected.

    Contains the cached result from the previous processing
    for replay purposes.
    """
    def __init__(self, message: str, cached_result: dict[str, Any] | None = None):
        super().__init__(message)
        self.cached_result = cached_result


def idempotent_event_handler(
    ttl_seconds: int = 86400,
    skip_on_duplicate: bool = False,
    return_cached_result: bool = True,
    checker: IdempotencyChecker | None = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator for idempotent event processing.

    Automatically checks for duplicate events before processing and stores
    results for replay. Works with any event handler that receives an
    EventEnvelope as its first argument.

    Args:
        ttl_seconds: TTL for idempotency records (default: 24 hours)
        skip_on_duplicate: If True, skip processing on duplicate (return None).
                          If False, raise DuplicateEventError with cached result.
        return_cached_result: If True and event is duplicate, return cached result.
                             Only applies when skip_on_duplicate=True.
        checker: Custom IdempotencyChecker instance (uses singleton if not provided)

    Example:
        >>> @idempotent_event_handler()
        >>> def handle_field_created(envelope: EventEnvelope) -> dict:
        >>>     # Process event...
        >>>     return {"status": "created", "field_id": "123"}
        >>>
        >>> # First call processes event
        >>> result1 = handle_field_created(envelope)
        >>>
        >>> # Second call returns cached result without processing
        >>> result2 = handle_field_created(envelope)  # Same result, no processing

    Raises:
        DuplicateEventError: If event is duplicate and skip_on_duplicate=False

    Returns:
        Decorated function with idempotency guarantees
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Get event envelope from first argument
            if not args or not isinstance(args[0], EventEnvelope):
                logger.warning(
                    f"Idempotent handler {func.__name__} called without EventEnvelope. "
                    "Skipping idempotency check."
                )
                return func(*args, **kwargs)

            envelope: EventEnvelope = args[0]

            # Get or create idempotency key
            idempotency_checker = checker or get_idempotency_checker(ttl_seconds)
            key = idempotency_checker.get_or_create_idempotency_key(
                envelope.event_id,
                envelope.idempotency_key
            )

            # Check for duplicate
            is_duplicate, record = idempotency_checker.is_duplicate(key)

            if is_duplicate and record:
                logger.info(
                    f"Duplicate event detected: {envelope.event_type} "
                    f"(key={key}, status={record.status})"
                )

                if record.status == ProcessingStatus.COMPLETED:
                    # Event was already successfully processed
                    if skip_on_duplicate:
                        if return_cached_result and record.result:
                            logger.info(f"Returning cached result for {key}")
                            return record.result  # type: ignore
                        else:
                            logger.info(f"Skipping duplicate event {key}")
                            return None  # type: ignore
                    else:
                        # Raise error with cached result
                        raise DuplicateEventError(
                            f"Duplicate event: {envelope.event_type} (key={key})",
                            cached_result=record.result
                        )

                elif record.status == ProcessingStatus.PROCESSING:
                    # Event is currently being processed (concurrent processing attempt)
                    logger.warning(
                        f"Concurrent processing detected for {envelope.event_type} (key={key})"
                    )
                    if skip_on_duplicate:
                        return None  # type: ignore
                    else:
                        raise DuplicateEventError(
                            f"Event is currently being processed: {envelope.event_type} (key={key})"
                        )

            # Mark as processing (atomic check-and-set)
            success = idempotency_checker.mark_processing(
                key,
                envelope.event_id,
                envelope.event_type
            )

            if not success:
                # Another process beat us to it
                logger.warning(
                    f"Lost race to process event {envelope.event_type} (key={key}). "
                    "Another instance is processing it."
                )
                if skip_on_duplicate:
                    return None  # type: ignore
                else:
                    raise DuplicateEventError(
                        f"Event is being processed by another instance: {envelope.event_type} (key={key})"
                    )

            try:
                # Process the event
                logger.info(
                    f"Processing event: {envelope.event_type} "
                    f"(key={key}, event_id={envelope.event_id})"
                )
                result = func(*args, **kwargs)

                # Mark as completed with result
                idempotency_checker.mark_completed(
                    key,
                    result=result if isinstance(result, dict) else None
                )

                return result

            except Exception as e:
                # Mark as failed
                idempotency_checker.mark_failed(key, str(e))
                logger.error(
                    f"Event processing failed: {envelope.event_type} "
                    f"(key={key}, error={e})"
                )
                raise

        return wrapper  # type: ignore

    return decorator


async def process_with_idempotency(
    envelope: EventEnvelope,
    handler: Callable[[EventEnvelope], T],
    ttl_seconds: int = 86400,
    checker: IdempotencyChecker | None = None
) -> tuple[bool, T | None]:
    """
    Process an event with idempotency guarantees (async version).

    This is a utility function for manual idempotency handling,
    useful when you can't use the decorator.

    Args:
        envelope: Event envelope to process
        handler: Event handler function
        ttl_seconds: TTL for idempotency records
        checker: Custom IdempotencyChecker instance

    Returns:
        Tuple of (was_processed, result)
        - was_processed: True if event was processed, False if duplicate
        - result: Processing result or cached result

    Example:
        >>> async def handle_event(envelope: EventEnvelope):
        >>>     # Process event...
        >>>     return {"status": "ok"}
        >>>
        >>> was_processed, result = await process_with_idempotency(
        >>>     envelope,
        >>>     handle_event
        >>> )
        >>> if not was_processed:
        >>>     print("Event was duplicate, using cached result")
    """
    idempotency_checker = checker or get_idempotency_checker(ttl_seconds)

    # Get or create idempotency key
    key = idempotency_checker.get_or_create_idempotency_key(
        envelope.event_id,
        envelope.idempotency_key
    )

    # Check for duplicate
    is_duplicate, record = idempotency_checker.is_duplicate(key)

    if is_duplicate and record:
        if record.status == ProcessingStatus.COMPLETED:
            logger.info(f"Returning cached result for duplicate event: {key}")
            return False, record.result  # type: ignore

        elif record.status == ProcessingStatus.PROCESSING:
            logger.warning(f"Event is being processed concurrently: {key}")
            return False, None

    # Mark as processing
    success = idempotency_checker.mark_processing(
        key,
        envelope.event_id,
        envelope.event_type
    )

    if not success:
        logger.warning(f"Lost race to process event: {key}")
        return False, None

    try:
        # Process event
        result = handler(envelope)

        # Mark as completed
        idempotency_checker.mark_completed(
            key,
            result=result if isinstance(result, dict) else None
        )

        return True, result

    except Exception as e:
        # Mark as failed
        idempotency_checker.mark_failed(key, str(e))
        raise


class IdempotentEventProcessor:
    """
    Context manager for idempotent event processing.

    Provides a clean API for manual idempotency handling with
    proper resource management.

    Example:
        >>> processor = IdempotentEventProcessor()
        >>>
        >>> with processor.process(envelope) as ctx:
        >>>     if ctx.is_duplicate:
        >>>         # Handle duplicate
        >>>         return ctx.cached_result
        >>>
        >>>     # Process event
        >>>     result = do_processing()
        >>>
        >>>     # Mark as completed
        >>>     ctx.mark_completed(result)
        >>>     return result
    """

    def __init__(
        self,
        ttl_seconds: int = 86400,
        checker: IdempotencyChecker | None = None
    ):
        """
        Initialize idempotent event processor.

        Args:
            ttl_seconds: TTL for idempotency records
            checker: Custom IdempotencyChecker instance
        """
        self.checker = checker or get_idempotency_checker(ttl_seconds)
        self.ttl_seconds = ttl_seconds

    def process(self, envelope: EventEnvelope) -> IdempotencyContext:
        """
        Start processing an event with idempotency.

        Args:
            envelope: Event envelope to process

        Returns:
            IdempotencyContext for managing the processing lifecycle
        """
        return IdempotencyContext(envelope, self.checker)


class IdempotencyContext:
    """
    Context manager for a single event processing operation.

    Handles idempotency checking, marking, and cleanup.
    """

    def __init__(self, envelope: EventEnvelope, checker: IdempotencyChecker):
        self.envelope = envelope
        self.checker = checker
        self.idempotency_key: str | None = None
        self.is_duplicate = False
        self.cached_result: Any = None
        self.processing_started = False

    def __enter__(self) -> IdempotencyContext:
        """Enter context and check for duplicates"""
        # Get idempotency key
        self.idempotency_key = self.checker.get_or_create_idempotency_key(
            self.envelope.event_id,
            self.envelope.idempotency_key
        )

        # Check for duplicate
        is_dup, record = self.checker.is_duplicate(self.idempotency_key)

        if is_dup and record:
            self.is_duplicate = True
            if record.status == ProcessingStatus.COMPLETED:
                self.cached_result = record.result
            return self

        # Mark as processing
        success = self.checker.mark_processing(
            self.idempotency_key,
            self.envelope.event_id,
            self.envelope.event_type
        )

        if success:
            self.processing_started = True
        else:
            # Lost race condition
            self.is_duplicate = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and handle cleanup"""
        if self.is_duplicate or not self.processing_started:
            return False

        if exc_type is not None:
            # Processing failed
            self.mark_failed(str(exc_val))
            return False

        # If we get here without explicit mark_completed,
        # still mark as completed (with no result)
        if self.idempotency_key:
            record = self.checker.get_processing_record(self.idempotency_key)
            if record and record.status == ProcessingStatus.PROCESSING:
                self.checker.mark_completed(self.idempotency_key)

        return False

    def mark_completed(self, result: dict[str, Any] | None = None):
        """Mark event processing as completed"""
        if self.idempotency_key:
            self.checker.mark_completed(self.idempotency_key, result)

    def mark_failed(self, error: str):
        """Mark event processing as failed"""
        if self.idempotency_key:
            self.checker.mark_failed(self.idempotency_key, error)
