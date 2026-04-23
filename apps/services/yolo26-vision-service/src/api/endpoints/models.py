"""
Model Management Endpoints for YOLO26 Vision Service.

Provides endpoints for model version management, performance metrics,
and model registry operations.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.core.config import settings

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


from src.models.versioning import (
    ModelMetrics,
    ModelStage,
    ModelStatus,
    ModelVersion,
    ModelVersionRegistry,
    get_version_registry,
)
from src.models.yolo26_manager import (
    ModelTask,
    YOLO26ModelManager,
    get_model_manager,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/vision/models", tags=["models"])


# =============================================================================
# Schemas
# =============================================================================


class ModelVersionResponse(BaseModel):
    """Model version information response."""

    version: str
    task: str
    variant: str
    model_key: str
    created_at: str
    status: str
    stage: str
    file_path: str
    file_hash: str
    file_size_mb: float
    metrics: dict[str, float]
    description: str
    description_ar: str
    changelog: list[str]
    tags: list[str]


class ModelMetricsUpdate(BaseModel):
    """Model metrics update request."""

    accuracy: float = Field(ge=0.0, le=1.0, default=0.0)
    precision: float = Field(ge=0.0, le=1.0, default=0.0)
    recall: float = Field(ge=0.0, le=1.0, default=0.0)
    f1_score: float = Field(ge=0.0, le=1.0, default=0.0)
    map50: float = Field(ge=0.0, le=1.0, default=0.0)
    map50_95: float = Field(ge=0.0, le=1.0, default=0.0)
    inference_time_ms: float = Field(ge=0.0, default=0.0)
    memory_mb: float = Field(ge=0.0, default=0.0)


class RegisterVersionRequest(BaseModel):
    """Request to register a new model version."""

    task: str = Field(..., description="Model task (e.g., pest_detection)")
    variant: str = Field(..., description="Model variant (n, s, m, l, x)")
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
    file_path: str = Field(..., description="Path to model file")
    description: str = Field(default="", description="Version description")
    description_ar: str = Field(default="", description="Arabic description")
    changelog: list[str] = Field(default_factory=list, description="List of changes")
    tags: list[str] = Field(default_factory=list, description="Version tags")
    stage: str = Field(default="development", description="Deployment stage")
    activate: bool = Field(default=False, description="Set as active version")
    metrics: ModelMetricsUpdate | None = None


class VersionComparisonResponse(BaseModel):
    """Response for version comparison."""

    version_a: dict[str, Any]
    version_b: dict[str, Any]
    metrics_comparison: dict[str, float]
    improved: bool


class LoadedModelInfo(BaseModel):
    """Information about a loaded model."""

    model_key: str
    task: str
    variant: str
    loaded: bool
    version: str | None = None
    status: str | None = None


# =============================================================================
# Dependencies
# =============================================================================


async def get_manager() -> YOLO26ModelManager:
    """Get the model manager instance."""
    return get_model_manager()


async def get_registry() -> ModelVersionRegistry:
    """Get the version registry instance."""
    return get_version_registry()


# =============================================================================
# Endpoints
# =============================================================================


@router.get(
    "/versions",
    summary="List all model versions",
    description="Get all registered model versions across all tasks.",
)
async def list_all_versions(
    registry: ModelVersionRegistry = Depends(get_registry),
) -> dict[str, list[dict[str, Any]]]:
    """List all registered model versions."""
    return registry.get_all_versions()


@router.get(
    "/versions/{task}/{variant}",
    summary="Get version history",
    description="Get version history for a specific task and variant.",
)
async def get_version_history(
    task: str,
    variant: str,
    registry: ModelVersionRegistry = Depends(get_registry),
) -> list[dict[str, Any]]:
    """Get version history for a task/variant."""
    versions = registry.get_version_history(task, variant)
    return [v.to_dict() for v in versions]


@router.get(
    "/versions/{task}/{variant}/active",
    response_model=ModelVersionResponse | None,
    summary="Get active version",
    description="Get the currently active version for a task and variant.",
)
async def get_active_version(
    task: str,
    variant: str,
    registry: ModelVersionRegistry = Depends(get_registry),
) -> ModelVersionResponse | None:
    """Get the active version for a task/variant."""
    version = registry.get_active_version(task, variant)
    if version:
        data = version.to_dict()
        return ModelVersionResponse(**data)
    return None


@router.get(
    "/versions/{task}/{variant}/{version}",
    response_model=ModelVersionResponse,
    summary="Get specific version",
    description="Get a specific model version by task, variant, and version.",
)
async def get_specific_version(
    task: str,
    variant: str,
    version: str,
    registry: ModelVersionRegistry = Depends(get_registry),
) -> ModelVersionResponse:
    """Get a specific version."""
    v = registry.get_version(task, variant, version)
    if not v:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Version not found",
                "message": f"Version {version} not found for {task}/{variant}",
                "message_ar": f"الإصدار {version} غير موجود لـ {task}/{variant}",
            },
        )
    return ModelVersionResponse(**v.to_dict())


@router.post(
    "/versions",
    response_model=ModelVersionResponse,
    summary="Register new version",
    description="Register a new model version in the registry.",
)
async def register_version(
    request: RegisterVersionRequest,
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> ModelVersionResponse:
    """Register a new model version."""
    try:
        stage = ModelStage(request.stage)
    except ValueError:
        stage = ModelStage.DEVELOPMENT

    metrics = None
    if request.metrics:
        metrics = ModelMetrics(
            accuracy=request.metrics.accuracy,
            precision=request.metrics.precision,
            recall=request.metrics.recall,
            f1_score=request.metrics.f1_score,
            map50=request.metrics.map50,
            map50_95=request.metrics.map50_95,
            inference_time_ms=request.metrics.inference_time_ms,
            memory_mb=request.metrics.memory_mb,
        )

    version = registry.register_version(
        task=request.task,
        variant=request.variant,
        version=request.version,
        file_path=request.file_path,
        metrics=metrics,
        description=request.description,
        description_ar=request.description_ar,
        changelog=request.changelog,
        tags=request.tags,
        stage=stage,
        activate=request.activate,
    )

    logger.info(
        "model_version_registered",
        task=request.task,
        variant=request.variant,
        version=request.version,
    )

    return ModelVersionResponse(**version.to_dict())


@router.post(
    "/versions/{task}/{variant}/{version}/activate",
    summary="Activate version",
    description="Activate a specific model version.",
)
async def activate_version(
    task: str,
    variant: str,
    version: str,
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Activate a specific version."""
    success = registry.activate_version(task, variant, version)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Activation failed",
                "message": f"Could not activate version {version}",
                "message_ar": f"فشل تفعيل الإصدار {version}",
            },
        )

    logger.info(
        "model_version_activated",
        task=task,
        variant=variant,
        version=version,
    )

    return {
        "status": "success",
        "message": f"Version {version} activated",
        "message_ar": f"تم تفعيل الإصدار {version}",
        "task": task,
        "variant": variant,
        "version": version,
    }


