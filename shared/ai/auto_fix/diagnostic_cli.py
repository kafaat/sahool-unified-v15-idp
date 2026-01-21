"""
Unified Diagnostic CLI for SAHOOL Platform
واجهة سطر الأوامر الموحدة للتشخيص في منصة سهول

Provides a unified command-line interface for running diagnostics
across all platform components (Python, Node.js, Flutter, Infrastructure).

Features:
- Multi-platform diagnostics
- Health checks
- Auto-fix capabilities
- Audit trail
- Bilingual output

Usage:
    python -m shared.ai.auto_fix.diagnostic_cli --all
    python -m shared.ai.auto_fix.diagnostic_cli --python --fix
    python -m shared.ai.auto_fix.diagnostic_cli --health
    python -m shared.ai.auto_fix.diagnostic_cli --audit-report

Author: SAHOOL Platform Team
Created: January 2026
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .auto_audit import create_audit
from .engine import AutoFixEngine
from .frontend_diagnostics import (
    diagnose_frontend,
    diagnose_mobile,
)
from .health_check import HealthChecker, HealthStatus
from .models import FixStrategy

logger = logging.getLogger(__name__)


# Terminal colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def colorize(text: str, color: str) -> str:
    """Add color to text | إضافة لون للنص"""
    return f"{color}{text}{Colors.RESET}"


def print_header(title: str, title_ar: str = "") -> None:
    """Print section header | طباعة عنوان القسم"""
    print()
    print(colorize("=" * 70, Colors.CYAN))
    print(colorize(f"  {title}", Colors.BOLD))
    if title_ar:
        print(colorize(f"  {title_ar}", Colors.CYAN))
    print(colorize("=" * 70, Colors.CYAN))
    print()


def print_status(message: str, status: str = "info") -> None:
    """Print status message | طباعة رسالة الحالة"""
    icons = {
        "success": (Colors.GREEN, "✅"),
        "error": (Colors.RED, "❌"),
        "warning": (Colors.YELLOW, "⚠️"),
        "info": (Colors.CYAN, "ℹ️"),
        "running": (Colors.BLUE, "🔄"),
    }
    color, icon = icons.get(status, (Colors.RESET, "•"))
    print(f"  {icon} {colorize(message, color)}")


def print_result_table(results: list[dict[str, Any]]) -> None:
    """Print results as table | طباعة النتائج كجدول"""
    if not results:
        return

    # Determine column widths
    headers = list(results[0].keys())
    widths = {h: len(h) for h in headers}
    for row in results:
        for h in headers:
            widths[h] = max(widths[h], len(str(row.get(h, ""))))

    # Print header
    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    separator = "-+-".join("-" * widths[h] for h in headers)
    print(f"  {header_line}")
    print(f"  {separator}")

    # Print rows
    for row in results:
        row_line = " | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)
        print(f"  {row_line}")


class DiagnosticCLI:
    """
    Unified diagnostic command-line interface.
    واجهة سطر الأوامر الموحدة للتشخيص.
    """

    def __init__(self, working_dir: str = "."):
        self.working_dir = Path(working_dir)
        self.audit = create_audit(enabled=True, audit_dir=str(self.working_dir / ".audit"))
        self.engine = AutoFixEngine()

    async def run_python_diagnostics(self, fix: bool = False, dry_run: bool = True) -> dict[str, Any]:
        """Run Python diagnostics | تشغيل تشخيص Python"""
        print_header("Python Diagnostics", "تشخيص Python")

        paths = ["apps/", "shared/"]
        tools = ["ruff", "mypy", "bandit"]

        print_status(f"Scanning paths: {', '.join(paths)}", "running")
        print_status(f"Using tools: {', '.join(tools)}", "info")

        try:
            report = await self.engine.diagnose(paths=paths)

            print_status(f"Found {report.total_issues} issues", "info" if report.total_issues == 0 else "warning")

            if report.total_issues > 0:
                # Summary by severity
                severity_counts = {}
                for diag in report.diagnostics:
                    sev = diag.severity.value
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                for sev, count in severity_counts.items():
                    status = "error" if sev == "error" else "warning" if sev == "warning" else "info"
                    print_status(f"  {sev.upper()}: {count}", status)

                if fix and report.fixable_count > 0:
                    print_status(f"Fixing {report.fixable_count} auto-fixable issues...", "running")
                    results = await self.engine.auto_fix(
                        dry_run=dry_run,
                        strategy=FixStrategy.SAFE,
                    )
                    successful = sum(1 for r in results if r.success)
                    print_status(f"Fixed {successful}/{len(results)} issues", "success" if successful > 0 else "warning")

            self.audit.log_diagnose(
                paths=paths,
                tools=tools,
                total_issues=report.total_issues,
                fixable_issues=report.fixable_count,
            )

            return {
                "platform": "python",
                "total_issues": report.total_issues,
                "fixable_issues": report.fixable_count,
                "fixed": fix,
            }

        except Exception as e:
            print_status(f"Python diagnostics failed: {e}", "error")
            return {"platform": "python", "error": str(e)}

    async def run_frontend_diagnostics(self, fix: bool = False) -> dict[str, Any]:
        """Run frontend diagnostics | تشغيل تشخيص الواجهة"""
        print_header("Frontend Diagnostics (Web/Admin)", "تشخيص الواجهة")

        try:
            report = await diagnose_frontend(auto_fix=fix)

            total_issues = report.total_diagnostics
            print_status(f"Found {total_issues} issues", "info" if total_issues == 0 else "warning")

            self.audit.log_diagnose(
                paths=["apps/web/", "apps/admin/"],
                tools=["eslint", "typescript", "biome"],
                total_issues=total_issues,
                fixable_issues=report.fixable_count,
            )

            return {
                "platform": "frontend",
                "total_issues": total_issues,
                "fixable_issues": report.fixable_count,
            }

        except Exception as e:
            print_status(f"Frontend diagnostics failed: {e}", "error")
            return {"platform": "frontend", "error": str(e)}

    async def run_mobile_diagnostics(self, fix: bool = False) -> dict[str, Any]:
        """Run mobile diagnostics | تشغيل تشخيص الهاتف"""
        print_header("Mobile Diagnostics (Flutter)", "تشخيص تطبيق الهاتف")

        try:
            report = await diagnose_mobile(auto_fix=fix)

            total_issues = report.total_diagnostics
            print_status(f"Found {total_issues} issues", "info" if total_issues == 0 else "warning")

            self.audit.log_diagnose(
                paths=["apps/mobile/"],
                tools=["dart_analyze", "dart_format"],
                total_issues=total_issues,
                fixable_issues=report.fixable_count,
            )

            return {
                "platform": "mobile",
                "total_issues": total_issues,
                "fixable_issues": report.fixable_count,
            }

        except Exception as e:
            print_status(f"Mobile diagnostics failed: {e}", "error")
            return {"platform": "mobile", "error": str(e)}

    async def run_health_check(self) -> dict[str, Any]:
        """Run platform health check | تشغيل فحص صحة المنصة"""
        print_header("Platform Health Check", "فحص صحة المنصة")

        try:
            checker = HealthChecker(working_dir=str(self.working_dir))
            report = await checker.run_full_health_check()

            results = []
            for result in report.results:
                status_icon = {
                    HealthStatus.HEALTHY: "✅",
                    HealthStatus.DEGRADED: "⚠️",
                    HealthStatus.UNHEALTHY: "❌",
                    HealthStatus.UNKNOWN: "❓",
                }.get(result.status, "•")

                results.append({
                    "Component": result.component,
                    "Status": f"{status_icon} {result.status.value}",
                    "Latency": f"{result.latency_ms:.1f}ms" if result.latency_ms else "N/A",
                })

                # Log to audit
                self.audit.log_health_check(
                    component=result.component,
                    status=result.status.value,
                    latency_ms=result.latency_ms,
                    details=result.details,
                )

            print_result_table(results)
            print()

            overall_status = report.overall_status.value
            status_type = "success" if overall_status == "healthy" else "warning" if overall_status == "degraded" else "error"
            print_status(f"Overall Status: {overall_status.upper()}", status_type)
            print_status(f"صحي: {report.healthy_count}/{report.total_count}", "info")

            return {
                "overall_status": overall_status,
                "healthy_count": report.healthy_count,
                "unhealthy_count": report.unhealthy_count,
                "total_count": report.total_count,
            }

        except Exception as e:
            print_status(f"Health check failed: {e}", "error")
            return {"error": str(e)}

    async def run_security_scan(self) -> dict[str, Any]:
        """Run security scan | تشغيل الفحص الأمني"""
        print_header("Security Scan", "الفحص الأمني")

        paths = ["apps/", "shared/"]
        print_status(f"Scanning: {', '.join(paths)}", "running")

        try:
            # Run bandit for Python security
            report = await self.engine.diagnose(
                paths=paths,
                tools=["bandit"],
            )

            security_issues = [d for d in report.diagnostics if d.category.value == "security"]
            high = sum(1 for d in security_issues if d.severity.value == "error")
            medium = sum(1 for d in security_issues if d.severity.value == "warning")
            low = sum(1 for d in security_issues if d.severity.value == "info")

            if security_issues:
                for issue in security_issues[:10]:  # Show first 10
                    print_status(f"{issue.message} ({issue.location.file}:{issue.location.line})",
                               "error" if issue.severity.value == "error" else "warning")

            self.audit.log_security_scan(
                paths=paths,
                vulnerabilities_found=len(security_issues),
                high_severity=high,
                medium_severity=medium,
                low_severity=low,
            )

            total = len(security_issues)
            status_type = "error" if high > 0 else "warning" if medium > 0 else "success"
            print_status(f"Found {total} security issues (H:{high} M:{medium} L:{low})", status_type)

            return {
                "total": total,
                "high": high,
                "medium": medium,
                "low": low,
            }

        except Exception as e:
            print_status(f"Security scan failed: {e}", "error")
            return {"error": str(e)}

    async def run_all_diagnostics(self, fix: bool = False, dry_run: bool = True) -> dict[str, Any]:
        """Run all diagnostics | تشغيل جميع التشخيصات"""
        print_header(
            "SAHOOL Platform Diagnostic Suite",
            "مجموعة أدوات تشخيص منصة سهول"
        )

        start_time = datetime.now()
        results = {}

        # Run all diagnostics
        results["python"] = await self.run_python_diagnostics(fix=fix, dry_run=dry_run)
        results["frontend"] = await self.run_frontend_diagnostics(fix=fix)
        results["mobile"] = await self.run_mobile_diagnostics(fix=fix)
        results["health"] = await self.run_health_check()
        results["security"] = await self.run_security_scan()

        # Summary
        duration = (datetime.now() - start_time).total_seconds()

        print_header("Summary", "الملخص")

        total_issues = sum(
            r.get("total_issues", 0)
            for r in results.values()
            if isinstance(r, dict) and "total_issues" in r
        )

        print_status(f"Total issues found: {total_issues}", "info" if total_issues == 0 else "warning")
        print_status(f"Duration: {duration:.2f}s", "info")
        print_status(f"المدة: {duration:.2f} ثانية", "info")

        return results

    def generate_audit_report(self, output_path: str = "audit_report.md") -> Path:
        """Generate audit report | توليد تقرير التدقيق"""
        print_header("Generating Audit Report", "توليد تقرير التدقيق")

        summary = self.audit.get_summary()
        print_status(f"Total entries: {summary.total_entries}", "info")
        print_status(f"Files modified: {summary.files_modified}", "info")
        print_status(f"Fixes applied: {summary.fixes_applied}", "info")

        report_path = self.audit.export_report(output_path, format="markdown")
        print_status(f"Report saved to: {report_path}", "success")

        return report_path


def parse_args() -> argparse.Namespace:
    """Parse command line arguments | تحليل وسائط سطر الأوامر"""
    parser = argparse.ArgumentParser(
        description="SAHOOL Platform Diagnostic CLI | واجهة تشخيص منصة سهول",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples | أمثلة:
  %(prog)s --all                    # Run all diagnostics
  %(prog)s --python --fix           # Diagnose and fix Python issues
  %(prog)s --frontend --mobile      # Diagnose frontend and mobile
  %(prog)s --health                 # Run health checks only
  %(prog)s --security               # Run security scan
  %(prog)s --audit-report           # Generate audit report
        """,
    )

    # Diagnostic targets
    parser.add_argument("--all", action="store_true", help="Run all diagnostics | تشغيل جميع التشخيصات")
    parser.add_argument("--python", action="store_true", help="Run Python diagnostics | تشخيص Python")
    parser.add_argument("--frontend", action="store_true", help="Run frontend diagnostics | تشخيص الواجهة")
    parser.add_argument("--mobile", action="store_true", help="Run mobile diagnostics | تشخيص الهاتف")
    parser.add_argument("--health", action="store_true", help="Run health checks | فحص الصحة")
    parser.add_argument("--security", action="store_true", help="Run security scan | الفحص الأمني")

    # Options
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues | إصلاح تلقائي")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes) | تشغيل تجريبي")
    parser.add_argument("--audit-report", action="store_true", help="Generate audit report | تقرير التدقيق")
    parser.add_argument("--output", "-o", default="audit_report.md", help="Output file for report | ملف الإخراج")
    parser.add_argument("--json", action="store_true", help="Output as JSON | إخراج JSON")
    parser.add_argument("--working-dir", "-w", default=".", help="Working directory | مجلد العمل")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output | إخراج مفصل")

    return parser.parse_args()


