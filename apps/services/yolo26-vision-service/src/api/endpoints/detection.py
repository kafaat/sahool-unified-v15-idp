"""
Detection endpoints for YOLO26 Vision Service.

Provides endpoints for pest detection, disease detection, and weed detection
with bilingual (Arabic/English) class names.
"""

import base64
import io
import time
from typing import Annotated
from uuid import uuid4

import numpy as np
import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from PIL import Image

from src.api.schemas import (
    DISEASE_CLASSES,
    PEST_CLASSES,
    WEED_CLASSES,
    BilingualLabel,
    BoundingBox,
    DiseaseDetection,
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
    ImageMetadata,
    ModelVariant,
    PestDetection,
    PestDetectionRequest,
    PestDetectionResponse,
    SeverityLevel,
    WeedDetection,
    WeedDetectionRequest,
    WeedDetectionResponse,
)
from src.core.config import settings
from src.events.publisher import (
    publish_disease_detection,
    publish_pest_detection,
    publish_weed_detection,
)
from src.models.yolo26_manager import (
    InferenceResult,
    ModelTask,
    YOLO26ModelManager,
    get_model_manager,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["detection"])


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


def create_visualization(
    image_bytes: bytes,
    detections: list[dict],
    class_labels: dict[int, BilingualLabel],
) -> str:
    """Create visualization with bounding boxes and return as base64."""
    try:
        from PIL import ImageDraw, ImageFont

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Try to load a font, fall back to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

        colors = {
            SeverityLevel.CRITICAL: "#FF0000",
            SeverityLevel.HIGH: "#FF6600",
            SeverityLevel.MEDIUM: "#FFCC00",
            SeverityLevel.LOW: "#00CC00",
            SeverityLevel.NONE: "#0066FF",
        }

        for det in detections:
            bbox = det["bbox"]
            severity = det.get("severity", SeverityLevel.MEDIUM)
            color = colors.get(severity, "#00FF00")
            class_id = det["class_id"]
            confidence = det["confidence"]

            # Draw bounding box
            draw.rectangle(
                [bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]],
                outline=color,
                width=2,
            )

            # Draw label
            label = class_labels.get(class_id)
            if label:
                text = f"{label.en} ({confidence:.0%})"
                text_bbox = draw.textbbox((bbox["x1"], bbox["y1"] - 20), text, font=font)
                draw.rectangle(text_bbox, fill=color)
                draw.text((bbox["x1"], bbox["y1"] - 20), text, fill="white", font=font)

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as e:
        logger.warning("visualization_failed", error=str(e))
        return ""


# =============================================================================
# Pest Detection Recommendations
# =============================================================================

