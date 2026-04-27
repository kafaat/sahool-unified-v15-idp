"""
SAHOOL Outbox Metrics
=====================
مقاييس الصندوق الصادر

Prometheus metrics for the transactional outbox relay.  All metrics are
optional — if ``prometheus_client`` is not installed (e.g. test environments
that don't run a full service stack) they degrade to no-ops and the relay
continues working without emitting metrics.

Metrics exposed:

``outbox_messages_published_total``   counter  {subject}
    Rows successfully published to NATS and marked ``published_at``.

``outbox_publish_failures_total``     counter  {subject, reason}
    Rows that failed to publish (NATS error) and were retried.

``outbox_dead_lettered_total``        counter  {subject}
    Rows that exhausted ``_MAX_RETRIES`` and were dead-lettered.

``outbox_pending_rows``               gauge    {}
    Snapshot of pending (unpublished, not dead-lettered) rows.
    Useful for alerting on relay backlog.

Usage (from relay or service lifespan):

    from shared.libs.outbox.metrics import OUTBOX_METRICS
    OUTBOX_METRICS.published(subject="sahool.satellite.ndvi.computed")
    OUTBOX_METRICS.failed(subject="sahool.satellite.ndvi.computed", reason="ConnectionRefused")
    OUTBOX_METRICS.dead_lettered(subject="sahool.satellite.ndvi.computed")
    OUTBOX_METRICS.set_pending(42)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Gauge

    _PROMETHEUS_AVAILABLE = True

    _published_counter = Counter(
        "outbox_messages_published_total",
        "Outbox rows successfully published to NATS",
        ["subject"],
    )

    _failures_counter = Counter(
        "outbox_publish_failures_total",
        "Outbox rows that failed NATS publish and were retried",
        ["subject", "reason"],
    )

    _dlq_counter = Counter(
        "outbox_dead_lettered_total",
        "Outbox rows dead-lettered after exhausting max retries",
        ["subject"],
    )

    _pending_gauge = Gauge(
        "outbox_pending_rows",
        "Current number of pending (unpublished, not dead-lettered) outbox rows",
    )

except ImportError:  # pragma: no cover
    _PROMETHEUS_AVAILABLE = False
    _published_counter = None
    _failures_counter = None
    _dlq_counter = None
    _pending_gauge = None


class _OutboxMetrics:
    """
    Thin façade over Prometheus counters/gauge.

    All methods are no-ops when prometheus_client is unavailable.
    Attribute access is safe in all environments.
    """

    @property
    def available(self) -> bool:
        return _PROMETHEUS_AVAILABLE

    def published(self, subject: str) -> None:
        """Increment successful-publish counter for *subject*."""
        if _published_counter is not None:
            try:
                _published_counter.labels(subject=subject).inc()
            except Exception:  # pragma: no cover
                pass  # metrics must never break the relay

    def failed(self, subject: str, reason: str = "unknown") -> None:
        """Increment failure counter — row will be retried next tick."""
        if _failures_counter is not None:
            try:
                _failures_counter.labels(subject=subject, reason=reason).inc()
            except Exception:  # pragma: no cover
                pass

    def dead_lettered(self, subject: str) -> None:
        """Increment DLQ counter — row exhausted max retries."""
        if _dlq_counter is not None:
            try:
                _dlq_counter.labels(subject=subject).inc()
            except Exception:  # pragma: no cover
                pass

    def set_pending(self, count: int) -> None:
        """Set the pending-rows gauge to *count* (call after each drain batch)."""
        if _pending_gauge is not None:
            try:
                _pending_gauge.set(count)
            except Exception:  # pragma: no cover
                pass


# Module-level singleton — import this everywhere.
OUTBOX_METRICS = _OutboxMetrics()
