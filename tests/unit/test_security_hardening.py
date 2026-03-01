"""Tests for security hardening module."""
import pytest
from shared.security.hardening import (
    SecurityHardening,
    SecurityLevel,
    AuditStatus,
)


class TestSecurityHardening:
    def setup_method(self):
        self.sec = SecurityHardening()

    def test_full_audit_secure(self):
        env = {
            "JWT_SECRET_KEY": "a" * 64,
            "JWT_ALGORITHM": "HS256",
            "DATABASE_URL": "postgresql://u:p@host/db?sslmode=require",
            "POSTGRES_PASSWORD": "a" * 32,
            "REDIS_PASSWORD": "secure_redis_password",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "VAULT_ENABLED": "true",
            "CORS_ORIGINS": "https://sahool.app",
            "RATE_LIMITING_ENABLED": "true",
        }
        report = self.sec.run_full_audit(tenant_id="test", env_vars=env)
        assert report.score_percent >= 90
        assert report.security_level == SecurityLevel.ENTERPRISE

    def test_full_audit_insecure(self):
        env = {
            "JWT_SECRET_KEY": "short",
            "JWT_ALGORITHM": "none",
            "DATABASE_URL": "postgresql://host/db",
            "POSTGRES_PASSWORD": "123",
            "REDIS_PASSWORD": "",
            "ENVIRONMENT": "development",
            "LOG_LEVEL": "DEBUG",
        }
        report = self.sec.run_full_audit(tenant_id="test", env_vars=env)
        assert report.score_percent < 50
        assert report.failed > 0

    def test_redis_tls_config(self):
        config = SecurityHardening.generate_redis_tls_config()
        assert config.enabled is True
        assert config.min_version == "TLSv1.2"
        assert len(config.cipher_suites) > 0

    def test_vault_config(self):
        config = SecurityHardening.generate_vault_config()
        assert config.enabled is True
        assert len(config.secrets_paths) > 0

    def test_generate_secure_key(self):
        key1 = SecurityHardening.generate_secure_key()
        key2 = SecurityHardening.generate_secure_key()
        assert key1 != key2
        assert len(key1) > 32

    def test_individual_check(self):
        check = {
            "id": "TEST-001",
            "category": "Test",
            "category_ar": "اختبار",
            "description": "Test check",
            "description_ar": "فحص اختبار",
            "env_var": "TEST_VAR",
            "check_type": "not_empty",
            "severity": "low",
        }
        result = self.sec.run_security_check(check, {"TEST_VAR": "value"})
        assert result.status == AuditStatus.PASS

        result = self.sec.run_security_check(check, {"TEST_VAR": ""})
        assert result.status == AuditStatus.FAIL
