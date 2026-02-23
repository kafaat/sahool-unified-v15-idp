# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for Production Runbook Accuracy
======================================
اختبارات دقة دليل العمليات الإنتاجية

Validates that the production runbook (docs/operations/runbook-production.md)
accurately references real codebase artifacts: file paths, stream names,
DLQ configuration, outbox schema, idempotency patterns, and event contracts.

These tests act as a **documentation guard** — if the codebase changes and
the runbook becomes stale, these tests will fail and flag the drift.
"""

from __future__ import annotations

import importlib
import os
import re
from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parents[2]  # sahool-unified-v15-idp/
RUNBOOK_PATH = ROOT_DIR / "docs" / "operations" / "runbook-production.md"


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def runbook_content() -> str:
    """Load the production runbook content."""
    assert RUNBOOK_PATH.exists(), f"Runbook not found at {RUNBOOK_PATH}"
    return RUNBOOK_PATH.read_text(encoding="utf-8")


# ═════════════════════════════════════════════════════════════════════════════
# 1. Runbook File Structure Tests — اختبارات هيكل ملف الدليل
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookStructure:
    """Validate the runbook file exists and has proper structure."""

    def test_runbook_file_exists(self):
        """Runbook must exist at docs/operations/runbook-production.md."""
        assert RUNBOOK_PATH.exists(), f"Missing: {RUNBOOK_PATH}"

    def test_runbook_not_empty(self, runbook_content: str):
        """Runbook must have substantial content."""
        assert len(runbook_content) > 5000, "Runbook is too short — likely incomplete"

    def test_runbook_has_title(self, runbook_content: str):
        """Runbook must start with a proper markdown heading."""
        assert runbook_content.startswith("# SAHOOL Operational Runbook")

    def test_runbook_has_version(self, runbook_content: str):
        """Runbook must declare a version."""
        assert "Version" in runbook_content

    def test_runbook_has_severity_levels(self, runbook_content: str):
        """Runbook must define severity levels P0-P3."""
        for level in ["P0", "P1", "P2", "P3"]:
            assert level in runbook_content, f"Missing severity level: {level}"

    def test_runbook_has_required_sections(self, runbook_content: str):
        """Runbook must contain all critical incident sections."""
        required_sections = [
            "DLQ Growth",
            "Consumer Lag",
            "Duplicate Recommendation",
            "Outbox Backlog",
            "DB High CPU",
            "Event Storm",
            "Correlation Debugging",
            "Pod Crash",
            "Emergency Rollback",
            "Health Check Routine",
            "Weekly Review",
            "Escalation Matrix",
            "Golden Rules",
            "Exit Criteria",
        ]
        for section in required_sections:
            assert section in runbook_content, f"Missing section: {section}"

    def test_runbook_has_golden_rules(self, runbook_content: str):
        """Runbook must have at least 5 golden rules."""
        # Count numbered golden rules in the table
        golden_rules_matches = re.findall(r"\| \d+ \|", runbook_content)
        assert len(golden_rules_matches) >= 5, (
            f"Expected at least 5 golden rules, found {len(golden_rules_matches)}"
        )

    def test_runbook_has_appendixes(self, runbook_content: str):
        """Runbook must include appendixes for reference."""
        assert "Appendix A" in runbook_content
        assert "Appendix B" in runbook_content
        assert "Appendix C" in runbook_content


# ═════════════════════════════════════════════════════════════════════════════
# 2. Referenced File Path Tests — اختبارات مسارات الملفات المرجعية
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookFileReferences:
    """Validate that all file paths referenced in the runbook exist."""

    # Key files that the runbook references in Appendix A
    REFERENCED_FILES = [
        "shared/events/dlq_config.py",
        "shared/events/outbox.py",
        "shared/events/publisher.py",
        "shared/events/subscriber.py",
        "shared/events/contracts.py",
        "shared/events/subjects.py",
        "shared/events/streams.py",
        "shared/middleware/request_logging.py",
        "shared/ai/circuit_breaker.py",
        "shared/middleware/rate_limit.py",
        "shared/monitoring/health_enhanced.py",
        "shared/monitoring/metrics.py",
        "config/nats/nats.conf",
        "docker/docker-compose.dlq.yml",
    ]

    @pytest.mark.parametrize("rel_path", REFERENCED_FILES)
    def test_referenced_file_exists(self, rel_path: str):
        """Each file referenced in the runbook must exist in the codebase."""
        full_path = ROOT_DIR / rel_path
        assert full_path.exists(), (
            f"Runbook references '{rel_path}' but file does not exist. "
            "Update the runbook or restore the missing file."
        )

    def test_dlq_service_file_exists(self):
        """DLQ service API file must exist."""
        path = ROOT_DIR / "shared" / "events" / "dlq_service.py"
        assert path.exists(), "shared/events/dlq_service.py is referenced but missing"

    def test_prometheus_rules_directory_exists(self):
        """Prometheus alert rules directory must exist."""
        path = ROOT_DIR / "infrastructure" / "monitoring" / "prometheus" / "rules"
        assert path.exists(), "Prometheus rules directory is missing"

    def test_grafana_dashboards_directory_exists(self):
        """Grafana dashboards directory must exist."""
        path = ROOT_DIR / "infrastructure" / "grafana" / "dashboards"
        assert path.exists() or (ROOT_DIR / "infrastructure" / "monitoring" / "grafana" / "dashboards").exists(), (
            "Grafana dashboards directory is missing"
        )

    def test_helm_charts_directory_exists(self):
        """Helm charts directory must exist."""
        path = ROOT_DIR / "helm" / "charts"
        assert path.exists(), "Helm charts directory is missing"


# ═════════════════════════════════════════════════════════════════════════════
# 3. Stream Definitions Tests — اختبارات تعريفات التدفقات
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookStreamAccuracy:
    """Validate that stream names in runbook match actual code."""

    def test_streams_module_importable(self):
        """shared.events.streams must be importable."""
        mod = importlib.import_module("shared.events.streams")
        assert hasattr(mod, "STREAMS"), "STREAMS list not found in streams module"

    def test_stream_names_match_runbook(self, runbook_content: str):
        """All stream names from code must appear in the runbook."""
        from shared.events.streams import STREAMS

        for stream_def in STREAMS:
            assert stream_def.name in runbook_content, (
                f"Stream '{stream_def.name}' exists in code but is missing from runbook"
            )

    def test_dlq_stream_referenced_in_runbook(self, runbook_content: str):
        """SAHOOL_DLQ stream must be referenced in the runbook."""
        assert "SAHOOL_DLQ" in runbook_content

    def test_stream_count_matches(self, runbook_content: str):
        """Runbook should document the correct number of streams."""
        from shared.events.streams import STREAMS

        # STREAMS list doesn't include DLQ (it's in dlq_config.py)
        # Runbook says "9 Pre-Defined" (8 from STREAMS + 1 DLQ)
        expected_total = len(STREAMS) + 1  # +1 for SAHOOL_DLQ
        assert f"{expected_total} Pre-Defined" in runbook_content or str(expected_total) in runbook_content, (
            f"Runbook should reference {expected_total} streams (got {len(STREAMS)} in code + DLQ)"
        )

    def test_stream_retention_accuracy(self):
        """Stream retention values in code must be reasonable."""
        from shared.events.streams import STREAMS

        for stream in STREAMS:
            days = stream.max_age_seconds / 86400
            assert 1 <= days <= 365, (
                f"Stream '{stream.name}' has unreasonable retention: {days} days"
            )

    def test_dedup_window_documented(self, runbook_content: str):
        """Dedup window value must be documented in runbook."""
        from shared.events.streams import STREAMS

        # Get dedup window from first stream definition
        dedup_window = STREAMS[0].duplicate_window_seconds
        assert str(dedup_window) in runbook_content, (
            f"Dedup window ({dedup_window}s) not found in runbook"
        )


# ═════════════════════════════════════════════════════════════════════════════
# 4. DLQ Configuration Tests — اختبارات إعدادات قائمة الانتظار الفاشلة
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookDLQAccuracy:
    """Validate that DLQ configuration in runbook matches actual code."""

    def test_dlq_config_importable(self):
        """shared.events.dlq_config must be importable."""
        mod = importlib.import_module("shared.events.dlq_config")
        assert hasattr(mod, "DLQConfig")
        assert hasattr(mod, "DLQMessageMetadata")
        assert hasattr(mod, "should_retry")
        assert hasattr(mod, "is_retriable_error")

    def test_default_max_retries_matches_runbook(self, runbook_content: str):
        """DLQ max retry attempts in runbook must match code defaults."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        assert str(config.max_retry_attempts) in runbook_content, (
            f"DLQ max_retry_attempts={config.max_retry_attempts} not found in runbook"
        )

    def test_default_backoff_matches_runbook(self, runbook_content: str):
        """DLQ backoff multiplier must match the runbook."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        # Runbook mentions "1s → 2s → 4s" backoff pattern
        delays = [config.get_retry_delay(i) for i in range(1, 4)]
        assert delays[0] == 1.0, f"First retry delay should be 1.0s, got {delays[0]}"
        assert delays[1] == 2.0, f"Second retry delay should be 2.0s, got {delays[1]}"
        assert delays[2] == 4.0, f"Third retry delay should be 4.0s, got {delays[2]}"

    def test_dlq_stream_name_matches_runbook(self, runbook_content: str):
        """DLQ stream name must match between code and runbook."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        assert config.dlq_stream_name in runbook_content

    def test_dlq_alert_threshold_matches_runbook(self, runbook_content: str):
        """DLQ alert threshold must be documented in runbook."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        assert str(config.alert_threshold) in runbook_content, (
            f"DLQ alert_threshold={config.alert_threshold} not documented in runbook"
        )

    def test_non_retriable_errors_documented(self, runbook_content: str):
        """Non-retriable error types must be listed in the runbook."""
        # These are the non-retriable types from is_retriable_error()
        for error_type in ["ValidationError", "ValueError", "KeyError", "TypeError"]:
            assert error_type in runbook_content, (
                f"Non-retriable error type '{error_type}' not documented in runbook"
            )

    def test_retriable_errors_documented(self, runbook_content: str):
        """Retriable error types must be listed in the runbook."""
        for error_type in ["TimeoutError", "ConnectionError"]:
            assert error_type in runbook_content, (
                f"Retriable error type '{error_type}' not documented in runbook"
            )

    def test_dlq_subject_pattern_documented(self, runbook_content: str):
        """DLQ subject pattern must be documented."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        assert config.dlq_subject_prefix in runbook_content

    def test_dlq_message_metadata_fields_documented(self, runbook_content: str):
        """Key DLQ metadata fields must be documented in runbook."""
        key_fields = [
            "original_subject",
            "correlation_id",
            "retry_count",
            "failure_reason",
            "error_type",
            "consumer_service",
            "retry_timestamps",
            "retry_errors",
        ]
        for field_name in key_fields:
            assert field_name in runbook_content, (
                f"DLQ metadata field '{field_name}' not documented in runbook"
            )


