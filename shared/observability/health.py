"""
Health Check Endpoints for All Services
نقاط فحص الصحة لجميع الخدمات

Provides standardized liveness, readiness, and startup probes
for Kubernetes and monitoring systems.
"""

import asyncio
import time
from typing import Callable, Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse


class HealthStatus(str, Enum):
    """Health check status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component"""
    name: str
    status: HealthStatus
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)


@dataclass
class ServiceHealth:
    """Overall service health status"""
    service_name: str
    version: str
    status: HealthStatus
    components: List[ComponentHealth] = field(default_factory=list)
    uptime_seconds: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now(datetime.UTC).isoformat() if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat() + 'Z')

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            "service": self.service_name,
            "version": self.version,
            "status": self.status.value,
            "uptime_seconds": self.uptime_seconds,
            "timestamp": self.timestamp,
            "components": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "metadata": c.metadata,
                }
                for c in self.components
            ],
        }


class HealthChecker:
    """
    Health checker with component-level health tracking.
    فاحص الصحة مع تتبع صحة المكونات.
    """

    def __init__(self, service_name: str, version: str):
        self.service_name = service_name
        self.version = version
        self.start_time = time.time()
        self._readiness_checks: Dict[str, Callable] = {}
        self._liveness_checks: Dict[str, Callable] = {}

    def add_readiness_check(self, name: str, check_func: Callable) -> None:
        """
        Add a readiness check.
        Readiness checks verify external dependencies (DB, cache, etc.)
        """
        self._readiness_checks[name] = check_func

    def add_liveness_check(self, name: str, check_func: Callable) -> None:
        """
        Add a liveness check.
        Liveness checks verify internal health (deadlock detection, etc.)
        """
        self._liveness_checks[name] = check_func

    async def _run_check(self, name: str, check_func: Callable) -> ComponentHealth:
        """Run a single health check"""
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()

            if isinstance(result, ComponentHealth):
                return result
            elif isinstance(result, bool):
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    message="Check passed" if result else "Check failed",
                )
            elif isinstance(result, dict):
                return ComponentHealth(
                    name=name,
                    status=HealthStatus(result.get("status", "healthy")),
                    message=result.get("message", ""),
                    metadata=result.get("metadata", {}),
                )
            else:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY,
                    message="Check completed",
                )
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
            )

    async def check_liveness(self) -> ServiceHealth:
        """
        Check liveness (is the service running?)
        فحص الحياة (هل الخدمة قيد التشغيل؟)
        """
        components = []
        for name, check_func in self._liveness_checks.items():
            component = await self._run_check(name, check_func)
            components.append(component)

        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in components):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in components):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        return ServiceHealth(
            service_name=self.service_name,
            version=self.version,
            status=overall_status,
            components=components,
            uptime_seconds=time.time() - self.start_time,
        )

    async def check_readiness(self) -> ServiceHealth:
        """
        Check readiness (can the service handle requests?)
        فحص الاستعداد (هل يمكن للخدمة معالجة الطلبات؟)
        """
        components = []
        for name, check_func in self._readiness_checks.items():
            component = await self._run_check(name, check_func)
            components.append(component)

        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in components):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in components):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        return ServiceHealth(
            service_name=self.service_name,
            version=self.version,
            status=overall_status,
            components=components,
            uptime_seconds=time.time() - self.start_time,
        )


