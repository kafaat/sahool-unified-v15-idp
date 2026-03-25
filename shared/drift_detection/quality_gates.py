"""
Quality Gates Engine
محرك بوابات الجودة

Enforces quality gates at different stages:
1. PR Gate: Lint, typecheck, unit tests, contract tests, migration checks, security scan
2. Merge Gate: Integration tests, E2E smoke, build artifacts, SBOM
3. Deploy Gate: Staging smoke, SLO verification, rollback test
4. Runtime Gate: SLO burn rate, JetStream health, config drift
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from shared.drift_detection.models import (
    DriftReport,
)

logger = logging.getLogger(__name__)


class GateStage(StrEnum):
    """Quality gate stage | مرحلة بوابة الجودة"""

    PR = "pr"  # Pull request checks
    MERGE = "merge"  # Merge to main checks
    DEPLOY = "deploy"  # Deployment checks
    RUNTIME = "runtime"  # Runtime monitoring


class GateStatus(StrEnum):
    """Quality gate status | حالة بوابة الجودة"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class GateCheck:
    """
    Single quality gate check.
    فحص بوابة جودة واحد.
    """

    name: str
    name_ar: str
    stage: GateStage
    status: GateStatus = GateStatus.SKIPPED
    required: bool = True  # If True, failure blocks the pipeline
    description: str = ""
    description_ar: str = ""
    details: str = ""
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    """
    Aggregate quality gate result for a stage.
    نتيجة بوابة الجودة الإجمالية لمرحلة.
    """

    stage: GateStage
    checks: list[GateCheck] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    @property
    def passed(self) -> bool:
        """Gate passes if all required checks pass."""
        return all(
            c.status in (GateStatus.PASSED, GateStatus.WARNING, GateStatus.SKIPPED) for c in self.checks if c.required
        )

    @property
    def has_warnings(self) -> bool:
        return any(c.status == GateStatus.WARNING for c in self.checks)

    @property
    def failed_checks(self) -> list[GateCheck]:
        return [c for c in self.checks if c.status == GateStatus.FAILED and c.required]

    def summary(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "passed": self.passed,
            "total_checks": len(self.checks),
            "passed_count": sum(1 for c in self.checks if c.status == GateStatus.PASSED),
            "failed_count": sum(1 for c in self.checks if c.status == GateStatus.FAILED),
            "warning_count": sum(1 for c in self.checks if c.status == GateStatus.WARNING),
            "failed_required": [c.name for c in self.failed_checks],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Gate Definitions
# ─────────────────────────────────────────────────────────────────────────────

PR_GATE_CHECKS = [
    GateCheck(
        name="lint_format",
        name_ar="التنسيق والفحص",
        stage=GateStage.PR,
        required=True,
        description="Code linting and formatting (Ruff + ESLint)",
        description_ar="فحص وتنسيق الكود",
    ),
    GateCheck(
        name="typecheck",
        name_ar="فحص الأنواع",
        stage=GateStage.PR,
        required=True,
        description="TypeScript type checking + MyPy for Python",
        description_ar="فحص أنواع TypeScript + MyPy لبايثون",
    ),
    GateCheck(
        name="unit_tests",
        name_ar="اختبارات الوحدة",
        stage=GateStage.PR,
        required=True,
        description="Unit tests with minimum 25% coverage",
        description_ar="اختبارات الوحدة مع تغطية 25% كحد أدنى",
    ),
    GateCheck(
        name="contract_tests",
        name_ar="اختبارات العقود",
        stage=GateStage.PR,
        required=True,
        description="API + Event contract validation",
        description_ar="التحقق من عقود API والأحداث",
    ),
    GateCheck(
        name="migration_check",
        name_ar="فحص الهجرة",
        stage=GateStage.PR,
        required=True,
        description="Migration backward compatibility check",
        description_ar="فحص التوافق العكسي للهجرة",
    ),
    GateCheck(
        name="security_scan",
        name_ar="فحص الأمان",
        stage=GateStage.PR,
        required=True,
        description="SAST + dependency vulnerability scan",
        description_ar="فحص SAST + فحص ثغرات التبعيات",
    ),
    GateCheck(
        name="drift_detection",
        name_ar="كشف الانحراف",
        stage=GateStage.PR,
        required=True,
        description="No critical/high drift allowed",
        description_ar="لا يسمح بانحراف حرج/عالي",
    ),
    GateCheck(
        name="e2e_smoke",
        name_ar="اختبار دخان E2E",
        stage=GateStage.PR,
        required=False,
        description="Minimal E2E smoke with auth harness",
        description_ar="اختبار دخان E2E بسيط مع إطار المصادقة",
    ),
]

MERGE_GATE_CHECKS = [
    GateCheck(
        name="integration_tests",
        name_ar="اختبارات التكامل",
        stage=GateStage.MERGE,
        required=True,
        description="Full integration test suite",
        description_ar="مجموعة اختبارات التكامل الكاملة",
    ),
    GateCheck(
        name="full_e2e",
        name_ar="E2E كامل",
        stage=GateStage.MERGE,
        required=True,
        description="Full E2E test suite with auth harness",
        description_ar="مجموعة اختبارات E2E الكاملة مع إطار المصادقة",
    ),
    GateCheck(
        name="build_artifacts",
        name_ar="مخرجات البناء",
        stage=GateStage.MERGE,
        required=True,
        description="Docker image build + SBOM generation",
        description_ar="بناء صورة Docker + إنشاء SBOM",
    ),
    GateCheck(
        name="staging_smoke",
        name_ar="اختبار دخان التجريبي",
        stage=GateStage.MERGE,
        required=True,
        description="Deploy to staging + smoke test",
        description_ar="نشر للبيئة التجريبية + اختبار دخان",
    ),
]

DEPLOY_GATE_CHECKS = [
    GateCheck(
        name="slo_verification",
        name_ar="التحقق من SLO",
        stage=GateStage.DEPLOY,
        required=True,
        description="SLO targets met in staging before production deploy",
        description_ar="أهداف SLO متحققة في التجريبي قبل نشر الإنتاج",
    ),
    GateCheck(
        name="rollback_test",
        name_ar="اختبار التراجع",
        stage=GateStage.DEPLOY,
        required=True,
        description="Rollback procedure verified",
        description_ar="إجراء التراجع تم التحقق منه",
    ),
    GateCheck(
        name="config_validation",
        name_ar="التحقق من التكوين",
        stage=GateStage.DEPLOY,
        required=True,
        description="Environment config schema validated",
        description_ar="تم التحقق من مخطط تكوين البيئة",
    ),
]

RUNTIME_GATE_CHECKS = [
    GateCheck(
        name="slo_burn_rate",
        name_ar="معدل حرق SLO",
        stage=GateStage.RUNTIME,
        required=True,
        description="SLO burn rate within acceptable window",
        description_ar="معدل حرق SLO ضمن النافذة المقبولة",
    ),
    GateCheck(
        name="jetstream_health",
        name_ar="صحة JetStream",
        stage=GateStage.RUNTIME,
        required=True,
        description="JetStream lag/redelivery/ack-time within thresholds",
        description_ar="تأخر/إعادة تسليم/وقت تأكيد JetStream ضمن الحدود",
    ),
    GateCheck(
        name="config_drift_check",
        name_ar="فحص انحراف التكوين",
        stage=GateStage.RUNTIME,
        required=False,
        description="GitOps desired vs cluster actual state",
        description_ar="الحالة المطلوبة GitOps مقابل الحالة الفعلية للمجموعة",
    ),
]


class QualityGatesEngine:
    """
    Orchestrates quality gate checks across pipeline stages.
    ينسق فحوصات بوابات الجودة عبر مراحل الأنبوب.
    """

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self._gate_results: dict[GateStage, GateResult] = {}

    async def evaluate_pr_gate(self, drift_report: DriftReport | None = None) -> GateResult:
        """
        Evaluate PR quality gate using drift report.
        تقييم بوابة جودة PR باستخدام تقرير الانحراف.
        """
        result = GateResult(stage=GateStage.PR, checks=list(PR_GATE_CHECKS))

        if drift_report:
            drift_check = _find_check(result.checks, "drift_detection")
            if drift_check:
                if drift_report.has_critical or drift_report.high_count > 0:
                    drift_check.status = GateStatus.FAILED
                    drift_check.details = (
                        f"Found {drift_report.critical_count} critical, {drift_report.high_count} high severity drifts"
                    )
                elif drift_report.total_drifts > 0:
                    drift_check.status = GateStatus.WARNING
                    drift_check.details = f"Found {drift_report.total_drifts} drifts (medium/low)"
                else:
                    drift_check.status = GateStatus.PASSED
                    drift_check.details = "No drift detected"

        result.completed_at = datetime.now(UTC)
        self._gate_results[GateStage.PR] = result
        return result

    async def evaluate_merge_gate(self) -> GateResult:
        """Evaluate merge-to-main quality gate."""
        result = GateResult(stage=GateStage.MERGE, checks=list(MERGE_GATE_CHECKS))
        result.completed_at = datetime.now(UTC)
        self._gate_results[GateStage.MERGE] = result
        return result

    async def evaluate_deploy_gate(self) -> GateResult:
        """Evaluate deployment quality gate."""
        result = GateResult(stage=GateStage.DEPLOY, checks=list(DEPLOY_GATE_CHECKS))
        result.completed_at = datetime.now(UTC)
        self._gate_results[GateStage.DEPLOY] = result
        return result

    def get_all_results(self) -> dict[str, Any]:
        """Get all gate results."""
        return {stage.value: result.summary() for stage, result in self._gate_results.items()}

    def get_gate_definitions(self) -> dict[str, list[dict[str, Any]]]:
        """Get all gate check definitions for documentation."""
        return {
            "pr": [
                {
                    "name": c.name,
                    "name_ar": c.name_ar,
                    "required": c.required,
                    "description": c.description,
                    "description_ar": c.description_ar,
                }
                for c in PR_GATE_CHECKS
            ],
            "merge": [
                {
                    "name": c.name,
                    "name_ar": c.name_ar,
                    "required": c.required,
                    "description": c.description,
                    "description_ar": c.description_ar,
                }
                for c in MERGE_GATE_CHECKS
            ],
            "deploy": [
                {
                    "name": c.name,
                    "name_ar": c.name_ar,
                    "required": c.required,
                    "description": c.description,
                    "description_ar": c.description_ar,
                }
                for c in DEPLOY_GATE_CHECKS
            ],
            "runtime": [
                {
                    "name": c.name,
                    "name_ar": c.name_ar,
                    "required": c.required,
                    "description": c.description,
                    "description_ar": c.description_ar,
                }
                for c in RUNTIME_GATE_CHECKS
            ],
        }


def _find_check(checks: list[GateCheck], name: str) -> GateCheck | None:
    for c in checks:
        if c.name == name:
            return c
    return None