# ═════════════════════════════════════════════════════════════════════════════
# 5. Outbox Pattern Tests — اختبارات نمط صندوق الصادر
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookOutboxAccuracy:
    """Validate that outbox pattern references in runbook match code."""

    def test_outbox_module_importable(self):
        """shared.events.outbox must be importable."""
        mod = importlib.import_module("shared.events.outbox")
        assert hasattr(mod, "write_outbox_event")
        assert hasattr(mod, "OutboxRelay")
        assert hasattr(mod, "ensure_outbox_table")

    def test_outbox_table_name_in_runbook(self, runbook_content: str):
        """Outbox table name must match between code and runbook."""
        from shared.events.outbox import SQL_CREATE_OUTBOX_TABLE

        assert "outbox_events" in SQL_CREATE_OUTBOX_TABLE
        assert "outbox_events" in runbook_content

    def test_outbox_status_values_documented(self, runbook_content: str):
        """Outbox status values must be documented in runbook."""
        assert "pending" in runbook_content
        assert "sent" in runbook_content
        assert "failed" in runbook_content

    def test_outbox_relay_defaults_documented(self, runbook_content: str):
        """OutboxRelay default values must be documented."""
        from shared.events.outbox import OutboxRelay

        # Check default poll_interval and batch_size
        relay = OutboxRelay(db_pool=None, publisher=None)
        assert str(relay._poll_interval) in runbook_content or "1.0" in runbook_content, (
            "OutboxRelay poll_interval not documented"
        )
        assert str(relay._batch_size) in runbook_content, (
            f"OutboxRelay batch_size={relay._batch_size} not documented"
        )

    def test_outbox_sql_queries_consistent(self):
        """Outbox SQL must include key columns referenced in runbook."""
        from shared.events.outbox import SQL_CREATE_OUTBOX_TABLE

        required_columns = [
            "id",
            "subject",
            "payload",
            "status",
            "created_at",
            "sent_at",
            "retry_count",
            "last_error",
            "tenant_id",
            "correlation_id",
        ]
        for col in required_columns:
            assert col in SQL_CREATE_OUTBOX_TABLE, (
                f"Column '{col}' missing from outbox CREATE TABLE"
            )


