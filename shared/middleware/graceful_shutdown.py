"""
SAHOOL Graceful Shutdown Middleware
=====================================
وسيط الإيقاف اللطيف مع تصريف الطلبات

Middleware that enables graceful shutdown by:
1. Tracking in-flight requests
2. Refusing new requests during shutdown (503)
3. Waiting for active requests to complete (with timeout)

This prevents dropped requests during deployments and restarts.

Usage:
    from shared.middleware.graceful_shutdown import (
        GracefulShutdownMiddleware,
        create_graceful_lifespan,
    )

    # Option 1: Wrap existing lifespan
    app = FastAPI(lifespan=create_graceful_lifespan(your_lifespan))

    # Option 2: Manual setup
    shutdown_handler = GracefulShutdownMiddleware(app, drain_timeout=30)

    @asynccontextmanager
    async def lifespan(app):
        yield
        await shutdown_handler.drain()
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class GracefulShutdownMiddleware:
    """
    Middleware for graceful shutdown with request draining.

    Tracks the number of in-flight requests and provides a drain()
    method that waits for all active requests to complete before
    allowing the process to exit.

    During drain:
    - New requests get 503 Service Unavailable
    - Active requests continue until completion or timeout
    - Health checks (/healthz, /readyz) return degraded status

    Args:
        app: FastAPI application
        drain_timeout: Maximum seconds to wait for requests to finish
        exclude_paths: Paths exempt from shutdown rejection
    """

    def __init__(
        self,
        app: FastAPI,
        drain_timeout: float = 30.0,
        exclude_paths: set[str] | None = None,
    ):
        self._app = app
        self._drain_timeout = drain_timeout
        self._exclude_paths = exclude_paths or {"/healthz", "/readyz", "/metrics"}
        self._in_flight = 0
        self._lock = asyncio.Lock()
        self._draining = False
        self._drain_event = asyncio.Event()
        self._drain_event.set()  # Not draining initially

        app.middleware("http")(self._middleware)

    @property
    def in_flight_count(self) -> int:
        return self._in_flight

    @property
    def is_draining(self) -> bool:
        return self._draining

    async def _middleware(self, request: Request, call_next: Callable) -> Response:
        """Track in-flight requests and reject during drain."""
        path = request.url.path

        # During drain, reject new requests (except health checks)
        if self._draining and path not in self._exclude_paths:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service shutting down",
                    "error_ar": "الخدمة قيد الإيقاف",
                    "message": "Please retry with another instance",
                    "message_ar": "يرجى إعادة المحاولة مع نسخة أخرى",
                },
                headers={"Retry-After": "5", "Connection": "close"},
            )

        # Health check during drain returns degraded status
        if self._draining and path in ("/healthz", "/readyz"):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "draining",
                    "in_flight": self._in_flight,
                    "message": "Service is shutting down gracefully",
                },
            )

        # Track request
        async with self._lock:
            self._in_flight += 1

        try:
            return await call_next(request)
        finally:
            async with self._lock:
                self._in_flight -= 1
                if self._draining and self._in_flight <= 0:
                    self._drain_event.set()

    async def drain(self) -> None:
        """
        Begin draining — wait for in-flight requests to complete.

        Call this in your lifespan shutdown handler. This method:
        1. Sets draining flag (new requests get 503)
        2. Waits up to drain_timeout for active requests
        3. Returns (even if requests remain after timeout)
        """
        logger.info(
            "graceful_shutdown_draining",
            extra={"in_flight": self._in_flight, "timeout": self._drain_timeout},
        )

        self._draining = True

        if self._in_flight <= 0:
            logger.info("graceful_shutdown_no_requests")
            return

        self._drain_event.clear()

        try:
            await asyncio.wait_for(
                self._drain_event.wait(),
                timeout=self._drain_timeout,
            )
            logger.info("graceful_shutdown_drained")
        except TimeoutError:
            logger.warning(
                "graceful_shutdown_timeout",
                extra={
                    "remaining_requests": self._in_flight,
                    "timeout": self._drain_timeout,
                },
            )


def create_graceful_lifespan(
    inner_lifespan: Callable | None = None,
    drain_timeout: float = 30.0,
) -> Callable:
    """
    Create a lifespan context manager with graceful shutdown.

    Wraps an optional inner lifespan and adds request draining
    on shutdown.

    Args:
        inner_lifespan: Optional existing lifespan to wrap
        drain_timeout: Max seconds to wait for requests

    Returns:
        Lifespan function for FastAPI

    Usage:
        app = FastAPI(lifespan=create_graceful_lifespan(my_lifespan, drain_timeout=30))
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        shutdown_handler = GracefulShutdownMiddleware(app, drain_timeout=drain_timeout)
        app.state.shutdown_handler = shutdown_handler

        if inner_lifespan:
            async with inner_lifespan(app):
                yield
        else:
            yield

        # Drain on shutdown
        await shutdown_handler.drain()

    return lifespan
