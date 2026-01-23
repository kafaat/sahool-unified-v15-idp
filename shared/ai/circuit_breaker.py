"""
Circuit Breaker Pattern for AI Services
========================================
نمط قاطع الدائرة لخدمات الذكاء الاصطناعي

Implements the circuit breaker pattern to prevent cascading failures
when external services (LLM providers, Ollama, etc.) are unavailable.

States:
    - CLOSED: Normal operation, requests pass through (عمل عادي)
    - OPEN: Service is down, requests fail immediately (الخدمة معطلة)
    - HALF_OPEN: Testing if service has recovered (اختبار استعادة الخدمة)

Features:
    - Async-first design for AI service calls
    - Configurable thresholds and timeouts
    - State change callbacks for monitoring
    - Pre-configured breakers for common AI services
    - Detailed statistics and monitoring

Author: SAHOOL Platform Team
Updated: January 2026

Example:
    >>> breaker = CircuitBreaker(
    ...     name="ollama",
    ...     config=CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30)
    ... )
    >>> try:
    ...     result = await breaker.call(async_llm_function, prompt)
    ... except CircuitBreakerError as e:
    ...     # Circuit is open, use fallback
    ...     result = await fallback_function(prompt)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: float = 60.0  # Time before trying again
    half_open_max_calls: int = 3  # Max concurrent calls in half-open


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0
    last_failure_time: datetime | None = None
    last_success_time: datetime | None = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "state_changes": self.state_changes,
            "last_failure_time": self.last_failure_time.isoformat()
            if self.last_failure_time
            else None,
            "last_success_time": self.last_success_time.isoformat()
            if self.last_success_time
            else None,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "success_rate": self.success_rate,
        }

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_calls == 0:
            return 1.0
        return self.successful_calls / self.total_calls


class CircuitBreakerError(Exception):
    """Exception raised when circuit is open."""

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


# Type alias for state change callback
StateChangeCallback = Callable[[str, "CircuitState", "CircuitState"], None]


class CircuitBreaker:
    """
    Async circuit breaker for protecting against cascading failures in AI services.
    قاطع الدائرة غير المتزامن للحماية من الفشل المتتالي في خدمات الذكاء الاصطناعي

    This implementation is designed specifically for async AI service calls,
    providing protection against:
    - Slow or unresponsive LLM providers
    - Network failures to AI endpoints
    - Service overload conditions

    The circuit breaker has three states:
    1. CLOSED: Normal operation - all requests pass through
    2. OPEN: Failures exceeded threshold - requests fail fast
    3. HALF_OPEN: Testing recovery - limited requests allowed

    Attributes:
        name: Identifier for this circuit breaker
        config: Configuration settings
        on_state_change: Optional callback for state transitions

    Example:
        >>> breaker = CircuitBreaker(
        ...     name="ollama",
        ...     config=CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30)
        ... )
        >>> try:
        ...     result = await breaker.call(async_function, arg1, arg2)
        ... except CircuitBreakerError as e:
        ...     # Circuit is open, use fallback
        ...     result = await fallback_function()

    Thread Safety:
        This implementation uses asyncio.Lock for thread-safe state transitions.
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
        on_state_change: StateChangeCallback | None = None,
    ) -> None:
        """
        Initialize CircuitBreaker.

        Args:
            name: Unique name for this circuit breaker (used in logs and metrics)
            config: Configuration settings (uses defaults if None)
            on_state_change: Optional callback invoked on state changes
                           Signature: (name, old_state, new_state) -> None
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.on_state_change = on_state_change

        self._state: CircuitState = CircuitState.CLOSED
        self._stats: CircuitBreakerStats = CircuitBreakerStats()
        self._lock: asyncio.Lock = asyncio.Lock()
        self._last_failure_time: float = 0.0
        self._half_open_calls: int = 0

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        return self._state

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get statistics."""
        return self._stats

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset from open state."""
        if self._state != CircuitState.OPEN:
            return False
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.config.timeout_seconds

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._stats.state_changes += 1

            if new_state == CircuitState.HALF_OPEN:
                self._half_open_calls = 0

            if self.on_state_change:
                self.on_state_change(self.name, old_state, new_state)

    def _record_success(self) -> None:
        """Record a successful call."""
        self._stats.total_calls += 1
        self._stats.successful_calls += 1
        self._stats.consecutive_successes += 1
        self._stats.consecutive_failures = 0
        self._stats.last_success_time = datetime.utcnow()

        if self._state == CircuitState.HALF_OPEN:
            if self._stats.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def _record_failure(self) -> None:
        """Record a failed call."""
        self._stats.total_calls += 1
        self._stats.failed_calls += 1
        self._stats.consecutive_failures += 1
        self._stats.consecutive_successes = 0
        self._stats.last_failure_time = datetime.utcnow()
        self._last_failure_time = time.time()

        if self._state == CircuitState.CLOSED:
            if self._stats.consecutive_failures >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)

    def _record_rejection(self) -> None:
        """Record a rejected call."""
        self._stats.rejected_calls += 1

    async def call(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute an async function through the circuit breaker.
        تنفيذ دالة غير متزامنة من خلال قاطع الدائرة

        This method wraps async function calls with circuit breaker logic:
        1. Checks if circuit is open (fails fast if so)
        2. Executes the function if circuit is closed or half-open
        3. Records success/failure and updates state accordingly

        Args:
            func: Async function to execute (must return Awaitable)
            *args: Positional arguments passed to the function
            **kwargs: Keyword arguments passed to the function

        Returns:
            Result of the function call (type T)

        Raises:
            CircuitBreakerError: If circuit is open and requests are blocked
            Exception: Any exception raised by the wrapped function

        Example:
            >>> async def call_llm(prompt: str) -> str:
            ...     # Call to LLM provider
            ...     return response
            >>> result = await breaker.call(call_llm, "Hello, world!")
        """
        async with self._lock:
            # Check if we should try to reset
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)

            # Reject if open
            if self._state == CircuitState.OPEN:
                self._record_rejection()
                retry_after = self.config.timeout_seconds - (time.time() - self._last_failure_time)
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. Service unavailable.",
                    retry_after=max(0, retry_after),
                )

            # Limit calls in half-open state
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    self._record_rejection()
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN with max calls reached.",
                        retry_after=1.0,
                    )
                self._half_open_calls += 1

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            async with self._lock:
                self._record_success()
            return result
        except Exception:
            async with self._lock:
                self._record_failure()
            raise

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._state = CircuitState.CLOSED
        self._stats.consecutive_failures = 0
        self._stats.consecutive_successes = 0
        self._half_open_calls = 0

    def trip(self) -> None:
        """Manually trip the circuit breaker."""
        self._transition_to(CircuitState.OPEN)
        self._last_failure_time = time.time()

    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self._state.value,
            "stats": self._stats.to_dict(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            },
        }


# Registry for circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    config: CircuitBreakerConfig | None = None,
) -> CircuitBreaker:
    """
    Get or create a named circuit breaker.

    الحصول على أو إنشاء قاطع دائرة مسمى
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name=name, config=config)
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict[str, CircuitBreaker]:
    """Get all registered circuit breakers."""
    return _circuit_breakers.copy()


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers."""
    for breaker in _circuit_breakers.values():
        breaker.reset()


# Pre-configured circuit breakers for common services
def get_ollama_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for Ollama service."""
    return get_circuit_breaker(
        "ollama",
        CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0,
            half_open_max_calls=2,
        ),
    )


def get_anthropic_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for Anthropic API."""
    return get_circuit_breaker(
        "anthropic",
        CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=60.0,
            half_open_max_calls=3,
        ),
    )


def get_openai_circuit_breaker() -> CircuitBreaker:
    """Get circuit breaker for OpenAI API."""
    return get_circuit_breaker(
        "openai",
        CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=60.0,
            half_open_max_calls=3,
        ),
    )
