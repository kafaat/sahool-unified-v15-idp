"""
Circuit Breaker Pattern Implementation
تنفيذ نمط قاطع الدائرة

Prevents cascading failures when a service is down
"""

import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation - requests allowed
    OPEN = "open"          # Failure state - requests blocked
    HALF_OPEN = "half_open"  # Testing state - limited requests


@dataclass
class CircuitBreaker:
    """
    Circuit Breaker for service calls
    قاطع الدائرة لاستدعاءات الخدمات

    Usage:
        breaker = CircuitBreaker(name="weather-service")

        async def call_weather_api():
            return await client.get("/weather")

        try:
            result = await breaker.call(call_weather_api)
        except CircuitOpenError:
            # Handle circuit open
            pass
    """
    name: str
    failure_threshold: int = 5        # Failures before opening
    success_threshold: int = 2        # Successes before closing
    timeout_seconds: int = 30         # Time before trying again
    half_open_max_calls: int = 3      # Max calls in half-open state

    # State tracking
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    success_count: int = field(default=0)
    last_failure_time: Optional[datetime] = field(default=None)
    half_open_calls: int = field(default=0)

    def _should_try(self) -> bool:
        """Check if we should attempt the call"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = datetime.utcnow() - self.last_failure_time
                if elapsed > timedelta(seconds=self.timeout_seconds):
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self.half_open_calls < self.half_open_max_calls

        return False

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state"""
        old_state = self.state
        self.state = new_state

        # Reset counters based on transition
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0

        elif new_state == CircuitState.OPEN:
            self.success_count = 0
            self.last_failure_time = datetime.utcnow()

        elif new_state == CircuitState.HALF_OPEN:
            self.half_open_calls = 0
            self.success_count = 0

        logger.info(f"Circuit {self.name}: {old_state.value} -> {new_state.value}")

    def record_success(self):
        """Record a successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.success_count = 0

        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

        elif self.state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)

    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs,
    ) -> Any:
        """
        Execute a function through the circuit breaker
        تنفيذ دالة من خلال قاطع الدائرة

        Args:
            func: Async function to call
            fallback: Optional fallback function if circuit is open
            *args, **kwargs: Arguments for the function

        Returns:
            Result of the function or fallback

        Raises:
            CircuitOpenError: If circuit is open and no fallback provided
        """
        if not self._should_try():
            logger.warning(f"Circuit {self.name} is OPEN, rejecting call")
            if fallback:
                return await fallback(*args, **kwargs) if asyncio.iscoroutinefunction(fallback) else fallback(*args, **kwargs)
            raise CircuitOpenError(f"Circuit {self.name} is open")

        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self.record_success()
            return result

        except Exception as e:
            self.record_failure()
            logger.error(f"Circuit {self.name} recorded failure: {e}")

            if fallback:
                return await fallback(*args, **kwargs) if asyncio.iscoroutinefunction(fallback) else fallback(*args, **kwargs)
            raise

    def get_status(self) -> dict:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }

    def reset(self):
        """Reset the circuit breaker"""
        self._transition_to(CircuitState.CLOSED)
        self.last_failure_time = None


class CircuitOpenError(Exception):
    """Raised when circuit is open and call is rejected"""
    pass


# =============================================================================
# Circuit Breaker Registry
# =============================================================================

_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get or create a circuit breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
    return _circuit_breakers[name]


def get_all_circuit_statuses() -> list[dict]:
    """Get status of all circuit breakers"""
    return [cb.get_status() for cb in _circuit_breakers.values()]


def reset_all_circuits():
    """Reset all circuit breakers"""
    for cb in _circuit_breakers.values():
        cb.reset()
