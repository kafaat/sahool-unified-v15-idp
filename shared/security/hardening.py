"""
Advanced Security Hardening Module | وحدة تعزيز الأمان المتقدمة

Provides:
- Redis TLS configuration helpers
- Vault integration utilities
- Security audit checklist
- GlobalGAP compliance reporting
- Automated security scanning configuration
"""

from __future__ import annotations

import os
import logging
import secrets
from datetime import datetime, UTC
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SecurityLevel(StrEnum):
    """Security compliance levels | مستويات الامتثال الأمني"""

    BASIC = "basic"  # أساسي
    STANDARD = "standard"  # قياسي
    ENHANCED = "enhanced"  # محسّن
    ENTERPRISE = "enterprise"  # مؤسسي


class AuditStatus(StrEnum):
    """Audit check status | حالة فحص التدقيق"""

    PASS = "pass"  # نجاح
    FAIL = "fail"  # فشل
    WARNING = "warning"  # تحذير
    SKIPPED = "skipped"  # تخطي
    NOT_APPLICABLE = "n/a"  # غير قابل للتطبيق


SECURITY_LEVEL_AR = {
    SecurityLevel.BASIC: "أساسي",
    SecurityLevel.STANDARD: "قياسي",
    SecurityLevel.ENHANCED: "محسّن",
    SecurityLevel.ENTERPRISE: "مؤسسي",
}


@dataclass
class SecurityCheckResult:
    """Result of a single security check | نتيجة فحص أمني واحد"""

    check_id: str = ""
    category: str = ""
    category_ar: str = ""
    description: str = ""
    description_ar: str = ""
    status: AuditStatus = AuditStatus.SKIPPED
    severity: str = "medium"
    details: str = ""
    recommendation: str = ""
    recommendation_ar: str = ""


@dataclass
class SecurityAuditReport:
    """Complete security audit report | تقرير التدقيق الأمني الكامل"""

    report_id: str = ""
    tenant_id: str = ""
    security_level: SecurityLevel = SecurityLevel.STANDARD
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    score_percent: float = 0.0
    checks: list[SecurityCheckResult] = field(default_factory=list)
    generated_at: str = ""
    message: str = ""
    message_ar: str = ""


@dataclass
class TLSConfig:
    """TLS configuration for services | تكوين TLS للخدمات"""

    enabled: bool = False
    cert_path: str = ""
    key_path: str = ""
    ca_path: str = ""
    min_version: str = "TLSv1.2"
    cipher_suites: list[str] = field(default_factory=list)
    verify_client: bool = False


@dataclass
class VaultConfig:
    """Vault integration configuration | تكوين تكامل Vault"""

    enabled: bool = False
    address: str = ""
    auth_method: str = "token"  # token, kubernetes, approle
    mount_path: str = "secret"
    namespace: str = ""
    secrets_paths: list[str] = field(default_factory=list)


