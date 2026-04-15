"""
Analysis endpoints for YOLO26 Vision Service.

Provides endpoints for plant counting, ripeness classification,
leaf segmentation, and object tracking.
"""

import base64
import io
import math
import time
from collections import defaultdict
from typing import Annotated
from uuid import uuid4

import numpy as np
import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from PIL import Image

from src.api.schemas import (
    RIPENESS_LABELS,
    BoundingBox,
    ImageMetadata,
    LeafSegment,
    LeafSegmentationResponse,
    ModelVariant,
    ObjectTrackingResponse,
    PlantCountResponse,
    RipenessClassificationResponse,
    RipenessResult,
    RipenessStage,
    TrackedObject,
)
from src.core.config import settings
from src.events import VisionEventPublisher
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


def _get_event_publisher(request) -> VisionEventPublisher | None:
    """Get event publisher from app state if NATS is connected."""
    nc = getattr(request.app.state, "nc", None)
    nats_connected = getattr(request.app.state, "nats_connected", False)
    if nc and nats_connected:
        return VisionEventPublisher(nc)
    return None


router = APIRouter(prefix="/api/v1", tags=["analysis"])


# =============================================================================
# Dependencies
# =============================================================================


async def get_manager() -> YOLO26ModelManager:
    """Get the model manager instance."""
    return get_model_manager()


