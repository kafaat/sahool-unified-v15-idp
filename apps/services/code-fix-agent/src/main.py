"""
SAHOOL Code Fix Agent Service
خدمة وكيل إصلاح الكود

FastAPI service for AI-powered code analysis, bug fixing, and implementation.
Follows SAHOOL service conventions and A2A Protocol.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .agent import CodeFixAgent

# ============================================================================
# CONFIGURATION
# ============================================================================

SERVICE_NAME = "code-fix-agent"
SERVICE_VERSION = "1.0.0"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class AnalyzeCodeRequest(BaseModel):
    """طلب تحليل الكود"""

    code: str = Field(..., description="Code snippet to analyze")
    language: str = Field(
        default="python", description="Programming language (python, typescript, dart)"
    )
    file_path: str | None = Field(default=None, description="Optional file path")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")


class FixCodeRequest(BaseModel):
    """طلب إصلاح الكود"""

    code: str = Field(..., description="Code with issue to fix")
    errors: list[dict[str, Any]] = Field(..., description="Error information")
    language: str = Field(default="python", description="Programming language")
    strategy: str = Field(
        default="minimal", description="Fix strategy (minimal, comprehensive, refactor)"
    )


class ReviewPRRequest(BaseModel):
    """طلب مراجعة طلب السحب"""

    diff: str = Field(..., description="PR diff content")
    context_files: list[str] | None = Field(default=None, description="Related files")
    review_focus: list[str] | None = Field(
        default=None, description="Focus areas (security, performance, style)"
    )


class GenerateTestsRequest(BaseModel):
    """طلب توليد الاختبارات"""

    code: str = Field(..., description="Code to generate tests for")
    language: str = Field(default="python", description="Programming language")
    framework: str | None = Field(default=None, description="Test framework")
    coverage_target: int = Field(default=80, ge=0, le=100, description="Coverage target")


class ImplementFeatureRequest(BaseModel):
    """طلب تنفيذ ميزة"""

    specification: dict[str, Any] = Field(..., description="Feature specification")
    target_files: list[str] | None = Field(default=None, description="Target files")
    design_patterns: list[str] | None = Field(default=None, description="Patterns to use")


class AgentResponse(BaseModel):
    """استجابة الوكيل"""

    success: bool
    action_type: str
    data: dict[str, Any] | None = None
    error: str | None = None
    confidence: float | None = None
    reasoning: str | None = None
    reasoning_ar: str | None = None
    response_time_ms: float | None = None
    agent_id: str


# ============================================================================
# LIFESPAN & APP SETUP
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Initialize and cleanup resources
    """
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION)

    # Initialize agent
    app.state.agent = CodeFixAgent(agent_id=f"{SERVICE_NAME}_001")

    # TODO: Initialize NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        logger.info("nats_configured", url=nats_url)
        # app.state.nc = await nats.connect(nats_url)

    logger.info("service_ready", service=SERVICE_NAME)

    yield

    # Cleanup
    logger.info("service_stopping", service=SERVICE_NAME)

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()


