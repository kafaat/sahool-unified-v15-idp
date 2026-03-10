"""Tests for drift detection engine, quality gates, and remediation."""

from __future__ import annotations

import pytest

from shared.drift_detection.engine import DriftDetectionEngine
from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationStrategy,
)
from shared.drift_detection.quality_gates import (
    GateStage,
    GateStatus,
    QualityGatesEngine,
)
from shared.drift_detection.remediation import (
    AutoRemediationEngine,
    RemediationPolicy,
)


class TestDriftDetectionEngine:
    """Tests for DriftDetectionEngine orchestrator."""

    @pytest.mark.asyncio
    async def test_full_scan(self, tmp_path):
        engine = DriftDetectionEngine(
            working_dir=str(tmp_path),
            environment="development",
        )
        report = await engine.run_full_scan(triggered_by="test")

        assert isinstance(report, DriftReport)
        assert report.environment == "development"
        assert report.triggered_by == "test"
        assert len(report.categories_checked) == len(DriftCategory)

    @pytest.mark.asyncio
    async def test_selective_scan(self, tmp_path):
        engine = DriftDetectionEngine(working_dir=str(tmp_path))
        report = await engine.run_scan(
            categories=[DriftCategory.CONFIG, DriftCategory.SECURITY],
            triggered_by="ci",
        )

        assert len(report.categories_checked) == 2
        assert DriftCategory.CONFIG in report.categories_checked
        assert DriftCategory.SECURITY in report.categories_checked

    @pytest.mark.asyncio
    async def test_scan_with_string_categories(self, tmp_path):
        engine = DriftDetectionEngine(working_dir=str(tmp_path))
        report = await engine.run_scan(categories=["config", "api"])
        assert DriftCategory.CONFIG in report.categories_checked
        assert DriftCategory.API in report.categories_checked

    def test_ci_exit_code_clean(self):
        engine = DriftDetectionEngine()
        report = DriftReport()
        assert engine.get_ci_exit_code(report) == 0

    def test_ci_exit_code_critical(self):
        engine = DriftDetectionEngine()
        report = DriftReport(results=[DriftResult(severity=DriftSeverity.CRITICAL)])
        assert engine.get_ci_exit_code(report) == 1

    def test_ci_exit_code_high(self):
        engine = DriftDetectionEngine()
        report = DriftReport(results=[DriftResult(severity=DriftSeverity.HIGH)])
        assert engine.get_ci_exit_code(report) == 1

    def test_ci_exit_code_medium(self):
        engine = DriftDetectionEngine()
        report = DriftReport(results=[DriftResult(severity=DriftSeverity.MEDIUM)])
        assert engine.get_ci_exit_code(report) == 2

    def test_json_output(self):
        engine = DriftDetectionEngine()
        report = DriftReport(
            results=[DriftResult(description="Test drift")],
            categories_checked=[DriftCategory.CONFIG],
        )
        json_str = engine.to_json(report)
        assert "summary" in json_str
        assert "Test drift" in json_str


class TestQualityGatesEngine:
    """Tests for QualityGatesEngine."""

    @pytest.mark.asyncio
    async def test_pr_gate_clean_report(self):
        engine = QualityGatesEngine()
        report = DriftReport()
        result = await engine.evaluate_pr_gate(report)

        assert result.stage == GateStage.PR
        # Drift check should pass on clean report
        drift_checks = [c for c in result.checks if c.name == "drift_detection"]
        assert len(drift_checks) == 1
        assert drift_checks[0].status == GateStatus.PASSED

    @pytest.mark.asyncio
    async def test_pr_gate_critical_drift(self):
        engine = QualityGatesEngine()
        report = DriftReport(results=[DriftResult(severity=DriftSeverity.CRITICAL)])
        result = await engine.evaluate_pr_gate(report)

        drift_checks = [c for c in result.checks if c.name == "drift_detection"]
        assert drift_checks[0].status == GateStatus.FAILED

    @pytest.mark.asyncio
    async def test_pr_gate_medium_drift(self):
        engine = QualityGatesEngine()
        report = DriftReport(results=[DriftResult(severity=DriftSeverity.MEDIUM)])
        result = await engine.evaluate_pr_gate(report)

        drift_checks = [c for c in result.checks if c.name == "drift_detection"]
        assert drift_checks[0].status == GateStatus.WARNING

    def test_gate_definitions(self):
        engine = QualityGatesEngine()
        definitions = engine.get_gate_definitions()
        assert "pr" in definitions
        assert "merge" in definitions
        assert "deploy" in definitions
        assert "runtime" in definitions
        assert len(definitions["pr"]) > 0


class TestAutoRemediationEngine:
    """Tests for AutoRemediationEngine."""

    def test_plan_remediation_empty_report(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport()
        actions = engine.plan_remediation(report)
        assert len(actions) == 0

    def test_plan_remediation_critical_security(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.CRITICAL,
                    description="Hardcoded secret found",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.BLOCK_PR

    def test_plan_remediation_high_config(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.CONFIG,
                    severity=DriftSeverity.HIGH,
                    description="Config drift detected",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.BLOCK_PR

    def test_plan_remediation_medium_config(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.CONFIG,
                    severity=DriftSeverity.MEDIUM,
                    description="Medium config issue",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.CREATE_ISSUE

    @pytest.mark.asyncio
    async def test_execute_dry_run(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.SECURITY,
                    severity=DriftSeverity.CRITICAL,
                    description="Test finding",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        results = await engine.execute(actions)

        assert len(results) == 1
        assert results[0].success is True
        assert "[DRY RUN]" in results[0].output

    @pytest.mark.asyncio
    async def test_execute_requires_approval(self):
        """Event drift with default policy requires human approval."""
        engine = AutoRemediationEngine(dry_run=False)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.HIGH,
                    description="Missing idempotency",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        results = await engine.execute(actions)

        assert len(results) == 1
        # Event drift requires approval by default
        assert results[0].output == "Requires human approval"

    @pytest.mark.asyncio
    async def test_execute_alert_auto_approved(self):
        """Alert-only with auto_approve=True should succeed."""
        custom_policies = [
            RemediationPolicy(
                category=DriftCategory.EVENT,
                min_severity=DriftSeverity.HIGH,
                strategy=RemediationStrategy.ALERT_ONLY,
                auto_approve=True,
                description="Auto-approved alert",
            )
        ]
        engine = AutoRemediationEngine(policies=custom_policies, dry_run=False)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.HIGH,
                    description="Missing idempotency",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        results = await engine.execute(actions)

        assert len(results) == 1
        assert results[0].success is True

    def test_summary(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
                DriftResult(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
            ]
        )
        engine.plan_remediation(report)
        summary = engine.summary()
        assert summary["total_actions"] == 2
        assert summary["dry_run"] is True

    def test_custom_policies(self):
        custom_policies = [
            RemediationPolicy(
                category=DriftCategory.DATA,
                min_severity=DriftSeverity.LOW,
                strategy=RemediationStrategy.AUTO_RESTART,
                auto_approve=True,
                description="Restart on any data drift",
            )
        ]
        engine = AutoRemediationEngine(policies=custom_policies, dry_run=True)
        report = DriftReport(
            results=[
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.LOW,
                    description="Data quality issue",
                )
            ]
        )
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.AUTO_RESTART
