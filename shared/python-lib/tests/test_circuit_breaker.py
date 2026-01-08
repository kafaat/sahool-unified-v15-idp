"""
Tests for Circuit Breaker (Resilient Client)
"""

import asyncio
from unittest.mock import patch

import pytest
from sahool_core.resilient_client import (
    CircuitBreaker,
    CircuitState,
    circuit_breaker,
)


class TestCircuitBreakerInit:
    """Test Circuit Breaker initialization"""

    def test_default_configuration(self):
        """Test default configuration values"""
        cb = CircuitBreaker()

        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60
        assert len(cb._endpoints) == 3

    def test_custom_configuration(self):
        """Test custom configuration"""
        cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30,
            endpoints=["http://custom:8000"],
        )

        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 30
        assert cb._endpoints == ["http://custom:8000"]


class TestCircuitBreakerStates:
    """Test circuit state transitions"""

    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self):
        """Test that initial state is CLOSED"""
        cb = CircuitBreaker()

        assert await cb._is_circuit_open("test-service") is False
        assert cb._states.get("test-service", CircuitState.CLOSED) == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Test circuit opens after threshold failures"""
        cb = CircuitBreaker(failure_threshold=3)

        # Simulate 3 failures
        for _ in range(3):
            await cb._on_failure("test-service")

        assert cb._states.get("test-service") == CircuitState.OPEN
        assert await cb._is_circuit_open("test-service") is True

    @pytest.mark.asyncio
    async def test_circuit_stays_closed_below_threshold(self):
        """Test circuit stays closed below failure threshold"""
        cb = CircuitBreaker(failure_threshold=5)

        # Simulate 4 failures (below threshold)
        for _ in range(4):
            await cb._on_failure("test-service")

        assert cb._states.get("test-service", CircuitState.CLOSED) == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        """Test success resets the failure counter"""
        cb = CircuitBreaker(failure_threshold=5)

        # Simulate some failures
        for _ in range(3):
            await cb._on_failure("test-service")

        # Then success
        await cb._on_success("test-service")

        assert cb._failure_counts.get("test-service", 0) == 0
        assert cb._states.get("test-service") == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_recovery_timeout(self):
        """Test circuit transitions to HALF_OPEN after recovery timeout"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        # Open the circuit
        await cb._on_failure("test-service")
        await cb._on_failure("test-service")

        assert cb._states.get("test-service") == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(1.1)

        # Check should transition to half-open
        is_open = await cb._is_circuit_open("test-service")
        assert is_open is False
        assert cb._states.get("test-service") == CircuitState.HALF_OPEN


class TestCircuitBreakerFallback:
    """Test fallback behavior"""

    @pytest.mark.asyncio
    async def test_fallback_returns_cached_data(self):
        """Test fallback returns cached data when available"""
        cb = CircuitBreaker()

        # Pre-populate cache
        cb._cache["test-service:/api/test"] = {"data": "cached"}

        result = await cb._fallback("test-service", "/api/test")

        assert result["data"] == "cached"
        assert result["_fallback"] is True
        assert "_cached_at" in result

    @pytest.mark.asyncio
    async def test_fallback_returns_service_defaults(self):
        """Test fallback returns service-specific defaults"""
        cb = CircuitBreaker()

        # field-ops service
        result = await cb._fallback("field-ops", "/api/v1/fields")
        assert result["_fallback"] is True
        assert "data" in result

        # weather-service
        result = await cb._fallback("weather-service", "/api/v1/weather")
        assert result["_fallback"] is True
        assert "temperature" in result

        # notification-service
        result = await cb._fallback("notification-service", "/notify")
        assert result["_fallback"] is True
        assert result["queued"] is True

    @pytest.mark.asyncio
    async def test_fallback_returns_generic_for_unknown_service(self):
        """Test fallback returns generic response for unknown service"""
        cb = CircuitBreaker()

        result = await cb._fallback("unknown-service", "/api/test")

        assert result["_fallback"] is True
        assert "error" in result


class TestCircuitBreakerCall:
    """Test the main call method"""

    @pytest.mark.asyncio
    async def test_call_returns_fallback_when_circuit_open(self):
        """Test call returns fallback when circuit is open"""
        cb = CircuitBreaker(failure_threshold=1)

        # Open the circuit
        await cb._on_failure("test-service")

        result = await cb.call("test-service", "/api/test")

        assert result is not None
        assert result.get("_fallback") is True

    @pytest.mark.asyncio
    async def test_call_returns_fallback_without_aiohttp(self):
        """Test call returns fallback when aiohttp not available"""
        cb = CircuitBreaker()

        with patch.object(cb, "_try_endpoint", side_effect=RuntimeError("aiohttp not installed")):
            result = await cb.call("test-service", "/api/test")

        # Should return fallback after all endpoints fail
        assert result is not None


class TestCircuitBreakerStatus:
    """Test status and health check methods"""

    def test_get_status_empty(self):
        """Test get_status with no services tracked"""
        cb = CircuitBreaker()

        status = cb.get_status()

        assert "services" in status
        assert "endpoints" in status
        assert "config" in status
        assert status["config"]["failure_threshold"] == 5

    @pytest.mark.asyncio
    async def test_get_status_with_failures(self):
        """Test get_status after some failures"""
        cb = CircuitBreaker(failure_threshold=5)

        await cb._on_failure("service-a")
        await cb._on_failure("service-a")
        await cb._on_failure("service-b")

        status = cb.get_status()

        assert "service-a" in status["services"]
        assert status["services"]["service-a"]["failures"] == 2
        assert "service-b" in status["services"]
        assert status["services"]["service-b"]["failures"] == 1


class TestSingletonInstance:
    """Test the singleton circuit_breaker instance"""

    def test_singleton_exists(self):
        """Test that singleton instance exists"""
        assert circuit_breaker is not None
        assert isinstance(circuit_breaker, CircuitBreaker)

    def test_singleton_has_default_config(self):
        """Test singleton has default configuration"""
        assert circuit_breaker.failure_threshold == 5
        assert circuit_breaker.recovery_timeout == 60


class TestCircuitBreakerIntegration:
    """Integration-style tests for circuit breaker workflow"""

    @pytest.mark.asyncio
    async def test_full_cycle_closed_open_halfopen_closed(self):
        """Test full circuit breaker lifecycle"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        # Initial state: CLOSED
        assert cb._states.get("svc", CircuitState.CLOSED) == CircuitState.CLOSED

        # Failure 1: still CLOSED
        await cb._on_failure("svc")
        assert cb._states.get("svc", CircuitState.CLOSED) == CircuitState.CLOSED

        # Failure 2: now OPEN
        await cb._on_failure("svc")
        assert cb._states.get("svc") == CircuitState.OPEN

        # Wait for recovery
        await asyncio.sleep(1.1)

        # Check transitions to HALF_OPEN
        await cb._is_circuit_open("svc")
        assert cb._states.get("svc") == CircuitState.HALF_OPEN

        # Success: back to CLOSED
        await cb._on_success("svc")
        assert cb._states.get("svc") == CircuitState.CLOSED
        assert cb._failure_counts.get("svc", 0) == 0