async def main() -> int:
    """Main entry point | نقطة الدخول الرئيسية"""
    args = parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    # Initialize CLI
    cli = DiagnosticCLI(working_dir=args.working_dir)

    results = {}

    try:
        if args.all:
            results = await cli.run_all_diagnostics(fix=args.fix, dry_run=args.dry_run)
        else:
            if args.python:
                results["python"] = await cli.run_python_diagnostics(fix=args.fix, dry_run=args.dry_run)
            if args.frontend:
                results["frontend"] = await cli.run_frontend_diagnostics(fix=args.fix)
            if args.mobile:
                results["mobile"] = await cli.run_mobile_diagnostics(fix=args.fix)
            if args.health:
                results["health"] = await cli.run_health_check()
            if args.security:
                results["security"] = await cli.run_security_scan()

        if args.audit_report:
            cli.generate_audit_report(args.output)

        # Output as JSON if requested
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))

        # Return code based on results
        has_errors = any(
            r.get("error") or r.get("total_issues", 0) > 0
            for r in results.values()
            if isinstance(r, dict)
        )
        return 1 if has_errors else 0

    except KeyboardInterrupt:
        print_status("Interrupted by user", "warning")
        return 130
    except Exception as e:
        print_status(f"Fatal error: {e}", "error")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
