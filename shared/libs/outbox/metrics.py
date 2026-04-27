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
    When JetStream is used this is the full round-trip time to receive a
    server-side PubAck (durable delivery confirmed).  When falling back to
    core NATS it is the socket-write time only (fire-and-forget at the
    broker level).  The ``delivery_mode`` field in the published log record
    indicates which semantic applies for each observation.

``outbox_replay_total``                      counter    {subject, reason}
    Rows reset by a replay operation (dead_lettered_at cleared, retry_count zeroed).
    ``reason`` = ``"all"`` | ``"by_subject"`` | ``"by_ids"``
    ``subject`` = actual NATS subject | ``"*"`` (all) | ``"(ids)"`` (by-ID list)
    Critical for SLOs: frequent replay indicates persistent delivery failures.
    Pair with ``outbox_dead_lettered_total`` to see: DLQ rate → replay rate.

``outbox_replay_blocked_total``              counter    {subject, reason}
    Replay attempts that were rejected by the rate-limiter guard.
    ``reason`` = ``"rate_limit"`` (only value currently).
    ``subject`` = NATS subject or ``"*"`` / ``"(ids)"`` (same conventions
    as ``outbox_replay_total``).
    A rising ``outbox_replay_blocked_total`` paired with a rising
    ``outbox_dead_lettered_total`` indicates a replay loop — the system is
    failing faster than replays are converging.

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

    _replay_counter = Counter(
        "outbox_replay_total",
        "Outbox rows reset by a replay operation",
        ["subject", "reason"],
    )

    _replay_blocked_counter = Counter(
        "outbox_replay_blocked_total",
        "Replay attempts rejected by the rate-limiter guard",
        ["subject", "reason"],
    )

except ImportError:  # pragma: no cover
    _PROMETHEUS_AVAILABLE = False
    _published_counter = None
    _failures_counter = None
    _dlq_counter = None
    _pending_gauge = None
    _latency_histogram = None
    _replay_counter = None
    _replay_blocked_counter = None


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

        Semantic note: when JetStream was used the observed duration covers
        the full round-trip to receive a server-side PubAck (durable delivery
        confirmed).  When the relay fell back to core NATS it covers only the
        socket-write time (fire-and-forget at the broker level).  The
        ``delivery_mode`` field in the published log record indicates which
        applies for each row.
        """
        if _latency_histogram is not None:
            try:
                _latency_histogram.labels(subject=subject).observe(duration_seconds)
            except Exception:  # pragma: no cover
                pass

    def record_replay(self, subject: str, reason: str, count: int = 1) -> None:
        """Increment the replay counter by *count* rows.

        Args:
            subject: NATS subject being replayed, or ``"*"`` for all-rows
                replay, or ``"(ids)"`` for a by-ID-list replay.
            reason: one of ``"all"``, ``"by_subject"``, ``"by_ids"``.
            count: number of rows reset (default 1, usually the UPDATE count).

        Pair this metric with ``outbox_dead_lettered_total`` in dashboards:
        a rising replay rate relative to the DLQ rate indicates that replays
        are not converging (stuck in a failure cycle).
        """
        if _replay_counter is not None:
            try:
                _replay_counter.labels(subject=subject, reason=reason).inc(count)
            except Exception:  # pragma: no cover
                pass

    def replay_blocked(self, subject: str, reason: str = "rate_limit") -> None:
        """Increment the replay-blocked counter.

        Called when ``OutboxReplayGuard`` rejects a replay attempt because
        the per-subject rate limit has been exceeded.  Pair this with
        ``outbox_replay_total`` and ``outbox_dead_lettered_total`` to detect
        replay loops: if ``outbox_replay_blocked_total`` rises alongside
        ``outbox_dead_lettered_total``, the system is failing faster than
        replays are converging.

        Args:
            subject: same conventions as ``record_replay`` (actual subject,
                ``"*"``, or ``"(ids)"``).
            reason: rejection cause; currently always ``"rate_limit"``.
        """
        if _replay_blocked_counter is not None:
            try:
                _replay_blocked_counter.labels(subject=subject, reason=reason).inc()
            except Exception:  # pragma: no cover
                pass


# Module-level singleton — import this everywhere.
OUTBOX_METRICS = _OutboxMetrics()
