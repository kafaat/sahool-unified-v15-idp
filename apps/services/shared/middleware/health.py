"""
SAHOOL Services - Health Check Endpoints
نقاط فحص صحة الخدمات

Provides standardized health check endpoints for Kubernetes:
- /healthz - Basic health check (liveness probe)
- /readyz - Readiness check (readiness probe)
- /livez - Kubernetes liveness probe

Version: 1.0.0
Created: 2024
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Status Types
# ═══════════════════════════════════════════════════════════════════════════════

class HealthStatus(str, Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: Optional[str] = None
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ServiceHealth:
    """Overall service health status."""
    status: HealthStatus
    service_name: str
    version: str
    uptime_seconds: float
    checks: List[HealthCheckResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "status": self.status.value,
            "service": self.service_name,
            "version": self.version,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check Manager
# ═══════════════════════════════════════════════════════════════════════════════

class HealthCheckManager:
    """Manages health checks for a service."""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
    ):
        self.service_name = service_name
        self.version = version
        self.start_time = time.time()
        self._checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self._ready = True

    def register_check(
        self,
        name: str,
        check_func: Callable[[], HealthCheckResult],
    ) -> None:
        """Register a health check function.

        Args:
            name: Name of the health check
            check_func: Function that returns HealthCheckResult
        """
        self._checks[name] = check_func
        logger.debug(f"Registered health check: {name}")

    def set_ready(self, ready: bool) -> None:
        """Set service readiness state."""
        self._ready = ready
        logger.info(f"Service readiness set to: {ready}")

    @property
    def uptime(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.start_time

    async def run_checks(self) -> ServiceHealth:
        """Run all registered health checks."""
        results = []
        overall_status = HealthStatus.HEALTHY

        for name, check_func in self._checks.items():
            try:
                start = time.time()
                result = check_func()
                result.latency_ms = (time.time() - start) * 1000
                results.append(result)

                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status != HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results.append(HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                ))
                overall_status = HealthStatus.UNHEALTHY

        return ServiceHealth(
            status=overall_status,
            service_name=self.service_name,
            version=self.version,
            uptime_seconds=self.uptime,
            checks=results,
        )

    def liveness_check(self) -> Dict[str, Any]:
        """Simple liveness check - is the process alive?"""
        return {
            "status": "alive",
            "service": self.service_name,
            "uptime_seconds": round(self.uptime, 2),
        }

    async def readiness_check(self) -> tuple[bool, Dict[str, Any]]:
        """Readiness check - is the service ready to accept traffic?"""
        if not self._ready:
            return False, {
                "status": "not_ready",
                "service": self.service_name,
                "message": "Service is not ready",
            }

        health = await self.run_checks()
        is_ready = health.status != HealthStatus.UNHEALTHY

        return is_ready, health.to_dict()


# ═══════════════════════════════════════════════════════════════════════════════
# Common Health Checks
# ═══════════════════════════════════════════════════════════════════════════════

def create_database_check(
    check_func: Callable[[], bool],
    name: str = "database",
) -> Callable[[], HealthCheckResult]:
    """Create a database health check.

    Args:
        check_func: Function that returns True if database is healthy
        name: Name for the health check

    Returns:
        Health check function
    """
    def check() -> HealthCheckResult:
        try:
            if check_func():
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message="Database connection OK",
                )
            else:
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message="Database connection failed",
                )
        except Exception as e:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database check error: {str(e)}",
            )

    return check


def create_redis_check(
    redis_url: Optional[str] = None,
    name: str = "redis",
) -> Callable[[], HealthCheckResult]:
    """Create a Redis health check.

    Args:
        redis_url: Redis connection URL
        name: Name for the health check

    Returns:
        Health check function
    """
    def check() -> HealthCheckResult:
        url = redis_url or os.getenv("REDIS_URL")
        if not url:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.DEGRADED,
                message="Redis not configured",
            )

        try:
            import redis
            r = redis.from_url(url)
            r.ping()
            return HealthCheckResult(
                name=name,
                status=HealthStatus.HEALTHY,
                message="Redis connection OK",
            )
        except ImportError:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.DEGRADED,
                message="Redis package not installed",
            )
        except Exception as e:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
            )

    return check


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Integration
# ═══════════════════════════════════════════════════════════════════════════════

def setup_health_endpoints(
    app: FastAPI,
    service_name: Optional[str] = None,
    version: Optional[str] = None,
    include_livez: bool = True,
    include_readyz: bool = True,
    include_healthz: bool = True,
) -> HealthCheckManager:
    """Set up health check endpoints for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Service name (defaults to app.title)
        version: Service version (defaults to app.version)
        include_livez: Include /livez endpoint
        include_readyz: Include /readyz endpoint
        include_healthz: Include /healthz endpoint

    Returns:
        HealthCheckManager instance for registering custom checks

    Usage:
        from apps.services.shared.middleware import setup_health_endpoints

        app = FastAPI(title="My Service", version="1.0.0")
        health_manager = setup_health_endpoints(app)

        # Register custom checks
        health_manager.register_check("database", my_db_check)
    """
    name = service_name or getattr(app, "title", "unknown")
    ver = version or getattr(app, "version", "1.0.0")

    manager = HealthCheckManager(service_name=name, version=ver)

    if include_livez:
        @app.get("/livez", tags=["Health"])
        async def livez():
            """Kubernetes liveness probe - is the process alive?"""
            return manager.liveness_check()

    if include_healthz:
        @app.get("/healthz", tags=["Health"])
        async def healthz():
            """Basic health check endpoint."""
            return manager.liveness_check()

    if include_readyz:
        @app.get("/readyz", tags=["Health"])
        async def readyz(response: Response):
            """Kubernetes readiness probe - is the service ready?"""
            is_ready, health_data = await manager.readiness_check()

            if not is_ready:
                response.status_code = 503

            return health_data

    logger.info(f"Health endpoints configured for {name} v{ver}")

    return manager
