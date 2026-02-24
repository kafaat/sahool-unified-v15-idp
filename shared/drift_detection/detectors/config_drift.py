"""
Config Drift Detector
كاشف انحراف التكوين

Detects configuration drift across:
- Environment variables (.env vs .env.example vs code usage)
- Docker Compose (generated vs actual)
- Helm values (generated vs deployed)
- Service ports (governance/services.yaml vs actual configs)
- CORS/Cookie/Domain settings per environment
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)


class ConfigDriftDetector(BaseDriftDetector):
    """
    Detects configuration drift between desired state (Git) and actual state.
    يكتشف انحراف التكوين بين الحالة المطلوبة والحالة الفعلية.
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.CONFIG

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_env_drift()
        await self._check_service_ports_drift()
        await self._check_docker_compose_drift()
        await self._check_helm_drift()
        await self._check_cors_domain_drift()

        return self.results

    async def _check_env_drift(self) -> None:
        """Check env variables used in code vs documented in .env.example."""
        root = Path(self.working_dir)
        env_example = root / ".env.example"

        if not env_example.exists():
            self.add_result(DriftResult(
                category=DriftCategory.CONFIG,
                severity=DriftSeverity.MEDIUM,
                source="env_drift",
                description=".env.example file not found",
                description_ar="ملف .env.example غير موجود",
                file_path=str(env_example),
                auto_fixable=False,
                remediation_hint="Create .env.example with all required environment variables",
                remediation_hint_ar="أنشئ ملف .env.example بجميع متغيرات البيئة المطلوبة",
            ))
            return

        documented = _parse_env_file(env_example)
        used = await _scan_env_usage(root)

        # Variables used but not documented
        missing = used - documented
        for var in sorted(missing):
            self.add_result(DriftResult(
                category=DriftCategory.CONFIG,
                severity=DriftSeverity.HIGH,
                source="env_drift",
                expected=f"{var} documented in .env.example",
                actual=f"{var} used in code but NOT documented",
                description=f"ENV var '{var}' used in code but missing from .env.example",
                description_ar=f"متغير البيئة '{var}' مستخدم في الكود لكنه مفقود من .env.example",
                file_path=str(env_example),
                auto_fixable=True,
                remediation_hint=f"Add {var}=<value> to .env.example",
                remediation_hint_ar=f"أضف {var}=<value> إلى .env.example",
            ))

    async def _check_service_ports_drift(self) -> None:
        """Check service ports in governance/services.yaml vs docker-compose."""
        root = Path(self.working_dir)
        services_yaml = root / "governance" / "services.yaml"
        compose_file = root / "docker-compose.yml"

        if not services_yaml.exists() or not compose_file.exists():
            return

        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed, skipping port drift check")
            return

        try:
            with open(services_yaml) as f:
                governance = yaml.safe_load(f)
            with open(compose_file) as f:
                compose = yaml.safe_load(f)
        except Exception as e:
            logger.warning("Failed to parse YAML files: %s", e)
            return

        if not governance or not compose:
            return

        # Extract ports from governance
        gov_ports: dict[str, int] = {}
        services = governance.get("services", [])
        if isinstance(services, list):
            for svc in services:
                name = svc.get("name", "")
                port = svc.get("port")
                if name and port:
                    gov_ports[name] = int(port)
        elif isinstance(services, dict):
            for name, svc in services.items():
                if isinstance(svc, dict):
                    port = svc.get("port")
                    if port:
                        gov_ports[name] = int(port)

        # Extract ports from docker-compose
        compose_ports: dict[str, list[str]] = {}
        compose_services = compose.get("services", {})
        if isinstance(compose_services, dict):
            for name, svc_conf in compose_services.items():
                if isinstance(svc_conf, dict) and "ports" in svc_conf:
                    compose_ports[name] = svc_conf["ports"]

        # Check for port mismatches
        for svc_name, gov_port in gov_ports.items():
            compose_key = svc_name.replace("-", "_")
            if compose_key in compose_ports:
                port_strs = compose_ports[compose_key]
                for ps in port_strs:
                    ps_str = str(ps)
                    if ":" in ps_str:
                        host_port = ps_str.split(":")[0]
                        try:
                            if int(host_port) != gov_port:
                                self.add_result(DriftResult(
                                    category=DriftCategory.CONFIG,
                                    severity=DriftSeverity.HIGH,
                                    source="port_drift",
                                    expected=f"Port {gov_port} (governance/services.yaml)",
                                    actual=f"Port {host_port} (docker-compose.yml)",
                                    description=f"Service '{svc_name}' port mismatch: governance={gov_port}, compose={host_port}",
                                    description_ar=f"عدم تطابق منفذ الخدمة '{svc_name}': الحوكمة={gov_port}، التركيب={host_port}",
                                    service_name=svc_name,
                                    auto_fixable=True,
                                    remediation_hint=f"Update docker-compose.yml port for {svc_name} to {gov_port}",
                                ))
                        except ValueError:
                            pass

    async def _check_docker_compose_drift(self) -> None:
        """Check if generated docker-compose is in sync with services.yaml."""
        root = Path(self.working_dir)
        generated = root / "docker" / "compose.generated.yml"
        services_yaml = root / "governance" / "services.yaml"

        if not generated.exists():
            return

        if not services_yaml.exists():
            return

        # Check file modification times
        gen_mtime = generated.stat().st_mtime
        svc_mtime = services_yaml.stat().st_mtime

        if svc_mtime > gen_mtime:
            self.add_result(DriftResult(
                category=DriftCategory.CONFIG,
                severity=DriftSeverity.HIGH,
                source="compose_drift",
                expected="Generated compose in sync with services.yaml",
                actual="services.yaml modified after compose generation",
                description="Docker Compose generated file is stale - services.yaml was modified after last generation",
                description_ar="ملف Docker Compose المُنشأ قديم - تم تعديل services.yaml بعد آخر إنشاء",
                file_path=str(generated),
                auto_fixable=True,
                remediation_hint="Run 'make generate-infra' to regenerate",
                remediation_hint_ar="شغّل 'make generate-infra' لإعادة الإنشاء",
            ))

    async def _check_helm_drift(self) -> None:
        """Check Helm values drift."""
        root = Path(self.working_dir)
        generated = root / "helm" / "sahool" / "values.generated.yaml"
        services_yaml = root / "governance" / "services.yaml"

        if not generated.exists() or not services_yaml.exists():
            return

        gen_mtime = generated.stat().st_mtime
        svc_mtime = services_yaml.stat().st_mtime

        if svc_mtime > gen_mtime:
            self.add_result(DriftResult(
                category=DriftCategory.CONFIG,
                severity=DriftSeverity.HIGH,
                source="helm_drift",
                expected="Generated Helm values in sync with services.yaml",
                actual="services.yaml modified after Helm values generation",
                description="Helm values generated file is stale",
                description_ar="ملف Helm المُنشأ قديم",
                file_path=str(generated),
                auto_fixable=True,
                remediation_hint="Run 'make generate-infra' to regenerate",
                remediation_hint_ar="شغّل 'make generate-infra' لإعادة الإنشاء",
            ))

    async def _check_cors_domain_drift(self) -> None:
        """Check CORS/domain settings consistency across configs."""
        root = Path(self.working_dir)

        # Check Kong config for CORS consistency
        kong_config = root / "config" / "kong" / "kong.yml"
        if not kong_config.exists():
            kong_config = root / "infrastructure" / "gateway" / "kong" / "kong.yml"

        if not kong_config.exists():
            return

        try:
            content = kong_config.read_text()
            # Check for wildcard CORS (security issue in production)
            if "origins:\n      - '*'" in content or 'origins: ["*"]' in content:
                self.add_result(DriftResult(
                    category=DriftCategory.CONFIG,
                    severity=DriftSeverity.HIGH,
                    source="cors_drift",
                    expected="Specific CORS origins per environment",
                    actual="Wildcard CORS origin (*) configured",
                    description="Kong has wildcard CORS origins - security risk in production",
                    description_ar="Kong يحتوي على أصول CORS عامة - خطر أمني في الإنتاج",
                    file_path=str(kong_config),
                    auto_fixable=False,
                    remediation_hint="Replace '*' with specific domain origins per environment",
                    remediation_hint_ar="استبدل '*' بأصول نطاقات محددة لكل بيئة",
                ))
        except Exception as e:
            logger.warning("Failed to check CORS config: %s", e)


def _parse_env_file(path: Path) -> set[str]:
    """Parse an env file and return variable names."""
    keys = set()
    if not path.exists():
        return keys
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=")[0].strip()
            keys.add(key)
    return keys


async def _scan_env_usage(root: Path) -> set[str]:
    """Scan codebase for environment variable usage."""
    env_vars: set[str] = set()
    patterns = [
        re.compile(r'os\.(?:environ|getenv)\s*[\[\(]\s*["\'](\w+)["\']'),
        re.compile(r'process\.env\.(\w+)'),
        re.compile(r'Settings\(\)\.(\w+)'),
    ]

    scan_dirs = ["apps/", "shared/", "packages/"]
    scan_extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}

    for scan_dir in scan_dirs:
        dir_path = root / scan_dir
        if not dir_path.exists():
            continue
        for file_path in dir_path.rglob("*"):
            if file_path.suffix not in scan_extensions:
                continue
            if "node_modules" in str(file_path) or ".venv" in str(file_path):
                continue
            try:
                content = file_path.read_text(errors="ignore")
                for pattern in patterns:
                    for match in pattern.finditer(content):
                        env_vars.add(match.group(1))
            except (OSError, UnicodeDecodeError):
                continue

    return env_vars