@router.post(
    "/versions/{task}/{variant}/rollback",
    summary="Rollback to previous version",
    description="Rollback to a previous model version.",
)
async def rollback_version(
    task: str,
    variant: str,
    to_version: str | None = Query(default=None, description="Specific version to rollback to"),
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Rollback to a previous version."""
    rolled_back = registry.rollback(task, variant, to_version)

    if not rolled_back:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Rollback failed",
                "message": "No version available for rollback",
                "message_ar": "لا يوجد إصدار متاح للتراجع",
            },
        )

    logger.info(
        "model_rollback",
        task=task,
        variant=variant,
        rolled_back_to=rolled_back.version,
    )

    return {
        "status": "success",
        "message": f"Rolled back to version {rolled_back.version}",
        "message_ar": f"تم التراجع إلى الإصدار {rolled_back.version}",
        "version": rolled_back.to_dict(),
    }


@router.put(
    "/versions/{task}/{variant}/{version}/metrics",
    summary="Update version metrics",
    description="Update performance metrics for a model version.",
)
async def update_version_metrics(
    task: str,
    variant: str,
    version: str,
    metrics: ModelMetricsUpdate,
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Update metrics for a version."""
    model_metrics = ModelMetrics(
        accuracy=metrics.accuracy,
        precision=metrics.precision,
        recall=metrics.recall,
        f1_score=metrics.f1_score,
        map50=metrics.map50,
        map50_95=metrics.map50_95,
        inference_time_ms=metrics.inference_time_ms,
        memory_mb=metrics.memory_mb,
    )

    success = registry.update_metrics(task, variant, version, model_metrics)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Update failed",
                "message": f"Version {version} not found",
                "message_ar": f"الإصدار {version} غير موجود",
            },
        )

    return {
        "status": "success",
        "message": "Metrics updated",
        "message_ar": "تم تحديث المقاييس",
        "metrics": model_metrics.to_dict(),
    }


