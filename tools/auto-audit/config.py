#!/usr/bin/env python3
"""
SAHOOL Auto Audit Tools - Configuration
Central configuration for all audit tools
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Environment(str, Enum):
    """Deployment environment"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database connection configuration"""

    host: str = "localhost"
    port: int = 5432
    database: str = "sahool"
    user: str = "sahool"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 5

    @classmethod
    def from_env(cls) -> DatabaseConfig:
        """Load configuration from environment variables"""
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "sahool"),
            user=os.getenv("POSTGRES_USER", "sahool"),
            password=os.getenv("POSTGRES_PASSWORD", ""),
            ssl_mode=os.getenv("POSTGRES_SSL_MODE", "prefer"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        )


@dataclass
class AnalyzerConfig:
    """Audit Log Analyzer configuration"""

    # Activity thresholds
    high_activity_threshold: int = 100  # Events per hour
    suspicious_hours: set[int] = field(default_factory=lambda: {0, 1, 2, 3, 4, 5})

    # Sensitive actions
    sensitive_actions: set[str] = field(
        default_factory=lambda: {
            "user.delete",
            "user.role.assign",
            "permission.grant",
            "data.export",
            "data.bulk_delete",
            "config.change",
            "api_key.create",
            "api_key.delete",
        }
    )

    # Report settings
    top_items_count: int = 20
    max_risk_indicators: int = 100


@dataclass
class ValidatorConfig:
    """Hash Chain Validator configuration"""

    # Validation settings
    parallel_validation: bool = True
    segment_size: int = 1000
    max_errors_to_report: int = 100

    # Recovery settings
    generate_recovery_report: bool = True
    anchor_search_limit: int = 10000


@dataclass
class ComplianceConfig:
    """Compliance Reporter configuration"""

    # Assessment settings
    default_assessment_period_days: int = 90
    minimum_evidence_items: int = 5
    strong_evidence_threshold: int = 20

    # Framework settings
    enabled_frameworks: list[str] = field(default_factory=lambda: ["gdpr", "soc2", "iso27001"])

    # Report settings
    max_recommendations: int = 30
    max_critical_findings: int = 50


@dataclass
class AnomalyConfig:
    """Anomaly Detector configuration"""

    # Statistical thresholds
    z_score_threshold: float = 3.0
    iqr_multiplier: float = 1.5

    # Time-based settings
    unusual_hour_threshold: float = 0.05
    velocity_threshold: int = 10  # Events per minute

    # Baseline settings
    baseline_period_days: int = 30
    minimum_baseline_events: int = 10

    # Threat scoring weights
    severity_weights: dict[str, int] = field(
        default_factory=lambda: {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
            "info": 1,
        }
    )

    # Detection rules
    brute_force_threshold: int = 5
    brute_force_window_seconds: int = 300
    data_exfiltration_threshold: int = 3


@dataclass
class ExporterConfig:
    """Audit Data Exporter configuration"""

    # Export settings
    default_batch_size: int = 10000
    default_redaction_level: str = "standard"

    # PII fields by level
    pii_fields_basic: set[str] = field(
        default_factory=lambda: {
            "password",
            "token",
            "secret",
            "api_key",
            "apikey",
            "auth",
            "credential",
        }
    )
    pii_fields_standard: set[str] = field(
        default_factory=lambda: {
            "ip",
            "ip_address",
            "email",
            "phone",
            "ssn",
            "credit_card",
            "card_number",
        }
    )
    pii_fields_strict: set[str] = field(
        default_factory=lambda: {
            "name",
            "first_name",
            "last_name",
            "username",
            "user_id",
            "actor_id",
            "address",
            "location",
        }
    )

    # SIEM settings
    splunk_index: str = "audit"
    elk_index: str = "sahool-audit"
    syslog_facility: int = 4  # Security facility


@dataclass
class AuditToolsConfig:
    """Main configuration for all audit tools"""

    environment: Environment = Environment.DEVELOPMENT
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    anomaly: AnomalyConfig = field(default_factory=AnomalyConfig)
    exporter: ExporterConfig = field(default_factory=ExporterConfig)

    # Global settings
    output_dir: Path = Path("audit_reports")
    log_level: str = "INFO"
    enable_telemetry: bool = False

    @classmethod
    def from_env(cls) -> AuditToolsConfig:
        """Load configuration from environment variables"""
        env_str = os.getenv("SAHOOL_ENV", "development").lower()
        env_map = {
            "development": Environment.DEVELOPMENT,
            "staging": Environment.STAGING,
            "production": Environment.PRODUCTION,
        }

        return cls(
            environment=env_map.get(env_str, Environment.DEVELOPMENT),
            database=DatabaseConfig.from_env(),
            output_dir=Path(os.getenv("AUDIT_OUTPUT_DIR", "audit_reports")),
            log_level=os.getenv("AUDIT_LOG_LEVEL", "INFO"),
            enable_telemetry=os.getenv("AUDIT_TELEMETRY", "false").lower() == "true",
        )


# Singleton configuration instance
_config: AuditToolsConfig | None = None


def get_config() -> AuditToolsConfig:
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = AuditToolsConfig.from_env()
    return _config


def set_config(config: AuditToolsConfig) -> None:
    """Set the global configuration instance"""
    global _config
    _config = config
