"""
SAHOOL Service Setup Module
===========================
Provides unified service setup for SAHOOL Python services.

Features:
- Middleware setup (error handling, logging, rate limiting)
- Health check endpoints
- CORS configuration
- Security headers
- Service metadata

Usage:
    from shared.service_enhancements.setup import setup_service, ServiceConfig

    config = ServiceConfig(
        name="advisory-service",
        version="16.0.0",
        enable_rate_limiting=True,
        enable_caching=True,
    )

    app = FastAPI(...)
    setup_service(app, config)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Callable

from fastapi import FastAPI, Request, Response

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for service setup."""

    # Service metadata
    name: str
    version: str = "16.0.0"
    description: str = ""

    # Features
    enable_rate_limiting: bool = True
    enable_request_logging: bool = True
    enable_security_headers: bool = True
    enable_cors: bool = True
    enable_caching: bool = True

    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000

    # CORS
    cors_origins: list[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","))
    cors_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    )
    cors_headers: list[str] = field(default_factory=lambda: ["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"])

    # Health check
    health_path: str = "/healthz"
    ready_path: str = "/readyz"

    # Excluded paths for middleware
    excluded_paths: list[str] = field(
        default_factory=lambda: [
            "/healthz",
            "/readyz",
            "/livez",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
    )


def setup_service(app: FastAPI, config: ServiceConfig) -> FastAPI:
    """
    Setup a FastAPI service with SAHOOL standard middleware and configuration.

    Args:
        app: FastAPI application instance
        config: Service configuration

    Returns:
        Configured FastAPI application

    Usage:
        from fastapi import FastAPI
        from shared.service_enhancements.setup import setup_service, ServiceConfig

        app = FastAPI(title="My Service", version="16.0.0")
        config = ServiceConfig(name="my-service")
        setup_service(app, config)
    """

    # 1. Setup exception handlers
    _setup_exception_handlers(app)

    # 2. Setup request ID middleware
    _setup_request_id_middleware(app)

    # 3. Setup request logging
    if config.enable_request_logging:
        _setup_request_logging(app, config)

    # 4. Setup rate limiting
    if config.enable_rate_limiting:
        _setup_rate_limiting(app, config)

    # 5. Setup CORS
    if config.enable_cors:
        _setup_cors(app, config)

    # 6. Setup security headers
    if config.enable_security_headers:
        _setup_security_headers(app)

    # 7. Setup health endpoints
    _setup_health_endpoints(app, config)

    logger.info(
        f"Service {config.name} v{config.version} configured",
        extra={
            "service": config.name,
            "version": config.version,
            "features": {
                "rate_limiting": config.enable_rate_limiting,
                "request_logging": config.enable_request_logging,
                "security_headers": config.enable_security_headers,
                "cors": config.enable_cors,
                "caching": config.enable_caching,
            },
        },
    )

    return app


def _setup_exception_handlers(app: FastAPI) -> None:
    """Setup unified exception handlers."""
    try:
        from shared.errors_py import setup_exception_handlers

        setup_exception_handlers(app)
        logger.debug("Exception handlers configured from shared.errors_py")
    except ImportError:
        try:
            from apps.services.shared.middleware.exception_handler import setup_exception_handlers

            setup_exception_handlers(app)
            logger.debug("Exception handlers configured from apps.services.shared")
        except ImportError:
            logger.warning("Exception handlers not available, using defaults")
            _setup_default_exception_handlers(app)


def _setup_default_exception_handlers(app: FastAPI) -> None:
    """Setup basic exception handlers when shared module not available."""
    import uuid

    from fastapi import HTTPException, status
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": str(exc.detail),
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"Unhandled exception [{error_id}]: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "error_id": error_id,
                },
            },
        )


def _setup_request_id_middleware(app: FastAPI) -> None:
    """Setup request ID middleware for tracing."""
    import uuid

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


def _setup_request_logging(app: FastAPI, config: ServiceConfig) -> None:
    """Setup request logging middleware."""
    try:
        from shared.middleware.request_logging import RequestLoggingMiddleware

        app.add_middleware(
            RequestLoggingMiddleware,
            service_name=config.name,
            exclude_paths=config.excluded_paths,
        )
        logger.debug("Request logging middleware configured")
    except ImportError:
        logger.warning("Request logging middleware not available")


def _setup_rate_limiting(app: FastAPI, config: ServiceConfig) -> None:
    """Setup rate limiting middleware."""
    try:
        from shared.middleware.rate_limit import rate_limit_middleware

        @app.middleware("http")
        async def rate_limit(request: Request, call_next: Callable) -> Response:
            return await rate_limit_middleware(request, call_next)

        logger.debug("Rate limiting middleware configured")
    except ImportError:
        logger.warning("Rate limiting middleware not available")


def _setup_cors(app: FastAPI, config: ServiceConfig) -> None:
    """Setup CORS middleware."""
    try:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=config.cors_methods,
            allow_headers=config.cors_headers,
        )
        logger.debug("CORS middleware configured")
    except Exception as e:
        logger.warning(f"CORS middleware setup failed: {e}")


def _setup_security_headers(app: FastAPI) -> None:
    """Setup security headers middleware."""
    try:
        from shared.middleware.security_headers import setup_security_headers

        setup_security_headers(app)
        logger.debug("Security headers middleware configured")
    except ImportError:
        logger.warning("Security headers middleware not available")


def _setup_health_endpoints(app: FastAPI, config: ServiceConfig) -> None:
    """Setup standard health check endpoints."""
    from datetime import UTC, datetime

    @app.get(config.health_path, tags=["Health"])
    def health():
        """Liveness probe endpoint."""
        return {
            "status": "ok",
            "service": config.name,
            "version": config.version,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
        }

    @app.get(config.ready_path, tags=["Health"])
    async def ready():
        """Readiness probe endpoint."""
        checks = {}

        # Check database if available
        if hasattr(app.state, "db_pool") and app.state.db_pool:
            try:
                async with app.state.db_pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                checks["database"] = "connected"
            except Exception:
                checks["database"] = "disconnected"

        # Check NATS if available
        if hasattr(app.state, "nc") and app.state.nc:
            checks["nats"] = "connected" if app.state.nc.is_connected else "disconnected"
        elif hasattr(app.state, "nats_connected"):
            checks["nats"] = "connected" if app.state.nats_connected else "disconnected"

        # Check Redis if available
        if hasattr(app.state, "redis") and app.state.redis:
            try:
                await app.state.redis.ping()
                checks["redis"] = "connected"
            except Exception:
                checks["redis"] = "disconnected"

        is_ready = all(v == "connected" for v in checks.values()) if checks else True

        return {
            "status": "ready" if is_ready else "not_ready",
            "service": config.name,
            "version": config.version,
            "checks": checks,
            "timestamp": datetime.now(UTC).isoformat() + "Z",
        }

    logger.debug(f"Health endpoints configured: {config.health_path}, {config.ready_path}")
