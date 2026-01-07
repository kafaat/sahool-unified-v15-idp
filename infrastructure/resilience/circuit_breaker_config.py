#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Circuit Breaker Configuration
إعدادات الدارة القصيرة
═══════════════════════════════════════════════════════════════════════════════════════

Implements Advanced Circuit Breaker pattern for critical endpoints.

Features:
- Login endpoint protection (5 failures in 10s = open circuit)
- Database query protection
- External API protection
- Automatic recovery with half-open state
- Metrics and monitoring integration

Usage:
    from circuit_breaker_config import CircuitBreaker, login_circuit_breaker

    @login_circuit_breaker
    async def authenticate_user(credentials):
        # If circuit is open, returns fallback immediately
        return await db.query_user(credentials)

═══════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("circuit-breaker")

# ═══════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER STATE
# ═══════════════════════════════════════════════════════════════════════════════


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking calls, returning fallback
    HALF_OPEN = "half_open"  # Testing if service recovered


# ═══════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class CircuitBreakerConfig:
    """Configuration for a circuit breaker instance."""

    name: str

    # Failure threshold to open circuit
    failure_threshold: int = 5

    # Time window for counting failures (seconds)
    failure_window: float = 10.0

    # Time to wait before trying again (seconds)
    recovery_timeout: float = 60.0

    # Number of successful calls in half-open to close circuit
    success_threshold: int = 3

    # Timeout for individual calls (seconds)
    call_timeout: float = 5.0

    # Enable metrics collection
    enable_metrics: bool = True

    # Fallback response when circuit is open
    fallback_response: Any = None
    fallback_message: str = "Service temporarily unavailable. Please try again later."
    fallback_message_ar: str = "الخدمة غير متاحة مؤقتاً. يرجى المحاولة مرة أخرى لاحقاً."


# ═══════════════════════════════════════════════════════════════════════════════
# PREDEFINED CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Login endpoint - strict protection
LOGIN_CONFIG = CircuitBreakerConfig(
    name="login",
    failure_threshold=5,
    failure_window=10.0,
    recovery_timeout=60.0,
    success_threshold=3,
    call_timeout=5.0,
    fallback_message="Too many login attempts. Please wait a moment.",
    fallback_message_ar="محاولات تسجيل دخول كثيرة. يرجى الانتظار قليلاً.",
)

# Database queries - moderate protection
DATABASE_CONFIG = CircuitBreakerConfig(
    name="database",
    failure_threshold=10,
    failure_window=30.0,
    recovery_timeout=30.0,
    success_threshold=5,
    call_timeout=10.0,
    fallback_message="Database temporarily unavailable.",
    fallback_message_ar="قاعدة البيانات غير متاحة مؤقتاً.",
)

# External APIs (weather, SMS, etc.) - lenient protection
EXTERNAL_API_CONFIG = CircuitBreakerConfig(
    name="external_api",
    failure_threshold=15,
    failure_window=60.0,
    recovery_timeout=120.0,
    success_threshold=3,
    call_timeout=30.0,
    fallback_message="External service temporarily unavailable.",
    fallback_message_ar="الخدمة الخارجية غير متاحة مؤقتاً.",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CIRCUIT BREAKER IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class CircuitBreakerMetrics:
    """Metrics for monitoring circuit breaker behavior."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0  # Calls rejected due to open circuit
    circuit_opened_count: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    state_changes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "circuit_opened_count": self.circuit_opened_count,
            "success_rate": self.successful_calls / max(1, self.total_calls) * 100,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
        }


class CircuitBreaker:
    """
    Circuit Breaker implementation with async support.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Circuit tripped, calls return fallback immediately
    - HALF_OPEN: Testing recovery, limited calls allowed
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failures: list = []  # Timestamps of recent failures
        self.successes_in_half_open = 0
        self.last_failure_time: float | None = None
        self.opened_at: float | None = None
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN

    def _clean_old_failures(self):
        """Remove failures outside the time window."""
        cutoff = time.time() - self.config.failure_window
        self.failures = [f for f in self.failures if f > cutoff]

    def _should_trip(self) -> bool:
        """Check if circuit should trip open."""
        self._clean_old_failures()
        return len(self.failures) >= self.config.failure_threshold

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self.opened_at is None:
            return True
        return time.time() - self.opened_at >= self.config.recovery_timeout

    def _record_success(self):
        """Record a successful call."""
        self.metrics.successful_calls += 1
        self.metrics.last_success_time = time.time()

        if self.is_half_open:
            self.successes_in_half_open += 1
            if self.successes_in_half_open >= self.config.success_threshold:
                self._close()

    def _record_failure(self):
        """Record a failed call."""
        now = time.time()
        self.failures.append(now)
        self.metrics.failed_calls += 1
        self.metrics.last_failure_time = now
        self.last_failure_time = now

        if self.is_half_open:
            # Immediately reopen on failure during half-open
            self._open()
        elif self._should_trip():
            self._open()

    def _open(self):
        """Open the circuit."""
        if self.state != CircuitState.OPEN:
            logger.warning(f"⚡ Circuit '{self.config.name}' OPENED - too many failures")
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
            self.metrics.circuit_opened_count += 1
            self.metrics.state_changes.append(
                {
                    "time": datetime.now(UTC).isoformat(),
                    "from": "closed/half_open",
                    "to": "open",
                }
            )

    def _close(self):
        """Close the circuit (resume normal operation)."""
        logger.info(f"✅ Circuit '{self.config.name}' CLOSED - recovered")
        self.state = CircuitState.CLOSED
        self.failures = []
        self.successes_in_half_open = 0
        self.opened_at = None
        self.metrics.state_changes.append(
            {
                "time": datetime.now(UTC).isoformat(),
                "from": "half_open",
                "to": "closed",
            }
        )

    def _half_open(self):
        """Enter half-open state to test recovery."""
        logger.info(f"🔄 Circuit '{self.config.name}' HALF-OPEN - testing recovery")
        self.state = CircuitState.HALF_OPEN
        self.successes_in_half_open = 0
        self.metrics.state_changes.append(
            {
                "time": datetime.now(UTC).isoformat(),
                "from": "open",
                "to": "half_open",
            }
        )

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with circuit breaker protection."""
        async with self._lock:
            self.metrics.total_calls += 1

            # Check if circuit is open
            if self.is_open:
                if self._should_attempt_recovery():
                    self._half_open()
                else:
                    self.metrics.rejected_calls += 1
                    return self._get_fallback_response()

        # Execute the function
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.call_timeout,
            )
            self._record_success()
            return result

        except TimeoutError:
            logger.warning(f"⏰ Circuit '{self.config.name}': call timed out")
            self._record_failure()
            return self._get_fallback_response()

        except Exception as e:
            logger.warning(f"❌ Circuit '{self.config.name}': call failed - {e}")
            self._record_failure()
            raise

    def _get_fallback_response(self) -> dict:
        """Return fallback response when circuit is open."""
        if self.config.fallback_response is not None:
            return self.config.fallback_response

        return {
            "success": False,
            "error": "circuit_breaker_open",
            "message": self.config.fallback_message,
            "message_ar": self.config.fallback_message_ar,
            "retry_after": int(self.config.recovery_timeout),
        }

    def get_status(self) -> dict:
        """Get current circuit breaker status."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "failures_in_window": len(self.failures),
            "failure_threshold": self.config.failure_threshold,
            "opened_at": self.opened_at,
            "metrics": self.metrics.to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATOR FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

# Global circuit breaker instances
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str, config: CircuitBreakerConfig | None = None) -> CircuitBreaker:
    """Get or create a circuit breaker instance."""
    if name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig(name=name)
        _circuit_breakers[name] = CircuitBreaker(config)
    return _circuit_breakers[name]