@router.post(
    "/versions/{task}/{variant}/{version}/deprecate",
    summary="Deprecate version",
    description="Mark a model version as deprecated.",
)
async def deprecate_version(
    task: str,
    variant: str,
    version: str,
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Deprecate a version."""
    success = registry.deprecate_version(task, variant, version)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Deprecation failed",
                "message": f"Version {version} not found",
                "message_ar": f"الإصدار {version} غير موجود",
            },
        )

    logger.info(
        "model_version_deprecated",
        task=task,
        variant=variant,
        version=version,
    )

    return {
        "status": "success",
        "message": f"Version {version} deprecated",
        "message_ar": f"تم إيقاف الإصدار {version}",
    }


@router.post(
    "/versions/{task}/{variant}/{version}/promote",
    summary="Promote to production",
    description="Promote a model version to production stage.",
)
async def promote_to_production(
    task: str,
    variant: str,
    version: str,
    registry: ModelVersionRegistry = Depends(get_registry),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Promote a version to production."""
    success = registry.promote_to_production(task, variant, version)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Promotion failed",
                "message": f"Version {version} not found",
                "message_ar": f"الإصدار {version} غير موجود",
            },
        )

    logger.info(
        "model_promoted_to_production",
        task=task,
        variant=variant,
        version=version,
    )

    return {
        "status": "success",
        "message": f"Version {version} promoted to production",
        "message_ar": f"تم ترقية الإصدار {version} إلى الإنتاج",
    }


@router.get(
    "/versions/{task}/{variant}/compare",
    response_model=VersionComparisonResponse,
    summary="Compare two versions",
    description="Compare metrics between two model versions.",
)
async def compare_versions(
    task: str,
    variant: str,
    version_a: str = Query(..., description="First version to compare"),
    version_b: str = Query(..., description="Second version to compare"),
    registry: ModelVersionRegistry = Depends(get_registry),
) -> VersionComparisonResponse:
    """Compare two model versions."""
    comparison = registry.compare_versions(task, variant, version_a, version_b)

    if "error" in comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Comparison failed",
                "message": comparison["error"],
                "message_ar": "فشلت المقارنة",
            },
        )

    return VersionComparisonResponse(**comparison)


@router.get(
    "/loaded",
    summary="Get loaded models",
    description="Get information about currently loaded models.",
)
async def get_loaded_models(
    manager: YOLO26ModelManager = Depends(get_manager),
    registry: ModelVersionRegistry = Depends(get_registry),
) -> list[LoadedModelInfo]:
    """Get information about loaded models."""
    loaded_keys = manager.get_loaded_models()
    result = []

    for key in loaded_keys:
        parts = key.split("_")
        if len(parts) >= 2:
            task = "_".join(parts[:-1])
            variant = parts[-1]

            active_version = registry.get_active_version(task, variant)

            result.append(
                LoadedModelInfo(
                    model_key=key,
                    task=task,
                    variant=variant,
                    loaded=True,
                    version=active_version.version if active_version else None,
                    status=active_version.status.value if active_version else None,
                )
            )

    return result


@router.get(
    "/tasks",
    summary="Get available tasks",
    description="Get list of available model tasks.",
)
async def get_available_tasks() -> dict[str, list[str]]:
    """Get available model tasks."""
    return {
        "tasks": [task.value for task in ModelTask],
        "variants": ["n", "s", "m", "l", "x"],
        "default_variant": settings.default_model_variant,
    }


