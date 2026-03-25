"""
SAHOOL Quality Orchestrator - منسق الجودة
==========================================

Automated quality orchestration service that integrates all quality tools,
AI agents, and audit logging for comprehensive code quality management.

خدمة تنسيق الجودة الآلية التي تدمج جميع أدوات الجودة ووكلاء الذكاء
والتدقيق التلقائي لإدارة جودة الكود الشاملة.

Features:
- Automatic tool selection based on file types
- Parallel execution for performance
- Auto-audit with full traceability
- Real-time quality metrics
- Integration with AI agents
- Webhook notifications
- Quality gates enforcement

Usage:
    from shared.ai.quality_orchestrator import (
        QualityOrchestrator,
        QualityReport,
        run_quality_check,
    )

    # Quick check
    report = await run_quality_check("apps/services/user-service/")

    # Full orchestration
    orchestrator = QualityOrchestrator()
    report = await orchestrator.analyze(
        paths=["apps/services/", "shared/"],
        languages=["python", "typescript"],
        fix=True,
        audit=True,
    )

    print(f"Issues: {report.total_issues}")
    print(f"Fixed: {report.fixed_count}")
    print(f"Quality Score: {report.quality_score}%")
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore[assignment]
    YAML_AVAILABLE = False

from .tool_registry import (
    ToolRegistry,
    ToolResult,
    ToolStatus,
    get_tool_registry,
)

# =============================================================================
# Enums - التعدادات
# =============================================================================


class QualityLevel(StrEnum):
    """Quality level classification - تصنيف مستوى الجودة"""

    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 70-89%
    ACCEPTABLE = "acceptable"  # 50-69%
    POOR = "poor"  # 30-49%
    CRITICAL = "critical"  # 0-29%


class IssueSeverity(StrEnum):
    """Issue severity levels - مستويات خطورة المشاكل"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AuditAction(StrEnum):
    """Audit action types - أنواع إجراءات التدقيق"""

    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    TOOL_EXECUTED = "tool_executed"
    ISSUE_FOUND = "issue_found"
    ISSUE_FIXED = "issue_fixed"
    QUALITY_GATE_CHECK = "quality_gate_check"
    QUALITY_GATE_PASSED = "quality_gate_passed"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    NOTIFICATION_SENT = "notification_sent"
    ERROR_OCCURRED = "error_occurred"


# =============================================================================
# Data Classes - فئات البيانات
# =============================================================================


@dataclass
class QualityIssue:
    """A single quality issue - مشكلة جودة واحدة"""

    id: str
    tool: str
    file_path: str
    line: int | None
    column: int | None
    severity: IssueSeverity
    category: str
    message: str
    message_ar: str | None = None
    code: str | None = None  # Error code like "E501", "F401"
    suggestion: str | None = None
    auto_fixable: bool = False
    fixed: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary - التحويل إلى قاموس"""
        return {
            "id": self.id,
            "tool": self.tool,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "message_ar": self.message_ar,
            "code": self.code,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable,
            "fixed": self.fixed,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class AuditEntry:
    """Audit log entry - إدخال سجل التدقيق"""

    id: str
    action: AuditAction
    timestamp: datetime
    session_id: str
    user_id: str | None
    agent_id: str | None
    details: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary - التحويل إلى قاموس"""
        return {
            "id": self.id,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "details": self.details,
            "metadata": self.metadata,
        }


@dataclass
class QualityGateResult:
    """Quality gate check result - نتيجة فحص بوابة الجودة"""

    passed: bool
    gate_name: str
    threshold: Any
    actual_value: Any
    message: str
    message_ar: str


