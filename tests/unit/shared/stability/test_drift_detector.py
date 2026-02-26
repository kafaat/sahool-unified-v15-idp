"""
Tests for SAHOOL Drift Detection System
==========================================
"""

import pytest
import tempfile
from pathlib import Path

from shared.stability.drift_detector import (
    DriftDetector,
    DriftReport,
    DriftType,
    DriftSeverity,
)


class TestConfigDrift:
    """Tests for config drift detection."""

    def test_detect_missing_env_vars(self, tmp_path):
        """Test detection of declared but unset env vars."""
        # Create .env.example
        env_example = tmp_path / ".env.example"
        env_example.write_text(
            "DATABASE_URL=postgresql://localhost:5432/sahool\n"
            "JWT_SECRET_KEY=change-me\n"
            "NATS_URL=nats://localhost:4222\n"
        )
        # Create governance dir so project root is found
        (tmp_path / "governance").mkdir()

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_config_drift(env_override={
            "DATABASE_URL": "postgresql://localhost:5432/sahool",
            # JWT_SECRET_KEY and NATS_URL missing
        })

        assert len(report.items) >= 2
        missing_vars = {d.resource for d in report.items}
        assert "JWT_SECRET_KEY" in missing_vars
        assert "NATS_URL" in missing_vars

    def test_detect_all_vars_set(self, tmp_path):
        """Test no drift when all vars are set."""
        env_example = tmp_path / ".env.example"
        env_example.write_text(
            "DATABASE_URL=postgresql://localhost:5432/sahool\n"
            "LOG_LEVEL=INFO\n"
        )
        (tmp_path / "governance").mkdir()

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_config_drift(env_override={
            "DATABASE_URL": "postgresql://localhost:5432/sahool",
            "LOG_LEVEL": "DEBUG",
        })

        assert len(report.items) == 0

    def test_secrets_get_higher_severity(self, tmp_path):
        """Test that secret-like vars get higher severity."""
        env_example = tmp_path / ".env.example"
        env_example.write_text(
            "JWT_SECRET_KEY=test\n"
            "LOG_LEVEL=INFO\n"
        )
        (tmp_path / "governance").mkdir()

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_config_drift(env_override={})

        # JWT_SECRET_KEY should be HIGH severity
        jwt_drift = [d for d in report.items if d.resource == "JWT_SECRET_KEY"]
        assert len(jwt_drift) == 1
        assert jwt_drift[0].severity == DriftSeverity.HIGH

        # LOG_LEVEL should be MEDIUM severity
        log_drift = [d for d in report.items if d.resource == "LOG_LEVEL"]
        assert len(log_drift) == 1
        assert log_drift[0].severity == DriftSeverity.MEDIUM


class TestServiceDrift:
    """Tests for service registry drift detection."""

    def test_detect_unregistered_service(self, tmp_path):
        """Test detection of service directory not in registry."""
        pytest.importorskip("yaml")

        # Setup governance/services.yaml
        gov = tmp_path / "governance"
        gov.mkdir()
        services_yaml = gov / "services.yaml"
        services_yaml.write_text(
            "services:\n"
            "  - name: field-management-service\n"
            "    owner: kafaat\n"
            "    team: platform\n"
            "    lifecycle: production\n"
            "    tier: tier-1\n"
        )

        # Setup service directories
        services = tmp_path / "apps" / "services"
        services.mkdir(parents=True)
        (services / "field-management-service").mkdir()
        (services / "unregistered-service").mkdir()

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_service_drift()

        # unregistered-service should be flagged
        unregistered = [d for d in report.items if d.resource == "unregistered-service"]
        assert len(unregistered) == 1
        assert "not in governance registry" in unregistered[0].message

    def test_detect_deprecated_still_active(self, tmp_path):
        """Test detection of deprecated service still in active directory."""
        pytest.importorskip("yaml")

        gov = tmp_path / "governance"
        gov.mkdir()
        services_yaml = gov / "services.yaml"
        services_yaml.write_text(
            "services:\n"
            "  - name: old-service\n"
            "    owner: kafaat\n"
            "    team: platform\n"
            "    lifecycle: deprecated\n"
            "    tier: tier-3\n"
        )

        services = tmp_path / "apps" / "services"
        services.mkdir(parents=True)
        (services / "old-service").mkdir()

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_service_drift()

        deprecated = [d for d in report.items if d.resource == "old-service"]
        assert len(deprecated) == 1
        assert "deprecated" in deprecated[0].message.lower()


