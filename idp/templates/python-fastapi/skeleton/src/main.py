"""
{{name}} - SAHOOL Platform Service

Auto-generated FastAPI service with:
- Health/readiness endpoints
- Prometheus metrics
- Audit logging middleware
- Structured logging
"""

import os
from contextlib import asynccontextmanager
from typing import Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

SERVICE_NAME = os.getenv("SERVICE_NAME", "{{name}}")
SERVICE_LAYER = os.getenv("SERVICE_LAYER", "{{layer}}")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")

log = structlog.get_logger()

# Prometheus metrics
REQS = Counter("http_requests_total", "Total HTTP requests", ["service", "path", "method", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["service", "path", "method"])


# ─────────────────────────────────────────────────────────────────────────────
# Audit Middleware
# ─────────────────────────────────────────────────────────────────────────────


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic request audit logging.

    Logs all requests with:
    - Request method and path
    - User ID (from JWT if authenticated)
    - IP address
    - Response status
    - Request duration

    Configure via environment variables:
    - AUDIT_ENABLED: Enable/disable audit logging (default: true)
    - AUDIT_EXCLUDE_PATHS: Comma-separated paths to exclude (default: /healthz,/readyz,/metrics)
    """

    def __init__(self, app, audit_enabled: bool = True, exclude_paths: list[str] | None = None):
        super().__init__(app)
        self.audit_enabled = audit_enabled
        self.exclude_paths = exclude_paths or ["/healthz", "/readyz", "/metrics", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import time

        # Skip audit for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        start_time = time.time()

        # Extract audit context
        audit_context = {
            "service": SERVICE_NAME,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else None,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "correlation_id": request.headers.get("x-correlation-id"),
            "user_id": self._extract_user_id(request),
        }

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log successful request
            if self.audit_enabled:
                log.info(
                    "audit.request",
                    **audit_context,
                    status_code=response.status_code,
                    duration_ms=round(duration * 1000, 2),
                )

            # Update metrics
            REQS.labels(SERVICE_NAME, request.url.path, request.method, response.status_code).inc()
            LATENCY.labels(SERVICE_NAME, request.url.path, request.method).observe(duration)

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Log failed request
            if self.audit_enabled:
                log.error(
                    "audit.request.error",
                    **audit_context,
                    error=str(e),
                    duration_ms=round(duration * 1000, 2),
                )

            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, handling proxy headers."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _extract_user_id(self, request: Request) -> str | None:
        """Extract user ID from JWT token if present."""
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        try:
            import base64
            import json

            token = auth_header[7:]  # Remove "Bearer "
            # Decode JWT payload (middle part) without verification
            # This is just for logging - actual verification happens in auth middleware
            payload_b64 = token.split(".")[1]
            # Add padding if needed
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            return payload.get("sub")
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────────────────────
# Application Lifecycle
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    log.info(
        "service.startup",
        service=SERVICE_NAME,
        layer=SERVICE_LAYER,
        version=SERVICE_VERSION,
    )

    # TODO: Initialize database connection
    # TODO: Initialize NATS connection

    yield

    # Shutdown
    log.info("service.shutdown", service=SERVICE_NAME)

    # TODO: Close database connection
    # TODO: Close NATS connection


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

# Add audit middleware
audit_enabled = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
audit_exclude = os.getenv("AUDIT_EXCLUDE_PATHS", "/healthz,/readyz,/metrics,/docs,/openapi.json").split(",")
app.add_middleware(AuditMiddleware, audit_enabled=audit_enabled, exclude_paths=audit_exclude)


# ─────────────────────────────────────────────────────────────────────────────
# Health & Metrics Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz")
def healthz():
    """Liveness probe - service is running."""
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz():
    """Readiness probe - service is ready to accept traffic."""
    # TODO: Add actual readiness checks (database, NATS, etc.)
    return {
        "status": "ready",
        "service": SERVICE_NAME,
        "checks": {
            "database": True,  # TODO: Implement actual check
            "nats": True,  # TODO: Implement actual check
        },
    }


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ─────────────────────────────────────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/")
def root():
    """Root endpoint - service information."""
    return {
        "service": SERVICE_NAME,
        "layer": SERVICE_LAYER,
        "version": SERVICE_VERSION,
    }


# TODO: Add your API routes here
# Example:
# @app.get("/api/v1/resource")
# def get_resource():
#     return {"data": "..."}