app = FastAPI(
    title="SAHOOL Code Fix Agent",
    description="AI-powered code analysis, bug fixing, and implementation agent",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MIDDLEWARE
# ============================================================================


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests"""
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================


@app.get("/healthz", tags=["Health"])
@app.get("/health/live", tags=["Health"])
async def liveness():
    """
    Liveness probe
    فحص الحياة
    """
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/readyz", tags=["Health"])
@app.get("/health/ready", tags=["Health"])
async def readiness(request: Request):
    """
    Readiness probe
    فحص الجاهزية
    """
    agent = getattr(request.app.state, "agent", None)

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "agent": agent.status.value if agent else "not_initialized",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", tags=["Health"])
async def health(request: Request):
    """
    Combined health check
    فحص الصحة الشامل
    """
    agent = getattr(request.app.state, "agent", None)

    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "agent": {
            "id": agent.agent_id if agent else None,
            "status": agent.status.value if agent else "not_initialized",
            "metrics": agent.get_metrics() if agent else None,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/metrics", tags=["Health"])
async def metrics(request: Request):
    """
    Prometheus metrics
    مقاييس بروميثيوس
    """
    agent = getattr(request.app.state, "agent", None)

    if not agent:
        return {"error": "Agent not initialized"}

    metrics = agent.get_metrics()

    # Format for Prometheus
    prometheus_metrics = f"""# HELP code_fix_agent_requests_total Total number of requests
# TYPE code_fix_agent_requests_total counter
code_fix_agent_requests_total {metrics["total_requests"]}

# HELP code_fix_agent_success_rate Success rate percentage
# TYPE code_fix_agent_success_rate gauge
code_fix_agent_success_rate {metrics["success_rate_percent"]}

# HELP code_fix_agent_response_time_ms Average response time in milliseconds
# TYPE code_fix_agent_response_time_ms gauge
code_fix_agent_response_time_ms {metrics["avg_response_time_ms"]}

# HELP code_fix_agent_patterns_learned Number of patterns learned
# TYPE code_fix_agent_patterns_learned gauge
code_fix_agent_patterns_learned {metrics["patterns_learned"]}
"""

    return JSONResponse(content=prometheus_metrics, media_type="text/plain")


# ============================================================================
# AGENT API ENDPOINTS
# ============================================================================


@app.post("/api/v1/analyze", response_model=AgentResponse, tags=["Agent"])
async def analyze_code(request: Request, body: AnalyzeCodeRequest):
    """
    تحليل الكود واكتشاف المشاكل
    Analyze code and detect issues

    Analyzes the provided code snippet for:
    - Syntax errors
    - Security vulnerabilities
    - Performance issues
    - Style violations
    - Type errors
    """
    agent: CodeFixAgent = request.app.state.agent

    from .agent.code_fix_agent import AgentPercept

    percept = AgentPercept(
        percept_type="code_snippet",
        data={
            "code": body.code,
            "language": body.language,
            "file_path": body.file_path or "",
        },
        source="api",
    )

    result = await agent.run(percept)

    return AgentResponse(
        success=result.get("success", False),
        action_type=result.get("action_type", "analyze_code"),
        data=result.get("analysis") or result.get("action", {}).get("parameters"),
        confidence=result.get("action", {}).get("confidence"),
        reasoning=result.get("action", {}).get("reasoning"),
        reasoning_ar=result.get("action", {}).get("reasoning_ar"),
        response_time_ms=result.get("total_time_ms"),
        agent_id=result.get("agent_id", agent.agent_id),
    )


@app.post("/api/v1/fix", response_model=AgentResponse, tags=["Agent"])
async def fix_code(request: Request, body: FixCodeRequest):
    """
    إصلاح الكود تلقائياً
    Automatically fix code issues

    Generates and applies fixes for the provided errors.
    """
    agent: CodeFixAgent = request.app.state.agent

    from .agent.code_fix_agent import AgentPercept

    # First perceive the code
    await agent.perceive(
        AgentPercept(
            percept_type="code_snippet",
            data={
                "code": body.code,
                "language": body.language,
            },
            source="api",
        )
    )

    # Then perceive the errors
    percept = AgentPercept(
        percept_type="error_log",
        data=body.errors,
        source="api",
    )

    result = await agent.run(percept)

    return AgentResponse(
        success=result.get("success", False),
        action_type=result.get("action_type", "fix_code"),
        data=result.get("fix") or result.get("action", {}).get("parameters"),
        confidence=result.get("action", {}).get("confidence"),
        reasoning=result.get("action", {}).get("reasoning"),
        reasoning_ar=result.get("action", {}).get("reasoning_ar"),
        response_time_ms=result.get("total_time_ms"),
        agent_id=result.get("agent_id", agent.agent_id),
    )


@app.post("/api/v1/review", response_model=AgentResponse, tags=["Agent"])
async def review_pr(request: Request, body: ReviewPRRequest):
    """
    مراجعة طلب السحب
    Review pull request

    Analyzes PR changes and provides review comments.
    """
    agent: CodeFixAgent = request.app.state.agent

    from .agent.code_fix_agent import AgentPercept

    percept = AgentPercept(
        percept_type="pr_diff",
        data=body.diff,
        source="api",
    )

    result = await agent.run(percept)

    return AgentResponse(
        success=result.get("success", False),
        action_type=result.get("action_type", "review_pr"),
        data=result.get("review") or result.get("action", {}).get("parameters"),
        confidence=result.get("action", {}).get("confidence"),
        reasoning=result.get("action", {}).get("reasoning"),
        reasoning_ar=result.get("action", {}).get("reasoning_ar"),
        response_time_ms=result.get("total_time_ms"),
        agent_id=result.get("agent_id", agent.agent_id),
    )


@app.post("/api/v1/generate-tests", response_model=AgentResponse, tags=["Agent"])
async def generate_tests(request: Request, body: GenerateTestsRequest):
    """
    توليد اختبارات تلقائية
    Generate automated tests

    Generates unit tests for the provided code.
    """
    agent: CodeFixAgent = request.app.state.agent

    from .agent.code_fix_agent import AgentPercept

    percept = AgentPercept(
        percept_type="code_snippet",
        data={
            "code": body.code,
            "language": body.language,
            "generate_tests": True,
            "framework": body.framework,
            "coverage_target": body.coverage_target,
        },
        source="api",
    )

    result = await agent.run(percept)

    return AgentResponse(
        success=result.get("success", False),
        action_type="generate_tests",
        data=result.get("tests") or result.get("action", {}).get("parameters"),
        confidence=result.get("action", {}).get("confidence"),
        reasoning=result.get("action", {}).get("reasoning"),
        reasoning_ar=result.get("action", {}).get("reasoning_ar"),
        response_time_ms=result.get("total_time_ms"),
        agent_id=result.get("agent_id", agent.agent_id),
    )


@app.post("/api/v1/implement", response_model=AgentResponse, tags=["Agent"])
async def implement_feature(request: Request, body: ImplementFeatureRequest):
    """
    تنفيذ ميزة جديدة
    Implement new feature

    Implements a feature based on the provided specification.
    """
    agent: CodeFixAgent = request.app.state.agent

    from .agent.code_fix_agent import AgentPercept

    percept = AgentPercept(
        percept_type="specification",
        data=body.specification,
        source="api",
    )

    result = await agent.run(percept)

    return AgentResponse(
        success=result.get("success", False),
        action_type="implement_feature",
        data=result.get("implementation") or result.get("action", {}).get("parameters"),
        confidence=result.get("action", {}).get("confidence"),
        reasoning=result.get("action", {}).get("reasoning"),
        reasoning_ar=result.get("action", {}).get("reasoning_ar"),
        response_time_ms=result.get("total_time_ms"),
        agent_id=result.get("agent_id", agent.agent_id),
    )


@app.post("/api/v1/feedback", tags=["Agent"])
async def submit_feedback(request: Request, feedback: dict[str, Any]):
    """
    إرسال التغذية الراجعة للتعلم
    Submit feedback for learning

    Allows the agent to learn from fix results.
    """
    agent: CodeFixAgent = request.app.state.agent

    await agent.learn(feedback)

    return {
        "success": True,
        "message": "Feedback processed",
        "patterns_learned": len(agent.success_patterns),
    }


@app.get("/api/v1/agent/info", tags=["Agent"])
async def get_agent_info(request: Request):
    """
    الحصول على معلومات الوكيل
    Get agent information
    """
    agent: CodeFixAgent = request.app.state.agent

    return agent.to_dict()


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        request_id=getattr(request.state, "request_id", None),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8090"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level=LOG_LEVEL.lower(),
    )
