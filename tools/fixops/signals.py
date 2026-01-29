"""
Signal Collection for FixOps
جمع الإشارات لـ FixOps

Collects signals from CI/CD, local environment, and external tools.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CISignal:
    """Signal from CI/CD system | إشارة من نظام CI/CD"""
    source: str  # "github_actions", "gitlab_ci", "jenkins"
    job_id: Optional[str] = None
    workflow: Optional[str] = None
    status: str = "unknown"
    artifacts: list[str] = field(default_factory=list)
    logs: Optional[str] = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "job_id": self.job_id,
            "workflow": self.workflow,
            "status": self.status,
            "artifacts": self.artifacts,
            "errors": self.errors,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LocalSignal:
    """Signal from local environment | إشارة من البيئة المحلية"""
    tool: str  # "ruff", "eslint", "mypy", "bandit"
    file_path: Optional[str] = None
    issues: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    exit_code: int = 0
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "file_path": self.file_path,
            "issues": self.issues,
            "metrics": self.metrics,
            "execution_time_ms": self.execution_time_ms,
            "exit_code": self.exit_code,
            "timestamp": self.timestamp.isoformat(),
        }


class SignalCollector:
    """
    Collects signals from various sources for FixOps.
    يجمع الإشارات من مصادر مختلفة لـ FixOps
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path.cwd()
        self._ci_signals: list[CISignal] = []
        self._local_signals: list[LocalSignal] = []

    def collect_ci_signals(self, artifacts_dir: Optional[Path] = None) -> list[CISignal]:
        """
        Collect signals from CI artifacts.
        جمع الإشارات من مخرجات CI
        """
        signals = []

        # Detect CI environment
        if os.getenv("GITHUB_ACTIONS"):
            signal = self._collect_github_actions_signal(artifacts_dir)
            if signal:
                signals.append(signal)

        elif os.getenv("GITLAB_CI"):
            signal = self._collect_gitlab_ci_signal(artifacts_dir)
            if signal:
                signals.append(signal)

        elif os.getenv("JENKINS_URL"):
            signal = self._collect_jenkins_signal(artifacts_dir)
            if signal:
                signals.append(signal)

        self._ci_signals.extend(signals)
        return signals

    def _collect_github_actions_signal(self, artifacts_dir: Optional[Path]) -> Optional[CISignal]:
        """Collect GitHub Actions signal"""
        try:
            signal = CISignal(
                source="github_actions",
                job_id=os.getenv("GITHUB_RUN_ID"),
                workflow=os.getenv("GITHUB_WORKFLOW"),
                status=os.getenv("GITHUB_ACTION_STATUS", "unknown"),
                metadata={
                    "repository": os.getenv("GITHUB_REPOSITORY"),
                    "ref": os.getenv("GITHUB_REF"),
                    "sha": os.getenv("GITHUB_SHA"),
                    "actor": os.getenv("GITHUB_ACTOR"),
                    "event_name": os.getenv("GITHUB_EVENT_NAME"),
                },
            )

            # Collect artifacts
            if artifacts_dir and artifacts_dir.exists():
                artifacts = list(artifacts_dir.rglob("*"))
                signal.artifacts = [str(a.relative_to(artifacts_dir)) for a in artifacts if a.is_file()][:100]

            return signal
        except Exception as e:
            logger.warning("Failed to collect GitHub Actions signal", error=str(e))
            return None

    def _collect_gitlab_ci_signal(self, artifacts_dir: Optional[Path]) -> Optional[CISignal]:
        """Collect GitLab CI signal"""
        try:
            return CISignal(
                source="gitlab_ci",
                job_id=os.getenv("CI_JOB_ID"),
                workflow=os.getenv("CI_PIPELINE_NAME"),
                status=os.getenv("CI_JOB_STATUS", "unknown"),
                metadata={
                    "project": os.getenv("CI_PROJECT_NAME"),
                    "ref": os.getenv("CI_COMMIT_REF_NAME"),
                    "sha": os.getenv("CI_COMMIT_SHA"),
                },
            )
        except Exception as e:
            logger.warning("Failed to collect GitLab CI signal", error=str(e))
            return None

    def _collect_jenkins_signal(self, artifacts_dir: Optional[Path]) -> Optional[CISignal]:
        """Collect Jenkins signal"""
        try:
            return CISignal(
                source="jenkins",
                job_id=os.getenv("BUILD_NUMBER"),
                workflow=os.getenv("JOB_NAME"),
                status="unknown",
                metadata={
                    "build_url": os.getenv("BUILD_URL"),
                    "workspace": os.getenv("WORKSPACE"),
                },
            )
        except Exception as e:
            logger.warning("Failed to collect Jenkins signal", error=str(e))
            return None

    def collect_local_signals(self, paths: Optional[list[str]] = None) -> list[LocalSignal]:
        """
        Collect signals from local analysis tools.
        جمع الإشارات من أدوات التحليل المحلية
        """
        signals = []
        target_paths = paths or [str(self.repo_root)]

        # Run Ruff
        ruff_signal = self._run_ruff(target_paths)
        if ruff_signal:
            signals.append(ruff_signal)

        # Run ESLint (if available)
        eslint_signal = self._run_eslint(target_paths)
        if eslint_signal:
            signals.append(eslint_signal)

        # Run Mypy
        mypy_signal = self._run_mypy(target_paths)
        if mypy_signal:
            signals.append(mypy_signal)

        # Run Bandit (security)
        bandit_signal = self._run_bandit(target_paths)
        if bandit_signal:
            signals.append(bandit_signal)

        self._local_signals.extend(signals)
        return signals

    def _run_ruff(self, paths: list[str]) -> Optional[LocalSignal]:
        """Run Ruff linter"""
        import time
        start = time.time()

        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json", *paths],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="ruff",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
                stdout=result.stdout[:5000] if result.stdout else None,
                stderr=result.stderr[:1000] if result.stderr else None,
            )
        except FileNotFoundError:
            logger.debug("Ruff not installed")
            return None
        except Exception as e:
            logger.warning("Ruff failed", error=str(e))
            return None

    def _run_eslint(self, paths: list[str]) -> Optional[LocalSignal]:
        """Run ESLint"""
        import time
        start = time.time()

        try:
            result = subprocess.run(
                ["npx", "eslint", "--format=json", *paths],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for file_result in data:
                        for msg in file_result.get("messages", []):
                            issues.append({
                                "file": file_result.get("filePath"),
                                "line": msg.get("line"),
                                "column": msg.get("column"),
                                "message": msg.get("message"),
                                "severity": msg.get("severity"),
                                "ruleId": msg.get("ruleId"),
                            })
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="eslint",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("ESLint not installed")
            return None
        except Exception as e:
            logger.warning("ESLint failed", error=str(e))
            return None

    def _run_mypy(self, paths: list[str]) -> Optional[LocalSignal]:
        """Run Mypy type checker"""
        import time
        start = time.time()

        try:
            result = subprocess.run(
                ["mypy", "--no-error-summary", "--no-pretty", *paths],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ": error:" in line or ": warning:" in line:
                        issues.append({"raw": line})

            return LocalSignal(
                tool="mypy",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Mypy not installed")
            return None
        except Exception as e:
            logger.warning("Mypy failed", error=str(e))
            return None

    def _run_bandit(self, paths: list[str]) -> Optional[LocalSignal]:
        """Run Bandit security scanner"""
        import time
        start = time.time()

        try:
            result = subprocess.run(
                ["bandit", "-r", "-f", "json", *paths],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    issues = data.get("results", [])
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="bandit",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "high_severity": len([i for i in issues if i.get("issue_severity") == "HIGH"]),
                    "medium_severity": len([i for i in issues if i.get("issue_severity") == "MEDIUM"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Bandit not installed")
            return None
        except Exception as e:
            logger.warning("Bandit failed", error=str(e))
            return None

    def get_all_signals(self) -> dict[str, Any]:
        """Get all collected signals"""
        return {
            "ci_signals": [s.to_dict() for s in self._ci_signals],
            "local_signals": [s.to_dict() for s in self._local_signals],
            "summary": {
                "ci_count": len(self._ci_signals),
                "local_count": len(self._local_signals),
                "total_issues": sum(
                    len(s.issues) for s in self._local_signals
                ),
            },
        }

    def clear(self) -> None:
        """Clear collected signals"""
        self._ci_signals.clear()
        self._local_signals.clear()