async def validate_image(file: UploadFile) -> bytes:
    """Validate and read uploaded image."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid file type",
                "message": "File must be an image (JPEG, PNG, WebP, etc.)",
                "message_ar": "يجب أن يكون الملف صورة (JPEG، PNG، WebP، إلخ)",
            },
        )

    content = await file.read()

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "File too large",
                "message": f"Maximum file size is {settings.max_upload_size_mb}MB",
                "message_ar": f"الحد الأقصى لحجم الملف هو {settings.max_upload_size_mb} ميجابايت",
            },
        )

    return content


def get_image_metadata(image_bytes: bytes) -> ImageMetadata:
    """Extract image metadata from bytes."""
    img = Image.open(io.BytesIO(image_bytes))
    return ImageMetadata(
        width=img.width,
        height=img.height,
        channels=len(img.getbands()),
        format=img.format,
    )


def generate_density_map(
    boxes: np.ndarray,
    image_shape: tuple[int, int],
    grid_size: int = 32,
) -> tuple[str, list[list[int]]]:
    """
    Generate a density heatmap from detection boxes.

    Args:
        boxes: Array of bounding boxes (N, 4) in xyxy format
        image_shape: (height, width) of original image
        grid_size: Size of each grid cell

    Returns:
        Tuple of (base64 encoded heatmap image, grid counts)
    """
    height, width = image_shape
    grid_h = math.ceil(height / grid_size)
    grid_w = math.ceil(width / grid_size)

    # Count plants per grid cell
    grid_counts = [[0 for _ in range(grid_w)] for _ in range(grid_h)]

    for box in boxes:
        # Use center of bounding box
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2

        grid_x = min(int(cx / grid_size), grid_w - 1)
        grid_y = min(int(cy / grid_size), grid_h - 1)

        if 0 <= grid_x < grid_w and 0 <= grid_y < grid_h:
            grid_counts[grid_y][grid_x] += 1

    # Create heatmap visualization
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap

        # Create custom colormap (green to yellow to red)
        colors = ["#006400", "#32CD32", "#FFFF00", "#FF8C00", "#FF0000"]
        cmap = LinearSegmentedColormap.from_list("density", colors)

        fig, ax = plt.subplots(figsize=(10, 10))
        grid_array = np.array(grid_counts)

        im = ax.imshow(grid_array, cmap=cmap, interpolation="bilinear", aspect="auto")
        ax.set_title("Plant Density Map | خريطة كثافة النباتات", fontsize=14)
        ax.set_xlabel("Grid X")
        ax.set_ylabel("Grid Y")

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Plants per cell | نباتات لكل خلية")

        # Save to bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8"), grid_counts

    except Exception as e:
        logger.warning("density_map_generation_failed", error=str(e))
        return "", grid_counts


def estimate_ripeness_stage(class_probs: np.ndarray | None, class_id: int) -> tuple[RipenessStage, float]:
    """
    Estimate ripeness stage from classification probabilities.

    Args:
        class_probs: Class probabilities from classification model
        class_id: Detected class ID

    Returns:
        Tuple of (RipenessStage, confidence)
    """
    if class_probs is not None and len(class_probs) > 0:
        # Map class indices to ripeness stages
        stage_mapping = {
            0: RipenessStage.UNRIPE,
            1: RipenessStage.EARLY_RIPE,
            2: RipenessStage.HALF_RIPE,
            3: RipenessStage.RIPE,
            4: RipenessStage.OVERRIPE,
        }
        stage = stage_mapping.get(class_id, RipenessStage.HALF_RIPE)
        confidence = float(class_probs[class_id]) if class_id < len(class_probs) else 0.5
        return stage, confidence

    # Default based on class_id
    stages = list(RipenessStage)
    stage_idx = min(class_id, len(stages) - 1)
    return stages[stage_idx], 0.5


def estimate_days_to_optimal(stage: RipenessStage, fruit_type: str | None) -> int | None:
    """Estimate days to optimal ripeness based on stage and fruit type."""
    # Base estimates (can be refined per fruit type)
    base_days = {
        RipenessStage.UNRIPE: 10,
        RipenessStage.EARLY_RIPE: 5,
        RipenessStage.HALF_RIPE: 2,
        RipenessStage.RIPE: 0,
        RipenessStage.OVERRIPE: -2,  # Past optimal
    }

    # Adjust for fruit type
    fruit_adjustments = {
        "tomato": 0.8,
        "date": 1.5,
        "grape": 0.7,
        "citrus": 1.2,
        "apple": 1.0,
        "mango": 1.3,
    }

    base = base_days.get(stage, 0)
    if base < 0:
        return None  # Already past optimal

    adjustment = fruit_adjustments.get(fruit_type.lower() if fruit_type else "", 1.0)
    return max(0, int(base * adjustment))


def calculate_ripeness_score(stage: RipenessStage) -> float:
    """Calculate numeric ripeness score (0=unripe, 100=overripe)."""
    scores = {
        RipenessStage.UNRIPE: 10.0,
        RipenessStage.EARLY_RIPE: 30.0,
        RipenessStage.HALF_RIPE: 50.0,
        RipenessStage.RIPE: 80.0,
        RipenessStage.OVERRIPE: 100.0,
    }
    return scores.get(stage, 50.0)


def create_tracking_visualization(
    image_bytes: bytes,
    tracked_objects: list[TrackedObject],
) -> str:
    """Create visualization with tracked objects and IDs."""
    try:
        from PIL import ImageDraw, ImageFont

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        # Color palette for different track IDs
        colors = [
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#FF00FF",
            "#00FFFF",
            "#FFA500",
            "#800080",
            "#008000",
            "#FFC0CB",
        ]

        for obj in tracked_objects:
            color = colors[obj.track_id % len(colors)]
            bbox = obj.bbox

            # Draw bounding box
            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline=color,
                width=3,
            )

            # Draw track ID label
            label = f"ID: {obj.track_id}"
            text_bbox = draw.textbbox((bbox.x1, bbox.y1 - 22), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text((bbox.x1, bbox.y1 - 22), label, fill="white", font=font)

            # Draw velocity vector if available
            if obj.velocity:
                cx, cy = bbox.center
                vx, vy = obj.velocity
                # Scale velocity for visualization
                scale = 5
                draw.line(
                    [cx, cy, cx + vx * scale, cy + vy * scale],
                    fill=color,
                    width=2,
                )

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("tracking_visualization_failed", error=str(e))
        return ""


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/count/plants",
    response_model=PlantCountResponse,
    response_model_by_alias=True,
    summary="Count plants in agricultural images",
    description="Count individual plants with optional density map generation.",
)
async def count_plants(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.3,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    generate_density_map_flag: Annotated[bool, Query(alias="generate_density_map")] = True,
    grid_size: Annotated[int, Query(ge=8, le=128)] = 32,
    count_per_unit_area: bool = True,
    gsd_meters: Annotated[float | None, Query(gt=0.0, description="Ground sampling distance in meters/pixel")] = None,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> PlantCountResponse:
    """
    Count plants in agricultural images.

    Features:
    - Accurate plant counting using YOLO26 detection
    - Density map generation showing plant distribution
    - Plants per square meter calculation (requires GSD)
    - Grid-based counting for field analysis

    Args:
        file: Image file to analyze
        confidence_threshold: Minimum detection confidence
        model_variant: Model size (n, s, m, l, x)
        generate_density_map_flag: Generate density heatmap
        grid_size: Grid cell size for density map
        count_per_unit_area: Calculate plants/sqm
        gsd_meters: Ground sampling distance for area calculation
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "plant_count_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.PLANT_COUNTING,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=0.45,
            max_det=1000,  # Higher limit for counting
            imgsz=640,
        )

        total_count = result.count

        # Calculate density per square meter
        density_per_sqm = None
        average_spacing = None

        if gsd_meters and count_per_unit_area:
            # Calculate image area in square meters
            image_area_sqm = (image_metadata.width * gsd_meters) * (image_metadata.height * gsd_meters)
            if image_area_sqm > 0:
                density_per_sqm = total_count / image_area_sqm

                # Estimate average spacing
                if total_count > 1:
                    average_spacing = math.sqrt(image_area_sqm / total_count)

        # Generate density map
        density_map_base64 = None
        grid_counts = None

        if generate_density_map_flag and result.count > 0:
            density_map_base64, grid_counts = generate_density_map(
                result.boxes,
                (image_metadata.height, image_metadata.width),
                grid_size,
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        logger.info(
            "plant_count_complete",
            request_id=str(request_id),
            total_count=total_count,
            density_per_sqm=density_per_sqm,
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS event
        publisher = _get_event_publisher(request)
        if publisher and total_count > 0:
            await publisher.publish_plant_count_completed(
                request_id=request_id,
                total_count=total_count,
                processing_time_ms=processing_time,
                model_variant=model_variant.value,
                density_per_sqm=round(density_per_sqm, 2) if density_per_sqm else None,
            )

        return PlantCountResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            total_count=total_count,
            density_per_sqm=round(density_per_sqm, 2) if density_per_sqm else None,
            density_map_base64=density_map_base64,
            grid_counts=grid_counts,
            average_spacing_m=round(average_spacing, 3) if average_spacing else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("plant_count_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Plant counting failed",
                "message": str(e),
                "message_ar": "فشل عد النباتات",
            },
        )


@router.post(
    "/classify/ripeness",
    response_model=RipenessClassificationResponse,
    response_model_by_alias=True,
    summary="Classify fruit ripeness",
    description="Classify fruit ripeness into 5 stages with bilingual labels.",
)
async def classify_ripeness(
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.3,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    fruit_type: Annotated[str | None, Query(description="Type of fruit (tomato, date, grape, etc.)")] = None,
    return_stage_distribution: bool = True,
    return_visualization: bool = False,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> RipenessClassificationResponse:
    """
    Classify fruit ripeness in agricultural images.

    Ripeness stages (5 levels):
    1. Unripe (غير ناضج) - Green, firm
    2. Early Ripe (بداية النضج) - Beginning to color
    3. Half Ripe (نصف ناضج) - Partial coloring
    4. Ripe (ناضج) - Optimal for harvest
    5. Overripe (مفرط النضج) - Past optimal

    Returns bilingual labels, harvest readiness percentage,
    and optional days-to-optimal estimation.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "ripeness_classification_request",
        request_id=str(request_id),
        filename=file.filename,
        fruit_type=fruit_type,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Run detection to find fruits first
        detection_result: InferenceResult = await manager.predict(
            task=ModelTask.RIPENESS_CLASSIFICATION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=0.45,
            max_det=300,
            imgsz=640,
        )

        # Process results
        results: list[RipenessResult] = []
        stage_distribution: dict[str, int] = {stage.value: 0 for stage in RipenessStage}
        total_ripeness_score = 0.0

        for i in range(detection_result.count):
            class_id = int(detection_result.class_ids[i])
            confidence = float(detection_result.scores[i])
            box = detection_result.boxes[i]

            # Determine ripeness stage
            stage, stage_confidence = estimate_ripeness_stage(
                detection_result.class_probs,
                class_id,
            )

            # Get bilingual label
            label = RIPENESS_LABELS.get(stage)

            # Estimate days to optimal
            days_to_optimal = estimate_days_to_optimal(stage, fruit_type)

            # Calculate ripeness score
            ripeness_score = calculate_ripeness_score(stage)
            total_ripeness_score += ripeness_score

            # Update distribution
            stage_distribution[stage.value] += 1

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            result = RipenessResult(
                bbox=bbox,
                stage=stage,
                stage_label_en=label.en if label else stage.value,
                stage_label_ar=label.ar if label else stage.value,
                confidence=min(confidence, stage_confidence),
                days_to_optimal=days_to_optimal,
            )
            results.append(result)

        processing_time = (time.perf_counter() - start_time) * 1000

        # Calculate averages
        total_count = len(results)
        avg_ripeness = total_ripeness_score / total_count if total_count > 0 else 0.0

        # Calculate harvest readiness (ripe + overripe)
        harvest_ready = stage_distribution.get(RipenessStage.RIPE.value, 0)
        harvest_ready += stage_distribution.get(RipenessStage.OVERRIPE.value, 0)
        harvest_readiness = (harvest_ready / total_count * 100) if total_count > 0 else 0.0

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and results:
            visualization_base64 = _create_ripeness_visualization(image_bytes, results)

        logger.info(
            "ripeness_classification_complete",
            request_id=str(request_id),
            total_count=total_count,
            harvest_readiness=round(harvest_readiness, 1),
            processing_time_ms=round(processing_time, 2),
        )

        return RipenessClassificationResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            results=results,
            total_count=total_count,
            stage_distribution=stage_distribution if return_stage_distribution else {},
            average_ripeness_score=round(avg_ripeness, 1),
            harvest_readiness_percent=round(harvest_readiness, 1),
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("ripeness_classification_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Ripeness classification failed",
                "message": str(e),
                "message_ar": "فشل تصنيف النضج",
            },
        )


def _create_ripeness_visualization(image_bytes: bytes, results: list[RipenessResult]) -> str:
    """Create visualization with ripeness colors."""
    try:
        from PIL import ImageDraw, ImageFont

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

        # Colors for each ripeness stage
        stage_colors = {
            RipenessStage.UNRIPE: "#00FF00",  # Green
            RipenessStage.EARLY_RIPE: "#90EE90",  # Light green
            RipenessStage.HALF_RIPE: "#FFD700",  # Gold
            RipenessStage.RIPE: "#FFA500",  # Orange
            RipenessStage.OVERRIPE: "#FF4500",  # Red-orange
        }

        for result in results:
            color = stage_colors.get(result.stage, "#FFFFFF")
            bbox = result.bbox

            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline=color,
                width=2,
            )

            label = f"{result.stage_label_en} ({result.confidence:.0%})"
            text_bbox = draw.textbbox((bbox.x1, bbox.y1 - 20), label, font=font)
            draw.rectangle(text_bbox, fill=color)
            draw.text((bbox.x1, bbox.y1 - 20), label, fill="black", font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("ripeness_visualization_failed", error=str(e))
        return ""


@router.post(
    "/segment/leaf",
    response_model=LeafSegmentationResponse,
    response_model_by_alias=True,
    summary="Segment leaves for area measurement",
    description="Segment individual leaves with area calculation and health indicators.",
)
async def segment_leaves(
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.5,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    return_mask: bool = True,
    calculate_area: bool = True,
    gsd_meters: Annotated[
        float | None, Query(gt=0.0, description="Ground sampling distance for area calculation")
    ] = None,
    return_visualization: bool = False,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> LeafSegmentationResponse:
    """
    Segment leaves in agricultural images for area measurement.

    Features:
    - Individual leaf segmentation using instance segmentation
    - Leaf area calculation in pixels and square meters (with GSD)
    - Health indicator based on color analysis
    - Leaf Area Index (LAI) estimation

    Applications:
    - Growth monitoring
    - Disease assessment
    - Fertilizer application planning
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "leaf_segmentation_request",
        request_id=str(request_id),
        filename=file.filename,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Run segmentation inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.LEAF_SEGMENTATION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=0.45,
            max_det=300,
            imgsz=640,
            retina_masks=True,
        )

        # Process segments
        segments: list[LeafSegment] = []
        total_area_pixels = 0
        total_area_sqm = 0.0

        for i in range(result.count):
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Calculate area from mask if available
            area_pixels = 0
            perimeter_pixels = None

            if result.masks is not None and i < len(result.masks):
                mask = result.masks[i]
                area_pixels = int(np.sum(mask > 0.5))

                # Calculate perimeter (approximate)
                try:
                    from scipy import ndimage

                    binary_mask = (mask > 0.5).astype(np.uint8)
                    perimeter_pixels = int(ndimage.morphology.binary_erosion(binary_mask).sum())
                    perimeter_pixels = int(np.sum(binary_mask) - perimeter_pixels) * 4
                except Exception:
                    pass
            else:
                # Estimate from bounding box
                area_pixels = int((box[2] - box[0]) * (box[3] - box[1]))

            total_area_pixels += area_pixels

            # Calculate area in square meters
            area_sqm = None
            if gsd_meters and calculate_area:
                area_sqm = area_pixels * (gsd_meters**2)
                total_area_sqm += area_sqm

            # Estimate health indicator (placeholder - would use color analysis)
            health_indicator = min(1.0, confidence * 1.2)  # Simplified

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            segment = LeafSegment(
                segment_id=i,
                bbox=bbox,
                area_pixels=area_pixels,
                area_sqm=round(area_sqm, 6) if area_sqm else None,
                perimeter_pixels=perimeter_pixels,
                confidence=confidence,
                health_indicator=round(health_indicator, 2),
            )
            segments.append(segment)

        processing_time = (time.perf_counter() - start_time) * 1000

        # Estimate LAI (Leaf Area Index)
        lai = None
        if gsd_meters and total_area_sqm > 0:
            ground_area_sqm = (image_metadata.width * gsd_meters) * (image_metadata.height * gsd_meters)
            if ground_area_sqm > 0:
                lai = total_area_sqm / ground_area_sqm

        # Generate mask visualization
        mask_base64 = None
        visualization_base64 = None

        if return_mask and result.masks is not None:
            mask_base64 = _create_mask_visualization(image_bytes, result.masks)

        if return_visualization:
            visualization_base64 = _create_segmentation_visualization(image_bytes, segments, result.masks)

        logger.info(
            "leaf_segmentation_complete",
            request_id=str(request_id),
            total_leaves=len(segments),
            total_area_pixels=total_area_pixels,
            lai=lai,
            processing_time_ms=round(processing_time, 2),
        )

        return LeafSegmentationResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            segments=segments,
            total_leaves=len(segments),
            total_leaf_area_pixels=total_area_pixels,
            total_leaf_area_sqm=round(total_area_sqm, 4) if total_area_sqm > 0 else None,
            leaf_area_index=round(lai, 2) if lai else None,
            mask_base64=mask_base64,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("leaf_segmentation_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Leaf segmentation failed",
                "message": str(e),
                "message_ar": "فشل تجزئة الأوراق",
            },
        )


