"""
Sahool Vision - Crop Health AI Service
خدمة سهول فيجن - الذكاء الاصطناعي لصحة المحاصيل

⚠️ DEPRECATED: This service is deprecated and will be removed in a future release.
Please use 'crop-intelligence-service' instead.

Architecture: Clean Service Layer Pattern
- Routes (this file): HTTP endpoints only
- Services: Business logic
- Models: Data structures

Field-First Architecture:
- كل تشخيص يُنتج ActionTemplate قابل للتنفيذ بدون اتصال
- التحليل يخدم الميدان، لا العكس

Port: 8095
Version: 2.2.1
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile

# Configure logger early
logger = logging.getLogger(__name__)

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.staticfiles import StaticFiles

sys.path.insert(0, "../../../../shared")
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

sys.path.insert(0, "/app")

# Import file validation utilities
try:
    from shared.file_validation import (
        ALLOWED_IMAGE_TYPES,
        FileValidationConfig,
        FileValidationError,
        FileValidator,
        get_virus_scanner,
    )

    FILE_VALIDATION_AVAILABLE = True
except ImportError:
    FILE_VALIDATION_AVAILABLE = False
    logger.warning("File validation module not available")

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../shared/config"))
from cors_config import setup_cors_middleware

# Field-First: Action Template Support
try:
    from shared.contracts.actions import (
        ActionTemplate,
        ActionTemplateFactory,
    )
    from shared.contracts.actions import (
        UrgencyLevel as ActionUrgency,
    )

    ACTION_TEMPLATE_AVAILABLE = True
except ImportError:
    ACTION_TEMPLATE_AVAILABLE = False

# Import models
# Import services
from services import (
    diagnosis_service,
    disease_service,
    prediction_service,
)

from models import (
    CropType,
    DiagnosisResult,
    HealthCheckResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-vision")

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "crop-health-ai"
SERVICE_VERSION = "2.2.0"  # Refactored with Service Layer
SERVICE_PORT = 8095

# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="سهول فيجن - Sahool Vision",
    description="⚠️ DEPRECATED - Use crop-intelligence-service instead. خدمة الذكاء الاصطناعي لتشخيص أمراض النباتات | AI-powered Plant Disease Diagnosis",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Use centralized secure configuration
setup_cors_middleware(app)

# Mount static files
Path("static/uploads").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.warning("=" * 80)
    logger.warning("⚠️  DEPRECATION WARNING")
    logger.warning("=" * 80)
    logger.warning(
        "This service (crop-health-ai) is DEPRECATED and will be removed in a future release."
    )
    logger.warning("Please migrate to 'crop-intelligence-service' instead.")
    logger.warning("Replacement service: crop-intelligence-service")
    logger.warning("Deprecation date: 2025-01-01")
    logger.warning("=" * 80)
    prediction_service.load_model()

    # Initialize file validator
    if FILE_VALIDATION_AVAILABLE:
        virus_scanner_type = os.getenv("VIRUS_SCANNER", "noop")
        clamav_host = os.getenv("CLAMAV_HOST", "localhost")
        clamav_port = int(os.getenv("CLAMAV_PORT", "3310"))

        app.state.virus_scanner = get_virus_scanner(
            virus_scanner_type, host=clamav_host, port=clamav_port
        )

        app.state.file_validator = FileValidator(
            config=FileValidationConfig(
                max_file_size=10 * 1024 * 1024,  # 10MB
                allowed_mime_types=ALLOWED_IMAGE_TYPES,
                check_magic_bytes=True,
                strict_mime_check=True,
                scan_for_viruses=virus_scanner_type != "noop",
                allow_executable=False,
                sanitize_filename=True,
            ),
            virus_scanner=app.state.virus_scanner,
        )
        logger.info(f"✅ File validation enabled with {virus_scanner_type} scanner")
    else:
        logger.warning("⚠️  File validation module not available, using basic validation")


@app.middleware("http")
async def add_deprecation_header(request: Request, call_next):
    """Add deprecation headers to all responses"""
    response = await call_next(request)
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecation-Date"] = "2025-01-01"
    response.headers["X-API-Deprecation-Info"] = (
        "This service is deprecated. Use crop-intelligence-service instead."
    )
    response.headers["X-API-Sunset"] = "2025-06-01"
    response.headers["Link"] = '<http://crop-intelligence-service:8095>; rel="successor-version"'
    response.headers["Deprecation"] = "true"
    return response


# ═══════════════════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz", response_model=HealthCheckResponse)
async def health_check():
    """نقطة فحص صحة الخدمة"""
    return HealthCheckResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        model_loaded=prediction_service.is_loaded,
        model_type=(prediction_service.model_type if prediction_service.is_real_model else "mock"),
        is_real_model=prediction_service.is_real_model,
        timestamp=datetime.utcnow(),
    )


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    return {
        "status": "ready",
        "service": "crop-health-ai",
        "version": "16.0.0",
        "checks": {
            "service": "ready",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Diagnosis Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/v1/diagnose", response_model=DiagnosisResult)
async def diagnose_plant_disease(
    image: UploadFile = File(..., description="صورة النبات المصاب"),
    field_id: str | None = Query(None, description="معرف الحقل"),
    crop_type: CropType | None = Query(None, description="نوع المحصول"),
    symptoms: str | None = Query(None, description="وصف الأعراض"),
    governorate: str | None = Query(None, description="المحافظة"),
    lat: float | None = Query(None, description="خط العرض"),
    lng: float | None = Query(None, description="خط الطول"),
    farmer_id: str | None = Query(None, description="معرف المزارع"),
):
    """
    🔬 تشخيص أمراض النباتات بالذكاء الاصطناعي

    AI-powered plant disease diagnosis from image.
    """
    # Read image bytes
    image_bytes = await image.read()

    # Enhanced validation using FileValidator
    if FILE_VALIDATION_AVAILABLE and hasattr(app.state, "file_validator"):
        try:
            validation_result = await app.state.file_validator.validate(
                file_content=image_bytes,
                filename=image.filename,
                declared_mime_type=image.content_type,
            )
            logger.info(f"File validation passed: {validation_result['safe_filename']}")
        except FileValidationError as e:
            logger.warning(f"File validation failed: {e.message}")
            raise HTTPException(status_code=400, detail=e.message)
    else:
        # Fallback to basic validation
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="الملف المرفوع ليس صورة صالحة")

        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400, detail="حجم الصورة كبير جداً (الحد الأقصى 10 ميجابايت)"
            )

    # Delegate to service
    return diagnosis_service.diagnose(
        image_bytes=image_bytes,
        filename=image.filename,
        field_id=field_id,
        crop_type=crop_type,
        symptoms=symptoms,
        governorate=governorate,
        lat=lat,
        lng=lng,
        farmer_id=farmer_id,
    )


@app.post("/v1/diagnose/batch")
async def batch_diagnose(
    images: list[UploadFile] = File(..., description="قائمة صور للتشخيص"),
    field_id: str | None = Query(None),
):
    """📦 تشخيص دفعة من الصور"""
    if len(images) > 20:
        raise HTTPException(status_code=400, detail="الحد الأقصى 20 صورة في الدفعة الواحدة")

    image_data = []
    for img in images:
        image_bytes = await img.read()

        # Enhanced validation for each image
        if FILE_VALIDATION_AVAILABLE and hasattr(app.state, "file_validator"):
            try:
                await app.state.file_validator.validate(
                    file_content=image_bytes,
                    filename=img.filename,
                    declared_mime_type=img.content_type,
                )
            except FileValidationError as e:
                logger.warning(f"File validation failed for {img.filename}: {e.message}")
                # Skip invalid files in batch processing
                continue
        else:
            # Fallback to basic validation
            if not img.content_type.startswith("image/"):
                continue

        image_data.append((image_bytes, img.filename))

    if not image_data:
        raise HTTPException(
            status_code=400, detail="لم يتم العثور على صور صالحة / No valid images found"
        )

    return diagnosis_service.batch_diagnose(image_data, field_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Disease Information Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/diseases", response_model=list[dict])
async def list_diseases(
    crop_type: CropType | None = Query(None, description="فلترة حسب نوع المحصول"),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of diseases to return"
    ),
    offset: int = Query(default=0, ge=0, description="Number of diseases to skip"),
):
    """📋 قائمة الأمراض المدعومة مع الترقيم"""
    all_diseases = disease_service.get_all_diseases(crop_type)

    # Apply pagination
    total = len(all_diseases)
    paginated_diseases = all_diseases[offset : offset + limit]

    return {
        "diseases": paginated_diseases,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


@app.get("/v1/crops", response_model=list[dict])
async def list_supported_crops():
    """🌾 قائمة المحاصيل المدعومة"""
    return disease_service.get_supported_crops()


@app.get("/v1/treatment/{disease_id}")
async def get_treatment_details(disease_id: str):
    """💊 تفاصيل العلاج لمرض معين"""
    result = disease_service.get_treatment_details(disease_id)
    if not result:
        raise HTTPException(status_code=404, detail="المرض غير موجود في قاعدة البيانات")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Expert Review Endpoint
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/v1/expert-review")
async def request_expert_review(
    diagnosis_id: str = Query(..., description="معرف التشخيص"),
    image: UploadFile = File(...),
    farmer_notes: str | None = Query(None, description="ملاحظات المزارع"),
    urgency: str = Query("normal", enum=["low", "normal", "high", "urgent"]),
):
    """👨‍🔬 طلب مراجعة خبير"""
    import uuid

    # Read and validate image
    image_bytes = await image.read()

    if FILE_VALIDATION_AVAILABLE and hasattr(app.state, "file_validator"):
        try:
            await app.state.file_validator.validate(
                file_content=image_bytes,
                filename=image.filename,
                declared_mime_type=image.content_type,
            )
        except FileValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)

    return {
        "review_id": str(uuid.uuid4()),
        "diagnosis_id": diagnosis_id,
        "status": "pending",
        "estimated_response_time": ("24-48 hours" if urgency != "urgent" else "2-4 hours"),
        "message": "تم إرسال طلب المراجعة. سيتواصل معك خبير قريباً.",
        "message_en": "Review request submitted. An expert will contact you soon.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Admin Dashboard Endpoints (Epidemic Monitoring Center)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/diagnoses", response_model=list[dict])
async def get_diagnosis_history(
    status: str | None = Query(None, description="فلترة حسب الحالة"),
    severity: str | None = Query(None, description="فلترة حسب الخطورة"),
    governorate: str | None = Query(None, description="فلترة حسب المحافظة"),
    limit: int = Query(50, ge=1, le=200, description="عدد النتائج"),
    offset: int = Query(0, ge=0, description="بداية النتائج"),
):
    """📋 سجل التشخيصات للوحة التحكم"""
    return diagnosis_service.get_history(status, severity, governorate, limit, offset)


@app.get("/v1/diagnoses/stats")
async def get_diagnosis_stats():
    """📊 إحصائيات التشخيصات"""
    return diagnosis_service.get_stats()


@app.get("/v1/diagnoses/{diagnosis_id}")
async def get_diagnosis_by_id(diagnosis_id: str):
    """🔍 تفاصيل تشخيص محدد"""
    result = diagnosis_service.get_diagnosis_by_id(diagnosis_id)
    if not result:
        raise HTTPException(status_code=404, detail="التشخيص غير موجود")
    return result


@app.patch("/v1/diagnoses/{diagnosis_id}")
async def update_diagnosis_status(
    diagnosis_id: str,
    status: str = Query(
        ...,
        description="الحالة الجديدة",
        enum=["pending", "confirmed", "rejected", "treated"],
    ),
    expert_notes: str | None = Query(None, description="ملاحظات الخبير"),
):
    """✏️ تحديث حالة التشخيص"""
    result = diagnosis_service.update_diagnosis_status(diagnosis_id, status, expert_notes)
    if not result:
        raise HTTPException(status_code=404, detail="التشخيص غير موجود")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# Context Engineering Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/field/{field_id}/health")
async def get_field_health(field_id: str):
    """
    🏥 Get field health metrics

    Returns comprehensive health assessment with disease patterns
    and risk factors for a specific field.
    """
    from services import field_memory

    metrics = field_memory.calculate_field_metrics(field_id)

    return {
        "field_id": field_id,
        "health_score": f"{metrics.health_score:.2f}",
        "total_diagnoses": metrics.total_diagnoses,
        "healthy_diagnoses": metrics.healthy_diagnoses,
        "infected_diagnoses": metrics.infected_diagnoses,
        "infection_trend": metrics.infection_trend,
        "dominant_disease": metrics.dominant_disease,
        "disease_variety": metrics.disease_variety,
        "avg_confidence": f"{metrics.avg_confidence:.2f}",
        "last_updated": metrics.last_updated.isoformat(),
    }


@app.get("/v1/field/{field_id}/disease-patterns")
async def get_field_disease_patterns(field_id: str):
    """
    📊 Get disease patterns for field

    Analyzes historical disease occurrences and recurrence patterns
    for predictive insights.
    """
    from services import field_memory

    patterns = field_memory.get_disease_patterns(field_id)

    return {
        "field_id": field_id,
        "patterns": [
            {
                "disease_id": disease_id,
                "disease_name_ar": pattern.disease_name_ar,
                "occurrence_count": pattern.occurrence_count,
                "avg_confidence": f"{pattern.avg_confidence:.2f}",
                "severity_levels": pattern.severity_levels,
                "last_occurred": pattern.last_occurred.isoformat(),
                "avg_days_between": (
                    sum(pattern.days_between_occurrences)
                    / len(pattern.days_between_occurrences)
                    if pattern.days_between_occurrences
                    else 0
                ),
                "avg_severity": pattern.avg_severity,
            }
            for disease_id, pattern in patterns.items()
        ],
        "total_patterns": len(patterns),
    }


@app.get("/v1/field/{field_id}/risk-assessment")
async def get_field_risk_assessment(field_id: str):
    """
    ⚠️ Get field risk assessment

    Provides comprehensive risk analysis including disease
    recurrence likelihood and recommended actions.
    """
    from services import field_memory

    risk = field_memory.get_field_risk_assessment(field_id)

    return risk


@app.post("/v1/field/{field_id}/diagnosis/{diagnosis_id}/mark-treated")
async def mark_diagnosis_treated(field_id: str, diagnosis_id: str):
    """
    ✅ Mark diagnosis as treated

    Records that treatment was applied to track intervention success.
    """
    from services import field_memory

    success = field_memory.mark_diagnosis_treated(field_id, diagnosis_id)

    if success:
        return {
            "success": True,
            "message": f"Diagnosis {diagnosis_id} marked as treated",
            "field_id": field_id,
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Diagnosis {diagnosis_id} not found in field {field_id}",
        )


@app.get("/v1/field/{field_id}/treatment-effectiveness")
async def get_treatment_effectiveness(field_id: str):
    """
    💊 Get treatment effectiveness metrics

    Shows how successful treatments have been for this field.
    """
    from services import field_memory

    effectiveness = field_memory.get_treatment_effectiveness(field_id)

    return effectiveness


@app.get("/v1/fields/summary")
async def get_all_fields_summary():
    """
    📈 Get summary across all fields

    Overview of total diagnoses, average health, and at-risk fields.
    """
    from services import field_memory

    summary = field_memory.get_all_fields_summary()

    return summary


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluation & Model Performance Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/v1/evaluation/record-outcome/{diagnosis_id}")
async def record_evaluation_outcome(
    diagnosis_id: str = Query(..., description="Diagnosis ID"),
    actual_disease: str = Query(..., description="Actual disease ID"),
    notes: str | None = Query(None, description="Optional notes"),
):
    """
    📝 Record actual diagnosis outcome

    Update prediction with ground truth for accuracy evaluation.
    Typically called after expert review confirms diagnosis.
    """
    from services import evaluation_scorer

    success = evaluation_scorer.record_outcome(diagnosis_id, actual_disease, notes)

    if success:
        return {
            "success": True,
            "diagnosis_id": diagnosis_id,
            "actual_disease": actual_disease,
            "message": "Outcome recorded for evaluation",
        }
    else:
        raise HTTPException(
            status_code=404, detail=f"Diagnosis {diagnosis_id} not found"
        )


@app.get("/v1/evaluation/accuracy-metrics")
async def get_accuracy_metrics(
    days_back: int = Query(30, ge=1, le=365, description="Days to include")
):
    """
    📊 Get accuracy metrics

    Prediction accuracy, confidence calibration, and performance by
    confidence level.
    """
    from services import evaluation_scorer

    metrics = evaluation_scorer.get_accuracy_metrics(days_back=days_back)

    return {
        "period_days": days_back,
        "total_evaluated": metrics.total_predictions,
        "correct": metrics.correct_predictions,
        "accuracy": f"{metrics.accuracy:.1%}",
        "high_confidence_accuracy": f"{metrics.high_confidence_accuracy:.1%}",
        "medium_confidence_accuracy": f"{metrics.medium_confidence_accuracy:.1%}",
        "low_confidence_accuracy": f"{metrics.low_confidence_accuracy:.1%}",
        "confidence_mean": f"{metrics.confidence_mean:.2f}",
        "confidence_std": f"{metrics.confidence_std:.2f}",
        "calibration_score": f"{metrics.calibration_score:.2f}",
    }


@app.get("/v1/evaluation/per-disease-metrics")
async def get_per_disease_metrics(
    days_back: int = Query(30, ge=1, le=365, description="Days to include")
):
    """
    🔬 Get accuracy metrics per disease

    Breakdown of prediction accuracy for each disease type.
    """
    from services import evaluation_scorer

    metrics = evaluation_scorer.get_per_disease_metrics(days_back=days_back)

    return {
        "period_days": days_back,
        "disease_metrics": metrics,
        "total_diseases": len(metrics),
    }


@app.get("/v1/evaluation/model-drift")
async def detect_model_drift(
    recent_days: int = Query(
        7, ge=1, le=30, description="Recent period for comparison (days)"
    )
):
    """
    🔴 Detect model drift

    Identifies if model performance is degrading compared to historical
    performance.
    """
    from services import evaluation_scorer

    drift = evaluation_scorer.detect_model_drift(days_back=recent_days)

    return {
        "drift_detected": drift.drift_detected,
        "drift_severity": drift.drift_severity,
        "recent_accuracy": f"{drift.accuracy_7day:.1%}",
        "historical_accuracy": f"{drift.accuracy_30day:.1%}",
        "accuracy_change": f"{drift.accuracy_change_percent:+.1f}%",
        "confidence_trend": drift.confidence_trend,
        "false_positive_rate": f"{drift.false_positive_rate:.1%}",
        "false_negative_rate": f"{drift.false_negative_rate:.1%}",
        "alert": (
            "⚠️ Model performance degrading!"
            if drift.drift_detected
            else "✅ Model performance stable"
        ),
    }


@app.get("/v1/evaluation/report")
async def get_evaluation_report(
    days_back: int = Query(30, ge=1, le=365, description="Report period (days)")
):
    """
    📑 Get comprehensive evaluation report

    Full report on model performance, accuracy trends, and recommendations.
    """
    from services import evaluation_scorer

    report = evaluation_scorer.get_evaluation_report(days_back=days_back)

    return report


@app.get("/v1/evaluation/statistics")
async def get_evaluation_statistics():
    """
    📈 Get evaluation statistics

    Summary of how many predictions have been evaluated.
    """
    from services import evaluation_scorer

    stats = evaluation_scorer.get_statistics_summary()

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# Field-First: Action Template Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/v1/diagnose-with-action")
async def diagnose_with_action(
    image: UploadFile = File(..., description="صورة النبات المصاب"),
    field_id: str | None = Query(None, description="معرف الحقل"),
    crop_type: CropType | None = Query(None, description="نوع المحصول"),
    symptoms: str | None = Query(None, description="وصف الأعراض"),
    governorate: str | None = Query(None, description="المحافظة"),
    lat: float | None = Query(None, description="خط العرض"),
    lng: float | None = Query(None, description="خط الطول"),
    farmer_id: str | None = Query(None, description="معرف المزارع"),
):
    """
    🔬 تشخيص أمراض النباتات مع ActionTemplate

    Field-First: يُنتج قالب إجراء قابل للتنفيذ (فحص/رش) بدون اتصال
    """
    # Get regular diagnosis
    diagnosis = await diagnose_plant_disease(
        image=image,
        field_id=field_id,
        crop_type=crop_type,
        symptoms=symptoms,
        governorate=governorate,
        lat=lat,
        lng=lng,
        farmer_id=farmer_id,
    )

    # If ActionTemplate not available, return diagnosis only
    if not ACTION_TEMPLATE_AVAILABLE:
        return {
            "diagnosis": diagnosis,
            "action_template": None,
            "action_template_available": False,
        }

    # Determine urgency based on severity
    severity = getattr(diagnosis, "severity", "medium")
    confidence = getattr(diagnosis, "confidence", 0.7)

    urgency_map = {
        "critical": ActionUrgency.CRITICAL,
        "high": ActionUrgency.HIGH,
        "medium": ActionUrgency.MEDIUM,
        "low": ActionUrgency.LOW,
    }
    urgency = urgency_map.get(severity, ActionUrgency.MEDIUM)

    # Get disease info
    disease_name_ar = getattr(diagnosis, "disease_name_ar", "مرض غير محدد")
    disease_name_en = getattr(diagnosis, "disease_name", "Unknown disease")
    diagnosis_id = getattr(diagnosis, "diagnosis_id", None)

    # Create inspection action first
    action = ActionTemplateFactory.create_disease_inspection_action(
        field_id=field_id or "unknown",
        disease_name_ar=disease_name_ar,
        disease_name_en=disease_name_en,
        confidence=confidence,
        affected_area_percent=getattr(diagnosis, "affected_area_percent", 10.0),
        urgency=urgency,
        source_analysis_id=diagnosis_id,
        recommended_treatment=getattr(diagnosis, "treatment_ar", None),
    )

    action.calculate_priority_score()

    # If treatment is recommended, also create spray action
    spray_action = None
    treatment = getattr(diagnosis, "treatment", None)
    if treatment and severity in ["critical", "high"]:
        pesticide_type = "fungicide"  # Default for diseases

        spray_action = ActionTemplateFactory.create_spray_action(
            field_id=field_id or "unknown",
            pesticide_type=pesticide_type,
            pesticide_name_ar=getattr(treatment, "product_name_ar", "مبيد فطري"),
            pesticide_name_en=getattr(treatment, "product_name", "Fungicide"),
            concentration=getattr(treatment, "dosage", "0.2%"),
            area_hectares=1.0,  # Default
            urgency=urgency,
            confidence=confidence,
            target_pest_ar=disease_name_ar,
            target_pest_en=disease_name_en,
            source_analysis_id=diagnosis_id,
        )
        spray_action.calculate_priority_score()

    return {
        "diagnosis": diagnosis,
        "action_template": action.model_dump(),
        "spray_action_template": spray_action.model_dump() if spray_action else None,
        "action_template_available": True,
        "task_card": action.to_task_card(),
        "notification_payload": action.to_notification_payload(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Run Application
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True, log_level="info")
