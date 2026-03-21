"""
Frontend & Mobile Diagnostics Module for SAHOOL AutoFix Engine
وحدة تشخيص الواجهات والتطبيق المحمول لمحرك الإصلاح التلقائي

Integrates frontend (React/Next.js) and mobile (Flutter) diagnostics
with the AI-powered AutoFix engine.

Author: SAHOOL Platform Team
Created: January 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from .models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
    FixConfidence,
)

logger = logging.getLogger(__name__)


class FrontendTool(StrEnum):
    """Supported frontend diagnostic tools"""

    ESLINT = "eslint"
    TYPESCRIPT = "typescript"
    BIOME = "biome"
    OXLINT = "oxlint"


class MobileTool(StrEnum):
    """Supported mobile diagnostic tools"""

    DART_ANALYZE = "dart_analyze"
    DART_FORMAT = "dart_format"
    FLUTTER_TEST = "flutter_test"


@dataclass
class FrontendDiagnosticConfig:
    """Configuration for frontend diagnostics | إعدادات تشخيص الواجهات"""

    # Paths
    web_path: str = "apps/web"
    admin_path: str = "apps/admin"
    packages_path: str = "packages"

    # Tools to use
    tools: list[FrontendTool] = field(
        default_factory=lambda: [
            FrontendTool.ESLINT,
            FrontendTool.TYPESCRIPT,
        ]
    )

    # Options
    auto_fix: bool = False
    include_packages: bool = True
    timeout_seconds: int = 120


@dataclass
class MobileDiagnosticConfig:
    """Configuration for mobile diagnostics | إعدادات تشخيص التطبيق المحمول"""

    # Paths
    mobile_path: str = "apps/mobile"
    field_app_path: str = "apps/mobile/sahool_field_app"

    # Tools to use
    tools: list[MobileTool] = field(
        default_factory=lambda: [
            MobileTool.DART_ANALYZE,
            MobileTool.DART_FORMAT,
        ]
    )

    # Options
    auto_fix: bool = False
    run_tests: bool = False
    timeout_seconds: int = 180


class FrontendDiagnosticRunner:
    """
    Runs frontend diagnostics and integrates with AutoFix engine.
    يشغل تشخيصات الواجهات ويتكامل مع محرك الإصلاح التلقائي.
    """

    def __init__(self, config: FrontendDiagnosticConfig | None = None):
        self.config = config or FrontendDiagnosticConfig()
        self.working_dir = Path.cwd()

    async def run_eslint(self, path: str) -> list[Diagnostic]:
        """Run ESLint and parse results | تشغيل ESLint وتحليل النتائج"""
        diagnostics = []
        full_path = self.working_dir / path

        if not full_path.exists():
            logger.warning(f"Path not found: {path}")
            return diagnostics

        try:
            cmd = ["npx", "eslint", str(path), "--format", "json"]
            if self.config.auto_fix:
                cmd.append("--fix")

            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            if result.stdout:
                try:
                    eslint_output = json.loads(result.stdout)
                    for file_result in eslint_output:
                        file_path = file_result.get("filePath", "")
                        for message in file_result.get("messages", []):
                            severity = (
                                DiagnosticSeverity.ERROR if message.get("severity") == 2 else DiagnosticSeverity.WARNING
                            )

                            diagnostics.append(
                                Diagnostic(
                                    tool="eslint",
                                    code=message.get("ruleId", "unknown"),
                                    message=message.get("message", ""),
                                    message_ar=self._translate_eslint_message(message.get("message", "")),
                                    file_path=file_path,
                                    line=message.get("line", 0),
                                    column=message.get("column", 0),
                                    severity=severity,
                                    category=DiagnosticCategory.STYLE,
                                    fixable=message.get("fix") is not None,
                                    fix_confidence=FixConfidence.HIGH if message.get("fix") else FixConfidence.LOW,
                                )
                            )
                except json.JSONDecodeError:
                    logger.warning("Failed to parse ESLint JSON output")

        except subprocess.TimeoutExpired:
            logger.error(f"ESLint timeout for {path}")
        except Exception as e:
            logger.error(f"ESLint error: {e}")

        return diagnostics

    async def run_typescript(self, path: str) -> list[Diagnostic]:
        """Run TypeScript compiler check | تشغيل فحص TypeScript"""
        diagnostics = []
        full_path = self.working_dir / path

        if not full_path.exists():
            return diagnostics

        try:
            cmd = ["npx", "tsc", "--noEmit", "--pretty", "false"]

            result = subprocess.run(
                cmd,
                cwd=full_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            # Parse TypeScript errors
            error_pattern = r"(.+)\((\d+),(\d+)\): error (TS\d+): (.+)"
            for line in result.stdout.split("\n") + result.stderr.split("\n"):
                match = re.match(error_pattern, line)
                if match:
                    file_path, line_num, col, code, message = match.groups()
                    diagnostics.append(
                        Diagnostic(
                            tool="typescript",
                            code=code,
                            message=message,
                            message_ar=f"خطأ TypeScript: {message}",
                            file_path=str(full_path / file_path),
                            line=int(line_num),
                            column=int(col),
                            severity=DiagnosticSeverity.ERROR,
                            category=DiagnosticCategory.TYPE_ERROR,
                            fixable=False,
                            fix_confidence=FixConfidence.LOW,
                        )
                    )

        except Exception as e:
            logger.error(f"TypeScript error: {e}")

        return diagnostics

    async def run_biome(self, path: str) -> list[Diagnostic]:
        """Run Biome linter | تشغيل Biome"""
        diagnostics = []

        try:
            cmd = ["npx", "@biomejs/biome", "check", str(path), "--reporter", "json"]
            if self.config.auto_fix:
                cmd.append("--apply")

            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            if result.stdout:
                try:
                    biome_output = json.loads(result.stdout)
                    for diagnostic in biome_output.get("diagnostics", []):
                        severity = (
                            DiagnosticSeverity.ERROR
                            if diagnostic.get("severity") == "error"
                            else DiagnosticSeverity.WARNING
                        )

                        location = diagnostic.get("location", {})
                        diagnostics.append(
                            Diagnostic(
                                tool="biome",
                                code=diagnostic.get("category", "unknown"),
                                message=diagnostic.get("message", ""),
                                message_ar=f"Biome: {diagnostic.get('message', '')}",
                                file_path=location.get("path", ""),
                                line=location.get("span", {}).get("start", {}).get("line", 0),
                                column=location.get("span", {}).get("start", {}).get("column", 0),
                                severity=severity,
                                category=DiagnosticCategory.STYLE,
                                fixable=diagnostic.get("fixable", False),
                            )
                        )
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.error(f"Biome error: {e}")

        return diagnostics

    async def diagnose(self) -> DiagnosticReport:
        """Run all frontend diagnostics | تشغيل جميع تشخيصات الواجهات"""
        all_diagnostics: list[Diagnostic] = []

        paths_to_check = [self.config.web_path, self.config.admin_path]

        for path in paths_to_check:
            if FrontendTool.ESLINT in self.config.tools:
                all_diagnostics.extend(await self.run_eslint(path))

            if FrontendTool.TYPESCRIPT in self.config.tools:
                all_diagnostics.extend(await self.run_typescript(path))

            if FrontendTool.BIOME in self.config.tools:
                all_diagnostics.extend(await self.run_biome(path))

        return DiagnosticReport(
            diagnostics=all_diagnostics,
            tools_used=[t.value for t in self.config.tools],
            paths_scanned=paths_to_check,
        )

    def _translate_eslint_message(self, message: str) -> str:
        """Translate common ESLint messages to Arabic"""
        translations = {
            "is defined but never used": "معرف ولكن غير مستخدم",
            "Missing semicolon": "فاصلة منقوطة مفقودة",
            "Unexpected console statement": "عبارة console غير متوقعة",
            "is not defined": "غير معرف",
        }
        for en, ar in translations.items():
            if en in message:
                return message.replace(en, ar)
        return message


class MobileDiagnosticRunner:
    """
    Runs Flutter/Dart diagnostics and integrates with AutoFix engine.
    يشغل تشخيصات Flutter/Dart ويتكامل مع محرك الإصلاح التلقائي.
    """

    def __init__(self, config: MobileDiagnosticConfig | None = None):
        self.config = config or MobileDiagnosticConfig()
        self.working_dir = Path.cwd()

    async def run_dart_analyze(self, path: str) -> list[Diagnostic]:
        """Run Dart analyzer | تشغيل محلل Dart"""
        diagnostics = []
        full_path = self.working_dir / path

        if not full_path.exists():
            return diagnostics

        try:
            cmd = ["flutter", "analyze", "--no-pub"]

            result = subprocess.run(
                cmd,
                cwd=full_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            # Parse Dart analyzer output
            # Format: "  info • Message • path/file.dart:line:col • rule_name"
            pattern = r"\s*(info|warning|error)\s*•\s*(.+?)\s*•\s*(.+?):(\d+):(\d+)\s*•\s*(\w+)"

            for line in result.stdout.split("\n"):
                match = re.match(pattern, line)
                if match:
                    severity_str, message, file_path, line_num, col, code = match.groups()

                    severity_map = {
                        "info": DiagnosticSeverity.INFO,
                        "warning": DiagnosticSeverity.WARNING,
                        "error": DiagnosticSeverity.ERROR,
                    }

                    diagnostics.append(
                        Diagnostic(
                            tool="dart_analyze",
                            code=code,
                            message=message,
                            message_ar=self._translate_dart_message(message),
                            file_path=str(full_path / file_path),
                            line=int(line_num),
                            column=int(col),
                            severity=severity_map.get(severity_str, DiagnosticSeverity.INFO),
                            category=DiagnosticCategory.STYLE,
                            fixable=code in self._fixable_dart_rules(),
                            fix_confidence=FixConfidence.HIGH
                            if code in self._fixable_dart_rules()
                            else FixConfidence.LOW,
                        )
                    )

        except Exception as e:
            logger.error(f"Dart analyze error: {e}")

        return diagnostics

    async def run_dart_format_check(self, path: str) -> list[Diagnostic]:
        """Check Dart formatting | فحص تنسيق Dart"""
        diagnostics = []
        full_path = self.working_dir / path

        if not full_path.exists():
            return diagnostics

        try:
            cmd = ["dart", "format", "--set-exit-if-changed", "--output=none", "."]

            result = subprocess.run(
                cmd,
                cwd=full_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            if result.returncode != 0:
                # Parse unformatted files
                for line in result.stdout.split("\n"):
                    if line.strip() and not line.startswith("Formatted"):
                        diagnostics.append(
                            Diagnostic(
                                tool="dart_format",
                                code="format_required",
                                message=f"File needs formatting: {line.strip()}",
                                message_ar=f"الملف يحتاج تنسيق: {line.strip()}",
                                file_path=str(full_path / line.strip()),
                                line=1,
                                column=1,
                                severity=DiagnosticSeverity.INFO,
                                category=DiagnosticCategory.STYLE,
                                fixable=True,
                                fix_confidence=FixConfidence.HIGH,
                            )
                        )

        except Exception as e:
            logger.error(f"Dart format check error: {e}")

        return diagnostics

    async def run_dart_fix(self, path: str) -> int:
        """Apply Dart fixes | تطبيق إصلاحات Dart"""
        full_path = self.working_dir / path

        if not full_path.exists():
            return 0

        try:
            cmd = ["dart", "fix", "--apply"]

            result = subprocess.run(
                cmd,
                cwd=full_path,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )

            # Count fixed issues
            match = re.search(r"(\d+) fix", result.stdout)
            if match:
                return int(match.group(1))

        except Exception as e:
            logger.error(f"Dart fix error: {e}")

        return 0

    async def diagnose(self) -> DiagnosticReport:
        """Run all mobile diagnostics | تشغيل جميع تشخيصات التطبيق المحمول"""
        all_diagnostics: list[Diagnostic] = []

        paths_to_check = [self.config.mobile_path]
        if Path(self.config.field_app_path).exists():
            paths_to_check.append(self.config.field_app_path)

        for path in paths_to_check:
            if MobileTool.DART_ANALYZE in self.config.tools:
                all_diagnostics.extend(await self.run_dart_analyze(path))

            if MobileTool.DART_FORMAT in self.config.tools:
                all_diagnostics.extend(await self.run_dart_format_check(path))

        # Apply fixes if configured
        if self.config.auto_fix:
            for path in paths_to_check:
                fixed_count = await self.run_dart_fix(path)
                logger.info(f"Applied {fixed_count} Dart fixes in {path}")

        return DiagnosticReport(
            diagnostics=all_diagnostics,
            tools_used=[t.value for t in self.config.tools],
            paths_scanned=paths_to_check,
        )

    def _translate_dart_message(self, message: str) -> str:
        """Translate common Dart messages to Arabic"""
        translations = {
            "unused_import": "استيراد غير مستخدم",
            "unused_local_variable": "متغير محلي غير مستخدم",
            "prefer_const_constructors": "يُفضل استخدام const",
            "avoid_print": "تجنب استخدام print",
        }
        for en, ar in translations.items():
            if en in message.lower():
                return ar
        return message

    def _fixable_dart_rules(self) -> set[str]:
        """Return set of auto-fixable Dart rules"""
        return {
            "prefer_const_constructors",
            "prefer_const_declarations",
            "unnecessary_new",
            "unnecessary_this",
            "prefer_single_quotes",
            "sort_child_properties_last",
            "unnecessary_const",
            "use_key_in_widget_constructors",
        }


class UnifiedDiagnosticRunner:
    """
    Unified diagnostic runner for all platforms.
    مشغل تشخيص موحد لجميع المنصات.
    """

    def __init__(
        self,
        frontend_config: FrontendDiagnosticConfig | None = None,
        mobile_config: MobileDiagnosticConfig | None = None,
    ):
        self.frontend_runner = FrontendDiagnosticRunner(frontend_config)
        self.mobile_runner = MobileDiagnosticRunner(mobile_config)

    async def diagnose_all(self) -> dict[str, DiagnosticReport]:
        """Run diagnostics on all platforms | تشغيل التشخيصات على جميع المنصات"""
        results = {}

        # Run frontend and mobile diagnostics in parallel
        frontend_task = asyncio.create_task(self.frontend_runner.diagnose())
        mobile_task = asyncio.create_task(self.mobile_runner.diagnose())

        results["frontend"] = await frontend_task
        results["mobile"] = await mobile_task

        return results

    async def diagnose_frontend(self) -> DiagnosticReport:
        """Run frontend diagnostics only | تشغيل تشخيصات الواجهات فقط"""
        return await self.frontend_runner.diagnose()

    async def diagnose_mobile(self) -> DiagnosticReport:
        """Run mobile diagnostics only | تشغيل تشخيصات التطبيق فقط"""
        return await self.mobile_runner.diagnose()

    def get_summary(self, reports: dict[str, DiagnosticReport]) -> dict[str, Any]:
        """Get summary of all diagnostics | الحصول على ملخص جميع التشخيصات"""
        total_issues = 0
        total_fixable = 0
        by_severity: dict[str, int] = {}
        by_platform: dict[str, int] = {}

        for platform, report in reports.items():
            platform_count = len(report.diagnostics)
            total_issues += platform_count
            by_platform[platform] = platform_count

            for diag in report.diagnostics:
                if diag.fixable:
                    total_fixable += 1
                severity_name = diag.severity.value
                by_severity[severity_name] = by_severity.get(severity_name, 0) + 1

        return {
            "total_issues": total_issues,
            "total_fixable": total_fixable,
            "by_severity": by_severity,
            "by_platform": by_platform,
            "summary_ar": f"إجمالي المشاكل: {total_issues}، قابلة للإصلاح: {total_fixable}",
        }


# Convenience functions
async def diagnose_frontend(auto_fix: bool = False) -> DiagnosticReport:
    """Quick frontend diagnostic | تشخيص سريع للواجهات"""
    config = FrontendDiagnosticConfig(auto_fix=auto_fix)
    runner = FrontendDiagnosticRunner(config)
    return await runner.diagnose()


async def diagnose_mobile(auto_fix: bool = False) -> DiagnosticReport:
    """Quick mobile diagnostic | تشخيص سريع للتطبيق"""
    config = MobileDiagnosticConfig(auto_fix=auto_fix)
    runner = MobileDiagnosticRunner(config)
    return await runner.diagnose()


async def diagnose_all_platforms(auto_fix: bool = False) -> dict[str, DiagnosticReport]:
    """Quick diagnostic for all platforms | تشخيص سريع لجميع المنصات"""
    frontend_config = FrontendDiagnosticConfig(auto_fix=auto_fix)
    mobile_config = MobileDiagnosticConfig(auto_fix=auto_fix)
    runner = UnifiedDiagnosticRunner(frontend_config, mobile_config)
    return await runner.diagnose_all()
