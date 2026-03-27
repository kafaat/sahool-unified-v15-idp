"""
FixOps Scheduler and Periodic Checks
=====================================
جدولة FixOps والفحوصات الدورية

Provides scheduled and periodic analysis capabilities:
- Pre-commit checks (مصاحبة)
- Post-fix verification (لاحقة)
- Periodic scans (دورية)
- Log analysis

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class CheckType(StrEnum):
    """Types of checks | أنواع الفحوصات"""

    PRE_COMMIT = "pre_commit"  # قبل الـ commit
    POST_COMMIT = "post_commit"  # بعد الـ commit
    POST_FIX = "post_fix"  # بعد الإصلاح
    PERIODIC = "periodic"  # دوري
    ON_DEMAND = "on_demand"  # عند الطلب
    CI_CD = "ci_cd"  # في CI/CD


class CheckFrequency(StrEnum):
    """Frequency of periodic checks | تكرار الفحوصات الدورية"""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduledCheck:
    """Scheduled check configuration | تكوين الفحص المجدول"""

    id: str
    name: str
    name_ar: str
    check_type: CheckType
    frequency: CheckFrequency | None = None
    tools: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "check_type": self.check_type.value,
            "frequency": self.frequency.value if self.frequency else None,
            "tools": self.tools,
            "paths": self.paths,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
        }


@dataclass
class CheckResult:
    """Result of a scheduled check | نتيجة الفحص المجدول"""

    check_id: str
    check_type: CheckType
    started_at: datetime
    completed_at: datetime | None = None
    success: bool = True
    total_issues: int = 0
    critical_issues: int = 0
    files_checked: int = 0
    duration_ms: float = 0.0
    summary: str = ""
    summary_ar: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "check_type": self.check_type.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "files_checked": self.files_checked,
            "duration_ms": self.duration_ms,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "details": self.details,
        }


class LogAnalyzer:
    """
    Analyzes log files for errors and patterns.
    يحلل ملفات السجلات للأخطاء والأنماط
    """

    # Common error patterns
    ERROR_PATTERNS = [
        (r"ERROR|Error|error", "error", "خطأ"),
        (r"CRITICAL|Critical|critical", "critical", "حرج"),
        (r"FATAL|Fatal|fatal", "fatal", "قاتل"),
        (r"Exception|exception", "exception", "استثناء"),
        (r"Traceback", "traceback", "تتبع الخطأ"),
        (r"failed|Failed|FAILED", "failure", "فشل"),
        (r"timeout|Timeout|TIMEOUT", "timeout", "انتهاء الوقت"),
        (r"connection refused|Connection refused", "connection", "رفض الاتصال"),
        (r"permission denied|Permission denied", "permission", "رفض الصلاحية"),
        (r"out of memory|OutOfMemory|OOM", "memory", "نفاد الذاكرة"),
    ]

    def __init__(self, log_dirs: list[Path] | None = None):
        self.log_dirs = log_dirs or [
            Path("/var/log"),
            Path.cwd() / "logs",
            Path.cwd() / ".fixops" / "logs",
        ]

    def analyze_log_file(self, log_path: Path, max_lines: int = 1000) -> dict[str, Any]:
        """Analyze a single log file | تحليل ملف سجل واحد"""
        issues = []
        line_count = 0

        try:
            with open(log_path, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    line_count = i + 1

                    for pattern, category, category_ar in self.ERROR_PATTERNS:
                        if re.search(pattern, line):
                            issues.append(
                                {
                                    "line_number": i + 1,
                                    "category": category,
                                    "category_ar": category_ar,
                                    "content": line.strip()[:200],
                                }
                            )
                            break
        except OSError as e:
            logger.warning("Failed to analyze log", path=str(log_path), error=str(e))
            return {"error": str(e)}

        return {
            "file": str(log_path),
            "lines_analyzed": line_count,
            "issues_found": len(issues),
            "issues": issues[:50],  # Limit to 50 issues
            "by_category": self._group_by_category(issues),
        }

    def analyze_all_logs(self, max_age_hours: int = 24) -> dict[str, Any]:
        """Analyze all recent log files | تحليل جميع ملفات السجلات الحديثة"""
        results = []
        cutoff = datetime.now(UTC) - timedelta(hours=max_age_hours)

        for log_dir in self.log_dirs:
            if not log_dir.exists():
                continue

            for log_file in log_dir.glob("**/*.log"):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime, UTC)
                    if mtime >= cutoff:
                        result = self.analyze_log_file(log_file)
                        if result.get("issues_found", 0) > 0:
                            results.append(result)
                except OSError:
                    continue

        return {
            "analyzed_at": datetime.now(UTC).isoformat(),
            "max_age_hours": max_age_hours,
            "files_analyzed": len(results),
            "total_issues": sum(r.get("issues_found", 0) for r in results),
            "results": results,
        }

    def _group_by_category(self, issues: list[dict]) -> dict[str, int]:
        """Group issues by category"""
        counts: dict[str, int] = {}
        for issue in issues:
            cat = issue.get("category", "unknown")
            counts[cat] = counts.get(cat, 0) + 1
        return counts


class FixOpsScheduler:
    """
    Scheduler for periodic and triggered checks.
    مجدول للفحوصات الدورية والمشغلة
    """

    # Default scheduled checks
    DEFAULT_CHECKS = [
        ScheduledCheck(
            id="daily-security",
            name="Daily Security Scan",
            name_ar="فحص الأمان اليومي",
            check_type=CheckType.PERIODIC,
            frequency=CheckFrequency.DAILY,
            tools=["bandit", "semgrep", "npm_audit", "pip_audit"],
        ),
        ScheduledCheck(
            id="weekly-full",
            name="Weekly Full Analysis",
            name_ar="التحليل الأسبوعي الشامل",
            check_type=CheckType.PERIODIC,
            frequency=CheckFrequency.WEEKLY,
            tools=["ruff", "eslint", "mypy", "pylint", "typescript"],
        ),
        ScheduledCheck(
            id="pre-commit-quick",
            name="Pre-commit Quick Check",
            name_ar="الفحص السريع قبل الـ commit",
            check_type=CheckType.PRE_COMMIT,
            tools=["ruff", "eslint"],
        ),
        ScheduledCheck(
            id="post-fix-verify",
            name="Post-fix Verification",
            name_ar="التحقق بعد الإصلاح",
            check_type=CheckType.POST_FIX,
            tools=["ruff", "mypy", "typescript"],
        ),
    ]

    def __init__(
        self,
        repo_root: Path | None = None,
        config_path: Path | None = None,
    ):
        self.repo_root = repo_root or Path.cwd()
        self.config_path = config_path or self.repo_root / ".fixops" / "scheduler.json"
        self.checks: list[ScheduledCheck] = []
        self.log_analyzer = LogAnalyzer()
        self._running = False
        self._callbacks: list[Callable[[CheckResult], None]] = []

        self._load_config()

    def _load_config(self) -> None:
        """Load scheduler configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for check_data in data.get("checks", []):
                        self.checks.append(
                            ScheduledCheck(
                                id=check_data["id"],
                                name=check_data["name"],
                                name_ar=check_data.get("name_ar", ""),
                                check_type=CheckType(check_data["check_type"]),
                                frequency=CheckFrequency(check_data["frequency"])
                                if check_data.get("frequency")
                                else None,
                                tools=check_data.get("tools", []),
                                paths=check_data.get("paths", []),
                                enabled=check_data.get("enabled", True),
                            )
                        )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load scheduler config", error=str(e))
                self.checks = self.DEFAULT_CHECKS.copy()
        else:
            self.checks = self.DEFAULT_CHECKS.copy()

    def save_config(self) -> None:
        """Save scheduler configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "checks": [c.to_dict() for c in self.checks],
                    "updated_at": datetime.now(UTC).isoformat(),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    def add_callback(self, callback: Callable[[CheckResult], None]) -> None:
        """Add callback for check results"""
        self._callbacks.append(callback)

    async def run_check(
        self,
        check: ScheduledCheck,
        paths: list[str] | None = None,
    ) -> CheckResult:
        """
        Run a scheduled check.
        تشغيل فحص مجدول
        """
        from .orchestrator import FixOpsConfig, FixOpsOrchestrator

        started_at = datetime.now(UTC)

        logger.info(
            "Running scheduled check",
            check_id=check.id,
            check_type=check.check_type.value,
        )

        try:
            # Configure orchestrator
            config = FixOpsConfig(
                repo_root=self.repo_root,
                dry_run=True,  # Don't apply fixes in scheduled checks
                enable_auto_fix=False,
            )
            orchestrator = FixOpsOrchestrator(config)

            # Run analysis
            target_paths = paths or check.paths or [str(self.repo_root)]
            summary = await orchestrator.run(paths=target_paths)

            completed_at = datetime.now(UTC)
            duration_ms = (completed_at - started_at).total_seconds() * 1000

            result = CheckResult(
                check_id=check.id,
                check_type=check.check_type,
                started_at=started_at,
                completed_at=completed_at,
                success=True,
                total_issues=summary.total_issues,
                critical_issues=summary.issues_by_severity.get("critical", 0),
                files_checked=len(summary.files_modified),
                duration_ms=duration_ms,
                summary=f"Found {summary.total_issues} issues",
                summary_ar=f"تم العثور على {summary.total_issues} مشكلة",
                details={
                    "by_severity": summary.issues_by_severity,
                    "by_category": summary.issues_by_category,
                    "recommendations": len(summary.recommendations),
                },
            )

            # Update last run time
            check.last_run = completed_at
            if check.frequency:
                check.next_run = self._calculate_next_run(check.frequency)

        except Exception as e:
            logger.error("Scheduled check failed", check_id=check.id, error=str(e))
            result = CheckResult(
                check_id=check.id,
                check_type=check.check_type,
                started_at=started_at,
                completed_at=datetime.now(UTC),
                success=False,
                summary=f"Check failed: {e}",
                summary_ar=f"فشل الفحص: {e}",
            )

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.warning("Callback failed", error=str(e))

        return result

    async def run_pre_commit_check(
        self,
        staged_files: list[str] | None = None,
    ) -> CheckResult:
        """
        Run pre-commit check.
        تشغيل فحص ما قبل الـ commit
        """
        check = next(
            (c for c in self.checks if c.check_type == CheckType.PRE_COMMIT and c.enabled),
            ScheduledCheck(
                id="pre-commit-adhoc",
                name="Pre-commit Check",
                name_ar="فحص قبل الـ commit",
                check_type=CheckType.PRE_COMMIT,
                tools=["ruff", "eslint"],
            ),
        )

        return await self.run_check(check, paths=staged_files)

    async def run_post_fix_verification(
        self,
        modified_files: list[str],
    ) -> CheckResult:
        """
        Run post-fix verification.
        تشغيل التحقق بعد الإصلاح
        """
        check = next(
            (c for c in self.checks if c.check_type == CheckType.POST_FIX and c.enabled),
            ScheduledCheck(
                id="post-fix-adhoc",
                name="Post-fix Verification",
                name_ar="التحقق بعد الإصلاح",
                check_type=CheckType.POST_FIX,
                tools=["ruff", "mypy"],
            ),
        )

        return await self.run_check(check, paths=modified_files)

    async def run_log_analysis(self, max_age_hours: int = 24) -> dict[str, Any]:
        """
        Run log file analysis.
        تشغيل تحليل ملفات السجلات
        """
        logger.info("Running log analysis", max_age_hours=max_age_hours)
        return self.log_analyzer.analyze_all_logs(max_age_hours)

    def _calculate_next_run(self, frequency: CheckFrequency) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now(UTC)

        if frequency == CheckFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == CheckFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == CheckFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == CheckFrequency.MONTHLY:
            return now + timedelta(days=30)

        return now + timedelta(days=1)

    def get_due_checks(self) -> list[ScheduledCheck]:
        """Get checks that are due to run"""
        now = datetime.now(UTC)
        due = []

        for check in self.checks:
            if not check.enabled:
                continue
            if check.check_type != CheckType.PERIODIC:
                continue
            if check.next_run is None or check.next_run <= now:
                due.append(check)

        return due

    async def run_due_checks(self) -> list[CheckResult]:
        """Run all due periodic checks"""
        due_checks = self.get_due_checks()
        results = []

        for check in due_checks:
            result = await self.run_check(check)
            results.append(result)

        # Save updated config with last/next run times
        self.save_config()

        return results

    async def start_scheduler(self, check_interval_seconds: int = 3600) -> None:
        """
        Start the periodic scheduler.
        بدء المجدول الدوري
        """
        self._running = True
        logger.info("Starting FixOps scheduler", interval=check_interval_seconds)

        while self._running:
            try:
                await self.run_due_checks()
            except Exception as e:
                logger.error("Scheduler iteration failed", error=str(e))

            await asyncio.sleep(check_interval_seconds)

    def stop_scheduler(self) -> None:
        """Stop the periodic scheduler"""
        self._running = False
        logger.info("Stopping FixOps scheduler")


# Convenience functions
async def run_pre_commit(
    repo_root: Path | None = None,
    staged_files: list[str] | None = None,
) -> CheckResult:
    """Run pre-commit check | تشغيل فحص قبل الـ commit"""
    scheduler = FixOpsScheduler(repo_root=repo_root)
    return await scheduler.run_pre_commit_check(staged_files)


async def run_post_fix(
    repo_root: Path | None = None,
    modified_files: list[str] | None = None,
) -> CheckResult:
    """Run post-fix verification | تشغيل التحقق بعد الإصلاح"""
    scheduler = FixOpsScheduler(repo_root=repo_root)
    return await scheduler.run_post_fix_verification(modified_files or [])


async def analyze_logs(
    repo_root: Path | None = None,
    max_age_hours: int = 24,
) -> dict[str, Any]:
    """Analyze log files | تحليل ملفات السجلات"""
    scheduler = FixOpsScheduler(repo_root=repo_root)
    return await scheduler.run_log_analysis(max_age_hours)
