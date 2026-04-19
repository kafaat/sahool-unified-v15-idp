"""
Batch Processing Endpoints for YOLO26 Vision Service.

Provides batch detection endpoints for processing multiple images
efficiently with progress tracking and comprehensive responses.
"""

from __future__ import annotations

import asyncio
import io
import time
from typing import Annotated
from uuid import UUID, uuid4

import numpy as np
import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from PIL import Image
from pydantic import BaseModel, ConfigDict, Field

from src.api.schemas import (
    DISEASE_CLASSES,
    PEST_CLASSES,
    WEED_CLASSES,
    BilingualLabel,
    BoundingBox,
    DiseaseDetection,
    ImageMetadata,
    ModelVariant,
    PestDetection,
    SeverityLevel,
    WeedDetection,
)
from src.core.batch_processor import BatchJob, BatchProcessor, BatchStatus, get_batch_processor
from src.core.cache import ResultCache, get_result_cache
from src.core.config import settings
from src.core.errors import ErrorCode, ValidationError
from src.core.image_security import validate_image_upload
from src.models.yolo26_manager import (
    InferenceResult,
    ModelTask,
    YOLO26ModelManager,
    get_model_manager,
)

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


logger = structlog.get_logger(__name__)

router = APIRouter(tags=["batch"])


# =============================================================================
# Schemas
# =============================================================================


class BatchItemResult(BaseModel):
    """Result for a single item in batch."""

    model_config = ConfigDict(populate_by_name=True)

    item_id: str = Field(..., alias="itemId")
    index: int
    status: str = Field(description="success, failed")
    filename: str | None = None
    detections: list[dict] = Field(default_factory=list)
    detection_count: int = Field(default=0, alias="detectionCount")
    processing_time_ms: float = Field(default=0.0, alias="processingTimeMs")
    error: str | None = None
    error_ar: str | None = Field(default=None, alias="errorAr")


