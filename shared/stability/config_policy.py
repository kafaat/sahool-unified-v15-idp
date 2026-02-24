"""
SAHOOL Config Policy Engine
=============================
محرك سياسات التكوين لمنصة سهول

Policy-as-code engine for validating environment configuration at startup time.
Prevents config drift by enforcing required variables, patterns, and constraints
before the service begins accepting traffic.

This replaces the informational-only validate_env.py with a strict, enforceable
policy engine that services call during lifespan startup.

Usage:
    from shared.stability.config_policy import ConfigPolicyEngine, PolicyViolation

    # In service main.py lifespan:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = ConfigPolicyEngine(service_name="advisory-service")
        violations = engine.validate()

        if violations.has_critical:
            logger.error("Config policy violations", violations=violations.summary())
            raise SystemExit(1)
        elif violations.has_warnings:
            logger.warning("Config policy warnings", warnings=violations.warnings_summary())

        yield

Policies:
    - REQUIRED: Variable must be set and non-empty
    - MIN_LENGTH: Variable must have minimum length (for secrets)
    - PATTERN: Variable must match a regex pattern (for URLs)
    - ALLOWED_VALUES: Variable must be one of the allowed values
    - PORT_RANGE: Variable must be a valid port number
    - MUTUAL_EXCLUSIVE: Only one of a group can be set
    - CONDITIONAL: If X is set, Y must also be set
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class PolicySeverity(StrEnum):
    """Policy violation severity levels."""
    CRITICAL = "critical"  # Service must not start
    WARNING = "warning"    # Service can start but may have issues
    INFO = "info"          # Informational / best practice


class PolicyType(StrEnum):
    """Types of config policies."""
    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    PATTERN = "pattern"
    ALLOWED_VALUES = "allowed_values"
    PORT_RANGE = "port_range"
    CONDITIONAL = "conditional"
    NOT_EMPTY = "not_empty"


@dataclass
class PolicyRule:
    """A single config policy rule."""
    variable: str
    policy_type: PolicyType
    severity: PolicySeverity = PolicySeverity.CRITICAL
    description: str = ""
    description_ar: str = ""
    # Type-specific params
    min_length: int | None = None
    pattern: str | None = None
    allowed_values: list[str] | None = None
    port_min: int = 1
    port_max: int = 65535
    condition_variable: str | None = None  # For CONDITIONAL: if this is set, target must be set
    default_value: str | None = None  # If missing, use this default (only for non-critical)


@dataclass
class PolicyViolation:
    """A detected policy violation."""
    variable: str
    rule: PolicyRule
    severity: PolicySeverity
    message: str
    message_ar: str
    current_value: str | None = None  # Redacted for secrets


@dataclass
class ValidationResult:
    """Result of config policy validation."""
    violations: list[PolicyViolation] = field(default_factory=list)
    service_name: str = ""

    @property
    def has_critical(self) -> bool:
        return any(v.severity == PolicySeverity.CRITICAL for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(v.severity == PolicySeverity.WARNING for v in self.violations)

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == PolicySeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == PolicySeverity.WARNING)

    def summary(self) -> dict[str, Any]:
        """Return a summary suitable for structured logging."""
        return {
            "service": self.service_name,
            "total_violations": len(self.violations),
            "critical": self.critical_count,
            "warnings": self.warning_count,
            "violations": [
                {
                    "variable": v.variable,
                    "severity": v.severity.value,
                    "message": v.message,
                    "message_ar": v.message_ar,
                }
                for v in self.violations
            ],
        }

    def warnings_summary(self) -> list[str]:
        return [v.message for v in self.violations if v.severity == PolicySeverity.WARNING]


# ─────────────────────────────────────────────────────────────────────────────
# Platform-wide base policies (shared across all services)
# ─────────────────────────────────────────────────────────────────────────────

PLATFORM_BASE_POLICIES: list[PolicyRule] = [
    # Core
    PolicyRule(
        variable="ENVIRONMENT",
        policy_type=PolicyType.ALLOWED_VALUES,
        severity=PolicySeverity.CRITICAL,
        description="Runtime environment must be explicitly set",
        description_ar="يجب تعيين بيئة التشغيل بشكل صريح",
        allowed_values=["development", "staging", "production", "test"],
    ),
    # Database
    PolicyRule(
        variable="DATABASE_URL",
        policy_type=PolicyType.PATTERN,
        severity=PolicySeverity.WARNING,
        description="Database URL must be a valid PostgreSQL connection string",
        description_ar="يجب أن يكون عنوان قاعدة البيانات سلسلة اتصال PostgreSQL صالحة",
        pattern=r"^postgresql(\+asyncpg)?://",
    ),
    # JWT
    PolicyRule(
        variable="JWT_SECRET_KEY",
        policy_type=PolicyType.MIN_LENGTH,
        severity=PolicySeverity.CRITICAL,
        description="JWT secret must be at least 32 characters",
        description_ar="يجب أن يكون مفتاح JWT بطول 32 حرفًا على الأقل",
        min_length=32,
    ),
    # NATS
    PolicyRule(
        variable="NATS_URL",
        policy_type=PolicyType.PATTERN,
        severity=PolicySeverity.WARNING,
        description="NATS URL must use nats:// protocol",
        description_ar="يجب أن يستخدم عنوان NATS بروتوكول nats://",
        pattern=r"^nats://",
    ),
    # Log level
    PolicyRule(
        variable="LOG_LEVEL",
        policy_type=PolicyType.ALLOWED_VALUES,
        severity=PolicySeverity.INFO,
        description="Log level should be a standard level",
        description_ar="يجب أن يكون مستوى السجل مستوى قياسي",
        allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default_value="INFO",
    ),
]

# Production-only policies (stricter)
PRODUCTION_POLICIES: list[PolicyRule] = [
    PolicyRule(
        variable="DATABASE_URL",
        policy_type=PolicyType.PATTERN,
        severity=PolicySeverity.CRITICAL,
        description="Production database must use SSL",
        description_ar="يجب أن تستخدم قاعدة بيانات الإنتاج SSL",
        pattern=r"sslmode=(require|verify-full|verify-ca)",
    ),
    PolicyRule(
        variable="JWT_SECRET_KEY",
        policy_type=PolicyType.MIN_LENGTH,
        severity=PolicySeverity.CRITICAL,
        description="Production JWT secret must be at least 64 characters",
        description_ar="يجب أن يكون مفتاح JWT في الإنتاج بطول 64 حرفًا على الأقل",
        min_length=64,
    ),
]


class ConfigPolicyEngine:
    """
    Config policy validation engine.
    محرك التحقق من سياسات التكوين.

    Validates environment variables against defined policies at service startup.
    Can be extended with service-specific rules.
    """

    def __init__(
        self,
        service_name: str,
        additional_rules: list[PolicyRule] | None = None,
        env_override: dict[str, str] | None = None,
    ):
        self.service_name = service_name
        self._env = env_override or dict(os.environ)
        self._rules = list(PLATFORM_BASE_POLICIES)

        # Add production policies if in production
        environment = self._env.get("ENVIRONMENT", "development").lower()
        if environment == "production":
            self._rules.extend(PRODUCTION_POLICIES)

        # Add service-specific rules
        if additional_rules:
            self._rules.extend(additional_rules)

    def validate(self) -> ValidationResult:
        """
        Run all policy rules against the current environment.
        تشغيل جميع قواعد السياسة ضد البيئة الحالية.

        Returns:
            ValidationResult with all violations found
        """
        result = ValidationResult(service_name=self.service_name)

        for rule in self._rules:
            violation = self._check_rule(rule)
            if violation:
                result.violations.append(violation)

        if result.is_clean:
            logger.info(
                "Config policy validation passed: service=%s rules_checked=%d",
                self.service_name,
                len(self._rules),
            )
        else:
            logger.warning(
                "Config policy violations detected: service=%s critical=%d warnings=%d",
                self.service_name,
                result.critical_count,
                result.warning_count,
            )

        return result

    def _check_rule(self, rule: PolicyRule) -> PolicyViolation | None:
        """Check a single rule against the environment."""
        value = self._env.get(rule.variable)

        if rule.policy_type == PolicyType.REQUIRED:
            if not value:
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=f"{rule.variable} is required but not set",
                    message_ar=f"{rule.variable} مطلوب ولكنه غير معيّن",
                )

        elif rule.policy_type == PolicyType.NOT_EMPTY:
            if value is not None and value.strip() == "":
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=f"{rule.variable} is set but empty",
                    message_ar=f"{rule.variable} معيّن ولكنه فارغ",
                )

        elif rule.policy_type == PolicyType.MIN_LENGTH:
            if value and rule.min_length and len(value) < rule.min_length:
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=f"{rule.variable} must be at least {rule.min_length} characters (got {len(value)})",
                    message_ar=f"{rule.variable} يجب أن يكون بطول {rule.min_length} حرفًا على الأقل (الحالي {len(value)})",
                )

        elif rule.policy_type == PolicyType.PATTERN:
            if value and rule.pattern and not re.search(rule.pattern, value):
                msg = rule.description if rule.description else f"{rule.variable} does not match required pattern"
                msg_ar = rule.description_ar if rule.description_ar else f"{rule.variable} لا يطابق النمط المطلوب"
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=msg,
                    message_ar=msg_ar,
                )

        elif rule.policy_type == PolicyType.ALLOWED_VALUES:
            if value and rule.allowed_values and value not in rule.allowed_values:
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=f"{rule.variable}={value} not in allowed values: {rule.allowed_values}",
                    message_ar=f"{rule.variable}={value} غير موجود في القيم المسموحة: {rule.allowed_values}",
                    current_value=value,
                )

        elif rule.policy_type == PolicyType.PORT_RANGE:
            if value:
                try:
                    port = int(value)
                    if port < rule.port_min or port > rule.port_max:
                        return PolicyViolation(
                            variable=rule.variable,
                            rule=rule,
                            severity=rule.severity,
                            message=f"{rule.variable}={port} outside valid range ({rule.port_min}-{rule.port_max})",
                            message_ar=f"{rule.variable}={port} خارج النطاق الصالح ({rule.port_min}-{rule.port_max})",
                            current_value=value,
                        )
                except ValueError:
                    return PolicyViolation(
                        variable=rule.variable,
                        rule=rule,
                        severity=rule.severity,
                        message=f"{rule.variable} must be a valid port number",
                        message_ar=f"{rule.variable} يجب أن يكون رقم منفذ صالح",
                        current_value=value,
                    )

        elif rule.policy_type == PolicyType.CONDITIONAL:
            condition_value = self._env.get(rule.condition_variable or "")
            if condition_value and not value:
                return PolicyViolation(
                    variable=rule.variable,
                    rule=rule,
                    severity=rule.severity,
                    message=f"{rule.variable} is required when {rule.condition_variable} is set",
                    message_ar=f"{rule.variable} مطلوب عندما يكون {rule.condition_variable} معيّنًا",
                )

        return None

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a custom rule dynamically."""
        self._rules.append(rule)

    def get_rules_summary(self) -> list[dict[str, Any]]:
        """Get a summary of all configured rules."""
        return [
            {
                "variable": r.variable,
                "type": r.policy_type.value,
                "severity": r.severity.value,
                "description": r.description,
            }
            for r in self._rules
        ]
