"""
SAHOOL Dead Letter Queue Configuration
========================================
إعدادات قائمة انتظار الرسائل الفاشلة - DLQ

Dead Letter Queue (DLQ) infrastructure for handling failed messages
in NATS JetStream. Provides reliable message processing with automatic
retry and failure handling.

Features:
- Automatic retry with exponential backoff
- Failed message persistence in DLQ streams
- Message metadata tracking (retry count, failure reason)
- Replay and monitoring capabilities
- Alerting for DLQ accumulation

Architecture:
    Message → Handler → Retry (3x) → DLQ Stream
                ↓
            Success (ACK)

DLQ Subjects Pattern:
    sahool.dlq.{domain}.{entity}.{action}

    Examples:
    - sahool.dlq.field.created
    - sahool.dlq.weather.alert
    - sahool.dlq.billing.payment.completed

Usage:
    from shared.events.dlq_config import DLQConfig, create_dlq_streams

    # Initialize DLQ streams
    await create_dlq_streams(js)

    # Use in subscriber
    config = DLQConfig()
    subscriber = EventSubscriber(dlq_config=config)
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────────────────────
# DLQ Configuration
# ─────────────────────────────────────────────────────────────────────────────


class DLQConfig(BaseModel):
    """
    Dead Letter Queue configuration.
    إعدادات قائمة انتظار الرسائل الفاشلة
    """

    # Retry configuration
    max_retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts before moving to DLQ",
    )
    initial_retry_delay: float = Field(
        default=1.0, ge=0.1, description="Initial retry delay in seconds"
    )
    max_retry_delay: float = Field(
        default=60.0,
        ge=1.0,
        description="Maximum retry delay in seconds (caps exponential backoff)",
    )
    backoff_multiplier: float = Field(
        default=2.0, ge=1.0, description="Exponential backoff multiplier"
    )

    # DLQ Stream configuration
    dlq_stream_name: str = Field(
        default="SAHOOL_DLQ", description="Name of the DLQ JetStream stream"
    )
    dlq_subject_prefix: str = Field(
        default="sahool.dlq", description="Subject prefix for DLQ messages"
    )

    # Retention
    dlq_max_age_days: int = Field(
        default=30, ge=1, description="Maximum age of messages in DLQ (days)"
    )
    dlq_max_messages: int = Field(
        default=100000, ge=1000, description="Maximum number of messages in DLQ stream"
    )
    dlq_max_bytes: int = Field(
        default=10 * 1024 * 1024 * 1024,  # 10 GB
        ge=1024 * 1024,
        description="Maximum bytes in DLQ stream",
    )

    # Monitoring and alerting
    alert_threshold: int = Field(
        default=100,
        ge=1,
        description="Alert when DLQ message count exceeds this threshold",
    )
    alert_enabled: bool = Field(
        default=True, description="Enable alerting for DLQ accumulation"
    )
    alert_check_interval_seconds: int = Field(
        default=300,  # 5 minutes
        ge=60,
        description="Interval to check DLQ size for alerts",
    )

    # Environment overrides
    @classmethod
    def from_env(cls) -> DLQConfig:
        """Create configuration from environment variables."""
        return cls(
            max_retry_attempts=int(os.getenv("DLQ_MAX_RETRIES", "3")),
            initial_retry_delay=float(os.getenv("DLQ_INITIAL_DELAY", "1.0")),
            max_retry_delay=float(os.getenv("DLQ_MAX_DELAY", "60.0")),
            backoff_multiplier=float(os.getenv("DLQ_BACKOFF_MULTIPLIER", "2.0")),
            dlq_stream_name=os.getenv("DLQ_STREAM_NAME", "SAHOOL_DLQ"),
            dlq_max_age_days=int(os.getenv("DLQ_MAX_AGE_DAYS", "30")),
            dlq_max_messages=int(os.getenv("DLQ_MAX_MESSAGES", "100000")),
            alert_threshold=int(os.getenv("DLQ_ALERT_THRESHOLD", "100")),
            alert_enabled=os.getenv("DLQ_ALERT_ENABLED", "true").lower() == "true",
        )

    def get_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay for the given attempt using exponential backoff.

        Args:
            attempt: Retry attempt number (1-based)

        Returns:
            Delay in seconds
        """
        delay = self.initial_retry_delay * (self.backoff_multiplier ** (attempt - 1))
        return min(delay, self.max_retry_delay)

    def get_dlq_subject(self, original_subject: str) -> str:
        """
        Get DLQ subject for a given original subject.

        Args:
            original_subject: Original NATS subject (e.g., "sahool.field.created")

        Returns:
            DLQ subject (e.g., "sahool.dlq.field.created")
        """
        # Remove "sahool." prefix if present
        if original_subject.startswith("sahool."):
            subject_suffix = original_subject[7:]  # Remove "sahool."
        else:
            subject_suffix = original_subject

        return f"{self.dlq_subject_prefix}.{subject_suffix}"


# ─────────────────────────────────────────────────────────────────────────────
# DLQ Message Metadata
# ─────────────────────────────────────────────────────────────────────────────


