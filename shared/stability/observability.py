"""
SAHOOL Stability Observability Kit
=====================================
حزمة المراقبة لإطار الاستقرار

Unified observability utilities that tie stability metrics together:
- Stability health check endpoint (aggregates all drift/contract/config checks)
- Stability metrics (Prometheus-compatible)
- SLI/SLO measurement helpers
- Structured stability event logging

Usage:
    from shared.stability.observability import StabilityHealthCheck, StabilityMetrics

    # Add stability health check to FastAPI app
    health = StabilityHealthCheck(service_name="advisory-service")
    app.include_router(health.router)

    # Record stability metrics
    metrics = StabilityMetrics(service_name="advisory-service")
    metrics.record_drift_check(drift_count=3, check_duration_ms=150)
    metrics.record_contract_violation(contract_type="event", severity="warning")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)


@dataclass
class StabilityStatus:
    """Aggregated stability status for a service."""

    service_name: str
    status: str = "healthy"  # healthy, degraded, unhealthy
    config_policy: str = "pass"
    drift_checks: str = "pass"
    contract_checks: str = "pass"
    last_check_timestamp: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service_name,
            "stability_status": self.status,
            "checks": {
                "config_policy": self.config_policy,
                "drift": self.drift_checks,
                "contracts": self.contract_checks,
            },
            "last_check": self.last_check_timestamp,
            "details": self.details,
        }


class StabilityHealthCheck:
    """
    Stability-aware health check endpoint for FastAPI services.
    نقطة فحص صحة الاستقرار لخدمات FastAPI.

    Adds a /stability/health endpoint that aggregates:
    - Config policy validation result
    - Drift detection summary
    - Contract compliance status

    This is separate from /healthz (liveness) and /readyz (readiness).
    It reports the platform stability posture of the service.
    """

    def __init__(self, service_name: str, service_version: str = "16.0.0"):
        self.service_name = service_name
        self.service_version = service_version
        self._status = StabilityStatus(service_name=service_name)
        self._last_config_result: Any = None
        self._last_drift_result: Any = None
        self._last_contract_result: Any = None
        self.router = APIRouter(tags=["stability"])
        self._setup_routes()

    def _setup_routes(self):
        """Register stability endpoints."""

        @self.router.get("/stability/health")
        async def stability_health():
            """
            Stability health check endpoint.
            Returns aggregated stability status.
            """
            return self._status.to_dict()

        @self.router.get("/stability/config")
        async def stability_config():
            """Config policy validation status."""
            if self._last_config_result:
                return self._last_config_result.summary()
            return {"status": "not_checked"}

        @self.router.get("/stability/drift")
        async def stability_drift():
            """Drift detection status."""
            if self._last_drift_result:
                return self._last_drift_result.summary()
            return {"status": "not_checked"}

        @self.router.get("/stability/contracts")
        async def stability_contracts():
            """Contract compliance status."""
            if self._last_contract_result:
                return self._last_contract_result.summary()
            return {"status": "not_checked"}

    def update_config_status(self, result: Any) -> None:
        """Update config policy validation status."""
        self._last_config_result = result
        if hasattr(result, "has_critical") and result.has_critical:
            self._status.config_policy = "fail"
        elif hasattr(result, "has_warnings") and result.has_warnings:
            self._status.config_policy = "warn"
        else:
            self._status.config_policy = "pass"
        self._recalculate_status()

    def update_drift_status(self, result: Any) -> None:
        """Update drift detection status."""
        self._last_drift_result = result
        if hasattr(result, "has_critical") and result.has_critical:
            self._status.drift_checks = "fail"
        elif hasattr(result, "items") and len(result.items) > 0:
            self._status.drift_checks = "warn"
        else:
            self._status.drift_checks = "pass"
        self._recalculate_status()

    def update_contract_status(self, result: Any) -> None:
        """Update contract compliance status."""
        self._last_contract_result = result
        if hasattr(result, "has_breaking") and result.has_breaking:
            self._status.contract_checks = "fail"
        elif hasattr(result, "violations") and len(result.violations) > 0:
            self._status.contract_checks = "warn"
        else:
            self._status.contract_checks = "pass"
        self._recalculate_status()

    def _recalculate_status(self) -> None:
        """Recalculate overall stability status."""
        from datetime import UTC, datetime

        self._status.last_check_timestamp = datetime.now(UTC).isoformat()

        checks = [
            self._status.config_policy,
            self._status.drift_checks,
            self._status.contract_checks,
        ]

        if "fail" in checks:
            self._status.status = "unhealthy"
        elif "warn" in checks:
            self._status.status = "degraded"
        else:
            self._status.status = "healthy"


class StabilityMetrics:
    """
    Stability-specific metrics collector.
    جامع مقاييس الاستقرار.

    Provides in-memory counters/gauges for stability events.
    Compatible with Prometheus scraping via /stability/metrics endpoint.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._counters: dict[str, int] = {
            "drift_checks_total": 0,
            "drift_items_total": 0,
            "contract_checks_total": 0,
            "contract_violations_total": 0,
            "config_validations_total": 0,
            "config_violations_total": 0,
            "remediation_actions_total": 0,
            "remediation_auto_fixed_total": 0,
        }
        self._gauges: dict[str, float] = {
            "drift_check_duration_ms": 0.0,
            "contract_check_duration_ms": 0.0,
            "stability_score": 100.0,  # 0-100, 100 = fully stable
        }

    def record_drift_check(self, drift_count: int, check_duration_ms: float) -> None:
        """Record a drift detection run."""
        self._counters["drift_checks_total"] += 1
        self._counters["drift_items_total"] += drift_count
        self._gauges["drift_check_duration_ms"] = check_duration_ms
        self._recalculate_score()

    def record_contract_violation(self, contract_type: str, severity: str) -> None:
        """Record a contract violation."""
        self._counters["contract_violations_total"] += 1

    def record_config_validation(self, violations: int) -> None:
        """Record a config validation run."""
        self._counters["config_validations_total"] += 1
        self._counters["config_violations_total"] += violations
        self._recalculate_score()

    def record_remediation(self, auto_fixed: bool = False) -> None:
        """Record a remediation action."""
        self._counters["remediation_actions_total"] += 1
        if auto_fixed:
            self._counters["remediation_auto_fixed_total"] += 1

    def _recalculate_score(self) -> None:
        """Recalculate the overall stability score (0-100)."""
        # Simple scoring: start at 100, deduct for issues
        score = 100.0
        score -= min(self._counters["drift_items_total"] * 2, 30)
        score -= min(self._counters["contract_violations_total"] * 5, 30)
        score -= min(self._counters["config_violations_total"] * 3, 20)
        self._gauges["stability_score"] = max(0.0, score)

    def to_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format.
        تصدير المقاييس بتنسيق Prometheus.
        """
        lines = []
        service = self.service_name

        for name, value in self._counters.items():
            lines.append(f"# TYPE sahool_stability_{name} counter")
            lines.append(f'sahool_stability_{name}{{service="{service}"}} {value}')

        for name, value in self._gauges.items():
            lines.append(f"# TYPE sahool_stability_{name} gauge")
            lines.append(f'sahool_stability_{name}{{service="{service}"}} {value}')

        return "\n".join(lines) + "\n"

    def summary(self) -> dict[str, Any]:
        return {
            "service": self.service_name,
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }


def run_startup_stability_checks(
    service_name: str,
    service_version: str = "16.0.0",
    fail_on_critical: bool = True,
) -> StabilityStatus:
    """
    Run all stability checks at service startup.
    تشغيل جميع فحوصات الاستقرار عند بدء تشغيل الخدمة.

    This is the recommended single-call for service lifespan startup.
    Runs config policy validation and drift detection, logs results,
    and optionally fails startup on critical issues.

    Usage in main.py:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            from shared.stability.observability import run_startup_stability_checks

            status = run_startup_stability_checks(
                service_name="advisory-service",
                fail_on_critical=True,
            )
            app.state.stability_status = status
            yield
    """
    from datetime import UTC, datetime

    status = StabilityStatus(
        service_name=service_name,
        last_check_timestamp=datetime.now(UTC).isoformat(),
    )

    # 1. Config policy validation
    try:
        from shared.stability.config_policy import ConfigPolicyEngine

        engine = ConfigPolicyEngine(service_name=service_name)
        config_result = engine.validate()

        if config_result.has_critical:
            status.config_policy = "fail"
            status.details["config_violations"] = config_result.critical_count
            logger.error(
                "Config policy CRITICAL violations: service=%s violations=%s",
                service_name,
                config_result.summary(),
            )
            if fail_on_critical:
                raise SystemExit(
                    f"[{service_name}] Config policy has {config_result.critical_count} critical violations"
                )
        elif config_result.has_warnings:
            status.config_policy = "warn"
            status.details["config_warnings"] = config_result.warning_count
            logger.warning(
                "Config policy warnings: service=%s warnings=%s", service_name, config_result.warnings_summary()
            )
        else:
            status.config_policy = "pass"
            logger.info("Config policy validation passed: service=%s", service_name)

    except (ImportError, SystemExit):
        raise
    except Exception as e:
        logger.warning(f"Config policy validation error: {e}")
        status.config_policy = "error"

    # 2. Drift detection (non-blocking)
    try:
        from shared.stability.drift_detector import DriftDetector

        detector = DriftDetector()
        drift_result = detector.detect_config_drift()

        if drift_result.has_critical:
            status.drift_checks = "fail"
            status.details["drift_critical"] = sum(1 for d in drift_result.items if d.severity.value == "critical")
        elif len(drift_result.items) > 0:
            status.drift_checks = "warn"
            status.details["drift_items"] = len(drift_result.items)
        else:
            status.drift_checks = "pass"

        logger.info(
            "Drift detection complete: service=%s drift_items=%d",
            service_name,
            len(drift_result.items),
        )

    except Exception as e:
        logger.warning(f"Drift detection error: {e}")
        status.drift_checks = "error"

    # Calculate overall status
    checks = [status.config_policy, status.drift_checks, status.contract_checks]
    if "fail" in checks:
        status.status = "unhealthy"
    elif "warn" in checks or "error" in checks:
        status.status = "degraded"
    else:
        status.status = "healthy"

    logger.info(
        "Stability checks complete: service=%s status=%s config=%s drift=%s",
        service_name,
        status.status,
        status.config_policy,
        status.drift_checks,
    )

    return status
