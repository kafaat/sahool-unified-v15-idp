"""
8-Layer Quality Orchestration System for SAHOOL Platform
نظام تنسيق الجودة ذو 8 طبقات لمنصة سهول

Orchestrates multi-layer quality analysis across the entire platform:
Python, Node.js, Flutter, containers, and infrastructure.

Layers:
    1. Lint & Format (التنسيق والتدقيق)
    2. Type Checking (فحص الأنواع)
    3. Security SAST (الأمان)
    4. Dependency Security (أمان التبعيات)
    5. Architecture (الهندسة المعمارية)
    6. Dead Code & Complexity (الكود الميت والتعقيد)
    7. Testing (الاختبارات)
    8. Container & Infrastructure (الحاويات والبنية التحتية)

Author: SAHOOL Platform Team
Created: March 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import (
    DiagnosticSeverity,
    QualityLayer,
    ToolType,
)

logger = logging.getLogger(__name__)

# Layer to tool mapping
LAYER_TOOLS: dict[QualityLayer, list[ToolType]] = {
    QualityLayer.LINT_FORMAT: [ToolType.RUFF, ToolType.ESLINT, ToolType.BIOME],
    QualityLayer.TYPE_CHECK: [ToolType.MYPY, ToolType.PYRIGHT, ToolType.TYPESCRIPT],
    QualityLayer.SECURITY_SAST: [ToolType.BANDIT, ToolType.SEMGREP, ToolType.CODEQL],
    QualityLayer.DEPENDENCY_SECURITY: [ToolType.NPM_AUDIT, ToolType.PIP_AUDIT],
    QualityLayer.ARCHITECTURE: [ToolType.KNIP, ToolType.MADGE, ToolType.DEPCHECK],
    QualityLayer.DEAD_CODE: [ToolType.VULTURE, ToolType.RADON],
    QualityLayer.TESTING: [],  # Uses pytest / vitest / flutter test
    QualityLayer.CONTAINER: [ToolType.HADOLINT, ToolType.DETECT_SECRETS, ToolType.TRIVY],
}


@dataclass
class LayerResult:
    """Result from a single quality layer analysis."""

    layer: QualityLayer
    passed: bool
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    tools_run: list[str] = field(default_factory=list)
    tools_skipped: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    details: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    summary_ar: str = ""

    @property
    def severity(self) -> DiagnosticSeverity:
        """Get overall severity based on issue counts."""
        if self.errors > 0:
            return DiagnosticSeverity.ERROR
        if self.warnings > 0:
            return DiagnosticSeverity.WARNING
        if self.infos > 0:
            return DiagnosticSeverity.INFO
        return DiagnosticSeverity.HINT

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer": self.layer.value,
            "passed": self.passed,
            "total_issues": self.total_issues,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
            "tools_run": self.tools_run,
            "tools_skipped": self.tools_skipped,
            "duration_ms": self.duration_ms,
            "details": self.details,
            "summary": self.summary,
            "summary_ar": self.summary_ar,
        }


@dataclass
class QualityReport:
    """Complete quality report across all layers."""

    id: str
    target: str
    layers: list[LayerResult] = field(default_factory=list)
    overall_passed: bool = True
    overall_score: float = 100.0
    total_issues: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    duration_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Calculate aggregated stats."""
        self._recalculate()

    def _recalculate(self):
        """Recalculate totals from layer results."""
        self.total_issues = sum(lr.total_issues for lr in self.layers)
        self.total_errors = sum(lr.errors for lr in self.layers)
        self.total_warnings = sum(lr.warnings for lr in self.layers)
        self.overall_passed = all(lr.passed for lr in self.layers)
        self.duration_ms = sum(lr.duration_ms for lr in self.layers)

        # Score: start at 100, deduct for issues
        score = 100.0
        score -= self.total_errors * 5.0
        score -= self.total_warnings * 1.0
        self.overall_score = max(0.0, min(100.0, score))

    def add_layer_result(self, result: LayerResult):
        """Add a layer result and recalculate."""
        self.layers.append(result)
        self._recalculate()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "target": self.target,
            "overall_passed": self.overall_passed,
            "overall_score": round(self.overall_score, 1),
            "total_issues": self.total_issues,
            "total_errors": self.total_errors,
            "total_warnings": self.total_warnings,
            "duration_ms": round(self.duration_ms, 1),
            "layers": [lr.to_dict() for lr in self.layers],
            "created_at": self.created_at.isoformat(),
        }


