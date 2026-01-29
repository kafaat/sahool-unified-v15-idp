"""
FixOps Orchestrator
منسق عمليات الإصلاح

Main orchestrator for automated code fixing operations.
Integrates signal collection, analysis, and fix application.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog

from .signals import CISignal, LocalSignal, SignalCollector

logger = structlog.get_logger(__name__)


class SignalSource(str, Enum):
    """Signal sources | مصادر الإشارات"""
    CI = "ci"
    LOCAL = "local"
    MANUAL = "manual"
    API = "api"


@dataclass
class FixOpsConfig:
    """Configuration for FixOps | تكوين FixOps"""
    repo_root: Path = field(default_factory=Path.cwd)
    artifacts_dir: Optional[Path] = None
    output_dir: Path = field(default_factory=lambda: Path.cwd() / ".fixops")
    dry_run: bool = False
    max_files_changed: int = 20
    enable_auto_fix: bool = True
    enable_audit: bool = True
    policy_path: Optional[Path] = None

    # Analysis settings
    analyze_python: bool = True
    analyze_typescript: bool = True
    analyze_dart: bool = False

    # Fix strategies
    fix_strategy: str = "safe"  # "minimal", "safe", "comprehensive"

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class FixRecommendation:
    """Single fix recommendation | توصية إصلاح واحدة"""
    id: str
    priority: str  # "critical", "high", "medium", "low"
    category: str  # "bug", "security", "style", "performance"
    title: str
    title_ar: str
    description: str
    description_ar: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    tool: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "priority": self.priority,
            "category": self.category,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggested_fix": self.suggested_fix,
            "auto_fixable": self.auto_fixable,
            "tool": self.tool,
            "confidence": self.confidence,
        }


@dataclass
class FixOpsSummary:
    """Summary of FixOps run | ملخص تشغيل FixOps"""
    id: str
    version: str = "1.0"
    repo_root: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "running"  # "running", "completed", "failed"

    # Signals
    ci_signals: list[dict[str, Any]] = field(default_factory=list)
    local_signals: list[dict[str, Any]] = field(default_factory=list)

    # Analysis results
    total_issues: int = 0
    issues_by_severity: dict[str, int] = field(default_factory=dict)
    issues_by_category: dict[str, int] = field(default_factory=dict)

    # Recommendations
    recommendations: list[FixRecommendation] = field(default_factory=list)

    # Actions taken
    fixes_applied: int = 0
    fixes_failed: int = 0
    files_modified: list[str] = field(default_factory=list)

    # Metadata
    config: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "repo_root": self.repo_root,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "signals": {
                "ci": self.ci_signals,
                "local": self.local_signals,
            },
            "analysis": {
                "total_issues": self.total_issues,
                "by_severity": self.issues_by_severity,
                "by_category": self.issues_by_category,
            },
            "recommendations": [r.to_dict() for r in self.recommendations],
            "actions": {
                "fixes_applied": self.fixes_applied,
                "fixes_failed": self.fixes_failed,
                "files_modified": self.files_modified,
            },
            "config": self.config,
            "errors": self.errors,
        }


class FixOpsOrchestrator:
    """
    Main orchestrator for FixOps operations.
    المنسق الرئيسي لعمليات FixOps

    Workflow:
    1. Collect signals (CI, local, manual)
    2. Analyze issues and prioritize
    3. Generate fix recommendations
    4. Apply fixes (if enabled)
    5. Generate summary report
    """

    def __init__(self, config: Optional[FixOpsConfig] = None):
        self.config = config or FixOpsConfig()
        self.signal_collector = SignalCollector(self.config.repo_root)
        self._summary: Optional[FixOpsSummary] = None

    async def run(
        self,
        paths: Optional[list[str]] = None,
        sources: Optional[list[SignalSource]] = None,
    ) -> FixOpsSummary:
        """
        Run complete FixOps workflow.
        تشغيل سير عمل FixOps الكامل

        Args:
            paths: Specific paths to analyze
            sources: Signal sources to use

        Returns:
            FixOpsSummary with results
        """
        run_id = str(uuid.uuid4())[:8]
        sources = sources or [SignalSource.LOCAL]

        self._summary = FixOpsSummary(
            id=run_id,
            repo_root=str(self.config.repo_root),
            config={
                "dry_run": self.config.dry_run,
                "fix_strategy": self.config.fix_strategy,
                "max_files_changed": self.config.max_files_changed,
            },
        )

        logger.info(
            "Starting FixOps run",
            run_id=run_id,
            sources=[s.value for s in sources],
        )

        try:
            # Step 1: Collect signals
            await self._collect_signals(sources, paths)

            # Step 2: Analyze and prioritize
            await self._analyze_issues()

            # Step 3: Generate recommendations
            await self._generate_recommendations()

            # Step 4: Apply fixes (if enabled)
            if self.config.enable_auto_fix and not self.config.dry_run:
                await self._apply_fixes()

            # Step 5: Finalize
            self._summary.status = "completed"
            self._summary.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            logger.error("FixOps run failed", error=str(e))
            self._summary.status = "failed"
            self._summary.errors.append(str(e))
            self._summary.completed_at = datetime.now(timezone.utc)

        # Save summary
        await self._save_summary()

        return self._summary

    async def _collect_signals(
        self,
        sources: list[SignalSource],
        paths: Optional[list[str]],
    ) -> None:
        """Collect signals from specified sources"""
        logger.info("Collecting signals", sources=[s.value for s in sources])

        if SignalSource.CI in sources:
            ci_signals = self.signal_collector.collect_ci_signals(
                self.config.artifacts_dir
            )
            self._summary.ci_signals = [s.to_dict() for s in ci_signals]

        if SignalSource.LOCAL in sources:
            local_signals = self.signal_collector.collect_local_signals(paths)
            self._summary.local_signals = [s.to_dict() for s in local_signals]

    async def _analyze_issues(self) -> None:
        """Analyze collected issues"""
        logger.info("Analyzing issues")

        total_issues = 0
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        by_category = {"bug": 0, "security": 0, "style": 0, "performance": 0}

        # Analyze local signals
        for signal_dict in self._summary.local_signals:
            issues = signal_dict.get("issues", [])
            total_issues += len(issues)

            tool = signal_dict.get("tool", "")

            for issue in issues:
                # Determine severity
                severity = self._classify_severity(issue, tool)
                by_severity[severity] = by_severity.get(severity, 0) + 1

                # Determine category
                category = self._classify_category(issue, tool)
                by_category[category] = by_category.get(category, 0) + 1

        self._summary.total_issues = total_issues
        self._summary.issues_by_severity = by_severity
        self._summary.issues_by_category = by_category

    def _classify_severity(self, issue: dict, tool: str) -> str:
        """Classify issue severity"""
        if tool == "bandit":
            severity = issue.get("issue_severity", "").lower()
            if severity == "high":
                return "critical"
            elif severity == "medium":
                return "high"
            return "medium"

        if tool == "ruff":
            code = issue.get("code", "")
            if code.startswith("S"):  # Security
                return "high"
            if code.startswith("E"):  # Error
                return "medium"
            return "low"

        return "medium"

    def _classify_category(self, issue: dict, tool: str) -> str:
        """Classify issue category"""
        if tool == "bandit":
            return "security"

        if tool == "ruff":
            code = issue.get("code", "")
            if code.startswith("S"):
                return "security"
            if code.startswith("E") or code.startswith("F"):
                return "bug"
            if code.startswith("W"):
                return "style"
            if code.startswith("B"):
                return "bug"
            return "style"

        if tool == "mypy":
            return "bug"

        return "style"

    async def _generate_recommendations(self) -> None:
        """Generate fix recommendations"""
        logger.info("Generating recommendations")

        recommendations = []

        # Process local signals
        for signal_dict in self._summary.local_signals:
            tool = signal_dict.get("tool", "")
            issues = signal_dict.get("issues", [])

            for i, issue in enumerate(issues[:50]):  # Limit to top 50
                rec = self._create_recommendation(issue, tool, i)
                if rec:
                    recommendations.append(rec)

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))

        self._summary.recommendations = recommendations[:100]  # Limit to top 100

    def _create_recommendation(
        self,
        issue: dict,
        tool: str,
        index: int,
    ) -> Optional[FixRecommendation]:
        """Create a fix recommendation from an issue"""
        try:
            severity = self._classify_severity(issue, tool)
            category = self._classify_category(issue, tool)

            # Extract file info
            file_path = issue.get("filename") or issue.get("file")
            line = issue.get("line") or issue.get("location", {}).get("row")
            message = issue.get("message") or issue.get("issue_text") or str(issue)

            # Determine if auto-fixable
            auto_fixable = False
            if tool == "ruff":
                auto_fixable = issue.get("fix", {}).get("applicability") == "safe"

            return FixRecommendation(
                id=f"{tool}-{index:04d}",
                priority=severity,
                category=category,
                title=message[:100],
                title_ar=f"مشكلة من {tool}",
                description=message,
                description_ar=f"تم اكتشاف مشكلة بواسطة {tool}",
                file_path=file_path,
                line_number=line,
                auto_fixable=auto_fixable,
                tool=tool,
                confidence=0.8 if auto_fixable else 0.5,
            )
        except Exception as e:
            logger.warning("Failed to create recommendation", error=str(e))
            return None

    async def _apply_fixes(self) -> None:
        """Apply auto-fixable fixes"""
        logger.info("Applying fixes", strategy=self.config.fix_strategy)

        auto_fixable = [
            r for r in self._summary.recommendations
            if r.auto_fixable and r.priority in ("critical", "high")
        ]

        if not auto_fixable:
            logger.info("No auto-fixable issues found")
            return

        # Apply Ruff fixes
        ruff_fixes = [r for r in auto_fixable if r.tool == "ruff"]
        if ruff_fixes:
            await self._apply_ruff_fixes()

    async def _apply_ruff_fixes(self) -> None:
        """Apply Ruff auto-fixes"""
        import subprocess

        try:
            result = subprocess.run(
                ["ruff", "check", "--fix", str(self.config.repo_root)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.config.repo_root,
            )

            if result.returncode == 0:
                self._summary.fixes_applied += 1
                logger.info("Ruff fixes applied")
            else:
                self._summary.fixes_failed += 1
                logger.warning("Ruff fixes failed", stderr=result.stderr[:500])

        except Exception as e:
            self._summary.fixes_failed += 1
            self._summary.errors.append(f"Ruff fix failed: {e}")

    async def _save_summary(self) -> None:
        """Save summary to file"""
        output_file = self.config.output_dir / f"fixops_summary_{self._summary.id}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self._summary.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info("Summary saved", path=str(output_file))

    def generate_kimi_request(self) -> dict[str, Any]:
        """
        Generate Kimi-compatible request for LLM processing.
        توليد طلب متوافق مع Kimi للمعالجة بواسطة LLM
        """
        if not self._summary:
            return {}

        return {
            "version": "1.0",
            "mode": "patch-only",
            "policy_path": str(self.config.policy_path) if self.config.policy_path else None,
            "constraints": {
                "no_network": True,
                "no_secrets": True,
                "max_files_changed": self.config.max_files_changed,
                "forbidden_globs": ["*.key", "*.pem", ".env", "*.secret"],
            },
            "context": {
                "repo_root": str(self.config.repo_root),
                "run_id": self._summary.id,
            },
            "questions": [
                {
                    "id": "fix-critical",
                    "priority": "HIGH",
                    "task": f"Fix the {self._summary.issues_by_severity.get('critical', 0)} critical issues",
                },
                {
                    "id": "fix-security",
                    "priority": "HIGH",
                    "task": f"Fix the {self._summary.issues_by_category.get('security', 0)} security issues",
                },
                {
                    "id": "fix-bugs",
                    "priority": "MEDIUM",
                    "task": f"Fix the {self._summary.issues_by_category.get('bug', 0)} bug issues",
                },
            ],
            "rag": {
                "top_k": 12,
                "include_paths": True,
            },
            "summary": {
                "total_issues": self._summary.total_issues,
                "by_severity": self._summary.issues_by_severity,
                "by_category": self._summary.issues_by_category,
                "recommendations_count": len(self._summary.recommendations),
            },
        }


async def run_fixops(
    repo_root: Optional[Path] = None,
    dry_run: bool = False,
    fix_strategy: str = "safe",
) -> FixOpsSummary:
    """
    Convenience function to run FixOps.
    دالة مساعدة لتشغيل FixOps
    """
    config = FixOpsConfig(
        repo_root=repo_root or Path.cwd(),
        dry_run=dry_run,
        fix_strategy=fix_strategy,
    )
    orchestrator = FixOpsOrchestrator(config)
    return await orchestrator.run()
