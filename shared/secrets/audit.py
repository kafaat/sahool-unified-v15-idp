"""
Secret Access Auditing and Monitoring
مراقبة وتدقيق الوصول للأسرار

Provides comprehensive audit logging for secret access patterns,
anomaly detection, and security monitoring.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════════════════════════


class SecretAccessType(str, Enum):
    """Type of secret access operation"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"


class AccessResult(str, Enum):
    """Result of secret access attempt"""

    SUCCESS = "success"
    DENIED = "denied"
    ERROR = "error"
    NOT_FOUND = "not_found"


@dataclass
class SecretAccessEvent:
    """
    Record of a secret access attempt.

    Attributes:
        timestamp: When the access occurred
        access_type: Type of operation (read/write/delete)
        secret_path: Path to the secret (sanitized)
        backend: Secrets backend used
        result: Success/failure status
        user: User or service account
        source_ip: IP address of requester
        service: Service making the request
        metadata: Additional context
    """

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_type: SecretAccessType = SecretAccessType.READ
    secret_path: str = ""
    backend: str = "environment"
    result: AccessResult = AccessResult.SUCCESS
    user: str = "unknown"
    source_ip: str = "unknown"
    service: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "access_type": self.access_type.value,
            "secret_path": self._sanitize_path(self.secret_path),
            "backend": self.backend,
            "result": self.result.value,
            "user": self.user,
            "source_ip": self.source_ip,
            "service": self.service,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())

    @staticmethod
    def _sanitize_path(path: str) -> str:
        """Sanitize secret path to prevent leaking sensitive info"""
        # Remove any potential secret values from path
        return path.split("?")[0].split("#")[0]


# ═══════════════════════════════════════════════════════════════════════════════
# Audit Logger
# ═══════════════════════════════════════════════════════════════════════════════


