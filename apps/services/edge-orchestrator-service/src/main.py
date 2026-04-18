# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Edge Orchestrator Service - Main Application Entry Point.

This service manages edge computing devices (Jetson Orin Nano, etc.)
for agricultural AI inference at the edge, supporting offline-first
operations with real-time device monitoring and model deployment.

خدمة تنسيق الحافة - نقطة دخول التطبيق الرئيسية.
تدير هذه الخدمة أجهزة الحوسبة على الحافة (Jetson Orin Nano، إلخ)
للاستدلال بالذكاء الاصطناعي الزراعي على الحافة، مع دعم العمليات
دون اتصال مع مراقبة الأجهزة في الوقت الفعلي ونشر النماذج.
"""

import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import structlog
import uvicorn
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.endpoints import devices, jobs, sync
from src.api.schemas import HealthStatus, ReadinessStatus
from src.core.config import settings
from src.events.websocket import WebSocketManager, get_websocket_manager
from src.utils.device_manager import get_device_manager

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    TENANT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    TENANT_MIDDLEWARE_AVAILABLE = False

# Configure structured logging and tracing
from shared.logging_config import setup_logging
from shared.observability.tracing import setup_tracing

setup_logging("edge-orchestrator-service")
logger = structlog.get_logger(__name__)
_tracer = setup_tracing("edge-orchestrator-service")


# =============================================================================
# Application Lifespan | دورة حياة التطبيق
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown.

    مدير دورة حياة التطبيق للبدء والإيقاف.
    """
    logger.info(
        "service_starting",
        service=settings.service_name,
        version=settings.version,
        environment=settings.environment,
        port=settings.port,
    )

    # Initialize device manager
    device_manager = get_device_manager()
    await device_manager.start()
    app.state.device_manager = device_manager

    # Initialize WebSocket manager
    ws_manager = get_websocket_manager()
    await ws_manager.start()
    app.state.ws_manager = ws_manager

    # Initialize database connection (if configured)
    if settings.database_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=settings.db_pool_min_size,
                max_size=settings.db_pool_max_size,
                statement_cache_size=0,  # PgBouncer transaction mode
            )
            app.state.db_connected = True
            logger.info("database_connected")
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))
            app.state.db_connected = False
            app.state.db_pool = None
    else:
        app.state.db_connected = False
        app.state.db_pool = None

    # Initialize NATS connection (if configured)
    if settings.nats_url:
        try:
            import nats

            nc = await nats.connect(settings.nats_url)
            app.state.nc = nc
            app.state.nats_connected = True
            logger.info("nats_connected", url=settings.nats_url)

            # Subscribe to edge events
            await _setup_nats_subscriptions(nc, ws_manager)

        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.nats_connected = False
            app.state.nc = None
    else:
        app.state.nats_connected = False
        app.state.nc = None

    # Initialize Redis connection (if configured)
    if settings.redis_url:
        try:
            import redis.asyncio as redis

            app.state.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await app.state.redis.ping()
            app.state.redis_connected = True
            logger.info("redis_connected")
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            app.state.redis_connected = False
            app.state.redis = None
    else:
        app.state.redis_connected = False
        app.state.redis = None

    logger.info(
        "service_started",
        service=settings.service_name,
        service_ar=settings.service_name_ar,
    )

    yield

    # Shutdown
    logger.info("service_stopping")

    # Stop WebSocket manager
    await ws_manager.stop()

    # Stop device manager
    await device_manager.stop()

    # Close database pool
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("database_disconnected")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("nats_disconnected")

    # Close Redis connection
    if hasattr(app.state, "redis") and app.state.redis:
        await app.state.redis.close()
        logger.info("redis_disconnected")

    logger.info("service_stopped")