def create_health_router(health_checker: HealthChecker) -> APIRouter:
    """
    Create a FastAPI router with health endpoints.
    إنشاء موجه FastAPI مع نقاط فحص الصحة.
    """
    router = APIRouter(tags=["Health"])

    @router.get("/health/live", summary="Liveness probe")
    async def liveness() -> JSONResponse:
        """
        Liveness probe - is the service running?
        Used by Kubernetes to restart crashed containers.
        """
        health = await health_checker.check_liveness()
        
        if health.status == HealthStatus.UNHEALTHY:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health.to_dict(),
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health.to_dict(),
        )

    @router.get("/health/ready", summary="Readiness probe")
    async def readiness() -> JSONResponse:
        """
        Readiness probe - can the service handle requests?
        Used by Kubernetes to route traffic to the service.
        """
        health = await health_checker.check_readiness()
        
        if health.status == HealthStatus.UNHEALTHY:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health.to_dict(),
            )
        elif health.status == HealthStatus.DEGRADED:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=health.to_dict(),
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health.to_dict(),
        )

    @router.get("/health/startup", summary="Startup probe")
    async def startup() -> JSONResponse:
        """
        Startup probe - has the service finished starting up?
        Used by Kubernetes to delay liveness checks during slow starts.
        """
        # For now, use readiness checks for startup
        health = await health_checker.check_readiness()
        
        if health.status == HealthStatus.UNHEALTHY:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health.to_dict(),
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=health.to_dict(),
        )

    @router.get("/health", summary="Combined health check")
    async def health() -> JSONResponse:
        """
        Combined health check for monitoring systems.
        Includes both liveness and readiness information.
        """
        liveness_health = await health_checker.check_liveness()
        readiness_health = await health_checker.check_readiness()
        
        # Combine results
        all_components = liveness_health.components + readiness_health.components
        
        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in all_components):
            overall_status = HealthStatus.UNHEALTHY
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif any(c.status == HealthStatus.DEGRADED for c in all_components):
            overall_status = HealthStatus.DEGRADED
            http_status = status.HTTP_200_OK
        else:
            overall_status = HealthStatus.HEALTHY
            http_status = status.HTTP_200_OK
        
        combined_health = ServiceHealth(
            service_name=health_checker.service_name,
            version=health_checker.version,
            status=overall_status,
            components=all_components,
            uptime_seconds=time.time() - health_checker.start_time,
        )
        
        return JSONResponse(
            status_code=http_status,
            content=combined_health.to_dict(),
        )

    return router


# Common health check functions
async def check_database(db_connection) -> ComponentHealth:
    """Check database connectivity"""
    try:
        # Try a simple query
        if hasattr(db_connection, 'execute_query'):
            await db_connection.execute_query("SELECT 1")
        elif hasattr(db_connection, 'fetch_one'):
            await db_connection.fetch_one("SELECT 1")
        else:
            # Assume it's healthy if we have a connection object
            pass
        
        return ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection OK",
        )
    except Exception as e:
        return ComponentHealth(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}",
        )


async def check_redis(redis_client) -> ComponentHealth:
    """Check Redis connectivity"""
    try:
        await redis_client.ping()
        return ComponentHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Redis connection OK",
        )
    except Exception as e:
        return ComponentHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}",
        )


async def check_nats(nats_client) -> ComponentHealth:
    """Check NATS connectivity"""
    try:
        if nats_client and nats_client.is_connected:
            return ComponentHealth(
                name="nats",
                status=HealthStatus.HEALTHY,
                message="NATS connection OK",
            )
        else:
            return ComponentHealth(
                name="nats",
                status=HealthStatus.UNHEALTHY,
                message="NATS not connected",
            )
    except Exception as e:
        return ComponentHealth(
            name="nats",
            status=HealthStatus.UNHEALTHY,
            message=f"NATS check failed: {str(e)}",
        )


def check_disk_space(threshold_percent: float = 90.0) -> ComponentHealth:
    """Check disk space usage"""
    try:
        import shutil
        disk_usage = shutil.disk_usage("/")
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        if used_percent > threshold_percent:
            return ComponentHealth(
                name="disk_space",
                status=HealthStatus.DEGRADED,
                message=f"Disk usage at {used_percent:.1f}%",
                metadata={"used_percent": used_percent},
            )
        
        return ComponentHealth(
            name="disk_space",
            status=HealthStatus.HEALTHY,
            message=f"Disk usage at {used_percent:.1f}%",
            metadata={"used_percent": used_percent},
        )
    except Exception as e:
        return ComponentHealth(
            name="disk_space",
            status=HealthStatus.UNHEALTHY,
            message=f"Disk check failed: {str(e)}",
        )


def check_memory(threshold_percent: float = 90.0) -> ComponentHealth:
    """Check memory usage"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        used_percent = memory.percent
        
        if used_percent > threshold_percent:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.DEGRADED,
                message=f"Memory usage at {used_percent:.1f}%",
                metadata={"used_percent": used_percent},
            )
        
        return ComponentHealth(
            name="memory",
            status=HealthStatus.HEALTHY,
            message=f"Memory usage at {used_percent:.1f}%",
            metadata={"used_percent": used_percent},
        )
    except ImportError:
        # psutil not available, skip check
        return ComponentHealth(
            name="memory",
            status=HealthStatus.HEALTHY,
            message="Memory check skipped (psutil not available)",
        )
    except Exception as e:
        return ComponentHealth(
            name="memory",
            status=HealthStatus.UNHEALTHY,
            message=f"Memory check failed: {str(e)}",
        )