@dataclass
class QualityReport:
    """Comprehensive quality analysis report - تقرير تحليل الجودة الشامل"""

    id: str
    session_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "running"

    # Paths analyzed
    paths: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    # Tools executed
    tools_executed: list[str] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)

    # Issues
    issues: list[QualityIssue] = field(default_factory=list)
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0

    # Fixes
    fixed_count: int = 0
    fixable_count: int = 0

    # Quality metrics
    quality_score: float = 100.0
    quality_level: QualityLevel = QualityLevel.EXCELLENT

    # Quality gates
    quality_gates: list[QualityGateResult] = field(default_factory=list)
    gates_passed: bool = True

    # Audit trail
    audit_entries: list[AuditEntry] = field(default_factory=list)

    # Performance
    duration_ms: float = 0.0
    files_analyzed: int = 0

    # Errors
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary - التحويل إلى قاموس"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "paths": self.paths,
            "languages": self.languages,
            "tools_executed": self.tools_executed,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "info_issues": self.info_issues,
            "fixed_count": self.fixed_count,
            "fixable_count": self.fixable_count,
            "quality_score": self.quality_score,
            "quality_level": self.quality_level.value,
            "gates_passed": self.gates_passed,
            "duration_ms": self.duration_ms,
            "files_analyzed": self.files_analyzed,
            "errors": self.errors,
            "issues": [i.to_dict() for i in self.issues],
            "quality_gates": [
                {
                    "passed": g.passed,
                    "gate_name": g.gate_name,
                    "threshold": g.threshold,
                    "actual_value": g.actual_value,
                    "message": g.message,
                    "message_ar": g.message_ar,
                }
                for g in self.quality_gates
            ],
            "audit_entries": [a.to_dict() for a in self.audit_entries],
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string - التحويل إلى نص JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_sarif(self) -> dict[str, Any]:
        """Convert to SARIF format for GitHub integration - التحويل إلى تنسيق SARIF"""
        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "SAHOOL Quality Orchestrator",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/kafaat/sahool-unified-v15-idp",
                        }
                    },
                    "results": [
                        {
                            "ruleId": issue.code or issue.tool,
                            "level": self._sarif_level(issue.severity),
                            "message": {"text": issue.message},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": issue.file_path},
                                        "region": {
                                            "startLine": issue.line or 1,
                                            "startColumn": issue.column or 1,
                                        },
                                    }
                                }
                            ],
                        }
                        for issue in self.issues
                    ],
                }
            ],
        }

    def _sarif_level(self, severity: IssueSeverity) -> str:
        """Convert severity to SARIF level"""
        mapping = {
            IssueSeverity.CRITICAL: "error",
            IssueSeverity.HIGH: "error",
            IssueSeverity.MEDIUM: "warning",
            IssueSeverity.LOW: "note",
            IssueSeverity.INFO: "note",
        }
        return mapping.get(severity, "note")


# =============================================================================
# Auto Audit System - نظام التدقيق التلقائي
# =============================================================================


class AutoAudit:
    """
    Automatic audit logging for quality operations.
    التدقيق التلقائي لعمليات الجودة.
    """

    def __init__(
        self,
        session_id: str,
        user_id: str | None = None,
        agent_id: str | None = None,
        persist_to_file: bool = True,
        audit_dir: Path | str = ".sahool-audit",
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.persist_to_file = persist_to_file
        self.audit_dir = Path(audit_dir)
        self.entries: list[AuditEntry] = []

        if persist_to_file:
            self.audit_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        action: AuditAction,
        details: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """
        Log an audit entry.
        تسجيل إدخال تدقيق.
        """
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action=action,
            timestamp=datetime.now(UTC),
            session_id=self.session_id,
            user_id=self.user_id,
            agent_id=self.agent_id,
            details=details,
            metadata=metadata or {},
        )

        self.entries.append(entry)

        # Log to structured logger
        logger.info(
            "audit_entry",
            action=action.value,
            session_id=self.session_id,
            details=details,
        )

        # Persist to file if enabled
        if self.persist_to_file:
            self._persist_entry(entry)

        return entry

    def _persist_entry(self, entry: AuditEntry) -> None:
        """Persist entry to file - حفظ الإدخال في ملف"""
        date_str = entry.timestamp.strftime("%Y-%m-%d")
        file_path = self.audit_dir / f"audit-{date_str}.jsonl"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def get_entries(
        self,
        action: AuditAction | None = None,
        since: datetime | None = None,
    ) -> list[AuditEntry]:
        """Get filtered audit entries - الحصول على إدخالات التدقيق المفلترة"""
        entries = self.entries

        if action:
            entries = [e for e in entries if e.action == action]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        return entries

    def export(self, format: str = "json") -> str:
        """Export audit log - تصدير سجل التدقيق"""
        if format == "json":
            return json.dumps(
                [e.to_dict() for e in self.entries],
                indent=2,
                ensure_ascii=False,
            )
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "action", "timestamp", "session_id", "user_id", "agent_id", "details"])
            for entry in self.entries:
                writer.writerow(
                    [
                        entry.id,
                        entry.action.value,
                        entry.timestamp.isoformat(),
                        entry.session_id,
                        entry.user_id,
                        entry.agent_id,
                        json.dumps(entry.details),
                    ]
                )
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")


