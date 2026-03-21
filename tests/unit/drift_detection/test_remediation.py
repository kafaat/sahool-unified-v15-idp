"""
Tests for the AutoRemediationEngine.
اختبارات لمحرك التصحيح التلقائي.

Covers strategy execution, audit logging, policy matching edge cases,
error handling, and the full plan→execute→audit lifecycle.
"""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
    RemediationStrategy,
)
from shared.drift_detection.remediation import (
    AutoRemediationEngine,
    DEFAULT_POLICIES,
    RemediationPolicy,
    SEVERITY_ORDER,
    _count_by_strategy,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_drift(
    category: DriftCategory = DriftCategory.CONFIG,
    severity: DriftSeverity = DriftSeverity.HIGH,
    description: str = "test drift",
    description_ar: str = "انحراف تجريبي",
    service_name: str = "test-service",
    file_path: str = "docker-compose.yml",
    source: str = "test",
) -> DriftResult:
    return DriftResult(
        category=category,
        severity=severity,
        description=description,
        description_ar=description_ar,
        service_name=service_name,
        file_path=file_path,
        source=source,
    )


def _make_report(*drifts: DriftResult) -> DriftReport:
    return DriftReport(results=list(drifts))


# ---------------------------------------------------------------------------
# Policy Matching
# ---------------------------------------------------------------------------


class TestPolicyMatching:
    """Tests for _match_policy and plan_remediation policy selection."""

    def test_no_match_for_low_severity(self):
        """LOW config drift does not match any default policy (min is MEDIUM)."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(severity=DriftSeverity.LOW))
        actions = engine.plan_remediation(report)
        assert len(actions) == 0

    def test_info_severity_no_match(self):
        """INFO severity never triggers remediation."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(severity=DriftSeverity.INFO))
        assert engine.plan_remediation(report) == []

    def test_critical_config_matches_block_pr(self):
        """CRITICAL config drift should match the HIGH BLOCK_PR policy (more severe qualifies)."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.CRITICAL))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.BLOCK_PR

    def test_high_api_matches_auto_fix(self):
        """HIGH API drift matches the AUTO_FIX policy."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.API, severity=DriftSeverity.HIGH))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.AUTO_FIX

    def test_critical_api_matches_block_pr_over_auto_fix(self):
        """CRITICAL API drift should match BLOCK_PR (most specific high-severity policy)."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.API, severity=DriftSeverity.CRITICAL))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.BLOCK_PR

    def test_high_security_matches_create_issue(self):
        """HIGH security drift matches CREATE_ISSUE policy."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.HIGH))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.CREATE_ISSUE

    def test_medium_schema_no_match(self):
        """MEDIUM schema drift is below min_severity for all schema policies."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.SCHEMA, severity=DriftSeverity.MEDIUM))
        assert engine.plan_remediation(report) == []

    def test_high_data_matches_alert_only(self):
        """HIGH data drift matches the ALERT_ONLY policy."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.DATA, severity=DriftSeverity.HIGH))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.ALERT_ONLY

    def test_multiple_drifts_produce_multiple_actions(self):
        """Multiple drifts each get their own action."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.MEDIUM),
            _make_drift(category=DriftCategory.EVENT, severity=DriftSeverity.HIGH),
        )
        actions = engine.plan_remediation(report)
        assert len(actions) == 3
        strategies = {a.strategy for a in actions}
        assert RemediationStrategy.BLOCK_PR in strategies
        assert RemediationStrategy.CREATE_ISSUE in strategies
        assert RemediationStrategy.ALERT_ONLY in strategies

    def test_custom_policies_override_defaults(self):
        """Engine with custom policies ignores the defaults entirely."""
        custom = [
            RemediationPolicy(
                category=DriftCategory.CONFIG,
                min_severity=DriftSeverity.INFO,
                strategy=RemediationStrategy.AUTO_RESTART,
                auto_approve=True,
                description="Restart on any config drift",
            )
        ]
        engine = AutoRemediationEngine(policies=custom, dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.INFO))
        actions = engine.plan_remediation(report)
        assert len(actions) == 1
        assert actions[0].strategy == RemediationStrategy.AUTO_RESTART

    def test_plan_clears_previous_actions(self):
        """Calling plan_remediation a second time replaces the first plan."""
        engine = AutoRemediationEngine(dry_run=True)
        report1 = _make_report(
            _make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
        )
        report2 = _make_report(
            _make_drift(category=DriftCategory.EVENT, severity=DriftSeverity.HIGH),
        )
        actions1 = engine.plan_remediation(report1)
        assert len(actions1) == 2
        actions2 = engine.plan_remediation(report2)
        assert len(actions2) == 1


# ---------------------------------------------------------------------------
# Action Metadata
# ---------------------------------------------------------------------------


class TestActionMetadata:
    """Tests that planned actions carry correct metadata."""

    def test_action_fields_populated(self):
        engine = AutoRemediationEngine(dry_run=True)
        drift = _make_drift(
            category=DriftCategory.SECURITY,
            severity=DriftSeverity.CRITICAL,
            service_name="user-service",
            file_path="apps/services/user-service/Dockerfile",
            source="dockerfile_scanner",
        )
        report = _make_report(drift)
        actions = engine.plan_remediation(report)

        action = actions[0]
        assert action.drift_result_id == drift.id
        assert action.target_service == "user-service"
        assert action.target_file == "apps/services/user-service/Dockerfile"
        assert action.dry_run is True
        assert action.metadata["drift_category"] == "security"
        assert action.metadata["drift_severity"] == "critical"
        assert action.metadata["drift_source"] == "dockerfile_scanner"

    def test_auto_approve_sets_requires_approval_false(self):
        """auto_approve=True on policy → requires_approval=False on action."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL))
        actions = engine.plan_remediation(report)
        # Security CRITICAL policy has auto_approve=True
        assert actions[0].requires_approval is False

    def test_no_auto_approve_sets_requires_approval_true(self):
        """auto_approve=False on policy → requires_approval=True on action."""
        engine = AutoRemediationEngine(dry_run=True)
        # Event HIGH policy has auto_approve=False (default)
        report = _make_report(_make_drift(category=DriftCategory.EVENT, severity=DriftSeverity.HIGH))
        actions = engine.plan_remediation(report)
        assert actions[0].requires_approval is True

    def test_description_includes_strategy(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(
                category=DriftCategory.CONFIG,
                severity=DriftSeverity.HIGH,
                description="Port mismatch on field-management-service",
            )
        )
        actions = engine.plan_remediation(report)
        assert "[block_pr]" in actions[0].description


# ---------------------------------------------------------------------------
# Strategy Execution
# ---------------------------------------------------------------------------


class TestExecuteBlockPR:
    """Tests for the BLOCK_PR strategy execution path."""

    @pytest.mark.asyncio
    async def test_block_pr_succeeds(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.BLOCK_PR,
            description="Block: port collision",
            requires_approval=False,
        )
        result = await engine._execute_block_pr(action)
        assert result.success is True
        assert "PR BLOCKED" in result.output

    @pytest.mark.asyncio
    async def test_block_pr_via_execute(self):
        """BLOCK_PR action flows through execute() correctly."""
        engine = AutoRemediationEngine(dry_run=False)
        report = _make_report(_make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL))
        actions = engine.plan_remediation(report)
        # Override dry_run on the action since engine is not dry_run
        for a in actions:
            a.dry_run = False
        results = await engine.execute(actions)
        assert len(results) == 1
        assert results[0].success is True
        assert "PR BLOCKED" in results[0].output


