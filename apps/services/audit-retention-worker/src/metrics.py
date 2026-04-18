"""
SAHOOL Audit Retention — Prometheus pushgateway emitter.

Why push, not scrape:
  The retention worker is a one-shot Kubernetes CronJob. Prometheus'
  pull model requires a stable endpoint that lives long enough to be
  scraped at the configured interval; by the time Prometheus notices
  a CronJob pod, the process has already exited. Pushing a batch of
  metrics to a cluster-wide pushgateway at end-of-run gives Prometheus
  something durable to scrape.

Metric contract (shared with audit-service's gauge emitter and with
the Grafana dashboards/alerts — do NOT rename, do NOT relabel):

    audit_retention_rows_deleted_total{tenant_id, category}        Counter
    audit_retention_runs_total{tenant_id, category, status}        Counter
        status ∈ {success, noop, dry_run, failed}
    audit_retention_last_run_timestamp_seconds                     Gauge
    audit_retention_last_run_duration_seconds                      Gauge
    audit_retention_last_run_tenants_touched                       Gauge
    audit_retention_last_run_rows_deleted_total                    Gauge

The four ``last_run_*`` gauges are global (no labels). Prometheus
pushgateway deduplicates by ``job`` + ``grouping_key``, so pushing
twice with the same grouping overwrites — which is what we want for
gauges but NOT for counters. The counters therefore use ``push`` (not
``pushadd``) only once per worker invocation; every invocation is a
fresh grouping keyed by the pod name.

Module-local registry:
  We deliberately do NOT use prometheus_client's default ``REGISTRY``.
  A process-global registry accumulates state across tests and across
  back-to-back test runs that reuse the same interpreter — which would
  make assertions on counter values flaky. A fresh
  ``CollectorRegistry`` per ``PushgatewayMetrics`` instance keeps the
  emitter self-contained.

Push failures are SWALLOWED (warning log, no re-raise):
  A broken pushgateway must never turn a successful retention run into
  a failed CronJob. The deletions already happened + were logged + were
  recorded in audit_retention_events; losing a metrics push is a
  monitoring problem, not a data-integrity problem.
"""

from __future__ import annotations

import logging
import socket
from datetime import datetime
from typing import TYPE_CHECKING

from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway

if TYPE_CHECKING:  # avoid importing retention at module top-level
    from .retention import RetentionRunResult, SweepSummary

logger = logging.getLogger(__name__)

# Shared contract — also referenced in audit-service's gauge emitter and in
# the Grafana dashboard/alert definitions. Keep names and labels exact.
JOB_NAME = "audit-retention-worker"


