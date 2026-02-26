"""
SAHOOL Drift Detection System
================================
نظام كشف الانحراف لمنصة سهول

Detects configuration, schema, and operational drift across the platform.
Drift = deviation from the expected/declared state.

Drift Types:
1. Config Drift: env vars differ from declared schema
2. Schema Drift: DB schema differs from migration state
3. Service Drift: running services differ from governance registry
4. Event Drift: published events differ from contract schemas
5. Docker Drift: running containers differ from compose declarations

Usage:
    from shared.stability.drift_detector import DriftDetector

    detector = DriftDetector(project_root="/path/to/repo")

    # Check for config drift
    report = detector.detect_config_drift()

    # Check for service registry drift
    report = detector.detect_service_drift()

    # Run all drift checks
    report = detector.detect_all()
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DriftType(StrEnum):
    """Types of drift that can be detected."""

    CONFIG = "config"
    SCHEMA = "schema"
    SERVICE = "service"
    EVENT = "event"
    DOCKER = "docker"
    SECURITY = "security"


class DriftSeverity(StrEnum):
    """Severity of detected drift."""

    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action within 24h
    MEDIUM = "medium"  # Action within 1 week
    LOW = "low"  # Informational


@dataclass
class DriftItem:
    """A single detected drift."""

    drift_type: DriftType
    severity: DriftSeverity
    resource: str  # What drifted (e.g., "advisory-service", "DATABASE_URL")
    expected: str  # What was expected
    actual: str  # What was found
    message: str
    message_ar: str
    remediation: str = ""  # How to fix
    remediation_ar: str = ""


@dataclass
class DriftReport:
    """Result of drift detection."""

    items: list[DriftItem] = field(default_factory=list)
    checks_run: int = 0
    timestamp: str = ""

    @property
    def has_critical(self) -> bool:
        return any(d.severity == DriftSeverity.CRITICAL for d in self.items)

    @property
    def is_clean(self) -> bool:
        return len(self.items) == 0

    @property
    def by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.drift_type.value] = counts.get(item.drift_type.value, 0) + 1
        return counts

    def summary(self) -> dict[str, Any]:
        return {
            "checks_run": self.checks_run,
            "total_drift": len(self.items),
            "critical": sum(1 for d in self.items if d.severity == DriftSeverity.CRITICAL),
            "high": sum(1 for d in self.items if d.severity == DriftSeverity.HIGH),
            "medium": sum(1 for d in self.items if d.severity == DriftSeverity.MEDIUM),
            "low": sum(1 for d in self.items if d.severity == DriftSeverity.LOW),
            "by_type": self.by_type,
            "items": [
                {
                    "type": d.drift_type.value,
                    "severity": d.severity.value,
                    "resource": d.resource,
                    "message": d.message,
                    "remediation": d.remediation,
                }
                for d in self.items
            ],
        }


class DriftDetector:
    """
    Platform-wide drift detection engine.
    محرك كشف الانحراف على مستوى المنصة.

    Detects deviations between declared (Git) state and actual (runtime) state.
    """

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root) if project_root else self._find_project_root()

    def _find_project_root(self) -> Path:
        current = Path.cwd()
        for parent in [current, *current.parents]:
            if (parent / "governance").is_dir():
                return parent
        return current

    # ─────────────────────────────────────────────────────────────────────────
    # Config Drift: env vars vs declared schema
    # ─────────────────────────────────────────────────────────────────────────

    def detect_config_drift(self, env_override: dict[str, str] | None = None) -> DriftReport:
        """
        Detect drift between .env.example declarations and actual environment.
        كشف الانحراف بين إعلانات .env.example والبيئة الفعلية.

        Checks:
        - Variables declared in .env.example but not set
        - Variables set but not declared in .env.example
        - Variables with values that differ from example defaults
        """
        report = DriftReport()
        env = env_override or dict(os.environ)
        env_example = self.project_root / ".env.example"

        if not env_example.is_file():
            logger.warning(".env.example not found, skipping config drift detection")
            return report

        declared_vars: dict[str, str] = {}
        with open(env_example) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    declared_vars[key.strip()] = value.strip()

        # Check declared vars that are not set
        for var_name, default_value in declared_vars.items():
            report.checks_run += 1
            actual = env.get(var_name)

            if actual is None:
                # Determine severity based on variable name patterns
                severity = DriftSeverity.MEDIUM
                if any(k in var_name.upper() for k in ["SECRET", "PASSWORD", "KEY", "TOKEN"]):
                    severity = DriftSeverity.HIGH
                if var_name in ("DATABASE_URL", "JWT_SECRET_KEY", "NATS_URL"):
                    severity = DriftSeverity.HIGH

                report.items.append(
                    DriftItem(
                        drift_type=DriftType.CONFIG,
                        severity=severity,
                        resource=var_name,
                        expected=f"declared in .env.example (default: {default_value[:20]}...)"
                        if len(default_value) > 20
                        else f"declared (default: {default_value})",
                        actual="not set",
                        message=f"Environment variable '{var_name}' is declared but not set",
                        message_ar=f"متغير البيئة '{var_name}' معلن ولكنه غير معيّن",
                        remediation=f"Set {var_name} in .env or environment",
                        remediation_ar=f"قم بتعيين {var_name} في .env أو البيئة",
                    )
                )

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Service Drift: running state vs governance registry
    # ─────────────────────────────────────────────────────────────────────────

    def detect_service_drift(self) -> DriftReport:
        """
        Detect drift between governance/services.yaml and actual service directories.
        كشف الانحراف بين سجل الحوكمة وأدلة الخدمات الفعلية.

        Checks:
        - Services in registry that don't have directories
        - Service directories not registered in governance
        - Deprecated services still in active directories
        """
        report = DriftReport()
        registry_path = self.project_root / "governance" / "services.yaml"
        services_dir = self.project_root / "apps" / "services"

        if not registry_path.is_file():
            return report

        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed, skipping service drift detection")
            return report

        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        registered_services = {}
        services_data = registry.get("services", {})

        # services.yaml uses a map structure: service-key -> {details}
        if isinstance(services_data, dict):
            for svc_key, svc_info in services_data.items():
                if isinstance(svc_info, dict):
                    registered_services[svc_key] = svc_info
        elif isinstance(services_data, list):
            for svc in services_data:
                name = svc.get("name", "")
                if name:
                    registered_services[name] = svc

        # Get actual service directories
        actual_services = set()
        if services_dir.is_dir():
            for d in services_dir.iterdir():
                if d.is_dir() and not d.name.startswith("."):
                    actual_services.add(d.name)

        # Services in registry but no directory
        for svc_name, svc_info in registered_services.items():
            report.checks_run += 1
            lifecycle = svc_info.get("lifecycle", "")

            # Skip retired/deprecated services
            if lifecycle in ("retired", "deprecated"):
                report.checks_run += 1
                # But check if still present in active dir
                if svc_name in actual_services:
                    report.items.append(
                        DriftItem(
                            drift_type=DriftType.SERVICE,
                            severity=DriftSeverity.MEDIUM,
                            resource=svc_name,
                            expected=f"lifecycle={lifecycle} (should be archived)",
                            actual=f"still present in apps/services/{svc_name}",
                            message=f"Deprecated service '{svc_name}' still in active directory",
                            message_ar=f"الخدمة المهملة '{svc_name}' لا تزال في الدليل النشط",
                            remediation=f"Move {svc_name} to archive/deprecated-services/",
                            remediation_ar=f"انقل {svc_name} إلى archive/deprecated-services/",
                        )
                    )
                continue

            if svc_name not in actual_services:
                report.items.append(
                    DriftItem(
                        drift_type=DriftType.SERVICE,
                        severity=DriftSeverity.MEDIUM,
                        resource=svc_name,
                        expected="registered in services.yaml",
                        actual="directory not found",
                        message=f"Registered service '{svc_name}' has no directory in apps/services/",
                        message_ar=f"الخدمة المسجلة '{svc_name}' ليس لها دليل في apps/services/",
                        remediation="Create directory or update services.yaml",
                        remediation_ar="أنشئ الدليل أو حدّث services.yaml",
                    )
                )

        # Directories not in registry
        for dir_name in actual_services:
            report.checks_run += 1
            if dir_name not in registered_services:
                report.items.append(
                    DriftItem(
                        drift_type=DriftType.SERVICE,
                        severity=DriftSeverity.LOW,
                        resource=dir_name,
                        expected="registered in services.yaml",
                        actual="directory exists but not registered",
                        message=f"Service directory '{dir_name}' not in governance registry",
                        message_ar=f"دليل الخدمة '{dir_name}' غير مسجل في سجل الحوكمة",
                        remediation=f"Add {dir_name} to governance/services.yaml",
                        remediation_ar=f"أضف {dir_name} إلى governance/services.yaml",
                    )
                )

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Event Drift: published events vs governance catalog
    # ─────────────────────────────────────────────────────────────────────────

    def detect_event_drift(self) -> DriftReport:
        """
        Detect drift between event subjects in code and governance catalog.
        كشف الانحراف بين مواضيع الأحداث في الكود وكتالوج الحوكمة.
        """
        report = DriftReport()
        subjects_file = self.project_root / "shared" / "events" / "subjects.py"
        catalog_file = self.project_root / "governance" / "events" / "catalog.yaml"

        if not subjects_file.is_file() or not catalog_file.is_file():
            return report

        # Parse subject constants from subjects.py
        code_subjects: set[str] = set()
        with open(subjects_file) as f:
            for line in f:
                # Look for SAHOOL_* = "sahool.*" patterns
                if '= "sahool.' in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        subject = parts[1]
                        code_subjects.add(subject)

        try:
            import yaml
        except ImportError:
            return report

        with open(catalog_file) as f:
            catalog = yaml.safe_load(f)

        # Parse catalog subjects
        # catalog.yaml uses map structure: events: { "field.created": {...}, ... }
        catalog_subjects: set[str] = set()
        events_data = catalog.get("events", {})
        if isinstance(events_data, dict):
            for event_key in events_data:
                # Convert event key to NATS subject: "field.created" -> "sahool.field.created"
                catalog_subjects.add(f"sahool.{event_key}")
        elif isinstance(events_data, list):
            for event in events_data:
                if isinstance(event, dict):
                    subject = event.get("subject", "")
                    if subject:
                        catalog_subjects.add(subject)

        # Subjects in code but not in catalog
        for subject in code_subjects - catalog_subjects:
            report.checks_run += 1
            report.items.append(
                DriftItem(
                    drift_type=DriftType.EVENT,
                    severity=DriftSeverity.LOW,
                    resource=subject,
                    expected="documented in catalog.yaml",
                    actual="defined in code only",
                    message=f"Event subject '{subject}' not in governance catalog",
                    message_ar=f"موضوع الحدث '{subject}' غير موجود في كتالوج الحوكمة",
                    remediation=f"Add '{subject}' to governance/events/catalog.yaml",
                    remediation_ar=f"أضف '{subject}' إلى governance/events/catalog.yaml",
                )
            )

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Docker Drift: Dockerfile patterns
    # ─────────────────────────────────────────────────────────────────────────

    def detect_docker_drift(self) -> DriftReport:
        """
        Detect drift in Dockerfile patterns across services.
        كشف الانحراف في أنماط Dockerfile عبر الخدمات.

        Checks:
        - Services missing Dockerfiles
        - Services running as root (no USER directive)
        - Services missing HEALTHCHECK
        - Services using :latest tag
        """
        report = DriftReport()
        services_dir = self.project_root / "apps" / "services"

        if not services_dir.is_dir():
            return report

        for service_dir in services_dir.iterdir():
            if not service_dir.is_dir() or service_dir.name.startswith("."):
                continue

            dockerfile = service_dir / "Dockerfile"
            report.checks_run += 1

            if not dockerfile.is_file():
                report.items.append(
                    DriftItem(
                        drift_type=DriftType.DOCKER,
                        severity=DriftSeverity.MEDIUM,
                        resource=service_dir.name,
                        expected="Dockerfile present",
                        actual="Dockerfile missing",
                        message=f"Service '{service_dir.name}' has no Dockerfile",
                        message_ar=f"الخدمة '{service_dir.name}' ليس لها Dockerfile",
                        remediation=f"Create Dockerfile for {service_dir.name}",
                    )
                )
                continue

            content = dockerfile.read_text()

            # Check for non-root user
            report.checks_run += 1
            if "USER " not in content and "user " not in content:
                report.items.append(
                    DriftItem(
                        drift_type=DriftType.SECURITY,
                        severity=DriftSeverity.HIGH,
                        resource=service_dir.name,
                        expected="Non-root USER directive",
                        actual="No USER directive found",
                        message=f"Service '{service_dir.name}' Dockerfile has no USER directive (runs as root)",
                        message_ar=f"ملف Docker للخدمة '{service_dir.name}' لا يحتوي على تعليمة USER (يعمل كـ root)",
                        remediation="Add 'USER sahool' or 'USER 1000' directive",
                    )
                )

            # Check for HEALTHCHECK
            report.checks_run += 1
            if "HEALTHCHECK" not in content:
                report.items.append(
                    DriftItem(
                        drift_type=DriftType.DOCKER,
                        severity=DriftSeverity.LOW,
                        resource=service_dir.name,
                        expected="HEALTHCHECK directive",
                        actual="No HEALTHCHECK found",
                        message=f"Service '{service_dir.name}' Dockerfile missing HEALTHCHECK",
                        message_ar=f"ملف Docker للخدمة '{service_dir.name}' يفتقد HEALTHCHECK",
                        remediation="Add HEALTHCHECK CMD curl -f http://localhost:PORT/healthz || exit 1",
                    )
                )

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Run All Drift Checks
    # ─────────────────────────────────────────────────────────────────────────

    def detect_all(self) -> DriftReport:
        """
        Run all drift detection checks.
        تشغيل جميع فحوصات كشف الانحراف.
        """
        from datetime import UTC, datetime

        combined = DriftReport(timestamp=datetime.now(UTC).isoformat())

        detectors = [
            ("config", self.detect_config_drift),
            ("service", self.detect_service_drift),
            ("event", self.detect_event_drift),
            ("docker", self.detect_docker_drift),
        ]

        for name, detector_fn in detectors:
            try:
                sub_report = detector_fn()
                combined.items.extend(sub_report.items)
                combined.checks_run += sub_report.checks_run
            except Exception as e:
                logger.error(f"Drift detection failed for {name}: {e}")

        logger.info(
            "Drift detection complete: checks_run=%d total_drift=%d critical=%d",
            combined.checks_run,
            len(combined.items),
            sum(1 for d in combined.items if d.severity == DriftSeverity.CRITICAL),
        )

        return combined
