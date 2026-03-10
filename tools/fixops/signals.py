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
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CISignal:
    """Signal from CI/CD system | إشارة من نظام CI/CD"""

    source: str  # "github_actions", "gitlab_ci", "jenkins"
    job_id: str | None = None
    workflow: str | None = None
    status: str = "unknown"
    artifacts: list[str] = field(default_factory=list)
    logs: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

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
    file_path: str | None = None
    issues: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    exit_code: int = 0
    stdout: str | None = None
    stderr: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

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

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path.cwd()
        self._ci_signals: list[CISignal] = []
        self._local_signals: list[LocalSignal] = []

    def collect_ci_signals(self, artifacts_dir: Path | None = None) -> list[CISignal]:
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

    def _collect_github_actions_signal(self, artifacts_dir: Path | None) -> CISignal | None:
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

    def _collect_gitlab_ci_signal(self, artifacts_dir: Path | None) -> CISignal | None:
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

    def _collect_jenkins_signal(self, artifacts_dir: Path | None) -> CISignal | None:
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

    def collect_local_signals(self, paths: list[str] | None = None) -> list[LocalSignal]:
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

        # Run Semgrep (advanced security)
        semgrep_signal = self._run_semgrep(target_paths)
        if semgrep_signal:
            signals.append(semgrep_signal)

        # Run Pylint (advanced Python analysis)
        pylint_signal = self._run_pylint(target_paths)
        if pylint_signal:
            signals.append(pylint_signal)

        # Run TypeScript compiler check
        typescript_signal = self._run_typescript(target_paths)
        if typescript_signal:
            signals.append(typescript_signal)

        # Run Dart/Flutter analysis
        dart_signal = self._run_dart_analyze(target_paths)
        if dart_signal:
            signals.append(dart_signal)

        flutter_signal = self._run_flutter_analyze(target_paths)
        if flutter_signal:
            signals.append(flutter_signal)

        # Run package vulnerability audits
        npm_audit_signal = self._run_npm_audit(target_paths)
        if npm_audit_signal:
            signals.append(npm_audit_signal)

        pip_audit_signal = self._run_pip_audit(target_paths)
        if pip_audit_signal:
            signals.append(pip_audit_signal)

        # Run OpenAPI/Swagger validation
        openapi_signal = self._run_openapi_validator(target_paths)
        if openapi_signal:
            signals.append(openapi_signal)

        # Run Docker/compose validation
        docker_signal = self._run_docker_lint(target_paths)
        if docker_signal:
            signals.append(docker_signal)

        # Run Kubernetes/Helm validation
        k8s_signal = self._run_k8s_lint(target_paths)
        if k8s_signal:
            signals.append(k8s_signal)

        # Run docker-compose validation
        compose_signal = self._run_docker_compose_validation(target_paths)
        if compose_signal:
            signals.append(compose_signal)

        # Run SQL linting
        sql_signal = self._run_sqlfluff(target_paths)
        if sql_signal:
            signals.append(sql_signal)

        # Run Prisma schema validation
        prisma_signal = self._run_prisma_validate(target_paths)
        if prisma_signal:
            signals.append(prisma_signal)

        # Run YAML linting
        yaml_signal = self._run_yaml_lint(target_paths)
        if yaml_signal:
            signals.append(yaml_signal)

        # Run shell script linting
        shell_signal = self._run_shellcheck(target_paths)
        if shell_signal:
            signals.append(shell_signal)

        self._local_signals.extend(signals)
        return signals

    def _run_openapi_validator(self, paths: list[str]) -> LocalSignal | None:
        """Validate OpenAPI/Swagger specs | فحص مواصفات OpenAPI"""
        import time

        start = time.time()

        # Check for OpenAPI files
        openapi_files = []
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                openapi_files.extend(path_obj.glob("**/openapi*.yaml"))
                openapi_files.extend(path_obj.glob("**/openapi*.json"))
                openapi_files.extend(path_obj.glob("**/swagger*.yaml"))
                openapi_files.extend(path_obj.glob("**/swagger*.json"))

        if not openapi_files:
            return None

        issues = []
        for spec_file in openapi_files[:10]:  # Limit to 10 files
            try:
                result = subprocess.run(
                    ["npx", "swagger-cli", "validate", str(spec_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.repo_root,
                )
                if result.returncode != 0:
                    issues.append(
                        {
                            "file": str(spec_file),
                            "message": result.stderr[:500] if result.stderr else "Validation failed",
                        }
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return LocalSignal(
            tool="openapi_validator",
            issues=issues,
            metrics={"total_issues": len(issues)},
            execution_time_ms=(time.time() - start) * 1000,
            exit_code=1 if issues else 0,
        )

    def _run_docker_lint(self, paths: list[str]) -> LocalSignal | None:
        """Lint Dockerfiles with hadolint | فحص Dockerfile بـ hadolint"""
        import time

        start = time.time()

        # Find Dockerfiles
        dockerfiles = []
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                dockerfiles.extend(path_obj.glob("**/Dockerfile"))
                dockerfiles.extend(path_obj.glob("**/Dockerfile.*"))

        if not dockerfiles:
            return None

        try:
            issues = []
            for dockerfile in dockerfiles[:20]:  # Limit to 20 files
                result = subprocess.run(
                    ["hadolint", "--format", "json", str(dockerfile)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.repo_root,
                )
                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        for item in data:
                            issues.append(
                                {
                                    "file": str(dockerfile),
                                    "line": item.get("line"),
                                    "code": item.get("code"),
                                    "message": item.get("message"),
                                    "level": item.get("level"),
                                }
                            )
                    except json.JSONDecodeError:
                        pass

            return LocalSignal(
                tool="hadolint",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "errors": len([i for i in issues if i.get("level") == "error"]),
                    "warnings": len([i for i in issues if i.get("level") == "warning"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=1 if issues else 0,
            )
        except FileNotFoundError:
            logger.debug("hadolint not installed")
            return None
        except Exception as e:
            logger.warning("hadolint failed", error=str(e))
            return None

    def _run_k8s_lint(self, paths: list[str]) -> LocalSignal | None:
        """Lint Kubernetes manifests | فحص ملفات Kubernetes"""
        import time

        start = time.time()

        # Check for Helm charts or K8s manifests
        helm_charts = list(self.repo_root.glob("helm/**/Chart.yaml"))
        k8s_manifests = list(self.repo_root.glob("**/k8s/**/*.yaml"))

        if not helm_charts and not k8s_manifests:
            return None

        issues = []

        # Helm lint
        for chart_dir in [chart.parent for chart in helm_charts[:5]]:
            try:
                result = subprocess.run(
                    ["helm", "lint", str(chart_dir)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.repo_root,
                )
                if result.returncode != 0:
                    for line in (result.stdout + result.stderr).split("\n"):
                        if "[ERROR]" in line or "[WARNING]" in line:
                            issues.append(
                                {
                                    "file": str(chart_dir),
                                    "message": line,
                                    "tool": "helm",
                                }
                            )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # kubeval for manifests
        for manifest in k8s_manifests[:10]:
            try:
                result = subprocess.run(
                    ["kubeval", str(manifest)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.repo_root,
                )
                if result.returncode != 0:
                    for line in result.stderr.split("\n"):
                        if line.strip():
                            issues.append(
                                {
                                    "file": str(manifest),
                                    "message": line,
                                    "tool": "kubeval",
                                }
                            )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return LocalSignal(
            tool="k8s_lint",
            issues=issues,
            metrics={"total_issues": len(issues)},
            execution_time_ms=(time.time() - start) * 1000,
            exit_code=1 if issues else 0,
        )

    def _run_docker_compose_validation(self, paths: list[str]) -> LocalSignal | None:
        """Validate docker-compose files | فحص ملفات docker-compose"""
        import time

        start = time.time()

        # Find docker-compose files
        compose_files = []
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                compose_files.extend(path_obj.glob("**/docker-compose*.yml"))
                compose_files.extend(path_obj.glob("**/docker-compose*.yaml"))
                compose_files.extend(path_obj.glob("**/compose*.yml"))
                compose_files.extend(path_obj.glob("**/compose*.yaml"))

        if not compose_files:
            return None

        issues = []
        for compose_file in compose_files[:10]:
            try:
                result = subprocess.run(
                    ["docker", "compose", "-f", str(compose_file), "config", "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.repo_root,
                )
                if result.returncode != 0:
                    issues.append(
                        {
                            "file": str(compose_file),
                            "message": result.stderr[:500] if result.stderr else "Validation failed",
                        }
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return LocalSignal(
            tool="docker_compose",
            issues=issues,
            metrics={"total_issues": len(issues)},
            execution_time_ms=(time.time() - start) * 1000,
            exit_code=1 if issues else 0,
        )

    def _run_sqlfluff(self, paths: list[str]) -> LocalSignal | None:
        """Lint SQL files with sqlfluff | فحص ملفات SQL"""
        import time

        start = time.time()

        # Find SQL files
        sql_files = []
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                sql_files.extend(path_obj.glob("**/*.sql"))

        if not sql_files:
            return None

        try:
            result = subprocess.run(
                ["sqlfluff", "lint", "--format", "json", *[str(f) for f in sql_files[:20]]],
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
                        for violation in file_result.get("violations", []):
                            issues.append(
                                {
                                    "file": file_result.get("filepath"),
                                    "line": violation.get("start_line_no"),
                                    "code": violation.get("code"),
                                    "message": violation.get("description"),
                                }
                            )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="sqlfluff",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("sqlfluff not installed")
            return None
        except Exception as e:
            logger.warning("sqlfluff failed", error=str(e))
            return None

    def _run_prisma_validate(self, paths: list[str]) -> LocalSignal | None:
        """Validate Prisma schema | فحص Prisma schema"""
        import time

        start = time.time()

        # Find Prisma schema files
        prisma_schemas = list(self.repo_root.glob("**/prisma/schema.prisma"))

        if not prisma_schemas:
            return None

        issues = []
        for schema in prisma_schemas[:5]:
            try:
                result = subprocess.run(
                    ["npx", "prisma", "validate", "--schema", str(schema)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=schema.parent.parent,
                )
                if result.returncode != 0:
                    issues.append(
                        {
                            "file": str(schema),
                            "message": result.stderr[:500] if result.stderr else "Validation failed",
                        }
                    )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return LocalSignal(
            tool="prisma_validate",
            issues=issues,
            metrics={"total_issues": len(issues)},
            execution_time_ms=(time.time() - start) * 1000,
            exit_code=1 if issues else 0,
        )

    def _run_yaml_lint(self, paths: list[str]) -> LocalSignal | None:
        """Lint YAML files with yamllint | فحص ملفات YAML"""
        import time

        start = time.time()

        try:
            result = subprocess.run(
                ["yamllint", "-f", "parsable", *paths],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line and line.strip():
                        parts = line.split(":")
                        if len(parts) >= 3:
                            issues.append(
                                {
                                    "file": parts[0],
                                    "line": parts[1] if len(parts) > 1 else "",
                                    "message": ":".join(parts[2:]).strip(),
                                }
                            )

            return LocalSignal(
                tool="yamllint",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("yamllint not installed")
            return None
        except Exception as e:
            logger.warning("yamllint failed", error=str(e))
            return None

    def _run_shellcheck(self, paths: list[str]) -> LocalSignal | None:
        """Lint shell scripts with shellcheck | فحص سكريبتات Shell"""
        import time

        start = time.time()

        # Find shell scripts
        shell_scripts = []
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_dir():
                shell_scripts.extend(path_obj.glob("**/*.sh"))
                shell_scripts.extend(path_obj.glob("**/*.bash"))

        if not shell_scripts:
            return None

        try:
            result = subprocess.run(
                ["shellcheck", "--format=json", *[str(f) for f in shell_scripts[:20]]],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        issues.append(
                            {
                                "file": item.get("file"),
                                "line": item.get("line"),
                                "code": item.get("code"),
                                "message": item.get("message"),
                                "level": item.get("level"),
                            }
                        )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="shellcheck",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "errors": len([i for i in issues if i.get("level") == "error"]),
                    "warnings": len([i for i in issues if i.get("level") == "warning"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("shellcheck not installed")
            return None
        except Exception as e:
            logger.warning("shellcheck failed", error=str(e))
            return None

    def _run_semgrep(self, paths: list[str]) -> LocalSignal | None:
        """Run Semgrep security scanner | تشغيل ماسح Semgrep الأمني"""
        import time

        start = time.time()

        try:
            result = subprocess.run(
                ["semgrep", "scan", "--json", "--config=auto", "--quiet", *paths],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data.get("results", []):
                        issues.append(
                            {
                                "file": item.get("path"),
                                "line": item.get("start", {}).get("line"),
                                "message": item.get("extra", {}).get("message"),
                                "severity": item.get("extra", {}).get("severity"),
                                "rule_id": item.get("check_id"),
                            }
                        )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="semgrep",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "high_severity": len([i for i in issues if i.get("severity") == "ERROR"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Semgrep not installed")
            return None
        except Exception as e:
            logger.warning("Semgrep failed", error=str(e))
            return None

    def _run_pylint(self, paths: list[str]) -> LocalSignal | None:
        """Run Pylint for advanced Python analysis | تشغيل Pylint للتحليل المتقدم"""
        import time

        start = time.time()

        # Filter to Python files only
        python_paths = [p for p in paths if p.endswith(".py") or os.path.isdir(p)]
        if not python_paths:
            return None

        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", "--disable=C0114,C0115,C0116", *python_paths],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        issues.append(
                            {
                                "file": item.get("path"),
                                "line": item.get("line"),
                                "message": item.get("message"),
                                "message_id": item.get("message-id"),
                                "symbol": item.get("symbol"),
                                "type": item.get("type"),  # error, warning, convention, refactor
                            }
                        )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="pylint",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "errors": len([i for i in issues if i.get("type") == "error"]),
                    "warnings": len([i for i in issues if i.get("type") == "warning"]),
                    "refactors": len([i for i in issues if i.get("type") == "refactor"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Pylint not installed")
            return None
        except Exception as e:
            logger.warning("Pylint failed", error=str(e))
            return None

    def _run_dart_analyze(self, paths: list[str]) -> LocalSignal | None:
        """Run Dart analyzer for Flutter | تشغيل محلل Dart لـ Flutter"""
        import time

        start = time.time()

        # Check for Dart/Flutter project
        pubspec = self.repo_root / "pubspec.yaml"
        if not pubspec.exists():
            return None

        try:
            result = subprocess.run(
                ["dart", "analyze", "--format=json", *paths],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data.get("diagnostics", []):
                        issues.append(
                            {
                                "file": item.get("location", {}).get("file"),
                                "line": item.get("location", {}).get("startLine"),
                                "message": item.get("problemMessage"),
                                "code": item.get("code"),
                                "severity": item.get("severity"),
                                "correction": item.get("correctionMessage"),
                            }
                        )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="dart_analyze",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "errors": len([i for i in issues if i.get("severity") == "ERROR"]),
                    "warnings": len([i for i in issues if i.get("severity") == "WARNING"]),
                    "infos": len([i for i in issues if i.get("severity") == "INFO"]),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Dart SDK not installed")
            return None
        except Exception as e:
            logger.warning("Dart analyze failed", error=str(e))
            return None

    def _run_flutter_analyze(self, paths: list[str]) -> LocalSignal | None:
        """Run Flutter analyzer | تشغيل محلل Flutter"""
        import time

        start = time.time()

        try:
            result = subprocess.run(
                ["flutter", "analyze", "--no-pub"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                # Parse Flutter analyze output
                for line in result.stdout.strip().split("\n"):
                    if " - " in line and ("info" in line or "warning" in line or "error" in line):
                        parts = line.split(" - ")
                        if len(parts) >= 2:
                            issues.append(
                                {
                                    "raw": line,
                                    "message": parts[-1] if len(parts) > 1 else line,
                                }
                            )

            return LocalSignal(
                tool="flutter_analyze",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("Flutter not installed")
            return None
        except Exception as e:
            logger.warning("Flutter analyze failed", error=str(e))
            return None

    def _run_typescript(self, paths: list[str]) -> LocalSignal | None:
        """Run TypeScript compiler check | تشغيل فحص مترجم TypeScript"""
        import time

        start = time.time()

        # Check for TypeScript project
        tsconfig = self.repo_root / "tsconfig.json"
        if not tsconfig.exists():
            return None

        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--pretty", "false"],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ": error TS" in line or ": warning TS" in line:
                        issues.append({"raw": line})

            return LocalSignal(
                tool="typescript",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("TypeScript not installed")
            return None
        except Exception as e:
            logger.warning("TypeScript check failed", error=str(e))
            return None

    def _run_npm_audit(self, paths: list[str]) -> LocalSignal | None:
        """Run npm audit for package vulnerabilities | تشغيل تدقيق npm للثغرات"""
        import time

        start = time.time()

        # Check for npm project
        package_json = self.repo_root / "package.json"
        if not package_json.exists():
            return None

        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.repo_root,
            )

            issues = []
            metrics = {}
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    vulnerabilities = data.get("vulnerabilities", {})
                    for pkg_name, vuln_data in vulnerabilities.items():
                        issues.append(
                            {
                                "package": pkg_name,
                                "severity": vuln_data.get("severity"),
                                "via": vuln_data.get("via"),
                                "fixAvailable": vuln_data.get("fixAvailable"),
                            }
                        )
                    metrics = data.get("metadata", {}).get("vulnerabilities", {})
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="npm_audit",
                issues=issues,
                metrics={
                    "total_issues": len(issues),
                    "critical": metrics.get("critical", 0),
                    "high": metrics.get("high", 0),
                    "moderate": metrics.get("moderate", 0),
                    "low": metrics.get("low", 0),
                },
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("npm not installed")
            return None
        except Exception as e:
            logger.warning("npm audit failed", error=str(e))
            return None

    def _run_pip_audit(self, paths: list[str]) -> LocalSignal | None:
        """Run pip-audit for Python package vulnerabilities | تشغيل تدقيق pip للثغرات"""
        import time

        start = time.time()

        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=180,
                cwd=self.repo_root,
            )

            issues = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for vuln in data:
                        issues.append(
                            {
                                "package": vuln.get("name"),
                                "version": vuln.get("version"),
                                "vulns": vuln.get("vulns", []),
                            }
                        )
                except json.JSONDecodeError:
                    pass

            return LocalSignal(
                tool="pip_audit",
                issues=issues,
                metrics={"total_issues": len(issues)},
                execution_time_ms=(time.time() - start) * 1000,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            logger.debug("pip-audit not installed")
            return None
        except Exception as e:
            logger.warning("pip-audit failed", error=str(e))
            return None

    def _run_ruff(self, paths: list[str]) -> LocalSignal | None:
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

    def _run_eslint(self, paths: list[str]) -> LocalSignal | None:
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
                            issues.append(
                                {
                                    "file": file_result.get("filePath"),
                                    "line": msg.get("line"),
                                    "column": msg.get("column"),
                                    "message": msg.get("message"),
                                    "severity": msg.get("severity"),
                                    "ruleId": msg.get("ruleId"),
                                }
                            )
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

    def _run_mypy(self, paths: list[str]) -> LocalSignal | None:
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

    def _run_bandit(self, paths: list[str]) -> LocalSignal | None:
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
                "total_issues": sum(len(s.issues) for s in self._local_signals),
            },
        }

    def clear(self) -> None:
        """Clear collected signals"""
        self._ci_signals.clear()
        self._local_signals.clear()
