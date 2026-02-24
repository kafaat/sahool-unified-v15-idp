"""
Drift Detection Engine (Orchestrator)
محرك كشف الانحراف (المنسق)

Main orchestrator that runs all drift detectors, generates reports,
and coordinates with auto-remediation and quality gates.

Usage:
    from shared.drift_detection import DriftDetectionEngine

    engine = DriftDetectionEngine(working_dir="/path/to/repo")

    # Run all detectors
    report = await engine.run_full_scan()

    # Run specific categories
    report = await engine.run_scan(categories=["config", "security"])

    # Get CI exit code
    exit_code = engine.get_ci_exit_code(report)

    # Plan and preview remediation
    actions = engine.plan_remediation(report)

    # Generate markdown report
    print(report.to_markdown())
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.drift_detection.detectors.config_drift import ConfigDriftDetector
from shared.drift_detection.detectors.schema_drift import SchemaDriftDetector
from shared.drift_detection.detectors.api_drift import APIDriftDetector
from shared.drift_detection.detectors.event_drift import EventDriftDetector
from shared.drift_detection.detectors.data_drift import DataDriftDetector
from shared.drift_detection.detectors.security_drift import SecurityDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
    RemediationAction,
)
from shared.drift_detection.quality_gates import QualityGatesEngine
from shared.drift_detection.remediation import AutoRemediationEngine

logger = logging.getLogger(__name__)


class DriftDetectionEngine:
    """
    Main drift detection orchestrator.
    المنسق الرئيسي لكشف الانحراف.

    Runs all drift detectors, generates reports, and coordinates remediation.
    يشغل جميع كواشف الانحراف، وينشئ التقارير، وينسق التصحيح.
    """

    def __init__(
        self,
        working_dir: str = ".",
        config: dict[str, Any] | None = None,
        environment: str = "development",
        dry_run: bool = True,
    ):
        self.working_dir = working_dir
        self.config = config or {}
        self.environment = environment
        self.dry_run = dry_run

        # Initialize detectors
        self._detectors = {
            DriftCategory.CONFIG: ConfigDriftDetector(working_dir, config),
            DriftCategory.SCHEMA: SchemaDriftDetector(working_dir, config),
            DriftCategory.API: APIDriftDetector(working_dir, config),
            DriftCategory.EVENT: EventDriftDetector(working_dir, config),
            DriftCategory.DATA: DataDriftDetector(working_dir, config),
            DriftCategory.SECURITY: SecurityDriftDetector(working_dir, config),
        }

        # Initialize engines
        self.remediation = AutoRemediationEngine(working_dir, dry_run=dry_run)
        self.quality_gates = QualityGatesEngine(working_dir)

    async def run_full_scan(self, triggered_by: str = "manual") -> DriftReport:
        """
        Run all drift detectors and generate a comprehensive report.
        تشغيل جميع كواشف الانحراف وإنشاء تقرير شامل.
        """
        return await self.run_scan(
            categories=list(DriftCategory),
            triggered_by=triggered_by,
        )

    async def run_scan(
        self,
        categories: list[DriftCategory | str] | None = None,
        triggered_by: str = "manual",
    ) -> DriftReport:
        """
        Run specific drift detectors and generate report.
        تشغيل كواشف انحراف محددة وإنشاء تقرير.
        """
        report = DriftReport(
            environment=self.environment,
            triggered_by=triggered_by,
        )

        # Resolve category strings to enums
        cats_to_run: list[DriftCategory] = []
        for cat in (categories or list(DriftCategory)):
            if isinstance(cat, str):
                try:
                    cats_to_run.append(DriftCategory(cat))
                except ValueError:
                    logger.warning(f"Unknown drift category: {cat}")
            else:
                cats_to_run.append(cat)

        report.categories_checked = cats_to_run

        # Run detectors
        for category in cats_to_run:
            detector = self._detectors.get(category)
            if not detector:
                logger.warning(f"No detector for category: {category}")
                continue

            try:
                logger.info(f"Running {category.value} drift detection...")
                results = await detector.detect()
                report.results.extend(results)
                logger.info(f"  {category.value}: {len(results)} drifts found")
            except Exception as e:
                logger.error(f"Error in {category.value} detector: {e}")
                report.results.append(DriftResult(
                    category=category,
                    severity=DriftSeverity.HIGH,
                    source="detector_error",
                    description=f"Detector failed for {category.value}: {e}",
                    description_ar=f"فشل الكاشف لـ {category.value}: {e}",
                ))

        report.completed_at = datetime.now(timezone.utc)

        # Log summary
        summary = report.summary()
        logger.info(
            f"Drift scan complete: {summary['total_drifts']} drifts "
            f"(critical={summary['critical']}, high={summary['high']})"
        )

        return report

    def plan_remediation(self, report: DriftReport) -> list[RemediationAction]:
        """
        Plan remediation actions for detected drifts.
        التخطيط لإجراءات التصحيح للانحرافات المكتشفة.
        """
        return self.remediation.plan_remediation(report)

    async def execute_remediation(
        self,
        report: DriftReport,
        actions: list[RemediationAction] | None = None,
    ) -> dict[str, Any]:
        """
        Execute remediation actions.
        تنفيذ إجراءات التصحيح.
        """
        if actions is None:
            actions = self.plan_remediation(report)

        results = await self.remediation.execute(actions)

        return {
            "actions_planned": len(actions),
            "actions_executed": len(results),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "dry_run": self.dry_run,
            "results": [r.to_dict() for r in results],
        }

    async def evaluate_quality_gate(self, report: DriftReport) -> dict[str, Any]:
        """
        Evaluate quality gate based on drift report.
        تقييم بوابة الجودة بناءً على تقرير الانحراف.
        """
        gate_result = await self.quality_gates.evaluate_pr_gate(report)
        return gate_result.summary()

    def get_ci_exit_code(
        self,
        report: DriftReport,
        baseline: dict[str, Any] | None = None,
    ) -> int:
        """
        Get CI-compatible exit code from drift report.
        الحصول على رمز خروج متوافق مع CI من تقرير الانحراف.

        When *baseline* is provided, only **regressions** (new drifts above
        the baseline counts) trigger a non-zero exit code.  This prevents
        pre-existing findings from blocking unrelated PRs.

        Returns:
            0: No new drift (or within baseline)
            1: Critical or high severity drift above baseline
            2: Medium severity drift above baseline
        """
        if baseline is not None:
            delta = compare_with_baseline(report, baseline)
            new_critical = delta.get("critical", 0)
            new_high = delta.get("high", 0)
            new_total = delta.get("total", 0)

            if new_critical > 0 or new_high > 0:
                return 1
            if new_total > 0:
                return 2
            return 0

        # No baseline — strict mode (original behaviour)
        if report.has_critical or report.high_count > 0:
            return 1
        if report.total_drifts > 0:
            return 2
        return 0

    def to_json(self, report: DriftReport) -> str:
        """Get JSON output for CI/CD integration."""
        return json.dumps({
            "summary": report.summary(),
            "results": [r.to_dict() for r in report.results],
            "remediation": self.remediation.summary(),
            "quality_gates": self.quality_gates.get_all_results(),
        }, indent=2, default=str)

    def print_report(
        self,
        report: DriftReport,
        format: str = "text",
        baseline: dict[str, Any] | None = None,
    ) -> None:
        """
        Print drift report to stdout.
        طباعة تقرير الانحراف.
        """
        if format == "json":
            print(self.to_json(report))
        elif format == "markdown":
            print(report.to_markdown())
        else:
            self._print_text_report(report, baseline=baseline)

    def _print_text_report(
        self,
        report: DriftReport,
        baseline: dict[str, Any] | None = None,
    ) -> None:
        """Print human-readable text report."""
        print("=" * 70)
        print("SAHOOL Drift Detection Report | تقرير كشف الانحراف")
        print("=" * 70)
        print(f"Environment: {report.environment}")
        print(f"Triggered by: {report.triggered_by}")
        print(f"Categories: {', '.join(c.value for c in report.categories_checked)}")
        print()

        summary = report.summary()
        if report.is_clean:
            print("STATUS: CLEAN - No drift detected")
            print()
        else:
            print(f"STATUS: DRIFT DETECTED")
            print(f"  Total:      {summary['total_drifts']}")
            print(f"  Critical:   {summary['critical']}")
            print(f"  High:       {summary['high']}")
            print(f"  Auto-fix:   {summary['auto_fixable']}")
            print()

            if baseline is not None:
                delta = compare_with_baseline(report, baseline)
                bl_total = delta["baseline_total"]
                new_total = delta["total"]
                print(f"  Baseline:   {bl_total} known drifts")
                print(f"  New drifts: {new_total}")
                print()

            for cat in DriftCategory:
                cat_results = report.by_category(cat)
                if not cat_results:
                    continue

                print(f"--- {cat.value.upper()} DRIFT ({len(cat_results)}) ---")
                for r in cat_results:
                    severity_icon = {
                        DriftSeverity.CRITICAL: "[!!!]",
                        DriftSeverity.HIGH: "[!!]",
                        DriftSeverity.MEDIUM: "[!]",
                        DriftSeverity.LOW: "[.]",
                        DriftSeverity.INFO: "[i]",
                    }.get(r.severity, "[?]")

                    fix_label = " [auto-fixable]" if r.auto_fixable else ""
                    print(f"  {severity_icon} {r.description}{fix_label}")
                    if r.remediation_hint:
                        print(f"      Fix: {r.remediation_hint}")
                print()

        print("=" * 70)
        exit_code = self.get_ci_exit_code(report, baseline=baseline)
        print(f"CI Exit Code: {exit_code}")


# ─────────────────────────────────────────────────────────────────────────────
# Baseline Comparison
# ─────────────────────────────────────────────────────────────────────────────


def create_baseline(report: DriftReport) -> dict[str, Any]:
    """
    Create a baseline snapshot from a drift report.
    إنشاء لقطة أساسية من تقرير الانحراف.

    The baseline records the current drift counts per category and severity
    so that future CI runs can compare against it and only flag regressions.
    """
    by_cat: dict[str, dict[str, int]] = {}
    for cat in DriftCategory:
        cat_results = report.by_category(cat)
        if cat_results:
            by_cat[cat.value] = {
                sev.value: sum(1 for r in cat_results if r.severity == sev)
                for sev in DriftSeverity
                if any(r.severity == sev for r in cat_results)
            }

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": report.environment,
        "total": report.total_drifts,
        "critical": report.critical_count,
        "high": report.high_count,
        "by_category": by_cat,
    }


def load_baseline(path: str) -> dict[str, Any] | None:
    """Load a baseline file, returning None if it doesn't exist."""
    p = Path(path)
    if not p.exists():
        logger.info(f"No baseline file at {path} — strict mode")
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to read baseline {path}: {e}")
        return None


