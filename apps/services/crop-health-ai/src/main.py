"""
Sahool Vision - Crop Health AI Service
خدمة سهول فيجن - الذكاء الاصطناعي لصحة المحاصيل

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
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, "../../../../shared")
sys.path.insert(0, "/app")

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../shared/config"))
from cors_config import setup_cors_middleware

# Field-First: Action Template Support
try:
    from shared.contracts.actions import (
        ActionTemplate,
        ActionTemplateFactory,
        UrgencyLevel as ActionUrgency,
    )
    ACTION_TEMPLATE_AVAILABLE = True
except ImportError:
    ACTION_TEMPLATE_AVAILABLE = False

# Import models
from models import (
    CropType,
    DiagnosisResult,
    HealthCheckResponse,
)

# Import services
from services import (
    disease_service,
    prediction_service,
    diagnosis_service,
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
    description="خدمة الذكاء الاصطناعي لتشخيص أمراض النباتات | AI-powered Plant Disease Diagnosis",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Use centralized secure configuration
setup_cors_middleware(app)

# Mount static files
Path("static/uploads").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    prediction_service.load_model()


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
        model_type=prediction_service.model_type if prediction_service.is_real_model else "mock",
        is_real_model=prediction_service.is_real_model,
        timestamp=datetime.utcnow()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Diagnosis Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/v1/diagnose", response_model=DiagnosisResult)
async def diagnose_plant_disease(
    image: UploadFile = File(..., description="صورة النبات المصاب"),
    field_id: Optional[str] = Query(None, description="معرف الحقل"),
    crop_type: Optional[CropType] = Query(None, description="نوع المحصول"),
    symptoms: Optional[str] = Query(None, description="وصف الأعراض"),
    governorate: Optional[str] = Query(None, description="المحافظة"),
    lat: Optional[float] = Query(None, description="خط العرض"),
    lng: Optional[float] = Query(None, description="خط الطول"),
    farmer_id: Optional[str] = Query(None, description="معرف المزارع")
):
    """
    🔬 تشخيص أمراض النباتات بالذكاء الاصطناعي

    AI-powered plant disease diagnosis from image.
    """
    # Validate image
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="الملف المرفوع ليس صورة صالحة")

    image_bytes = await image.read()

    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="حجم الصورة كبير جداً (الحد الأقصى 10 ميجابايت)")

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
    images: List[UploadFile] = File(..., description="قائمة صور للتشخيص"),
    field_id: Optional[str] = Query(None),
):
    """📦 تشخيص دفعة من الصور"""
    if len(images) > 20:
        raise HTTPException(status_code=400, detail="الحد الأقصى 20 صورة في الدفعة الواحدة")

    image_data = []
    for img in images:
        if img.content_type.startswith('image/'):
            image_bytes = await img.read()
            image_data.append((image_bytes, img.filename))

    return diagnosis_service.batch_diagnose(image_data, field_id)


# ═══════════════════════════════════════════════════════════════════════════════
# Disease Information Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/v1/diseases", response_model=List[dict])
async def list_diseases(
    crop_type: Optional[CropType] = Query(None, description="فلترة حسب نوع المحصول")
):
    """📋 قائمة الأمراض المدعومة"""
    return disease_service.get_all_diseases(crop_type)


@app.get("/v1/crops", response_model=List[dict])
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
    farmer_notes: Optional[str] = Query(None, description="ملاحظات المزارع"),
    urgency: str = Query("normal", enum=["low", "normal", "high", "urgent"])
):
    """👨‍🔬 طلب مراجعة خبير"""
    import uuid

    return {
        "review_id": str(uuid.uuid4()),
        "diagnosis_id": diagnosis_id,
        "status": "pending",
        "estimated_response_time": "24-48 hours" if urgency != "urgent" else "2-4 hours",
        "message": "تم إرسال طلب المراجعة. سيتواصل معك خبير قريباً.",
        "message_en": "Review request submitted. An expert will contact you soon."
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Admin Dashboard Endpoints (Epidemic Monitoring Center)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/v1/diagnoses", response_model=List[dict])
async def get_diagnosis_history(
    status: Optional[str] = Query(None, description="فلترة حسب الحالة"),
    severity: Optional[str] = Query(None, description="فلترة حسب الخطورة"),
    governorate: Optional[str] = Query(None, description="فلترة حسب المحافظة"),
    limit: int = Query(50, ge=1, le=200, description="عدد النتائج"),
    offset: int = Query(0, ge=0, description="بداية النتائج")
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
    status: str = Query(..., description="الحالة الجديدة", enum=["pending", "confirmed", "rejected", "treated"]),
    expert_notes: Optional[str] = Query(None, description="ملاحظات الخبير")
):
    """✏️ تحديث حالة التشخيص"""
    result = diagnosis_service.update_diagnosis_status(diagnosis_id, status, expert_notes)
    if not result:
        raise HTTPException(status_code=404, detail="التشخيص غير موجود")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Field-First: Action Template Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/v1/diagnose-with-action")
async def diagnose_with_action(
    image: UploadFile = File(..., description="صورة النبات المصاب"),
    field_id: Optional[str] = Query(None, description="معرف الحقل"),
    crop_type: Optional[CropType] = Query(None, description="نوع المحصول"),
    symptoms: Optional[str] = Query(None, description="وصف الأعراض"),
    governorate: Optional[str] = Query(None, description="المحافظة"),
    lat: Optional[float] = Query(None, description="خط العرض"),
    lng: Optional[float] = Query(None, description="خط الطول"),
    farmer_id: Optional[str] = Query(None, description="معرف المزارع")
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
        farmer_id=farmer_id
    )

    # If ActionTemplate not available, return diagnosis only
    if not ACTION_TEMPLATE_AVAILABLE:
        return {
            "diagnosis": diagnosis,
            "action_template": None,
            "action_template_available": False,
        }

    # Determine urgency based on severity
    severity = getattr(diagnosis, 'severity', 'medium')
    confidence = getattr(diagnosis, 'confidence', 0.7)

    urgency_map = {
        "critical": ActionUrgency.CRITICAL,
        "high": ActionUrgency.HIGH,
        "medium": ActionUrgency.MEDIUM,
        "low": ActionUrgency.LOW,
    }
    urgency = urgency_map.get(severity, ActionUrgency.MEDIUM)

    # Get disease info
    disease_name_ar = getattr(diagnosis, 'disease_name_ar', 'مرض غير محدد')
    disease_name_en = getattr(diagnosis, 'disease_name_en', 'Unknown disease')
    diagnosis_id = getattr(diagnosis, 'diagnosis_id', None)

    # Create inspection action first
    action = ActionTemplateFactory.create_disease_inspection_action(
        field_id=field_id or "unknown",
        disease_name_ar=disease_name_ar,
        disease_name_en=disease_name_en,
        confidence=confidence,
        affected_area_percent=getattr(diagnosis, 'affected_area_percent', 10.0),
        urgency=urgency,
        source_analysis_id=diagnosis_id,
        recommended_treatment=getattr(diagnosis, 'treatment_ar', None),
    )

    action.calculate_priority_score()

    # If treatment is recommended, also create spray action
    spray_action = None
    treatment = getattr(diagnosis, 'treatment', None)
    if treatment and severity in ["critical", "high"]:
        pesticide_type = "fungicide"  # Default for diseases

        spray_action = ActionTemplateFactory.create_spray_action(
            field_id=field_id or "unknown",
            pesticide_type=pesticide_type,
            pesticide_name_ar=getattr(treatment, 'pesticide_name_ar', 'مبيد فطري'),
            pesticide_name_en=getattr(treatment, 'pesticide_name_en', 'Fungicide'),
            concentration=getattr(treatment, 'concentration', '0.2%'),
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info"
    )
