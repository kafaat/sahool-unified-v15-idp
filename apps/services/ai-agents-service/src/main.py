"""
SAHOOL AI Agents Service
=========================
Autonomous AI agents for agricultural intelligence.

Inspired by: Dexter, OpenCode, Claude Code patterns
Features:
- Task decomposition and execution
- Agricultural research agents
- Farm advisory agents (Plan/Execute modes)
- Self-validation with retry logic

Port: 8130
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from shared.ai.agents import (
    AgriculturalResearchAgent,
    FarmAdvisorAgent,
    PlannerAgent,
    AgentMode,
)

# Service configuration
SERVICE_NAME = "ai-agents-service"
SERVICE_NAME_AR = "خدمة الوكلاء الذكية"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = 8130


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════

class AgentExecuteRequest(BaseModel):
    """Request to execute an agent task"""
    task: str = Field(..., description="Task description in natural language")
    task_ar: str | None = Field(None, description="Task description in Arabic")
    agent_type: str = Field("farm_advisor", description="Agent type: farm_advisor, research, planner")
    mode: str = Field("hybrid", description="Execution mode: plan, execute, hybrid")
    context: dict[str, Any] | None = Field(None, description="Additional context for the agent")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    field_id: str | None = Field(None, description="Optional field ID for field-specific tasks")
    farm_id: str | None = Field(None, description="Optional farm ID")
    max_steps: int = Field(50, ge=1, le=100, description="Maximum execution steps")
    timeout_seconds: int = Field(300, ge=30, le=600, description="Execution timeout")


class AgentStep(BaseModel):
    """Single step in agent execution"""
    step_number: int
    action: str
    action_ar: str | None = None
    tool_used: str | None = None
    result: dict[str, Any] | None = None
    timestamp: datetime
    duration_ms: int | None = None


class AgentExecuteResponse(BaseModel):
    """Response from agent execution"""
    execution_id: str
    agent_type: str
    mode: str
    task: str
    status: str  # running, completed, failed, timeout
    state: str  # idle, planning, executing, validating, completed, error
    steps: list[AgentStep] = []
    final_result: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    total_duration_ms: int | None = None


class AgentListItem(BaseModel):
    """Agent type information"""
    agent_type: str
    name: str
    name_ar: str
    description: str
    description_ar: str
    supported_modes: list[str]
    available_tools: list[str]


class ExecutionStatusResponse(BaseModel):
    """Status of an ongoing execution"""
    execution_id: str
    status: str
    state: str
    current_step: int
    total_steps: int
    progress_percent: float
    last_action: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory execution store (replace with Redis in production)
# ═══════════════════════════════════════════════════════════════════════════════

executions: dict[str, AgentExecuteResponse] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")

    # Initialize NATS publisher (if available)
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            from shared.events.publisher import get_publisher
            app.state.publisher = await get_publisher(
                service_name=SERVICE_NAME,
                service_version=SERVICE_VERSION
            )
            app.state.nats_connected = True
            print(f"✅ NATS connected: {nats_url}")
        except Exception as e:
            print(f"⚠️ NATS connection failed: {e}")
            app.state.publisher = None
            app.state.nats_connected = False
    else:
        app.state.publisher = None
        app.state.nats_connected = False

    print(f"✅ {SERVICE_NAME} ready on port {SERVICE_PORT}")

    yield

    # Shutdown
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    print(f"👋 {SERVICE_NAME} shutdown complete")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL AI Agents Service",
    description="Autonomous AI agents for agricultural intelligence | وكلاء ذكاء اصطناعي مستقلين للذكاء الزراعي",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/healthz", tags=["Health"])
def health():
    """Liveness probe"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """Readiness probe"""
    return {
        "status": "ok",
        "nats": getattr(app.state, "nats_connected", False),
        "executions_active": len([e for e in executions.values() if e.status == "running"]),
    }


@app.get("/health", tags=["Health"])
def health_detailed():
    """Detailed health status"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "service_ar": SERVICE_NAME_AR,
        "version": SERVICE_VERSION,
        "nats_connected": getattr(app.state, "nats_connected", False),
        "active_executions": len([e for e in executions.values() if e.status == "running"]),
        "total_executions": len(executions),
        "available_agents": ["farm_advisor", "research", "planner"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Management Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/agents", response_model=list[AgentListItem], tags=["Agents"])
def list_agents():
    """List available agent types | قائمة أنواع الوكلاء المتاحة"""
    return [
        AgentListItem(
            agent_type="farm_advisor",
            name="Farm Advisor Agent",
            name_ar="وكيل المستشار الزراعي",
            description="Dual-mode agent for farm advisory with Plan and Execute modes",
            description_ar="وكيل ثنائي الوضع للاستشارات الزراعية مع وضعي التخطيط والتنفيذ",
            supported_modes=["plan", "execute", "hybrid"],
            available_tools=[
                "fetch_satellite_data", "fetch_weather_data", "fetch_sensor_data",
                "analyze_crop_health", "generate_recommendations",
                "schedule_irrigation", "create_task"
            ],
        ),
        AgentListItem(
            agent_type="research",
            name="Agricultural Research Agent",
            name_ar="وكيل البحث الزراعي",
            description="Specialized agent for agricultural data analysis and research",
            description_ar="وكيل متخصص لتحليل البيانات الزراعية والبحث",
            supported_modes=["execute", "hybrid"],
            available_tools=[
                "fetch_satellite_data", "fetch_weather_data", "fetch_sensor_data",
                "analyze_crop_health", "calculate_irrigation_need", "diagnose_crop_issue"
            ],
        ),
        AgentListItem(
            agent_type="planner",
            name="Planner Agent",
            name_ar="وكيل التخطيط",
            description="Read-only planning agent for task analysis and recommendations",
            description_ar="وكيل تخطيط للقراءة فقط لتحليل المهام والتوصيات",
            supported_modes=["plan"],
            available_tools=[
                "fetch_satellite_data", "fetch_weather_data", "analyze_crop_health"
            ],
        ),
    ]


@app.post("/api/v1/agents/execute", response_model=AgentExecuteResponse, tags=["Agents"])
async def execute_agent(
    request: AgentExecuteRequest,
    background_tasks: BackgroundTasks,
):
    """
    Execute an agent task

    تنفيذ مهمة الوكيل

    - **task**: Task description in natural language
    - **agent_type**: Type of agent (farm_advisor, research, planner)
    - **mode**: Execution mode (plan, execute, hybrid)
    - **context**: Additional context for the agent
    """
    execution_id = str(uuid4())
    started_at = datetime.utcnow()

    # Create initial response
    response = AgentExecuteResponse(
        execution_id=execution_id,
        agent_type=request.agent_type,
        mode=request.mode,
        task=request.task,
        status="running",
        state="planning" if request.mode in ["plan", "hybrid"] else "executing",
        started_at=started_at,
    )

    executions[execution_id] = response

    # Execute in background
    background_tasks.add_task(
        _execute_agent_task,
        execution_id,
        request,
    )

    return response


async def _execute_agent_task(execution_id: str, request: AgentExecuteRequest):
    """Background task to execute agent"""
    response = executions[execution_id]

    try:
        # Select agent type
        if request.agent_type == "farm_advisor":
            mode = AgentMode.HYBRID
            if request.mode == "plan":
                mode = AgentMode.PLAN
            elif request.mode == "execute":
                mode = AgentMode.EXECUTE

            agent = FarmAdvisorAgent(
                agent_id=execution_id,
                mode=mode,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        elif request.agent_type == "research":
            agent = AgriculturalResearchAgent(
                agent_id=execution_id,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        elif request.agent_type == "planner":
            agent = PlannerAgent(
                agent_id=execution_id,
                max_steps=request.max_steps,
                timeout_seconds=request.timeout_seconds,
            )
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")

        # Build context
        context = request.context or {}
        if request.field_id:
            context["field_id"] = request.field_id
        if request.farm_id:
            context["farm_id"] = request.farm_id
        context["tenant_id"] = request.tenant_id

        # Execute agent
        result = await agent.run(request.task, context)

        # Update response with results
        response.status = "completed" if result.get("success") else "failed"
        response.state = "completed"
        response.final_result = result
        response.completed_at = datetime.utcnow()

        if response.started_at and response.completed_at:
            response.total_duration_ms = int(
                (response.completed_at - response.started_at).total_seconds() * 1000
            )

        # Convert agent steps to response format
        if hasattr(agent, "steps"):
            for i, step in enumerate(agent.steps):
                response.steps.append(AgentStep(
                    step_number=i + 1,
                    action=step.get("action", "unknown"),
                    action_ar=step.get("action_ar"),
                    tool_used=step.get("tool"),
                    result=step.get("result"),
                    timestamp=step.get("timestamp", datetime.utcnow()),
                    duration_ms=step.get("duration_ms"),
                ))

    except Exception as e:
        response.status = "failed"
        response.state = "error"
        response.error = str(e)
        response.completed_at = datetime.utcnow()

        if response.started_at and response.completed_at:
            response.total_duration_ms = int(
                (response.completed_at - response.started_at).total_seconds() * 1000
            )


@app.get("/api/v1/agents/executions/{execution_id}", response_model=AgentExecuteResponse, tags=["Agents"])
def get_execution(execution_id: str):
    """Get execution status and results | الحصول على حالة ونتائج التنفيذ"""
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    return executions[execution_id]


@app.get("/api/v1/agents/executions/{execution_id}/status", response_model=ExecutionStatusResponse, tags=["Agents"])
def get_execution_status(execution_id: str):
    """Get brief execution status | الحصول على حالة التنفيذ المختصرة"""
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = executions[execution_id]
    total_steps = len(execution.steps) or 1
    current_step = len(execution.steps)

    return ExecutionStatusResponse(
        execution_id=execution_id,
        status=execution.status,
        state=execution.state,
        current_step=current_step,
        total_steps=total_steps,
        progress_percent=(current_step / total_steps) * 100 if total_steps > 0 else 0,
        last_action=execution.steps[-1].action if execution.steps else None,
    )


@app.delete("/api/v1/agents/executions/{execution_id}", tags=["Agents"])
def cancel_execution(execution_id: str):
    """Cancel a running execution | إلغاء تنفيذ قيد التشغيل"""
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = executions[execution_id]
    if execution.status == "running":
        execution.status = "cancelled"
        execution.state = "cancelled"
        execution.completed_at = datetime.utcnow()
        return {"message": "Execution cancelled", "execution_id": execution_id}

    return {"message": "Execution already completed", "execution_id": execution_id}


@app.get("/api/v1/agents/executions", response_model=list[AgentExecuteResponse], tags=["Agents"])
def list_executions(
    tenant_id: str = Query(..., description="Filter by tenant ID"),
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100),
):
    """List recent executions | قائمة التنفيذات الأخيرة"""
    results = list(executions.values())

    # Filter by status if provided
    if status:
        results = [e for e in results if e.status == status]

    # Sort by started_at descending
    results.sort(key=lambda x: x.started_at, reverse=True)

    return results[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Action Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

class QuickAnalysisRequest(BaseModel):
    """Quick analysis request"""
    field_id: str
    tenant_id: str
    analysis_type: str = Field("crop_health", description="Type: crop_health, irrigation, yield")


class QuickAnalysisResponse(BaseModel):
    """Quick analysis response"""
    field_id: str
    analysis_type: str
    summary: str
    summary_ar: str
    recommendations: list[dict[str, Any]]
    confidence: float
    timestamp: datetime


@app.post("/api/v1/agents/quick/analyze", response_model=QuickAnalysisResponse, tags=["Quick Actions"])
async def quick_analyze(request: QuickAnalysisRequest):
    """
    Quick field analysis without full agent execution

    تحليل سريع للحقل بدون تنفيذ الوكيل الكامل
    """
    # Simulated quick analysis (replace with actual implementation)
    return QuickAnalysisResponse(
        field_id=request.field_id,
        analysis_type=request.analysis_type,
        summary=f"Quick {request.analysis_type} analysis completed for field {request.field_id}",
        summary_ar=f"تم إكمال تحليل {request.analysis_type} السريع للحقل {request.field_id}",
        recommendations=[
            {
                "action": "Monitor soil moisture",
                "action_ar": "مراقبة رطوبة التربة",
                "priority": "medium",
                "reason": "Soil moisture levels are within normal range",
            }
        ],
        confidence=0.85,
        timestamp=datetime.utcnow(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Metrics Endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus-compatible metrics"""
    total = len(executions)
    running = len([e for e in executions.values() if e.status == "running"])
    completed = len([e for e in executions.values() if e.status == "completed"])
    failed = len([e for e in executions.values() if e.status == "failed"])

    return f"""# HELP ai_agents_executions_total Total number of agent executions
# TYPE ai_agents_executions_total counter
ai_agents_executions_total {total}

# HELP ai_agents_executions_running Currently running executions
# TYPE ai_agents_executions_running gauge
ai_agents_executions_running {running}

# HELP ai_agents_executions_completed Completed executions
# TYPE ai_agents_executions_completed counter
ai_agents_executions_completed {completed}

# HELP ai_agents_executions_failed Failed executions
# TYPE ai_agents_executions_failed counter
ai_agents_executions_failed {failed}
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