async def _setup_nats_subscriptions(nc, ws_manager: WebSocketManager) -> None:
    """Setup NATS subscriptions for edge events."""

    # Idempotency: track processed event IDs to prevent duplicate handling
    _processed_ids: dict[str, float] = {}
    _DEDUP_MAX = 10_000

    def _is_duplicate(event_id: str | None) -> bool:
        """Check if event was already processed (idempotency guard)."""
        if not event_id:
            return False
        import time

        now = time.monotonic()
        if event_id in _processed_ids:
            return True
        # Evict expired entries (older than 1 hour)
        if len(_processed_ids) >= _DEDUP_MAX:
            cutoff = now - 3600
            expired = [k for k, v in _processed_ids.items() if v < cutoff]
            for k in expired:
                del _processed_ids[k]
        _processed_ids[event_id] = now
        return False

    async def handle_device_metrics(msg):
        """Handle device metrics event from NATS."""
        try:
            data = json.loads(msg.data.decode())
            if _is_duplicate(data.get("event_id")):
                return
            # Validate tenant context from message payload
            tenant_id_str = data.get("tenant_id")
            if not tenant_id_str:
                logger.warning("nats_metrics_missing_tenant_id", subject=msg.subject)
                return
            device_id = UUID(data.get("device_id"))
            await ws_manager.broadcast_device_metrics(device_id, data.get("metrics", {}))
        except Exception as e:
            logger.error("nats_metrics_handler_error", error=str(e))

    async def handle_detection_result(msg):
        """Handle detection result event from NATS."""
        try:
            data = json.loads(msg.data.decode())
            if _is_duplicate(data.get("event_id")):
                return
            # Validate tenant context from message payload
            tenant_id_str = data.get("tenant_id")
            if not tenant_id_str:
                logger.warning("nats_detection_missing_tenant_id", subject=msg.subject)
                return
            device_id = UUID(data.get("device_id"))
            await ws_manager.broadcast_detection_result(device_id, data)
        except Exception as e:
            logger.error("nats_detection_handler_error", error=str(e))

    # Subscribe to edge events (tenant-scoped wildcard)
    await nc.subscribe("sahool.tenant.*.edge.metrics", cb=handle_device_metrics)
    await nc.subscribe("sahool.tenant.*.edge.detection", cb=handle_detection_result)
    logger.info("nats_subscriptions_setup")


# =============================================================================
# FastAPI Application | تطبيق FastAPI
# =============================================================================


app = FastAPI(
    title="Edge Orchestrator Service | خدمة تنسيق الحافة",
    description="""
    Manages edge computing devices for agricultural AI inference.

    تدير أجهزة الحوسبة على الحافة للاستدلال بالذكاء الاصطناعي الزراعي.

    ## Features | الميزات

    - **Device Management**: Register, monitor, and manage edge devices
    - **Job Orchestration**: Queue and execute AI inference jobs
    - **Model Deployment**: Deploy AI models to edge devices
    - **Data Synchronization**: Sync data between edge and cloud
    - **Real-time Updates**: WebSocket support for live monitoring

    - **إدارة الأجهزة**: تسجيل ومراقبة وإدارة أجهزة الحافة
    - **تنسيق المهام**: إدراج وتنفيذ مهام استدلال الذكاء الاصطناعي
    - **نشر النماذج**: نشر نماذج الذكاء الاصطناعي على أجهزة الحافة
    - **مزامنة البيانات**: مزامنة البيانات بين الحافة والسحابة
    - **التحديثات الفورية**: دعم WebSocket للمراقبة المباشرة

    ## Supported Devices | الأجهزة المدعومة

    - NVIDIA Jetson Orin Nano (8GB)
    - NVIDIA Jetson Orin NX (16GB)
    - NVIDIA Jetson AGX Orin (64GB)
    - Raspberry Pi 5 with AI HAT
    """,
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)
_tracer.instrument_fastapi(app)

# Setup unified error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

