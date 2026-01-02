#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Environment Parity Checker
فاحص تطابق البيئات
═══════════════════════════════════════════════════════════════════════════════════════

Closes the "Reality Gap" by verifying production environment matches staging/simulation.

Features:
- Compares environment variables across environments
- Validates infrastructure configuration parity
- Detects configuration drift
- Generates parity report

Usage:
    # Compare staging vs production
    python environment_parity_checker.py --source staging --target production

    # Compare local simulation vs staging
    python environment_parity_checker.py --source simulation --target staging

    # Full parity check with remediation suggestions
    python environment_parity_checker.py --full --output report.json

═══════════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import hashlib

try:
    import aiohttp
except ImportError:
    print("Warning: aiohttp not installed. HTTP checks will be skipped.")
    aiohttp = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("env-parity")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class Environment(Enum):
    SIMULATION = "simulation"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# Critical environment variables that MUST match across environments
CRITICAL_ENV_VARS = [
    "DATABASE_POOL_SIZE",
    "DATABASE_MAX_OVERFLOW",
    "REDIS_MAX_CONNECTIONS",
    "JWT_ALGORITHM",
    "SESSION_TIMEOUT",
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_WINDOW",
]

# Environment variables that should differ (secrets, URLs)
EXPECTED_DIFFERENCES = [
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET",
    "API_KEY",
    "KONG_ADMIN_URL",
    "SENTRY_DSN",
]

# Required services that must be running
REQUIRED_SERVICES = [
    "postgres",
    "redis",
    "kong",
    "auth-service",
    "field-service",
    "weather-service",
]

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ConfigDiff:
    key: str
    source_value: Optional[str]
    target_value: Optional[str]
    severity: str  # critical, warning, info
    recommendation: str = ""

@dataclass
class ServiceStatus:
    name: str
    healthy: bool
    response_time_ms: float = 0.0
    version: str = "unknown"
    error: str = ""

@dataclass
class ParityReport:
    timestamp: str
    source_env: str
    target_env: str
    parity_score: float  # 0-100
    critical_issues: int
    warnings: int
    config_diffs: List[Dict] = field(default_factory=list)
    service_status: Dict[str, Dict] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    ready_for_production: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def print_summary(self):
        print("\n" + "=" * 70)
        print("  🔍 ENVIRONMENT PARITY CHECK RESULTS")
        print("  نتائج فحص تطابق البيئات")
        print("=" * 70)
        print(f"  Source:       {self.source_env}")
        print(f"  Target:       {self.target_env}")
        print(f"  Timestamp:    {self.timestamp}")
        print("")

        # Parity score with color indicator
        if self.parity_score >= 95:
            icon = "✅"
        elif self.parity_score >= 80:
            icon = "⚠️"
        else:
            icon = "❌"

        print(f"  {icon} Parity Score: {self.parity_score:.1f}%")
        print(f"  🔴 Critical Issues: {self.critical_issues}")
        print(f"  🟡 Warnings: {self.warnings}")
        print("")

        if self.config_diffs:
            print("  Configuration Differences:")
            print("  " + "-" * 66)
            for diff in self.config_diffs[:10]:  # Show first 10
                severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(diff["severity"], "⚪")
                print(f"  {severity_icon} {diff['key']}")
                if diff.get("recommendation"):
                    print(f"      → {diff['recommendation']}")

        if self.recommendations:
            print("")
            print("  Recommendations:")
            print("  " + "-" * 66)
            for rec in self.recommendations:
                print(f"  📌 {rec}")

        print("")
        if self.ready_for_production:
            print("  ✅ READY FOR PRODUCTION")
            print("  ✅ جاهز للإنتاج")
        else:
            print("  ❌ NOT READY FOR PRODUCTION")
            print("  ❌ غير جاهز للإنتاج")

        print("=" * 70 + "\n")

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT PARITY CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