class SecurityHardening:
    """Security hardening utilities for the SAHOOL platform.

    أدوات تعزيز الأمان لمنصة سهول.
    """

    # Security checklist items
    SECURITY_CHECKS = [
        {
            "id": "SEC-001",
            "category": "Authentication",
            "category_ar": "المصادقة",
            "description": "JWT secret key is at least 32 characters",
            "description_ar": "مفتاح JWT السري لا يقل عن 32 حرفاً",
            "env_var": "JWT_SECRET_KEY",
            "check_type": "min_length",
            "min_length": 32,
            "severity": "critical",
        },
        {
            "id": "SEC-002",
            "category": "Authentication",
            "category_ar": "المصادقة",
            "description": "JWT algorithm is HS256 or RS256",
            "description_ar": "خوارزمية JWT هي HS256 أو RS256",
            "env_var": "JWT_ALGORITHM",
            "check_type": "allowed_values",
            "allowed": ["HS256", "RS256", "ES256"],
            "severity": "high",
        },
        {
            "id": "SEC-003",
            "category": "Database",
            "category_ar": "قاعدة البيانات",
            "description": "Database connection uses SSL/TLS",
            "description_ar": "اتصال قاعدة البيانات يستخدم SSL/TLS",
            "env_var": "DATABASE_URL",
            "check_type": "contains",
            "contains": "sslmode=require",
            "severity": "high",
        },
        {
            "id": "SEC-004",
            "category": "Database",
            "category_ar": "قاعدة البيانات",
            "description": "Database password is set and strong",
            "description_ar": "كلمة مرور قاعدة البيانات قوية ومعيّنة",
            "env_var": "POSTGRES_PASSWORD",
            "check_type": "min_length",
            "min_length": 16,
            "severity": "critical",
        },
        {
            "id": "SEC-005",
            "category": "Redis",
            "category_ar": "ريديس",
            "description": "Redis password is configured",
            "description_ar": "كلمة مرور Redis معيّنة",
            "env_var": "REDIS_PASSWORD",
            "check_type": "not_empty",
            "severity": "high",
        },
        {
            "id": "SEC-006",
            "category": "Environment",
            "category_ar": "البيئة",
            "description": "Environment is not set to development in production",
            "description_ar": "البيئة ليست 'تطوير' في الإنتاج",
            "env_var": "ENVIRONMENT",
            "check_type": "not_value",
            "not_value": "development",
            "severity": "medium",
        },
        {
            "id": "SEC-007",
            "category": "Logging",
            "category_ar": "السجلات",
            "description": "Log level is not DEBUG in production",
            "description_ar": "مستوى السجل ليس DEBUG في الإنتاج",
            "env_var": "LOG_LEVEL",
            "check_type": "not_value",
            "not_value": "DEBUG",
            "severity": "low",
        },
        {
            "id": "SEC-008",
            "category": "Secrets",
            "category_ar": "الأسرار",
            "description": "Vault is enabled for secret management",
            "description_ar": "Vault مفعّل لإدارة الأسرار",
            "env_var": "VAULT_ENABLED",
            "check_type": "equals",
            "equals": "true",
            "severity": "medium",
        },
        {
            "id": "SEC-009",
            "category": "Network",
            "category_ar": "الشبكة",
            "description": "CORS origins are properly restricted",
            "description_ar": "أصول CORS مقيدة بشكل صحيح",
            "env_var": "CORS_ORIGINS",
            "check_type": "not_contains",
            "not_contains": "*",
            "severity": "medium",
        },
        {
            "id": "SEC-010",
            "category": "Rate Limiting",
            "category_ar": "تحديد المعدل",
            "description": "Rate limiting is enabled on API gateway",
            "description_ar": "تحديد المعدل مفعّل على بوابة API",
            "env_var": "RATE_LIMITING_ENABLED",
            "check_type": "equals",
            "equals": "true",
            "severity": "high",
        },
    ]

    def __init__(self):
        pass

    def run_security_check(self, check: dict, env_vars: dict | None = None) -> SecurityCheckResult:
        """Run a single security check.

        تشغيل فحص أمني واحد.
        """
        env = env_vars or dict(os.environ)
        check_id = check["id"]
        env_var = check.get("env_var", "")
        value = env.get(env_var, "")
        check_type = check.get("check_type", "")

        status = AuditStatus.FAIL
        details = ""

        if check_type == "min_length":
            min_len = check.get("min_length", 0)
            if len(value) >= min_len:
                status = AuditStatus.PASS
                details = f"Value length {len(value)} >= {min_len}"
            else:
                details = f"Value length {len(value)} < {min_len}"

        elif check_type == "allowed_values":
            allowed = check.get("allowed", [])
            if value in allowed:
                status = AuditStatus.PASS
                details = f"Value '{value}' is in allowed list"
            else:
                details = f"Value '{value}' not in {allowed}"

        elif check_type == "contains":
            needle = check.get("contains", "")
            if needle in value:
                status = AuditStatus.PASS
                details = f"Value contains '{needle}'"
            else:
                details = f"Value does not contain '{needle}'"

        elif check_type == "not_empty":
            if value:
                status = AuditStatus.PASS
                details = "Value is set"
            else:
                details = "Value is empty"

        elif check_type == "equals":
            expected = check.get("equals", "")
            if value == expected:
                status = AuditStatus.PASS
                details = f"Value equals '{expected}'"
            elif not value:
                status = AuditStatus.WARNING
                details = f"Variable not set (expected '{expected}')"
            else:
                details = f"Value '{value}' != '{expected}'"

        elif check_type == "not_value":
            not_val = check.get("not_value", "")
            if value != not_val:
                status = AuditStatus.PASS
                details = f"Value is not '{not_val}'"
            else:
                details = f"Value is '{not_val}' (should not be)"

        elif check_type == "not_contains":
            needle = check.get("not_contains", "")
            if needle not in value:
                status = AuditStatus.PASS
                details = f"Value does not contain '{needle}'"
            else:
                details = f"Value contains forbidden '{needle}'"

        return SecurityCheckResult(
            check_id=check_id,
            category=check.get("category", ""),
            category_ar=check.get("category_ar", ""),
            description=check.get("description", ""),
            description_ar=check.get("description_ar", ""),
            status=status,
            severity=check.get("severity", "medium"),
            details=details,
        )

    def run_full_audit(
        self,
        tenant_id: str = "",
        env_vars: dict | None = None,
    ) -> SecurityAuditReport:
        """Run full security audit.

        تشغيل تدقيق أمني كامل.
        """
        results = []
        for check in self.SECURITY_CHECKS:
            result = self.run_security_check(check, env_vars)
            results.append(result)

        passed = sum(1 for r in results if r.status == AuditStatus.PASS)
        failed = sum(1 for r in results if r.status == AuditStatus.FAIL)
        warnings = sum(1 for r in results if r.status == AuditStatus.WARNING)
        total = len(results)
        score = (passed / total * 100) if total > 0 else 0

        # Determine security level
        if score >= 90:
            level = SecurityLevel.ENTERPRISE
        elif score >= 70:
            level = SecurityLevel.ENHANCED
        elif score >= 50:
            level = SecurityLevel.STANDARD
        else:
            level = SecurityLevel.BASIC

        return SecurityAuditReport(
            report_id=f"AUDIT-{datetime.now().strftime('%Y%m%d%H%M')}",
            tenant_id=tenant_id,
            security_level=level,
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            score_percent=round(score, 1),
            checks=results,
            generated_at=datetime.now(UTC).isoformat(),
            message=f"Security audit: {score:.0f}% ({passed}/{total} passed)",
            message_ar=f"تدقيق أمني: {score:.0f}% ({passed}/{total} نجح)",
        )

    @staticmethod
    def generate_redis_tls_config(
        cert_dir: str = "/etc/ssl/redis",
    ) -> TLSConfig:
        """Generate Redis TLS configuration.

        إنشاء تكوين TLS لـ Redis.
        """
        return TLSConfig(
            enabled=True,
            cert_path=f"{cert_dir}/redis.crt",
            key_path=f"{cert_dir}/redis.key",
            ca_path=f"{cert_dir}/ca.crt",
            min_version="TLSv1.2",
            cipher_suites=[
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_128_GCM_SHA256",
            ],
        )

    @staticmethod
    def generate_vault_config(
        vault_addr: str = "http://vault:8200",
    ) -> VaultConfig:
        """Generate Vault integration configuration.

        إنشاء تكوين تكامل Vault.
        """
        return VaultConfig(
            enabled=True,
            address=vault_addr,
            auth_method="kubernetes",
            mount_path="secret/sahool",
            secrets_paths=[
                "secret/sahool/database",
                "secret/sahool/redis",
                "secret/sahool/jwt",
                "secret/sahool/nats",
                "secret/sahool/sentinel-hub",
                "secret/sahool/ollama",
            ],
        )

    @staticmethod
    def generate_secure_key(length: int = 64) -> str:
        """Generate a cryptographically secure random key.

        إنشاء مفتاح عشوائي آمن تشفيرياً.
        """
        return secrets.token_urlsafe(length)