# =============================================================================
# Quality Orchestrator - منسق الجودة
# =============================================================================


class QualityOrchestrator:
    """
    Automated quality orchestration service.
    خدمة تنسيق الجودة الآلية.

    Integrates all quality tools, AI agents, and audit logging
    for comprehensive code quality management.
    """

    def __init__(
        self,
        config_path: Path | str | None = None,
        registry: ToolRegistry | None = None,
        user_id: str | None = None,
        agent_id: str | None = None,
    ):
        """
        Initialize quality orchestrator.
        تهيئة منسق الجودة.

        Args:
            config_path: Path to .sahool-quality.yaml
            registry: Tool registry instance (or create new)
            user_id: User identifier for audit
            agent_id: Agent identifier for audit
        """
        # Load configuration
        self._config_path = config_path or Path(".sahool-quality.yaml")
        self._config = self._load_config()

        # Initialize tool registry
        self._registry = registry or get_tool_registry()

        # User/agent info
        self._user_id = user_id
        self._agent_id = agent_id

        # Session tracking
        self._current_session: str | None = None
        self._audit: AutoAudit | None = None

        logger.info(
            "quality_orchestrator_initialized",
            config_path=str(self._config_path),
        )

    def _load_config(self) -> dict[str, Any]:
        """Load quality configuration - تحميل إعدادات الجودة"""
        if not YAML_AVAILABLE:
            return {}
        if Path(self._config_path).exists():
            with open(self._config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    async def analyze(
        self,
        paths: list[str] | None = None,
        languages: list[str] | None = None,
        tools: list[str] | None = None,
        fix: bool = True,
        audit: bool = True,
        check_gates: bool = True,
        parallel: bool = True,
    ) -> QualityReport:
        """
        Run comprehensive quality analysis.
        تشغيل تحليل الجودة الشامل.

        Args:
            paths: Paths to analyze (or use config defaults)
            languages: Languages to check (or auto-detect)
            tools: Specific tools to run (or use config)
            fix: Apply auto-fixes
            audit: Enable audit logging
            check_gates: Check quality gates
            parallel: Run tools in parallel

        Returns:
            QualityReport with full analysis results
        """
        import time

        start_time = time.time()

        # Create session
        session_id = str(uuid.uuid4())
        self._current_session = session_id

        # Initialize audit
        if audit:
            self._audit = AutoAudit(
                session_id=session_id,
                user_id=self._user_id,
                agent_id=self._agent_id,
            )
            self._audit.log(
                AuditAction.ANALYSIS_STARTED,
                {"paths": paths, "languages": languages, "tools": tools, "fix": fix},
            )

        # Initialize report
        report = QualityReport(
            id=str(uuid.uuid4()),
            session_id=session_id,
            started_at=datetime.now(UTC),
            paths=paths or [],
            languages=languages or [],
        )

        try:
            # Determine paths to analyze
            analysis_paths = paths or self._get_default_paths()
            report.paths = analysis_paths

            # Check tool availability
            await self._registry.check_availability()

            # Detect languages if not specified
            if not languages:
                languages = self._detect_languages(analysis_paths)
            report.languages = languages

            # Get tools to run
            tools_to_run = self._get_tools(languages, tools)
            report.tools_executed = [t.id for t in tools_to_run]

            # Run tools
            all_results: list[ToolResult] = []

            for path in analysis_paths:
                path_obj = Path(path)
                if not path_obj.exists():
                    report.errors.append(f"Path not found: {path}")
                    continue

                # Get files to analyze
                files = self._get_files(path_obj, languages)
                report.files_analyzed += len(files)

                # Run tools on each file or directory
                if path_obj.is_file():
                    results = await self._run_tools_on_target(path, tools_to_run, fix, parallel)
                    all_results.extend(results)
                else:
                    # For directories, run on the whole directory
                    results = await self._run_tools_on_target(path, tools_to_run, fix, parallel)
                    all_results.extend(results)

            report.tool_results = all_results

            # Parse issues from results
            for result in all_results:
                issues = self._parse_issues(result)
                report.issues.extend(issues)

                if self._audit:
                    self._audit.log(
                        AuditAction.TOOL_EXECUTED,
                        {
                            "tool": result.tool_id,
                            "success": result.success,
                            "issues_count": len(issues),
                            "duration_ms": result.duration_ms,
                        },
                    )

            # Count issues by severity
            for issue in report.issues:
                report.total_issues += 1
                if issue.severity == IssueSeverity.CRITICAL:
                    report.critical_issues += 1
                elif issue.severity == IssueSeverity.HIGH:
                    report.high_issues += 1
                elif issue.severity == IssueSeverity.MEDIUM:
                    report.medium_issues += 1
                elif issue.severity == IssueSeverity.LOW:
                    report.low_issues += 1
                else:
                    report.info_issues += 1

                if issue.auto_fixable:
                    report.fixable_count += 1
                if issue.fixed:
                    report.fixed_count += 1

            # Calculate quality score
            report.quality_score = self._calculate_quality_score(report)
            report.quality_level = self._get_quality_level(report.quality_score)

            # Check quality gates
            if check_gates:
                report.quality_gates = self._check_quality_gates(report)
                report.gates_passed = all(g.passed for g in report.quality_gates)

                if self._audit:
                    self._audit.log(
                        AuditAction.QUALITY_GATE_PASSED if report.gates_passed else AuditAction.QUALITY_GATE_FAILED,
                        {
                            "gates_passed": report.gates_passed,
                            "quality_score": report.quality_score,
                        },
                    )

            # Finalize report
            report.completed_at = datetime.now(UTC)
            report.duration_ms = (time.time() - start_time) * 1000
            report.status = "completed"

            if self._audit:
                report.audit_entries = self._audit.entries
                self._audit.log(
                    AuditAction.ANALYSIS_COMPLETED,
                    {
                        "total_issues": report.total_issues,
                        "fixed_count": report.fixed_count,
                        "quality_score": report.quality_score,
                        "gates_passed": report.gates_passed,
                        "duration_ms": report.duration_ms,
                    },
                )

            logger.info(
                "quality_analysis_completed",
                session_id=session_id,
                total_issues=report.total_issues,
                quality_score=report.quality_score,
                duration_ms=report.duration_ms,
            )

            return report

        except Exception as e:
            report.status = "failed"
            report.errors.append(str(e))
            report.completed_at = datetime.now(UTC)
            report.duration_ms = (time.time() - start_time) * 1000

            if self._audit:
                self._audit.log(
                    AuditAction.ERROR_OCCURRED,
                    {"error": str(e), "type": type(e).__name__},
                )

            logger.error(
                "quality_analysis_failed",
                session_id=session_id,
                error=str(e),
            )

            return report

    def _get_default_paths(self) -> list[str]:
        """Get default paths from config - الحصول على المسارات الافتراضية من الإعدادات"""
        paths = []

        for lang in ["python", "typescript", "dart"]:
            lang_config = self._config.get(lang, {})
            if lang_config.get("enabled", True):
                paths.extend(lang_config.get("paths", []))

        return paths or ["."]

    def _detect_languages(self, paths: list[str]) -> list[str]:
        """Detect languages from file extensions - اكتشاف اللغات من امتدادات الملفات"""
        languages = set()
        ext_to_lang = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".dart": "dart",
        }

        for path in paths:
            path_obj = Path(path)
            if path_obj.is_file():
                lang = ext_to_lang.get(path_obj.suffix.lower())
                if lang:
                    languages.add(lang)
            else:
                for ext, lang in ext_to_lang.items():
                    if list(path_obj.rglob(f"*{ext}")):
                        languages.add(lang)

        return list(languages)

    def _get_tools(self, languages: list[str], specific_tools: list[str] | None) -> list:
        """Get tools to run based on config and languages"""
        if specific_tools:
            return [self._registry.get_tool(t) for t in specific_tools if self._registry.get_tool(t)]

        tools = []
        for lang in languages:
            lang_config = self._config.get(lang, {})
            tool_ids = lang_config.get("tools", [])

            for tool_id in tool_ids:
                tool = self._registry.get_tool(tool_id)
                if tool and tool.status != ToolStatus.DISABLED:
                    tools.append(tool)

        return tools

    def _get_files(self, path: Path, languages: list[str]) -> list[Path]:
        """Get files to analyze based on languages"""
        ext_map = {
            "python": [".py"],
            "typescript": [".ts", ".tsx"],
            "javascript": [".js", ".jsx"],
            "dart": [".dart"],
        }

        extensions = []
        for lang in languages:
            extensions.extend(ext_map.get(lang, []))

        if path.is_file():
            return [path] if path.suffix in extensions else []

        files = []
        exclude_patterns = self._config.get("exclude", [])

        for ext in extensions:
            for file in path.rglob(f"*{ext}"):
                # Check exclusions
                skip = False
                for pattern in exclude_patterns:
                    if file.match(pattern):
                        skip = True
                        break
                if not skip:
                    files.append(file)

        return files

    async def _run_tools_on_target(
        self,
        target: str,
        tools: list,
        fix: bool,
        parallel: bool,
    ) -> list[ToolResult]:
        """Run tools on a target path"""
        if parallel:
            tasks = [self._registry.run_tool(tool.id, target, auto_fix=fix) for tool in tools]
            return list(await asyncio.gather(*tasks))
        else:
            results = []
            for tool in tools:
                result = await self._registry.run_tool(tool.id, target, auto_fix=fix)
                results.append(result)
            return results

    def _parse_issues(self, result: ToolResult) -> list[QualityIssue]:
        """Parse issues from tool result - استخراج المشاكل من نتيجة الأداة"""
        import json
        import re

        issues = []

        try:
            if result.tool_id == "ruff":
                # Ruff JSON output
                data = json.loads(result.stdout) if result.stdout else []
                for item in data:
                    issues.append(
                        QualityIssue(
                            id=str(uuid.uuid4()),
                            tool="ruff",
                            file_path=item.get("filename", ""),
                            line=item.get("location", {}).get("row"),
                            column=item.get("location", {}).get("column"),
                            severity=self._map_severity(item.get("code", "")[:1]),
                            category="lint",
                            message=item.get("message", ""),
                            code=item.get("code"),
                            auto_fixable=item.get("fix") is not None,
                            fixed=result.exit_code == 0 and item.get("fix") is not None,
                        )
                    )

            elif result.tool_id == "eslint":
                # ESLint JSON output
                data = json.loads(result.stdout) if result.stdout else []
                for file_result in data:
                    for msg in file_result.get("messages", []):
                        issues.append(
                            QualityIssue(
                                id=str(uuid.uuid4()),
                                tool="eslint",
                                file_path=file_result.get("filePath", ""),
                                line=msg.get("line"),
                                column=msg.get("column"),
                                severity=IssueSeverity.HIGH if msg.get("severity") == 2 else IssueSeverity.MEDIUM,
                                category="lint",
                                message=msg.get("message", ""),
                                code=msg.get("ruleId"),
                                auto_fixable=msg.get("fix") is not None,
                            )
                        )

            elif result.tool_id == "bandit":
                # Bandit JSON output
                data = json.loads(result.stdout) if result.stdout else {}
                for item in data.get("results", []):
                    issues.append(
                        QualityIssue(
                            id=str(uuid.uuid4()),
                            tool="bandit",
                            file_path=item.get("filename", ""),
                            line=item.get("line_number"),
                            column=None,
                            severity=self._map_bandit_severity(item.get("issue_severity", "LOW")),
                            category="security",
                            message=item.get("issue_text", ""),
                            code=item.get("test_id"),
                            auto_fixable=False,
                        )
                    )

            elif result.tool_id == "mypy":
                # Mypy text output parsing
                for line in result.stdout.split("\n"):
                    match = re.match(r"(.+):(\d+):(\d+)?: (error|warning|note): (.+)", line)
                    if match:
                        issues.append(
                            QualityIssue(
                                id=str(uuid.uuid4()),
                                tool="mypy",
                                file_path=match.group(1),
                                line=int(match.group(2)),
                                column=int(match.group(3)) if match.group(3) else None,
                                severity=IssueSeverity.HIGH if match.group(4) == "error" else IssueSeverity.MEDIUM,
                                category="type",
                                message=match.group(5),
                                auto_fixable=False,
                            )
                        )

            elif result.tool_id in ("dart_analyze", "flutter_analyze"):
                # Dart analyzer output parsing
                for line in (result.stdout + result.stderr).split("\n"):
                    match = re.match(
                        r"\s*(info|warning|error)\s+-\s+(.+)\s+at\s+(.+):(\d+):(\d+)",
                        line,
                    )
                    if match:
                        severity_map = {
                            "error": IssueSeverity.HIGH,
                            "warning": IssueSeverity.MEDIUM,
                            "info": IssueSeverity.LOW,
                        }
                        issues.append(
                            QualityIssue(
                                id=str(uuid.uuid4()),
                                tool=result.tool_id,
                                file_path=match.group(3),
                                line=int(match.group(4)),
                                column=int(match.group(5)),
                                severity=severity_map.get(match.group(1), IssueSeverity.MEDIUM),
                                category="lint",
                                message=match.group(2),
                                auto_fixable=False,
                            )
                        )

        except Exception as e:
            logger.warning(
                "issue_parsing_failed",
                tool=result.tool_id,
                error=str(e),
            )

        return issues

    def _map_severity(self, code_prefix: str) -> IssueSeverity:
        """Map tool code to severity"""
        severity_map = {
            "E": IssueSeverity.HIGH,  # Error
            "F": IssueSeverity.HIGH,  # Fatal
            "W": IssueSeverity.MEDIUM,  # Warning
            "C": IssueSeverity.LOW,  # Convention
            "R": IssueSeverity.LOW,  # Refactor
            "I": IssueSeverity.INFO,  # Info
        }
        return severity_map.get(code_prefix, IssueSeverity.MEDIUM)

    def _map_bandit_severity(self, severity: str) -> IssueSeverity:
        """Map Bandit severity to IssueSeverity"""
        mapping = {
            "HIGH": IssueSeverity.CRITICAL,
            "MEDIUM": IssueSeverity.HIGH,
            "LOW": IssueSeverity.MEDIUM,
        }
        return mapping.get(severity, IssueSeverity.MEDIUM)

    def _calculate_quality_score(self, report: QualityReport) -> float:
        """Calculate quality score (0-100) - حساب نتيجة الجودة"""
        if report.files_analyzed == 0:
            return 100.0

        # Weighted issue penalties
        penalties = (
            report.critical_issues * 20 + report.high_issues * 10 + report.medium_issues * 3 + report.low_issues * 1
        )

        # Bonus for fixes
        fix_bonus = report.fixed_count * 2

        # Calculate score
        base_score = 100.0
        score = base_score - penalties + fix_bonus

        # Clamp to 0-100
        return max(0.0, min(100.0, score))

    def _get_quality_level(self, score: float) -> QualityLevel:
        """Get quality level from score - الحصول على مستوى الجودة من النتيجة"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.ACCEPTABLE
        elif score >= 30:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    def _check_quality_gates(self, report: QualityReport) -> list[QualityGateResult]:
        """Check quality gates - فحص بوابات الجودة"""
        gates = []
        gate_config = self._config.get("ci", {}).get("quality_gates", {})

        # Critical issues gate
        max_critical = gate_config.get("max_critical_issues", 0)
        gates.append(
            QualityGateResult(
                passed=report.critical_issues <= max_critical,
                gate_name="max_critical_issues",
                threshold=max_critical,
                actual_value=report.critical_issues,
                message=f"Critical issues: {report.critical_issues} (max: {max_critical})",
                message_ar=f"المشاكل الحرجة: {report.critical_issues} (الحد الأقصى: {max_critical})",
            )
        )

        # High issues gate
        max_high = gate_config.get("max_high_issues", 5)
        gates.append(
            QualityGateResult(
                passed=report.high_issues <= max_high,
                gate_name="max_high_issues",
                threshold=max_high,
                actual_value=report.high_issues,
                message=f"High issues: {report.high_issues} (max: {max_high})",
                message_ar=f"المشاكل العالية: {report.high_issues} (الحد الأقصى: {max_high})",
            )
        )

        # Warnings gate
        max_warnings = gate_config.get("max_warnings", 50)
        total_warnings = report.medium_issues + report.low_issues
        gates.append(
            QualityGateResult(
                passed=total_warnings <= max_warnings,
                gate_name="max_warnings",
                threshold=max_warnings,
                actual_value=total_warnings,
                message=f"Warnings: {total_warnings} (max: {max_warnings})",
                message_ar=f"التحذيرات: {total_warnings} (الحد الأقصى: {max_warnings})",
            )
        )

        return gates


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


async def run_quality_check(
    path: str | list[str],
    fix: bool = True,
    audit: bool = True,
) -> QualityReport:
    """
    Quick quality check helper.
    مساعد فحص الجودة السريع.

    Args:
        path: Path(s) to analyze
        fix: Apply auto-fixes
        audit: Enable audit logging

    Returns:
        QualityReport with results
    """
    paths = [path] if isinstance(path, str) else path
    orchestrator = QualityOrchestrator()
    return await orchestrator.analyze(paths=paths, fix=fix, audit=audit)


def generate_quality_report_markdown(report: QualityReport) -> str:
    """
    Generate markdown report.
    توليد تقرير Markdown.
    """
    status_emoji = "✅" if report.gates_passed else "❌"
    level_emoji = {
        QualityLevel.EXCELLENT: "🌟",
        QualityLevel.GOOD: "✅",
        QualityLevel.ACCEPTABLE: "⚠️",
        QualityLevel.POOR: "🔶",
        QualityLevel.CRITICAL: "🔴",
    }

    md = f"""# Quality Report | تقرير الجودة