# CORS middleware
# Security: Never use allow_origins=["*"] with allow_credentials=True
# الأمان: لا تستخدم أبداً allow_origins=["*"] مع allow_credentials=True
_cors_origins = (
    ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    if settings.is_development
    else [
        "https://app.sahool.app",
        "https://admin.sahool.app",
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Tenant-ID"],
)

if TENANT_MIDDLEWARE_AVAILABLE:
    app.add_middleware(TenantContextMiddleware)


# =============================================================================
# Health Endpoints | نقاط نهاية الصحة
# =============================================================================


@app.get(
    "/healthz",
    response_model=HealthStatus,
    tags=["health"],
    summary="Liveness probe | فحص الحياة",
)
@app.get(
    "/health/live",
    response_model=HealthStatus,
    tags=["health"],
    include_in_schema=False,
)
async def health_check() -> HealthStatus:
    """
    Liveness probe for Kubernetes.

    فحص الحياة لـ Kubernetes.
    """
    return HealthStatus(
        status="ok",
        service=settings.service_name,
        version=settings.version,
    )


@app.get(
    "/readyz",
    response_model=ReadinessStatus,
    tags=["health"],
    summary="Readiness probe | فحص الجاهزية",
)
@app.get(
    "/health/ready",
    response_model=ReadinessStatus,
    tags=["health"],
    include_in_schema=False,
)
async def readiness_check() -> ReadinessStatus:
    """
    Readiness probe for Kubernetes.

    فحص الجاهزية لـ Kubernetes.
    """
    device_manager = get_device_manager()
    ws_manager = get_websocket_manager()

    return ReadinessStatus(
        status="ok",
        database=getattr(app.state, "db_connected", False),
        nats=getattr(app.state, "nats_connected", False),
        redis=getattr(app.state, "redis_connected", False),
        active_devices=len(device_manager.connected_devices),
        active_jobs=ws_manager.connection_count,
    )


@app.get(
    "/health",
    tags=["health"],
    summary="Combined health status | حالة الصحة المجمعة",
)
async def combined_health() -> dict[str, Any]:
    """
    Combined health check with detailed status.

    فحص صحة مجمع مع حالة مفصلة.
    """
    device_manager = get_device_manager()
    ws_manager = get_websocket_manager()

    return {
        "status": "ok",
        "service": settings.service_name,
        "service_ar": settings.service_name_ar,
        "version": settings.version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "connections": {
            "database": getattr(app.state, "db_connected", False),
            "nats": getattr(app.state, "nats_connected", False),
            "redis": getattr(app.state, "redis_connected", False),
        },
        "devices": {
            "total": device_manager.total_devices,
            "connected": len(device_manager.connected_devices),
        },
        "websockets": {
            "active_connections": ws_manager.connection_count,
        },
    }


# =============================================================================
# Include API Routers | تضمين موجهات API
# =============================================================================

app.include_router(devices.router)
app.include_router(jobs.router)
app.include_router(sync.router)


# =============================================================================
# WebSocket Endpoint | نقطة نهاية WebSocket
# =============================================================================


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: UUID | None = Query(default=None),
    tenant_id: UUID | None = Query(default=None),
):
    """
    WebSocket endpoint for real-time device updates.

    نقطة نهاية WebSocket للتحديثات الفورية للأجهزة.

    Query Parameters:
    - device_id: Subscribe to updates for a specific device
    - tenant_id: Required for authentication

    Connect and subscribe to events:
    ```json
    {
        "type": "subscribe",
        "event_types": ["metrics", "detection", "job_status", "alert"]
    }
    ```
    """
    ws_manager = get_websocket_manager()
    client_id = str(uuid4())

    try:
        conn = await ws_manager.connect(
            websocket=websocket,
            client_id=client_id,
            tenant_id=tenant_id,
            device_id=device_id,
        )

        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                await ws_manager.handle_client_message(client_id, data)
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await conn.send_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                        "message_ar": "JSON غير صالح",
                    }
                )

    except Exception as e:
        logger.error("websocket_error", client_id=client_id, error=str(e))
    finally:
        await ws_manager.disconnect(client_id)