# ═════════════════════════════════════════════════════════════════════════════
# 6. Event Contract Tests — اختبارات عقود الأحداث
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookEventContractAccuracy:
    """Validate that event contract references match actual code."""

    def test_base_event_importable(self):
        """BaseEvent must be importable from contracts with expected fields."""
        from shared.events.contracts import BaseEvent

        # Pydantic v2 fields are in model_fields, not as class attributes
        fields = BaseEvent.model_fields
        assert "event_id" in fields
        assert "correlation_id" in fields
        assert "causation_id" in fields
        assert "trace_id" in fields
        assert "span_id" in fields

    def test_base_event_fields_documented(self, runbook_content: str):
        """Key BaseEvent fields must be referenced in the runbook."""
        documented_fields = [
            "correlation_id",
            "causation_id",
            "event_id",
            "trace_id",
            "span_id",
        ]
        for field_name in documented_fields:
            assert field_name in runbook_content, (
                f"BaseEvent field '{field_name}' not documented in runbook"
            )

    def test_nats_headers_documented(self, runbook_content: str):
        """NATS header names must match between publisher code and runbook."""
        expected_headers = [
            "X-Correlation-ID",
            "X-Causation-ID",
            "X-Event-ID",
            "X-Tenant-ID",
            "X-Schema-Version",
            "traceparent",
        ]
        for header in expected_headers:
            assert header in runbook_content, (
                f"NATS header '{header}' not documented in runbook"
            )


