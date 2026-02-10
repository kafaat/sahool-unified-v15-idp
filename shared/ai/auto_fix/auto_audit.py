"""
Auto Audit Module for SAHOOL Platform
وحدة التدقيق التلقائي لمنصة سهول

Provides automated audit capabilities for code changes,
diagnostic results, and fix operations.

Features:
- Automatic audit logging for all operations
- Change tracking with diff generation
- Compliance reporting
- Bilingual audit entries

Author: SAHOOL Platform Team
Created: January 2026
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AuditAction(StrEnum):
    """Audit action types | أنواع إجراءات التدقيق"""

    DIAGNOSE = "diagnose"
    FIX_APPLY = "fix_apply"
    FIX_ROLLBACK = "fix_rollback"
    CONFIG_CHANGE = "config_change"
    FILE_MODIFIED = "file_modified"
    FILE_CREATED = "file_created"
    FILE_DELETED = "file_deleted"
    HEALTH_CHECK = "health_check"
    DEPENDENCY_UPDATE = "dependency_update"
    SECURITY_SCAN = "security_scan"


class AuditSeverity(StrEnum):
    """Audit entry severity levels | مستويات خطورة التدقيق"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditLogEntry:
    """
    Audit log entry with full context.
    إدخال سجل التدقيق مع السياق الكامل.
    """

    id: str
    timestamp: datetime
    action: AuditAction
    severity: AuditSeverity
    description: str
    description_ar: str
    user_id: str = "system"
    tenant_id: str = "sahool"
    component: str = ""
    file_path: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    diff: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "severity": self.severity.value,
            "description": self.description,
            "description_ar": self.description_ar,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "component": self.component,
            "file_path": self.file_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "diff": self.diff,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class AuditSummary:
    """Summary of audit entries | ملخص إدخالات التدقيق"""

    total_entries: int = 0
    by_action: dict[str, int] = field(default_factory=dict)
    by_severity: dict[str, int] = field(default_factory=dict)
    files_modified: int = 0
    fixes_applied: int = 0
    errors_encountered: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_entries": self.total_entries,
            "by_action": self.by_action,
            "by_severity": self.by_severity,
            "files_modified": self.files_modified,
            "fixes_applied": self.fixes_applied,
            "errors_encountered": self.errors_encountered,
            "duration_seconds": self.duration_seconds,
            "summary_ar": f"إجمالي: {self.total_entries} | تعديلات: {self.files_modified} | إصلاحات: {self.fixes_applied}",
        }