class TestExecuteCreateIssue:
    """Tests for the CREATE_ISSUE strategy execution path."""

    @pytest.mark.asyncio
    async def test_create_issue_builds_body(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.CREATE_ISSUE,
            description="Config drift in user-service",
            description_ar="انحراف التكوين في خدمة المستخدم",
            target_service="user-service",
            target_file="docker-compose.yml",
            requires_approval=False,
            metadata={
                "drift_category": "config",
                "drift_severity": "high",
            },
        )
        result = await engine._execute_create_issue(action)
        assert result.success is True
        assert "Issue created" in result.output

    @pytest.mark.asyncio
    async def test_create_issue_via_execute(self):
        custom = [
            RemediationPolicy(
                category=DriftCategory.CONFIG,
                min_severity=DriftSeverity.MEDIUM,
                strategy=RemediationStrategy.CREATE_ISSUE,
                auto_approve=True,
            )
        ]
        engine = AutoRemediationEngine(policies=custom, dry_run=False)
        report = _make_report(_make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.MEDIUM))
        actions = engine.plan_remediation(report)
        for a in actions:
            a.dry_run = False
        results = await engine.execute(actions)
        assert results[0].success is True


class TestExecuteAlertOnly:
    """Tests for the ALERT_ONLY strategy execution path."""

    @pytest.mark.asyncio
    async def test_alert_only_succeeds(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.ALERT_ONLY,
            description="Data quality degradation",
            requires_approval=False,
            dry_run=False,
        )
        result = await engine._execute_action(action)
        assert result.success is True
        assert "Alert:" in result.output