# ═════════════════════════════════════════════════════════════════════════════
# 7. Idempotency Pattern Tests — اختبارات نمط عدم التكرار
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookIdempotencyAccuracy:
    """Validate idempotency patterns referenced in the runbook."""

    def test_processed_events_table_documented(self, runbook_content: str):
        """processed_events table must be referenced in runbook."""
        assert "processed_events" in runbook_content

    def test_processed_events_pk_documented(self, runbook_content: str):
        """Primary key (tenant_id, event_id) must be documented."""
        assert "tenant_id" in runbook_content
        assert "event_id" in runbook_content

    def test_dedup_cache_size_documented(self, runbook_content: str):
        """In-memory dedup cache size must be documented."""
        # EventSubscriber uses _dedup_max_size = 50_000
        assert "50" in runbook_content  # 50K or 50,000

    def test_subscriber_has_dedup_logic(self):
        """EventSubscriber must have dedup attributes."""
        from shared.events.subscriber import EventSubscriber

        # Verify the class has dedup-related attributes
        sub = EventSubscriber.__new__(EventSubscriber)
        # Check class has expected dedup constants/logic
        source = Path(ROOT_DIR / "shared" / "events" / "subscriber.py").read_text()
        assert "_processed_event_ids" in source, "EventSubscriber missing dedup cache"
        assert "_dedup_max_size" in source, "EventSubscriber missing dedup size limit"