class AutoAudit:
    """
    Automated audit system for code operations.
    نظام التدقيق التلقائي لعمليات الكود.
    """

    def __init__(
        self,
        audit_dir: str | Path = ".audit",
        enabled: bool = True,
        tenant_id: str = "sahool",
        user_id: str = "system",
    ):
        self.audit_dir = Path(audit_dir)
        self.enabled = enabled
        self.tenant_id = tenant_id
        self.user_id = user_id
        self._entries: list[AuditLogEntry] = []
        self._session_id = self._generate_session_id()
        self._session_start = datetime.now()

        if self.enabled:
            self.audit_dir.mkdir(parents=True, exist_ok=True)

    def _generate_session_id(self) -> str:
        """Generate unique session ID | توليد معرف جلسة فريد"""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(timestamp.encode()).hexdigest()[:12]

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID | توليد معرف إدخال فريد"""
        timestamp = datetime.now().isoformat()
        count = len(self._entries)
        return hashlib.sha256(f"{timestamp}-{count}".encode()).hexdigest()[:16]

    def log(
        self,
        action: AuditAction,
        description: str,
        description_ar: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        component: str = "",
        file_path: str | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
        diff: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """
        Log an audit entry.
        تسجيل إدخال تدقيق.
        """
        entry = AuditLogEntry(
            id=self._generate_entry_id(),
            timestamp=datetime.now(),
            action=action,
            severity=severity,
            description=description,
            description_ar=description_ar,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            component=component,
            file_path=file_path,
            old_value=old_value,
            new_value=new_value,
            diff=diff,
            metadata=metadata or {},
        )

        self._entries.append(entry)

        if self.enabled:
            self._persist_entry(entry)

        logger.info(f"Audit: {action.value} - {description}")
        return entry

    def log_diagnose(
        self,
        paths: list[str],
        tools: list[str],
        total_issues: int,
        fixable_issues: int,
    ) -> AuditLogEntry:
        """Log diagnostic operation | تسجيل عملية التشخيص"""
        return self.log(
            action=AuditAction.DIAGNOSE,
            description=f"Diagnosed {len(paths)} paths with {len(tools)} tools: {total_issues} issues ({fixable_issues} fixable)",
            description_ar=f"تم تشخيص {len(paths)} مسار بـ {len(tools)} أداة: {total_issues} مشكلة ({fixable_issues} قابلة للإصلاح)",
            component="diagnostics",
            metadata={
                "paths": paths,
                "tools": tools,
                "total_issues": total_issues,
                "fixable_issues": fixable_issues,
            },
        )

    def log_fix(
        self,
        file_path: str,
        fix_type: str,
        old_content: str | None = None,
        new_content: str | None = None,
        success: bool = True,
    ) -> AuditLogEntry:
        """Log fix operation | تسجيل عملية الإصلاح"""
        severity = AuditSeverity.INFO if success else AuditSeverity.ERROR
        status = "successful" if success else "failed"
        status_ar = "ناجح" if success else "فاشل"

        diff = None
        if old_content and new_content:
            diff = self._generate_diff(old_content, new_content)

        return self.log(
            action=AuditAction.FIX_APPLY,
            description=f"Fix {fix_type} on {file_path}: {status}",
            description_ar=f"إصلاح {fix_type} في {file_path}: {status_ar}",
            severity=severity,
            component="fixer",
            file_path=file_path,
            old_value=old_content[:500] if old_content else None,
            new_value=new_content[:500] if new_content else None,
            diff=diff,
            metadata={"fix_type": fix_type, "success": success},
        )

    def log_health_check(
        self,
        component: str,
        status: str,
        latency_ms: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        """Log health check | تسجيل فحص الصحة"""
        severity = (
            AuditSeverity.INFO
            if status == "healthy"
            else AuditSeverity.WARNING
            if status == "degraded"
            else AuditSeverity.ERROR
        )

        return self.log(
            action=AuditAction.HEALTH_CHECK,
            description=f"Health check {component}: {status}",
            description_ar=f"فحص صحة {component}: {status}",
            severity=severity,
            component=component,
            metadata={
                "status": status,
                "latency_ms": latency_ms,
                **(details or {}),
            },
        )

    def log_security_scan(
        self,
        paths: list[str],
        vulnerabilities_found: int,
        high_severity: int = 0,
        medium_severity: int = 0,
        low_severity: int = 0,
    ) -> AuditLogEntry:
        """Log security scan | تسجيل الفحص الأمني"""
        severity = (
            AuditSeverity.CRITICAL
            if high_severity > 0
            else AuditSeverity.WARNING
            if medium_severity > 0
            else AuditSeverity.INFO
        )

        return self.log(
            action=AuditAction.SECURITY_SCAN,
            description=f"Security scan: {vulnerabilities_found} vulnerabilities (H:{high_severity} M:{medium_severity} L:{low_severity})",
            description_ar=f"فحص أمني: {vulnerabilities_found} ثغرة (عالي:{high_severity} متوسط:{medium_severity} منخفض:{low_severity})",
            severity=severity,
            component="security",
            metadata={
                "paths": paths,
                "total": vulnerabilities_found,
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity,
            },
        )

    def log_file_change(
        self,
        file_path: str,
        action: AuditAction,
        old_content: str | None = None,
        new_content: str | None = None,
    ) -> AuditLogEntry:
        """Log file change | تسجيل تغيير ملف"""
        action_desc = {
            AuditAction.FILE_MODIFIED: ("Modified", "تم تعديل"),
            AuditAction.FILE_CREATED: ("Created", "تم إنشاء"),
            AuditAction.FILE_DELETED: ("Deleted", "تم حذف"),
        }.get(action, ("Changed", "تم تغيير"))

        diff = None
        if old_content and new_content:
            diff = self._generate_diff(old_content, new_content)

        return self.log(
            action=action,
            description=f"{action_desc[0]} file: {file_path}",
            description_ar=f"{action_desc[1]} ملف: {file_path}",
            file_path=file_path,
            old_value=old_content[:500] if old_content else None,
            new_value=new_content[:500] if new_content else None,
            diff=diff,
        )

    def _generate_diff(self, old: str, new: str, max_lines: int = 50) -> str:
        """Generate unified diff | توليد فرق موحد"""
        try:
            import difflib

            old_lines = old.splitlines(keepends=True)
            new_lines = new.splitlines(keepends=True)
            diff = list(
                difflib.unified_diff(old_lines, new_lines, fromfile="before", tofile="after")
            )
            return "".join(diff[:max_lines])
        except Exception:
            return ""

    def _persist_entry(self, entry: AuditLogEntry) -> None:
        """Persist entry to disk | حفظ الإدخال على القرص"""
        try:
            log_file = self.audit_dir / f"audit_{self._session_id}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist audit entry: {e}")

    def get_entries(
        self,
        action: AuditAction | None = None,
        severity: AuditSeverity | None = None,
        component: str | None = None,
        since: datetime | None = None,
    ) -> list[AuditLogEntry]:
        """
        Get filtered audit entries.
        الحصول على إدخالات التدقيق المفلترة.
        """
        entries = self._entries

        if action:
            entries = [e for e in entries if e.action == action]
        if severity:
            entries = [e for e in entries if e.severity == severity]
        if component:
            entries = [e for e in entries if e.component == component]
        if since:
            entries = [e for e in entries if e.timestamp >= since]

        return entries

    def get_summary(self) -> AuditSummary:
        """
        Get audit summary.
        الحصول على ملخص التدقيق.
        """
        summary = AuditSummary(
            total_entries=len(self._entries),
            start_time=self._session_start,
            end_time=datetime.now(),
        )

        for entry in self._entries:
            # Count by action
            action_key = entry.action.value
            summary.by_action[action_key] = summary.by_action.get(action_key, 0) + 1

            # Count by severity
            severity_key = entry.severity.value
            summary.by_severity[severity_key] = summary.by_severity.get(severity_key, 0) + 1

            # Count file modifications
            if entry.action in (
                AuditAction.FILE_MODIFIED,
                AuditAction.FILE_CREATED,
                AuditAction.FILE_DELETED,
            ):
                summary.files_modified += 1

            # Count fixes
            if entry.action == AuditAction.FIX_APPLY:
                summary.fixes_applied += 1

            # Count errors
            if entry.severity in (AuditSeverity.ERROR, AuditSeverity.CRITICAL):
                summary.errors_encountered += 1

        return summary

    def export_report(
        self,
        output_path: str | Path,
        format: str = "json",
        include_diffs: bool = False,
    ) -> Path:
        """
        Export audit report to file.
        تصدير تقرير التدقيق إلى ملف.
        """
        output_path = Path(output_path)

        entries_data = []
        for entry in self._entries:
            data = entry.to_dict()
            if not include_diffs:
                data.pop("diff", None)
                data.pop("old_value", None)
                data.pop("new_value", None)
            entries_data.append(data)

        report = {
            "session_id": self._session_id,
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_summary().to_dict(),
            "entries": entries_data,
        }

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        elif format == "markdown":
            self._export_markdown(output_path, report)

        return output_path

    def _export_markdown(self, output_path: Path, report: dict[str, Any]) -> None:
        """Export as markdown | تصدير كـ Markdown"""
        summary = report["summary"]
        content = f"""# Audit Report | تقرير التدقيق