def _create_mask_visualization(image_bytes: bytes, masks: np.ndarray) -> str:
    """Create combined mask visualization."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        img_array = np.array(img)

        # Create colored overlay for each mask
        colors = [
            [255, 0, 0, 128],
            [0, 255, 0, 128],
            [0, 0, 255, 128],
            [255, 255, 0, 128],
            [255, 0, 255, 128],
            [0, 255, 255, 128],
        ]

        overlay = np.zeros((img_array.shape[0], img_array.shape[1], 4), dtype=np.uint8)

        for i, mask in enumerate(masks):
            color = colors[i % len(colors)]
            # Resize mask to image size if needed
            if mask.shape != (img_array.shape[0], img_array.shape[1]):
                mask_img = Image.fromarray((mask * 255).astype(np.uint8))
                mask_img = mask_img.resize((img_array.shape[1], img_array.shape[0]))
                mask = np.array(mask_img) / 255.0

            mask_binary = mask > 0.5
            overlay[mask_binary] = color

        # Blend with original
        result = Image.alpha_composite(img, Image.fromarray(overlay))

        buffer = io.BytesIO()
        result.convert("RGB").save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("mask_visualization_failed", error=str(e))
        return ""


def _create_segmentation_visualization(
    image_bytes: bytes,
    segments: list[LeafSegment],
    masks: np.ndarray | None,
) -> str:
    """Create segmentation visualization with bboxes and labels."""
    try:
        from PIL import ImageDraw, ImageFont

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except Exception:
            font = ImageFont.load_default()

        for segment in segments:
            color = "#00FF00" if segment.health_indicator and segment.health_indicator > 0.7 else "#FFFF00"
            bbox = segment.bbox

            draw.rectangle(
                [bbox.x1, bbox.y1, bbox.x2, bbox.y2],
                outline=color,
                width=2,
            )

            label = f"#{segment.segment_id} | {segment.area_pixels}px"
            if segment.area_sqm:
                label += f" | {segment.area_sqm:.4f}m²"

            draw.text((bbox.x1, bbox.y2 + 2), label, fill=color, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("segmentation_visualization_failed", error=str(e))
        return ""


@router.post(
    "/track/objects",
    response_model=ObjectTrackingResponse,
    response_model_by_alias=True,
    summary="Track objects with ID persistence",
    description="Track objects across video frames with persistent IDs.",
)
async def track_objects(
    file: Annotated[UploadFile, File(description="Video frame to analyze")],
    tracker_id: Annotated[str, Query(description="Unique tracker session ID")] = "default",
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.3,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    tracking_method: Annotated[str, Query(description="Tracking algorithm")] = "bytetrack",
    persist_ids: bool = True,
    track_buffer: Annotated[int, Query(ge=1, le=300)] = 30,
    frame_number: Annotated[int, Query(ge=0)] = 0,
    return_visualization: bool = False,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> ObjectTrackingResponse:
    """
    Track objects across video frames with persistent IDs.

    Features:
    - ByteTrack or BoT-SORT tracking algorithms
    - Persistent object IDs across frames
    - Velocity estimation for movement tracking
    - Track history and lost track handling

    Use cases:
    - Animal monitoring (livestock counting)
    - Equipment tracking
    - Pest movement analysis
    - Worker safety monitoring
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "object_tracking_request",
        request_id=str(request_id),
        tracker_id=tracker_id,
        frame_number=frame_number,
        tracking_method=tracking_method,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Map tracking method to config
        tracker_config = {
            "bytetrack": "bytetrack.yaml",
            "botsort": "botsort.yaml",
        }
        tracker = tracker_config.get(tracking_method.lower(), "bytetrack.yaml")

        # Run tracking inference
        result: InferenceResult = await manager.predict_with_tracking(
            task=ModelTask.GENERAL_DETECTION,
            image=image_bytes,
            tracker_id=tracker_id,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=0.45,
            max_det=300,
            imgsz=640,
            tracker=tracker,
            persist=persist_ids,
        )

        # Process tracked objects
        tracked_objects: list[TrackedObject] = []
        active_track_ids = set()
        new_tracks = 0

        # Track history management (simple in-memory for demo)
        track_history_key = f"history_{tracker_id}"
        if not hasattr(manager, "_track_histories"):
            manager._track_histories = {}

        previous_tracks = manager._track_histories.get(track_history_key, {})

        for i in range(result.count):
            box = result.boxes[i]
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])

            # Get track ID
            track_id = int(result.track_ids[i]) if result.track_ids is not None and i < len(result.track_ids) else i
            active_track_ids.add(track_id)

            # Check if new track
            is_new = track_id not in previous_tracks
            if is_new:
                new_tracks += 1

            # Calculate velocity from previous position
            velocity = None
            track_length = 1
            if track_id in previous_tracks:
                prev = previous_tracks[track_id]
                prev_cx = (prev["box"][0] + prev["box"][2]) / 2
                prev_cy = (prev["box"][1] + prev["box"][3]) / 2
                curr_cx = (box[0] + box[2]) / 2
                curr_cy = (box[1] + box[3]) / 2
                velocity = (curr_cx - prev_cx, curr_cy - prev_cy)
                track_length = prev.get("length", 1) + 1

            # Update history
            previous_tracks[track_id] = {
                "box": box.tolist(),
                "length": track_length,
                "frame": frame_number,
            }

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            tracked_obj = TrackedObject(
                track_id=track_id,
                class_id=class_id,
                class_name=f"object_{class_id}",
                bbox=bbox,
                confidence=confidence,
                velocity=velocity,
                track_length=track_length,
                is_new=is_new,
            )
            tracked_objects.append(tracked_obj)

        # Clean up old tracks (beyond buffer)
        lost_tracks = 0
        for tid in list(previous_tracks.keys()):
            if tid not in active_track_ids:
                if frame_number - previous_tracks[tid].get("frame", 0) > track_buffer:
                    del previous_tracks[tid]
                    lost_tracks += 1

        # Save updated history
        manager._track_histories[track_history_key] = previous_tracks

        processing_time = (time.perf_counter() - start_time) * 1000

        # Count total unique objects
        total_unique = len(previous_tracks)

        # Generate visualization
        visualization_base64 = None
        if return_visualization and tracked_objects:
            visualization_base64 = create_tracking_visualization(image_bytes, tracked_objects)

        logger.info(
            "object_tracking_complete",
            request_id=str(request_id),
            active_tracks=len(tracked_objects),
            new_tracks=new_tracks,
            lost_tracks=lost_tracks,
            total_unique=total_unique,
            processing_time_ms=round(processing_time, 2),
        )

        return ObjectTrackingResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            frame_number=frame_number,
            tracked_objects=tracked_objects,
            active_tracks=len(tracked_objects),
            new_tracks=new_tracks,
            lost_tracks=lost_tracks,
            total_unique_objects=total_unique,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("object_tracking_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Object tracking failed",
                "message": str(e),
                "message_ar": "فشل تتبع الأجسام",
            },
        )


@router.delete(
    "/track/{tracker_id}",
    summary="Reset tracker state",
    description="Reset the tracker state for a given session ID.",
)
async def reset_tracker(
    tracker_id: str,
    manager: YOLO26ModelManager = Depends(get_manager),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Reset tracker state for a given session."""
    manager.reset_tracker(tracker_id)

    # Also clear history
    if hasattr(manager, "_track_histories"):
        history_key = f"history_{tracker_id}"
        if history_key in manager._track_histories:
            del manager._track_histories[history_key]

    logger.info("tracker_reset", tracker_id=tracker_id)

    return {
        "status": "ok",
        "message": f"Tracker '{tracker_id}' has been reset",
        "message_ar": f"تم إعادة تعيين المتتبع '{tracker_id}'",
    }