class TestDockerDrift:
    """Tests for Docker drift detection."""

    def test_detect_missing_user_directive(self, tmp_path):
        """Test detection of Dockerfile without USER directive."""
        (tmp_path / "governance").mkdir()
        services = tmp_path / "apps" / "services"
        svc = services / "test-service"
        svc.mkdir(parents=True)

        dockerfile = svc / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "CMD [\"python\", \"main.py\"]\n"
        )

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_docker_drift()

        security = [d for d in report.items if d.drift_type == DriftType.SECURITY]
        assert len(security) >= 1
        assert any("USER" in d.message for d in security)

    def test_detect_missing_healthcheck(self, tmp_path):
        """Test detection of Dockerfile without HEALTHCHECK."""
        (tmp_path / "governance").mkdir()
        services = tmp_path / "apps" / "services"
        svc = services / "test-service"
        svc.mkdir(parents=True)

        dockerfile = svc / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11-slim\n"
            "USER sahool\n"
            "WORKDIR /app\n"
            "CMD [\"python\", \"main.py\"]\n"
        )

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_docker_drift()

        docker_drift = [d for d in report.items if d.drift_type == DriftType.DOCKER]
        assert any("HEALTHCHECK" in d.message for d in docker_drift)

    def test_good_dockerfile_no_drift(self, tmp_path):
        """Test that a compliant Dockerfile produces no drift."""
        (tmp_path / "governance").mkdir()
        services = tmp_path / "apps" / "services"
        svc = services / "good-service"
        svc.mkdir(parents=True)

        dockerfile = svc / "Dockerfile"
        dockerfile.write_text(
            "FROM python:3.11-slim\n"
            "RUN adduser --uid 1000 sahool\n"
            "USER sahool\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "HEALTHCHECK CMD curl -f http://localhost:8080/healthz || exit 1\n"
            "CMD [\"python\", \"main.py\"]\n"
        )

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_docker_drift()

        svc_items = [d for d in report.items if d.resource == "good-service"]
        assert len(svc_items) == 0


class TestDriftReport:
    """Tests for DriftReport."""

    def test_empty_report_is_clean(self):
        report = DriftReport()
        assert report.is_clean
        assert not report.has_critical

    def test_summary_format(self):
        report = DriftReport(checks_run=10)
        report.items.append(
            __import__("shared.stability.drift_detector", fromlist=["DriftItem"]).DriftItem(
                drift_type=DriftType.CONFIG,
                severity=DriftSeverity.HIGH,
                resource="TEST_VAR",
                expected="set",
                actual="not set",
                message="Test drift",
                message_ar="انحراف تجريبي",
            )
        )
        summary = report.summary()

        assert summary["checks_run"] == 10
        assert summary["total_drift"] == 1
        assert summary["high"] == 1
        assert "config" in summary["by_type"]


class TestDetectAll:
    """Tests for running all drift checks."""

    def test_detect_all_returns_combined(self, tmp_path):
        """Test that detect_all combines all drift types."""
        (tmp_path / "governance").mkdir()
        env_example = tmp_path / ".env.example"
        env_example.write_text("TEST_VAR=value\n")

        detector = DriftDetector(project_root=str(tmp_path))
        report = detector.detect_all()

        assert report.checks_run >= 0
        assert report.timestamp != ""