**Session ID**: {report["session_id"]}
**Generated**: {report["generated_at"]}

## Summary | الملخص

| Metric | Value |
|--------|-------|
| Total Entries | {summary["total_entries"]} |
| Files Modified | {summary["files_modified"]} |
| Fixes Applied | {summary["fixes_applied"]} |
| Errors | {summary["errors_encountered"]} |
| Duration | {summary.get("duration_seconds", "N/A")}s |

## By Action | حسب الإجراء

| Action | Count |
|--------|-------|
"""
        for action, count in summary.get("by_action", {}).items():
            content += f"| {action} | {count} |\n"

        content += "\n## Entries | الإدخالات\n\n"

        for entry in report["entries"]:
            severity_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌",
                "critical": "🚨",
            }.get(entry["severity"], "")

            content += f"""### {severity_icon} {entry["action"]}

- **Time**: {entry["timestamp"]}
- **Description**: {entry["description"]}
- **Description (AR)**: {entry["description_ar"]}
- **Component**: {entry.get("component", "N/A")}

---

"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def clear(self) -> None:
        """Clear all entries | مسح جميع الإدخالات"""
        self._entries.clear()
        self._session_start = datetime.now()
        self._session_id = self._generate_session_id()


# Convenience functions
def create_audit(
    enabled: bool = True,
    audit_dir: str = ".audit",
    tenant_id: str = "sahool",
) -> AutoAudit:
    """Create an audit instance | إنشاء نسخة تدقيق"""
    return AutoAudit(
        audit_dir=audit_dir,
        enabled=enabled,
        tenant_id=tenant_id,
    )


async def audit_operation(
    audit: AutoAudit,
    action: AuditAction,
    description: str,
    description_ar: str,
    operation,  # Callable
    **kwargs,
) -> tuple[Any, AuditLogEntry]:
    """
    Execute an operation with automatic audit logging.
    تنفيذ عملية مع تسجيل تدقيق تلقائي.
    """
    start_time = datetime.now()

    try:
        if asyncio.iscoroutinefunction(operation):
            result = await operation()
        else:
            result = operation()

        entry = audit.log(
            action=action,
            description=description,
            description_ar=description_ar,
            severity=AuditSeverity.INFO,
            metadata={
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "success": True,
                **kwargs,
            },
        )
        return result, entry

    except Exception as e:
        entry = audit.log(
            action=action,
            description=f"{description} - FAILED: {e}",
            description_ar=f"{description_ar} - فشل: {e}",
            severity=AuditSeverity.ERROR,
            metadata={
                "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "success": False,
                "error": str(e),
                **kwargs,
            },
        )
        raise