class BatchDetectionResponse(BaseModel):
    """Response for batch detection request."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(..., alias="jobId")
    status: str
    total_items: int = Field(..., alias="totalItems")
    successful_count: int = Field(..., alias="successfulCount")
    failed_count: int = Field(..., alias="failedCount")
    progress: float
    total_processing_time_ms: float = Field(..., alias="totalProcessingTimeMs")
    average_time_per_image_ms: float = Field(..., alias="averageTimePerImageMs")
    results: list[BatchItemResult]
    model_variant: ModelVariant = Field(..., alias="modelVariant")
    task: str
    created_at: float = Field(..., alias="createdAt")
    completed_at: float | None = Field(default=None, alias="completedAt")


class BatchJobStatusResponse(BaseModel):
    """Response for batch job status query."""

    model_config = ConfigDict(populate_by_name=True)

    job_id: str = Field(..., alias="jobId")
    status: str
    total_items: int = Field(..., alias="totalItems")
    successful_count: int = Field(..., alias="successfulCount")
    failed_count: int = Field(..., alias="failedCount")
    progress: float
    total_processing_time_ms: float = Field(..., alias="totalProcessingTimeMs")
    created_at: float = Field(..., alias="createdAt")
    started_at: float | None = Field(default=None, alias="startedAt")
    completed_at: float | None = Field(default=None, alias="completedAt")
    estimated_remaining_time_ms: float | None = Field(default=None, alias="estimatedRemainingTimeMs")


class BatchQueueStatusResponse(BaseModel):
    """Response for batch queue status."""

    model_config = ConfigDict(populate_by_name=True)

    queue_size: int = Field(..., alias="queueSize")
    active_jobs: int = Field(..., alias="activeJobs")
    completed_jobs: int = Field(..., alias="completedJobs")
    current_batch_size: int = Field(..., alias="currentBatchSize")
    total_processed: int = Field(..., alias="totalProcessed")
    average_throughput: float = Field(..., alias="averageThroughput")


# =============================================================================
# Dependencies
# =============================================================================


async def get_manager() -> YOLO26ModelManager:
    """Get the model manager instance."""
    return get_model_manager()


async def get_cache() -> ResultCache:
    """Get the result cache instance."""
    return get_result_cache()


async def get_processor() -> BatchProcessor:
    """Get the batch processor instance."""
    return get_batch_processor()


async def validate_and_read_images(files: list[UploadFile]) -> list[tuple[str, bytes]]:
    """
    Validate and read uploaded images.

    Delegates per-file checks to ``validate_image_upload`` (magic-byte +
    decompression-bomb + integrity). Wraps its HTTPException into the
    ``ValidationError`` type that batch endpoints already expect so that
    callers keep receiving the structured batch error payload.
    """
    images: list[tuple[str, bytes]] = []
    for file in files:
        try:
            content = await validate_image_upload(file)
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
            if exc.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
                raise ValidationError(
                    code=ErrorCode.IMAGE_TOO_LARGE,
                    message_params={"max_size": settings.max_upload_size_mb},
                    details=f"File '{file.filename}' exceeds size limit",
                ) from exc
            raise ValidationError(
                code=ErrorCode.INVALID_IMAGE_FORMAT,
                details=f"File '{file.filename}': {detail.get('message', 'invalid image')}",
            ) from exc

        images.append((file.filename or f"image_{len(images)}", content))

    return images


def get_image_metadata(image_bytes: bytes) -> ImageMetadata:
    """Extract image metadata from bytes."""
    img = Image.open(io.BytesIO(image_bytes))
    return ImageMetadata(
        width=img.width,
        height=img.height,
        channels=len(img.getbands()),
        format=img.format,
    )


def calculate_severity(confidence: float, area_ratio: float = 0.0) -> SeverityLevel:
    """Calculate severity level based on confidence and affected area."""
    score = confidence * 0.6 + area_ratio * 0.4

    if score >= 0.8:
        return SeverityLevel.CRITICAL
    elif score >= 0.6:
        return SeverityLevel.HIGH
    elif score >= 0.4:
        return SeverityLevel.MEDIUM
    elif score >= 0.2:
        return SeverityLevel.LOW
    else:
        return SeverityLevel.NONE


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/detect/pest",
    response_model=BatchDetectionResponse,
    response_model_by_alias=True,
    summary="Batch pest detection",
    description="Detect pests in multiple images with efficient batch processing.",
)
async def batch_detect_pests(
    files: Annotated[list[UploadFile], File(description="Image files to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    use_cache: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
    cache: ResultCache = Depends(get_cache),
    processor: BatchProcessor = Depends(get_processor),
    current_user: User = Depends(get_current_user),
) -> BatchDetectionResponse:
    """
    Batch detect pests in multiple agricultural images.

    Efficiently processes multiple images using GPU batching.
    Supports caching for repeated detections.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "batch_pest_detection_request",
        request_id=str(request_id),
        file_count=len(files),
        model_variant=model_variant.value,
    )

    try:
        # Validate and read images
        images = await validate_and_read_images(files)

        # Check cache for each image
        cached_results = {}
        images_to_process = []

        if use_cache:
            for i, (filename, image_bytes) in enumerate(images):
                cached = await cache.get(
                    image_bytes,
                    task="pest_detection",
                    variant=model_variant.value,
                    confidence=confidence_threshold,
                    iou=iou_threshold,
                    image_size=image_size,
                )
                if cached:
                    cached_results[i] = cached
                else:
                    images_to_process.append((i, filename, image_bytes))
        else:
            images_to_process = [(i, fn, ib) for i, (fn, ib) in enumerate(images)]

        # Process non-cached images
        results: list[BatchItemResult] = [None] * len(images)

        # Fill in cached results
        for idx, cached_data in cached_results.items():
            filename = images[idx][0]
            results[idx] = BatchItemResult(
                item_id=str(uuid4()),
                index=idx,
                status="success",
                filename=filename,
                detections=cached_data.get("detections", []),
                detection_count=cached_data.get("count", 0),
                processing_time_ms=0.0,  # Cached
            )

        # Process remaining images
        if images_to_process:
            for idx, filename, image_bytes in images_to_process:
                try:
                    item_start = time.perf_counter()
                    image_metadata = get_image_metadata(image_bytes)

                    # Run inference
                    result: InferenceResult = await manager.predict(
                        task=ModelTask.PEST_DETECTION,
                        image=image_bytes,
                        variant=model_variant.value,
                        conf=confidence_threshold,
                        iou=iou_threshold,
                        max_det=max_detections,
                        imgsz=image_size,
                    )

                    # Process detections
                    detections = []
                    for i in range(result.count):
                        class_id = int(result.class_ids[i])
                        confidence = float(result.scores[i])
                        box = result.boxes[i]

                        label = PEST_CLASSES.get(
                            class_id,
                            BilingualLabel(en="Unknown Pest", ar="آفة غير معروفة"),
                        )

                        box_area = (box[2] - box[0]) * (box[3] - box[1])
                        image_area = image_metadata.width * image_metadata.height
                        area_ratio = box_area / image_area if image_area > 0 else 0
                        severity = calculate_severity(confidence, area_ratio)

                        detections.append(
                            {
                                "class_id": class_id,
                                "class_name_en": label.en,
                                "class_name_ar": label.ar,
                                "scientific_name": label.scientific_name,
                                "confidence": round(confidence, 4),
                                "bbox": {
                                    "x1": float(box[0]),
                                    "y1": float(box[1]),
                                    "x2": float(box[2]),
                                    "y2": float(box[3]),
                                },
                                "severity": severity.value,
                            }
                        )

                    item_time = (time.perf_counter() - item_start) * 1000

                    # Cache result
                    if use_cache:
                        await cache.set(
                            image_bytes,
                            task="pest_detection",
                            variant=model_variant.value,
                            confidence=confidence_threshold,
                            iou=iou_threshold,
                            image_size=image_size,
                            result={"detections": detections, "count": len(detections)},
                        )

                    results[idx] = BatchItemResult(
                        item_id=str(uuid4()),
                        index=idx,
                        status="success",
                        filename=filename,
                        detections=detections,
                        detection_count=len(detections),
                        processing_time_ms=round(item_time, 2),
                    )

                except Exception as e:
                    logger.warning(
                        "batch_item_failed",
                        index=idx,
                        filename=filename,
                        error=str(e),
                    )
                    results[idx] = BatchItemResult(
                        item_id=str(uuid4()),
                        index=idx,
                        status="failed",
                        filename=filename,
                        error=str(e),
                        error_ar="فشل معالجة الصورة",
                    )

        total_time = (time.perf_counter() - start_time) * 1000
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")

        logger.info(
            "batch_pest_detection_complete",
            request_id=str(request_id),
            total=len(files),
            successful=successful,
            failed=failed,
            cached=len(cached_results),
            processing_time_ms=round(total_time, 2),
        )

        return BatchDetectionResponse(
            job_id=str(request_id),
            status="completed",
            total_items=len(files),
            successful_count=successful,
            failed_count=failed,
            progress=100.0,
            total_processing_time_ms=round(total_time, 2),
            average_time_per_image_ms=round(total_time / len(files), 2) if files else 0,
            results=results,
            model_variant=model_variant,
            task="pest_detection",
            created_at=start_time,
            completed_at=time.perf_counter(),
        )

    except ValidationError:
        raise
    except Exception as e:
        logger.error(
            "batch_pest_detection_failed",
            request_id=str(request_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Batch detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف الدفعي",
            },
        )


