"""
Unit tests for the pushgateway metrics emitter.

These tests use a local CollectorRegistry (the default in
``PushgatewayMetrics.__init__``) and assert metric values via
``registry.get_sample_value(...)``. No HTTP server is started; push
failures are exercised by pointing ``push()`` at a deliberately bad URL
and asserting the warning log instead of a raised exception.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import pytest
from src.metrics import JOB_NAME, PushgatewayMetrics
from src.retention import RetentionRunResult, SweepSummary

# ─────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 4, 17, 3, 0, 0, tzinfo=UTC)


def _make_result(
    *,
    tenant_id: str = "tenant-1",
    category: str = "authentication",
    rows_deleted: int = 0,
    dry_run: bool = False,
    retention_days: int = 90,
    cutoff: datetime | None = None,
) -> RetentionRunResult:
    return RetentionRunResult(
        tenant_id=tenant_id,
        category=category,
        retention_days=retention_days,
        cutoff=cutoff or datetime(2026, 1, 17, tzinfo=UTC),
        rows_deleted=rows_deleted,
        last_deleted_seq_num=None,
        last_deleted_entry_hash=None,
        deleted_entry_hashes=[],
        dry_run=dry_run,
    )


# ─────────────────────────────────────────────────────────────────────────
# record_run — counter increments
# ─────────────────────────────────────────────────────────────────────────


class TestRecordRun:
    def test_success_run_increments_rows_and_runs_counters(self) -> None:
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="authentication", rows_deleted=42))

        rows = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "authentication"},
        )
        runs = metrics.registry.get_sample_value(
            "audit_retention_runs_total",
            labels={"tenant_id": "t1", "category": "authentication", "status": "success"},
        )
        assert rows == 42.0
        assert runs == 1.0

    def test_noop_run_increments_runs_noop_and_not_rows(self) -> None:
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="system", rows_deleted=0))

        # No rows_deleted sample exists at all for a noop — prometheus_client
        # lazily creates label combinations on first .inc(), which we skip.
        rows = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "system"},
        )
        noop = metrics.registry.get_sample_value(
            "audit_retention_runs_total",
            labels={"tenant_id": "t1", "category": "system", "status": "noop"},
        )
        assert rows is None
        assert noop == 1.0

    def test_dry_run_increments_dry_run_status_and_not_rows(self) -> None:
        metrics = PushgatewayMetrics()
        metrics.record_run(
            _make_result(
                tenant_id="t1",
                category="billing",
                rows_deleted=17,  # "would delete" count, not actual
                dry_run=True,
            )
        )

        rows = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "billing"},
        )
        dry = metrics.registry.get_sample_value(
            "audit_retention_runs_total",
            labels={"tenant_id": "t1", "category": "billing", "status": "dry_run"},
        )
        assert rows is None, "dry-run must not contribute to real deletion counter"
        assert dry == 1.0

    def test_counters_increment_by_category(self) -> None:
        """Multiple categories for the same tenant keep separate counters."""
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="authentication", rows_deleted=5))
        metrics.record_run(_make_result(tenant_id="t1", category="billing", rows_deleted=12))
        metrics.record_run(_make_result(tenant_id="t1", category="authentication", rows_deleted=3))

        auth_rows = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "authentication"},
        )
        billing_rows = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "billing"},
        )
        auth_runs = metrics.registry.get_sample_value(
            "audit_retention_runs_total",
            labels={"tenant_id": "t1", "category": "authentication", "status": "success"},
        )
        assert auth_rows == 8.0  # 5 + 3
        assert billing_rows == 12.0
        assert auth_runs == 2.0

    def test_counters_increment_by_tenant(self) -> None:
        """Same category across multiple tenants keeps separate counters."""
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="field_ops", rows_deleted=100))
        metrics.record_run(_make_result(tenant_id="t2", category="field_ops", rows_deleted=50))

        t1 = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t1", "category": "field_ops"},
        )
        t2 = metrics.registry.get_sample_value(
            "audit_retention_rows_deleted_total",
            labels={"tenant_id": "t2", "category": "field_ops"},
        )
        assert t1 == 100.0
        assert t2 == 50.0

    def test_record_failure_emits_failed_status(self) -> None:
        metrics = PushgatewayMetrics()
        metrics.record_failure("t1", "authentication")

        failed = metrics.registry.get_sample_value(
            "audit_retention_runs_total",
            labels={"tenant_id": "t1", "category": "authentication", "status": "failed"},
        )
        assert failed == 1.0


# ─────────────────────────────────────────────────────────────────────────
# finalize — gauges
# ─────────────────────────────────────────────────────────────────────────


class TestFinalize:
    def test_finalize_sets_all_four_gauges(self, now: datetime) -> None:
        metrics = PushgatewayMetrics()
        started = now
        finished = now + timedelta(seconds=12.5)
        summary = SweepSummary(
            runs=[
                _make_result(tenant_id="t1", category="authentication", rows_deleted=10),
                _make_result(tenant_id="t2", category="billing", rows_deleted=5),
                _make_result(tenant_id="t3", category="system", rows_deleted=0),
            ],
            started_at=started,
            finished_at=finished,
        )

        metrics.finalize(summary)

        timestamp = metrics.registry.get_sample_value("audit_retention_last_run_timestamp_seconds")
        duration = metrics.registry.get_sample_value("audit_retention_last_run_duration_seconds")
        tenants = metrics.registry.get_sample_value("audit_retention_last_run_tenants_touched")
        rows = metrics.registry.get_sample_value("audit_retention_last_run_rows_deleted_total")

        assert timestamp == finished.timestamp()
        assert duration == pytest.approx(12.5)
        # t3 had zero deletions; tenants_touched excludes it.
        assert tenants == 2.0
        assert rows == 15.0

    def test_finalize_with_empty_summary_sets_zeroes(self, now: datetime) -> None:
        metrics = PushgatewayMetrics()
        summary = SweepSummary(runs=[], started_at=now, finished_at=now)
        metrics.finalize(summary)

        assert metrics.registry.get_sample_value("audit_retention_last_run_tenants_touched") == 0.0
        assert metrics.registry.get_sample_value("audit_retention_last_run_rows_deleted_total") == 0.0


# ─────────────────────────────────────────────────────────────────────────
# push — no-op + error swallowing
# ─────────────────────────────────────────────────────────────────────────


class TestPush:
    def test_push_with_none_url_is_noop(self) -> None:
        """No URL → push() must return silently, not raise."""
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="authentication", rows_deleted=1))
        # Must not raise.
        metrics.push(None)

    def test_push_with_empty_url_is_noop(self) -> None:
        """Empty string is treated the same as None — common when the env
        var is present but unset in docker-compose/.env files."""
        metrics = PushgatewayMetrics()
        metrics.push("")

    def test_push_swallows_exception_on_bad_url(self, caplog: pytest.LogCaptureFixture) -> None:
        """A broken pushgateway URL must never raise; the run already
        succeeded by the time push() is called."""
        metrics = PushgatewayMetrics()
        metrics.record_run(_make_result(tenant_id="t1", category="authentication", rows_deleted=1))

        # 127.0.0.1 on a port nothing is listening on → connection refused.
        # The exact exception depends on the OS but it's always an OSError
        # subclass routed through urllib; push_to_gateway re-raises it.
        bad_url = "http://127.0.0.1:1"

        with caplog.at_level(logging.WARNING, logger="src.metrics"):
            # Must NOT raise.
            metrics.push(bad_url, instance="test-pod")

        # The failure is logged as a WARNING.
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        assert any(r.message == "metrics.push_failed" for r in warning_records), (
            f"expected metrics.push_failed WARNING, got {[r.message for r in warning_records]}"
        )

    def test_job_name_constant_is_stable(self) -> None:
        """The shared metric contract keys push batches by this job name.
        If it changes, sibling tooling (Grafana, alerts, audit-service
        gauge) won't find our metrics."""
        assert JOB_NAME == "audit-retention-worker"