class SecretAuditLogger:
    """
    Audit logger for secret access.

    Provides:
    - Structured logging of all secret access
    - Anomaly detection
    - Alert generation for suspicious patterns
    - Metrics collection
    """

    def __init__(
        self,
        log_file: str | None = None,
        alert_threshold: int = 100,
        enable_anomaly_detection: bool = True,
    ):
        self.log_file = log_file
        self.alert_threshold = alert_threshold
        self.enable_anomaly_detection = enable_anomaly_detection

        # In-memory access tracking (for anomaly detection)
        self._access_history: list[SecretAccessEvent] = []
        self._access_counts: dict[str, int] = {}
        self._failed_attempts: dict[str, list[datetime]] = {}

        # Configure file logging if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            logger.addHandler(file_handler)

    async def log_access(self, event: SecretAccessEvent) -> None:
        """
        Log a secret access event.

        Args:
            event: Secret access event to log
        """
        # Log to standard logger
        log_data = event.to_json()

        if event.result == AccessResult.SUCCESS:
            logger.info(f"Secret access: {log_data}")
        elif event.result == AccessResult.DENIED:
            logger.warning(f"Secret access denied: {log_data}")
        elif event.result == AccessResult.ERROR:
            logger.error(f"Secret access error: {log_data}")
        else:
            logger.info(f"Secret access: {log_data}")

        # Track in memory for anomaly detection
        if self.enable_anomaly_detection:
            self._track_access(event)

            # Check for anomalies
            await self._check_anomalies(event)

    def _track_access(self, event: SecretAccessEvent) -> None:
        """Track access in memory for pattern analysis"""
        # Keep only recent history (last 24 hours)
        cutoff = datetime.now(UTC) - timedelta(hours=24)
        self._access_history = [e for e in self._access_history if e.timestamp > cutoff]

        # Add new event
        self._access_history.append(event)

        # Update counts
        key = f"{event.user}:{event.secret_path}"
        self._access_counts[key] = self._access_counts.get(key, 0) + 1

        # Track failed attempts
        if event.result in (AccessResult.DENIED, AccessResult.ERROR):
            if event.user not in self._failed_attempts:
                self._failed_attempts[event.user] = []
            self._failed_attempts[event.user].append(event.timestamp)

            # Clean old failed attempts
            recent_cutoff = datetime.now(UTC) - timedelta(minutes=15)
            self._failed_attempts[event.user] = [
                t for t in self._failed_attempts[event.user] if t > recent_cutoff
            ]

    async def _check_anomalies(self, event: SecretAccessEvent) -> None:
        """Check for anomalous access patterns"""

        # 1. High frequency access
        key = f"{event.user}:{event.secret_path}"
        if self._access_counts.get(key, 0) > self.alert_threshold:
            await self._alert_high_frequency(event)

        # 2. Multiple failed attempts
        failed_count = len(self._failed_attempts.get(event.user, []))
        if failed_count >= 5:
            await self._alert_failed_attempts(event, failed_count)

        # 3. Unusual access time (3-6 AM)
        hour = event.timestamp.hour
        if 3 <= hour <= 6:
            await self._alert_unusual_time(event)

        # 4. Access from new IP
        recent_ips = {e.source_ip for e in self._access_history[-100:] if e.user == event.user}
        if event.source_ip != "unknown" and event.source_ip not in recent_ips:
            await self._alert_new_ip(event)

    async def _alert_high_frequency(self, event: SecretAccessEvent) -> None:
        """Alert on high frequency access"""
        logger.warning(
            f"ALERT: High frequency secret access detected - "
            f"User: {event.user}, Path: {event.secret_path}, "
            f"Count: {self._access_counts.get(f'{event.user}:{event.secret_path}', 0)}"
        )

    async def _alert_failed_attempts(self, event: SecretAccessEvent, count: int) -> None:
        """Alert on multiple failed attempts"""
        logger.warning(
            f"ALERT: Multiple failed secret access attempts - User: {event.user}, Count: {count}"
        )

    async def _alert_unusual_time(self, event: SecretAccessEvent) -> None:
        """Alert on unusual access time"""
        logger.warning(
            f"ALERT: Unusual time secret access - "
            f"User: {event.user}, Time: {event.timestamp.strftime('%H:%M')}"
        )

    async def _alert_new_ip(self, event: SecretAccessEvent) -> None:
        """Alert on access from new IP"""
        logger.warning(
            f"ALERT: Secret access from new IP - User: {event.user}, IP: {event.source_ip}"
        )

    def get_access_stats(self, hours: int = 24) -> dict[str, Any]:
        """
        Get access statistics for the last N hours.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with access statistics
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        recent_events = [e for e in self._access_history if e.timestamp > cutoff]

        if not recent_events:
            return {
                "total_accesses": 0,
                "successful": 0,
                "failed": 0,
                "unique_users": 0,
                "unique_paths": 0,
                "by_backend": {},
                "by_user": {},
            }

        # Calculate stats
        total = len(recent_events)
        successful = sum(1 for e in recent_events if e.result == AccessResult.SUCCESS)
        failed = total - successful
        unique_users = len({e.user for e in recent_events})
        unique_paths = len({e.secret_path for e in recent_events})

        # By backend
        by_backend: dict[str, int] = {}
        for event in recent_events:
            by_backend[event.backend] = by_backend.get(event.backend, 0) + 1

        # By user
        by_user: dict[str, int] = {}
        for event in recent_events:
            by_user[event.user] = by_user.get(event.user, 0) + 1

        return {
            "total_accesses": total,
            "successful": successful,
            "failed": failed,
            "unique_users": unique_users,
            "unique_paths": unique_paths,
            "by_backend": by_backend,
            "by_user": by_user,
            "time_range_hours": hours,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Prometheus Metrics
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from prometheus_client import Counter, Histogram

    # Secret access counter
    secret_access_counter = Counter(
        "sahool_secret_access_total",
        "Total number of secret accesses",
        ["backend", "access_type", "result", "service"],
    )

    # Secret access duration
    secret_access_duration = Histogram(
        "sahool_secret_access_duration_seconds",
        "Time spent accessing secrets",
        ["backend", "access_type"],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    )

    # Failed access attempts
    secret_access_failures = Counter(
        "sahool_secret_access_failures_total",
        "Total number of failed secret access attempts",
        ["backend", "result", "user"],
    )

    METRICS_ENABLED = True

except ImportError:
    METRICS_ENABLED = False
    logger.warning("Prometheus client not installed, metrics disabled")


def record_metrics(event: SecretAccessEvent) -> None:
    """Record Prometheus metrics for secret access"""
    if not METRICS_ENABLED:
        return

    try:
        # Record access
        secret_access_counter.labels(
            backend=event.backend,
            access_type=event.access_type.value,
            result=event.result.value,
            service=event.service,
        ).inc()

        # Record duration
        secret_access_duration.labels(
            backend=event.backend,
            access_type=event.access_type.value,
        ).observe(event.duration_ms / 1000.0)

        # Record failures
        if event.result != AccessResult.SUCCESS:
            secret_access_failures.labels(
                backend=event.backend,
                result=event.result.value,
                user=event.user,
            ).inc()

    except Exception as e:
        logger.error(f"Failed to record metrics: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Global Audit Logger
# ═══════════════════════════════════════════════════════════════════════════════

_audit_logger: SecretAuditLogger | None = None


def get_audit_logger() -> SecretAuditLogger:
    """Get or create the global audit logger"""
    global _audit_logger

    if _audit_logger is None:
        _audit_logger = SecretAuditLogger(log_file="/var/log/sahool/secret-audit.log")

    return _audit_logger


async def audit_secret_access(event: SecretAccessEvent) -> None:
    """
    Convenience function to audit secret access.

    Args:
        event: Secret access event to audit
    """
    logger_instance = get_audit_logger()
    await logger_instance.log_access(event)
    record_metrics(event)