class DLQMessageMetadata(BaseModel):
    """
    Metadata stored with each DLQ message.
    البيانات الوصفية المخزنة مع كل رسالة في قائمة الانتظار الفاشلة
    """

    # Original message info
    original_subject: str = Field(..., description="Original NATS subject")
    original_event_id: str | None = Field(None, description="Original event ID")
    correlation_id: str | None = Field(
        None, description="Correlation ID for tracing"
    )

    # Failure info
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    failure_reason: str = Field(..., description="Reason for failure")
    failure_timestamp: str = Field(
        ..., description="ISO 8601 timestamp of final failure"
    )
    error_type: str | None = Field(None, description="Python exception class name")
    error_traceback: str | None = Field(None, description="Stack trace (truncated)")

    # Consumer info
    consumer_service: str | None = Field(
        None, description="Service that failed to process"
    )
    consumer_version: str | None = Field(None, description="Service version")
    handler_function: str | None = Field(None, description="Handler function name")

    # Retry history
    retry_timestamps: list[str] = Field(
        default_factory=list, description="ISO 8601 timestamps of each retry attempt"
    )
    retry_errors: list[str] = Field(
        default_factory=list, description="Error messages from each retry"
    )

    # Replay info
    replayed: bool = Field(default=False, description="Has this message been replayed")
    replay_count: int = Field(default=0, ge=0, description="Number of replay attempts")
    last_replay_timestamp: str | None = Field(
        None, description="Last replay timestamp"
    )


# ─────────────────────────────────────────────────────────────────────────────
# JetStream Stream Configuration
# ─────────────────────────────────────────────────────────────────────────────


class StreamConfig(BaseModel):
    """JetStream stream configuration."""

    name: str
    subjects: list[str]
    retention: str = "limits"  # limits, interest, workqueue
    max_age_seconds: int | None = None
    max_messages: int | None = None
    max_bytes: int | None = None
    max_msg_size: int | None = None
    storage: str = "file"  # file or memory
    replicas: int = 1
    discard: str = "old"  # old or new


def get_dlq_stream_config(config: DLQConfig) -> StreamConfig:
    """
    Get JetStream stream configuration for DLQ.

    Args:
        config: DLQ configuration

    Returns:
        Stream configuration for DLQ
    """
    return StreamConfig(
        name=config.dlq_stream_name,
        subjects=[f"{config.dlq_subject_prefix}.>"],  # All DLQ subjects
        retention="limits",
        max_age_seconds=config.dlq_max_age_days * 86400,  # days to seconds
        max_messages=config.dlq_max_messages,
        max_bytes=config.dlq_max_bytes,
        max_msg_size=1024 * 1024,  # 1 MB per message
        storage="file",  # Persistent storage
        replicas=1,
        discard="old",  # Discard oldest when limits reached
    )


async def create_dlq_streams(js, config: DLQConfig | None = None):
    """
    Create or update DLQ JetStream streams.
    إنشاء أو تحديث تدفقات JetStream لقائمة الانتظار الفاشلة

    Args:
        js: JetStream context
        config: DLQ configuration (uses defaults if None)
    """
    if config is None:
        config = DLQConfig()

    stream_config = get_dlq_stream_config(config)

    try:
        # Try to get existing stream
        stream_info = await js.stream_info(stream_config.name)
        print(f"✅ DLQ stream '{stream_config.name}' already exists")

        # Update if needed
        await js.update_stream(
            name=stream_config.name,
            subjects=stream_config.subjects,
            retention=stream_config.retention,
            max_age=stream_config.max_age_seconds,
            max_msgs=stream_config.max_messages,
            max_bytes=stream_config.max_bytes,
            max_msg_size=stream_config.max_msg_size,
            storage=stream_config.storage,
            num_replicas=stream_config.replicas,
            discard=stream_config.discard,
        )
        print("✅ Updated DLQ stream configuration")

    except Exception:
        # Stream doesn't exist, create it
        try:
            await js.add_stream(
                name=stream_config.name,
                subjects=stream_config.subjects,
                retention=stream_config.retention,
                max_age=stream_config.max_age_seconds,
                max_msgs=stream_config.max_messages,
                max_bytes=stream_config.max_bytes,
                max_msg_size=stream_config.max_msg_size,
                storage=stream_config.storage,
                num_replicas=stream_config.replicas,
                discard=stream_config.discard,
            )
            print(f"✅ Created DLQ stream '{stream_config.name}'")
            print(f"   Subjects: {stream_config.subjects}")
            print(f"   Max age: {config.dlq_max_age_days} days")
            print(f"   Max messages: {config.dlq_max_messages:,}")

        except Exception as create_error:
            print(f"❌ Failed to create DLQ stream: {create_error}")
            raise


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────


def should_retry(attempt: int, config: DLQConfig) -> bool:
    """
    Determine if message should be retried.

    Args:
        attempt: Current attempt number (1-based)
        config: DLQ configuration

    Returns:
        True if should retry, False if should move to DLQ
    """
    return attempt < config.max_retry_attempts


def is_retriable_error(error: Exception) -> bool:
    """
    Determine if an error is retriable.

    Non-retriable errors (permanent failures):
    - ValidationError (bad message format)
    - ValueError (invalid data)
    - KeyError (missing required fields)
    - TypeError (wrong data types)

    Retriable errors (transient failures):
    - ConnectionError (network issues)
    - TimeoutError (temporary unavailability)
    - Any other exceptions

    Args:
        error: Exception that occurred

    Returns:
        True if error is retriable, False for permanent failures
    """
    from pydantic import ValidationError

    # Permanent failures - don't retry
    non_retriable = (
        ValidationError,
        ValueError,
        KeyError,
        TypeError,
    )

    if isinstance(error, non_retriable):
        return False

    # Transient failures - retry
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────


__all__ = [
    "DLQConfig",
    "DLQMessageMetadata",
    "StreamConfig",
    "get_dlq_stream_config",
    "create_dlq_streams",
    "should_retry",
    "is_retriable_error",
]