# ═════════════════════════════════════════════════════════════════════════════
# 8. Circuit Breaker Tests — اختبارات قاطع الدائرة
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookCircuitBreakerAccuracy:
    """Validate circuit breaker references in the runbook."""

    def test_circuit_breaker_importable(self):
        """Circuit breaker module must be importable."""
        mod = importlib.import_module("shared.ai.circuit_breaker")
        assert hasattr(mod, "CircuitBreaker") or hasattr(mod, "get_circuit_breaker")

    def test_circuit_breaker_referenced_in_runbook(self, runbook_content: str):
        """Circuit breaker must be mentioned in runbook."""
        assert "circuit breaker" in runbook_content.lower()

    def test_preconfigured_breakers_documented(self, runbook_content: str):
        """Pre-configured circuit breakers must be listed."""
        assert "ollama" in runbook_content
        assert "anthropic" in runbook_content
        assert "openai" in runbook_content


# ═════════════════════════════════════════════════════════════════════════════
# 9. Rate Limiting Tests — اختبارات تحديد المعدل
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookRateLimitAccuracy:
    """Validate rate limiting references in the runbook."""

    def test_rate_limit_module_exists(self):
        """Rate limiting module file must exist in the codebase."""
        path = ROOT_DIR / "shared" / "middleware" / "rate_limit.py"
        assert path.exists(), "shared/middleware/rate_limit.py is missing"

    def test_rate_limit_tiers_documented(self, runbook_content: str):
        """Rate limit tiers must be documented in runbook."""
        # Check key tier values from shared/middleware/rate_limit.py
        assert "30" in runbook_content  # Starter: 30 req/min
        assert "60" in runbook_content  # Professional: 60 req/min
        assert "120" in runbook_content  # Enterprise: 120 req/min
        assert "1000" in runbook_content  # Internal: 1000 req/min


# ═════════════════════════════════════════════════════════════════════════════
# 10. Health Check Tests — اختبارات فحص الصحة
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookHealthCheckAccuracy:
    """Validate health check documentation accuracy."""

    def test_health_module_importable(self):
        """Enhanced health check module must be importable."""
        mod = importlib.import_module("shared.monitoring.health_enhanced")
        assert hasattr(mod, "EnhancedHealthChecker")

    def test_health_endpoints_documented(self, runbook_content: str):
        """Standard health endpoints must be documented."""
        endpoints = ["/healthz", "/readyz", "/health", "/metrics"]
        for endpoint in endpoints:
            assert endpoint in runbook_content, (
                f"Health endpoint '{endpoint}' not documented"
            )

    def test_health_endpoint_probe_mapping(self, runbook_content: str):
        """K8s probe types must be documented."""
        assert "livenessProbe" in runbook_content
        assert "readinessProbe" in runbook_content


# ═════════════════════════════════════════════════════════════════════════════
# 11. Monitoring Infrastructure Tests — اختبارات البنية التحتية للمراقبة
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookMonitoringAccuracy:
    """Validate monitoring references in the runbook."""

    def test_prometheus_config_exists(self):
        """Prometheus configuration file must exist."""
        path = ROOT_DIR / "infrastructure" / "monitoring" / "prometheus" / "prometheus.yml"
        assert path.exists(), "Prometheus config missing"

    def test_nats_alert_rules_exist(self):
        """NATS alert rules file must exist."""
        rules_dir = ROOT_DIR / "infrastructure" / "monitoring" / "prometheus" / "rules"
        if rules_dir.exists():
            rule_files = list(rules_dir.glob("*.yml")) + list(rules_dir.glob("*.yaml"))
            assert len(rule_files) > 0, "No alert rule files found"

    def test_hpa_templates_exist(self):
        """At least some Helm charts should have HPA templates."""
        helm_dir = ROOT_DIR / "helm" / "charts"
        if helm_dir.exists():
            hpa_files = list(helm_dir.glob("*/templates/hpa.yaml"))
            assert len(hpa_files) > 0, "No HPA templates found in Helm charts"


