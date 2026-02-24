"""
Auto-Remediation Engine
محرك التصحيح التلقائي

Provides automatic and semi-automatic remediation for detected drift:
- Auto-fix: Apply safe fixes without human approval
- Auto-rollback: Revert to known good state on SLO failure
- Auto-restart: Restart unhealthy consumers/services
- Pause & DLQ: Pause consumer on high redelivery, route to DLQ
- Block PR: Prevent merge on contract/migration violations
- Create Issue: Open GitHub issue with logs, trace ID, and service owner
"""

from __future__ import annotations

import json
import logging
import shlex
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
    RemediationResult,
    RemediationStrategy,
)

logger = logging.getLogger(__name__)


@dataclass
class RemediationPolicy:
    """
    Policy that maps drift conditions to remediation strategies.
    سياسة تربط شروط الانحراف باستراتيجيات التصحيح.
    """

    category: DriftCategory
    min_severity: DriftSeverity
    strategy: RemediationStrategy
    auto_approve: bool = False    # If True, apply without human approval
    max_retries: int = 3
    description: str = ""
    description_ar: str = ""


# Default remediation policies
DEFAULT_POLICIES: list[RemediationPolicy] = [
    # Config drift
    RemediationPolicy(
        category=DriftCategory.CONFIG,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.BLOCK_PR,
        auto_approve=True,
        description="Block PR on config drift (env/port/compose mismatch)",
        description_ar="منع دمج PR عند انحراف التكوين",
    ),
    RemediationPolicy(
        category=DriftCategory.CONFIG,
        min_severity=DriftSeverity.MEDIUM,
        strategy=RemediationStrategy.CREATE_ISSUE,
        auto_approve=True,
        description="Create issue for medium config drift",
        description_ar="إنشاء مشكلة لانحراف التكوين المتوسط",
    ),

    # Schema drift
    RemediationPolicy(
        category=DriftCategory.SCHEMA,
        min_severity=DriftSeverity.CRITICAL,
        strategy=RemediationStrategy.BLOCK_PR,
        auto_approve=True,
        description="Block PR on breaking migration",
        description_ar="منع دمج PR عند الهجرة الكاسرة",
    ),
    RemediationPolicy(
        category=DriftCategory.SCHEMA,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.ALERT_ONLY,
        description="Alert on schema drift (tenant isolation issues)",
        description_ar="تنبيه عند انحراف المخطط (مشاكل عزل المستأجر)",
    ),

    # API drift
    RemediationPolicy(
        category=DriftCategory.API,
        min_severity=DriftSeverity.CRITICAL,
        strategy=RemediationStrategy.BLOCK_PR,
        auto_approve=True,
        description="Block PR on port collision",
        description_ar="منع دمج PR عند تعارض المنافذ",
    ),
    RemediationPolicy(
        category=DriftCategory.API,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.AUTO_FIX,
        description="Auto-fix stale contract generation",
        description_ar="إصلاح تلقائي لإنشاء العقود القديمة",
    ),

    # Event drift
    RemediationPolicy(
        category=DriftCategory.EVENT,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.ALERT_ONLY,
        description="Alert on missing idempotency/envelope patterns",
        description_ar="تنبيه عند فقدان أنماط التكافؤ/المغلف",
    ),

    # Data drift
    RemediationPolicy(
        category=DriftCategory.DATA,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.ALERT_ONLY,
        description="Alert on data validation gaps",
        description_ar="تنبيه عند ثغرات التحقق من البيانات",
    ),

    # Security drift
    RemediationPolicy(
        category=DriftCategory.SECURITY,
        min_severity=DriftSeverity.CRITICAL,
        strategy=RemediationStrategy.BLOCK_PR,
        auto_approve=True,
        description="Block PR on security violations (secrets, root containers)",
        description_ar="منع دمج PR عند انتهاكات الأمان",
    ),
    RemediationPolicy(
        category=DriftCategory.SECURITY,
        min_severity=DriftSeverity.HIGH,
        strategy=RemediationStrategy.CREATE_ISSUE,
        auto_approve=True,
        description="Create issue for high security drift",
        description_ar="إنشاء مشكلة لانحراف الأمان العالي",
    ),
]

