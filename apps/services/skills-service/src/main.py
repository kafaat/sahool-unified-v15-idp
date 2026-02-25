"""
SAHOOL Skills Service - Main API
Manages AI model skill compression, memory storage/recall, and evaluation
Port: 8121
"""

import json
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

import nats
import structlog
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field

# Initialize structured logger
logger = structlog.get_logger()

# Add shared modules to path
# In Docker, shared is at /app/shared
SHARED_PATH = Path("/app/shared")
if not SHARED_PATH.exists():
    # Fallback for local development
    SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# Import unified error handling
from shared.errors_py import (
    ErrorCode,
    ValidationException,
    add_request_id_middleware,
    create_success_response,
    setup_exception_handlers,
)

# Import authentication dependencies
from shared.middleware.tenant_context import TenantContextMiddleware

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str = ""

    async def get_current_user():
        """Placeholder when auth not available"""
        return None


# Token revocation middleware
try:
    from shared.auth.revocation_middleware import TokenRevocationMiddleware
    from shared.auth.token_revocation import get_revocation_store

    REVOCATION_AVAILABLE = True
except ImportError:
    REVOCATION_AVAILABLE = False


# ============== Lifespan Context Manager ==============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage service lifecycle - startup and shutdown
    """
    # Startup
    app.state.revocation_store = None
    app.state.nc = None
    logger.info("Starting Skills Service...")

    # Initialize token revocation store
    if REVOCATION_AVAILABLE:
        try:
            revocation_store = get_revocation_store()
            await revocation_store.initialize()
            app.state.revocation_store = revocation_store
            logger.info("Token revocation store initialized")
        except Exception as e:
            logger.warning(
                "Token revocation store failed (running without revocation)", error=str(e)
            )

    # Initialize NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            app.state.nc = await nats.connect(nats_url)
            logger.info("Connected to NATS", nats_url=nats_url)
        except Exception as e:
            logger.warning("Failed to connect to NATS", error=str(e))
            app.state.nc = None
    else:
        logger.info("NATS_URL not configured, event publishing disabled")

    logger.info("Skills Service ready on port 8121")
    yield

    # Shutdown
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")
    if getattr(app.state, "revocation_store", None):
        await app.state.revocation_store.close()
    logger.info("Skills Service shutting down")


# ============== FastAPI App Initialization ==============

app = FastAPI(
    title="SAHOOL Skills Service",
    description="AI model skill compression, memory management, and evaluation",
    version="16.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Add token revocation middleware
if REVOCATION_AVAILABLE:
    app.add_middleware(
        TokenRevocationMiddleware,
        exempt_paths=["/healthz", "/health", "/docs", "/redoc", "/openapi.json"],
    )

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)


# ============== Event Publishing Helper ==============


async def publish_event(request: Request, subject: str, data: dict) -> bool:
    """
    Publish an event to NATS.
    Returns True if published successfully, False otherwise.
    """
    nc = getattr(request.app.state, "nc", None)
    if not nc:
        logger.debug("NATS not connected, skipping event publish", subject=subject)
        return False

    try:
        payload = json.dumps(data).encode()
        await nc.publish(subject, payload)
        logger.info("Event published", subject=subject, data=data)
        return True
    except Exception as e:
        logger.error("Failed to publish event", subject=subject, error=str(e))
        return False


# ============== Request/Response Models ==============


class CompressRequest(BaseModel):
    """Request model for skill compression"""

    skill_id: str = Field(..., description="Unique identifier for the skill")
    skill_data: dict[str, Any] = Field(..., description="The skill data to compress")
    compression_level: int = Field(
        default=1, ge=1, le=9, description="Compression level 1-9 (1=fastest, 9=best)"
    )
    target_size_kb: int = Field(default=None, description="Target compressed size in KB")


class CompressResponse(BaseModel):
    """Response model for compression"""

    skill_id: str
    original_size_kb: float
    compressed_size_kb: float
    compression_ratio: float
    compression_level: int
    compressed_data: str


class MemoryStoreRequest(BaseModel):
    """Request model for storing skill in memory"""

    skill_id: str = Field(..., description="Unique skill identifier")
    namespace: str = Field(default="default", description="Memory namespace for organization")
    skill_data: dict[str, Any] = Field(..., description="Skill data to store")
    ttl_seconds: int = Field(
        default=3600, ge=0, description="Time to live in seconds (0=permanent)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata")


class MemoryStoreResponse(BaseModel):
    """Response model for memory store"""

    skill_id: str
    namespace: str
    stored_at: str
    ttl_seconds: int
    success: bool


class MemoryRecallRequest(BaseModel):
    """Request model for recalling skill from memory"""

    skill_id: str = Field(..., description="Skill ID to recall")
    namespace: str = Field(default="default", description="Memory namespace")
    include_metadata: bool = Field(default=False, description="Include metadata in response")


class MemoryRecallResponse(BaseModel):
    """Response model for memory recall"""

    skill_id: str
    namespace: str
    found: bool
    skill_data: dict[str, Any] = None
    metadata: dict[str, Any] = None
    retrieved_at: str = None


class EvaluateRequest(BaseModel):
    """Request model for skill evaluation"""

    skill_id: str = Field(..., description="Skill ID to evaluate")
    input_data: dict[str, Any] = Field(..., description="Test input data")
    expected_output: dict[str, Any] = Field(
        default=None, description="Expected output for validation"
    )
    metrics: list[str] = Field(default=["accuracy", "latency"], description="Metrics to evaluate")


class EvaluateResponse(BaseModel):
    """Response model for evaluation"""

    skill_id: str
    status: str
    metrics: dict[str, Any]
    performance_score: float
    timestamp: str


class LearningModuleModel(BaseModel):
    """Model for a learning module"""

    module_id: str = Field(..., description="Unique module identifier")
    title: str = Field(..., description="Module title")
    title_ar: str = Field(default=None, description="Module title in Arabic")
    skill_type: str = Field(..., description="Type of skill covered")
    difficulty: str = Field(default="beginner", description="Difficulty level")
    duration_minutes: int = Field(default=30, description="Estimated duration")


class LearningPathRequest(BaseModel):
    """Request model for learning path recommendation"""

    farmer_id: str = Field(..., description="Unique farmer identifier")
    current_skills: list[str] = Field(default_factory=list, description="List of current skill IDs")
    target_skills: list[str] = Field(default_factory=list, description="Desired skills to learn")
    preferred_difficulty: str = Field(
        default="intermediate", description="Preferred difficulty level"
    )
    max_modules: int = Field(default=5, ge=1, le=20, description="Maximum modules in path")


class LearningPathResponse(BaseModel):
    """Response model for learning path"""

    path_id: str
    farmer_id: str
    modules: list[LearningModuleModel]
    total_duration_minutes: int
    recommended_order: list[str]
    created_at: str


class SkillAssessmentRequest(BaseModel):
    """Request model for skill assessment"""

    farmer_id: str = Field(..., description="Unique farmer identifier")
    skill_type: str = Field(..., description="Type of skill being assessed")
    assessment_data: dict[str, Any] = Field(..., description="Assessment input data")
    assessment_type: str = Field(
        default="quiz", description="Type of assessment (quiz, practical, self)"
    )


class SkillAssessmentResponse(BaseModel):
    """Response model for skill assessment"""

    assessment_id: str
    farmer_id: str
    skill_type: str
    score: float
    level: str
    feedback: str
    feedback_ar: str = None
    timestamp: str


# ============== Health Check Endpoints ==============


@app.get("/healthz")
def health():
    """Health check endpoint for liveness probe"""
    return {"status": "ok", "service": "skills_service", "version": "16.0.0"}


@app.get("/readyz")
def readiness():
    """Readiness check endpoint"""
    return {
        "status": "ok",
        "revocation_store": getattr(app.state, "revocation_store", None) is not None,
        "nats": getattr(app.state, "nc", None) is not None,
    }


# ============== Skill Compression Endpoint ==============


@app.post("/compress")
async def compress_skill(
    request: CompressRequest,
    user: User | None = Depends(get_current_user),
):
    """
    Compress skill data using configurable compression levels
    Reduces skill size while maintaining functionality
    """
    # Validate input
    if not request.skill_data:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_data", "message": "Skill data cannot be empty"},
        )

    # Simulate compression process
    # In production, this would use actual compression algorithms
    original_json = json.dumps(request.skill_data)
    original_size_kb = len(original_json.encode()) / 1024

    # Simple compression simulation (in production, use gzip or other algorithms)
    # The compression_level affects the ratio achieved
    compression_ratio = 0.7 - (request.compression_level * 0.03)  # 0.7 to 0.4
    compressed_size_kb = original_size_kb * max(0.1, compression_ratio)

    # Create compressed representation (base64 encoded)
    import base64

    compressed_data = base64.b64encode(
        json.dumps(
            {
                "skill_id": request.skill_id,
                "original_size": original_size_kb,
                "data": request.skill_data,
            }
        ).encode()
    ).decode()

    return CompressResponse(
        skill_id=request.skill_id,
        original_size_kb=round(original_size_kb, 2),
        compressed_size_kb=round(compressed_size_kb, 2),
        compression_ratio=round(1 - (compressed_size_kb / original_size_kb), 3),
        compression_level=request.compression_level,
        compressed_data=compressed_data,
    )


# ============== Memory Storage Endpoint ==============


@app.post("/memory/store")
async def store_in_memory(
    request: MemoryStoreRequest,
    user: User | None = Depends(get_current_user),
):
    """
    Store skill in volatile memory for fast access
    Supports namespacing and TTL (time-to-live)
    """
    # Validate input
    if not request.skill_id:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_id", "message": "Skill ID is required"},
        )

    if not request.skill_data:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_data", "message": "Skill data is required"},
        )

    # In production, this would store in Redis or in-memory cache
    stored_at = datetime.now(UTC).isoformat()

    return MemoryStoreResponse(
        skill_id=request.skill_id,
        namespace=request.namespace,
        stored_at=stored_at,
        ttl_seconds=request.ttl_seconds,
        success=True,
    )


# ============== Memory Recall Endpoint ==============


@app.post("/memory/recall")
async def recall_from_memory(
    request: MemoryRecallRequest,
    user: User | None = Depends(get_current_user),
):
    """
    Recall previously stored skill from memory
    Returns skill data with optional metadata
    """
    # Validate input
    if not request.skill_id:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_id", "message": "Skill ID is required"},
        )

    # In production, this would retrieve from Redis or in-memory cache
    # For now, return simulated response
    retrieved_at = datetime.now(UTC).isoformat()

    return MemoryRecallResponse(
        skill_id=request.skill_id,
        namespace=request.namespace,
        found=False,  # Simulated - in production check actual cache
        skill_data=None,
        metadata=None if not request.include_metadata else {},
        retrieved_at=retrieved_at,
    )


# ============== Skill Evaluation Endpoint ==============


@app.post("/evaluate")
async def evaluate_skill(
    request: EvaluateRequest,
    http_request: Request,
    user: User | None = Depends(get_current_user),
):
    """
    Evaluate skill performance against metrics
    Measures accuracy, latency, and other performance indicators
    """
    import random

    # Validate input
    if not request.skill_id:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_id", "message": "Skill ID is required"},
        )

    if not request.input_data:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "input_data", "message": "Input data is required"},
        )

    # Simulate evaluation metrics
    metrics = {}
    for metric in request.metrics:
        if metric == "accuracy":
            metrics["accuracy"] = round(random.uniform(0.8, 0.99), 3)
        elif metric == "latency":
            metrics["latency_ms"] = round(random.uniform(10, 500), 2)
        elif metric == "memory":
            metrics["memory_mb"] = round(random.uniform(10, 100), 2)
        else:
            metrics[metric] = round(random.uniform(0.5, 1.0), 3)

    # Calculate overall performance score
    performance_score = sum(v for k, v in metrics.items() if k == "accuracy") or sum(
        metrics.values()
    ) / len(metrics)
    performance_score = min(1.0, performance_score)

    timestamp = datetime.now(UTC).isoformat()

    # Publish skill evaluation event
    await publish_event(
        http_request,
        "sahool.skills.evaluated",
        {
            "skill_id": request.skill_id,
            "performance_score": round(performance_score, 3),
            "metrics": metrics,
            "timestamp": timestamp,
        },
    )

    return EvaluateResponse(
        skill_id=request.skill_id,
        status="completed",
        metrics=metrics,
        performance_score=round(performance_score, 3),
        timestamp=timestamp,
    )


# ============== Skill Assessment Endpoint ==============


@app.post("/assess", response_model=SkillAssessmentResponse)
async def assess_skill(
    request: SkillAssessmentRequest,
    http_request: Request,
    user: User | None = Depends(get_current_user),
):
    """
    Assess a farmer's skill level based on assessment data.
    Publishes assessment results to NATS for downstream processing.
    """
    import random

    # Validate input
    if not request.farmer_id:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "farmer_id", "message": "Farmer ID is required"},
        )

    if not request.skill_type:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "skill_type", "message": "Skill type is required"},
        )

    if not request.assessment_data:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "assessment_data", "message": "Assessment data is required"},
        )

    # Generate assessment ID
    assessment_id = f"assess_{uuid.uuid4().hex[:12]}"

    # Simulate skill assessment scoring
    # In production, this would use ML models or rule-based evaluation
    score = round(random.uniform(40, 100), 1)

    # Determine skill level based on score
    if score >= 90:
        level = "expert"
        feedback = "Excellent performance! You demonstrate mastery of this skill."
        feedback_ar = "أداء ممتاز! أنت تُظهر إتقانًا لهذه المهارة."
    elif score >= 75:
        level = "advanced"
        feedback = "Great job! You have a strong understanding of this skill."
        feedback_ar = "عمل رائع! لديك فهم قوي لهذه المهارة."
    elif score >= 60:
        level = "intermediate"
        feedback = "Good progress! Consider reviewing advanced concepts."
        feedback_ar = "تقدم جيد! فكر في مراجعة المفاهيم المتقدمة."
    elif score >= 40:
        level = "beginner"
        feedback = "Keep practicing! Focus on foundational concepts."
        feedback_ar = "استمر في الممارسة! ركز على المفاهيم الأساسية."
    else:
        level = "novice"
        feedback = "We recommend starting with basic training modules."
        feedback_ar = "نوصي بالبدء بوحدات التدريب الأساسية."

    timestamp = datetime.now(UTC).isoformat()

    # Publish skill assessment event to NATS
    await publish_event(
        http_request,
        "sahool.skills.assessed",
        {
            "farmer_id": request.farmer_id,
            "skill_type": request.skill_type,
            "score": score,
            "level": level,
            "assessment_id": assessment_id,
            "timestamp": timestamp,
        },
    )

    logger.info(
        "Skill assessment completed",
        assessment_id=assessment_id,
        farmer_id=request.farmer_id,
        skill_type=request.skill_type,
        score=score,
        level=level,
    )

    return SkillAssessmentResponse(
        assessment_id=assessment_id,
        farmer_id=request.farmer_id,
        skill_type=request.skill_type,
        score=score,
        level=level,
        feedback=feedback,
        feedback_ar=feedback_ar,
        timestamp=timestamp,
    )


# ============== Learning Path Endpoint ==============


@app.post("/learning-path", response_model=LearningPathResponse)
async def create_learning_path(
    request: LearningPathRequest,
    http_request: Request,
    user: User | None = Depends(get_current_user),
):
    """
    Generate a personalized learning path for a farmer.
    Publishes learning path creation event to NATS.
    """
    # Validate input
    if not request.farmer_id:
        raise ValidationException(
            ErrorCode.INVALID_INPUT,
            details={"field": "farmer_id", "message": "Farmer ID is required"},
        )

    # Generate path ID
    path_id = f"path_{uuid.uuid4().hex[:12]}"

    # Simulate learning path generation
    # In production, this would use recommendation algorithms
    skill_modules = {
        "irrigation": [
            LearningModuleModel(
                module_id="irr_basics",
                title="Irrigation Fundamentals",
                title_ar="أساسيات الري",
                skill_type="irrigation",
                difficulty="beginner",
                duration_minutes=30,
            ),
            LearningModuleModel(
                module_id="irr_drip",
                title="Drip Irrigation Systems",
                title_ar="أنظمة الري بالتنقيط",
                skill_type="irrigation",
                difficulty="intermediate",
                duration_minutes=45,
            ),
            LearningModuleModel(
                module_id="irr_smart",
                title="Smart Irrigation Scheduling",
                title_ar="جدولة الري الذكي",
                skill_type="irrigation",
                difficulty="advanced",
                duration_minutes=60,
            ),
        ],
        "crop_management": [
            LearningModuleModel(
                module_id="crop_basics",
                title="Crop Management Basics",
                title_ar="أساسيات إدارة المحاصيل",
                skill_type="crop_management",
                difficulty="beginner",
                duration_minutes=40,
            ),
            LearningModuleModel(
                module_id="crop_disease",
                title="Disease Identification",
                title_ar="تحديد الأمراض",
                skill_type="crop_management",
                difficulty="intermediate",
                duration_minutes=50,
            ),
        ],
        "soil_analysis": [
            LearningModuleModel(
                module_id="soil_testing",
                title="Soil Testing Fundamentals",
                title_ar="أساسيات فحص التربة",
                skill_type="soil_analysis",
                difficulty="beginner",
                duration_minutes=35,
            ),
            LearningModuleModel(
                module_id="soil_nutrition",
                title="Soil Nutrition Management",
                title_ar="إدارة تغذية التربة",
                skill_type="soil_analysis",
                difficulty="intermediate",
                duration_minutes=55,
            ),
        ],
        "pest_control": [
            LearningModuleModel(
                module_id="pest_id",
                title="Pest Identification",
                title_ar="تحديد الآفات",
                skill_type="pest_control",
                difficulty="beginner",
                duration_minutes=30,
            ),
            LearningModuleModel(
                module_id="pest_ipm",
                title="Integrated Pest Management",
                title_ar="الإدارة المتكاملة للآفات",
                skill_type="pest_control",
                difficulty="advanced",
                duration_minutes=60,
            ),
        ],
    }

    # Build learning path based on target skills
    modules = []
    target_skills = (
        request.target_skills if request.target_skills else list(skill_modules.keys())[:2]
    )

    for skill in target_skills:
        if skill in skill_modules:
            for module in skill_modules[skill]:
                if len(modules) < request.max_modules:
                    # Filter by difficulty preference
                    if (
                        request.preferred_difficulty == "beginner"
                        and module.difficulty in ["beginner"]
                        or request.preferred_difficulty == "intermediate"
                        and module.difficulty
                        in [
                            "beginner",
                            "intermediate",
                        ]
                        or request.preferred_difficulty == "advanced"
                        or request.preferred_difficulty
                        not in ["beginner", "intermediate", "advanced"]
                    ):
                        modules.append(module)

    # If no modules matched, add some defaults
    if not modules:
        for skill_list in skill_modules.values():
            for module in skill_list:
                if len(modules) < request.max_modules:
                    modules.append(module)

    # Calculate total duration
    total_duration = sum(m.duration_minutes for m in modules)

    # Get recommended order (by module_id)
    recommended_order = [m.module_id for m in modules]

    timestamp = datetime.now(UTC).isoformat()

    # Publish learning path creation event to NATS
    await publish_event(
        http_request,
        "sahool.skills.learning_path_created",
        {
            "farmer_id": request.farmer_id,
            "path_id": path_id,
            "modules": [m.module_id for m in modules],
            "total_modules": len(modules),
            "total_duration_minutes": total_duration,
            "timestamp": timestamp,
        },
    )

    logger.info(
        "Learning path created",
        path_id=path_id,
        farmer_id=request.farmer_id,
        module_count=len(modules),
        total_duration=total_duration,
    )

    return LearningPathResponse(
        path_id=path_id,
        farmer_id=request.farmer_id,
        modules=modules,
        total_duration_minutes=total_duration,
        recommended_order=recommended_order,
        created_at=timestamp,
    )


# ============== Root Endpoint ==============


@app.get("/")
def root():
    """API root endpoint"""
    return create_success_response(
        {
            "service": "skills_service",
            "version": "16.0.0",
            "endpoints": [
                "POST /compress",
                "POST /memory/store",
                "POST /memory/recall",
                "POST /evaluate",
                "POST /assess",
                "POST /learning-path",
                "GET /healthz",
                "GET /readyz",
            ],
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8121))
    uvicorn.run(app, host="0.0.0.0", port=port)