class QualityOrchestrator:
    """
    Orchestrates 8-layer quality analysis across the SAHOOL platform.
    منسق الجودة ذو 8 طبقات لمنصة سهول

    Usage:
        orchestrator = QualityOrchestrator(working_dir="/path/to/project")
        report = await orchestrator.run_all_layers()
        print(f"Score: {report.overall_score}/100")
    """

    def __init__(
        self,
        working_dir: str = ".",
        timeout: int = 300,
        fail_fast: bool = False,
        layers: list[QualityLayer] | None = None,
    ):
        self.working_dir = Path(working_dir).resolve()
        self.timeout = timeout
        self.fail_fast = fail_fast
        self.enabled_layers = layers or list(QualityLayer)

    async def run_all_layers(self) -> QualityReport:
        """Run all enabled quality layers sequentially."""
        import uuid

        report = QualityReport(
            id=f"qr-{uuid.uuid4().hex[:12]}",
            target=str(self.working_dir),
        )

        for layer in self.enabled_layers:
            result = await self._run_layer(layer)
            report.add_layer_result(result)

            if self.fail_fast and not result.passed:
                logger.warning("Fail-fast: stopping at layer %s", layer.value)
                break

        return report

    async def run_layer(self, layer: QualityLayer) -> LayerResult:
        """Run a single quality layer."""
        return await self._run_layer(layer)

    async def _run_layer(self, layer: QualityLayer) -> LayerResult:
        """Execute a single layer's tools."""
        start = time.monotonic()
        handler = self._get_layer_handler(layer)

        try:
            result = await handler()
        except Exception as e:
            logger.error("Layer %s failed: %s", layer.value, e)
            result = LayerResult(
                layer=layer,
                passed=False,
                errors=1,
                total_issues=1,
                summary=f"Layer failed: {e}",
                summary_ar=f"فشلت الطبقة: {e}",
            )

        result.duration_ms = (time.monotonic() - start) * 1000
        return result

    def _get_layer_handler(self, layer: QualityLayer):
        """Get the handler function for a layer."""
        handlers = {
            QualityLayer.LINT_FORMAT: self._layer_lint_format,
            QualityLayer.TYPE_CHECK: self._layer_type_check,
            QualityLayer.SECURITY_SAST: self._layer_security_sast,
            QualityLayer.DEPENDENCY_SECURITY: self._layer_dependency_security,
            QualityLayer.ARCHITECTURE: self._layer_architecture,
            QualityLayer.DEAD_CODE: self._layer_dead_code,
            QualityLayer.TESTING: self._layer_testing,
            QualityLayer.CONTAINER: self._layer_container,
        }
        return handlers[layer]

    async def _run_cmd(self, cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
        """Run a command asynchronously."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)
            return subprocess.CompletedProcess(
                cmd, proc.returncode or 0, stdout.decode(errors="replace"), stderr.decode(errors="replace")
            )
        except asyncio.TimeoutError:
            logger.warning("Command timed out: %s", " ".join(cmd))
            return subprocess.CompletedProcess(cmd, 124, "", "timeout")
        except FileNotFoundError:
            return subprocess.CompletedProcess(cmd, 127, "", f"Command not found: {cmd[0]}")

    def _tool_available(self, cmd: str) -> bool:
        """Check if a command-line tool is available."""
        try:
            result = subprocess.run(
                ["which", cmd], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    # ──────────────────────────────────────────────
    # Layer 1: Lint & Format | التنسيق والتدقيق
    # ──────────────────────────────────────────────
    async def _layer_lint_format(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.LINT_FORMAT, passed=True)
        errors = 0
        warnings = 0

        # Ruff (Python)
        if self._tool_available("ruff"):
            proc = await self._run_cmd(["ruff", "check", "--output-format=json", "apps/", "shared/"])
            result.tools_run.append("ruff")
            if proc.returncode != 0 and proc.stdout.strip():
                try:
                    issues = json.loads(proc.stdout)
                    e_count = sum(1 for i in issues if i.get("type") == "E")
                    w_count = len(issues) - e_count
                    errors += e_count
                    warnings += w_count
                    result.details.append({"tool": "ruff", "issues": len(issues)})
                except json.JSONDecodeError:
                    warnings += 1
        else:
            result.tools_skipped.append("ruff")

        # ESLint (Node.js)
        if self._tool_available("npx"):
            proc = await self._run_cmd(["npx", "eslint", "--format=json", "apps/web/", "apps/admin/", "packages/"])
            result.tools_run.append("eslint")
            if proc.returncode != 0 and proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    for file_result in data:
                        errors += file_result.get("errorCount", 0)
                        warnings += file_result.get("warningCount", 0)
                    result.details.append({"tool": "eslint", "errors": errors, "warnings": warnings})
                except json.JSONDecodeError:
                    warnings += 1
        else:
            result.tools_skipped.append("eslint")

        result.errors = errors
        result.warnings = warnings
        result.total_issues = errors + warnings
        result.passed = errors == 0
        result.summary = f"Lint: {errors} errors, {warnings} warnings"
        result.summary_ar = f"التدقيق: {errors} أخطاء، {warnings} تحذيرات"
        return result

    # ──────────────────────────────────────────────
    # Layer 2: Type Checking | فحص الأنواع
    # ──────────────────────────────────────────────
    async def _layer_type_check(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.TYPE_CHECK, passed=True)
        errors = 0

        # Mypy (Python)
        if self._tool_available("mypy"):
            proc = await self._run_cmd(["mypy", "--no-error-summary", "apps/", "shared/"])
            result.tools_run.append("mypy")
            if proc.returncode != 0:
                error_lines = [l for l in proc.stdout.splitlines() if ": error:" in l]
                errors += len(error_lines)
                result.details.append({"tool": "mypy", "errors": len(error_lines)})
        else:
            result.tools_skipped.append("mypy")

        # TypeScript
        if self._tool_available("npx"):
            proc = await self._run_cmd(["npx", "tsc", "--noEmit", "--pretty", "false"])
            result.tools_run.append("typescript")
            if proc.returncode != 0:
                ts_errors = len([l for l in proc.stdout.splitlines() if "error TS" in l])
                errors += ts_errors
                result.details.append({"tool": "typescript", "errors": ts_errors})
        else:
            result.tools_skipped.append("typescript")

        result.errors = errors
        result.total_issues = errors
        result.passed = errors == 0
        result.summary = f"Type check: {errors} type errors"
        result.summary_ar = f"فحص الأنواع: {errors} أخطاء"
        return result

    # ──────────────────────────────────────────────
    # Layer 3: Security SAST | الأمان
    # ──────────────────────────────────────────────
    async def _layer_security_sast(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.SECURITY_SAST, passed=True)
        errors = 0
        warnings = 0

        # Bandit (Python security)
        if self._tool_available("bandit"):
            proc = await self._run_cmd(["bandit", "-r", "-f", "json", "apps/", "shared/"])
            result.tools_run.append("bandit")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    results_list = data.get("results", [])
                    for issue in results_list:
                        sev = issue.get("issue_severity", "LOW")
                        if sev in ("HIGH", "MEDIUM"):
                            errors += 1
                        else:
                            warnings += 1
                    result.details.append({"tool": "bandit", "issues": len(results_list)})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("bandit")

        # Semgrep
        if self._tool_available("semgrep"):
            proc = await self._run_cmd(["semgrep", "--json", "--config=auto", "apps/", "shared/"])
            result.tools_run.append("semgrep")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    sg_results = data.get("results", [])
                    errors += len(sg_results)
                    result.details.append({"tool": "semgrep", "issues": len(sg_results)})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("semgrep")

        result.errors = errors
        result.warnings = warnings
        result.total_issues = errors + warnings
        result.passed = errors == 0
        result.summary = f"Security: {errors} vulnerabilities, {warnings} advisories"
        result.summary_ar = f"الأمان: {errors} ثغرات، {warnings} تنبيهات"
        return result

    # ──────────────────────────────────────────────
    # Layer 4: Dependency Security | أمان التبعيات
    # ──────────────────────────────────────────────
    async def _layer_dependency_security(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.DEPENDENCY_SECURITY, passed=True)
        errors = 0
        warnings = 0

        # npm audit
        if self._tool_available("npm"):
            proc = await self._run_cmd(["npm", "audit", "--json"])
            result.tools_run.append("npm_audit")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    vulns = data.get("vulnerabilities", {})
                    for _name, info in vulns.items():
                        sev = info.get("severity", "low")
                        if sev in ("critical", "high"):
                            errors += 1
                        else:
                            warnings += 1
                    result.details.append({"tool": "npm_audit", "vulnerabilities": len(vulns)})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("npm_audit")

        # pip-audit
        if self._tool_available("pip-audit"):
            proc = await self._run_cmd(["pip-audit", "--format=json"])
            result.tools_run.append("pip_audit")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    deps = data if isinstance(data, list) else data.get("dependencies", [])
                    vuln_deps = [d for d in deps if d.get("vulns")]
                    errors += len(vuln_deps)
                    result.details.append({"tool": "pip_audit", "vulnerable_deps": len(vuln_deps)})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("pip_audit")

        result.errors = errors
        result.warnings = warnings
        result.total_issues = errors + warnings
        result.passed = errors == 0
        result.summary = f"Dependencies: {errors} critical, {warnings} advisory"
        result.summary_ar = f"التبعيات: {errors} حرجة، {warnings} تنبيهات"
        return result

    # ──────────────────────────────────────────────
    # Layer 5: Architecture | الهندسة المعمارية
    # ──────────────────────────────────────────────
    async def _layer_architecture(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.ARCHITECTURE, passed=True)
        warnings = 0

        # Circular dependencies (madge)
        if self._tool_available("npx"):
            proc = await self._run_cmd(["npx", "madge", "--circular", "--json", "apps/web/src/"])
            result.tools_run.append("madge")
            if proc.stdout.strip():
                try:
                    cycles = json.loads(proc.stdout)
                    if cycles:
                        warnings += len(cycles)
                        result.details.append({"tool": "madge", "circular_deps": len(cycles)})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("madge")

        # Unused exports (knip)
        if self._tool_available("npx"):
            proc = await self._run_cmd(["npx", "knip", "--reporter=json"])
            result.tools_run.append("knip")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    unused_count = len(data.get("files", [])) + len(data.get("exports", []))
                    warnings += unused_count
                    result.details.append({"tool": "knip", "unused": unused_count})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("knip")

        result.warnings = warnings
        result.total_issues = warnings
        result.passed = True  # Warnings only, don't fail
        result.summary = f"Architecture: {warnings} issues found"
        result.summary_ar = f"الهندسة المعمارية: {warnings} مشكلة"
        return result

    # ──────────────────────────────────────────────
    # Layer 6: Dead Code & Complexity | الكود الميت
    # ──────────────────────────────────────────────
    async def _layer_dead_code(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.DEAD_CODE, passed=True)
        warnings = 0

        # Vulture (Python dead code)
        if self._tool_available("vulture"):
            proc = await self._run_cmd(["vulture", "apps/", "shared/", "--min-confidence=80"])
            result.tools_run.append("vulture")
            if proc.returncode != 0:
                dead_lines = [l for l in proc.stdout.splitlines() if l.strip()]
                warnings += len(dead_lines)
                result.details.append({"tool": "vulture", "dead_code": len(dead_lines)})
        else:
            result.tools_skipped.append("vulture")

        # Radon (Python complexity)
        if self._tool_available("radon"):
            proc = await self._run_cmd(["radon", "cc", "-j", "-nc", "apps/", "shared/"])
            result.tools_run.append("radon")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    complex_funcs = 0
                    for _file, funcs in data.items():
                        for func in funcs:
                            if func.get("complexity", 0) > 20:
                                complex_funcs += 1
                    warnings += complex_funcs
                    result.details.append({"tool": "radon", "complex_functions": complex_funcs})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("radon")

        result.warnings = warnings
        result.total_issues = warnings
        result.passed = True  # Informational
        result.summary = f"Dead code & complexity: {warnings} issues"
        result.summary_ar = f"الكود الميت والتعقيد: {warnings} مشكلة"
        return result

    # ──────────────────────────────────────────────
    # Layer 7: Testing | الاختبارات
    # ──────────────────────────────────────────────
    async def _layer_testing(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.TESTING, passed=True)
        errors = 0

        # Python tests (pytest)
        if self._tool_available("pytest"):
            proc = await self._run_cmd(["pytest", "--tb=no", "-q", "tests/unit/"])
            result.tools_run.append("pytest")
            if proc.returncode != 0:
                errors += 1
                result.details.append({"tool": "pytest", "status": "failed"})
            else:
                result.details.append({"tool": "pytest", "status": "passed"})
        else:
            result.tools_skipped.append("pytest")

        # Node.js tests (vitest)
        if self._tool_available("npx"):
            proc = await self._run_cmd(["npx", "vitest", "run", "--reporter=json"])
            result.tools_run.append("vitest")
            if proc.returncode != 0:
                errors += 1
                result.details.append({"tool": "vitest", "status": "failed"})
            else:
                result.details.append({"tool": "vitest", "status": "passed"})
        else:
            result.tools_skipped.append("vitest")

        result.errors = errors
        result.total_issues = errors
        result.passed = errors == 0
        result.summary = f"Tests: {len(result.tools_run)} suites, {errors} failed"
        result.summary_ar = f"الاختبارات: {len(result.tools_run)} مجموعات، {errors} فشل"
        return result

    # ──────────────────────────────────────────────
    # Layer 8: Container & Infrastructure | الحاويات
    # ──────────────────────────────────────────────
    async def _layer_container(self) -> LayerResult:
        result = LayerResult(layer=QualityLayer.CONTAINER, passed=True)
        errors = 0
        warnings = 0

        # Hadolint (Dockerfile linting)
        if self._tool_available("hadolint"):
            dockerfiles = list(self.working_dir.rglob("Dockerfile*"))
            for df in dockerfiles[:20]:  # Limit to first 20
                proc = await self._run_cmd(["hadolint", "--format=json", str(df)])
                if proc.stdout.strip():
                    try:
                        issues = json.loads(proc.stdout)
                        for issue in issues:
                            lvl = issue.get("level", "info")
                            if lvl == "error":
                                errors += 1
                            elif lvl == "warning":
                                warnings += 1
                    except json.JSONDecodeError:
                        pass
            result.tools_run.append("hadolint")
            result.details.append({
                "tool": "hadolint",
                "dockerfiles_scanned": min(len(dockerfiles), 20),
                "errors": errors,
                "warnings": warnings,
            })
        else:
            result.tools_skipped.append("hadolint")

        # detect-secrets
        if self._tool_available("detect-secrets"):
            proc = await self._run_cmd(["detect-secrets", "scan", "--list-all-plugins"])
            result.tools_run.append("detect_secrets")
            if proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout)
                    secrets_found = len(data.get("results", {}))
                    if secrets_found > 0:
                        errors += secrets_found
                        result.details.append({"tool": "detect_secrets", "secrets": secrets_found})
                except json.JSONDecodeError:
                    pass
        else:
            result.tools_skipped.append("detect_secrets")

        result.errors = errors
        result.warnings = warnings
        result.total_issues = errors + warnings
        result.passed = errors == 0
        result.summary = f"Container: {errors} errors, {warnings} warnings"
        result.summary_ar = f"الحاويات: {errors} أخطاء، {warnings} تحذيرات"
        return result


async def run_quality_scan(
    working_dir: str = ".",
    layers: list[QualityLayer] | None = None,
    fail_fast: bool = False,
    timeout: int = 300,
) -> QualityReport:
    """
    Quick function to run a quality scan.
    دالة سريعة لتشغيل فحص الجودة

    Args:
        working_dir: Project root directory
        layers: Specific layers to run (None = all)
        fail_fast: Stop on first layer failure
        timeout: Timeout per tool in seconds

    Returns:
        QualityReport with all layer results
    """
    orchestrator = QualityOrchestrator(
        working_dir=working_dir,
        layers=layers,
        fail_fast=fail_fast,
        timeout=timeout,
    )
    return await orchestrator.run_all_layers()
