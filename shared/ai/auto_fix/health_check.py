"""
Platform Health Check Module for SAHOOL
وحدة فحص صحة المنصة لسهول

Comprehensive health checks for all platform components:
- Services health (API endpoints)
- Database connectivity
- Cache (Redis) status
- Message queue (NATS) status
- Container health
- Dependencies check

Author: SAHOOL Platform Team
Created: January 2026
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(StrEnum):
    """Health status levels | مستويات حالة الصحة"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(StrEnum):
    """Platform component types | أنواع مكونات المنصة"""

    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    API_GATEWAY = "api_gateway"
    CONTAINER = "container"
    DEPENDENCY = "dependency"


@dataclass
class HealthCheckResult:
    """Result of a health check | نتيجة فحص الصحة"""

    component: str
    component_type: ComponentType
    status: HealthStatus
    message: str
    message_ar: str
    latency_ms: float | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy | فحص إذا كان المكون صحي"""
        return self.status == HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "message": self.message,
            "message_ar": self.message_ar,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HealthReport:
    """Complete health report | تقرير صحة كامل"""

    results: list[HealthCheckResult] = field(default_factory=list)
    _overall_status: HealthStatus | None = field(default=None, repr=False)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def healthy_count(self) -> int:
        return sum(1 for r in self.results if r.status == HealthStatus.HEALTHY)

    @property
    def unhealthy_count(self) -> int:
        return sum(1 for r in self.results if r.status == HealthStatus.UNHEALTHY)

    @property
    def degraded_count(self) -> int:
        return sum(1 for r in self.results if r.status == HealthStatus.DEGRADED)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def overall_status(self) -> HealthStatus:
        """Calculate overall status from results | حساب الحالة العامة من النتائج"""
        if self._overall_status is not None:
            return self._overall_status
        if not self.results:
            return HealthStatus.UNKNOWN
        if self.unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        if self.degraded_count > 0:
            return HealthStatus.DEGRADED
        if self.healthy_count == self.total_count:
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN

    @overall_status.setter
    def overall_status(self, value: HealthStatus) -> None:
        self._overall_status = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status.value,
            "healthy_count": self.healthy_count,
            "unhealthy_count": self.unhealthy_count,
            "total_count": self.total_count,
            "results": [r.to_dict() for r in self.results],
            "timestamp": self.timestamp.isoformat(),
            "summary_ar": f"صحي: {self.healthy_count}/{self.total_count}",
        }


class HealthChecker:
    """
    Platform health checker.
    فاحص صحة المنصة.
    """

    def __init__(self, working_dir: str | Path = "."):
        self.working_dir = Path(working_dir)

    async def _check_port(self, host: str, port: int, timeout: float = 2.0) -> tuple[bool, float]:
        """Check if a port is open | فحص إذا كان المنفذ مفتوحاً"""
        start = asyncio.get_event_loop().time()
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
            writer.close()
            await writer.wait_closed()
            latency = (asyncio.get_event_loop().time() - start) * 1000
            return True, latency
        except Exception:
            return False, 0

    async def check_postgresql(self, host: str = "localhost", port: int = 5432) -> HealthCheckResult:
        """Check PostgreSQL health | فحص صحة PostgreSQL"""
        is_open, latency = await self._check_port(host, port)

        if is_open:
            return HealthCheckResult(
                component="PostgreSQL",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message=f"PostgreSQL is reachable on {host}:{port}",
                message_ar=f"PostgreSQL متصل على {host}:{port}",
                latency_ms=latency,
            )
        else:
            return HealthCheckResult(
                component="PostgreSQL",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to PostgreSQL on {host}:{port}",
                message_ar=f"لا يمكن الاتصال بـ PostgreSQL على {host}:{port}",
            )

    async def check_redis(self, host: str = "redis", port: int = 6379) -> HealthCheckResult:
        """Check Redis health | فحص صحة Redis"""
        is_open, latency = await self._check_port(host, port)

        if is_open:
            return HealthCheckResult(
                component="Redis",
                component_type=ComponentType.CACHE,
                status=HealthStatus.HEALTHY,
                message=f"Redis is reachable on {host}:{port}",
                message_ar=f"Redis متصل على {host}:{port}",
                latency_ms=latency,
            )
        else:
            return HealthCheckResult(
                component="Redis",
                component_type=ComponentType.CACHE,
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to Redis on {host}:{port}",
                message_ar=f"لا يمكن الاتصال بـ Redis على {host}:{port}",
            )

    async def check_nats(self, host: str = "localhost", port: int = 4222) -> HealthCheckResult:
        """Check NATS health | فحص صحة NATS"""
        is_open, latency = await self._check_port(host, port)

        if is_open:
            return HealthCheckResult(
                component="NATS",
                component_type=ComponentType.MESSAGE_QUEUE,
                status=HealthStatus.HEALTHY,
                message=f"NATS is reachable on {host}:{port}",
                message_ar=f"NATS متصل على {host}:{port}",
                latency_ms=latency,
            )
        else:
            return HealthCheckResult(
                component="NATS",
                component_type=ComponentType.MESSAGE_QUEUE,
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to NATS on {host}:{port}",
                message_ar=f"لا يمكن الاتصال بـ NATS على {host}:{port}",
            )

    async def check_pgbouncer(self, host: str = "localhost", port: int = 6432) -> HealthCheckResult:
        """Check PgBouncer health | فحص صحة PgBouncer"""
        is_open, latency = await self._check_port(host, port)

        if is_open:
            return HealthCheckResult(
                component="PgBouncer",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message=f"PgBouncer is reachable on {host}:{port}",
                message_ar=f"PgBouncer متصل على {host}:{port}",
                latency_ms=latency,
            )
        else:
            return HealthCheckResult(
                component="PgBouncer",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to PgBouncer on {host}:{port}",
                message_ar=f"لا يمكن الاتصال بـ PgBouncer على {host}:{port}",
            )

    async def check_docker_containers(self) -> list[HealthCheckResult]:
        """Check Docker container health | فحص صحة حاويات Docker"""
        results = []

        try:
            cmd = ["docker", "compose", "ps", "--format", "json"]
            # nosemgrep: dangerous-asyncio-create-exec-audit -- internal tooling; args are hardcoded program names + validated paths, not user-controlled shell strings
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if stdout:
                import json

                for line in stdout.decode().strip().split("\n"):
                    if line:
                        try:
                            container = json.loads(line)
                            name = container.get("Name", "unknown")
                            state = container.get("State", "unknown")
                            health = container.get("Health", "")

                            if state == "running":
                                status = HealthStatus.HEALTHY
                                if health == "unhealthy":
                                    status = HealthStatus.UNHEALTHY
                                elif health == "starting":
                                    status = HealthStatus.DEGRADED
                            else:
                                status = HealthStatus.UNHEALTHY

                            results.append(
                                HealthCheckResult(
                                    component=name,
                                    component_type=ComponentType.CONTAINER,
                                    status=status,
                                    message=f"Container {name}: {state}",
                                    message_ar=f"حاوية {name}: {state}",
                                    details={"state": state, "health": health},
                                )
                            )
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Docker check failed: {e}")
            results.append(
                HealthCheckResult(
                    component="Docker",
                    component_type=ComponentType.CONTAINER,
                    status=HealthStatus.UNKNOWN,
                    message=f"Cannot check Docker: {e}",
                    message_ar=f"لا يمكن فحص Docker: {e}",
                )
            )

        return results

    async def check_python_dependencies(self) -> HealthCheckResult:
        """Check Python dependencies | فحص تبعيات Python"""
        try:
            cmd = ["pip", "check"]
            # nosemgrep: dangerous-asyncio-create-exec-audit -- internal tooling; args are hardcoded program names + validated paths, not user-controlled shell strings
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return HealthCheckResult(
                    component="Python Dependencies",
                    component_type=ComponentType.DEPENDENCY,
                    status=HealthStatus.HEALTHY,
                    message="All Python dependencies are satisfied",
                    message_ar="جميع تبعيات Python مستوفاة",
                )
            else:
                return HealthCheckResult(
                    component="Python Dependencies",
                    component_type=ComponentType.DEPENDENCY,
                    status=HealthStatus.DEGRADED,
                    message=f"Dependency issues: {stderr.decode()[:200]}",
                    message_ar="مشاكل في التبعيات",
                    details={"output": stderr.decode()},
                )

        except Exception as e:
            return HealthCheckResult(
                component="Python Dependencies",
                component_type=ComponentType.DEPENDENCY,
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check dependencies: {e}",
                message_ar=f"لا يمكن فحص التبعيات: {e}",
            )

    async def check_node_dependencies(self) -> HealthCheckResult:
        """Check Node.js dependencies | فحص تبعيات Node.js"""
        try:
            cmd = ["npm", "ls", "--json"]
            # nosemgrep: dangerous-asyncio-create-exec-audit -- internal tooling; args are hardcoded program names + validated paths, not user-controlled shell strings
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if process.returncode == 0:
                return HealthCheckResult(
                    component="Node.js Dependencies",
                    component_type=ComponentType.DEPENDENCY,
                    status=HealthStatus.HEALTHY,
                    message="All Node.js dependencies are installed",
                    message_ar="جميع تبعيات Node.js مثبتة",
                )
            else:
                return HealthCheckResult(
                    component="Node.js Dependencies",
                    component_type=ComponentType.DEPENDENCY,
                    status=HealthStatus.DEGRADED,
                    message="Some Node.js dependencies may be missing",
                    message_ar="بعض تبعيات Node.js قد تكون مفقودة",
                )

        except Exception as e:
            return HealthCheckResult(
                component="Node.js Dependencies",
                component_type=ComponentType.DEPENDENCY,
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check Node.js dependencies: {e}",
                message_ar=f"لا يمكن فحص تبعيات Node.js: {e}",
            )

    async def run_full_health_check(self) -> HealthReport:
        """Run complete health check | تشغيل فحص صحة كامل"""
        results: list[HealthCheckResult] = []

        # Infrastructure checks
        infrastructure_checks = [
            self.check_postgresql(),
            self.check_redis(),
            self.check_nats(),
            self.check_pgbouncer(),
        ]

        # Run infrastructure checks in parallel
        infrastructure_results = await asyncio.gather(*infrastructure_checks)
        results.extend(infrastructure_results)

        # Container checks
        container_results = await self.check_docker_containers()
        results.extend(container_results)

        # Dependency checks
        dep_checks = [
            self.check_python_dependencies(),
            self.check_node_dependencies(),
        ]
        dep_results = await asyncio.gather(*dep_checks)
        results.extend(dep_results)

        # Determine overall status
        unhealthy_count = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in results if r.status == HealthStatus.DEGRADED)

        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        report = HealthReport(results=results)
        report.overall_status = overall_status
        return report


# Convenience functions
async def quick_health_check() -> HealthReport:
    """Quick health check | فحص صحة سريع"""
    checker = HealthChecker()
    return await checker.run_full_health_check()


async def check_infrastructure() -> list[HealthCheckResult]:
    """Check infrastructure only | فحص البنية التحتية فقط"""
    checker = HealthChecker()
    results = await asyncio.gather(
        checker.check_postgresql(),
        checker.check_redis(),
        checker.check_nats(),
        checker.check_pgbouncer(),
    )
    return list(results)