# ═════════════════════════════════════════════════════════════════════════════
# 12. Environment Variables Tests — اختبارات متغيرات البيئة
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRunbookEnvVarAccuracy:
    """Validate environment variable documentation accuracy."""

    def test_dlq_env_vars_documented(self, runbook_content: str):
        """DLQ environment variables must be documented in Appendix B."""
        env_vars = [
            "DLQ_ENABLED",
            "DLQ_MAX_RETRIES",
            "DLQ_INITIAL_DELAY",
            "DLQ_MAX_DELAY",
            "DLQ_BACKOFF_MULTIPLIER",
            "DLQ_STREAM_NAME",
            "DLQ_MAX_AGE_DAYS",
            "DLQ_MAX_MESSAGES",
            "DLQ_ALERT_ENABLED",
            "DLQ_ALERT_THRESHOLD",
            "DLQ_ALERT_CHECK_INTERVAL",
        ]
        for var in env_vars:
            assert var in runbook_content, (
                f"Environment variable '{var}' not documented in runbook"
            )

    def test_dlq_env_defaults_match_code(self):
        """DLQ env var defaults must match DLQConfig.from_env() defaults."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig.from_env()
        assert config.max_retry_attempts == 3
        assert config.initial_retry_delay == 1.0
        assert config.max_retry_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.dlq_stream_name == "SAHOOL_DLQ"
        assert config.dlq_max_age_days == 30
        assert config.dlq_max_messages == 100000
        assert config.alert_threshold == 100

    def test_core_env_vars_documented(self, runbook_content: str):
        """Core infrastructure env vars must be documented."""
        core_vars = ["NATS_URL", "DATABASE_URL", "ENVIRONMENT"]
        for var in core_vars:
            assert var in runbook_content, f"Core env var '{var}' not in runbook"


# ═════════════════════════════════════════════════════════════════════════════
# 13. DLQ Logic Unit Tests — اختبارات وحدة منطق DLQ
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDLQLogic:
    """Validate DLQ retry logic that the runbook describes."""

    def test_should_retry_under_max(self):
        """should_retry returns True for attempts below max."""
        from shared.events.dlq_config import DLQConfig, should_retry

        config = DLQConfig(max_retry_attempts=3)
        assert should_retry(1, config) is True  # attempt 1 < 3
        assert should_retry(2, config) is True  # attempt 2 < 3

    def test_should_not_retry_at_max(self):
        """should_retry returns False when max attempts reached."""
        from shared.events.dlq_config import DLQConfig, should_retry

        config = DLQConfig(max_retry_attempts=3)
        assert should_retry(3, config) is False  # attempt 3 >= 3

    def test_is_retriable_for_connection_error(self):
        """ConnectionError must be classified as retriable."""
        from shared.events.dlq_config import is_retriable_error

        assert is_retriable_error(ConnectionError("timeout")) is True

    def test_is_retriable_for_timeout_error(self):
        """TimeoutError must be classified as retriable."""
        from shared.events.dlq_config import is_retriable_error

        assert is_retriable_error(TimeoutError("deadline")) is True

    def test_not_retriable_for_value_error(self):
        """ValueError must be classified as non-retriable."""
        from shared.events.dlq_config import is_retriable_error

        assert is_retriable_error(ValueError("bad data")) is False

    def test_not_retriable_for_key_error(self):
        """KeyError must be classified as non-retriable."""
        from shared.events.dlq_config import is_retriable_error

        assert is_retriable_error(KeyError("missing")) is False

    def test_not_retriable_for_type_error(self):
        """TypeError must be classified as non-retriable."""
        from shared.events.dlq_config import is_retriable_error

        assert is_retriable_error(TypeError("wrong type")) is False

    def test_exponential_backoff_delays(self):
        """Backoff delays must follow exponential pattern documented in runbook."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig(
            initial_retry_delay=1.0,
            backoff_multiplier=2.0,
            max_retry_delay=60.0,
        )
        assert config.get_retry_delay(1) == 1.0   # 1.0 * 2^0
        assert config.get_retry_delay(2) == 2.0   # 1.0 * 2^1
        assert config.get_retry_delay(3) == 4.0   # 1.0 * 2^2
        assert config.get_retry_delay(4) == 8.0   # 1.0 * 2^3
        assert config.get_retry_delay(10) == 60.0  # Capped at max

    def test_dlq_subject_generation(self):
        """DLQ subject must strip sahool. prefix and prepend dlq prefix."""
        from shared.events.dlq_config import DLQConfig

        config = DLQConfig()
        assert config.get_dlq_subject("sahool.field.created") == "sahool.dlq.field.created"
        assert config.get_dlq_subject("sahool.weather.alert") == "sahool.dlq.weather.alert"

    def test_dlq_metadata_model(self):
        """DLQMessageMetadata must validate correctly."""
        from shared.events.dlq_config import DLQMessageMetadata

        meta = DLQMessageMetadata(
            original_subject="sahool.field.created",
            failure_reason="DB timeout",
            failure_timestamp="2026-02-23T10:00:00Z",
            retry_count=3,
            error_type="TimeoutError",
            consumer_service="crop-intelligence-service",
        )
        assert meta.original_subject == "sahool.field.created"
        assert meta.retry_count == 3
        assert meta.replayed is False
        assert meta.replay_count == 0


