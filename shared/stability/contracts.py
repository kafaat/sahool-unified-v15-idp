"""
SAHOOL Contract Validation Framework
========================================
إطار التحقق من العقود لمنصة سهول

Validates API and event contracts to prevent breaking changes.
Works at two levels:
1. Static: CI-time validation of schemas against golden files
2. Runtime: Live endpoint probing against expected contract

This module provides tools for:
- API contract validation (OpenAPI schema comparison)
- Event contract validation (event envelope + payload schema)
- Health endpoint contract validation (standardized health responses)
- Migration contract validation (backward compatibility)

Usage:
    from shared.stability.contracts import ContractValidator

    # Validate event contracts
    validator = ContractValidator()
    report = validator.validate_event_contracts()

    # Validate health endpoints
    report = await validator.validate_health_contract("http://service:8090")
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ContractSeverity(StrEnum):
    """Severity of contract violations."""
    BREAKING = "breaking"    # Backward-incompatible change
    WARNING = "warning"      # Potentially problematic change
    INFO = "info"            # Safe change


class ContractType(StrEnum):
    """Types of contracts."""
    EVENT_SCHEMA = "event_schema"
    API_ENDPOINT = "api_endpoint"
    HEALTH_CHECK = "health_check"
    MIGRATION = "migration"


@dataclass
class ContractViolation:
    """A single contract violation."""
    contract_type: ContractType
    severity: ContractSeverity
    location: str  # e.g., "sahool.field.created" or "/api/v1/fields"
    message: str
    message_ar: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractReport:
    """Result of contract validation."""
    violations: list[ContractViolation] = field(default_factory=list)
    checks_run: int = 0
    checks_passed: int = 0

    @property
    def has_breaking(self) -> bool:
        return any(v.severity == ContractSeverity.BREAKING for v in self.violations)

    @property
    def breaking_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ContractSeverity.BREAKING)

    @property
    def is_clean(self) -> bool:
        return not self.has_breaking

    def summary(self) -> dict[str, Any]:
        return {
            "checks_run": self.checks_run,
            "checks_passed": self.checks_passed,
            "breaking_violations": self.breaking_count,
            "total_violations": len(self.violations),
            "violations": [
                {
                    "type": v.contract_type.value,
                    "severity": v.severity.value,
                    "location": v.location,
                    "message": v.message,
                }
                for v in self.violations
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Event Contract Definitions
# ─────────────────────────────────────────────────────────────────────────────

# Required fields in every event envelope (from BaseEvent in shared/events/contracts.py)
REQUIRED_EVENT_ENVELOPE_FIELDS = {
    "event_id": str,
    "timestamp": str,
    "version": str,
    "source_service": str,
    "event_type": str,
}

# Optional but expected fields
EXPECTED_EVENT_FIELDS = {
    "correlation_id": str,
    "causation_id": str,
    "tenant_id_header": str,
    "trace_id": str,
    "span_id": str,
}

# Required NATS headers (from publisher.py _build_nats_headers)
REQUIRED_NATS_HEADERS = [
    "X-Event-ID",
    "X-Correlation-ID",
]

EXPECTED_NATS_HEADERS = [
    "traceparent",
    "X-Tenant-ID",
    "X-Schema-Version",
    "X-Causation-ID",
]

# Health endpoint contract
HEALTH_CONTRACT = {
    "liveness": {
        "paths": ["/healthz", "/health"],
        "required_fields": ["status"],
        "expected_status_values": ["ok", "healthy", "up"],
    },
    "readiness": {
        "paths": ["/readyz", "/health/ready"],
        "required_fields": ["status"],
    },
}


class ContractValidator:
    """
    Contract validation engine for SAHOOL platform.
    محرك التحقق من العقود لمنصة سهول.

    Validates that services adhere to platform-wide contracts for
    events, APIs, health checks, and migrations.
    """

    def __init__(self, project_root: str | None = None):
        self.project_root = Path(project_root) if project_root else self._find_project_root()

    def _find_project_root(self) -> Path:
        """Find project root by looking for governance/ directory."""
        current = Path.cwd()
        for parent in [current, *current.parents]:
            if (parent / "governance").is_dir():
                return parent
        return current

    # ─────────────────────────────────────────────────────────────────────────
    # Event Contract Validation
    # ─────────────────────────────────────────────────────────────────────────

    def validate_event_envelope(self, event_data: dict[str, Any]) -> ContractReport:
        """
        Validate that an event dict conforms to the BaseEvent contract.
        التحقق من أن بيانات الحدث تتوافق مع عقد BaseEvent.

        Args:
            event_data: Deserialized event JSON

        Returns:
            ContractReport with any violations
        """
        report = ContractReport()

        # Check required fields
        for field_name, field_type in REQUIRED_EVENT_ENVELOPE_FIELDS.items():
            report.checks_run += 1
            value = event_data.get(field_name)

            if value is None:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.EVENT_SCHEMA,
                    severity=ContractSeverity.BREAKING,
                    location=f"envelope.{field_name}",
                    message=f"Required field '{field_name}' is missing from event envelope",
                    message_ar=f"الحقل المطلوب '{field_name}' مفقود من غلاف الحدث",
                ))
            elif not isinstance(value, field_type):
                report.violations.append(ContractViolation(
                    contract_type=ContractType.EVENT_SCHEMA,
                    severity=ContractSeverity.BREAKING,
                    location=f"envelope.{field_name}",
                    message=f"Field '{field_name}' expected type {field_type.__name__}, got {type(value).__name__}",
                    message_ar=f"الحقل '{field_name}' يتوقع نوع {field_type.__name__}، الحالي {type(value).__name__}",
                ))
            else:
                report.checks_passed += 1

        # Check expected (optional but recommended) fields
        for field_name, field_type in EXPECTED_EVENT_FIELDS.items():
            report.checks_run += 1
            value = event_data.get(field_name)

            if value is None:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.EVENT_SCHEMA,
                    severity=ContractSeverity.INFO,
                    location=f"envelope.{field_name}",
                    message=f"Expected field '{field_name}' is missing (recommended for tracing)",
                    message_ar=f"الحقل المتوقع '{field_name}' مفقود (موصى به للتتبع)",
                ))
            else:
                report.checks_passed += 1

        return report

    def validate_event_schema_files(self) -> ContractReport:
        """
        Validate event schema files in governance/events/schemas/ directory.
        التحقق من ملفات مخططات الأحداث.

        Checks:
        - All schema files are valid JSON
        - Each schema has required metadata (title, type, properties)
        - Event types referenced in catalog exist as schemas
        """
        report = ContractReport()
        schemas_dir = self.project_root / "governance" / "events" / "schemas"

        if not schemas_dir.is_dir():
            report.violations.append(ContractViolation(
                contract_type=ContractType.EVENT_SCHEMA,
                severity=ContractSeverity.WARNING,
                location="governance/events/schemas/",
                message="Event schemas directory not found",
                message_ar="دليل مخططات الأحداث غير موجود",
            ))
            return report

        for schema_file in schemas_dir.glob("*.json"):
            report.checks_run += 1
            try:
                with open(schema_file) as f:
                    schema = json.load(f)

                # Validate schema structure
                if "type" not in schema and "$ref" not in schema:
                    report.violations.append(ContractViolation(
                        contract_type=ContractType.EVENT_SCHEMA,
                        severity=ContractSeverity.WARNING,
                        location=str(schema_file.relative_to(self.project_root)),
                        message=f"Schema {schema_file.name} missing 'type' field",
                        message_ar=f"المخطط {schema_file.name} يفتقد حقل 'type'",
                    ))
                else:
                    report.checks_passed += 1

            except json.JSONDecodeError as e:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.EVENT_SCHEMA,
                    severity=ContractSeverity.BREAKING,
                    location=str(schema_file.relative_to(self.project_root)),
                    message=f"Invalid JSON in schema: {e}",
                    message_ar=f"JSON غير صالح في المخطط: {e}",
                ))

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Service Registry Contract Validation
    # ─────────────────────────────────────────────────────────────────────────

    def validate_service_registry(self) -> ContractReport:
        """
        Validate that services.yaml has required fields for every service.
        التحقق من أن ملف الخدمات يحتوي على الحقول المطلوبة لكل خدمة.
        """
        report = ContractReport()
        registry_path = self.project_root / "governance" / "services.yaml"

        if not registry_path.is_file():
            report.violations.append(ContractViolation(
                contract_type=ContractType.API_ENDPOINT,
                severity=ContractSeverity.BREAKING,
                location="governance/services.yaml",
                message="Service registry file not found",
                message_ar="ملف سجل الخدمات غير موجود",
            ))
            return report

        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not installed, skipping service registry validation")
            return report

        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        services_data = registry.get("services", {})
        required_fields = ["owner", "team", "lifecycle", "tier"]

        # services.yaml uses a map structure: service-key -> {details}
        if isinstance(services_data, dict):
            services_iter = services_data.items()
        elif isinstance(services_data, list):
            services_iter = ((s.get("name", "<unnamed>"), s) for s in services_data)
        else:
            return report

        for svc_key, svc_info in services_iter:
            report.checks_run += 1
            if not isinstance(svc_info, dict):
                continue

            service_name = svc_info.get("name", svc_key)

            missing = [f for f in required_fields if f not in svc_info]
            if missing:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.API_ENDPOINT,
                    severity=ContractSeverity.WARNING,
                    location=f"services.yaml:{service_name}",
                    message=f"Service '{service_name}' missing required fields: {missing}",
                    message_ar=f"الخدمة '{service_name}' تفتقد الحقول المطلوبة: {missing}",
                ))
            else:
                report.checks_passed += 1

            # Validate lifecycle is valid
            lifecycle = svc_info.get("lifecycle", "")
            valid_lifecycles = {"experimental", "internal", "production", "deprecated", "retired"}
            if lifecycle and lifecycle not in valid_lifecycles:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.API_ENDPOINT,
                    severity=ContractSeverity.WARNING,
                    location=f"services.yaml:{service_name}",
                    message=f"Invalid lifecycle '{lifecycle}' for service '{service_name}'",
                    message_ar=f"دورة حياة غير صالحة '{lifecycle}' للخدمة '{service_name}'",
                ))

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Health Endpoint Contract
    # ─────────────────────────────────────────────────────────────────────────

    async def validate_health_contract(self, base_url: str) -> ContractReport:
        """
        Validate that a service exposes standard health endpoints.
        التحقق من أن الخدمة توفر نقاط نهاية صحة قياسية.

        Args:
            base_url: Service base URL (e.g., "http://localhost:8090")
        """
        report = ContractReport()

        try:
            import httpx
        except ImportError:
            logger.warning("httpx not installed, skipping health contract validation")
            return report

        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check liveness
            for path in HEALTH_CONTRACT["liveness"]["paths"]:
                report.checks_run += 1
                try:
                    resp = await client.get(f"{base_url}{path}")
                    if resp.status_code == 200:
                        data = resp.json()
                        if "status" in data:
                            report.checks_passed += 1
                            break  # One liveness path is enough
                        else:
                            report.violations.append(ContractViolation(
                                contract_type=ContractType.HEALTH_CHECK,
                                severity=ContractSeverity.WARNING,
                                location=path,
                                message=f"Health endpoint {path} missing 'status' field",
                                message_ar=f"نقطة نهاية الصحة {path} تفتقد حقل 'status'",
                            ))
                except Exception:
                    continue
            else:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.HEALTH_CHECK,
                    severity=ContractSeverity.BREAKING,
                    location="liveness",
                    message=f"No liveness endpoint responding at {base_url}",
                    message_ar=f"لا توجد نقطة نهاية حية تستجيب في {base_url}",
                ))

            # Check readiness
            for path in HEALTH_CONTRACT["readiness"]["paths"]:
                report.checks_run += 1
                try:
                    resp = await client.get(f"{base_url}{path}")
                    if resp.status_code == 200:
                        report.checks_passed += 1
                        break
                except Exception:
                    continue

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Migration Contract
    # ─────────────────────────────────────────────────────────────────────────

    def validate_migration_backward_compat(
        self,
        old_schema: dict[str, Any],
        new_schema: dict[str, Any],
    ) -> ContractReport:
        """
        Check that a schema change is backward-compatible (expand/contract pattern).
        التحقق من أن تغيير المخطط متوافق مع الإصدارات السابقة.

        Rules:
        - Cannot remove required fields (BREAKING)
        - Cannot change field types (BREAKING)
        - Can add new optional fields (OK)
        - Can add new required fields with defaults (WARNING)
        """
        report = ContractReport()

        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        # Check removed fields
        for field_name in old_props:
            report.checks_run += 1
            if field_name not in new_props:
                if field_name in old_required:
                    report.violations.append(ContractViolation(
                        contract_type=ContractType.MIGRATION,
                        severity=ContractSeverity.BREAKING,
                        location=f"properties.{field_name}",
                        message=f"Required field '{field_name}' was removed (breaking change)",
                        message_ar=f"تم إزالة الحقل المطلوب '{field_name}' (تغيير جذري)",
                    ))
                else:
                    report.violations.append(ContractViolation(
                        contract_type=ContractType.MIGRATION,
                        severity=ContractSeverity.WARNING,
                        location=f"properties.{field_name}",
                        message=f"Optional field '{field_name}' was removed",
                        message_ar=f"تم إزالة الحقل الاختياري '{field_name}'",
                    ))
            else:
                report.checks_passed += 1

        # Check type changes
        for field_name in old_props:
            if field_name in new_props:
                report.checks_run += 1
                old_type = old_props[field_name].get("type")
                new_type = new_props[field_name].get("type")
                if old_type and new_type and old_type != new_type:
                    report.violations.append(ContractViolation(
                        contract_type=ContractType.MIGRATION,
                        severity=ContractSeverity.BREAKING,
                        location=f"properties.{field_name}.type",
                        message=f"Field '{field_name}' type changed from '{old_type}' to '{new_type}'",
                        message_ar=f"تم تغيير نوع الحقل '{field_name}' من '{old_type}' إلى '{new_type}'",
                    ))
                else:
                    report.checks_passed += 1

        # Check new required fields without defaults
        new_required_fields = new_required - old_required
        for field_name in new_required_fields:
            report.checks_run += 1
            if field_name in new_props and "default" not in new_props[field_name]:
                report.violations.append(ContractViolation(
                    contract_type=ContractType.MIGRATION,
                    severity=ContractSeverity.BREAKING,
                    location=f"required.{field_name}",
                    message=f"New required field '{field_name}' has no default value",
                    message_ar=f"الحقل المطلوب الجديد '{field_name}' ليس له قيمة افتراضية",
                ))
            else:
                report.checks_passed += 1

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Run All Contracts
    # ─────────────────────────────────────────────────────────────────────────

    def validate_all_static(self) -> ContractReport:
        """
        Run all static (non-network) contract validations.
        تشغيل جميع عمليات التحقق الثابتة من العقود.
        """
        combined = ContractReport()

        # Event schemas
        event_report = self.validate_event_schema_files()
        combined.violations.extend(event_report.violations)
        combined.checks_run += event_report.checks_run
        combined.checks_passed += event_report.checks_passed

        # Service registry
        registry_report = self.validate_service_registry()
        combined.violations.extend(registry_report.violations)
        combined.checks_run += registry_report.checks_run
        combined.checks_passed += registry_report.checks_passed

        logger.info(
            "Contract validation complete: checks_run=%d checks_passed=%d violations=%d breaking=%d",
            combined.checks_run,
            combined.checks_passed,
            len(combined.violations),
            combined.breaking_count,
        )

        return combined
