"""
SAHOOL Platform - Enhanced Health Checks
فحوصات الصحة المحسّنة

Provides comprehensive health monitoring with:
- Kubernetes-compatible probes
- Dependency health tracking
- Graceful degradation support
- Agricultural domain-specific checks
- Circuit breaker integration
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

try:
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class HealthStatus(StrEnum):
    """Health status values | قيم حالة الصحة"""

    HEALTHY = "healthy"  # صحي - All checks passing
    DEGRADED = "degraded"  # متدهور - Some non-critical checks failing
    UNHEALTHY = "unhealthy"  # غير صحي - Critical checks failing
    UNKNOWN = "unknown"  # غير معروف - Unable to determine


class DependencyType(StrEnum):
    """Types of service dependencies | أنواع تبعيات الخدمة"""

    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    EXTERNAL_API = "external_api"
    INTERNAL_SERVICE = "internal_service"
    STORAGE = "storage"
    AI_MODEL = "ai_model"
    IOT_DEVICE = "iot_device"


class CheckSeverity(StrEnum):
    """Severity of health check failure | خطورة فشل فحص الصحة"""

    CRITICAL = "critical"  # حرج - Service cannot function
    WARNING = "warning"  # تحذير - Service degraded
    INFO = "info"  # إعلامي - Minor issue


@dataclass
class DependencyHealth:
    """
    Health status of a single dependency.
    حالة صحة تبعية واحدة.
    """

    name: str
    name_ar: str
    type: DependencyType
    status: HealthStatus
    severity: CheckSeverity = CheckSeverity.WARNING
    message: str = ""
    message_ar: str = ""
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    circuit_open: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.type.value,
            "status": self.status.value,
            "severity": self.severity.value,
            "message": self.message,
            "message_ar": self.message_ar,
            "latency_ms": round(self.latency_ms, 2),
            "metadata": self.metadata,
            "circuit_open": self.circuit_open,
        }


@dataclass
class ServiceHealthReport:
    """
    Complete health report for a service.
    تقرير الصحة الكامل لخدمة.
    """

    service_name: str
    service_name_ar: str
    version: str
    environment: str
    status: HealthStatus
    dependencies: list[DependencyHealth] = field(default_factory=list)
    uptime_seconds: float = 0
    timestamp: str = ""
    ready_to_serve: bool = True
    graceful_shutdown: bool = False

    # Kubernetes probe specific
    live: bool = True
    ready: bool = True
    startup_complete: bool = True

    # Performance metrics
    memory_usage_mb: float = 0
    cpu_percent: float = 0
    open_connections: int = 0
    request_queue_size: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat() + "Z"

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service_name,
            "service_ar": self.service_name_ar,
            "version": self.version,
            "environment": self.environment,
            "status": self.status.value,
            "uptime_seconds": round(self.uptime_seconds, 2),
            "timestamp": self.timestamp,
            "kubernetes": {
                "live": self.live,
                "ready": self.ready,
                "startup_complete": self.startup_complete,
            },
            "performance": {
                "memory_usage_mb": round(self.memory_usage_mb, 2),
                "cpu_percent": round(self.cpu_percent, 2),
                "open_connections": self.open_connections,
                "request_queue_size": self.request_queue_size,
            },
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "ready_to_serve": self.ready_to_serve,
            "graceful_shutdown": self.graceful_shutdown,
        }


class EnhancedHealthChecker:
    """
    Enhanced health checker with comprehensive monitoring.
    فاحص الصحة المحسّن مع مراقبة شاملة.

    Features:
    - Multi-layer health checks (liveness, readiness, startup)
    - Dependency health tracking with circuit breakers
    - Graceful degradation support
    - Performance metrics collection
    - Agricultural domain-specific checks
    """

    def __init__(
        self,
        service_name: str,
        service_name_ar: str,
        version: str,
        environment: str | None = None,
    ):
        self.service_name = service_name
        self.service_name_ar = service_name_ar
        self.version = version
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.start_time = time.time()
        self.startup_complete = False
        self.graceful_shutdown = False

        # Check registries
        self._liveness_checks: dict[str, Callable] = {}
        self._readiness_checks: dict[str, Callable] = {}
        self._startup_checks: dict[str, Callable] = {}

        # Dependency tracking
        self._dependencies: dict[str, DependencyHealth] = {}
        self._circuit_breaker_threshold = 5  # failures before opening circuit

        # Cache for check results
        self._cache: dict[str, tuple[DependencyHealth, float]] = {}
        self._cache_ttl = 5.0  # seconds

    def register_liveness_check(
        self,
        name: str,
        check_func: Callable,
        severity: CheckSeverity = CheckSeverity.CRITICAL,
    ) -> None:
        """
        Register a liveness check.
        Liveness checks verify the service is running and not deadlocked.

        Args:
            name: Check name
            check_func: Async or sync function returning bool, dict, or DependencyHealth
            severity: Severity if check fails
        """
        self._liveness_checks[name] = (check_func, severity)

    def register_readiness_check(
        self,
        name: str,
        check_func: Callable,
        dependency_type: DependencyType = DependencyType.INTERNAL_SERVICE,
        name_ar: str = "",
        severity: CheckSeverity = CheckSeverity.WARNING,
    ) -> None:
        """
        Register a readiness check.
        Readiness checks verify external dependencies are available.
        """
        self._readiness_checks[name] = (check_func, dependency_type, name_ar, severity)

    def register_startup_check(
        self,
        name: str,
        check_func: Callable,
    ) -> None:
        """
        Register a startup check.
        Startup checks run once during service initialization.
        """
        self._startup_checks[name] = check_func

    async def _run_check(
        self,
        name: str,
        check_func: Callable,
        dependency_type: DependencyType = DependencyType.INTERNAL_SERVICE,
        name_ar: str = "",
        severity: CheckSeverity = CheckSeverity.WARNING,
    ) -> DependencyHealth:
        """Execute a single health check with timing and error handling."""

        # Check cache first
        if name in self._cache:
            cached_result, cached_time = self._cache[name]
            if time.time() - cached_time < self._cache_ttl:
                return cached_result

        start_time = time.time()

        try:
            # Run check
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()

            latency_ms = (time.time() - start_time) * 1000

            # Parse result
            if isinstance(result, DependencyHealth):
                result.latency_ms = latency_ms
                health = result
            elif isinstance(result, bool):
                health = DependencyHealth(
                    name=name,
                    name_ar=name_ar or name,
                    type=dependency_type,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    severity=severity,
                    message="Check passed" if result else "Check failed",
                    message_ar="الفحص نجح" if result else "الفحص فشل",
                    latency_ms=latency_ms,
                )
            elif isinstance(result, dict):
                status_str = result.get("status", "healthy")
                health = DependencyHealth(
                    name=name,
                    name_ar=name_ar or result.get("name_ar", name),
                    type=dependency_type,
                    status=HealthStatus(status_str)
                    if status_str in ["healthy", "degraded", "unhealthy"]
                    else HealthStatus.HEALTHY,
                    severity=severity,
                    message=result.get("message", ""),
                    message_ar=result.get("message_ar", ""),
                    latency_ms=latency_ms,
                    metadata=result.get("metadata", {}),
                )
            else:
                health = DependencyHealth(
                    name=name,
                    name_ar=name_ar or name,
                    type=dependency_type,
                    status=HealthStatus.HEALTHY,
                    severity=severity,
                    message="Check completed",
                    message_ar="الفحص اكتمل",
                    latency_ms=latency_ms,
                )

            # Reset consecutive failures on success
            if name in self._dependencies:
                self._dependencies[name].consecutive_failures = 0
                self._dependencies[name].circuit_open = False

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000

            # Track consecutive failures
            if name in self._dependencies:
                self._dependencies[name].consecutive_failures += 1
                if self._dependencies[name].consecutive_failures >= self._circuit_breaker_threshold:
                    self._dependencies[name].circuit_open = True

            health = DependencyHealth(
                name=name,
                name_ar=name_ar or name,
                type=dependency_type,
                status=HealthStatus.UNHEALTHY,
                severity=severity,
                message=f"Check failed: {str(e)}",
                message_ar=f"الفحص فشل: {str(e)}",
                latency_ms=latency_ms,
                consecutive_failures=self._dependencies.get(
                    name,
                    DependencyHealth(
                        name=name,
                        name_ar=name_ar,
                        type=dependency_type,
                        status=HealthStatus.UNKNOWN,
                    ),
                ).consecutive_failures
                + 1,
            )

        # Update cache and dependency registry
        self._cache[name] = (health, time.time())
        self._dependencies[name] = health

        return health

    async def check_liveness(self) -> ServiceHealthReport:
        """
        Check liveness (is the service process running and not deadlocked?).
        فحص الحياة (هل عملية الخدمة تعمل وليست معلقة؟)

        Used by Kubernetes liveness probe.
        """
        dependencies = []

        for name, (check_func, severity) in self._liveness_checks.items():
            health = await self._run_check(
                name,
                check_func,
                severity=severity,
            )
            dependencies.append(health)

        # Liveness fails only if critical checks fail
        critical_failures = [
            d
            for d in dependencies
            if d.status == HealthStatus.UNHEALTHY and d.severity == CheckSeverity.CRITICAL
        ]

        if critical_failures:
            status = HealthStatus.UNHEALTHY
            live = False
        elif any(d.status == HealthStatus.DEGRADED for d in dependencies):
            status = HealthStatus.DEGRADED
            live = True
        else:
            status = HealthStatus.HEALTHY
            live = True

        return ServiceHealthReport(
            service_name=self.service_name,
            service_name_ar=self.service_name_ar,
            version=self.version,
            environment=self.environment,
            status=status,
            dependencies=dependencies,
            uptime_seconds=time.time() - self.start_time,
            live=live,
            ready=True,
            startup_complete=self.startup_complete,
            graceful_shutdown=self.graceful_shutdown,
        )

    async def check_readiness(self) -> ServiceHealthReport:
        """
        Check readiness (can the service handle traffic?).
        فحص الاستعداد (هل يمكن للخدمة معالجة الحركة؟)

        Used by Kubernetes readiness probe.
        """
        dependencies = []

        for name, (check_func, dep_type, name_ar, severity) in self._readiness_checks.items():
            health = await self._run_check(
                name,
                check_func,
                dependency_type=dep_type,
                name_ar=name_ar,
                severity=severity,
            )
            dependencies.append(health)

        # Readiness fails if any critical dependency is down
        critical_failures = [
            d
            for d in dependencies
            if d.status == HealthStatus.UNHEALTHY and d.severity == CheckSeverity.CRITICAL
        ]

        if self.graceful_shutdown or critical_failures:
            status = HealthStatus.UNHEALTHY
            ready = False
        elif any(d.status == HealthStatus.DEGRADED for d in dependencies):
            status = HealthStatus.DEGRADED
            ready = True
        else:
            status = HealthStatus.HEALTHY
            ready = True

        return ServiceHealthReport(
            service_name=self.service_name,
            service_name_ar=self.service_name_ar,
            version=self.version,
            environment=self.environment,
            status=status,
            dependencies=dependencies,
            uptime_seconds=time.time() - self.start_time,
            live=True,
            ready=ready,
            startup_complete=self.startup_complete,
            graceful_shutdown=self.graceful_shutdown,
        )

    async def check_startup(self) -> ServiceHealthReport:
        """
        Check startup (has the service finished initializing?).
        فحص بدء التشغيل (هل انتهت الخدمة من التهيئة؟)

        Used by Kubernetes startup probe.
        """
        if self.startup_complete:
            return await self.check_readiness()

        dependencies = []

        for name, check_func in self._startup_checks.items():
            health = await self._run_check(name, check_func)
            dependencies.append(health)

        # Startup complete if all startup checks pass
        all_healthy = all(
            d.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] for d in dependencies
        )

        if all_healthy:
            self.startup_complete = True

        status = HealthStatus.HEALTHY if all_healthy else HealthStatus.UNHEALTHY

        return ServiceHealthReport(
            service_name=self.service_name,
            service_name_ar=self.service_name_ar,
            version=self.version,
            environment=self.environment,
            status=status,
            dependencies=dependencies,
            uptime_seconds=time.time() - self.start_time,
            live=True,
            ready=self.startup_complete,
            startup_complete=self.startup_complete,
            graceful_shutdown=self.graceful_shutdown,
        )

    async def check_full(self) -> ServiceHealthReport:
        """
        Run all health checks and return comprehensive report.
        تشغيل جميع فحوصات الصحة وإرجاع تقرير شامل.
        """
        # Run all checks
        liveness = await self.check_liveness()
        readiness = await self.check_readiness()

        # Combine dependencies
        all_deps = liveness.dependencies + readiness.dependencies

        # Collect performance metrics
        memory_mb, cpu_percent = await self._collect_performance_metrics()

        # Determine overall status
        if not liveness.live or not readiness.ready:
            status = HealthStatus.UNHEALTHY
        elif liveness.status == HealthStatus.DEGRADED or readiness.status == HealthStatus.DEGRADED:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return ServiceHealthReport(
            service_name=self.service_name,
            service_name_ar=self.service_name_ar,
            version=self.version,
            environment=self.environment,
            status=status,
            dependencies=all_deps,
            uptime_seconds=time.time() - self.start_time,
            live=liveness.live,
            ready=readiness.ready,
            startup_complete=self.startup_complete,
            graceful_shutdown=self.graceful_shutdown,
            memory_usage_mb=memory_mb,
            cpu_percent=cpu_percent,
        )

    async def _collect_performance_metrics(self) -> tuple[float, float]:
        """Collect current performance metrics."""
        memory_mb = 0.0
        cpu_percent = 0.0

        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            cpu_percent = process.cpu_percent()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Failed to get process metrics: {e}")

        return memory_mb, cpu_percent

    def begin_graceful_shutdown(self) -> None:
        """
        Signal graceful shutdown to stop accepting new traffic.
        إشارة الإغلاق السلس لإيقاف قبول حركة جديدة.
        """
        self.graceful_shutdown = True


# ═══════════════════════════════════════════════════════════════════════════════
# Common Health Check Functions | دوال فحص الصحة الشائعة
# ═══════════════════════════════════════════════════════════════════════════════


async def check_postgres(connection_pool) -> DependencyHealth:
    """
    Check PostgreSQL database health.
    فحص صحة قاعدة بيانات PostgreSQL.
    """
    start = time.time()
    try:
        async with connection_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

        return DependencyHealth(
            name="postgres",
            name_ar="PostgreSQL",
            type=DependencyType.DATABASE,
            status=HealthStatus.HEALTHY,
            severity=CheckSeverity.CRITICAL,
            message="Database connection OK",
            message_ar="اتصال قاعدة البيانات سليم",
            latency_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        return DependencyHealth(
            name="postgres",
            name_ar="PostgreSQL",
            type=DependencyType.DATABASE,
            status=HealthStatus.UNHEALTHY,
            severity=CheckSeverity.CRITICAL,
            message=f"Database connection failed: {e}",
            message_ar=f"فشل اتصال قاعدة البيانات: {e}",
            latency_ms=(time.time() - start) * 1000,
        )


async def check_redis(redis_client) -> DependencyHealth:
    """
    Check Redis cache health.
    فحص صحة ذاكرة التخزين المؤقت Redis.
    """
    start = time.time()
    try:
        await redis_client.ping()

        # Get memory usage
        info = await redis_client.info("memory")
        used_memory_mb = info.get("used_memory", 0) / (1024 * 1024)

        return DependencyHealth(
            name="redis",
            name_ar="Redis",
            type=DependencyType.CACHE,
            status=HealthStatus.HEALTHY,
            severity=CheckSeverity.CRITICAL,
            message="Redis connection OK",
            message_ar="اتصال Redis سليم",
            latency_ms=(time.time() - start) * 1000,
            metadata={"used_memory_mb": round(used_memory_mb, 2)},
        )
    except Exception as e:
        return DependencyHealth(
            name="redis",
            name_ar="Redis",
            type=DependencyType.CACHE,
            status=HealthStatus.UNHEALTHY,
            severity=CheckSeverity.CRITICAL,
            message=f"Redis connection failed: {e}",
            message_ar=f"فشل اتصال Redis: {e}",
            latency_ms=(time.time() - start) * 1000,
        )


async def check_nats(nats_client) -> DependencyHealth:
    """
    Check NATS message queue health.
    فحص صحة نظام الرسائل NATS.
    """
    start = time.time()
    try:
        if nats_client and nats_client.is_connected:
            return DependencyHealth(
                name="nats",
                name_ar="NATS",
                type=DependencyType.MESSAGE_QUEUE,
                status=HealthStatus.HEALTHY,
                severity=CheckSeverity.CRITICAL,
                message="NATS connection OK",
                message_ar="اتصال NATS سليم",
                latency_ms=(time.time() - start) * 1000,
            )
        else:
            return DependencyHealth(
                name="nats",
                name_ar="NATS",
                type=DependencyType.MESSAGE_QUEUE,
                status=HealthStatus.UNHEALTHY,
                severity=CheckSeverity.CRITICAL,
                message="NATS not connected",
                message_ar="NATS غير متصل",
                latency_ms=(time.time() - start) * 1000,
            )
    except Exception as e:
        return DependencyHealth(
            name="nats",
            name_ar="NATS",
            type=DependencyType.MESSAGE_QUEUE,
            status=HealthStatus.UNHEALTHY,
            severity=CheckSeverity.CRITICAL,
            message=f"NATS check failed: {e}",
            message_ar=f"فشل فحص NATS: {e}",
            latency_ms=(time.time() - start) * 1000,
        )


def check_disk_space(threshold_percent: float = 85.0) -> DependencyHealth:
    """
    Check disk space usage.
    فحص استخدام مساحة القرص.
    """
    try:
        import shutil

        disk = shutil.disk_usage("/")
        used_percent = (disk.used / disk.total) * 100
        free_gb = disk.free / (1024**3)

        if used_percent > 95:
            status = HealthStatus.UNHEALTHY
            severity = CheckSeverity.CRITICAL
        elif used_percent > threshold_percent:
            status = HealthStatus.DEGRADED
            severity = CheckSeverity.WARNING
        else:
            status = HealthStatus.HEALTHY
            severity = CheckSeverity.INFO

        return DependencyHealth(
            name="disk_space",
            name_ar="مساحة القرص",
            type=DependencyType.STORAGE,
            status=status,
            severity=severity,
            message=f"Disk usage: {used_percent:.1f}%, Free: {free_gb:.1f}GB",
            message_ar=f"استخدام القرص: {used_percent:.1f}%، متاح: {free_gb:.1f} جيجابايت",
            metadata={
                "used_percent": round(used_percent, 2),
                "free_gb": round(free_gb, 2),
            },
        )
    except Exception as e:
        return DependencyHealth(
            name="disk_space",
            name_ar="مساحة القرص",
            type=DependencyType.STORAGE,
            status=HealthStatus.UNKNOWN,
            severity=CheckSeverity.WARNING,
            message=f"Disk check failed: {e}",
            message_ar=f"فشل فحص القرص: {e}",
        )


def check_memory(threshold_percent: float = 85.0) -> DependencyHealth:
    """
    Check memory usage.
    فحص استخدام الذاكرة.
    """
    try:
        import psutil

        memory = psutil.virtual_memory()
        used_percent = memory.percent
        available_gb = memory.available / (1024**3)

        if used_percent > 95:
            status = HealthStatus.UNHEALTHY
            severity = CheckSeverity.CRITICAL
        elif used_percent > threshold_percent:
            status = HealthStatus.DEGRADED
            severity = CheckSeverity.WARNING
        else:
            status = HealthStatus.HEALTHY
            severity = CheckSeverity.INFO

        return DependencyHealth(
            name="memory",
            name_ar="الذاكرة",
            type=DependencyType.STORAGE,
            status=status,
            severity=severity,
            message=f"Memory usage: {used_percent:.1f}%, Available: {available_gb:.1f}GB",
            message_ar=f"استخدام الذاكرة: {used_percent:.1f}%، متاح: {available_gb:.1f} جيجابايت",
            metadata={
                "used_percent": round(used_percent, 2),
                "available_gb": round(available_gb, 2),
            },
        )
    except ImportError:
        return DependencyHealth(
            name="memory",
            name_ar="الذاكرة",
            type=DependencyType.STORAGE,
            status=HealthStatus.UNKNOWN,
            severity=CheckSeverity.INFO,
            message="psutil not available",
            message_ar="psutil غير متاح",
        )
    except Exception as e:
        return DependencyHealth(
            name="memory",
            name_ar="الذاكرة",
            type=DependencyType.STORAGE,
            status=HealthStatus.UNKNOWN,
            severity=CheckSeverity.WARNING,
            message=f"Memory check failed: {e}",
            message_ar=f"فشل فحص الذاكرة: {e}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Router Creation | إنشاء موجه FastAPI
# ═══════════════════════════════════════════════════════════════════════════════


def create_health_router(health_checker: EnhancedHealthChecker) -> APIRouter:
    """
    Create FastAPI router with comprehensive health endpoints.
    إنشاء موجه FastAPI مع نقاط فحص صحة شاملة.
    """
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI is required for create_health_router")

    router = APIRouter(tags=["Health", "الصحة"])

    @router.get("/health/live", summary="Liveness probe | فحص الحياة")
    async def liveness():
        """
        Kubernetes liveness probe.
        Used to restart crashed/deadlocked containers.
        """
        report = await health_checker.check_liveness()
        status_code = 200 if report.live else 503
        return JSONResponse(content=report.to_dict(), status_code=status_code)

    @router.get("/health/ready", summary="Readiness probe | فحص الاستعداد")
    async def readiness():
        """
        Kubernetes readiness probe.
        Used to route traffic only to ready instances.
        """
        report = await health_checker.check_readiness()
        status_code = 200 if report.ready else 503
        return JSONResponse(content=report.to_dict(), status_code=status_code)

    @router.get("/health/startup", summary="Startup probe | فحص بدء التشغيل")
    async def startup():
        """
        Kubernetes startup probe.
        Used during container initialization.
        """
        report = await health_checker.check_startup()
        status_code = 200 if report.startup_complete else 503
        return JSONResponse(content=report.to_dict(), status_code=status_code)

    @router.get("/health", summary="Full health check | فحص الصحة الكامل")
    async def full_health():
        """
        Complete health check with all dependencies.
        Suitable for monitoring systems.
        """
        report = await health_checker.check_full()
        status_code = 200 if report.status != HealthStatus.UNHEALTHY else 503
        return JSONResponse(content=report.to_dict(), status_code=status_code)

    @router.get("/healthz", summary="Simple health check | فحص صحة بسيط")
    async def healthz():
        """Simple health check for legacy compatibility."""
        report = await health_checker.check_liveness()
        return {"status": "ok" if report.live else "error"}

    @router.get("/readyz", summary="Simple readiness check | فحص استعداد بسيط")
    async def readyz():
        """Simple readiness check for legacy compatibility."""
        report = await health_checker.check_readiness()
        return {"status": "ok" if report.ready else "error"}

    return router
