"""
Service Client for Inter-Service Communication
عميل الخدمة للاتصال بين الخدمات
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import httpx

from ..versions import SERVICE_PORTS, get_service_url

logger = logging.getLogger(__name__)


class ServiceName(str, Enum):
    """Available services"""

    BILLING = "billing-core"
    SATELLITE = "satellite-service"
    INDICATORS = "indicators-service"
    WEATHER = "weather-advanced"
    FERTILIZER = "fertilizer-advisor"
    IRRIGATION = "irrigation-smart"
    CROP_HEALTH = "crop-health-ai"
    VIRTUAL_SENSORS = "virtual-sensors"
    YIELD = "yield-engine"
    NOTIFICATION = "notification-service"
    ASTRONOMICAL = "astronomical-calendar"


@dataclass
class ServiceResponse:
    """Response from a service call"""

    success: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: float = 0


class ServiceClient:
    """
    Client for making requests to other SAHOOL services
    عميل لإجراء طلبات إلى خدمات سهول الأخرى

    Usage:
        client = ServiceClient(ServiceName.WEATHER)
        response = await client.get("/v1/current/sanaa")
        if response.success:
            print(response.data)
    """

    def __init__(
        self,
        service: ServiceName,
        host: Optional[str] = None,
        timeout: float = 30.0,
        api_key: Optional[str] = None,
        auth_token: Optional[str] = None,
    ):
        self.service = service
        self.host = host or os.getenv("SERVICES_HOST", "localhost")
        self.timeout = timeout
        self.api_key = api_key or os.getenv("INTER_SERVICE_API_KEY", "")
        self.auth_token = auth_token

        self.base_url = get_service_url(service.value, self.host)

        # Request cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {
            "Content-Type": "application/json",
            "X-Service-Name": self.service.value,
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def _get_cache_key(
        self, method: str, path: str, params: Optional[Dict] = None
    ) -> str:
        """Generate cache key"""
        param_str = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        return f"{method}:{path}?{param_str}"

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        return datetime.utcnow() - cached_at < self._cache_ttl

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> ServiceResponse:
        """Make GET request to service"""
        cache_key = self._get_cache_key("GET", path, params)

        # Check cache
        if use_cache and cache_key in self._cache:
            if self._is_cache_valid(self._cache[cache_key]):
                logger.debug(f"Cache hit for {self.service.value}{path}")
                return self._cache[cache_key]["response"]

        start = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}{path}",
                    params=params,
                    headers=self._get_headers(),
                )
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                result = ServiceResponse(
                    success=response.is_success,
                    status_code=response.status_code,
                    data=response.json() if response.is_success else None,
                    error=response.text if not response.is_success else None,
                    latency_ms=latency,
                )

                # Cache successful responses
                if use_cache and result.success:
                    self._cache[cache_key] = {
                        "response": result,
                        "cached_at": datetime.utcnow(),
                    }

                return result

        except httpx.TimeoutException:
            return ServiceResponse(
                success=False,
                status_code=504,
                error=f"Timeout connecting to {self.service.value}",
            )
        except Exception as e:
            logger.error(f"Error calling {self.service.value}: {e}")
            return ServiceResponse(
                success=False,
                status_code=500,
                error=str(e),
            )

    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> ServiceResponse:
        """Make POST request to service"""
        start = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{path}",
                    data=data,
                    json=json,
                    headers=self._get_headers(),
                )
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                return ServiceResponse(
                    success=response.is_success,
                    status_code=response.status_code,
                    data=response.json() if response.is_success else None,
                    error=response.text if not response.is_success else None,
                    latency_ms=latency,
                )

        except httpx.TimeoutException:
            return ServiceResponse(
                success=False,
                status_code=504,
                error=f"Timeout connecting to {self.service.value}",
            )
        except Exception as e:
            logger.error(f"Error calling {self.service.value}: {e}")
            return ServiceResponse(
                success=False,
                status_code=500,
                error=str(e),
            )

    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> ServiceResponse:
        """Make PUT request to service"""
        start = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}{path}",
                    data=data,
                    json=json,
                    headers=self._get_headers(),
                )
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                return ServiceResponse(
                    success=response.is_success,
                    status_code=response.status_code,
                    data=response.json() if response.is_success else None,
                    error=response.text if not response.is_success else None,
                    latency_ms=latency,
                )

        except Exception as e:
            logger.error(f"Error calling {self.service.value}: {e}")
            return ServiceResponse(
                success=False,
                status_code=500,
                error=str(e),
            )

    async def delete(self, path: str) -> ServiceResponse:
        """Make DELETE request to service"""
        start = datetime.utcnow()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    f"{self.base_url}{path}",
                    headers=self._get_headers(),
                )
                latency = (datetime.utcnow() - start).total_seconds() * 1000

                return ServiceResponse(
                    success=response.is_success,
                    status_code=response.status_code,
                    data=response.json() if response.is_success else None,
                    error=response.text if not response.is_success else None,
                    latency_ms=latency,
                )

        except Exception as e:
            logger.error(f"Error calling {self.service.value}: {e}")
            return ServiceResponse(
                success=False,
                status_code=500,
                error=str(e),
            )

    async def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            response = await self.get("/healthz", use_cache=False)
            return response.success and response.data.get("status") == "ok"
        except Exception:
            return False

    def clear_cache(self):
        """Clear the request cache"""
        self._cache.clear()


# Global clients registry
_clients: Dict[str, ServiceClient] = {}


def get_service_client(
    service: ServiceName,
    host: Optional[str] = None,
    **kwargs,
) -> ServiceClient:
    """
    Get or create a service client
    الحصول على أو إنشاء عميل خدمة

    Usage:
        weather_client = get_service_client(ServiceName.WEATHER)
        response = await weather_client.get("/v1/current/sanaa")
    """
    cache_key = f"{service.value}:{host or 'default'}"

    if cache_key not in _clients:
        _clients[cache_key] = ServiceClient(service, host, **kwargs)

    return _clients[cache_key]


# =============================================================================
# Convenience Functions - دوال مساعدة
# =============================================================================


async def get_current_weather(location_id: str) -> Optional[Dict]:
    """Get current weather for a location"""
    client = get_service_client(ServiceName.WEATHER)
    response = await client.get(f"/v1/current/{location_id}")
    return response.data if response.success else None


async def get_weather_forecast(location_id: str, days: int = 7) -> Optional[Dict]:
    """Get weather forecast for a location"""
    client = get_service_client(ServiceName.WEATHER)
    response = await client.get(f"/v1/forecast/{location_id}", params={"days": days})
    return response.data if response.success else None


async def get_tenant_subscription(tenant_id: str) -> Optional[Dict]:
    """Get tenant subscription details"""
    client = get_service_client(ServiceName.BILLING)
    response = await client.get(f"/v1/tenants/{tenant_id}/subscription")
    return response.data if response.success else None


async def record_usage(tenant_id: str, usage_type: str, amount: float) -> bool:
    """Record usage for a tenant"""
    client = get_service_client(ServiceName.BILLING)
    response = await client.post(
        f"/v1/tenants/{tenant_id}/usage",
        json={"usage_type": usage_type, "amount": amount},
    )
    return response.success


async def check_quota(tenant_id: str, usage_type: str) -> Optional[Dict]:
    """Check quota for a tenant"""
    client = get_service_client(ServiceName.BILLING)
    response = await client.get(f"/v1/tenants/{tenant_id}/quota")
    return response.data if response.success else None


async def send_notification(
    tenant_id: str,
    title: str,
    body: str,
    notification_type: str = "info",
) -> bool:
    """Send a notification to a tenant"""
    client = get_service_client(ServiceName.NOTIFICATION)
    response = await client.post(
        "/v1/notifications",
        json={
            "tenant_id": tenant_id,
            "title": title,
            "body": body,
            "type": notification_type,
        },
    )
    return response.success


async def get_irrigation_recommendation(field_id: str) -> Optional[Dict]:
    """Get irrigation recommendation for a field"""
    client = get_service_client(ServiceName.IRRIGATION)
    response = await client.get(f"/v1/recommendations/{field_id}")
    return response.data if response.success else None


async def get_satellite_imagery(field_id: str, date: str = None) -> Optional[Dict]:
    """Get satellite imagery for a field"""
    client = get_service_client(ServiceName.SATELLITE)
    params = {"date": date} if date else None
    response = await client.get(f"/v1/imagery/{field_id}", params=params)
    return response.data if response.success else None


async def analyze_crop_health(image_path: str, crop_type: str) -> Optional[Dict]:
    """Analyze crop health from image"""
    client = get_service_client(ServiceName.CROP_HEALTH)
    response = await client.post(
        "/v1/analyze", json={"image_path": image_path, "crop_type": crop_type}
    )
    return response.data if response.success else None
