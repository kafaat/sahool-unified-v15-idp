"""
FastAPI Service with Request Logging Middleware
Example demonstrating how to integrate request logging into a FastAPI service.
"""

import os

# Import request logging middleware
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel

# Add shared to path (adjust based on your service location)
SHARED_PATH = Path(__file__).parent.parent.parent
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

from middleware.request_logging import (
    RequestLoggingMiddleware,
    get_correlation_id,
    get_request_context,
)
from middleware.tenant_context import (
    TenantContextMiddleware,
    get_current_tenant,
)

# ─────────────────────────────────────────────────────────────────────────────
# Application Setup
# ─────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    print("🚀 Starting service...")
    yield
    print("👋 Shutting down service...")


app = FastAPI(
    title="Example Service",
    description="Example service with request logging middleware",
    version="1.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────────────────────
# Middleware Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Add request logging middleware
# NOTE: Order matters! Add middlewares in reverse order of execution
# They will execute in the order: Tenant -> Logging -> Your handlers

app.add_middleware(
    RequestLoggingMiddleware,
    service_name=os.getenv("SERVICE_NAME", "example-service"),
    log_request_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
    log_response_body=False,
)

# Add tenant context middleware (optional, but recommended)
app.add_middleware(
    TenantContextMiddleware,
    require_tenant=False,  # Set to True if all endpoints require tenant
    exempt_paths=["/healthz", "/docs", "/openapi.json"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────


class CreateFieldRequest(BaseModel):
    name: str
    area_ha: float
    crop_type: str


class FieldResponse(BaseModel):
    id: str
    name: str
    area_ha: float
    crop_type: str
    tenant_id: str
    correlation_id: str


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/healthz")
def health_check():
    """Health check endpoint (excluded from logging)."""
    return {"status": "ok", "service": "example-service"}


# ─────────────────────────────────────────────────────────────────────────────
# Example Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/api/v1/fields")
async def list_fields(request: Request):
    """
    List all fields for the current tenant.

    This endpoint demonstrates:
    - Automatic request/response logging
    - Correlation ID extraction
    - Tenant context extraction
    """
    # Get correlation ID from request (set by middleware)
    correlation_id = get_correlation_id(request)

    # Get full request context (correlation_id, tenant_id, user_id)
    context = get_request_context(request)

    # Get tenant from context (if tenant middleware is enabled)
    try:
        tenant = get_current_tenant()
        tenant_id = tenant.id
    except RuntimeError:
        # Tenant middleware not configured or no tenant in request
        tenant_id = context.get("tenant_id", "unknown")

    # Simulate database query
    fields = [
        {
            "id": "field-1",
            "name": "North Field",
            "area_ha": 5.2,
            "crop_type": "wheat",
            "tenant_id": tenant_id,
        },
        {
            "id": "field-2",
            "name": "South Field",
            "area_ha": 3.8,
            "crop_type": "corn",
            "tenant_id": tenant_id,
        },
    ]

    # Add correlation ID to response for debugging
    return {
        "fields": fields,
        "total": len(fields),
        "correlation_id": correlation_id,
    }


@app.post("/api/v1/fields")
async def create_field(
    field: CreateFieldRequest,
    request: Request,
):
    """
    Create a new field.

    This endpoint demonstrates:
    - Request body logging (if enabled)
    - Correlation ID in response
    - Tenant isolation
    """
    correlation_id = get_correlation_id(request)
    context = get_request_context(request)

    try:
        tenant = get_current_tenant()
        tenant_id = tenant.id
    except RuntimeError:
        tenant_id = context.get("tenant_id", "unknown")

    # Simulate field creation
    new_field = {
        "id": "field-new",
        "name": field.name,
        "area_ha": field.area_ha,
        "crop_type": field.crop_type,
        "tenant_id": tenant_id,
    }

    # Return with correlation ID
    return FieldResponse(
        **new_field,
        correlation_id=correlation_id,
    )


@app.get("/api/v1/fields/{field_id}")
async def get_field(
    field_id: str,
    request: Request,
):
    """
    Get a specific field by ID.

    This endpoint demonstrates:
    - Path parameter handling
    - Error logging (when field not found)
    """
    correlation_id = get_correlation_id(request)
    context = get_request_context(request)

    try:
        tenant = get_current_tenant()
        tenant_id = tenant.id
    except RuntimeError:
        tenant_id = context.get("tenant_id", "unknown")

    # Simulate database lookup
    if field_id == "field-404":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"Field {field_id} not found",
        )

    return {
        "id": field_id,
        "name": "Example Field",
        "area_ha": 10.5,
        "crop_type": "rice",
        "tenant_id": tenant_id,
        "correlation_id": correlation_id,
    }


@app.get("/api/v1/external-call")
async def call_external_service(request: Request):
    """
    Example of calling another service with correlation ID propagation.

    This demonstrates:
    - Correlation ID propagation to downstream services
    - Service-to-service communication tracing
    """
    import httpx

    correlation_id = get_correlation_id(request)
    context = get_request_context(request)

    # Call another service, passing the correlation ID
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "http://weather-service:8080/api/v1/forecast",
                headers={
                    "X-Correlation-ID": correlation_id,
                    "X-Tenant-ID": context.get("tenant_id", ""),
                },
                timeout=5.0,
            )

            return {
                "correlation_id": correlation_id,
                "external_data": response.json(),
            }

        except httpx.RequestError as e:
            # Error will be automatically logged by middleware
            from fastapi import HTTPException

            raise HTTPException(
                status_code=503,
                detail=f"External service unavailable: {str(e)}",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Custom Logging in Endpoints
# ─────────────────────────────────────────────────────────────────────────────



# Configure structured logging
from observability.logging import get_logger

service_logger = get_logger("example-service")


@app.post("/api/v1/process")
async def process_data(request: Request):
    """
    Example endpoint with custom logging.

    This demonstrates:
    - Using the structured logger with request context
    - Adding custom fields to logs
    """
    context = get_request_context(request)

    # Log with context
    service_logger.info(
        "Starting data processing",
        correlation_id=context.get("correlation_id"),
        tenant_id=context.get("tenant_id"),
        operation="process_data",
    )

    try:
        # Simulate processing
        import time

        time.sleep(0.1)

        service_logger.info(
            "Data processing completed",
            correlation_id=context.get("correlation_id"),
            tenant_id=context.get("tenant_id"),
            operation="process_data",
            duration_ms=100,
        )

        return {"status": "success", "correlation_id": context.get("correlation_id")}

    except Exception as e:
        service_logger.error(
            f"Data processing failed: {str(e)}",
            correlation_id=context.get("correlation_id"),
            tenant_id=context.get("tenant_id"),
            operation="process_data",
            error_type=type(e).__name__,
        )
        raise


# ─────────────────────────────────────────────────────────────────────────────
# Run Application
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