@router.post(
    "/preload",
    summary="Preload model",
    description="Preload a model into memory.",
)
async def preload_model(
    task: str,
    variant: str = Query(default="m", description="Model variant"),
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Preload a model into memory."""
    try:
        model_task = ModelTask(task)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid task",
                "message": f"Unknown task: {task}",
                "message_ar": f"مهمة غير معروفة: {task}",
            },
        )

    try:
        await manager.load_model(model_task, variant)

        logger.info(
            "model_preloaded",
            task=task,
            variant=variant,
        )

        return {
            "status": "success",
            "message": f"Model {task}/{variant} preloaded",
            "message_ar": f"تم تحميل النموذج {task}/{variant} مسبقاً",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Preload failed",
                "message": str(e),
                "message_ar": "فشل التحميل المسبق",
            },
        )


@router.post(
    "/cache/clear",
    summary="Clear model cache",
    description="Clear all cached models from memory.",
)
async def clear_model_cache(
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Clear the model cache."""
    manager.clear_cache()

    logger.info("model_cache_cleared")

    return {
        "status": "success",
        "message": "Model cache cleared",
        "message_ar": "تم مسح ذاكرة التخزين المؤقت للنماذج",
    }


@router.get(
    "/gpu",
    summary="Get GPU information",
    description="Get GPU status and memory information.",
)
async def get_gpu_info(
    manager: YOLO26ModelManager = Depends(get_manager),
) -> dict[str, Any]:
    """Get GPU information."""
    return {
        "gpu_available": manager.gpu_available,
        "device": settings.device,
        "memory": manager.gpu_memory_info,
        "half_precision": settings.half_precision,
        "tensorrt_enabled": settings.enable_tensorrt,
    }


# ---------------------------------------------------------------------------
# CONTRACT-ALIGNED ENDPOINTS
# The routes below match the path shapes declared in VISION_ENDPOINTS of the
# shared-types contracts package:
#   MODEL_INFO   = /api/v1/vision/models/{variant}/info
#   MODELS_WARMUP = /api/v1/vision/models/warmup
# The models router prefix was updated to /api/v1/vision/models so Kong can
# forward requests with strip_path: false directly to the service.
# ---------------------------------------------------------------------------


@router.get(
    "/{variant}/info",
    summary="Get model variant info",
    description=(
        "Return high-level information about a specific model variant "
        "(n / s / m / l / x), including parameter count, GPU VRAM requirement, "
        "typical latency, and the currently active version for each task."
    ),
)
async def get_variant_info(
    variant: str,
    manager: YOLO26ModelManager = Depends(get_manager),
    registry: ModelVersionRegistry = Depends(get_registry),
) -> dict[str, Any]:
    """Return variant metadata keyed by task."""
    valid_variants = {"n", "s", "m", "l", "x"}
    if variant not in valid_variants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Unknown variant '{variant}'. Valid: {sorted(valid_variants)}",
                "error_ar": "نوع النموذج غير معروف",
            },
        )

    # Static variant metadata
    variant_meta: dict[str, Any] = {
        "n": {"params_m": 3.2, "vram_mb": 512, "latency_ms": 2.2, "map50": 0.78},
        "s": {"params_m": 11.2, "vram_mb": 1024, "latency_ms": 3.6, "map50": 0.84},
        "m": {"params_m": 25.9, "vram_mb": 2048, "latency_ms": 5.5, "map50": 0.88},
        "l": {"params_m": 43.7, "vram_mb": 3072, "latency_ms": 8.3, "map50": 0.91},
        "x": {"params_m": 68.2, "vram_mb": 4096, "latency_ms": 12.5, "map50": 0.93},
    }[variant]

    # Active versions per task
    active_versions: dict[str, Any] = {}
    for task in ModelTask:
        active = registry.get_active_version(task.value, variant)
        active_versions[task.value] = active.version if active else None

    loaded_keys = manager.get_loaded_models()
    loaded_tasks = [k.rsplit("_", 1)[0] for k in loaded_keys if k.endswith(f"_{variant}")]

    return {
        "variant": variant,
        "is_default": variant == settings.default_model_variant,
        "loaded_tasks": loaded_tasks,
        "active_versions": active_versions,
        **variant_meta,
    }


@router.post(
    "/warmup",
    summary="Warm up models",
    description=(
        "Pre-load one or more task/variant combinations into GPU memory so the "
        "first real inference request is not delayed by model loading. "
        "Equivalent to the internal /preload endpoint but named to match the "
        "MODELS_WARMUP contract constant."
    ),
)
async def warmup_models(
    task: str = Query(default="pest_detection", description="Model task to warm up"),
    variant: str = Query(default="m", description="Model variant: n|s|m|l|x"),
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Warm up (pre-load) a model — contract alias for /preload."""
    try:
        model_task = ModelTask(task)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Unknown task '{task}'",
                "error_ar": "المهمة غير معروفة",
                "valid_tasks": [t.value for t in ModelTask],
            },
        )

    try:
        await manager.get_model(model_task, variant)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "Model warmup failed",
                "message": str(exc),
                "error_ar": "فشل التدفئة المسبقة للنموذج",
            },
        ) from exc

    logger.info("model_warmed_up", task=task, variant=variant)
    return {
        "status": "success",
        "task": task,
        "variant": variant,
        "message": f"Model {task}/{variant} is warm and ready",
        "message_ar": f"النموذج {task}/{variant} جاهز للاستخدام",
    }
