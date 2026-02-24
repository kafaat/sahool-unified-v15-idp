"""Tests for drift detection data models."""

from __future__ import annotations

import pytest

from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
    RemediationResult,
    RemediationStrategy,
)


class TestDriftResult:
    """Tests for DriftResult model."""

    def test_create_default(self):
        result = DriftResult()
        assert result.category == DriftCategory.CONFIG
        assert result.severity == DriftSeverity.MEDIUM
        assert result.auto_fixable is False
        assert result.id  # UUID generated

    def test_create_with_params(self):
        result = DriftResult(
            category=DriftCategory.SECURITY,
            severity=DriftSeverity.CRITICAL,
            source="secret_scan",
            description="Hardcoded password found",
            description_ar="تم العثور على كلمة مرور مشفرة",
            file_path="/app/main.py",
            service_name="user-service",
            auto_fixable=False,
        )
        assert result.category == DriftCategory.SECURITY
        assert result.severity == DriftSeverity.CRITICAL
        assert result.source == "secret_scan"
        assert result.service_name == "user-service"

    def test_to_dict(self):
        result = DriftResult(
            category=DriftCategory.CONFIG,
            severity=DriftSeverity.HIGH,
            source="env_drift",
            description="Missing env var",
        )
        d = result.to_dict()
        assert d["category"] == "config"
        assert d["severity"] == "high"
        assert d["source"] == "env_drift"
        assert "detected_at" in d


class TestDriftReport:
    """Tests for DriftReport model."""

    def test_empty_report(self):
        report = DriftReport()
        assert report.total_drifts == 0
        assert report.critical_count == 0
        assert report.is_clean is True
        assert report.has_critical is False

    def test_report_with_results(self):
        report = DriftReport(
            results=[
                DriftResult(severity=DriftSeverity.CRITICAL, category=DriftCategory.SECURITY),
                DriftResult(severity=DriftSeverity.HIGH, category=DriftCategory.CONFIG),
                DriftResult(severity=DriftSeverity.MEDIUM, category=DriftCategory.CONFIG),
                DriftResult(severity=DriftSeverity.LOW, auto_fixable=True),
            ],
            categories_checked=[DriftCategory.CONFIG, DriftCategory.SECURITY],
        )
        assert report.total_drifts == 4
        assert report.critical_count == 1
        assert report.high_count == 1
        assert report.auto_fixable_count == 1
        assert report.is_clean is False
        assert report.has_critical is True

    def test_by_category(self):
        report = DriftReport(
            results=[
                DriftResult(category=DriftCategory.CONFIG),
                DriftResult(category=DriftCategory.CONFIG),
                DriftResult(category=DriftCategory.SECURITY),
            ]
        )
        assert len(report.by_category(DriftCategory.CONFIG)) == 2
        assert len(report.by_category(DriftCategory.SECURITY)) == 1
        assert len(report.by_category(DriftCategory.SCHEMA)) == 0

    def test_by_severity(self):
        report = DriftReport(
            results=[
                DriftResult(severity=DriftSeverity.CRITICAL),
                DriftResult(severity=DriftSeverity.HIGH),
                DriftResult(severity=DriftSeverity.HIGH),
            ]
        )
        assert len(report.by_severity(DriftSeverity.CRITICAL)) == 1
        assert len(report.by_severity(DriftSeverity.HIGH)) == 2

    def test_by_service(self):
        report = DriftReport(
            results=[
                DriftResult(service_name="user-service"),
                DriftResult(service_name="user-service"),
                DriftResult(service_name="field-management-service"),
            ]
        )
        assert len(report.by_service("user-service")) == 2

    def test_summary(self):
        report = DriftReport(
            environment="staging",
            triggered_by="ci",
            categories_checked=[DriftCategory.CONFIG],
        )
        summary = report.summary()
        assert summary["environment"] == "staging"
        assert summary["triggered_by"] == "ci"
        assert summary["is_clean"] is True

    def test_to_markdown(self):
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.CONFIG,
                    severity=DriftSeverity.HIGH,
                    source="env_drift",
                    description="Missing DB_URL",
                    auto_fixable=True,
                ),
            ]
        )
        md = report.to_markdown()
        assert "# Drift Detection Report" in md
        assert "Config Drift" in md
        assert "Missing DB_URL" in md


class TestRemediationModels:
    """Tests for remediation models."""

    def test_remediation_action(self):
        action = RemediationAction(
            drift_result_id="abc123",
            strategy=RemediationStrategy.BLOCK_PR,
            description="Block for security violation",
            dry_run=True,
        )
        assert action.strategy == RemediationStrategy.BLOCK_PR
        assert action.dry_run is True

    def test_remediation_result(self):
        result = RemediationResult(
            action_id="xyz789",
            success=True,
            output="Fix applied",
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == "Fix applied"