@app.websocket("/ws/device/{device_id}")
async def device_websocket_endpoint(
    websocket: WebSocket,
    device_id: UUID,
):
    """
    WebSocket endpoint for edge device connections.

    نقطة نهاية WebSocket لاتصالات أجهزة الحافة.

    This endpoint is used by edge devices (Jetson, etc.) to:
    - Send heartbeats
    - Report metrics
    - Send detection results
    - Receive commands
    """
    ws_manager = get_websocket_manager()
    device_manager = get_device_manager()
    client_id = f"device-{device_id}"

    try:
        conn = await ws_manager.connect(
            websocket=websocket,
            client_id=client_id,
            device_id=device_id,
        )

        logger.info("device_ws_connected", device_id=str(device_id))

        # Handle incoming messages from device
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "heartbeat":
                    # Update device last seen
                    device = await device_manager.get_device(device_id)
                    if device:
                        device.last_seen = datetime.utcnow()

                elif message_type == "metrics":
                    # Broadcast metrics to subscribers
                    from src.api.schemas import DeviceMetrics

                    metrics = DeviceMetrics(**data.get("payload", {}))
                    await device_manager.update_device_metrics(device_id, metrics)
                    await ws_manager.broadcast_device_metrics(device_id, metrics)

                elif message_type == "detection":
                    # Broadcast detection result
                    from src.api.schemas import InferenceResult

                    result = InferenceResult(**data.get("payload", {}))
                    await ws_manager.broadcast_detection_result(device_id, result)

                    # Publish to NATS if connected (tenant-scoped topic)
                    if hasattr(app.state, "nc") and app.state.nc:
                        # Extract tenant_id from device registration
                        device = await device_manager.get_device(device_id)
                        tenant_id = device.tenant_id if device else None
                        if tenant_id:
                            nats_payload = data.get("payload", {})
                            nats_payload["tenant_id"] = str(tenant_id)
                            await app.state.nc.publish(
                                f"sahool.tenant.{tenant_id}.edge.detection",
                                json.dumps(nats_payload).encode(),
                            )
                        else:
                            logger.warning(
                                "nats_publish_skipped_no_tenant",
                                device_id=str(device_id),
                            )

                elif message_type == "job_status":
                    # Broadcast job status update
                    payload = data.get("payload", {})
                    await ws_manager.broadcast_job_status(
                        device_id=device_id,
                        job_id=UUID(payload.get("job_id")),
                        status=payload.get("status"),
                        progress=payload.get("progress_percent", 0),
                        result=payload.get("result"),
                    )

                elif message_type == "alert":
                    # Broadcast alert with tenant context from device registration
                    payload = data.get("payload", {})
                    device = await device_manager.get_device(device_id)
                    alert_tenant_id = device.tenant_id if device else None
                    await ws_manager.broadcast_alert(
                        device_id=device_id,
                        tenant_id=alert_tenant_id,
                        alert_type=payload.get("alert_type", "device_alert"),
                        message_en=payload.get("message", ""),
                        message_ar=payload.get("message_ar", ""),
                        severity=payload.get("severity", "warning"),
                        data=payload.get("data"),
                    )

                elif message_type == "ping":
                    await conn.send_message(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await conn.send_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                    }
                )
            except Exception as e:
                logger.error(
                    "device_ws_message_error",
                    device_id=str(device_id),
                    error=str(e),
                )

    except Exception as e:
        logger.error("device_websocket_error", device_id=str(device_id), error=str(e))
    finally:
        await ws_manager.disconnect(client_id)
        logger.info("device_ws_disconnected", device_id=str(device_id))


# =============================================================================
# Error Handlers | معالجات الأخطاء
# =============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=str(request.url.path),
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_ar": "خطأ داخلي في الخادم",
            "detail": str(exc) if settings.is_development else None,
        },
    )


# =============================================================================
# Run Application | تشغيل التطبيق
# =============================================================================


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=settings.is_development,
    )