PEST_RECOMMENDATIONS: dict[int, dict[str, str]] = {
    0: {  # Red Palm Weevil
        "en": "Immediately report to agricultural authorities. Apply trunk injection with imidacloprid. Install pheromone traps.",
        "ar": "أبلغ السلطات الزراعية فورًا. قم بحقن الجذع بمادة الإيميداكلوبريد. ثبّت مصائد الفرمونات.",
    },
    1: {  # Aphid
        "en": "Apply neem oil or insecticidal soap. Introduce beneficial insects like ladybugs. Remove heavily infested leaves.",
        "ar": "استخدم زيت النيم أو الصابون الحشري. أدخل حشرات نافعة مثل الدعسوقة. أزل الأوراق المصابة بشدة.",
    },
    2: {  # Whitefly
        "en": "Use yellow sticky traps. Apply insecticidal soap or neem oil. Introduce parasitic wasps (Encarsia formosa).",
        "ar": "استخدم المصائد اللاصقة الصفراء. طبق الصابون الحشري أو زيت النيم. أدخل الدبابير الطفيلية.",
    },
    3: {  # Spider Mite
        "en": "Increase humidity. Apply miticide or neem oil. Introduce predatory mites (Phytoseiulus persimilis).",
        "ar": "زد الرطوبة. طبق المبيد العنكبوتي أو زيت النيم. أدخل العث المفترس.",
    },
    4: {  # Thrips
        "en": "Use blue sticky traps. Apply spinosad or neem oil. Remove plant debris.",
        "ar": "استخدم المصائد اللاصقة الزرقاء. طبق السبينوساد أو زيت النيم. أزل بقايا النباتات.",
    },
    5: {  # Leaf Miner
        "en": "Remove and destroy affected leaves. Apply systemic insecticide. Use yellow sticky traps for adults.",
        "ar": "أزل الأوراق المصابة ودمرها. طبق مبيدًا جهازيًا. استخدم المصائد اللاصقة الصفراء للحشرات البالغة.",
    },
    6: {  # Cutworm
        "en": "Apply Bacillus thuringiensis (Bt). Create barriers around seedlings. Hand-pick at night.",
        "ar": "طبق باسيلوس ثورنجينسيس. أنشئ حواجز حول الشتلات. اجمعها يدويًا ليلًا.",
    },
    7: {  # Armyworm
        "en": "Apply Bacillus thuringiensis (Bt) or spinosad. Scout fields early morning. Remove egg masses.",
        "ar": "طبق باسيلوس ثورنجينسيس أو السبينوساد. تفقد الحقول في الصباح الباكر. أزل كتل البيض.",
    },
    11: {  # Locust
        "en": "Report to agricultural authorities immediately. Apply recommended insecticides. Coordinate with regional control programs.",
        "ar": "أبلغ السلطات الزراعية فورًا. طبق المبيدات الموصى بها. نسق مع برامج المكافحة الإقليمية.",
    },
}

# =============================================================================
# Disease Treatment Recommendations
# =============================================================================