@router.post(
    "/detect/disease",
    response_model=BatchDetectionResponse,
    response_model_by_alias=True,
    summary="Batch disease detection",
    description="Detect plant diseases in multiple images with efficient batch processing.",
)
async def batch_detect_diseases(
    files: Annotated[list[UploadFile], File(description="Image files to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    use_cache: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
    cache: ResultCache = Depends(get_cache),
    current_user: User = Depends(get_current_user),
) -> BatchDetectionResponse:
    """
    Batch detect plant diseases in multiple agricultural images.

    Efficiently processes multiple images using GPU batching.
    Returns disease detections with severity and treatment recommendations.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "batch_disease_detection_request",
        request_id=str(request_id),
        file_count=len(files),
        model_variant=model_variant.value,
    )

    try:
        images = await validate_and_read_images(files)
        results: list[BatchItemResult] = []

        for idx, (filename, image_bytes) in enumerate(images):
            try:
                # Check cache
                if use_cache:
                    cached = await cache.get(
                        image_bytes,
                        task="disease_detection",
                        variant=model_variant.value,
                        confidence=confidence_threshold,
                        iou=iou_threshold,
                        image_size=image_size,
                    )
                    if cached:
                        results.append(
                            BatchItemResult(
                                item_id=str(uuid4()),
                                index=idx,
                                status="success",
                                filename=filename,
                                detections=cached.get("detections", []),
                                detection_count=cached.get("count", 0),
                                processing_time_ms=0.0,
                            )
                        )
                        continue

                item_start = time.perf_counter()
                image_metadata = get_image_metadata(image_bytes)

                result: InferenceResult = await manager.predict(
                    task=ModelTask.DISEASE_DETECTION,
                    image=image_bytes,
                    variant=model_variant.value,
                    conf=confidence_threshold,
                    iou=iou_threshold,
                    max_det=max_detections,
                    imgsz=image_size,
                )

                detections = []
                for i in range(result.count):
                    class_id = int(result.class_ids[i])
                    confidence = float(result.scores[i])
                    box = result.boxes[i]

                    label = DISEASE_CLASSES.get(
                        class_id,
                        BilingualLabel(en="Unknown Disease", ar="مرض غير معروف"),
                    )

                    box_area = (box[2] - box[0]) * (box[3] - box[1])
                    image_area = image_metadata.width * image_metadata.height
                    area_ratio = box_area / image_area if image_area > 0 else 0
                    severity = calculate_severity(confidence, area_ratio)

                    detections.append(
                        {
                            "class_id": class_id,
                            "class_name_en": label.en,
                            "class_name_ar": label.ar,
                            "scientific_name": label.scientific_name,
                            "confidence": round(confidence, 4),
                            "bbox": {
                                "x1": float(box[0]),
                                "y1": float(box[1]),
                                "x2": float(box[2]),
                                "y2": float(box[3]),
                            },
                            "severity": severity.value,
                            "affected_area_percent": round(area_ratio * 100, 2),
                        }
                    )

                item_time = (time.perf_counter() - item_start) * 1000

                if use_cache:
                    await cache.set(
                        image_bytes,
                        task="disease_detection",
                        variant=model_variant.value,
                        confidence=confidence_threshold,
                        iou=iou_threshold,
                        image_size=image_size,
                        result={"detections": detections, "count": len(detections)},
                    )

                results.append(
                    BatchItemResult(
                        item_id=str(uuid4()),
                        index=idx,
                        status="success",
                        filename=filename,
                        detections=detections,
                        detection_count=len(detections),
                        processing_time_ms=round(item_time, 2),
                    )
                )

            except Exception as e:
                results.append(
                    BatchItemResult(
                        item_id=str(uuid4()),
                        index=idx,
                        status="failed",
                        filename=filename,
                        error=str(e),
                        error_ar="فشل معالجة الصورة",
                    )
                )

        total_time = (time.perf_counter() - start_time) * 1000
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")

        return BatchDetectionResponse(
            job_id=str(request_id),
            status="completed",
            total_items=len(files),
            successful_count=successful,
            failed_count=failed,
            progress=100.0,
            total_processing_time_ms=round(total_time, 2),
            average_time_per_image_ms=round(total_time / len(files), 2) if files else 0,
            results=results,
            model_variant=model_variant,
            task="disease_detection",
            created_at=start_time,
            completed_at=time.perf_counter(),
        )

    except ValidationError:
        raise
    except Exception as e:
        logger.error("batch_disease_detection_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Batch detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف الدفعي",
            },
        )


@router.get(
    "/status",
    response_model=BatchQueueStatusResponse,
    response_model_by_alias=True,
    summary="Get batch queue status",
    description="Get the current status of the batch processing queue.",
)
async def get_queue_status(
    processor: BatchProcessor = Depends(get_processor),
) -> BatchQueueStatusResponse:
    """Get batch processing queue status."""
    status_info = processor.get_queue_status()

    return BatchQueueStatusResponse(
        queue_size=status_info["queue_size"],
        active_jobs=status_info["active_jobs"],
        completed_jobs=status_info["completed_jobs"],
        current_batch_size=status_info["current_batch_size"],
        total_processed=status_info["total_processed"],
        average_throughput=round(status_info["average_throughput"], 2),
    )


@router.get(
    "/performance",
    summary="Get batch performance statistics",
    description="Get performance statistics for batch processing.",
)
async def get_performance_stats(
    processor: BatchProcessor = Depends(get_processor),
) -> dict:
    """Get batch processing performance statistics."""
    return processor.get_performance_stats()


@router.get(
    "/cache/stats",
    summary="Get cache statistics",
    description="Get caching statistics for batch processing.",
)
async def get_cache_stats(
    cache: ResultCache = Depends(get_cache),
) -> dict:
    """Get cache statistics."""
    return cache.get_stats()


@router.post(
    "/cache/clear",
    summary="Clear result cache",
    description="Clear all cached inference results.",
)
async def clear_cache(
    cache: ResultCache = Depends(get_cache),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Clear the result cache."""
    await cache.invalidate()
    return {
        "status": "success",
        "message": "Cache cleared successfully",
        "message_ar": "تم مسح ذاكرة التخزين المؤقت بنجاح",
    }
