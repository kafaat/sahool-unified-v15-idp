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

from agents import (
    AgentContext,
    AgentPercept,
    DroneAgent,
    FeedbackLearnerAgent,
    IoTAgent,
    MasterCoordinatorAgent,
    MobileAgent,
)
from fastapi import FastAPI, HTTPException

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="SAHOOL AI Agents Core",
    description="Hierarchical Multi-Agent System for Smart Agriculture",
    version="1.0.0",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Configure allowed origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8080,https://sahool.com,https://app.sahool.com",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Initialize agents
coordinator = MasterCoordinatorAgent()
mobile_agent = MobileAgent()
iot_agent = IoTAgent()
drone_agent = DroneAgent()
feedback_learner = FeedbackLearnerAgent()


# Request/Response Models
class AnalysisRequest(BaseModel):
    field_id: str
    crop_type: str
    sensor_data: dict[str, Any] | None = None
    weather_data: dict[str, Any] | None = None
    image_data: dict[str, Any] | None = None


class FeedbackRequest(BaseModel):
    recommendation_id: str
    agent_id: str
    action_type: str
    rating: float  # -1 to 1
    success: bool
    actual_result: dict[str, Any] | None = None
    comments: str | None = None


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


# Full analysis endpoint
@app.post("/api/v1/analyze")
async def analyze_field(request: AnalysisRequest):
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
async def process_sensor_data(request: SensorDataRequest):
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
async def mobile_quick_action(data: dict[str, Any]):
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
async def submit_feedback(request: FeedbackRequest):
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
async def get_system_status():
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
async def get_agent_metrics(agent_id: str):
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

    port = int(os.getenv("PORT", "8120"))
    uvicorn.run(app, host="0.0.0.0", port=port)