{status_emoji} **Status**: {report.status.upper()}

## Summary | الملخص

| Metric | Value |
|--------|-------|
| Quality Score | {level_emoji.get(report.quality_level, "")} {report.quality_score:.1f}% ({report.quality_level.value}) |
| Files Analyzed | {report.files_analyzed} |
| Total Issues | {report.total_issues} |
| Fixed | {report.fixed_count} |
| Duration | {report.duration_ms:.0f}ms |

## Issues by Severity | المشاكل حسب الخطورة

| Severity | Count |
|----------|-------|
| 🔴 Critical | {report.critical_issues} |
| 🟠 High | {report.high_issues} |
| 🟡 Medium | {report.medium_issues} |
| 🔵 Low | {report.low_issues} |
| ⚪ Info | {report.info_issues} |

## Quality Gates | بوابات الجودة

| Gate | Status | Value | Threshold |
|------|--------|-------|-----------|
"""

    for gate in report.quality_gates:
        status = "✅" if gate.passed else "❌"
        md += f"| {gate.gate_name} | {status} | {gate.actual_value} | {gate.threshold} |\n"

    md += f"""
## Tools Executed | الأدوات المنفذة

{", ".join(report.tools_executed)}

## Paths Analyzed | المسارات المحللة

{chr(10).join("- " + p for p in report.paths)}

---
*Report ID: {report.id}*
*Session: {report.session_id}*
*Generated: {report.completed_at.isoformat() if report.completed_at else "N/A"}*
"""

    return md


# =============================================================================
# Exports - التصديرات
# =============================================================================

__all__ = [
    # Classes
    "QualityOrchestrator",
    "QualityReport",
    "QualityIssue",
    "QualityGateResult",
    "AutoAudit",
    "AuditEntry",
    # Enums
    "QualityLevel",
    "IssueSeverity",
    "AuditAction",
    # Functions
    "run_quality_check",
    "generate_quality_report_markdown",
]
