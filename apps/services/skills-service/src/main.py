"""
SAHOOL Skills Service - Main API
Manages AI model skill compression, memory storage/recall, and evaluation
Port: 8121
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

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
try:
    from auth.dependencies import get_current_user
    from auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False
    User = None

    def get_current_user():
        """Placeholder when auth not available"""
        return None


# Token revocation middleware
try:
    from auth.revocation_middleware import TokenRevocationMiddleware
    from auth.token_revocation import get_revocation_store

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
    print("🧠 Starting Skills Service...")

    # Initialize token revocation store
    if REVOCATION_AVAILABLE:
        try:
            revocation_store = get_revocation_store()
            await revocation_store.initialize()
            app.state.revocation_store = revocation_store
            print("✅ Token revocation store initialized")
        except Exception as e:
            print(f"⚠️ Token revocation store failed (running without revocation): {e}")

    print("✅ Skills Service ready on port 8110")
    yield

    # Shutdown
    if getattr(app.state, "revocation_store", None):
        await app.state.revocation_store.close()
    print("👋 Skills Service shutting down")


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


# ============== Request/Response Models ==============


class CompressRequest(BaseModel):
    """Request model for skill compression"""

    skill_id: str = Field(..., description="Unique identifier for the skill")
    skill_data: dict[str, Any] = Field(..., description="The skill data to compress")
    compression_level: int = Field(
        default=1, ge=1, le=9, description="Compression level 1-9 (1=fastest, 9=best)"
    )
    target_size_kb: int = Field(
        default=None, description="Target compressed size in KB"
    )


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
    namespace: str = Field(
        default="default", description="Memory namespace for organization"
    )
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
    metrics: list[str] = Field(
        default=["accuracy", "latency"], description="Metrics to evaluate"
    )


class EvaluateResponse(BaseModel):
    """Response model for evaluation"""

    skill_id: str
    status: str
    metrics: dict[str, Any]
    performance_score: float
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
    }


# ============== Skill Compression Endpoint ==============


@app.post("/compress")
async def compress_skill(
    request: CompressRequest,
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
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
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
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
    from datetime import datetime

    stored_at = datetime.utcnow().isoformat()

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
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
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
    from datetime import datetime

    retrieved_at = datetime.utcnow().isoformat()

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
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
):
    """
    Evaluate skill performance against metrics
    Measures accuracy, latency, and other performance indicators
    """
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
    from datetime import datetime
    import random

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
    performance_score = sum(
        v for k, v in metrics.items() if k == "accuracy"
    ) or sum(metrics.values()) / len(metrics)
    performance_score = min(1.0, performance_score)

    return EvaluateResponse(
        skill_id=request.skill_id,
        status="completed",
        metrics=metrics,
        performance_score=round(performance_score, 3),
        timestamp=datetime.utcnow().isoformat(),
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
                "GET /healthz",
                "GET /readyz",
            ],
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8110))
    uvicorn.run(app, host="0.0.0.0", port=port)