def compare_with_baseline(
    report: DriftReport,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare a drift report against a known baseline.
    مقارنة تقرير الانحراف مع الحالة الأساسية المعروفة.

    Returns a dict of *deltas* — positive values indicate regressions
    (new drifts above baseline).  Zero or negative means no regression.
    """
    bl_total = baseline.get("total", 0)
    bl_critical = baseline.get("critical", 0)
    bl_high = baseline.get("high", 0)

    delta_total = max(0, report.total_drifts - bl_total)
    delta_critical = max(0, report.critical_count - bl_critical)
    delta_high = max(0, report.high_count - bl_high)

    delta_by_cat: dict[str, int] = {}
    bl_by_cat = baseline.get("by_category", {})
    for cat in DriftCategory:
        current = len(report.by_category(cat))
        previous = sum(bl_by_cat.get(cat.value, {}).values())
        diff = max(0, current - previous)
        if diff > 0:
            delta_by_cat[cat.value] = diff

    return {
        "total": delta_total,
        "critical": delta_critical,
        "high": delta_high,
        "by_category": delta_by_cat,
        "baseline_total": bl_total,
        "current_total": report.total_drifts,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def _main() -> int:
    """CLI entry point for drift detection."""
    import argparse

    parser = argparse.ArgumentParser(
        description="SAHOOL Drift Detection Framework | إطار كشف الانحراف",
    )
    parser.add_argument(
        "--dir", "-d",
        default=".",
        help="Working directory (repository root)",
    )
    parser.add_argument(
        "--categories", "-c",
        nargs="*",
        choices=[c.value for c in DriftCategory],
        help="Categories to check (default: all)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--environment", "-e",
        default="development",
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "--triggered-by",
        default="manual",
        help="Trigger source (manual, ci, scheduled)",
    )
    parser.add_argument(
        "--remediate",
        action="store_true",
        help="Plan and show remediation actions",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply auto-fixable remediations (CAUTION: modifies files)",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Path to baseline file for diff-aware CI gating",
    )
    parser.add_argument(
        "--update-baseline",
        default=None,
        metavar="PATH",
        help="Write/update baseline file from current scan results",
    )

    args = parser.parse_args()

    engine = DriftDetectionEngine(
        working_dir=args.dir,
        environment=args.environment,
        dry_run=not args.fix,
    )

    categories = [DriftCategory(c) for c in args.categories] if args.categories else None
    report = await engine.run_scan(
        categories=categories,
        triggered_by=args.triggered_by,
    )

    if args.remediate or args.fix:
        actions = engine.plan_remediation(report)
        if actions:
            results = await engine.execute_remediation(report, actions)
            if args.format == "json":
                print(json.dumps(results, indent=2, default=str))
            else:
                print(f"\nRemediation: {results['successful']}/{results['actions_executed']} successful")

    # Update baseline if requested
    if args.update_baseline:
        bl = create_baseline(report)
        Path(args.update_baseline).write_text(json.dumps(bl, indent=2) + "\n")
        logger.info(f"Baseline written to {args.update_baseline}")

    # Load baseline for diff-aware gating
    baseline = load_baseline(args.baseline) if args.baseline else None

    engine.print_report(report, format=args.format, baseline=baseline)

    return engine.get_ci_exit_code(report, baseline=baseline)


def main() -> None:
    """Sync wrapper for CLI."""
    import asyncio
    exit_code = asyncio.run(_main())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
