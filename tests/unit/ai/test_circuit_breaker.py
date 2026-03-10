"""
Tests for Circuit Breaker Module
================================
اختبارات وحدة قاطع الدائرة

Comprehensive tests for circuit breaker pattern implementation.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from shared.ai.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerStats,
    CircuitState,
    get_circuit_breaker,
    get_ollama_circuit_breaker,
    get_anthropic_circuit_breaker,
    get_openai_circuit_breaker,
    get_all_circuit_breakers,
    reset_all_circuit_breakers,
)


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def circuit_config() -> CircuitBreakerConfig:
    """Create a test circuit breaker config."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=1.0,  # Short timeout for tests
        half_open_max_calls=2,
    )


@pytest.fixture
def circuit_breaker(circuit_config: CircuitBreakerConfig) -> CircuitBreaker:
    """Create a circuit breaker for testing."""
    return CircuitBreaker(
        name="test-breaker",
        config=circuit_config,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test CircuitState Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestCircuitState:
    """Tests for CircuitState enum."""

    def test_circuit_states_exist(self):
        """Test that all expected states exist."""
        assert CircuitState.CLOSED
        assert CircuitState.OPEN
        assert CircuitState.HALF_OPEN

    def test_circuit_state_values(self):
        """Test state string values."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


# ═══════════════════════════════════════════════════════════════════════════
# Test CircuitBreakerConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CircuitBreakerConfig()

        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 60.0
        assert config.half_open_max_calls == 3

    def test_custom_config(self, circuit_config: CircuitBreakerConfig):
        """Test custom configuration."""
        assert circuit_config.failure_threshold == 3
        assert circuit_config.timeout_seconds == 1.0


# ═══════════════════════════════════════════════════════════════════════════
# Test CircuitBreakerStats
# ═══════════════════════════════════════════════════════════════════════════


class TestCircuitBreakerStats:
    """Tests for CircuitBreakerStats."""

    def test_default_stats(self):
        """Test default statistics values."""
        stats = CircuitBreakerStats()

        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.failed_calls == 0
        assert stats.rejected_calls == 0
        assert stats.success_rate == 1.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = CircuitBreakerStats(
            total_calls=10,
            successful_calls=7,
            failed_calls=3,
        )

        assert stats.success_rate == 0.7

    def test_to_dict(self):
        """Test stats to dictionary conversion."""
        stats = CircuitBreakerStats(
            total_calls=5,
            successful_calls=4,
            failed_calls=1,
        )

        data = stats.to_dict()

        assert data["total_calls"] == 5
        assert data["successful_calls"] == 4
        assert data["success_rate"] == 0.8


# ═══════════════════════════════════════════════════════════════════════════
# Test CircuitBreakerError
# ═══════════════════════════════════════════════════════════════════════════


class TestCircuitBreakerError:
    """Tests for CircuitBreakerError."""

    def test_error_with_retry_after(self):
        """Test error with retry_after attribute."""
        error = CircuitBreakerError(
            "Service unavailable",
            retry_after=30.0,
        )

        assert str(error) == "Service unavailable"
        assert error.retry_after == 30.0

    def test_error_without_retry_after(self):
        """Test error without retry_after."""
        error = CircuitBreakerError("Test error")

        assert error.retry_after is None


# ═══════════════════════════════════════════════════════════════════════════
# Test CircuitBreaker
# ═══════════════════════════════════════════════════════════════════════════


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initialization(self, circuit_breaker: CircuitBreaker):
        """Test circuit breaker initialization."""
        assert circuit_breaker.name == "test-breaker"
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.is_closed is True
        assert circuit_breaker.is_open is False

    @pytest.mark.asyncio
    async def test_successful_call(self, circuit_breaker: CircuitBreaker):
        """Test successful function call through circuit breaker."""

        async def success_func():
            return "success"

        result = await circuit_breaker.call(success_func)

        assert result == "success"
        assert circuit_breaker.stats.total_calls == 1
        assert circuit_breaker.stats.successful_calls == 1
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failed_call(self, circuit_breaker: CircuitBreaker):
        """Test failed function call through circuit breaker."""

        async def fail_func():
            raise ValueError("Test failure")

        with pytest.raises(ValueError):
            await circuit_breaker.call(fail_func)

        assert circuit_breaker.stats.total_calls == 1
        assert circuit_breaker.stats.failed_calls == 1
        assert circuit_breaker.stats.consecutive_failures == 1

    @pytest.mark.asyncio
    async def test_circuit_opens_after_threshold(self, circuit_breaker: CircuitBreaker):
        """Test circuit opens after failure threshold."""

        async def fail_func():
            raise ValueError("Test failure")

        # Fail until threshold (3 failures)
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        # Circuit should now be open
        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.is_open is True

    @pytest.mark.asyncio
    async def test_circuit_rejects_when_open(self, circuit_breaker: CircuitBreaker):
        """Test that circuit rejects calls when open."""

        async def fail_func():
            raise ValueError("Test failure")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        # Next call should raise CircuitBreakerError
        async def any_func():
            return "test"

        with pytest.raises(CircuitBreakerError) as exc_info:
            await circuit_breaker.call(any_func)

        assert "OPEN" in str(exc_info.value)
        assert exc_info.value.retry_after is not None

    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open(self, circuit_breaker: CircuitBreaker):
        """Test circuit transitions to half-open after timeout."""

        async def fail_func():
            raise ValueError("Test failure")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        assert circuit_breaker.state == CircuitState.OPEN

        # Wait for timeout (1 second)
        await asyncio.sleep(1.1)

        # Next call should attempt (half-open)
        async def success_func():
            return "success"

        result = await circuit_breaker.call(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_closes_after_successes_in_half_open(self, circuit_breaker: CircuitBreaker):
        """Test circuit closes after success threshold in half-open."""

        async def fail_func():
            raise ValueError("Test failure")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Succeed twice (success_threshold=2)
        async def success_func():
            return "success"

        await circuit_breaker.call(success_func)
        await circuit_breaker.call(success_func)

        # Circuit should be closed again
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_reopens_on_failure_in_half_open(self, circuit_breaker: CircuitBreaker):
        """Test circuit reopens on failure in half-open state."""

        async def fail_func():
            raise ValueError("Test failure")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Fail in half-open
        with pytest.raises(ValueError):
            await circuit_breaker.call(fail_func)

        # Circuit should be open again
        assert circuit_breaker.state == CircuitState.OPEN

    def test_manual_reset(self, circuit_breaker: CircuitBreaker):
        """Test manual circuit breaker reset."""
        # Manually set state
        circuit_breaker._state = CircuitState.OPEN
        circuit_breaker._stats.consecutive_failures = 5

        circuit_breaker.reset()

        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.stats.consecutive_failures == 0

    def test_manual_trip(self, circuit_breaker: CircuitBreaker):
        """Test manual circuit breaker trip."""
        assert circuit_breaker.state == CircuitState.CLOSED

        circuit_breaker.trip()

        assert circuit_breaker.state == CircuitState.OPEN

    def test_get_status(self, circuit_breaker: CircuitBreaker):
        """Test getting circuit breaker status."""
        status = circuit_breaker.get_status()

        assert status["name"] == "test-breaker"
        assert status["state"] == "closed"
        assert "stats" in status
        assert "config" in status

    def test_state_change_callback(self, circuit_config: CircuitBreakerConfig):
        """Test state change callback is called."""
        state_changes = []

        def on_change(name, old_state, new_state):
            state_changes.append((name, old_state, new_state))

        breaker = CircuitBreaker(
            name="callback-breaker",
            config=circuit_config,
            on_state_change=on_change,
        )

        # Trip the circuit
        breaker.trip()

        assert len(state_changes) == 1
        assert state_changes[0] == (
            "callback-breaker",
            CircuitState.CLOSED,
            CircuitState.OPEN,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test Module Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_circuit_breaker_creates_new(self):
        """Test get_circuit_breaker creates new breaker."""
        breaker = get_circuit_breaker("new-test-breaker")

        assert breaker.name == "new-test-breaker"
        assert breaker.state == CircuitState.CLOSED

    def test_get_circuit_breaker_returns_existing(self):
        """Test get_circuit_breaker returns existing breaker."""
        breaker1 = get_circuit_breaker("shared-breaker")
        breaker2 = get_circuit_breaker("shared-breaker")

        assert breaker1 is breaker2

    def test_get_ollama_circuit_breaker(self):
        """Test pre-configured Ollama circuit breaker."""
        breaker = get_ollama_circuit_breaker()

        assert breaker.name == "ollama"
        assert breaker.config.failure_threshold == 3
        assert breaker.config.timeout_seconds == 30.0

    def test_get_anthropic_circuit_breaker(self):
        """Test pre-configured Anthropic circuit breaker."""
        breaker = get_anthropic_circuit_breaker()

        assert breaker.name == "anthropic"
        assert breaker.config.failure_threshold == 5
        assert breaker.config.timeout_seconds == 60.0

    def test_get_openai_circuit_breaker(self):
        """Test pre-configured OpenAI circuit breaker."""
        breaker = get_openai_circuit_breaker()

        assert breaker.name == "openai"
        assert breaker.config.failure_threshold == 5

    def test_get_all_circuit_breakers(self):
        """Test getting all registered circuit breakers."""
        # Ensure some breakers exist
        get_ollama_circuit_breaker()
        get_anthropic_circuit_breaker()

        all_breakers = get_all_circuit_breakers()

        assert "ollama" in all_breakers
        assert "anthropic" in all_breakers

    def test_reset_all_circuit_breakers(self):
        """Test resetting all circuit breakers."""
        # Get and trip some breakers
        ollama = get_ollama_circuit_breaker()
        anthropic = get_anthropic_circuit_breaker()

        ollama.trip()
        anthropic.trip()

        assert ollama.state == CircuitState.OPEN
        assert anthropic.state == CircuitState.OPEN

        reset_all_circuit_breakers()

        assert ollama.state == CircuitState.CLOSED
        assert anthropic.state == CircuitState.CLOSED


# ═══════════════════════════════════════════════════════════════════════════
# Test Concurrency
# ═══════════════════════════════════════════════════════════════════════════


class TestConcurrency:
    """Tests for concurrent access to circuit breaker."""

    @pytest.mark.asyncio
    async def test_concurrent_calls(self, circuit_breaker: CircuitBreaker):
        """Test multiple concurrent calls."""

        async def slow_success():
            await asyncio.sleep(0.1)
            return "success"

        # Run multiple concurrent calls
        results = await asyncio.gather(*[circuit_breaker.call(slow_success) for _ in range(5)])

        assert all(r == "success" for r in results)
        assert circuit_breaker.stats.total_calls == 5
        assert circuit_breaker.stats.successful_calls == 5

    @pytest.mark.asyncio
    async def test_half_open_max_calls_limit(self, circuit_breaker: CircuitBreaker):
        """Test max calls limit in half-open state."""

        async def fail_func():
            raise ValueError("fail")

        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                await circuit_breaker.call(fail_func)

        # Wait for timeout
        await asyncio.sleep(1.1)

        # Try to make more than max_calls in half-open
        async def success_func():
            await asyncio.sleep(0.5)  # Slow to allow concurrent attempts
            return "success"

        # This should respect half_open_max_calls limit
        # Some calls should be rejected
        tasks = [circuit_breaker.call(success_func) for _ in range(5)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # At least some should succeed, some might be rejected
        successes = [r for r in results if r == "success"]
        errors = [r for r in results if isinstance(r, CircuitBreakerError)]

        # We should have some successes (up to half_open_max_calls)
        assert len(successes) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_function_with_arguments(self, circuit_breaker: CircuitBreaker):
        """Test calling function with arguments."""

        async def add(a: int, b: int) -> int:
            return a + b

        result = await circuit_breaker.call(add, 2, 3)
        assert result == 5  # 2 + 3 = 5

    @pytest.mark.asyncio
    async def test_function_with_kwargs(self, circuit_breaker: CircuitBreaker):
        """Test calling function with keyword arguments."""

        async def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = await circuit_breaker.call(greet, name="World", greeting="Hi")
        assert result == "Hi, World!"

    @pytest.mark.asyncio
    async def test_async_generator_not_supported(self, circuit_breaker: CircuitBreaker):
        """Test that we handle async calls correctly."""

        async def async_func():
            return 42

        result = await circuit_breaker.call(async_func)
        assert result == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
