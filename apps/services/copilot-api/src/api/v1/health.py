"""
Health Check Endpoints
نقاط نهاية فحص الصحة

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, Response

from ...core.config import SERVICE_VERSION, get_settings
from ...models.schemas import CopilotMode, HealthResponse
from ...rag import get_rag_service
from ..deps import get_current_user

router = APIRouter(tags=["Health"])


@router.get("/healthz", response_model=HealthResponse)
@router.get("/health/live", response_model=HealthResponse)
async def liveness():
    """
    Liveness probe - basic health check.
    فحص الحياة - فحص صحة أساسي
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="copilot-api",
        version=SERVICE_VERSION,
        mode=CopilotMode(settings.copilot_mode),
        timestamp=datetime.now(UTC),
    )


@router.get("/readyz", response_model=HealthResponse)
@router.get("/health/ready", response_model=HealthResponse)
async def readiness(request: Request):
    """
    Readiness probe - checks all dependencies using app-level connections.
    فحص الجاهزية - يفحص جميع التبعيات باستخدام اتصالات مستوى التطبيق
    """
    settings = get_settings()
    components = {}

    # Check RAG service
    try:
        rag_service = get_rag_service()
        stats = await rag_service.get_stats()
        components["rag"] = True
        components["qdrant"] = stats.get("qdrant_available", False)
    except Exception:
        components["rag"] = False
        components["qdrant"] = False

    # Check NATS using app-level connection (only when explicitly configured)
    # فحص NATS باستخدام اتصال مستوى التطبيق (فقط عندما يكون مكوناً صراحة)
    nc = getattr(request.app.state, "nc", None)
    if nc is not None:
        # NATS was configured and initialized — include in readiness
        components["nats"] = nc.is_connected
    # else: NATS not configured — omit from readiness (non-blocking)

    # Check chat DB readiness (only when database_url is configured)
    if settings.database_url:
        components["chat_db"] = getattr(request.app.state, "chat_db_ready", False)

    # Determine overall status
    all_healthy = all(components.values()) if components else True
    status = "ok" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        service="copilot-api",
        version=SERVICE_VERSION,
        mode=CopilotMode(settings.copilot_mode),
        components=components,
        timestamp=datetime.now(UTC),
    )


@router.get("/health", response_model=HealthResponse)
async def health(request: Request):
    """
    Combined health check.
    فحص صحة مجمع
    """
    return await readiness(request)


@router.get("/metrics")
async def metrics(user: dict = Depends(get_current_user)):
    """
    Prometheus metrics endpoint.
    نقطة نهاية مقاييس Prometheus
    """
    from ...security import get_guard

    guard = get_guard()
    stats = guard.get_stats()

    metrics_text = f"""# HELP copilot_guard_checks_total Total guard checks
# TYPE copilot_guard_checks_total counter
copilot_guard_checks_total {stats["total_checks"]}

# HELP copilot_guard_allowed_total Total allowed calls
# TYPE copilot_guard_allowed_total counter
copilot_guard_allowed_total {stats["allowed"]}

# HELP copilot_guard_blocked_total Total blocked calls
# TYPE copilot_guard_blocked_total counter
copilot_guard_blocked_total {stats["blocked"]}
"""

    return Response(content=metrics_text, media_type="text/plain")
