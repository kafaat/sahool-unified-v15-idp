"""
Tests for SAHOOL Auto-Remediation Engine
==========================================
"""

import pytest
from unittest.mock import MagicMock

from shared.stability.remediation import (
    RemediationEngine,
    RemediationAction,
    RemediationPlan,
    RemediationType,
    RemediationStatus,
)


class TestRemediationEngine:
    """Tests for the RemediationEngine."""

    def _make_drift_item(self, drift_type, severity, resource, message):
        """Helper to create mock drift items."""
        item = MagicMock()
        item.drift_type = MagicMock()
        item.drift_type.value = drift_type
        item.severity = MagicMock()
        item.severity.value = severity
        item.resource = resource
        item.message = message
        item.message_ar = message
        return item

    def test_plan_from_config_drift(self):
        """Test remediation plan generation from config drift."""
        engine = RemediationEngine(dry_run=True)

        drift_report = MagicMock()
        drift_report.items = [
            self._make_drift_item("config", "high", "DATABASE_URL", "DATABASE_URL not set"),
        ]

        plan = engine.plan_from_drift(drift_report)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == RemediationType.CREATE_ISSUE
        assert plan.actions[0].resource == "DATABASE_URL"

    def test_plan_from_service_drift_deprecated(self):
        """Test remediation plan for deprecated service drift."""
        engine = RemediationEngine(dry_run=True)

        drift_report = MagicMock()
        drift_report.items = [
            self._make_drift_item("service", "medium", "old-service", "Deprecated service 'old-service' still active"),
        ]

        plan = engine.plan_from_drift(drift_report)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == RemediationType.MANUAL_FIX
        assert "old-service" in plan.actions[0].resource

    def test_plan_from_security_drift(self):
        """Test remediation plan for security drift (Dockerfile root USER)."""
        engine = RemediationEngine(dry_run=True)

        drift_report = MagicMock()
        drift_report.items = [
            self._make_drift_item(
                "security", "high", "test-service",
                "Service 'test-service' Dockerfile has no USER directive (runs as root)"
            ),
        ]

        plan = engine.plan_from_drift(drift_report)

        assert len(plan.actions) == 1
        assert plan.actions[0].action_type == RemediationType.AUTO_FIX
        assert plan.actions[0].is_safe is True


class TestAlertRemediation:
    """Tests for alert-based remediation."""

    def test_service_down_alert(self):
        engine = RemediationEngine()
        action = engine.plan_from_alert(
            alert_name="ServiceDown",
            alert_labels={"service": "advisory-service", "instance": "pod-123"},
        )

        assert action is not None
        assert action.action_type == RemediationType.RESTART
        assert action.severity == "critical"
        assert "advisory-service" in action.description

    def test_queue_backlog_alert(self):
        engine = RemediationEngine()
        action = engine.plan_from_alert(
            alert_name="QueueBacklog",
            alert_labels={"stream": "SAHOOL_INTELLIGENCE"},
        )

        assert action is not None
        assert action.action_type == RemediationType.SCALE
        assert "SAHOOL_INTELLIGENCE" in action.description

    def test_unknown_alert_returns_none(self):
        engine = RemediationEngine()
        action = engine.plan_from_alert(
            alert_name="UnknownAlert",
            alert_labels={"service": "test"},
        )

        assert action is None

    def test_high_error_rate_alert(self):
        engine = RemediationEngine()
        action = engine.plan_from_alert(
            alert_name="HighErrorRate",
            alert_labels={"service": "weather-service"},
        )

        assert action is not None
        assert action.action_type == RemediationType.ALERT
        assert action.severity == "high"


class TestSLORemediation:
    """Tests for SLO-based remediation."""

    def test_critical_burn_rate(self):
        engine = RemediationEngine()
        action = engine.plan_slo_remediation(
            service_name="field-management",
            error_budget_remaining=0.50,
            burn_rate_1h=15.0,
        )

        assert action is not None
        assert action.action_type == RemediationType.ROLLBACK
        assert action.severity == "critical"

    def test_high_burn_rate(self):
        engine = RemediationEngine()
        action = engine.plan_slo_remediation(
            service_name="user-service",
            error_budget_remaining=0.30,
            burn_rate_1h=8.0,
        )

        assert action is not None
        assert action.action_type == RemediationType.ALERT
        assert action.severity == "high"

    def test_low_error_budget(self):
        engine = RemediationEngine()
        action = engine.plan_slo_remediation(
            service_name="advisory-service",
            error_budget_remaining=0.05,
            burn_rate_1h=1.0,
        )

        assert action is not None
        assert action.action_type == RemediationType.PAUSE
        assert "freeze" in action.description.lower()

    def test_healthy_slo_no_action(self):
        engine = RemediationEngine()
        action = engine.plan_slo_remediation(
            service_name="healthy-service",
            error_budget_remaining=0.80,
            burn_rate_1h=0.5,
        )

        assert action is None


class TestRemediationPlan:
    """Tests for RemediationPlan."""

    def test_plan_summary(self):
        plan = RemediationPlan(dry_run=True)
        plan.actions = [
            RemediationAction(
                action_type=RemediationType.AUTO_FIX,
                severity="high",
                resource="test",
                description="Fix something",
                description_ar="إصلاح شيء",
                is_safe=True,
            ),
            RemediationAction(
                action_type=RemediationType.MANUAL_FIX,
                severity="medium",
                resource="test2",
                description="Manual fix needed",
                description_ar="إصلاح يدوي مطلوب",
                is_safe=False,
            ),
        ]

        assert len(plan.auto_fixable) == 1
        assert len(plan.manual_required) == 1

        summary = plan.summary()
        assert summary["total_actions"] == 2
        assert summary["auto_fixable"] == 1
        assert summary["manual_required"] == 1
        assert summary["dry_run"] is True

    @pytest.mark.asyncio
    async def test_dry_run_skips_execution(self):
        engine = RemediationEngine(dry_run=True)
        plan = RemediationPlan(dry_run=True)
        plan.actions = [
            RemediationAction(
                action_type=RemediationType.AUTO_FIX,
                severity="low",
                resource="test",
                description="Test action",
                description_ar="إجراء تجريبي",
                is_safe=True,
            ),
        ]

        result = await engine.execute_plan(plan)

        assert result.actions[0].status == RemediationStatus.SKIPPED
        assert "Dry run" in result.actions[0].result
