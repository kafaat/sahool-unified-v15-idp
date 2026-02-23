"""
Tests for SAHOOL Config Policy Engine
========================================
"""

import pytest

from shared.stability.config_policy import (
    ConfigPolicyEngine,
    PolicyRule,
    PolicySeverity,
    PolicyType,
    ValidationResult,
)


class TestConfigPolicyEngine:
    """Tests for the ConfigPolicyEngine."""

    def test_validate_clean_environment(self):
        """Test validation with all required vars set correctly."""
        env = {
            "ENVIRONMENT": "development",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/sahool?sslmode=require",
            "JWT_SECRET_KEY": "a" * 64,
            "NATS_URL": "nats://localhost:4222",
            "LOG_LEVEL": "INFO",
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        assert result.is_clean
        assert not result.has_critical
        assert not result.has_warnings

    def test_validate_missing_jwt_secret(self):
        """Test that short JWT secret is detected."""
        env = {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "short",
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        assert result.has_critical
        jwt_violations = [v for v in result.violations if v.variable == "JWT_SECRET_KEY"]
        assert len(jwt_violations) > 0
        assert "at least 32 characters" in jwt_violations[0].message

    def test_validate_invalid_environment(self):
        """Test that invalid ENVIRONMENT value is detected."""
        env = {
            "ENVIRONMENT": "invalid-env",
            "JWT_SECRET_KEY": "a" * 32,
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        env_violations = [v for v in result.violations if v.variable == "ENVIRONMENT"]
        assert len(env_violations) > 0
        assert "not in allowed values" in env_violations[0].message

    def test_validate_invalid_database_url(self):
        """Test that non-PostgreSQL DATABASE_URL is flagged."""
        env = {
            "ENVIRONMENT": "development",
            "DATABASE_URL": "mysql://invalid",
            "JWT_SECRET_KEY": "a" * 32,
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        db_violations = [v for v in result.violations if v.variable == "DATABASE_URL"]
        assert len(db_violations) > 0

    def test_validate_invalid_nats_url(self):
        """Test that non-nats:// NATS_URL is flagged."""
        env = {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32,
            "NATS_URL": "http://wrong-protocol",
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        nats_violations = [v for v in result.violations if v.variable == "NATS_URL"]
        assert len(nats_violations) > 0

    def test_production_requires_ssl(self):
        """Test that production enforces SSL on DATABASE_URL."""
        env = {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/sahool",
            "JWT_SECRET_KEY": "a" * 64,
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        ssl_violations = [
            v for v in result.violations
            if v.variable == "DATABASE_URL" and "SSL" in v.message
        ]
        assert len(ssl_violations) > 0

    def test_production_requires_longer_jwt(self):
        """Test that production requires 64-char JWT secret."""
        env = {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/sahool?sslmode=require",
            "JWT_SECRET_KEY": "a" * 40,  # 40 chars, not 64
        }
        engine = ConfigPolicyEngine(service_name="test", env_override=env)
        result = engine.validate()

        jwt_violations = [
            v for v in result.violations
            if v.variable == "JWT_SECRET_KEY" and "64 characters" in v.message
        ]
        assert len(jwt_violations) > 0

    def test_custom_rules(self):
        """Test adding custom service-specific rules."""
        custom_rule = PolicyRule(
            variable="CUSTOM_API_KEY",
            policy_type=PolicyType.MIN_LENGTH,
            severity=PolicySeverity.WARNING,
            min_length=20,
            description="Custom API key must be at least 20 chars",
        )
        env = {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32,
            "CUSTOM_API_KEY": "short",
        }
        engine = ConfigPolicyEngine(
            service_name="test",
            env_override=env,
            additional_rules=[custom_rule],
        )
        result = engine.validate()

        custom_violations = [v for v in result.violations if v.variable == "CUSTOM_API_KEY"]
        assert len(custom_violations) > 0

    def test_port_range_validation(self):
        """Test port range policy type."""
        rule = PolicyRule(
            variable="SERVICE_PORT",
            policy_type=PolicyType.PORT_RANGE,
            severity=PolicySeverity.WARNING,
            port_min=1024,
            port_max=65535,
        )
        env = {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32,
            "SERVICE_PORT": "80",  # Below 1024
        }
        engine = ConfigPolicyEngine(
            service_name="test",
            env_override=env,
            additional_rules=[rule],
        )
        result = engine.validate()

        port_violations = [v for v in result.violations if v.variable == "SERVICE_PORT"]
        assert len(port_violations) > 0

    def test_conditional_validation(self):
        """Test conditional policy type."""
        rule = PolicyRule(
            variable="REDIS_PASSWORD",
            policy_type=PolicyType.CONDITIONAL,
            severity=PolicySeverity.WARNING,
            condition_variable="REDIS_URL",
            description="REDIS_PASSWORD required when REDIS_URL is set",
        )
        env = {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32,
            "REDIS_URL": "redis://localhost:6379",
            # No REDIS_PASSWORD
        }
        engine = ConfigPolicyEngine(
            service_name="test",
            env_override=env,
            additional_rules=[rule],
        )
        result = engine.validate()

        redis_violations = [v for v in result.violations if v.variable == "REDIS_PASSWORD"]
        assert len(redis_violations) > 0

    def test_validation_result_summary(self):
        """Test that summary output is structured correctly."""
        env = {
            "ENVIRONMENT": "invalid",
            "JWT_SECRET_KEY": "short",
        }
        engine = ConfigPolicyEngine(service_name="test-service", env_override=env)
        result = engine.validate()
        summary = result.summary()

        assert summary["service"] == "test-service"
        assert summary["total_violations"] > 0
        assert isinstance(summary["violations"], list)

    def test_get_rules_summary(self):
        """Test rules summary output."""
        engine = ConfigPolicyEngine(service_name="test", env_override={"ENVIRONMENT": "development"})
        summary = engine.get_rules_summary()

        assert len(summary) > 0
        assert all("variable" in r for r in summary)
        assert all("type" in r for r in summary)
