"""
Service Discovery
اكتشاف الخدمات

Provides service health monitoring and discovery
"""

import os
import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum

import httpx

from ..versions import SERVICE_PORTS, SERVICE_VERSIONS

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Service health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status of a service"""

    name: str
    status: HealthStatus
    version: Optional[str] = None
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Dict = field(default_factory=dict)


class ServiceDiscovery:
    """
    Service Discovery and Health Monitoring
    اكتشاف الخدمات ومراقبة الصحة

    Usage:
        discovery = ServiceDiscovery()
        await discovery.start_health_checks()

        health = await discovery.get_service_health("weather-advanced")
        all_health = discovery.get_all_health()
    """

    def __init__(
        self,
        host: str = None,
        check_interval_seconds: int = 30,
    ):
        self.host = host or os.getenv("SERVICES_HOST", "localhost")
        self.check_interval = check_interval_seconds
        self._health_cache: Dict[str, ServiceHealth] = {}
        self._running = False
        self._check_task: Optional[asyncio.Task] = None

    def _get_service_url(self, service_name: str) -> str:
        """Get URL for a service"""
        port = SERVICE_PORTS.get(service_name)
        if port:
            return f"http://{self.host}:{port}"
        raise ValueError(f"Unknown service: {service_name}")

    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """
        Check health of a specific service
        فحص صحة خدمة معينة
        """
        url = self._get_service_url(service_name)
        start = datetime.utcnow()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/healthz")
                response_time = (datetime.utcnow() - start).total_seconds() * 1000

                if response.is_success:
                    data = response.json()
                    status = HealthStatus.HEALTHY

                    # Check for degraded status
                    if data.get("status") == "degraded":
                        status = HealthStatus.DEGRADED

                    health = ServiceHealth(
                        name=service_name,
                        status=status,
                        version=data.get("version"),
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        details=data,
                    )
                else:
                    health = ServiceHealth(
                        name=service_name,
                        status=HealthStatus.UNHEALTHY,
                        last_check=datetime.utcnow(),
                        response_time_ms=response_time,
                        error=f"HTTP {response.status_code}",
                    )

        except httpx.TimeoutException:
            health = ServiceHealth(
                name=service_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                error="Connection timeout",
            )
        except httpx.ConnectError:
            health = ServiceHealth(
                name=service_name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                error="Connection refused",
            )
        except Exception as e:
            health = ServiceHealth(
                name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=datetime.utcnow(),
                error=str(e),
            )

        self._health_cache[service_name] = health
        return health

    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """
        Check health of all services
        فحص صحة جميع الخدمات
        """
        tasks = [self.check_service_health(service) for service in SERVICE_PORTS.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_map = {}
        for i, service in enumerate(SERVICE_PORTS.keys()):
            if isinstance(results[i], Exception):
                health_map[service] = ServiceHealth(
                    name=service,
                    status=HealthStatus.UNKNOWN,
                    error=str(results[i]),
                )
            else:
                health_map[service] = results[i]

        return health_map

    async def _health_check_loop(self):
        """Background health check loop"""
        while self._running:
            try:
                await self.check_all_services()
                logger.debug("Health check completed for all services")
            except Exception as e:
                logger.error(f"Health check loop error: {e}")

            await asyncio.sleep(self.check_interval)

    async def start_health_checks(self):
        """Start background health checks"""
        if self._running:
            return

        self._running = True
        self._check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started background health checks")

    async def stop_health_checks(self):
        """Stop background health checks"""
        self._running = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped background health checks")

    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """Get cached health for a service"""
        return self._health_cache.get(service_name)

    def get_all_health(self) -> Dict[str, ServiceHealth]:
        """Get cached health for all services"""
        return dict(self._health_cache)

    def get_healthy_services(self) -> List[str]:
        """Get list of healthy services"""
        return [
            name
            for name, health in self._health_cache.items()
            if health.status == HealthStatus.HEALTHY
        ]

    def get_unhealthy_services(self) -> List[str]:
        """Get list of unhealthy services"""
        return [
            name
            for name, health in self._health_cache.items()
            if health.status in (HealthStatus.UNHEALTHY, HealthStatus.UNKNOWN)
        ]

    def get_summary(self) -> Dict:
        """Get health summary"""
        total = len(SERVICE_PORTS)
        healthy = len(
            [h for h in self._health_cache.values() if h.status == HealthStatus.HEALTHY]
        )
        degraded = len(
            [
                h
                for h in self._health_cache.values()
                if h.status == HealthStatus.DEGRADED
            ]
        )
        unhealthy = len(
            [
                h
                for h in self._health_cache.values()
                if h.status == HealthStatus.UNHEALTHY
            ]
        )

        return {
            "total_services": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "unknown": total - healthy - degraded - unhealthy,
            "last_check": max(
                (h.last_check for h in self._health_cache.values() if h.last_check),
                default=None,
            ),
        }


# =============================================================================
# Global Discovery Instance
# =============================================================================

_discovery: Optional[ServiceDiscovery] = None


def get_service_discovery() -> ServiceDiscovery:
    """Get or create the service discovery instance"""
    global _discovery
    if _discovery is None:
        _discovery = ServiceDiscovery()
    return _discovery


async def initialize_discovery():
    """Initialize and start service discovery"""
    discovery = get_service_discovery()
    await discovery.start_health_checks()
    return discovery