class TestExecuteAutoFix:
    """Tests for the AUTO_FIX strategy execution path."""

    @pytest.mark.asyncio
    async def test_auto_fix_success(self):
        engine = AutoRemediationEngine(working_dir="/tmp", dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_FIX,
            command="ruff check --fix .",
            requires_approval=False,
            dry_run=False,
        )
        with patch("shared.drift_detection.remediation.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["ruff", "check", "--fix", "."], returncode=0, stdout="fixed", stderr=""
            )
            result = await engine._execute_auto_fix(action)
        assert result.success is True
        assert "fixed" in result.output

    @pytest.mark.asyncio
    async def test_auto_fix_failure(self):
        engine = AutoRemediationEngine(working_dir="/tmp", dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_FIX,
            command="ruff check .",
            requires_approval=False,
            dry_run=False,
        )
        with patch("shared.drift_detection.remediation.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["ruff", "check", "."], returncode=1, stdout="", stderr="lint errors"
            )
            result = await engine._execute_auto_fix(action)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_auto_fix_no_command(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_FIX,
            command="",
            requires_approval=False,
            dry_run=False,
        )
        result = await engine._execute_auto_fix(action)
        assert result.success is False
        assert "No command specified" in result.error

    @pytest.mark.asyncio
    async def test_auto_fix_timeout(self):
        engine = AutoRemediationEngine(working_dir="/tmp", dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_FIX,
            command="ruff check --fix .",
            requires_approval=False,
            dry_run=False,
        )
        with patch("shared.drift_detection.remediation.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="ruff check --fix .", timeout=60)
            result = await engine._execute_auto_fix(action)
        assert result.success is False
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_auto_fix_via_execute(self):
        custom = [
            RemediationPolicy(
                category=DriftCategory.API,
                min_severity=DriftSeverity.HIGH,
                strategy=RemediationStrategy.AUTO_FIX,
                auto_approve=True,
            )
        ]
        engine = AutoRemediationEngine(policies=custom, working_dir="/tmp", dry_run=False)
        drift = _make_drift(category=DriftCategory.API, severity=DriftSeverity.HIGH)
        report = _make_report(drift)
        actions = engine.plan_remediation(report)
        for a in actions:
            a.dry_run = False
            a.command = "npx prisma generate"
        with patch("shared.drift_detection.remediation.subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["npx", "prisma", "generate"], returncode=0, stdout="contract regenerated", stderr=""
            )
            results = await engine.execute(actions)
        assert results[0].success is True
        assert "contract regenerated" in results[0].output


class TestExecuteAutoRestart:
    """Tests for the AUTO_RESTART strategy execution path."""

    @pytest.mark.asyncio
    async def test_auto_restart_with_service(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_RESTART,
            target_service="weather-service",
            requires_approval=False,
            dry_run=False,
        )
        result = await engine._execute_auto_restart(action)
        assert result.success is True
        assert "weather-service" in result.output

    @pytest.mark.asyncio
    async def test_auto_restart_no_service(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_RESTART,
            target_service="",
            requires_approval=False,
            dry_run=False,
        )
        result = await engine._execute_auto_restart(action)
        assert result.success is False
        assert "No target service" in result.error


# ---------------------------------------------------------------------------
# Dry Run
# ---------------------------------------------------------------------------


class TestDryRun:
    """Tests that dry-run mode prevents actual execution."""

    @pytest.mark.asyncio
    async def test_dry_run_all_strategies(self):
        """All strategies produce '[DRY RUN]' output when dry_run=True."""
        engine = AutoRemediationEngine(dry_run=True)
        strategies_and_services = [
            (RemediationStrategy.BLOCK_PR, "svc-a", ""),
            (RemediationStrategy.CREATE_ISSUE, "svc-b", ""),
            (RemediationStrategy.AUTO_FIX, "", "echo hello"),
            (RemediationStrategy.AUTO_RESTART, "svc-c", ""),
            (RemediationStrategy.ALERT_ONLY, "svc-d", ""),
        ]
        for strategy, service, command in strategies_and_services:
            action = RemediationAction(
                strategy=strategy,
                target_service=service,
                command=command,
                dry_run=True,
            )
            result = await engine._execute_action(action)
            assert result.success is True, f"Dry-run failed for {strategy}"
            assert "[DRY RUN]" in result.output, f"Missing [DRY RUN] for {strategy}"


# ---------------------------------------------------------------------------
# Approval Flow
# ---------------------------------------------------------------------------


class TestApprovalFlow:
    """Tests for the requires_approval gate."""

    @pytest.mark.asyncio
    async def test_requires_approval_skipped(self):
        """Actions requiring approval are skipped in non-dry-run mode."""
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.BLOCK_PR,
            requires_approval=True,
            dry_run=False,
        )
        results = await engine.execute([action])
        assert len(results) == 1
        assert results[0].success is False
        assert "Requires human approval" in results[0].output

    @pytest.mark.asyncio
    async def test_approval_not_required_executes(self):
        """Actions with requires_approval=False execute normally."""
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.ALERT_ONLY,
            description="Alert test",
            requires_approval=False,
            dry_run=False,
        )
        results = await engine.execute([action])
        assert results[0].success is True