# ═════════════════════════════════════════════════════════════════════════════
# 14. Outbox Logic Unit Tests — اختبارات وحدة منطق صندوق الصادر
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOutboxLogic:
    """Validate outbox pattern logic that the runbook describes."""

    def test_outbox_relay_initialization(self):
        """OutboxRelay must initialize with correct defaults."""
        from shared.events.outbox import OutboxRelay

        relay = OutboxRelay(db_pool=None, publisher=None)
        assert relay._poll_interval == 1.0
        assert relay._batch_size == 50
        assert relay.published_count == 0
        assert relay.failed_count == 0
        assert relay._running is False

    def test_outbox_relay_custom_config(self):
        """OutboxRelay must accept custom poll_interval and batch_size."""
        from shared.events.outbox import OutboxRelay

        relay = OutboxRelay(
            db_pool=None,
            publisher=None,
            poll_interval=2.0,
            batch_size=100,
        )
        assert relay._poll_interval == 2.0
        assert relay._batch_size == 100

    def test_outbox_create_table_sql_valid(self):
        """Outbox CREATE TABLE SQL must include all required columns."""
        from shared.events.outbox import SQL_CREATE_OUTBOX_TABLE

        assert "CREATE TABLE IF NOT EXISTS outbox_events" in SQL_CREATE_OUTBOX_TABLE
        assert "PRIMARY KEY" in SQL_CREATE_OUTBOX_TABLE
        assert "idx_outbox_pending" in SQL_CREATE_OUTBOX_TABLE
        assert "idx_outbox_sent_ttl" in SQL_CREATE_OUTBOX_TABLE

    def test_max_relay_retries_reasonable(self):
        """Max relay retries must be a reasonable value."""
        from shared.events.outbox import _MAX_RELAY_RETRIES

        assert 1 <= _MAX_RELAY_RETRIES <= 20, (
            f"_MAX_RELAY_RETRIES={_MAX_RELAY_RETRIES} is outside reasonable range"
        )