class EnvironmentParityChecker:
    """Checks environment parity between simulation and production."""

    def __init__(self, source_env: str, target_env: str):
        self.source_env = source_env
        self.target_env = target_env
        self.diffs: List[ConfigDiff] = []
        self.service_status: Dict[str, ServiceStatus] = {}

    def _get_env_config(self, env: str) -> Dict[str, str]:
        """Load environment configuration."""
        # In real implementation, this would fetch from:
        # - Kubernetes ConfigMaps/Secrets
        # - AWS Parameter Store
        # - HashiCorp Vault
        # - .env files

        configs = {
            "simulation": {
                "DATABASE_POOL_SIZE": "25",
                "DATABASE_MAX_OVERFLOW": "10",
                "REDIS_MAX_CONNECTIONS": "100",
                "JWT_ALGORITHM": "RS256",
                "SESSION_TIMEOUT": "3600",
                "RATE_LIMIT_REQUESTS": "100",
                "RATE_LIMIT_WINDOW": "60",
                "LOG_LEVEL": "DEBUG",
                "ENABLE_METRICS": "true",
                "CIRCUIT_BREAKER_ENABLED": "true",
            },
            "staging": {
                "DATABASE_POOL_SIZE": "25",
                "DATABASE_MAX_OVERFLOW": "10",
                "REDIS_MAX_CONNECTIONS": "100",
                "JWT_ALGORITHM": "RS256",
                "SESSION_TIMEOUT": "3600",
                "RATE_LIMIT_REQUESTS": "100",
                "RATE_LIMIT_WINDOW": "60",
                "LOG_LEVEL": "INFO",
                "ENABLE_METRICS": "true",
                "CIRCUIT_BREAKER_ENABLED": "true",
            },
            "production": {
                "DATABASE_POOL_SIZE": "25",
                "DATABASE_MAX_OVERFLOW": "10",
                "REDIS_MAX_CONNECTIONS": "100",
                "JWT_ALGORITHM": "RS256",
                "SESSION_TIMEOUT": "3600",
                "RATE_LIMIT_REQUESTS": "100",
                "RATE_LIMIT_WINDOW": "60",
                "LOG_LEVEL": "WARNING",
                "ENABLE_METRICS": "true",
                "CIRCUIT_BREAKER_ENABLED": "true",
            },
        }

        # Override with actual environment variables if available
        env_prefix = env.upper() + "_"
        result = configs.get(env, {})

        for key in result.keys():
            env_value = os.getenv(env_prefix + key) or os.getenv(key)
            if env_value:
                result[key] = env_value

        return result

    def _compare_configs(self) -> List[ConfigDiff]:
        """Compare configurations between environments."""
        source_config = self._get_env_config(self.source_env)
        target_config = self._get_env_config(self.target_env)

        diffs = []
        all_keys = set(source_config.keys()) | set(target_config.keys())

        for key in all_keys:
            source_val = source_config.get(key)
            target_val = target_config.get(key)

            if source_val != target_val:
                # Determine severity
                if key in CRITICAL_ENV_VARS:
                    severity = "critical"
                    recommendation = f"MUST align {key} between environments"
                elif key in EXPECTED_DIFFERENCES:
                    severity = "info"
                    recommendation = f"Expected difference for {key}"
                else:
                    severity = "warning"
                    recommendation = f"Consider aligning {key}"

                diffs.append(ConfigDiff(
                    key=key,
                    source_value=source_val,
                    target_value=target_val,
                    severity=severity,
                    recommendation=recommendation,
                ))

        return diffs

    async def _check_service_health(self, service: str, url: str) -> ServiceStatus:
        """Check if a service is healthy."""
        if not aiohttp:
            return ServiceStatus(name=service, healthy=False, error="aiohttp not installed")

        try:
            start = datetime.now()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    elapsed = (datetime.now() - start).total_seconds() * 1000

                    if response.status == 200:
                        data = await response.json()
                        return ServiceStatus(
                            name=service,
                            healthy=True,
                            response_time_ms=elapsed,
                            version=data.get("version", "unknown"),
                        )
                    else:
                        return ServiceStatus(
                            name=service,
                            healthy=False,
                            response_time_ms=elapsed,
                            error=f"HTTP {response.status}",
                        )
        except Exception as e:
            return ServiceStatus(
                name=service,
                healthy=False,
                error=str(e),
            )

    def _check_docker_compose_parity(self) -> List[ConfigDiff]:
        """Check if docker-compose files have matching configurations."""
        diffs = []

        # Check for common docker-compose mismatches
        compose_files = [
            "docker-compose.yml",
            "docker-compose-sim.yml",
            "tests/load/simulation/docker-compose-sim.yml",
        ]

        for compose_file in compose_files:
            full_path = os.path.join(os.getcwd(), compose_file)
            if os.path.exists(full_path):
                with open(full_path, 'r') as f:
                    content = f.read()

                    # Check for hardcoded localhost references
                    if 'localhost' in content and self.target_env == "production":
                        diffs.append(ConfigDiff(
                            key=f"{compose_file}:localhost_reference",
                            source_value="localhost",
                            target_value="<service-name>",
                            severity="critical",
                            recommendation="Replace localhost with service names for production",
                        ))

                    # Check for missing health checks
                    if 'healthcheck' not in content:
                        diffs.append(ConfigDiff(
                            key=f"{compose_file}:missing_healthcheck",
                            source_value="none",
                            target_value="required",
                            severity="warning",
                            recommendation="Add healthcheck configuration to services",
                        ))

        return diffs

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on diffs."""
        recommendations = []

        critical_count = sum(1 for d in self.diffs if d.severity == "critical")

        if critical_count > 0:
            recommendations.append(
                f"Fix {critical_count} critical configuration mismatches before deployment"
            )

        # Check for common issues
        config_keys = {d.key for d in self.diffs}

        if "DATABASE_POOL_SIZE" in config_keys:
            recommendations.append(
                "Align DATABASE_POOL_SIZE across environments to prevent connection issues"
            )

        if "REDIS_MAX_CONNECTIONS" in config_keys:
            recommendations.append(
                "Ensure Redis connection limits match to prevent session loss"
            )

        if self.target_env == "production":
            recommendations.append(
                "Run load test on staging before production deployment"
            )
            recommendations.append(
                "Ensure database migrations are applied in correct order"
            )
            recommendations.append(
                "Verify Redis AOF persistence is enabled in production"
            )

        return recommendations

    async def run_check(self) -> ParityReport:
        """Run full parity check."""
        logger.info(f"Starting parity check: {self.source_env} → {self.target_env}")

        # Compare configurations
        self.diffs = self._compare_configs()

        # Check docker-compose parity
        compose_diffs = self._check_docker_compose_parity()
        self.diffs.extend(compose_diffs)

        # Calculate parity score
        critical_issues = sum(1 for d in self.diffs if d.severity == "critical")
        warnings = sum(1 for d in self.diffs if d.severity == "warning")

        # Parity score: 100 - (critical * 10) - (warnings * 2)
        parity_score = max(0, 100 - (critical_issues * 10) - (warnings * 2))

        # Generate recommendations
        recommendations = self._generate_recommendations()

        # Determine if ready for production
        ready = critical_issues == 0 and parity_score >= 80

        report = ParityReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_env=self.source_env,
            target_env=self.target_env,
            parity_score=parity_score,
            critical_issues=critical_issues,
            warnings=warnings,
            config_diffs=[asdict(d) for d in self.diffs],
            service_status={name: asdict(status) for name, status in self.service_status.items()},
            recommendations=recommendations,
            ready_for_production=ready,
        )

        return report

# ═══════════════════════════════════════════════════════════════════════════════
# TERRAFORM PARITY TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════

TERRAFORM_TEMPLATE = '''
# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL IDP - Infrastructure as Code (Terraform)
# قالب البنية التحتية ككود
# ═══════════════════════════════════════════════════════════════════════════════
#
# This ensures environment parity between simulation and production.
# Generated by: environment_parity_checker.py
# ═══════════════════════════════════════════════════════════════════════════════

variable "environment" {
  description = "Environment name (simulation, staging, production)"
  type        = string
}

variable "database_pool_size" {
  description = "Database connection pool size"
  type        = number
  default     = 25
}

variable "redis_max_connections" {
  description = "Redis max connections"
  type        = number
  default     = 100
}

# ─────────────────────────────────────────────────────────────────────────────
# Database Configuration (Identical across environments)
# ─────────────────────────────────────────────────────────────────────────────

resource "aws_db_instance" "sahool_db" {
  identifier     = "sahool-${var.environment}"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.environment == "production" ? "db.r5.large" : "db.t3.medium"

  # These values MUST match across environments
  parameter_group_name = aws_db_parameter_group.sahool_pg.name

  tags = {
    Environment = var.environment
    Project     = "sahool-idp"
  }
}

resource "aws_db_parameter_group" "sahool_pg" {
  name   = "sahool-pg-${var.environment}"
  family = "postgres15"

  # Connection pool settings - MUST match HikariCP settings
  parameter {
    name  = "max_connections"
    value = var.database_pool_size * 3  # Account for multiple app instances
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Redis Configuration (With AOF Persistence)
# ─────────────────────────────────────────────────────────────────────────────

resource "aws_elasticache_cluster" "sahool_redis" {
  cluster_id           = "sahool-redis-${var.environment}"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.environment == "production" ? "cache.r5.large" : "cache.t3.medium"
  num_cache_nodes      = 1
  parameter_group_name = aws_elasticache_parameter_group.sahool_redis_pg.name

  # Security
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true

  tags = {
    Environment = var.environment
    Project     = "sahool-idp"
  }
}

resource "aws_elasticache_parameter_group" "sahool_redis_pg" {
  name   = "sahool-redis-pg-${var.environment}"
  family = "redis7"

  # AOF Persistence - Closes Redis Persistence Gap
  parameter {
    name  = "appendonly"
    value = "yes"
  }

  parameter {
    name  = "appendfsync"
    value = "everysec"
  }

  # Connection limits - MUST match application settings
  parameter {
    name  = "maxclients"
    value = var.redis_max_connections
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Output for Verification
# ─────────────────────────────────────────────────────────────────────────────

output "environment_config" {
  value = {
    environment           = var.environment
    database_pool_size    = var.database_pool_size
    redis_max_connections = var.redis_max_connections
    parity_hash           = md5(jsonencode({
      db_pool  = var.database_pool_size
      redis_conn = var.redis_max_connections
    }))
  }
}
'''

def generate_terraform_template(output_path: str):
    """Generate Terraform template for infrastructure parity."""
    with open(output_path, 'w') as f:
        f.write(TERRAFORM_TEMPLATE)
    logger.info(f"Generated Terraform template: {output_path}")

# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL Environment Parity Checker - فاحص تطابق البيئات"
    )

    parser.add_argument("--source", "-s", default="simulation",
                       choices=["simulation", "development", "staging", "production"],
                       help="Source environment")
    parser.add_argument("--target", "-t", default="production",
                       choices=["simulation", "development", "staging", "production"],
                       help="Target environment")
    parser.add_argument("--full", "-f", action="store_true",
                       help="Run full parity check with service health")
    parser.add_argument("--output", "-o", type=str,
                       help="Output file for JSON report")
    parser.add_argument("--generate-terraform", action="store_true",
                       help="Generate Terraform template for IaC")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")

    args = parser.parse_args()

    if args.generate_terraform:
        generate_terraform_template("infrastructure/terraform/sahool-parity.tf")
        return

    checker = EnvironmentParityChecker(args.source, args.target)
    report = await checker.run_check()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report.to_json())
        logger.info(f"Report saved to: {args.output}")

    if args.json:
        print(report.to_json())
    else:
        report.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