# ---------------------------------------------------------------------------
# Error Handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for exception handling during execution."""

    @pytest.mark.asyncio
    async def test_unknown_strategy_fails(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.PAUSE_AND_DLQ,  # No handler implemented
            requires_approval=False,
            dry_run=False,
        )
        # _execute_action has a catch-all for strategies without a handler
        # PAUSE_AND_DLQ and AUTO_ROLLBACK fall into the else branch
        result = await engine._execute_action(action)
        assert result.success is False
        assert "Unknown strategy" in result.error

    @pytest.mark.asyncio
    async def test_exception_in_handler_caught(self):
        """Exceptions raised during handler execution are caught gracefully."""
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.BLOCK_PR,
            requires_approval=False,
            dry_run=False,
        )
        with patch.object(engine, "_execute_block_pr", side_effect=RuntimeError("boom")):
            result = await engine._execute_action(action)
        assert result.success is False
        assert "boom" in result.error

    @pytest.mark.asyncio
    async def test_auto_rollback_not_implemented(self):
        """AUTO_ROLLBACK has no handler and returns unknown strategy error."""
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.AUTO_ROLLBACK,
            requires_approval=False,
            dry_run=False,
        )
        result = await engine._execute_action(action)
        assert result.success is False


# ---------------------------------------------------------------------------
# Audit Logging
# ---------------------------------------------------------------------------


class TestAuditLogging:
    """Tests for the audit trail."""

    @pytest.mark.asyncio
    async def test_audit_log_populated_after_execute(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(_make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL))
        actions = engine.plan_remediation(report)
        await engine.execute(actions)

        log = engine.audit_log
        assert len(log) == 1
        entry = log[0]
        assert "timestamp" in entry
        assert entry["strategy"] == "block_pr"
        assert entry["dry_run"] is True
        assert entry["success"] is True

    @pytest.mark.asyncio
    async def test_audit_log_records_failure(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.PAUSE_AND_DLQ,
            requires_approval=False,
            dry_run=False,
        )
        await engine.execute([action])

        log = engine.audit_log
        assert len(log) == 1
        assert log[0]["success"] is False

    @pytest.mark.asyncio
    async def test_audit_log_not_populated_for_approval_skip(self):
        """Skipped-for-approval actions do NOT get audit entries."""
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.BLOCK_PR,
            requires_approval=True,
            dry_run=False,
        )
        await engine.execute([action])
        # The approval-skip path does not call _log_audit
        assert len(engine.audit_log) == 0

    @pytest.mark.asyncio
    async def test_audit_log_truncates_long_output(self):
        engine = AutoRemediationEngine(dry_run=False)
        action = RemediationAction(
            strategy=RemediationStrategy.ALERT_ONLY,
            description="x" * 1000,
            requires_approval=False,
            dry_run=False,
        )
        await engine.execute([action])
        entry = engine.audit_log[0]
        assert len(entry["output"]) <= 500

    @pytest.mark.asyncio
    async def test_audit_log_multiple_actions(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
            _make_drift(category=DriftCategory.EVENT, severity=DriftSeverity.HIGH),
        )
        actions = engine.plan_remediation(report)
        await engine.execute(actions)
        assert len(engine.audit_log) == 3

    def test_audit_log_returns_copy(self):
        """audit_log property returns a copy, not the internal list."""
        engine = AutoRemediationEngine(dry_run=True)
        log1 = engine.audit_log
        log1.append({"fake": True})
        assert len(engine.audit_log) == 0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


