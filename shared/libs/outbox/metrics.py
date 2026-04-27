"""
SAHOOL Outbox Metrics
=====================
مقاييس الصندوق الصادر

Prometheus metrics for the transactional outbox relay.  All metrics are
optional — if ``prometheus_client`` is not installed (e.g. test environments
that don't run a full service stack) they degrade to no-ops and the relay
continues working without emitting metrics.

Metrics exposed:

``outbox_messages_published_total``          counter    {subject}
    Rows successfully published to NATS and marked ``published_at``.

``outbox_publish_failures_total``            counter    {subject, reason}
    Rows that failed to publish (NATS error) and were retried.
    ``reason`` = exception class name — controlled high-cardinality dimension.

``outbox_dead_lettered_total``               counter    {subject}
    Rows that exhausted ``_MAX_RETRIES`` and were dead-lettered.
    Golden signal for silent failure. Alert: rate(…[5m]) > 0

``outbox_pending_rows``                      gauge      {}
    Snapshot of pending (unpublished, not dead-lettered) rows.
    Key backpressure indicator. Alert: value > 10000

``outbox_publish_latency_seconds``           histogram  {subject}
    End-to-end NATS publish duration per row.
    Exposes NATS slowness, lock contention, and network jitter.

Recommended alert rules (PromQL):

    # Critical — any DLQ activity in the last 5 minutes
    rate(outbox_dead_lettered_total[5m]) > 0

    # Warning — publish error rate > 5% over 5 minutes
    rate(outbox_publish_failures_total[5m]) > 0.05

    # Warning — relay backlog too large
    outbox_pending_rows > 10000

Usage (from relay or service lifespan):

    from shared.libs.outbox.metrics import OUTBOX_METRICS
    OUTBOX_METRICS.published(subject="sahool.satellite.ndvi.computed")
    OUTBOX_METRICS.failed(subject="sahool.satellite.ndvi.computed", reason="ConnectionRefused")
    OUTBOX_METRICS.dead_lettered(subject="sahool.satellite.ndvi.computed")
    OUTBOX_METRICS.set_pending(42)
    OUTBOX_METRICS.observe_publish_latency(subject="sahool.satellite.ndvi.computed", duration_seconds=0.012)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Latency histogram buckets (seconds): 1 ms → 5 s.
# These cover the full range of healthy NATS publish latency (≤ 50 ms in
# a co-located cluster) through degraded/overloaded conditions (≤ 5 s).
# Observations beyond 5 s are still recorded in Prometheus's implicit +Inf
# bucket so no data is lost even during severe outages.
_LATENCY_BUCKETS = (0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

try:
    from prometheus_client import Counter, Gauge, Histogram

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

    _latency_histogram = Histogram(
        "outbox_publish_latency_seconds",
        "End-to-end NATS publish duration per outbox row",
        ["subject"],
        buckets=_LATENCY_BUCKETS,
    )

except ImportError:  # pragma: no cover
    _PROMETHEUS_AVAILABLE = False
    _published_counter = None
    _failures_counter = None
    _dlq_counter = None
    _pending_gauge = None
    _latency_histogram = None


class _OutboxMetrics:
    """
    Thin façade over Prometheus counters/gauge/histogram.

    All methods are no-ops when prometheus_client is unavailable.
    Attribute access is safe in all environments.
    Exceptions inside metric calls are swallowed — metrics must never
    crash or slow down the relay.
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
        """Increment failure counter — row will be retried next tick.

        *reason* should be the exception class name so alert grouping works
        without creating unbounded label cardinality.
        """
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

    def observe_publish_latency(self, subject: str, duration_seconds: float) -> None:
        """Record the end-to-end NATS publish latency for one row.

        Call this immediately after a successful ``_nats_publish`` call,
        passing ``time.monotonic() - t0`` as *duration_seconds*.

        This histogram reveals:
        - NATS broker slowness (high p99 across all subjects)
        - Per-subject hot spots (slow streams or large payloads)
        - Lock-contention spikes (latency spikes correlated with DB load)
        """
        if _latency_histogram is not None:
            try:
                _latency_histogram.labels(subject=subject).observe(duration_seconds)
            except Exception:  # pragma: no cover
                pass


# Module-level singleton — import this everywhere.
OUTBOX_METRICS = _OutboxMetrics()
