"""
Auto-Fix Engine
===============
محرك الإصلاح التلقائي

Main engine for automated code analysis and fixing with
audit trail integration.

Features:
    - Multi-tool diagnostics (Ruff, ESLint, Mypy, Bandit)
    - Automated fix generation and application
    - Audit logging for all operations
    - Safe rollback capabilities
    - Bilingual reports (English/Arabic)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from .diagnostics import CodeDiagnostics, DiagnosticError
from .fixers import CodeFixer
from .models import (
    AuditEntry,
    CodeFix,
    Diagnostic,
    DiagnosticReport,
    DiagnosticSeverity,
    FixPlan,
    FixResult,
    FixStrategy,
    ToolType,
)


class AutoFixEngine:
    """
    Automated code analysis and fixing engine.

    محرك التحليل والإصلاح التلقائي للكود

    Provides a unified interface for diagnosing code issues and
    automatically fixing them with full audit trail support.

    Example:
        engine = AutoFixEngine()

        # Diagnose a file
        report = await engine.diagnose("src/main.py")
        print(f"Found {len(report.diagnostics)} issues")

        # Generate and apply safe fixes
        results = await engine.auto_fix(report, strategy=FixStrategy.SAFE)
        print(f"Applied {len([r for r in results if r.success])} fixes")

        # Get audit trail
        audit = engine.get_audit_log()
    """

    def __init__(
        self,
        backup_dir: str | None = None,
        dry_run: bool = False,
        audit_callback: Callable[[AuditEntry], None] | None = None,
    ):
        """
        Initialize AutoFixEngine.

        Args:
            backup_dir: Directory for file backups
            dry_run: If True, simulate fixes without applying
            audit_callback: Callback for audit entries
        """
        self.diagnostics = CodeDiagnostics()
        self.fixer = CodeFixer(backup_dir=backup_dir, dry_run=dry_run)
        self.dry_run = dry_run
        self.audit_callback = audit_callback
        self._audit_log: list[AuditEntry] = []
        self._fix_history: dict[str, list[FixResult]] = {}

    def _log_audit(
        self,
        action: str,
        target: str,
        details: dict[str, Any],
        success: bool = True,
        error: str | None = None,
        severity: DiagnosticSeverity | None = None,
    ) -> AuditEntry:
        """Log an audit entry."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action=action,
            actor="system",  # Could be user_id in production
            target=target,
            details=details,
            severity=severity,
            success=success,
            error=error,
        )
        self._audit_log.append(entry)

        if self.audit_callback:
            self.audit_callback(entry)

        return entry

    async def diagnose(
        self,
        target: str,
        tools: list[ToolType] | None = None,
    ) -> DiagnosticReport:
        """
        Diagnose a file or directory.

        تشخيص ملف أو مجلد

        Args:
            target: File or directory path
            tools: Specific tools to use (auto-detected if None)

        Returns:
            DiagnosticReport with found issues
        """
        self._log_audit(
            action="diagnose_started",
            target=target,
            details={"tools": [t.value for t in tools] if tools else "auto"},
        )

        try:
            if os.path.isfile(target):
                report = await self.diagnostics.diagnose_file(target, tools)
            elif os.path.isdir(target):
                report = await self.diagnostics.diagnose_directory(target)
            else:
                raise DiagnosticError(f"Target not found: {target}")

            self._log_audit(
                action="diagnose_completed",
                target=target,
                details={
                    "total_issues": len(report.diagnostics),
                    "errors": report.total_errors,
                    "warnings": report.total_warnings,
                    "duration_ms": report.scan_duration_ms,
                },
            )

            return report

        except DiagnosticError as e:
            self._log_audit(
                action="diagnose_failed",
                target=target,
                details={},
                success=False,
                error=str(e),
            )
            raise

    async def generate_fix_plan(
        self,
        report: DiagnosticReport,
        strategy: FixStrategy = FixStrategy.SAFE,
        max_fixes: int = 50,
    ) -> FixPlan:
        """
        Generate a plan for fixing diagnostics.

        توليد خطة لإصلاح التشخيصات

        Args:
            report: Diagnostic report to generate fixes for
            strategy: Fix strategy to use
            max_fixes: Maximum number of fixes to generate

        Returns:
            FixPlan with proposed fixes
        """
        self._log_audit(
            action="fix_plan_started",
            target=report.target,
            details={
                "strategy": strategy.value,
                "diagnostics_count": len(report.diagnostics),
            },
        )

        fixes: list[CodeFix] = []

        # Sort diagnostics by severity (errors first)
        sorted_diagnostics = sorted(
            report.diagnostics,
            key=lambda d: (
                0 if d.severity == DiagnosticSeverity.ERROR else 1 if d.severity == DiagnosticSeverity.WARNING else 2
            ),
        )

        for diagnostic in sorted_diagnostics[:max_fixes]:
            fix = await self.fixer.generate_fix(diagnostic, strategy)
            if fix:
                fixes.append(fix)

        # Filter by strategy
        if strategy == FixStrategy.SAFE:
            fixes = [f for f in fixes if f.is_safe and not f.requires_review]
        elif strategy == FixStrategy.MINIMAL:
            fixes = [f for f in fixes if f.is_safe]

        plan = FixPlan(
            id=str(uuid.uuid4()),
            diagnostic_report_id=report.id,
            fixes=fixes,
            strategy=strategy,
            estimated_impact=f"Will fix {len(fixes)} of {len(report.diagnostics)} issues",
            estimated_impact_ar=f"سيتم إصلاح {len(fixes)} من {len(report.diagnostics)} مشكلة",
        )

        self._log_audit(
            action="fix_plan_completed",
            target=report.target,
            details={
                "plan_id": plan.id,
                "total_fixes": plan.total_fixes,
                "safe_fixes": plan.safe_fixes,
                "review_required": plan.review_required,
            },
        )

        return plan

    async def apply_fix_plan(
        self,
        plan: FixPlan,
        report: DiagnosticReport,
        stop_on_error: bool = False,
    ) -> list[FixResult]:
        """
        Apply a fix plan.

        تطبيق خطة الإصلاح

        Args:
            plan: The fix plan to apply
            report: Original diagnostic report (for file paths)
            stop_on_error: Stop on first error if True

        Returns:
            List of FixResults
        """
        self._log_audit(
            action="fix_apply_started",
            target=report.target,
            details={
                "plan_id": plan.id,
                "fixes_count": len(plan.fixes),
                "dry_run": self.dry_run,
            },
        )

        results: list[FixResult] = []

        # Build diagnostic ID to file path mapping
        diag_map: dict[str, Diagnostic] = {d.id: d for d in report.diagnostics}

        for fix in plan.fixes:
            diagnostic = diag_map.get(fix.diagnostic_id)
            if not diagnostic:
                continue

            result = await self.fixer.apply_fix_to_file(
                fix,
                diagnostic.location.file_path,
            )
            results.append(result)

            self._log_audit(
                action="fix_applied" if result.success else "fix_failed",
                target=diagnostic.location.file_path,
                details={
                    "fix_id": fix.id,
                    "rule_id": diagnostic.rule_id,
                    "success": result.success,
                    "backup_path": result.backup_path,
                },
                success=result.success,
                error=result.error_message,
                severity=diagnostic.severity,
            )

            if stop_on_error and not result.success:
                break

        # Store history for rollback
        self._fix_history[plan.id] = results

        self._log_audit(
            action="fix_apply_completed",
            target=report.target,
            details={
                "plan_id": plan.id,
                "total_applied": len([r for r in results if r.success]),
                "total_failed": len([r for r in results if not r.success]),
            },
        )

        return results

    async def auto_fix(
        self,
        report: DiagnosticReport,
        strategy: FixStrategy = FixStrategy.SAFE,
        max_fixes: int = 50,
    ) -> list[FixResult]:
        """
        Automatically fix issues in a diagnostic report.

        إصلاح المشاكل تلقائياً

        This is a convenience method that generates a plan and applies it.

        Args:
            report: Diagnostic report to fix
            strategy: Fix strategy to use
            max_fixes: Maximum number of fixes

        Returns:
            List of FixResults
        """
        plan = await self.generate_fix_plan(report, strategy, max_fixes)
        return await self.apply_fix_plan(plan, report)

    async def diagnose_and_fix(
        self,
        target: str,
        strategy: FixStrategy = FixStrategy.SAFE,
        tools: list[ToolType] | None = None,
    ) -> tuple[DiagnosticReport, list[FixResult]]:
        """
        Diagnose and fix a target in one operation.

        تشخيص وإصلاح الهدف في عملية واحدة

        Args:
            target: File or directory to process
            strategy: Fix strategy to use
            tools: Specific tools to use

        Returns:
            Tuple of (DiagnosticReport, FixResults)
        """
        report = await self.diagnose(target, tools)

        if report.has_errors or report.has_issues:
            results = await self.auto_fix(report, strategy)
        else:
            results = []

        return report, results

    async def rollback_plan(self, plan_id: str) -> list[bool]:
        """
        Rollback all fixes from a plan.

        التراجع عن جميع إصلاحات الخطة

        Args:
            plan_id: ID of the plan to rollback

        Returns:
            List of rollback success statuses
        """
        results = self._fix_history.get(plan_id, [])
        rollback_results: list[bool] = []

        for result in reversed(results):  # Rollback in reverse order
            if result.success:
                success = await self.fixer.rollback_fix(result)
                rollback_results.append(success)

                self._log_audit(
                    action="fix_rolled_back" if success else "rollback_failed",
                    target=result.file_path,
                    details={
                        "fix_id": result.fix_id,
                        "success": success,
                    },
                    success=success,
                )

        return rollback_results

    def get_audit_log(
        self,
        action_filter: str | None = None,
        since: datetime | None = None,
    ) -> list[AuditEntry]:
        """
        Get audit log entries.

        الحصول على سجل التدقيق

        Args:
            action_filter: Filter by action type
            since: Filter by timestamp

        Returns:
            List of audit entries
        """
        entries = self._audit_log

        if action_filter:
            entries = [e for e in entries if e.action == action_filter]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        return entries

    def export_audit_log(self, format: str = "json") -> str:
        """
        Export audit log to specified format.

        تصدير سجل التدقيق

        Args:
            format: Output format (json, markdown)

        Returns:
            Formatted audit log
        """
        if format == "json":
            return json.dumps(
                [e.to_dict() for e in self._audit_log],
                indent=2,
                ensure_ascii=False,
            )

        # Markdown format
        lines = [
            "# Auto-Fix Audit Log | سجل التدقيق للإصلاح التلقائي",
            "",
            f"**Total Entries | إجمالي السجلات**: {len(self._audit_log)}",
            f"**Generated | تاريخ التوليد**: {datetime.now(UTC).isoformat()}",
            "",
            "## Entries | السجلات",
            "",
            "| Timestamp | Action | Target | Success |",
            "|-----------|--------|--------|---------|",
        ]

        for entry in self._audit_log:
            success = "✅" if entry.success else "❌"
            lines.append(
                f"| {entry.timestamp.strftime('%H:%M:%S')} | {entry.action} | `{entry.target[:30]}...` | {success} |"
            )

        return "\n".join(lines)

    def generate_report(
        self,
        report: DiagnosticReport,
        results: list[FixResult],
        include_arabic: bool = True,
    ) -> str:
        """
        Generate a comprehensive report.

        توليد تقرير شامل

        Args:
            report: Diagnostic report
            results: Fix results
            include_arabic: Include Arabic translations

        Returns:
            Formatted markdown report
        """
        fixed_count = len([r for r in results if r.success])
        failed_count = len([r for r in results if not r.success])

        lines = [
            "# Auto-Fix Report | تقرير الإصلاح التلقائي",
            "",
            "## Summary | ملخص",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Target | `{report.target}` |",
            f"| Total Issues Found | {len(report.diagnostics)} |",
            f"| Errors | {report.total_errors} |",
            f"| Warnings | {report.total_warnings} |",
            f"| Fixes Applied | {fixed_count} |",
            f"| Fixes Failed | {failed_count} |",
            f"| Scan Duration | {report.scan_duration_ms:.2f}ms |",
            "",
        ]

        if include_arabic:
            lines.extend(
                [
                    "### ملخص بالعربية",
                    "",
                    f"- **الهدف**: `{report.target}`",
                    f"- **إجمالي المشاكل**: {len(report.diagnostics)}",
                    f"- **الأخطاء**: {report.total_errors}",
                    f"- **التحذيرات**: {report.total_warnings}",
                    f"- **الإصلاحات المطبقة**: {fixed_count}",
                    f"- **الإصلاحات الفاشلة**: {failed_count}",
                    "",
                ]
            )

        # Add issues section
        lines.append("## Issues | المشاكل")
        lines.append("")

        lines.extend(self.diagnostics.format_report_markdown(report, include_arabic).split("\n")[10:])

        # Add fix results
        if results:
            lines.append("## Fix Results | نتائج الإصلاح")
            lines.append("")

            for result in results:
                status = "✅ Success" if result.success else f"❌ Failed: {result.error_message}"
                lines.append(f"- `{result.file_path}`: {status}")

        return "\n".join(lines)

    async def get_available_tools(self) -> dict[str, bool]:
        """
        Check which tools are available.

        التحقق من الأدوات المتاحة

        Returns:
            Dict mapping tool names to availability
        """
        availability = {}
        for tool in ToolType:
            availability[tool.value] = await self.diagnostics.check_tool_available(tool)

        return availability


# Convenience functions for quick usage
async def quick_diagnose(target: str) -> DiagnosticReport:
    """
    Quick diagnostic scan.

    فحص تشخيصي سريع

    Args:
        target: File or directory to scan

    Returns:
        DiagnosticReport
    """
    engine = AutoFixEngine()
    return await engine.diagnose(target)


async def quick_fix(target: str, strategy: FixStrategy = FixStrategy.SAFE) -> tuple[DiagnosticReport, list[FixResult]]:
    """
    Quick diagnose and fix.

    تشخيص وإصلاح سريع

    Args:
        target: File or directory to process
        strategy: Fix strategy

    Returns:
        Tuple of (DiagnosticReport, FixResults)
    """
    engine = AutoFixEngine()
    return await engine.diagnose_and_fix(target, strategy)