# ═════════════════════════════════════════════════════════════════════════════
# 15. BaseEvent Contract Tests — اختبارات عقد الحدث الأساسي
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseEventContract:
    """Validate BaseEvent contract that the runbook describes."""

    def test_base_event_creates_with_defaults(self):
        """BaseEvent must auto-generate event_id and timestamp."""
        from shared.events.contracts import BaseEvent

        event = BaseEvent()
        assert event.event_id is not None
        assert len(event.event_id) > 0
        assert event.timestamp is not None
        assert event.version == "1.0"
        assert event.correlation_id is None
        assert event.causation_id is None

    def test_base_event_with_tracing(self):
        """BaseEvent must support correlation and trace fields."""
        from shared.events.contracts import BaseEvent

        event = BaseEvent(
            correlation_id="corr-123",
            causation_id="cause-456",
            trace_id="abcdef1234567890",
            span_id="1234567890abcdef",
            source_service="advisory-service",
        )
        assert event.correlation_id == "corr-123"
        assert event.causation_id == "cause-456"
        assert event.trace_id == "abcdef1234567890"
        assert event.source_service == "advisory-service"

    def test_base_event_type_property(self):
        """event_type property must return class name."""
        from shared.events.contracts import BaseEvent

        base = BaseEvent()
        assert base.event_type == "BaseEvent"

    def test_field_event_type_property(self):
        """FieldCreatedEvent.event_type must return correct class name."""
        from uuid import uuid4

        from shared.events.contracts import FieldCreatedEvent

        field_event = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            tenant_id=uuid4(),
            name="Test Field",
            geometry_wkt="POINT(46.7 24.7)",
            area_hectares=10.0,
        )
        assert field_event.event_type == "FieldCreatedEvent"


# ═════════════════════════════════════════════════════════════════════════════
# 16. Stream Definition Logic Tests — اختبارات منطق تعريف التدفقات
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestStreamDefinitions:
    """Validate stream definitions that the runbook enumerates."""

    def test_all_streams_have_unique_names(self):
        """Each stream must have a unique name."""
        from shared.events.streams import STREAMS

        names = [s.name for s in STREAMS]
        assert len(names) == len(set(names)), "Duplicate stream names found"

    def test_all_streams_have_subjects(self):
        """Each stream must define at least one subject."""
        from shared.events.streams import STREAMS

        for stream in STREAMS:
            assert len(stream.subjects) > 0, f"Stream '{stream.name}' has no subjects"

    def test_no_overlapping_subjects(self):
        """Stream subjects must not overlap (no two streams catch same event)."""
        from shared.events.streams import STREAMS

        # Extract base subjects (before ">") for each stream
        subject_to_stream: dict[str, str] = {}
        for stream in STREAMS:
            for subject in stream.subjects:
                base = subject.replace(".>", "")
                if base in subject_to_stream:
                    pytest.fail(
                        f"Subject '{base}' is in both '{subject_to_stream[base]}' "
                        f"and '{stream.name}'"
                    )
                subject_to_stream[base] = stream.name

    def test_dlq_stream_config_valid(self):
        """DLQ stream config must be valid."""
        from shared.events.dlq_config import DLQConfig, get_dlq_stream_config

        config = DLQConfig()
        stream_config = get_dlq_stream_config(config)
        assert stream_config.name == "SAHOOL_DLQ"
        assert "sahool.dlq.>" in stream_config.subjects
        assert stream_config.storage == "file"
        assert stream_config.discard == "old"

    def test_stream_defaults_are_sane(self):
        """Default stream properties must be production-safe."""
        from shared.events.streams import StreamDef

        defaults = StreamDef(name="test", subjects=["test.>"])
        assert defaults.max_msgs == 1_000_000
        assert defaults.max_bytes == 5 * 1024 * 1024 * 1024  # 5 GB
        assert defaults.max_msg_size == 1024 * 1024  # 1 MB
        assert defaults.storage == "file"  # not memory
        assert defaults.discard == "old"
        assert defaults.duplicate_window_seconds == 120
