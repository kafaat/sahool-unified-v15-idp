"""
SAHOOL Resilient Client with Circuit Breaker
Provides fault-tolerant API calls with automatic failover.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

try:
    import aiohttp
except ImportError:
    aiohttp = None  # type: ignore

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit Breaker for Kong API calls.

    Provides automatic failover between Kong nodes and
    prevents cascading failures by opening the circuit
    after repeated failures.

    Example:
        breaker = CircuitBreaker()
        result = await breaker.call("field-ops", "/api/v1/fields")
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        endpoints: list[str] | None = None,
    ):
        """
        Initialize Circuit Breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            endpoints: List of Kong endpoints to try
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self._states: dict[str, CircuitState] = {}
        self._failure_counts: dict[str, int] = {}
        self._last_failure_time: dict[str, datetime] = {}
        self._endpoints = endpoints or [
            "http://kong-primary:8000",
            "http://kong-secondary:8000",
            "http://kong-tertiary:8000",
        ]

        # Fallback cache
        self._cache: dict[str, dict[str, Any]] = {}

    async def call(
        self,
        service: str,
        path: str,
        method: str = "GET",
        timeout: float = 5.0,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """
        Call API with Circuit Breaker protection.

        Args:
            service: Service name (e.g., 'field-ops')
            path: API path (e.g., '/api/v1/fields')
            method: HTTP method
            timeout: Request timeout in seconds
            **kwargs: Additional arguments for aiohttp

        Returns:
            API response as dict, or fallback data
        """
        if not aiohttp:
            logger.error("aiohttp not installed")
            return await self._fallback(service, path)

        # Check circuit state
        if await self._is_circuit_open(service):
            logger.warning(f"Circuit open for {service}, using fallback")
            return await self._fallback(service, path)

        # Try each endpoint
        last_error = None
        for endpoint in self._endpoints:
            try:
                result = await self._try_endpoint(
                    endpoint, service, path, method, timeout, **kwargs
                )
                await self._on_success(service)

                # Cache successful response
                cache_key = f"{service}:{path}"
                self._cache[cache_key] = result

                return result
            except Exception as e:
                logger.error(f"Failed {endpoint}/{service}: {e}")
                last_error = e
                continue

        # All attempts failed
        await self._on_failure(service)

        if last_error:
            logger.error(f"All endpoints failed for {service}: {last_error}")

        return await self._fallback(service, path)

    async def _try_endpoint(
        self,
        endpoint: str,
        service: str,
        path: str,
        method: str,
        timeout: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Try a single endpoint."""
        if not aiohttp:
            raise RuntimeError("aiohttp not installed")

        url = f"{endpoint}{path}"
        client_timeout = aiohttp.ClientTimeout(total=timeout)

        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()

    async def _is_circuit_open(self, service: str) -> bool:
        """Check if circuit is open for service."""
        state = self._states.get(service, CircuitState.CLOSED)

        if state == CircuitState.OPEN:
            last_failure = self._last_failure_time.get(service)
            if last_failure:
                elapsed = datetime.now() - last_failure
                if elapsed > timedelta(seconds=self.recovery_timeout):
                    # Try to recover
                    self._states[service] = CircuitState.HALF_OPEN
                    logger.info(f"Circuit half-open for {service}, attempting recovery")
                    return False
                return True

        return False

    async def _on_failure(self, service: str) -> None:
        """Record a failure."""
        self._failure_counts[service] = self._failure_counts.get(service, 0) + 1
        self._last_failure_time[service] = datetime.now()

        if self._failure_counts[service] >= self.failure_threshold:
            logger.critical(
                f"Circuit OPEN for {service} after {self.failure_threshold} failures"
            )
            self._states[service] = CircuitState.OPEN

    async def _on_success(self, service: str) -> None:
        """Reset counters on success."""
        self._failure_counts[service] = 0
        self._states[service] = CircuitState.CLOSED

        if service in self._last_failure_time:
            del self._last_failure_time[service]

    async def _fallback(self, service: str, path: str) -> dict[str, Any] | None:
        """
        Provide fallback data when service is unavailable.

        Returns cached data or service-specific defaults.
        """
        # Try cache first
        cache_key = f"{service}:{path}"
        if cache_key in self._cache:
            logger.info(f"Returning cached data for {cache_key}")
            cached = self._cache[cache_key].copy()
            cached["_fallback"] = True
            cached["_cached_at"] = str(datetime.now())
            return cached

        # Service-specific fallbacks
        fallbacks: dict[str, dict[str, Any]] = {
            "field-ops": {
                "_fallback": True,
                "message": "Showing cached data",
                "data": [],
            },
            "weather-service": {
                "_fallback": True,
                "temperature": 25,
                "humidity": 50,
                "status": "offline_estimate",
            },
            "notification-service": {
                "_fallback": True,
                "queued": True,
                "message": "Notification queued for later delivery",
            },
        }

        return fallbacks.get(
            service,
            {"_fallback": True, "error": "Service temporarily unavailable"},
        )

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status for all services."""
        return {
            "services": {
                service: {
                    "state": self._states.get(service, CircuitState.CLOSED).value,
                    "failures": self._failure_counts.get(service, 0),
                    "last_failure": str(self._last_failure_time.get(service, "N/A")),
                }
                for service in set(
                    list(self._states.keys()) + list(self._failure_counts.keys())
                )
            },
            "endpoints": self._endpoints,
            "config": {
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
            },
        }

    async def health_check(self) -> dict[str, bool]:
        """Check health of all endpoints."""
        results = {}

        for endpoint in self._endpoints:
            try:
                if aiohttp:
                    timeout = aiohttp.ClientTimeout(total=2)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(f"{endpoint}/health") as resp:
                            results[endpoint] = resp.status == 200
                else:
                    results[endpoint] = False
            except Exception:
                results[endpoint] = False

        return results


# Singleton instance
circuit_breaker = CircuitBreaker()
