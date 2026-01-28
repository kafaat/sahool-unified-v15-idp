"""
SAHOOL Event Subscriber - DLQ Handler Methods
==============================================
معالج قائمة انتظار الرسائل الفاشلة - Dead Letter Queue Handler

This module contains DLQ-specific handler methods for EventSubscriber.
Separated for clarity and maintainability.

These methods are mixed into EventSubscriber class.
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from typing import Any

from .dlq_config import DLQMessageMetadata, is_retriable_error, should_retry

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# DLQ Handler Methods (to be added to EventSubscriber)
# ─────────────────────────────────────────────────────────────────────────────


async def _handle_failed_message_with_dlq(
    self,
    msg,
    subscription,
    error: Exception,
    retry_count: int,
    retry_timestamps: list[str],
    retry_errors: list[str],
):
    """
    Handle failed message processing with DLQ logic.

    Args:
        msg: NATS message
        subscription: Subscription configuration
        error: Exception that occurred
        retry_count: Current retry count
        retry_timestamps: List of retry attempt timestamps
        retry_errors: List of error messages from retries
    """
    # Check if error is retriable
    if not is_retriable_error(error):
        logger.warning(
            f"⚠️  Non-retriable error for {msg.subject}: {error.__class__.__name__}. "
            f"Moving to DLQ immediately."
        )
        await self._move_to_dlq(
            msg=msg,
            subscription=subscription,
            error=error,
            retry_count=retry_count,
            retry_timestamps=retry_timestamps,
            retry_errors=retry_errors,
        )
        return

    # Check if we should retry
    next_attempt = retry_count + 1

    if should_retry(next_attempt, self._dlq_config):
        # Retry the message
        await self._retry_message_with_dlq(
            msg=msg,
            subscription=subscription,
            attempt=next_attempt,
            retry_timestamps=retry_timestamps,
            retry_errors=retry_errors,
        )
    else:
        # Move to DLQ
        logger.warning(
            f"⚠️  Max retries ({self._dlq_config.max_retry_attempts}) exceeded for {msg.subject}. "
            f"Moving to DLQ."
        )
        await self._move_to_dlq(
            msg=msg,
            subscription=subscription,
            error=error,
            retry_count=retry_count,
            retry_timestamps=retry_timestamps,
            retry_errors=retry_errors,
        )


async def _retry_message_with_dlq(
    self,
    msg,
    subscription,
    attempt: int,
    retry_timestamps: list[str],
    retry_errors: list[str],
):
    """
    Retry processing a failed message with metadata tracking.

    Args:
        msg: NATS message
        subscription: Subscription configuration
        attempt: Current attempt number (1-based)
        retry_timestamps: List of retry timestamps
        retry_errors: List of retry errors
    """
    delay = self._dlq_config.get_retry_delay(attempt)
    logger.info(
        f"🔄 Retrying message on {msg.subject} "
        f"(attempt {attempt}/{self._dlq_config.max_retry_attempts}) "
        f"after {delay:.1f}s"
    )

    self._retry_count += 1

    await asyncio.sleep(delay)

    try:
        data = msg.data.decode("utf-8")
        event = await self._deserialize_message(data, subscription.event_class)

        if asyncio.iscoroutinefunction(subscription.handler):
            await subscription.handler(event)
        else:
            subscription.handler(event)

        await self._acknowledge_message(msg)
        logger.info(f"✅ Retry successful on attempt {attempt} for {msg.subject}")

    except Exception as e:
        logger.error(f"❌ Retry attempt {attempt} failed for {msg.subject}: {e}")

        # Update retry tracking
        retry_timestamps.append(datetime.utcnow().isoformat())
        retry_errors.append(str(e)[:200])

        # Recursively handle the failure
        await self._handle_failed_message_with_dlq(
            msg=msg,
            subscription=subscription,
            error=e,
            retry_count=attempt,
            retry_timestamps=retry_timestamps,
            retry_errors=retry_errors,
        )


async def _move_to_dlq(
    self,
    msg,
    subscription,
    error: Exception,
    retry_count: int,
    retry_timestamps: list[str],
    retry_errors: list[str],
):
    """
    Move failed message to Dead Letter Queue.
    نقل الرسالة الفاشلة إلى قائمة انتظار الرسائل الفاشلة

    Args:
        msg: NATS message
        subscription: Subscription configuration
        error: Final exception
        retry_count: Number of retries attempted
        retry_timestamps: Timestamps of retry attempts
        retry_errors: Error messages from retries
    """
    try:
        # Extract event ID if available
        original_event_id = None
        try:
            data = json.loads(msg.data.decode("utf-8"))
            original_event_id = data.get("event_id")
        except:
            pass

        # Create DLQ metadata
        metadata = DLQMessageMetadata(
            original_subject=msg.subject,
            original_event_id=original_event_id,
            correlation_id=getattr(msg, "reply", None),
            retry_count=retry_count,
            failure_reason=str(error),
            failure_timestamp=datetime.utcnow().isoformat(),
            error_type=error.__class__.__name__,
            error_traceback=traceback.format_exc()[:1000],  # Truncate traceback
            consumer_service=self.service_name,
            consumer_version=self.service_version,
            handler_function=getattr(subscription.handler, "__name__", "unknown"),
            retry_timestamps=retry_timestamps,
            retry_errors=retry_errors,
        )

        # Construct DLQ message
        dlq_message = {
            "metadata": metadata.model_dump(),
            "original_message": msg.data.decode("utf-8"),
        }

        # Get DLQ subject
        dlq_subject = self._dlq_config.get_dlq_subject(msg.subject)

        # Publish to DLQ using JetStream
        if self._js:
            await self._js.publish(
                dlq_subject,
                json.dumps(dlq_message, default=str).encode("utf-8"),
            )

            self._dlq_count += 1

            logger.warning(
                f"📮 Moved message to DLQ: {dlq_subject} "
                f"(retries: {retry_count}, error: {error.__class__.__name__})"
            )

            # ACK the original message (it's now in DLQ)
            await self._acknowledge_message(msg)

        else:
            logger.error("❌ Cannot move to DLQ: JetStream not enabled")
            await self._nack_message(msg)

    except Exception as dlq_error:
        logger.error(f"❌ Failed to move message to DLQ: {dlq_error}")
        # NAK the message as last resort
        await self._nack_message(msg)


async def _get_dlq_stats(self) -> dict[str, Any]:
    """
    Get DLQ statistics from JetStream.

    Returns:
        Dictionary with DLQ statistics
    """
    if not self._js or not self._dlq_initialized:
        return {
            "dlq_enabled": False,
            "message_count": 0,
            "stream_name": None,
        }

    try:
        stream_info = await self._js.stream_info(self._dlq_config.dlq_stream_name)

        return {
            "dlq_enabled": True,
            "stream_name": self._dlq_config.dlq_stream_name,
            "message_count": stream_info.state.messages,
            "bytes": stream_info.state.bytes,
            "first_seq": stream_info.state.first_seq,
            "last_seq": stream_info.state.last_seq,
            "consumer_count": stream_info.state.consumer_count,
            "subjects": stream_info.config.subjects,
        }

    except Exception as e:
        logger.error(f"Failed to get DLQ stats: {e}")
        return {
            "dlq_enabled": True,
            "error": str(e),
        }


# Add these methods to EventSubscriber class
def add_dlq_methods_to_subscriber(subscriber_class):
    """
    Add DLQ methods to EventSubscriber class.

    This is called when the module is imported.
    """
    subscriber_class._handle_failed_message_with_dlq = _handle_failed_message_with_dlq
    subscriber_class._retry_message_with_dlq = _retry_message_with_dlq
    subscriber_class._move_to_dlq = _move_to_dlq
    subscriber_class.get_dlq_stats = _get_dlq_stats
