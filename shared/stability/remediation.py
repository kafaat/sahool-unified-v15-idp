"""
SAHOOL Auto-Remediation Engine
=================================
محرك الإصلاح التلقائي لمنصة سهول

Provides automated and semi-automated remediation for common platform issues.
Works in conjunction with drift detection and monitoring alerts to automatically
fix known failure patterns.

Remediation Categories:
1. Config remediation: Apply missing defaults, fix invalid values
2. Service remediation: Restart unhealthy services, scale based on load
3. Event remediation: Pause failing consumers, move to DLQ
4. Deploy remediation: Auto-rollback on SLO breach
5. Issue creation: Open GitHub issues for manual intervention

Usage:
    from shared.stability.remediation import RemediationEngine, RemediationAction

    engine = RemediationEngine(dry_run=True)

    # From drift report
    actions = engine.plan_remediation(drift_report)

    # Review actions
    for action in actions:
        print(f"{action.severity}: {action.description}")

    # Execute (if not dry_run)
    results = await engine.execute(actions)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class RemediationType(StrEnum):
    """Types of remediation actions."""

    AUTO_FIX = "auto_fix"  # Can be fixed automatically
    MANUAL_FIX = "manual_fix"  # Requires human intervention
    RESTART = "restart"  # Service restart
    ROLLBACK = "rollback"  # Deploy rollback
    SCALE = "scale"  # Scale up/down
    PAUSE = "pause"  # Pause (e.g., consumer)
    CREATE_ISSUE = "create_issue"  # Open tracking issue
    ALERT = "alert"  # Send alert notification


class RemediationStatus(StrEnum):
    """Status of a remediation action."""

    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RemediationAction:
    """A single remediation action to take."""

    action_type: RemediationType
    severity: str  # critical, high, medium, low
    resource: str  # What to act on
    description: str
    description_ar: str
    command: str | None = None  # Shell command to execute (for auto_fix)
    config_change: dict[str, Any] | None = None  # Config values to set
    status: RemediationStatus = RemediationStatus.PLANNED
    result: str = ""
    is_safe: bool = True  # Safe to auto-execute without approval


@dataclass
class RemediationPlan:
    """A plan of remediation actions."""

    actions: list[RemediationAction] = field(default_factory=list)
    dry_run: bool = True

    @property
    def auto_fixable(self) -> list[RemediationAction]:
        """Actions that can be auto-fixed safely."""
        return [a for a in self.actions if a.action_type == RemediationType.AUTO_FIX and a.is_safe]

    @property
    def manual_required(self) -> list[RemediationAction]:
        """Actions requiring manual intervention."""
        return [a for a in self.actions if a.action_type == RemediationType.MANUAL_FIX]

    def summary(self) -> dict[str, Any]:
        return {
            "total_actions": len(self.actions),
            "auto_fixable": len(self.auto_fixable),
            "manual_required": len(self.manual_required),
            "dry_run": self.dry_run,
            "by_type": self._count_by_type(),
            "actions": [
                {
                    "type": a.action_type.value,
                    "severity": a.severity,
                    "resource": a.resource,
                    "description": a.description,
                    "status": a.status.value,
                    "safe": a.is_safe,
                }
                for a in self.actions
            ],
        }

    def _count_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for a in self.actions:
            counts[a.action_type.value] = counts.get(a.action_type.value, 0) + 1
        return counts


class RemediationEngine:
    """
    Auto-remediation engine for the SAHOOL platform.
    محرك الإصلاح التلقائي لمنصة سهول.

    Analyzes drift reports and monitoring alerts to generate remediation plans.
    In dry_run mode (default), only plans actions without executing them.
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def plan_from_drift(self, drift_report: Any) -> RemediationPlan:
        """
        Generate a remediation plan from a drift report.
        إنشاء خطة إصلاح من تقرير الانحراف.

        Args:
            drift_report: DriftReport from DriftDetector

        Returns:
            RemediationPlan with planned actions
        """
        plan = RemediationPlan(dry_run=self.dry_run)

        for item in drift_report.items:
            action = self._drift_to_action(item)
            if action:
                plan.actions.append(action)

        logger.info(
            "Remediation plan created: total_actions=%d auto_fixable=%d manual=%d",
            len(plan.actions),
            len(plan.auto_fixable),
            len(plan.manual_required),
        )

        return plan

    def _drift_to_action(self, drift_item: Any) -> RemediationAction | None:
        """Convert a drift item to a remediation action."""
        drift_type = drift_item.drift_type.value
        severity = drift_item.severity.value

        # Config drift remediation
        if drift_type == "config":
            return RemediationAction(
                action_type=RemediationType.CREATE_ISSUE,
                severity=severity,
                resource=drift_item.resource,
                description=f"Fix config drift: {drift_item.message}",
                description_ar=f"إصلاح انحراف التكوين: {drift_item.message_ar}",
                is_safe=False,
            )

        # Service drift remediation
        elif drift_type == "service":
            if "deprecated" in drift_item.message.lower():
                return RemediationAction(
                    action_type=RemediationType.MANUAL_FIX,
                    severity=severity,
                    resource=drift_item.resource,
                    description=f"Archive deprecated service: {drift_item.resource}",
                    description_ar=f"أرشفة الخدمة المهملة: {drift_item.resource}",
                    command=f"mv apps/services/{drift_item.resource} archive/deprecated-services/",
                    is_safe=False,  # Archiving requires review
                )
            elif "not registered" in drift_item.message.lower():
                return RemediationAction(
                    action_type=RemediationType.CREATE_ISSUE,
                    severity=severity,
                    resource=drift_item.resource,
                    description=f"Register service in governance: {drift_item.resource}",
                    description_ar=f"تسجيل الخدمة في الحوكمة: {drift_item.resource}",
                    is_safe=False,
                )

        # Security drift remediation
        elif drift_type == "security":
            if "USER" in drift_item.message and "root" in drift_item.message:
                return RemediationAction(
                    action_type=RemediationType.AUTO_FIX,
                    severity=severity,
                    resource=drift_item.resource,
                    description=f"Add non-root USER to Dockerfile: {drift_item.resource}",
                    description_ar=f"إضافة مستخدم غير root إلى Dockerfile: {drift_item.resource}",
                    is_safe=True,
                )

        # Docker drift
        elif drift_type == "docker":
            return RemediationAction(
                action_type=RemediationType.CREATE_ISSUE,
                severity=severity,
                resource=drift_item.resource,
                description=f"Fix Docker drift: {drift_item.message}",
                description_ar=f"إصلاح انحراف Docker: {drift_item.message_ar}",
                is_safe=False,
            )

        # Event drift
        elif drift_type == "event":
            return RemediationAction(
                action_type=RemediationType.CREATE_ISSUE,
                severity=severity,
                resource=drift_item.resource,
                description=f"Update event catalog: {drift_item.message}",
                description_ar=f"تحديث كتالوج الأحداث: {drift_item.message_ar}",
                is_safe=False,
            )

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Alert-based remediation
    # ─────────────────────────────────────────────────────────────────────────

    def plan_from_alert(
        self,
        alert_name: str,
        alert_labels: dict[str, str],
        alert_annotations: dict[str, str] | None = None,
    ) -> RemediationAction | None:
        """
        Generate a remediation action from a monitoring alert.
        إنشاء إجراء إصلاح من تنبيه المراقبة.

        Maps known alert names to remediation actions.
        """
        alert_annotations = alert_annotations or {}

        # Map alert patterns to remediations
        alert_remediations: dict[str, dict[str, Any]] = {
            "ServiceDown": {
                "type": RemediationType.RESTART,
                "severity": "critical",
                "description": f"Restart down service: {alert_labels.get('service', 'unknown')}",
                "description_ar": f"إعادة تشغيل الخدمة المتوقفة: {alert_labels.get('service', 'unknown')}",
                "safe": False,
            },
            "HighErrorRate": {
                "type": RemediationType.ALERT,
                "severity": "high",
                "description": f"High error rate on {alert_labels.get('service', 'unknown')} - investigate",
                "description_ar": f"معدل خطأ مرتفع على {alert_labels.get('service', 'unknown')} - تحقق",
                "safe": False,
            },
            "QueueBacklog": {
                "type": RemediationType.SCALE,
                "severity": "high",
                "description": f"NATS consumer backlog on {alert_labels.get('stream', 'unknown')} - scale consumers",
                "description_ar": f"تراكم مستهلك NATS على {alert_labels.get('stream', 'unknown')} - توسيع المستهلكين",
                "safe": False,
            },
            "ConsumerLag": {
                "type": RemediationType.ALERT,
                "severity": "medium",
                "description": f"JetStream consumer lag on {alert_labels.get('consumer', 'unknown')}",
                "description_ar": f"تأخر مستهلك JetStream على {alert_labels.get('consumer', 'unknown')}",
                "safe": False,
            },
            "DatabaseConnectionPoolExhausted": {
                "type": RemediationType.ALERT,
                "severity": "critical",
                "description": "Database connection pool exhausted - check for leaks",
                "description_ar": "استنفاد مجمع اتصالات قاعدة البيانات - تحقق من التسريبات",
                "safe": False,
            },
            "RedisMemoryHigh": {
                "type": RemediationType.ALERT,
                "severity": "high",
                "description": "Redis memory usage high - check eviction policy",
                "description_ar": "استخدام ذاكرة Redis مرتفع - تحقق من سياسة الإخلاء",
                "safe": False,
            },
        }

        remediation_config = alert_remediations.get(alert_name)
        if not remediation_config:
            return None

        return RemediationAction(
            action_type=remediation_config["type"],
            severity=remediation_config["severity"],
            resource=alert_labels.get("service", alert_labels.get("instance", "unknown")),
            description=remediation_config["description"],
            description_ar=remediation_config["description_ar"],
            is_safe=remediation_config.get("safe", False),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # SLO-based remediation
    # ─────────────────────────────────────────────────────────────────────────

    def plan_slo_remediation(
        self,
        service_name: str,
        error_budget_remaining: float,
        burn_rate_1h: float,
    ) -> RemediationAction | None:
        """
        Generate remediation based on SLO error budget consumption.
        إنشاء إصلاح بناءً على استهلاك ميزانية خطأ SLO.

        Rules:
        - burn_rate > 14.4x for 1h: Critical - consider rollback
        - burn_rate > 6x for 1h: High - investigate immediately
        - error_budget < 10%: Warning - freeze deployments
        """
        if burn_rate_1h > 14.4:
            return RemediationAction(
                action_type=RemediationType.ROLLBACK,
                severity="critical",
                resource=service_name,
                description=f"SLO burn rate {burn_rate_1h:.1f}x on {service_name} - consider rollback",
                description_ar=f"معدل حرق SLO {burn_rate_1h:.1f}x على {service_name} - فكر في التراجع",
                is_safe=False,  # Rollback needs approval
            )
        elif burn_rate_1h > 6:
            return RemediationAction(
                action_type=RemediationType.ALERT,
                severity="high",
                resource=service_name,
                description=f"SLO burn rate {burn_rate_1h:.1f}x on {service_name} - investigate now",
                description_ar=f"معدل حرق SLO {burn_rate_1h:.1f}x على {service_name} - تحقق الآن",
                is_safe=False,
            )
        elif error_budget_remaining < 0.10:
            return RemediationAction(
                action_type=RemediationType.PAUSE,
                severity="medium",
                resource=service_name,
                description=f"Error budget at {error_budget_remaining:.0%} for {service_name} - freeze deploys",
                description_ar=f"ميزانية الخطأ عند {error_budget_remaining:.0%} لـ {service_name} - تجميد النشر",
                is_safe=False,
            )

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Execution
    # ─────────────────────────────────────────────────────────────────────────

    async def execute_plan(self, plan: RemediationPlan) -> RemediationPlan:
        """
        Execute a remediation plan.
        تنفيذ خطة الإصلاح.

        In dry_run mode, marks all actions as SKIPPED.
        Otherwise, executes safe auto_fix actions and creates issues for manual ones.
        """
        for action in plan.actions:
            if plan.dry_run:
                action.status = RemediationStatus.SKIPPED
                action.result = "Dry run - action not executed"
                continue

            if action.action_type == RemediationType.AUTO_FIX and action.is_safe:
                try:
                    action.status = RemediationStatus.EXECUTING
                    # Execute auto-fix
                    if action.command:
                        import asyncio
                        import shlex

                        # Use subprocess_exec with args list to prevent shell injection.
                        # Timeout prevents hung processes from blocking remediation.
                        args = shlex.split(action.command)
                        proc = await asyncio.create_subprocess_exec(
                            *args,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                        )
                        try:
                            stdout, stderr = await asyncio.wait_for(
                                proc.communicate(), timeout=120
                            )
                        except asyncio.TimeoutError:
                            proc.kill()
                            await proc.wait()
                            action.status = RemediationStatus.FAILED
                            action.result = "Command timed out after 120s"
                            logger.error(f"Remediation timed out for {action.resource}")
                            continue
                        if proc.returncode == 0:
                            action.status = RemediationStatus.COMPLETED
                            action.result = stdout.decode()[:500]
                        else:
                            action.status = RemediationStatus.FAILED
                            action.result = stderr.decode()[:500]
                    else:
                        action.status = RemediationStatus.COMPLETED
                        action.result = "Auto-fix applied"
                except Exception as e:
                    action.status = RemediationStatus.FAILED
                    action.result = str(e)
                    logger.error(f"Remediation failed for {action.resource}: {e}")
            else:
                # Non-auto actions: mark as planned for manual execution
                action.status = RemediationStatus.PLANNED
                action.result = "Requires manual intervention"

        return plan