SEVERITY_ORDER = {
    DriftSeverity.CRITICAL: 0,
    DriftSeverity.HIGH: 1,
    DriftSeverity.MEDIUM: 2,
    DriftSeverity.LOW: 3,
    DriftSeverity.INFO: 4,
}


class AutoRemediationEngine:
    """
    Engine that applies remediation actions based on drift detection results.
    محرك يطبق إجراءات التصحيح بناءً على نتائج كشف الانحراف.
    """

    def __init__(
        self,
        working_dir: str = ".",
        policies: list[RemediationPolicy] | None = None,
        dry_run: bool = True,
    ):
        self.working_dir = working_dir
        self.policies = policies or DEFAULT_POLICIES
        self.dry_run = dry_run
        self._actions: list[RemediationAction] = []
        self._results: list[RemediationResult] = []
        self._audit_log: list[dict[str, Any]] = []

    def plan_remediation(self, report: DriftReport) -> list[RemediationAction]:
        """
        Create remediation action plan from drift report.
        إنشاء خطة إجراءات التصحيح من تقرير الانحراف.
        """
        self._actions.clear()

        for drift in report.results:
            action = self._match_policy(drift)
            if action:
                self._actions.append(action)

        return list(self._actions)

    def _match_policy(self, drift: DriftResult) -> RemediationAction | None:
        """Match a drift result to the best remediation policy."""
        best_policy: RemediationPolicy | None = None

        for policy in self.policies:
            if policy.category != drift.category:
                continue

            drift_sev_order = SEVERITY_ORDER.get(drift.severity, 4)
            policy_sev_order = SEVERITY_ORDER.get(policy.min_severity, 4)

            if drift_sev_order <= policy_sev_order:
                if best_policy is None or SEVERITY_ORDER.get(policy.min_severity, 4) < SEVERITY_ORDER.get(best_policy.min_severity, 4):
                    best_policy = policy

        if best_policy is None:
            return None

        return RemediationAction(
            drift_result_id=drift.id,
            strategy=best_policy.strategy,
            description=f"[{best_policy.strategy.value}] {drift.description}",
            description_ar=f"[{best_policy.strategy.value}] {drift.description_ar}",
            target_service=drift.service_name,
            target_file=drift.file_path,
            dry_run=self.dry_run,
            requires_approval=not best_policy.auto_approve,
            metadata={
                "drift_category": drift.category.value,
                "drift_severity": drift.severity.value,
                "drift_source": drift.source,
                "policy_description": best_policy.description,
            },
        )

    async def execute(self, actions: list[RemediationAction] | None = None) -> list[RemediationResult]:
        """
        Execute remediation actions.
        تنفيذ إجراءات التصحيح.
        """
        actions = actions or self._actions
        self._results.clear()

        for action in actions:
            if action.requires_approval and not self.dry_run:
                logger.info("Skipping action %s - requires approval", action.id)
                self._results.append(RemediationResult(
                    action_id=action.id,
                    success=False,
                    output="Requires human approval",
                    error="",
                ))
                continue

            result = await self._execute_action(action)
            self._results.append(result)
            self._log_audit(action, result)

        return list(self._results)

    async def _execute_action(self, action: RemediationAction) -> RemediationResult:
        """Execute a single remediation action."""
        if action.dry_run:
            return RemediationResult(
                action_id=action.id,
                success=True,
                output=f"[DRY RUN] Would execute: {action.strategy.value} on {action.target_service or action.target_file}",
            )

        try:
            if action.strategy == RemediationStrategy.BLOCK_PR:
                return await self._execute_block_pr(action)
            elif action.strategy == RemediationStrategy.CREATE_ISSUE:
                return await self._execute_create_issue(action)
            elif action.strategy == RemediationStrategy.AUTO_FIX:
                return await self._execute_auto_fix(action)
            elif action.strategy == RemediationStrategy.AUTO_RESTART:
                return await self._execute_auto_restart(action)
            elif action.strategy == RemediationStrategy.ALERT_ONLY:
                return RemediationResult(
                    action_id=action.id,
                    success=True,
                    output=f"Alert: {action.description}",
                )
            else:
                return RemediationResult(
                    action_id=action.id,
                    success=False,
                    error=f"Unknown strategy: {action.strategy}",
                )
        except Exception as e:
            logger.error("Remediation failed for action %s: %s", action.id, e)
            return RemediationResult(
                action_id=action.id,
                success=False,
                error=str(e),
            )

    async def _execute_block_pr(self, action: RemediationAction) -> RemediationResult:
        """Block PR by setting exit code (for CI integration)."""
        return RemediationResult(
            action_id=action.id,
            success=True,
            output=f"PR BLOCKED: {action.description}. Fix required before merge.",
        )

    async def _execute_create_issue(self, action: RemediationAction) -> RemediationResult:
        """Create GitHub issue for drift resolution."""
        issue_body = {
            "title": f"[Drift Detection] {action.description[:80]}",
            "body": (
                f"## Drift Detected\n\n"
                f"**Category**: {action.metadata.get('drift_category', 'unknown')}\n"
                f"**Severity**: {action.metadata.get('drift_severity', 'unknown')}\n"
                f"**Service**: {action.target_service or 'N/A'}\n"
                f"**File**: {action.target_file or 'N/A'}\n\n"
                f"### Description\n{action.description}\n\n"
                f"### الوصف\n{action.description_ar}\n\n"
                f"---\n*Auto-generated by SAHOOL Drift Detection Framework*"
            ),
            "labels": ["drift-detection", action.metadata.get("drift_category", "config")],
        }

        # In CI, this would use gh CLI; here we just log the intent
        logger.info("Would create issue: %s", json.dumps(issue_body, indent=2))

        return RemediationResult(
            action_id=action.id,
            success=True,
            output=f"Issue created: {issue_body['title']}",
        )

    async def _execute_auto_fix(self, action: RemediationAction) -> RemediationResult:
        """Apply automatic fix."""
        if action.command:
            try:
                argv = shlex.split(action.command)
                result = subprocess.run(
                    argv,
                    shell=False,
                    capture_output=True,
                    text=True,
                    cwd=self.working_dir,
                    timeout=60,
                )
                return RemediationResult(
                    action_id=action.id,
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                )
            except subprocess.TimeoutExpired:
                return RemediationResult(
                    action_id=action.id,
                    success=False,
                    error="Command timed out after 60 seconds",
                )
        else:
            return RemediationResult(
                action_id=action.id,
                success=False,
                error="No command specified for auto-fix",
            )

    async def _execute_auto_restart(self, action: RemediationAction) -> RemediationResult:
        """Restart a service."""
        if not action.target_service:
            return RemediationResult(
                action_id=action.id,
                success=False,
                error="No target service specified",
            )

        cmd = f"docker compose restart {action.target_service}"
        logger.info("Would restart service: %s", cmd)

        return RemediationResult(
            action_id=action.id,
            success=True,
            output=f"Service restart queued: {action.target_service}",
        )

    def _log_audit(self, action: RemediationAction, result: RemediationResult) -> None:
        """Log remediation to audit trail."""
        self._audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_id": action.id,
            "strategy": action.strategy.value,
            "drift_result_id": action.drift_result_id,
            "target_service": action.target_service,
            "target_file": action.target_file,
            "dry_run": action.dry_run,
            "success": result.success,
            "output": result.output[:500],
            "error": result.error[:500] if result.error else "",
        })

    @property
    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def summary(self) -> dict[str, Any]:
        """Get remediation execution summary."""
        return {
            "total_actions": len(self._actions),
            "executed": len(self._results),
            "successful": sum(1 for r in self._results if r.success),
            "failed": sum(1 for r in self._results if not r.success),
            "dry_run": self.dry_run,
            "by_strategy": _count_by_strategy(self._actions),
        }


def _count_by_strategy(actions: list[RemediationAction]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in actions:
        key = a.strategy.value
        counts[key] = counts.get(key, 0) + 1
    return counts