DISEASE_TREATMENTS: dict[int, dict[str, str]] = {
    0: {  # Wheat Rust
        "en": "Apply fungicide (propiconazole or tebuconazole). Remove infected plant debris. Use resistant varieties.",
        "ar": "طبق مبيدًا فطريًا (بروبيكونازول أو تيبوكونازول). أزل بقايا النباتات المصابة. استخدم أصنافًا مقاومة.",
    },
    1: {  # Powdery Mildew
        "en": "Apply sulfur-based fungicide or potassium bicarbonate. Improve air circulation. Avoid overhead watering.",
        "ar": "طبق مبيدًا فطريًا كبريتيًا أو بيكربونات البوتاسيوم. حسّن دوران الهواء. تجنب الري العلوي.",
    },
    2: {  # Downy Mildew
        "en": "Apply copper-based fungicide. Remove infected leaves. Ensure good drainage and air circulation.",
        "ar": "طبق مبيدًا فطريًا نحاسيًا. أزل الأوراق المصابة. تأكد من الصرف الجيد ودوران الهواء.",
    },
    3: {  # Early Blight
        "en": "Apply chlorothalonil or mancozeb. Remove lower infected leaves. Mulch to prevent soil splash.",
        "ar": "طبق كلوروثالونيل أو مانكوزيب. أزل الأوراق السفلية المصابة. ضع نشارة لمنع تناثر التربة.",
    },
    4: {  # Late Blight
        "en": "Apply systemic fungicide immediately (metalaxyl). Remove and destroy infected plants. Avoid overhead irrigation.",
        "ar": "طبق مبيدًا فطريًا جهازيًا فورًا (ميتالاكسيل). أزل النباتات المصابة ودمرها. تجنب الري العلوي.",
    },
    6: {  # Fusarium Wilt
        "en": "Remove infected plants. Solarize soil. Use resistant varieties. Rotate crops for 4+ years.",
        "ar": "أزل النباتات المصابة. شمّس التربة. استخدم أصنافًا مقاومة. قم بالدورة الزراعية لأكثر من 4 سنوات.",
    },
    8: {  # Root Rot
        "en": "Improve drainage. Apply phosphonate fungicide. Avoid overwatering. Remove severely affected plants.",
        "ar": "حسّن الصرف. طبق مبيد فوسفونات فطري. تجنب الإفراط في الري. أزل النباتات المصابة بشدة.",
    },
    12: {  # Mosaic Virus
        "en": "Remove infected plants immediately. Control aphid vectors. Use virus-free seeds. Disinfect tools.",
        "ar": "أزل النباتات المصابة فورًا. كافح ناقلات المن. استخدم بذورًا خالية من الفيروس. عقم الأدوات.",
    },
    28: {  # Date Palm Bayoud
        "en": "Remove and burn infected palms. Do not replant in infected areas for 5+ years. Use resistant cultivars.",
        "ar": "أزل النخيل المصاب واحرقه. لا تعد الزراعة في المناطق المصابة لأكثر من 5 سنوات. استخدم أصنافًا مقاومة.",
    },
}


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/detect/pest",
    response_model=PestDetectionResponse,
    summary="Detect pests in agricultural images",
    description="Detect and classify agricultural pests (20+ species) with bilingual labels and treatment recommendations.",
)
async def detect_pests(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    include_recommendations: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
) -> PestDetectionResponse:
    """
    Detect pests in agricultural images.

    Supports detection of 20+ pest species including:
    - Red Palm Weevil (سوسة النخيل الحمراء)
    - Aphids (المن)
    - Whitefly (الذبابة البيضاء)
    - Spider Mites (العنكبوت الأحمر)
    - Thrips (التربس)
    - And many more...

    Returns bilingual (Arabic/English) class names, severity levels,
    and optional treatment recommendations.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "pest_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

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
        detections: list[PestDetection] = []
        severity_counts: dict[str, int] = {s.value: 0 for s in SeverityLevel}
        visualization_data = []

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = PEST_CLASSES.get(
                class_id, BilingualLabel(en="Unknown Pest", ar="آفة غير معروفة")
            )

            # Calculate severity
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            image_area = image_metadata.width * image_metadata.height
            area_ratio = box_area / image_area if image_area > 0 else 0
            severity = calculate_severity(confidence, area_ratio)
            severity_counts[severity.value] += 1

            # Get recommendations
            rec = PEST_RECOMMENDATIONS.get(class_id, {})

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = PestDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                severity=severity,
                life_stage=None,  # Would require additional model
                recommended_action_en=rec.get("en") if include_recommendations else None,
                recommended_action_ar=rec.get("ar") if include_recommendations else None,
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": severity,
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(
                image_bytes, visualization_data, PEST_CLASSES
            )

        logger.info(
            "pest_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS events for downstream services
        if detections:
            await publish_pest_detection(
                request,
                [
                    {
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                    }
                    for d in detections
                ],
                model_variant=model_variant.value,
                processing_time_ms=processing_time,
            )

        return PestDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            severity_summary=severity_counts,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("pest_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )


@router.post(
    "/detect/disease",
    response_model=DiseaseDetectionResponse,
    summary="Detect plant diseases in agricultural images",
    description="Detect and classify plant diseases (30+ diseases) with bilingual labels and treatment recommendations.",
)
async def detect_diseases(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    include_treatments: bool = True,
    calculate_affected_area: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
) -> DiseaseDetectionResponse:
    """
    Detect plant diseases in agricultural images.

    Supports detection of 30+ diseases including:
    - Wheat Rust (صدأ القمح)
    - Powdery Mildew (البياض الدقيقي)
    - Early/Late Blight (اللفحة المبكرة/المتأخرة)
    - Fusarium Wilt (ذبول الفيوزاريوم)
    - Mosaic Virus (فيروس الموزاييك)
    - Date Palm Bayoud (مرض البيوض)
    - And many more...

    Returns bilingual (Arabic/English) class names, severity levels,
    affected area estimation, and optional treatment recommendations.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "disease_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.DISEASE_DETECTION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=iou_threshold,
            max_det=max_detections,
            imgsz=image_size,
        )

        # Process detections
        detections: list[DiseaseDetection] = []
        severity_counts: dict[str, int] = {s.value: 0 for s in SeverityLevel}
        total_affected_area = 0.0
        visualization_data = []

        image_area = image_metadata.width * image_metadata.height

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = DISEASE_CLASSES.get(
                class_id, BilingualLabel(en="Unknown Disease", ar="مرض غير معروف")
            )

            # Calculate affected area
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            area_percent = (
                (box_area / image_area * 100)
                if image_area > 0 and calculate_affected_area
                else None
            )
            if area_percent:
                total_affected_area += area_percent

            # Calculate severity
            area_ratio = box_area / image_area if image_area > 0 else 0
            severity = calculate_severity(confidence, area_ratio)
            severity_counts[severity.value] += 1

            # Estimate spread risk based on disease type and severity
            spread_risk = severity
            if class_id in [4, 12, 13]:  # Late Blight, Mosaic Virus, YLCV - high spread risk
                spread_risk = (
                    SeverityLevel.HIGH
                    if severity != SeverityLevel.CRITICAL
                    else SeverityLevel.CRITICAL
                )

            # Get treatment recommendations
            treatment = DISEASE_TREATMENTS.get(class_id, {})

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = DiseaseDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                severity=severity,
                affected_area_percent=area_percent,
                spread_risk=spread_risk,
                recommended_treatment_en=treatment.get("en") if include_treatments else None,
                recommended_treatment_ar=treatment.get("ar") if include_treatments else None,
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": severity,
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Calculate overall health score (100 = healthy, 0 = severely diseased)
        health_score = max(0.0, 100.0 - total_affected_area)
        if len(detections) > 0:
            avg_severity = sum(
                [
                    1
                    if d.severity == SeverityLevel.LOW
                    else 2
                    if d.severity == SeverityLevel.MEDIUM
                    else 3
                    if d.severity == SeverityLevel.HIGH
                    else 4
                    if d.severity == SeverityLevel.CRITICAL
                    else 0
                    for d in detections
                ]
            ) / len(detections)
            health_score = max(0.0, health_score - (avg_severity * 10))

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(
                image_bytes, visualization_data, DISEASE_CLASSES
            )

        logger.info(
            "disease_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            health_score=round(health_score, 1),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS events for downstream services
        if detections:
            await publish_disease_detection(
                request,
                [
                    {
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                        "affected_area_percentage": d.affected_area_percent,
                    }
                    for d in detections
                ],
                model_variant=model_variant.value,
                processing_time_ms=processing_time,
            )

        return DiseaseDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            overall_health_score=round(health_score, 1),
            severity_summary=severity_counts,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("disease_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )


@router.post(
    "/detect/weed",
    response_model=WeedDetectionResponse,
    summary="Detect weeds in agricultural images",
    description="Detect and classify weeds with bilingual labels and coverage estimation.",
)
async def detect_weeds(
    request: Request,
    file: Annotated[UploadFile, File(description="Image file to analyze")],
    confidence_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.25,
    iou_threshold: Annotated[float, Query(ge=0.0, le=1.0)] = 0.45,
    model_variant: ModelVariant = ModelVariant.MEDIUM,
    max_detections: Annotated[int, Query(ge=1, le=1000)] = 300,
    image_size: Annotated[int, Query(ge=320, le=1280)] = 640,
    return_visualization: bool = False,
    calculate_coverage: bool = True,
    manager: YOLO26ModelManager = Depends(get_manager),
) -> WeedDetectionResponse:
    """
    Detect weeds in agricultural images.

    Supports detection of common agricultural weeds including:
    - Wild Oat (الشوفان البري)
    - Bermuda Grass (النجيل)
    - Johnson Grass (حشيشة جونسون)
    - Pigweed (عرف الديك)
    - Bindweed (العليق)
    - And more...

    Returns bilingual (Arabic/English) class names, coverage percentage,
    and species distribution.
    """
    request_id = uuid4()
    start_time = time.perf_counter()

    logger.info(
        "weed_detection_request",
        request_id=str(request_id),
        filename=file.filename,
        model_variant=model_variant.value,
    )

    try:
        # Validate and read image
        image_bytes = await validate_image(file)
        image_metadata = get_image_metadata(image_bytes)

        # Ensure image size is multiple of 32
        if image_size % 32 != 0:
            image_size = (image_size // 32 + 1) * 32

        # Run inference
        result: InferenceResult = await manager.predict(
            task=ModelTask.WEED_DETECTION,
            image=image_bytes,
            variant=model_variant.value,
            conf=confidence_threshold,
            iou=iou_threshold,
            max_det=max_detections,
            imgsz=image_size,
        )

        # Process detections
        detections: list[WeedDetection] = []
        species_distribution: dict[str, int] = {}
        total_coverage = 0.0
        visualization_data = []

        image_area = image_metadata.width * image_metadata.height

        for i in range(result.count):
            class_id = int(result.class_ids[i])
            confidence = float(result.scores[i])
            box = result.boxes[i]

            # Get bilingual label
            label = WEED_CLASSES.get(
                class_id, BilingualLabel(en="Unknown Weed", ar="عشبة غير معروفة")
            )

            # Update species distribution
            species_distribution[label.en] = species_distribution.get(label.en, 0) + 1

            # Calculate coverage
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            coverage_percent = (
                (box_area / image_area * 100) if image_area > 0 and calculate_coverage else None
            )
            if coverage_percent:
                total_coverage += coverage_percent

            bbox = BoundingBox(
                x1=float(box[0]),
                y1=float(box[1]),
                x2=float(box[2]),
                y2=float(box[3]),
            )

            detection = WeedDetection(
                class_id=class_id,
                class_name_en=label.en,
                class_name_ar=label.ar,
                scientific_name=label.scientific_name,
                confidence=confidence,
                bbox=bbox,
                coverage_percent=coverage_percent,
                growth_stage=None,  # Would require additional model
            )
            detections.append(detection)

            visualization_data.append(
                {
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                    "severity": SeverityLevel.MEDIUM,  # Default for visualization
                }
            )

        processing_time = (time.perf_counter() - start_time) * 1000

        # Cap total coverage at 100%
        total_coverage = min(total_coverage, 100.0)

        # Generate visualization if requested
        visualization_base64 = None
        if return_visualization and detections:
            visualization_base64 = create_visualization(
                image_bytes, visualization_data, WEED_CLASSES
            )

        logger.info(
            "weed_detection_complete",
            request_id=str(request_id),
            detections=len(detections),
            total_coverage=round(total_coverage, 1),
            processing_time_ms=round(processing_time, 2),
        )

        # Publish NATS events for downstream services
        if detections:
            await publish_weed_detection(
                request,
                [
                    {
                        "class_name_en": d.class_name_en,
                        "class_name_ar": d.class_name_ar,
                        "confidence": d.confidence,
                        "bbox": {"x1": d.bbox.x1, "y1": d.bbox.y1, "x2": d.bbox.x2, "y2": d.bbox.y2},
                        "coverage_percentage": d.coverage_percent,
                    }
                    for d in detections
                ],
                model_variant=model_variant.value,
                processing_time_ms=processing_time,
            )

        return WeedDetectionResponse(
            request_id=request_id,
            processing_time_ms=processing_time,
            model_variant=model_variant,
            image_metadata=image_metadata,
            detections=detections,
            total_count=len(detections),
            total_coverage_percent=round(total_coverage, 1),
            species_distribution=species_distribution,
            visualization_base64=visualization_base64,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("weed_detection_failed", request_id=str(request_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Detection failed",
                "message": str(e),
                "message_ar": "فشل الكشف",
            },
        )
