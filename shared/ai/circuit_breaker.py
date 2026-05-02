"""
Circuit Breaker Pattern for AI Services
========================================
نمط قاطع الدائرة لخدمات الذكاء الاصطناعي

Implements the circuit breaker pattern to prevent cascading failures
when external services (LLM providers, Ollama, etc.) are unavailable.

States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is down, requests fail immediately
    - HALF_OPEN: Testing if service recovered

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, TypeVar

T = TypeVar("T")


class CircuitState(StrEnum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker.

    Adaptive recovery (opt-in)
    --------------------------
    When ``adaptive_recovery`` is ``True``, the recovery wait between OPEN and
    HALF_OPEN is dynamically scaled based on an EWMA of recent failure
    intervals, bounded by ``[min_recovery_seconds, max_recovery_seconds]``.
    Default is ``False`` for full backward compatibility — existing call sites
    continue to use the fixed ``timeout_seconds`` exactly as before.
    """

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout_seconds: float = 60.0  # Time before trying again
    half_open_max_calls: int = 3  # Max concurrent calls in half-open

    # ── Adaptive recovery (opt-in, default OFF) ──
    adaptive_recovery: bool = False
    min_recovery_seconds: float = 5.0  # Hard lower bound when adaptive
    max_recovery_seconds: float = 300.0  # Hard upper bound when adaptive
    adaptive_alpha: float = 0.3  # EWMA smoothing factor in (0, 1]

    def __post_init__(self) -> None:
        # Validate adaptive recovery bounds eagerly so misconfiguration is
        # surfaced at construction, not on first failure.
        if self.adaptive_recovery:
            if self.min_recovery_seconds <= 0:
                raise ValueError("min_recovery_seconds must be > 0")
            if self.max_recovery_seconds < self.min_recovery_seconds:
                raise ValueError("max_recovery_seconds must be >= min_recovery_seconds")
            if not (0.0 < self.adaptive_alpha <= 1.0):
                raise ValueError("adaptive_alpha must be in the interval (0, 1]")


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

    # ── Adaptive recovery telemetry (populated only when enabled) ──
    # EWMA (in seconds) of intervals between consecutive failure events.
    # ``None`` until at least two failures have been observed.
    ewma_failure_interval: float | None = None
    # Last computed adaptive recovery timeout (seconds). Useful for metrics.
    last_adaptive_recovery_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "rejected_calls": self.rejected_calls,
            "state_changes": self.state_changes,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "success_rate": self.success_rate,
            "ewma_failure_interval": self.ewma_failure_interval,
            "last_adaptive_recovery_seconds": self.last_adaptive_recovery_seconds,
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


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    قاطع الدائرة للحماية من الفشل المتتالي

    Example:
        breaker = CircuitBreaker(
            name="ollama",
            config=CircuitBreakerConfig(failure_threshold=3, timeout_seconds=30)
        )

        try:
            result = await breaker.call(async_function, arg1, arg2)
        except CircuitBreakerError as e:
            # Circuit is open, use fallback
            result = await fallback_function()
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
        on_state_change: Callable[[str, CircuitState, CircuitState], None] | None = None,
    ):
        """
        Initialize CircuitBreaker.

        Args:
            name: Name for this circuit breaker
            config: Configuration
            on_state_change: Callback for state changes (name, old_state, new_state)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.on_state_change = on_state_change

        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        self._last_failure_time: float = 0
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

    def _get_recovery_timeout(self) -> float:
        """Return the (possibly adaptive) recovery timeout in seconds.

        With ``adaptive_recovery`` disabled this returns ``timeout_seconds``
        unchanged so behavior is identical to the original implementation.
        With it enabled, the value scales with the EWMA of failure intervals,
        clamped to ``[min_recovery_seconds, max_recovery_seconds]``. A short
        EWMA (rapid, repeated failures) shortens recovery probes; a long EWMA
        (rare, isolated failures) lengthens them.
        """
        cfg = self.config
        if not cfg.adaptive_recovery:
            return cfg.timeout_seconds

        ewma = self._stats.ewma_failure_interval
        if ewma is None:
            # Not enough data yet — fall back to configured base timeout but
            # still respect the adaptive bounds.
            adaptive = cfg.timeout_seconds
        else:
            # Use the EWMA of inter-failure intervals directly as the recovery
            # signal: rapid repeated failures → short EWMA → faster probes;
            # rare isolated failures → long EWMA → slower probes. The value is
            # then clamped to ``[min_recovery_seconds, max_recovery_seconds]``
            # below, so ``timeout_seconds`` is not a scaling factor here. This
            # also avoids a latent ZeroDivisionError if a caller (legitimately
            # or by misconfiguration) sets ``timeout_seconds=0``.
            adaptive = ewma

        clamped = max(cfg.min_recovery_seconds, min(cfg.max_recovery_seconds, adaptive))
        self._stats.last_adaptive_recovery_seconds = clamped
        return clamped

    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset from open state.

        Uses ``time.monotonic()`` so wall-clock adjustments (NTP slews, VM
        clock drift, suspend/resume) cannot make ``elapsed`` go negative or
        leap forward and prematurely transition the breaker to HALF_OPEN.
        Wall-clock timestamps are still used for human-readable telemetry on
        ``CircuitBreakerStats.last_failure_time``.
        """
        if self._state != CircuitState.OPEN:
            return False
        elapsed = time.monotonic() - self._last_failure_time
        return elapsed >= self._get_recovery_timeout()

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
        self._stats.last_success_time = datetime.now(UTC)

        if self._state == CircuitState.HALF_OPEN:
            if self._stats.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def _record_failure(self) -> None:
        """Record a failed call."""
        # Monotonic time is used for elapsed/EWMA computations so wall-clock
        # adjustments (NTP, VM clock drift) cannot produce negative intervals
        # that would distort adaptive recovery. Wall-clock ``datetime`` is
        # retained on ``stats.last_failure_time`` for telemetry only.
        now_mono = time.monotonic()
        # ``self._last_failure_time`` is initialized to 0.0 in __init__ and acts
        # as a sentinel meaning "no previous failure observed". We capture it
        # *before* updating so the EWMA below can compare against the prior
        # failure timestamp; the ``> 0`` guard skips the very first failure.
        previous_failure_mono = self._last_failure_time

        self._stats.total_calls += 1
        self._stats.failed_calls += 1
        self._stats.consecutive_failures += 1
        self._stats.consecutive_successes = 0
        self._stats.last_failure_time = datetime.now(UTC)
        self._last_failure_time = now_mono

        # Update EWMA of inter-failure intervals only when adaptive recovery
        # is enabled, to avoid any overhead for the default code path.
        if self.config.adaptive_recovery and previous_failure_mono > 0:
            interval = now_mono - previous_failure_mono
            if interval > 0:
                alpha = self.config.adaptive_alpha
                prev = self._stats.ewma_failure_interval
                self._stats.ewma_failure_interval = (
                    interval if prev is None else (alpha * interval) + ((1.0 - alpha) * prev)
                )

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
        func: Callable[..., Any],
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a function through the circuit breaker.

        تنفيذ دالة من خلال قاطع الدائرة

        Args:
            func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Result of the function

        Raises:
            CircuitBreakerError: If circuit is open
        """
        async with self._lock:
            # Check if we should try to reset
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)

            # Reject if open
            if self._state == CircuitState.OPEN:
                self._record_rejection()
                recovery_timeout = self._get_recovery_timeout()
                retry_after = recovery_timeout - (time.monotonic() - self._last_failure_time)
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
                "adaptive_recovery": self.config.adaptive_recovery,
                "min_recovery_seconds": self.config.min_recovery_seconds,
                "max_recovery_seconds": self.config.max_recovery_seconds,
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