def circuit_breaker(config: CircuitBreakerConfig):
    """
    Decorator to protect a function with a circuit breaker.

    Usage:
        @circuit_breaker(LOGIN_CONFIG)
        async def authenticate_user(credentials):
            return await db.query_user(credentials)
    """

    def decorator(func: Callable):
        cb = get_circuit_breaker(config.name, config)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)

        # Attach circuit breaker for status access
        wrapper.circuit_breaker = cb
        return wrapper

    return decorator


# Convenience decorators for common use cases
def login_circuit_breaker(func: Callable):
    """Decorator specifically for login endpoints."""
    return circuit_breaker(LOGIN_CONFIG)(func)


def database_circuit_breaker(func: Callable):
    """Decorator for database operations."""
    return circuit_breaker(DATABASE_CONFIG)(func)


def external_api_circuit_breaker(func: Callable):
    """Decorator for external API calls."""
    return circuit_breaker(EXTERNAL_API_CONFIG)(func)


# ═══════════════════════════════════════════════════════════════════════════════
# MONITORING ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════


def get_all_circuit_breaker_status() -> dict:
    """Get status of all circuit breakers for monitoring."""
    return {name: cb.get_status() for name, cb in _circuit_breakers.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


def create_circuit_breaker_routes(app):
    """
    Add circuit breaker monitoring routes to FastAPI app.

    Usage:
        from circuit_breaker_config import create_circuit_breaker_routes
        create_circuit_breaker_routes(app)
    """
    from fastapi import APIRouter
    from fastapi.responses import JSONResponse

    router = APIRouter(prefix="/circuit-breakers", tags=["monitoring"])

    @router.get("/status")
    async def get_status():
        """Get all circuit breaker statuses."""
        return JSONResponse(content=get_all_circuit_breaker_status())

    @router.get("/status/{name}")
    async def get_single_status(name: str):
        """Get specific circuit breaker status."""
        if name in _circuit_breakers:
            return JSONResponse(content=_circuit_breakers[name].get_status())
        return JSONResponse(content={"error": "not_found"}, status_code=404)

    @router.post("/reset/{name}")
    async def reset_circuit_breaker(name: str):
        """Manually reset a circuit breaker to closed state."""
        if name in _circuit_breakers:
            _circuit_breakers[name]._close()
            return JSONResponse(content={"message": f"Circuit '{name}' reset to CLOSED"})
        return JSONResponse(content={"error": "not_found"}, status_code=404)

    app.include_router(router)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example: Protected login function
    @login_circuit_breaker
    async def authenticate(username: str, password: str):
        # Simulated database call
        await asyncio.sleep(0.1)
        if username == "fail":
            raise Exception("Authentication failed")
        return {"user_id": 123, "username": username}

    async def test():
        # Normal calls
        for i in range(3):
            result = await authenticate("user1", "pass")
            print(f"Call {i + 1}: {result}")

        # Failing calls - should trip circuit
        for i in range(7):
            try:
                result = await authenticate("fail", "pass")
                print(f"Fail call {i + 1}: {result}")
            except Exception as e:
                print(f"Fail call {i + 1}: Exception - {e}")

        # Circuit should be open now
        result = await authenticate("user2", "pass")
        print(f"After circuit open: {result}")

        # Print status
        print("\nCircuit Breaker Status:")
        print(json.dumps(get_all_circuit_breaker_status(), indent=2))

    asyncio.run(test())
