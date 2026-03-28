"""
SAHOOL AI Agents Core Service
خدمة نواة وكلاء الذكاء الاصطناعي

FastAPI service exposing the hierarchical multi-agent system.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any

try:
    import structlog
except ImportError:
    structlog = None  # type: ignore[assignment]

from agents import (
    AgentContext,
    AgentPercept,
    DroneAgent,
    FeedbackLearnerAgent,
    IoTAgent,
    MasterCoordinatorAgent,
    MobileAgent,
)
from fastapi import Depends, FastAPI, HTTPException

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware import setup_cors
from shared.middleware.tenant_context import TenantContextMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
if structlog is not None:
    logger = structlog.get_logger(__name__)
else:
    logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SAHOOL AI Agents Core",
    description="Hierarchical Multi-Agent System for Smart Agriculture",
    version="16.0.0",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Setup CORS
setup_cors(app)

app.add_middleware(TenantContextMiddleware)

# Rate Limiting - Critical for AI agent endpoints
try:
    from fastapi import Request

    from shared.middleware.rate_limiter import RateLimitTier, setup_rate_limiting

    def ai_agents_tier_func(request: Request) -> RateLimitTier:
        """Determine rate limit tier for AI agents endpoints"""
        # Check for internal service header
        if request.headers.get("X-Internal-Service"):
            return RateLimitTier.INTERNAL

        # AI analysis endpoints are resource-intensive, use stricter limits
        if request.url.path.startswith("/api/v1/analyze"):
            return RateLimitTier.STANDARD

        # Edge endpoints can have higher limits
        if request.url.path.startswith("/api/v1/edge"):
            return RateLimitTier.PREMIUM

        return RateLimitTier.STANDARD

    rate_limiter = setup_rate_limiting(
        app,
        use_redis=os.getenv("REDIS_URL") is not None,
        tier_func=ai_agents_tier_func,
        exclude_paths=["/healthz", "/api/v1/system/status"],
    )
    logger.info("Rate limiting enabled for ai-agents-core")
except ImportError:
    logger.warning("Rate limiter not available - proceeding without rate limiting")

# Initialize agents
coordinator = MasterCoordinatorAgent()
mobile_agent = MobileAgent()
iot_agent = IoTAgent()
drone_agent = DroneAgent()
feedback_learner = FeedbackLearnerAgent()


# Request/Response Models
class AnalysisRequest(BaseModel):
    field_id: str = Field(..., max_length=100)
    crop_type: str = Field(..., max_length=50)
    sensor_data: dict[str, Any] | None = None
    weather_data: dict[str, Any] | None = None
    image_data: dict[str, Any] | None = None


class FeedbackRequest(BaseModel):
    recommendation_id: str
    agent_id: str
    action_type: str
    rating: float = Field(..., ge=-1, le=1)
    success: bool
    actual_result: dict[str, Any] | None = None
    comments: str | None = Field(None, max_length=2000)


class SensorDataRequest(BaseModel):
    device_id: str
    sensor_type: str
    value: float
    timestamp: str | None = None


# Health check
@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-agents-core",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    return {
        "status": "ready",
        "service": "ai-agents-core",
        "version": "16.0.0",
        "checks": {
            "service": "ready",
        },
    }


# Full analysis endpoint
@app.post("/api/v1/analyze")
async def analyze_field(request: AnalysisRequest, user: User = Depends(get_current_user)):
    """تحليل شامل للحقل باستخدام جميع الوكلاء"""
    try:
        # Create context
        context = AgentContext(
            field_id=request.field_id,
            crop_type=request.crop_type,
            sensor_data=request.sensor_data or {},
            weather_data=request.weather_data or {},
            metadata={"image_data": request.image_data},
        )

        # Run coordinated analysis
        result = await coordinator.run_full_analysis(context)

        return {
            "success": True,
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Edge agent endpoints
@app.post("/api/v1/edge/sensor")
async def process_sensor_data(request: SensorDataRequest, user: User = Depends(get_current_user)):
    """معالجة بيانات المستشعر عبر IoT Agent"""
    try:
        percept = AgentPercept(
            percept_type="single_sensor",
            data={"type": request.sensor_type, "value": request.value},
            source=request.device_id,
        )

        result = await iot_agent.run(percept)

        return {
            "success": True,
            "result": result,
            "response_time_ms": result.get("response_time_ms", 0),
        }

    except Exception as e:
        logger.error(f"Sensor processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/v1/edge/mobile")
async def mobile_quick_action(data: dict[str, Any], user: User = Depends(get_current_user)):
    """إجراء سريع من الموبايل"""
    try:
        percept = AgentPercept(
            percept_type=data.get("type", "sensor_reading"),
            data=data.get("data", {}),
            source="mobile_app",
        )

        result = await mobile_agent.run(percept)

        return {
            "success": True,
            "result": result,
            "response_time_ms": result.get("response_time_ms", 0),
        }

    except Exception as e:
        logger.error(f"Mobile action error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Learning endpoints
@app.post("/api/v1/feedback")
async def submit_feedback(request: FeedbackRequest, user: User = Depends(get_current_user)):
    """تقديم تغذية راجعة للتعلم"""
    try:
        percept = AgentPercept(
            percept_type="user_feedback",
            data={
                "recommendation_id": request.recommendation_id,
                "agent_id": request.agent_id,
                "action_type": request.action_type,
                "rating": request.rating,
                "success": request.success,
                "actual_result": request.actual_result or {},
                "comments": request.comments,
            },
            source="user",
        )

        result = await feedback_learner.run(percept)

        return {
            "success": True,
            "learning_result": result,
            "message": "تم استلام التغذية الراجعة",
        }

    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# System status
@app.get("/api/v1/system/status")
async def get_system_status(user: User = Depends(get_current_user)):
    """حالة النظام"""
    return {
        "coordinator": coordinator.get_system_status(),
        "edge_agents": {
            "mobile": mobile_agent.get_metrics(),
            "iot": iot_agent.get_metrics(),
            "drone": drone_agent.get_metrics(),
        },
        "learning": feedback_learner.get_learning_stats(),
        "timestamp": datetime.now().isoformat(),
    }


# Agent metrics
@app.get("/api/v1/agents/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str, user: User = Depends(get_current_user)):
    """مقاييس وكيل محدد"""
    agents = {
        "coordinator": coordinator,
        "mobile": mobile_agent,
        "iot": iot_agent,
        "drone": drone_agent,
        "feedback": feedback_learner,
    }

    agent = agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.get_metrics()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8161"))
    uvicorn.run(app, host="0.0.0.0", port=port)
