"""
Retry Classifier — typed retry policy on top of ``tenacity``.
=============================================================
مُصنِّف إعادة المحاولة فوق tenacity

A small, dependency-light helper that turns ad-hoc per-service ``tenacity``
retry boilerplate into a single typed entry point. Two public functions:

* :func:`classify` — map an exception instance to a :class:`FailureClass`
  using ``isinstance`` against concrete exception types only (no string
  matching, no heuristics).
* :func:`build_retry` — build a configured ``tenacity.Retrying`` /
  ``tenacity.AsyncRetrying`` that retries only the requested failure
  classes, honors ``Retry-After`` for HTTP 429/503, and refuses to retry
  ``AUTH`` failures.

Design constraints (intentional):
    - No state, no learning, no history (zero memory leaks).
    - All exception checks done structurally via ``isinstance`` against
      types we import lazily so the module imports cleanly even when
      ``redis`` / ``nats`` / ``httpx`` are not installed.
    - 100% additive — does not replace existing ``tenacity`` usage; service
      authors opt in by calling :func:`build_retry`.

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from enum import StrEnum
from typing import Any

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)


class FailureClass(StrEnum):
    """Coarse classification of failure modes for retry decisions.

    These categories are intentionally small. Anything we cannot classify
    structurally maps to :attr:`UNKNOWN` and is *not* retried by default —
    safer than retrying the wrong thing.
    """

    NETWORK = "network"  # Connection refused/reset, DNS, transient socket
    TIMEOUT = "timeout"  # Asyncio / library / HTTP read timeout
    RATE_LIMITED = "rate_limited"  # HTTP 429
    SERVER_ERROR = "server_error"  # HTTP 5xx (excluding 503 handled below)
    SERVICE_UNAVAILABLE = "service_unavailable"  # HTTP 503
    AUTH = "auth"  # HTTP 401/403 — never retry
    CLIENT_ERROR = "client_error"  # HTTP 4xx (excl. 401/403/429) — never retry
    UNKNOWN = "unknown"  # Anything we cannot classify — never retry


# Default set of classes that benefit from retrying. Callers can override.
DEFAULT_RETRYABLE: frozenset[FailureClass] = frozenset(
    {
        FailureClass.NETWORK,
        FailureClass.TIMEOUT,
        FailureClass.RATE_LIMITED,
        FailureClass.SERVER_ERROR,
        FailureClass.SERVICE_UNAVAILABLE,
    }
)


# ─────────────────────────────────────────────────────────────────────────────
# Lazy type lookups — keep import cost low and avoid hard dependencies.
# ─────────────────────────────────────────────────────────────────────────────


def _httpx_types() -> tuple[type, ...]:
    try:
        import httpx
    except ImportError:
        return ()
    # Only types we actually classify against — keep this list narrow.
    return (
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        httpx.PoolTimeout,
        httpx.RemoteProtocolError,
        httpx.HTTPStatusError,
    )


def _redis_types() -> tuple[type, ...]:
    try:
        from redis import exceptions as redis_exc  # type: ignore[import-not-found]
    except ImportError:
        return ()
    return (
        redis_exc.ConnectionError,
        redis_exc.TimeoutError,
    )


def _nats_types() -> tuple[type, ...]:
    try:
        from nats import errors as nats_errors  # type: ignore[import-not-found]
    except ImportError:
        return ()
    # Use only the most common transient error types.
    candidates = []
    for name in ("ConnectionClosedError", "TimeoutError", "NoServersError", "OutboundBufferLimitError"):
        cls = getattr(nats_errors, name, None)
        if isinstance(cls, type):
            candidates.append(cls)
    return tuple(candidates)


# ─────────────────────────────────────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────────────────────────────────────


def _classify_http_status(status_code: int) -> FailureClass:
    """Classify an HTTP status code into a :class:`FailureClass`."""
    if status_code == 429:
        return FailureClass.RATE_LIMITED
    if status_code == 503:
        return FailureClass.SERVICE_UNAVAILABLE
    if status_code in (401, 403):
        return FailureClass.AUTH
    if 500 <= status_code < 600:
        return FailureClass.SERVER_ERROR
    if 400 <= status_code < 500:
        return FailureClass.CLIENT_ERROR
    return FailureClass.UNKNOWN


def classify(exc: BaseException) -> FailureClass:
    """Classify ``exc`` into a :class:`FailureClass`.

    Uses ``isinstance`` against concrete exception types from ``httpx``,
    ``redis`` and ``nats`` (when installed). String matching is *never*
    used — unrecognized exceptions return :attr:`FailureClass.UNKNOWN`.
    """
    # Asyncio timeout (3.11+ asyncio.TimeoutError aliases TimeoutError, but
    # we test both for forward compatibility with libraries that subclass
    # only one of them).
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError)):
        return FailureClass.TIMEOUT

    # httpx — lookup is dynamic but cheap; do it once per call.
    httpx_types = _httpx_types()
    if httpx_types:
        import httpx  # noqa: PLC0415 — lazy import is intentional

        if isinstance(exc, httpx.HTTPStatusError):
            try:
                return _classify_http_status(exc.response.status_code)
            except Exception:  # pragma: no cover — defensive only
                return FailureClass.UNKNOWN
        if isinstance(exc, (httpx.ConnectError, httpx.RemoteProtocolError)):
            return FailureClass.NETWORK
        if isinstance(
            exc,
            (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout),
        ):
            return FailureClass.TIMEOUT

    # redis
    redis_types = _redis_types()
    if redis_types:
        from redis import exceptions as redis_exc  # noqa: PLC0415

        if isinstance(exc, redis_exc.TimeoutError):
            return FailureClass.TIMEOUT
        if isinstance(exc, redis_exc.ConnectionError):
            return FailureClass.NETWORK

    # nats
    nats_types = _nats_types()
    if nats_types and isinstance(exc, nats_types):
        # All of the chosen NATS error types are transient connectivity issues.
        return FailureClass.NETWORK

    # Builtin connection-style errors (used by aiohttp, asyncpg, etc.).
    if isinstance(exc, (ConnectionError, OSError)) and not isinstance(exc, TimeoutError):
        return FailureClass.NETWORK

    return FailureClass.UNKNOWN


# ─────────────────────────────────────────────────────────────────────────────
# Retry-After parsing
# ─────────────────────────────────────────────────────────────────────────────


def parse_retry_after(exc: BaseException) -> float | None:
    """Return the ``Retry-After`` hint (in seconds) from an HTTP exception.

    Returns ``None`` when the header is absent, malformed, or the exception
    is not an ``httpx.HTTPStatusError``. Only numeric ``Retry-After`` values
    are honored — HTTP-date forms are intentionally ignored to keep the
    helper free of timezone parsing bugs.
    """
    httpx_types = _httpx_types()
    if not httpx_types:
        return None
    import httpx  # noqa: PLC0415

    if not isinstance(exc, httpx.HTTPStatusError):
        return None
    try:
        raw = exc.response.headers.get("Retry-After")
    except Exception:  # pragma: no cover — defensive
        return None
    if not raw:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value < 0 or value > 3600:  # cap absurd values to 1h
        return None
    return value


# ─────────────────────────────────────────────────────────────────────────────
# Retry builder
# ─────────────────────────────────────────────────────────────────────────────


def _build_retry_predicate(
    retryable: frozenset[FailureClass],
) -> Any:
    """Return a tenacity ``retry=`` predicate that respects ``retryable``."""

    def _predicate(exc: BaseException) -> bool:
        cls = classify(exc)
        if cls is FailureClass.AUTH:
            # Defense in depth: never retry auth, even if caller asks.
            return False
        return cls in retryable

    return retry_if_exception(_predicate)


def _build_wait(
    retryable: frozenset[FailureClass],
    *,
    multiplier: float,
    max_wait: float,
) -> Any:
    """Return a wait strategy that honors ``Retry-After`` for 429/503.

    Falls back to ``wait_random_exponential`` for everything else.
    """
    base = wait_random_exponential(multiplier=multiplier, max=max_wait)
    if not retryable & {FailureClass.RATE_LIMITED, FailureClass.SERVICE_UNAVAILABLE}:
        return base

    def _wait(retry_state: Any) -> float:
        exc = retry_state.outcome.exception() if retry_state.outcome else None
        if exc is not None:
            hint = parse_retry_after(exc)
            if hint is not None:
                return min(hint, max_wait)
        return base(retry_state)

    return _wait


def build_retry(
    *,
    failure_classes: Iterable[FailureClass] | None = None,
    max_attempts: int = 3,
    multiplier: float = 0.5,
    max_wait: float = 30.0,
    asynchronous: bool = False,
) -> Retrying | AsyncRetrying:
    """Build a configured ``tenacity`` retry object.

    Parameters
    ----------
    failure_classes
        Classes that should trigger a retry. Defaults to
        :data:`DEFAULT_RETRYABLE`. Passing a set containing
        :attr:`FailureClass.AUTH` is silently ignored.
    max_attempts
        Total attempts including the first call. Must be >= 1. Internally,
        any request to retry :attr:`FailureClass.AUTH` is collapsed to
        ``stop_after_attempt(1)`` so authentication failures fail fast.
    multiplier, max_wait
        Forwarded to :func:`tenacity.wait_random_exponential` for non
        ``Retry-After`` waits.
    asynchronous
        When True, returns :class:`tenacity.AsyncRetrying`; otherwise a
        synchronous :class:`tenacity.Retrying`.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    requested = frozenset(failure_classes) if failure_classes is not None else DEFAULT_RETRYABLE
    # AUTH must never be retried, even if explicitly requested.
    retryable = frozenset(c for c in requested if c is not FailureClass.AUTH)

    # If the caller asked *only* for AUTH (or supplied an empty set), force a
    # single-attempt no-retry policy. This makes the AUTH guarantee explicit.
    effective_attempts = max_attempts if retryable else 1

    kwargs: dict[str, Any] = {
        "stop": stop_after_attempt(effective_attempts),
        "wait": _build_wait(retryable, multiplier=multiplier, max_wait=max_wait),
        "retry": _build_retry_predicate(retryable),
        "reraise": True,
    }

    return AsyncRetrying(**kwargs) if asynchronous else Retrying(**kwargs)


__all__ = [
    "FailureClass",
    "DEFAULT_RETRYABLE",
    "classify",
    "parse_retry_after",
    "build_retry",
]