class PushgatewayMetrics:
    """Accumulates retention-sweep metrics and pushes them as one batch.

    Usage::

        metrics = PushgatewayMetrics()
        for run in summary.runs:
            metrics.record_run(run)
        metrics.finalize(summary)
        metrics.push(os.getenv("AUDIT_RETENTION_PUSHGATEWAY_URL"))

    The instance owns its own CollectorRegistry so tests can inspect
    sample values via ``registry.get_sample_value(...)`` without reaching
    into a process-global.
    """

    def __init__(self, *, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry or CollectorRegistry()

        self.rows_deleted = Counter(
            "audit_retention_rows_deleted_total",
            "Total audit_log rows deleted by the retention worker, by tenant and category.",
            labelnames=("tenant_id", "category"),
            registry=self.registry,
        )
        self.runs = Counter(
            "audit_retention_runs_total",
            "Count of retention-run outcomes, by tenant, category and status.",
            labelnames=("tenant_id", "category", "status"),
            registry=self.registry,
        )
        self.last_run_timestamp = Gauge(
            "audit_retention_last_run_timestamp_seconds",
            "Unix timestamp (seconds) when the most recent sweep finished.",
            registry=self.registry,
        )
        self.last_run_duration = Gauge(
            "audit_retention_last_run_duration_seconds",
            "Wall-clock seconds the most recent sweep took.",
            registry=self.registry,
        )
        self.last_run_tenants_touched = Gauge(
            "audit_retention_last_run_tenants_touched",
            "Number of tenants with at least one deletion in the most recent sweep.",
            registry=self.registry,
        )
        self.last_run_rows_deleted = Gauge(
            "audit_retention_last_run_rows_deleted_total",
            "Total rows deleted across all tenants in the most recent sweep.",
            registry=self.registry,
        )

    def record_run(self, result: RetentionRunResult) -> None:
        """Fold a single (tenant, policy) run into the registry.

        Status derivation (dry_run wins because a dry-run that "would
        delete" something is operationally noteworthy but did NOT
        actually delete; lumping it under success would overstate real
        deletions):
          * dry_run  → dry_run
          * rows > 0 → success
          * else     → noop
        """
        if result.dry_run:
            status = "dry_run"
        elif result.rows_deleted > 0:
            status = "success"
        else:
            status = "noop"

        self.runs.labels(
            tenant_id=result.tenant_id,
            category=result.category,
            status=status,
        ).inc()

        # Only count real deletions toward rows_deleted_total. A dry-run
        # run's rows_deleted is the "would delete" count — recording it
        # here would double-count once the real run lands.
        if not result.dry_run and result.rows_deleted > 0:
            self.rows_deleted.labels(
                tenant_id=result.tenant_id,
                category=result.category,
            ).inc(result.rows_deleted)

    def record_failure(self, tenant_id: str, category: str) -> None:
        """Mark a (tenant, category) as failed.

        Called from main.py's exception branch — RetentionRunResult
        doesn't model failures (run_sweep raises instead), so the
        status="failed" counter is only ever incremented through this
        entry point.
        """
        self.runs.labels(
            tenant_id=tenant_id,
            category=category,
            status="failed",
        ).inc()

    def finalize(self, summary: SweepSummary) -> None:
        """Set the four last_run_* gauges from the aggregate summary."""
        duration = (summary.finished_at - summary.started_at).total_seconds()
        self.last_run_timestamp.set(summary.finished_at.timestamp())
        self.last_run_duration.set(duration)
        self.last_run_tenants_touched.set(summary.tenants_touched)
        self.last_run_rows_deleted.set(summary.total_deleted)

    def push(self, url: str | None, *, instance: str | None = None) -> None:
        """Push the batch to the pushgateway.

        No-op when ``url`` is None — that's the default in dev and in
        environments that don't run a pushgateway. Failures are logged
        at WARNING and swallowed: a retention run that successfully
        deleted rows must never be reported as failed because the
        metrics push broke.

        ``instance`` is the pushgateway grouping_key; defaults to the
        pod name (K8s injects HOSTNAME) or socket.gethostname() as a
        fallback. Two concurrent workers will push under different
        instances and neither will overwrite the other's counters.
        """
        if not url:
            logger.debug("metrics.push_skipped_no_url")
            return

        instance_value = instance or _pod_instance()
        grouping_key = {"instance": instance_value}

        try:
            push_to_gateway(
                url,
                job=JOB_NAME,
                registry=self.registry,
                grouping_key=grouping_key,
            )
            logger.info(
                "metrics.pushed",
                extra={
                    "url": url,
                    "job": JOB_NAME,
                    "instance": instance_value,
                },
            )
        except Exception as exc:  # noqa: BLE001 — push failure must not break the run
            logger.warning(
                "metrics.push_failed",
                extra={
                    "url": url,
                    "instance": instance_value,
                    "error": str(exc),
                    "hint": (
                        "pushgateway unreachable or rejecting; retention deletions "
                        "still succeeded — check pushgateway health, network policy, "
                        "or AUDIT_RETENTION_PUSHGATEWAY_URL value"
                    ),
                },
            )


def _pod_instance() -> str:
    """Best-effort identifier for the pushgateway grouping key.

    K8s sets HOSTNAME to the pod name inside every container; falling
    back to socket.gethostname() keeps local runs working too. Worst
    case the value is "unknown", which just means concurrent local
    runs would clobber each other's gauges — acceptable for dev.
    """
    import os

    hostname = os.getenv("HOSTNAME") or socket.gethostname() or "unknown"
    return hostname
