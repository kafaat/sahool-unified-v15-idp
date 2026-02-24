"""
Drift Detection Data Models
نماذج بيانات كشف الانحراف

Core data structures for drift detection results, reports, and remediation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class DriftCategory(StrEnum):
    """Drift category classification | تصنيف فئة الانحراف"""

    CONFIG = "config"        # GitOps / env / compose / helm drift
    SCHEMA = "schema"        # Database migration drift
    API = "api"              # API contract drift
    EVENT = "event"          # NATS event schema drift
    DATA = "data"            # ML model / sensor / NDVI data drift
    SECURITY = "security"    # Policy / secret / compliance drift


class DriftSeverity(StrEnum):
    """Drift severity level | مستوى خطورة الانحراف"""

    CRITICAL = "critical"    # Immediate action (<6h) | حرج - إجراء فوري
    HIGH = "high"            # Action within 24h | عالي - إجراء خلال 24 ساعة
    MEDIUM = "medium"        # Action within 48h | متوسط - إجراء خلال 48 ساعة
    LOW = "low"              # Informational | منخفض - للعلم
    INFO = "info"            # No action needed | معلوماتي


class RemediationStrategy(StrEnum):
    """Auto-remediation strategy | استراتيجية التصحيح التلقائي"""

    AUTO_FIX = "auto_fix"              # Automatically apply fix
    AUTO_ROLLBACK = "auto_rollback"    # Rollback to known good state
    AUTO_RESTART = "auto_restart"      # Restart affected service
    PAUSE_AND_DLQ = "pause_and_dlq"    # Pause consumer, route to DLQ
    BLOCK_PR = "block_pr"              # Block PR merge
    ALERT_ONLY = "alert_only"          # Alert human, no auto action
    CREATE_ISSUE = "create_issue"      # Create GitHub issue automatically


@dataclass
class DriftResult:
    """
    Single drift detection result.
    نتيجة كشف انحراف واحدة.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: DriftCategory = DriftCategory.CONFIG
    severity: DriftSeverity = DriftSeverity.MEDIUM
    source: str = ""                    # What was checked (file, service, schema)
    expected: str = ""                  # Expected state
    actual: str = ""                    # Actual state
    description: str = ""              # Human-readable description (EN)
    description_ar: str = ""           # Human-readable description (AR)
    file_path: str = ""                # Affected file/resource path
    service_name: str = ""             # Affected service name
    tenant_id: str = ""                # Affected tenant (if applicable)
    auto_fixable: bool = False         # Can be auto-remediated
    remediation_hint: str = ""         # Suggested fix
    remediation_hint_ar: str = ""      # Suggested fix (AR)
    metadata: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "source": self.source,
            "expected": self.expected,
            "actual": self.actual,
            "description": self.description,
            "description_ar": self.description_ar,
            "file_path": self.file_path,
            "service_name": self.service_name,
            "auto_fixable": self.auto_fixable,
            "remediation_hint": self.remediation_hint,
            "metadata": self.metadata,
            "detected_at": self.detected_at.isoformat(),
        }


@dataclass
class DriftReport:
    """
    Aggregate drift detection report.
    تقرير كشف الانحراف الشامل.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    results: list[DriftResult] = field(default_factory=list)
    categories_checked: list[DriftCategory] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    environment: str = "development"    # development | staging | production
    triggered_by: str = "manual"        # manual | ci | scheduled | webhook

    @property
    def total_drifts(self) -> int:
        return len(self.results)

    @property
    def critical_count(self) -> int:
        return sum(1 for r in self.results if r.severity == DriftSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for r in self.results if r.severity == DriftSeverity.HIGH)

    @property
    def auto_fixable_count(self) -> int:
        return sum(1 for r in self.results if r.auto_fixable)

    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0

    @property
    def is_clean(self) -> bool:
        return self.total_drifts == 0

    def by_category(self, category: DriftCategory) -> list[DriftResult]:
        return [r for r in self.results if r.category == category]

    def by_severity(self, severity: DriftSeverity) -> list[DriftResult]:
        return [r for r in self.results if r.severity == severity]

    def by_service(self, service_name: str) -> list[DriftResult]:
        return [r for r in self.results if r.service_name == service_name]

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "total_drifts": self.total_drifts,
            "critical": self.critical_count,
            "high": self.high_count,
            "auto_fixable": self.auto_fixable_count,
            "is_clean": self.is_clean,
            "categories_checked": [c.value for c in self.categories_checked],
            "by_category": {
                cat.value: len(self.by_category(cat))
                for cat in DriftCategory
                if self.by_category(cat)
            },
            "environment": self.environment,
            "triggered_by": self.triggered_by,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def to_markdown(self) -> str:
        """Generate markdown summary report."""
        lines = [
            f"# Drift Detection Report | تقرير كشف الانحراف",
            f"",
            f"**Report ID**: `{self.id}`",
            f"**Environment**: {self.environment}",
            f"**Triggered by**: {self.triggered_by}",
            f"**Started**: {self.started_at.isoformat()}",
            f"",
            f"## Summary | ملخص",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Drifts | {self.total_drifts} |",
            f"| Critical | {self.critical_count} |",
            f"| High | {self.high_count} |",
            f"| Auto-fixable | {self.auto_fixable_count} |",
            f"| Status | {'CLEAN' if self.is_clean else 'DRIFT DETECTED'} |",
            f"",
        ]

        if self.results:
            lines.append("## Details | التفاصيل")
            lines.append("")
            for cat in DriftCategory:
                cat_results = self.by_category(cat)
                if cat_results:
                    lines.append(f"### {cat.value.title()} Drift ({len(cat_results)})")
                    lines.append("")
                    lines.append("| Severity | Source | Description | Auto-fix |")
                    lines.append("|----------|--------|-------------|----------|")
                    for r in cat_results:
                        fix = "Yes" if r.auto_fixable else "No"
                        lines.append(
                            f"| {r.severity.value} | {r.source} | {r.description} | {fix} |"
                        )
                    lines.append("")

        return "\n".join(lines)


@dataclass
class RemediationAction:
    """
    A single remediation action to apply.
    إجراء تصحيح واحد للتطبيق.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    drift_result_id: str = ""
    strategy: RemediationStrategy = RemediationStrategy.ALERT_ONLY
    description: str = ""
    description_ar: str = ""
    command: str = ""                  # Shell command or API call
    target_service: str = ""
    target_file: str = ""
    dry_run: bool = True               # Default to dry-run for safety
    requires_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RemediationResult:
    """
    Result of applying a remediation action.
    نتيجة تطبيق إجراء التصحيح.
    """

    action_id: str = ""
    success: bool = False
    output: str = ""
    error: str = ""
    applied_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reverted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "applied_at": self.applied_at.isoformat(),
            "reverted": self.reverted,
        }
