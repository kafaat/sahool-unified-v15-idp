"""
Health Check Endpoints
نقاط نهاية فحص الصحة

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime, timezone

from fastapi import APIRouter, Response

from ...core.config import get_settings
from ...models.schemas import CopilotMode, HealthResponse
from ...rag import get_rag_service

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
        version="16.0.0",
        mode=CopilotMode(settings.copilot_mode),
        timestamp=datetime.now(UTC),
    )


@router.get("/readyz", response_model=HealthResponse)
@router.get("/health/ready", response_model=HealthResponse)
async def readiness():
    """
    Readiness probe - checks all dependencies.
    فحص الجاهزية - يفحص جميع التبعيات
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

    # Check Redis (if configured)
    if settings.redis_url:
        try:
            import redis.asyncio as redis

            client = redis.from_url(settings.redis_url)
            await client.ping()
            components["redis"] = True
            await client.close()
        except Exception:
            components["redis"] = False

    # Check NATS
    try:
        import nats

        nc = await nats.connect(settings.nats_url, connect_timeout=2)
        await nc.close()
        components["nats"] = True
    except Exception:
        components["nats"] = False

    # Determine overall status
    all_healthy = all(components.values()) if components else True
    status = "ok" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        service="copilot-api",
        version="16.0.0",
        mode=CopilotMode(settings.copilot_mode),
        components=components,
        timestamp=datetime.now(UTC),
    )


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Combined health check.
    فحص صحة مجمع
    """
    return await readiness()


@router.get("/metrics")
async def metrics():
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