class TestSummary:
    """Tests for the summary() method."""

    def test_summary_empty(self):
        engine = AutoRemediationEngine(dry_run=True)
        s = engine.summary()
        assert s["total_actions"] == 0
        assert s["executed"] == 0
        assert s["successful"] == 0
        assert s["failed"] == 0
        assert s["dry_run"] is True
        assert s["by_strategy"] == {}

    @pytest.mark.asyncio
    async def test_summary_after_execution(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.MEDIUM),
        )
        actions = engine.plan_remediation(report)
        await engine.execute(actions)

        s = engine.summary()
        assert s["total_actions"] == 2
        assert s["executed"] == 2
        assert s["successful"] == 2
        assert s["failed"] == 0
        assert s["by_strategy"]["block_pr"] == 1
        assert s["by_strategy"]["create_issue"] == 1

    @pytest.mark.asyncio
    async def test_summary_counts_failures(self):
        engine = AutoRemediationEngine(dry_run=False)
        actions = [
            RemediationAction(
                strategy=RemediationStrategy.ALERT_ONLY,
                description="ok",
                requires_approval=False,
                dry_run=False,
            ),
            RemediationAction(
                strategy=RemediationStrategy.PAUSE_AND_DLQ,
                requires_approval=False,
                dry_run=False,
            ),
        ]
        await engine.execute(actions)
        # Need to set _actions for summary to report total_actions
        engine._actions = actions

        s = engine.summary()
        assert s["total_actions"] == 2
        assert s["successful"] == 1
        assert s["failed"] == 1


# ---------------------------------------------------------------------------
# Execute Clears Previous Results
# ---------------------------------------------------------------------------


class TestExecuteLifecycle:
    """Tests for the execute lifecycle and state management."""

    @pytest.mark.asyncio
    async def test_execute_clears_previous_results(self):
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
        )
        actions = engine.plan_remediation(report)
        results1 = await engine.execute(actions)
        assert len(results1) == 1

        # Execute again with different actions
        report2 = _make_report(
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
            _make_drift(category=DriftCategory.EVENT, severity=DriftSeverity.HIGH),
        )
        actions2 = engine.plan_remediation(report2)
        results2 = await engine.execute(actions2)
        assert len(results2) == 2

    @pytest.mark.asyncio
    async def test_execute_with_explicit_actions(self):
        """execute() accepts explicit action list, ignoring internal _actions."""
        engine = AutoRemediationEngine(dry_run=True)
        explicit = [
            RemediationAction(strategy=RemediationStrategy.ALERT_ONLY, dry_run=True),
            RemediationAction(strategy=RemediationStrategy.BLOCK_PR, dry_run=True),
        ]
        results = await engine.execute(explicit)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_execute_defaults_to_planned_actions(self):
        """execute() with no args uses the previously planned actions."""
        engine = AutoRemediationEngine(dry_run=True)
        report = _make_report(
            _make_drift(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
        )
        engine.plan_remediation(report)
        results = await engine.execute()
        assert len(results) == 1


# ---------------------------------------------------------------------------
# Default Policies
# ---------------------------------------------------------------------------


class TestDefaultPolicies:
    """Tests for the default policy list."""

    def test_all_categories_covered(self):
        """Every DriftCategory has at least one default policy."""
        covered = {p.category for p in DEFAULT_POLICIES}
        for cat in DriftCategory:
            assert cat in covered, f"No default policy for {cat}"

    def test_security_critical_is_block_pr(self):
        matches = [
            p
            for p in DEFAULT_POLICIES
            if p.category == DriftCategory.SECURITY and p.min_severity == DriftSeverity.CRITICAL
        ]
        assert len(matches) == 1
        assert matches[0].strategy == RemediationStrategy.BLOCK_PR
        assert matches[0].auto_approve is True

    def test_no_duplicate_category_severity_pairs(self):
        """No two policies have the same (category, min_severity)."""
        pairs = [(p.category, p.min_severity) for p in DEFAULT_POLICIES]
        assert len(pairs) == len(set(pairs))


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


class TestCountByStrategy:
    """Tests for _count_by_strategy helper."""

    def test_empty(self):
        assert _count_by_strategy([]) == {}

    def test_counts(self):
        actions = [
            RemediationAction(strategy=RemediationStrategy.BLOCK_PR),
            RemediationAction(strategy=RemediationStrategy.BLOCK_PR),
            RemediationAction(strategy=RemediationStrategy.ALERT_ONLY),
        ]
        counts = _count_by_strategy(actions)
        assert counts == {"block_pr": 2, "alert_only": 1}


class TestSeverityOrder:
    """Tests for SEVERITY_ORDER constant."""

    def test_critical_is_highest(self):
        assert SEVERITY_ORDER[DriftSeverity.CRITICAL] < SEVERITY_ORDER[DriftSeverity.HIGH]

    def test_info_is_lowest(self):
        assert SEVERITY_ORDER[DriftSeverity.INFO] > SEVERITY_ORDER[DriftSeverity.LOW]

    def test_all_severities_present(self):
        for sev in DriftSeverity:
            assert sev in SEVERITY_ORDER
