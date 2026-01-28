"""
Code Diagnostics Module
=======================
وحدة تشخيص الأخطاء البرمجية

Provides integration with multiple linting and analysis tools
to detect code issues across Python, TypeScript, and Dart.

Supported Tools:
    - Ruff (Python linting/formatting)
    - ESLint (JavaScript/TypeScript)
    - Mypy (Python type checking)
    - Bandit (Python security)
    - Dart Analyze (Flutter/Dart)

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import json
import os
import time
import uuid
from pathlib import Path

from .models import (
    CodeLocation,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
    ToolType,
)


class DiagnosticError(Exception):
    """Exception raised for diagnostic errors."""

    pass


# Arabic translations for common error messages
ERROR_TRANSLATIONS: dict[str, str] = {
    "undefined name": "اسم غير معرّف",
    "unused import": "استيراد غير مستخدم",
    "unused variable": "متغير غير مستخدم",
    "missing whitespace": "مسافة بيضاء ناقصة",
    "line too long": "السطر طويل جداً",
    "expected indentation": "المسافة البادئة متوقعة",
    "invalid syntax": "بناء جملة غير صالح",
    "undefined variable": "متغير غير معرّف",
    "module not found": "الوحدة غير موجودة",
    "type mismatch": "عدم تطابق النوع",
    "security vulnerability": "ثغرة أمنية",
    "deprecated": "مهمل",
    "unreachable code": "كود لا يمكن الوصول إليه",
    "duplicate key": "مفتاح مكرر",
    "naming convention": "اصطلاح التسمية",
    "missing return": "إرجاع ناقص",
    "possible bug": "خطأ محتمل",
    "hardcoded secret": "سر مكتوب في الكود",
    "sql injection": "حقن SQL",
    "xss vulnerability": "ثغرة XSS",
}


def translate_message(message: str) -> str:
    """Translate error message to Arabic."""
    message_lower = message.lower()
    for eng, ar in ERROR_TRANSLATIONS.items():
        if eng in message_lower:
            return ar
    return "خطأ في الكود"


def get_category_from_rule(rule_id: str, tool: ToolType) -> DiagnosticCategory:
    """Determine category from rule ID and tool."""
    if tool == ToolType.RUFF:
        if rule_id.startswith("E"):
            return DiagnosticCategory.SYNTAX
        elif rule_id.startswith("F"):
            return DiagnosticCategory.LOGIC
        elif rule_id.startswith("W"):
            return DiagnosticCategory.STYLE
        elif rule_id.startswith("I"):
            return DiagnosticCategory.IMPORT
        elif rule_id.startswith("N"):
            return DiagnosticCategory.NAMING
        elif rule_id.startswith("B"):
            return DiagnosticCategory.BEST_PRACTICE
        elif rule_id.startswith("S"):
            return DiagnosticCategory.SECURITY
        elif rule_id.startswith("UP"):
            return DiagnosticCategory.DEPRECATION
        elif rule_id.startswith("SIM"):
            return DiagnosticCategory.PERFORMANCE
    elif tool == ToolType.BANDIT:
        return DiagnosticCategory.SECURITY
    elif tool == ToolType.MYPY:
        return DiagnosticCategory.TYPE
    elif tool == ToolType.ESLINT:
        if "security" in rule_id.lower():
            return DiagnosticCategory.SECURITY
        elif "no-unused" in rule_id:
            return DiagnosticCategory.LOGIC
        elif "style" in rule_id or "format" in rule_id:
            return DiagnosticCategory.STYLE

    return DiagnosticCategory.LOGIC


def get_severity_from_level(level: str) -> DiagnosticSeverity:
    """Convert tool-specific level to DiagnosticSeverity."""
    level = level.lower()
    if level in ("error", "e", "high", "critical"):
        return DiagnosticSeverity.ERROR
    elif level in ("warning", "w", "warn", "medium"):
        return DiagnosticSeverity.WARNING
    elif level in ("info", "information", "i", "low"):
        return DiagnosticSeverity.INFO
    return DiagnosticSeverity.HINT


class CodeDiagnostics:
    """
    Code diagnostics engine.

    محرك تشخيص الأخطاء البرمجية

    Integrates with multiple linting tools to provide
    comprehensive code analysis.

    Example:
        diagnostics = CodeDiagnostics()
        report = await diagnostics.diagnose_file("src/main.py")
        for diag in report.diagnostics:
            print(f"{diag.severity}: {diag.message}")
    """

    def __init__(
        self,
        ruff_path: str = "ruff",
        eslint_path: str = "eslint",
        mypy_path: str = "mypy",
        bandit_path: str = "bandit",
        dart_path: str = "dart",
        timeout: int = 60,
    ):
        """
        Initialize CodeDiagnostics.

        Args:
            ruff_path: Path to ruff executable
            eslint_path: Path to eslint executable
            mypy_path: Path to mypy executable
            bandit_path: Path to bandit executable
            dart_path: Path to dart executable
            timeout: Timeout for tool execution in seconds
        """
        self.ruff_path = ruff_path
        self.eslint_path = eslint_path
        self.mypy_path = mypy_path
        self.bandit_path = bandit_path
        self.dart_path = dart_path
        self.timeout = timeout
        self._tool_available: dict[ToolType, bool | None] = {}

    async def check_tool_available(self, tool: ToolType) -> bool:
        """Check if a tool is available."""
        if tool in self._tool_available:
            return self._tool_available[tool] or False

        cmd_map = {
            ToolType.RUFF: [self.ruff_path, "--version"],
            ToolType.ESLINT: [self.eslint_path, "--version"],
            ToolType.MYPY: [self.mypy_path, "--version"],
            ToolType.BANDIT: [self.bandit_path, "--version"],
            ToolType.DART_ANALYZE: [self.dart_path, "--version"],
        }

        cmd = cmd_map.get(tool)
        if not cmd:
            self._tool_available[tool] = False
            return False

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=5)
            self._tool_available[tool] = proc.returncode == 0
        except (TimeoutError, FileNotFoundError, OSError):
            self._tool_available[tool] = False

        return self._tool_available[tool] or False

    def _get_file_tools(self, file_path: str) -> list[ToolType]:
        """Determine which tools to use for a file."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".py":
            return [ToolType.RUFF, ToolType.MYPY, ToolType.BANDIT]
        elif suffix in (".ts", ".tsx", ".js", ".jsx"):
            return [ToolType.ESLINT]
        elif suffix == ".dart":
            return [ToolType.DART_ANALYZE]
        return []

    async def diagnose_file(
        self,
        file_path: str,
        tools: list[ToolType] | None = None,
    ) -> DiagnosticReport:
        """
        Diagnose a single file.

        تشخيص ملف واحد

        Args:
            file_path: Path to the file to diagnose
            tools: Specific tools to use (auto-detected if None)

        Returns:
            DiagnosticReport with all found issues
        """
        if not os.path.exists(file_path):
            raise DiagnosticError(f"File not found: {file_path}")

        start_time = time.time()

        if tools is None:
            tools = self._get_file_tools(file_path)

        all_diagnostics: list[Diagnostic] = []
        used_tools: list[ToolType] = []

        for tool in tools:
            if not await self.check_tool_available(tool):
                continue

            used_tools.append(tool)

            if tool == ToolType.RUFF:
                diags = await self._run_ruff(file_path)
            elif tool == ToolType.ESLINT:
                diags = await self._run_eslint(file_path)
            elif tool == ToolType.MYPY:
                diags = await self._run_mypy(file_path)
            elif tool == ToolType.BANDIT:
                diags = await self._run_bandit(file_path)
            elif tool == ToolType.DART_ANALYZE:
                diags = await self._run_dart_analyze(file_path)
            else:
                continue

            all_diagnostics.extend(diags)

        duration = (time.time() - start_time) * 1000

        return DiagnosticReport(
            id=str(uuid.uuid4()),
            target=file_path,
            diagnostics=all_diagnostics,
            tools_used=used_tools,
            scan_duration_ms=duration,
        )

    async def diagnose_directory(
        self,
        directory: str,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        max_files: int = 100,
    ) -> DiagnosticReport:
        """
        Diagnose all files in a directory.

        تشخيص جميع الملفات في مجلد

        Args:
            directory: Directory path to diagnose
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            max_files: Maximum number of files to process

        Returns:
            Combined DiagnosticReport
        """
        if not os.path.isdir(directory):
            raise DiagnosticError(f"Directory not found: {directory}")

        start_time = time.time()

        if include_patterns is None:
            include_patterns = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.dart"]
        if exclude_patterns is None:
            exclude_patterns = [
                "**/node_modules/**",
                "**/.venv/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/build/**",
            ]

        # Find files
        files: list[str] = []
        dir_path = Path(directory)

        for pattern in include_patterns:
            for file_path in dir_path.rglob(pattern):
                if len(files) >= max_files:
                    break

                # Check exclusions
                excluded = any(
                    file_path.match(excl) for excl in exclude_patterns
                )
                if not excluded and file_path.is_file():
                    files.append(str(file_path))

        # Run diagnostics on all files concurrently
        tasks = [self.diagnose_file(f) for f in files]
        reports = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        all_diagnostics: list[Diagnostic] = []
        all_tools: set[ToolType] = set()

        for report in reports:
            if isinstance(report, DiagnosticReport):
                all_diagnostics.extend(report.diagnostics)
                all_tools.update(report.tools_used)

        duration = (time.time() - start_time) * 1000

        return DiagnosticReport(
            id=str(uuid.uuid4()),
            target=directory,
            diagnostics=all_diagnostics,
            tools_used=list(all_tools),
            scan_duration_ms=duration,
        )

    async def _run_ruff(self, file_path: str) -> list[Diagnostic]:
        """Run ruff on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.ruff_path,
                "check",
                "--output-format=json",
                "--no-fix",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results:
                message = item.get("message", "Unknown error")
                rule_id = item.get("code", "")

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level(
                        "error" if rule_id.startswith(("E", "F")) else "warning"
                    ),
                    category=get_category_from_rule(rule_id, ToolType.RUFF),
                    location=CodeLocation(
                        file_path=item.get("filename", file_path),
                        line_start=item.get("location", {}).get("row", 1),
                        line_end=item.get("end_location", {}).get("row"),
                        column_start=item.get("location", {}).get("column"),
                        column_end=item.get("end_location", {}).get("column"),
                    ),
                    rule_id=rule_id,
                    tool=ToolType.RUFF,
                    suggestion=item.get("fix", {}).get("message"),
                    documentation_url=item.get("url"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Ruff execution failed: {e}") from e

    async def _run_eslint(self, file_path: str) -> list[Diagnostic]:
        """Run eslint on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.eslint_path,
                "--format=json",
                "--no-fix",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for file_result in results:
                for msg in file_result.get("messages", []):
                    message = msg.get("message", "Unknown error")
                    rule_id = msg.get("ruleId", "")
                    severity = "error" if msg.get("severity", 1) == 2 else "warning"

                    diag = Diagnostic(
                        id=str(uuid.uuid4()),
                        message=message,
                        message_ar=translate_message(message),
                        severity=get_severity_from_level(severity),
                        category=get_category_from_rule(rule_id, ToolType.ESLINT),
                        location=CodeLocation(
                            file_path=file_result.get("filePath", file_path),
                            line_start=msg.get("line", 1),
                            line_end=msg.get("endLine"),
                            column_start=msg.get("column"),
                            column_end=msg.get("endColumn"),
                        ),
                        rule_id=rule_id,
                        tool=ToolType.ESLINT,
                        suggestion=msg.get("suggestions", [{}])[0].get("desc")
                        if msg.get("suggestions")
                        else None,
                    )
                    diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"ESLint execution failed: {e}") from e

    async def _run_mypy(self, file_path: str) -> list[Diagnostic]:
        """Run mypy on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.mypy_path,
                "--output=json",
                "--no-error-summary",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            diagnostics: list[Diagnostic] = []

            for line in stdout.decode().strip().split("\n"):
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    message = item.get("message", "Unknown type error")

                    diag = Diagnostic(
                        id=str(uuid.uuid4()),
                        message=message,
                        message_ar=translate_message(message),
                        severity=get_severity_from_level(
                            item.get("severity", "error")
                        ),
                        category=DiagnosticCategory.TYPE,
                        location=CodeLocation(
                            file_path=item.get("file", file_path),
                            line_start=item.get("line", 1),
                            column_start=item.get("column"),
                        ),
                        rule_id=item.get("code"),
                        tool=ToolType.MYPY,
                    )
                    diagnostics.append(diag)
                except json.JSONDecodeError:
                    continue

            return diagnostics

        except (TimeoutError, OSError) as e:
            raise DiagnosticError(f"Mypy execution failed: {e}") from e

    async def _run_bandit(self, file_path: str) -> list[Diagnostic]:
        """Run bandit security scanner on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.bandit_path,
                "-f",
                "json",
                "-q",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results.get("results", []):
                message = item.get("issue_text", "Security issue")

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level(
                        item.get("issue_severity", "medium")
                    ),
                    category=DiagnosticCategory.SECURITY,
                    location=CodeLocation(
                        file_path=item.get("filename", file_path),
                        line_start=item.get("line_number", 1),
                        line_end=item.get("line_range", [1])[-1],
                    ),
                    rule_id=item.get("test_id"),
                    tool=ToolType.BANDIT,
                    source_code=item.get("code"),
                    documentation_url=item.get("more_info"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Bandit execution failed: {e}") from e

    async def _run_dart_analyze(self, file_path: str) -> list[Diagnostic]:
        """Run dart analyze on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.dart_path,
                "analyze",
                "--format=json",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results.get("diagnostics", []):
                message = item.get("problemMessage", "Dart analysis issue")
                severity = item.get("severity", "WARNING").lower()

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level(severity),
                    category=get_category_from_rule(
                        item.get("code", ""), ToolType.DART_ANALYZE
                    ),
                    location=CodeLocation(
                        file_path=item.get("location", {}).get("file", file_path),
                        line_start=item.get("location", {}).get("startLine", 1),
                        line_end=item.get("location", {}).get("endLine"),
                        column_start=item.get("location", {}).get("startColumn"),
                        column_end=item.get("location", {}).get("endColumn"),
                    ),
                    rule_id=item.get("code"),
                    tool=ToolType.DART_ANALYZE,
                    suggestion=item.get("correctionMessage"),
                    documentation_url=item.get("documentation"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Dart analyze execution failed: {e}") from e

    def format_report_markdown(
        self,
        report: DiagnosticReport,
        include_arabic: bool = True,
    ) -> str:
        """
        Format diagnostic report as markdown.

        تنسيق تقرير التشخيص كـ Markdown

        Args:
            report: The diagnostic report to format
            include_arabic: Include Arabic translations

        Returns:
            Formatted markdown string
        """
        lines = [
            "# Code Diagnostic Report | تقرير تشخيص الكود",
            "",
            f"**Target | الهدف**: `{report.target}`",
            f"**Scan Time | وقت الفحص**: {report.scan_duration_ms:.2f}ms",
            f"**Tools Used | الأدوات**: {', '.join(t.value for t in report.tools_used)}",
            "",
            "## Summary | ملخص",
            "",
            "| Severity | Count |",
            "|----------|-------|",
            f"| 🔴 Errors | {report.total_errors} |",
            f"| 🟠 Warnings | {report.total_warnings} |",
            f"| 🔵 Info | {report.total_info} |",
            f"| ⚪ Hints | {report.total_hints} |",
            "",
            "## Issues | المشاكل",
            "",
        ]

        severity_icons = {
            DiagnosticSeverity.ERROR: "🔴",
            DiagnosticSeverity.WARNING: "🟠",
            DiagnosticSeverity.INFO: "🔵",
            DiagnosticSeverity.HINT: "⚪",
        }

        for diag in report.diagnostics:
            icon = severity_icons.get(diag.severity, "⚪")
            lines.append(f"### {icon} {diag.rule_id or 'Unknown'}")
            lines.append("")
            lines.append(f"**Location**: `{diag.location}`")
            lines.append(f"**Message**: {diag.message}")

            if include_arabic and diag.message_ar:
                lines.append(f"**الرسالة**: {diag.message_ar}")

            if diag.suggestion:
                lines.append(f"**Suggestion**: {diag.suggestion}")

            if diag.documentation_url:
                lines.append(f"**Docs**: [{diag.rule_id}]({diag.documentation_url})")

            lines.append("")

        return "\n".join(lines)
