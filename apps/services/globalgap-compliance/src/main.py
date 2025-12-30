"""
SAHOOL GlobalGAP Compliance Service - Main API
خدمة الامتثال لمعايير GlobalGAP للمنصة الزراعية SAHOOL
Port: 8120
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Depends, Header
import structlog

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../shared/config"))

try:
    from cors_config import setup_cors_middleware
except ImportError:
    # Fallback if shared config not available | احتياطي إذا لم يكن التكوين المشترك متاحًا
    def setup_cors_middleware(app):
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

from .config import settings
from .models.compliance import (
    ComplianceRecord,
    ComplianceStatus,
    NonConformity,
    SeverityLevel,
    AuditResult,
)
from .models.checklist import (
    ChecklistItem,
    ChecklistCategory,
    ComplianceLevel,
    Checklist,
    ChecklistAssessment,
    ControlPointStatus,
)
from .models.certificate import (
    GGNCertificate,
    CertificateStatus,
    CertificationScope,
    CertificateRenewal,
)
from .services.compliance_service import ComplianceService
from .services.audit_service import AuditService

# Initialize structured logging | تهيئة السجلات المنظمة
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger(__name__)


# ============== Authentication ==============


def get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")) -> str:
    """
    Extract and validate tenant ID from X-Tenant-Id header
    استخراج والتحقق من معرف المستأجر من رأس X-Tenant-Id
    """
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ============== In-Memory Data Store ==============
# للتطوير فقط - استخدم قاعدة بيانات في الإنتاج
# For development only - use database in production

_compliance_records: dict = {}
_checklists: dict = {}
_checklist_items: dict = {}
_assessments: dict = {}
_audit_results: dict = {}
_certificates: dict = {}


# ============== Application Lifecycle ==============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management
    إدارة دورة حياة التطبيق
    """
    logger.info("starting_globalgap_compliance_service", port=settings.service_port)

    # Initialize services | تهيئة الخدمات
    app.state.compliance_service = ComplianceService()
    app.state.audit_service = AuditService()

    # TODO: Connect to NATS for event publishing
    # TODO: الاتصال بـ NATS لنشر الأحداث
    # try:
    #     from .events import get_publisher
    #     publisher = await get_publisher()
    #     app.state.publisher = publisher
    #     logger.info("nats_connected")
    # except Exception as e:
    #     logger.warning("nats_connection_failed", error=str(e))
    #     app.state.publisher = None

    logger.info("globalgap_compliance_service_ready", port=settings.service_port)
    yield

    # Cleanup | التنظيف
    logger.info("globalgap_compliance_service_shutting_down")


# ============== Application Setup ==============


app = FastAPI(
    title="SAHOOL GlobalGAP Compliance Service",
    description="""
    خدمة الامتثال لمعايير GlobalGAP IFA v6
    GlobalGAP IFA v6 Compliance Service

    ## الميزات الرئيسية | Main Features

    - تتبع الامتثال للمزارع | Farm compliance tracking
    - إدارة قوائم المراجعة | Checklist management
    - إعداد تقارير التدقيق | Audit report preparation
    - إدارة شهادات GGN | GGN certificate management
    - تتبع عدم المطابقات والإجراءات التصحيحية | Non-conformity and corrective action tracking
    """,
    version=settings.service_version,
    lifespan=lifespan,
)

# CORS - Use centralized secure configuration
setup_cors_middleware(app)


# ============== Health Endpoints ==============


@app.get("/health")
def health():
    """
    Health check with dependencies
    فحص الصحة مع التبعيات
    """
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "database": "disconnected",  # TODO: Implement database health check
            "nats": "disconnected",  # TODO: Implement NATS health check
        }
    }


@app.get("/health/live")
def liveness():
    """
    Kubernetes liveness probe
    فحص الصحة - Kubernetes liveness probe
    """
    return {
        "status": "alive",
        "service": settings.service_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/ready")
def readiness():
    """
    Kubernetes readiness probe
    فحص الجاهزية - Kubernetes readiness probe
    """
    return {
        "status": "ready",
        "service": settings.service_name,
        "database": False,  # TODO: Implement database readiness check
        "nats": False,  # TODO: Implement NATS readiness check
    }


# ============== Compliance Endpoints ==============


@app.get("/farms/{farm_id}/compliance")
async def get_farm_compliance(
    farm_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get current compliance status for a farm
    الحصول على حالة الامتثال الحالية للمزرعة
    """
    compliance_service = app.state.compliance_service

    # Get compliance record | الحصول على سجل الامتثال
    compliance_record = await compliance_service.get_farm_compliance(farm_id, tenant_id)

    if not compliance_record:
        # Return default not assessed status | إرجاع حالة لم يتم التقييم الافتراضية
        return ComplianceRecord(
            farm_id=farm_id,
            tenant_id=tenant_id,
            overall_status=ComplianceStatus.NOT_ASSESSED,
            compliance_percentage=0.0,
            total_control_points=0,
            compliant_points=0,
            non_compliant_points=0,
        )

    return compliance_record


@app.post("/farms/{farm_id}/compliance", status_code=201)
async def create_or_update_compliance(
    farm_id: str,
    compliance_data: ComplianceRecord,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create or update compliance record for a farm
    إنشاء أو تحديث سجل الامتثال للمزرعة
    """
    # Validate tenant matches | التحقق من تطابق المستأجر
    if compliance_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    if compliance_data.farm_id != farm_id:
        raise HTTPException(status_code=400, detail="Farm ID mismatch")

    compliance_service = app.state.compliance_service

    # Save compliance record | حفظ سجل الامتثال
    saved_record = await compliance_service.save_compliance_record(compliance_data)

    logger.info(
        "compliance_record_saved",
        farm_id=farm_id,
        tenant_id=tenant_id,
        status=saved_record.overall_status.value,
        compliance_percentage=saved_record.compliance_percentage
    )

    return saved_record


@app.get("/farms/{farm_id}/compliance/trends")
async def get_compliance_trends(
    farm_id: str,
    months: int = Query(12, ge=1, le=24),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get compliance trends over time
    الحصول على اتجاهات الامتثال عبر الزمن
    """
    compliance_service = app.state.compliance_service
    trends = await compliance_service.get_compliance_trends(farm_id, tenant_id, months)

    return {
        "farm_id": farm_id,
        "tenant_id": tenant_id,
        "trends": trends,
        "period_months": months
    }


# ============== Checklist Endpoints ==============


@app.get("/checklists")
async def get_checklists(
    ifa_version: str = Query("6.0", description="IFA version | إصدار معايير IFA"),
    checklist_type: Optional[str] = Query(None, description="full, partial, follow_up"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get available checklists
    الحصول على قوائم المراجعة المتاحة
    """
    # Filter checklists | تصفية قوائم المراجعة
    filtered = [
        c for c in _checklists.values()
        if c.get("ifa_version") == ifa_version and c.get("is_active", True)
    ]

    if checklist_type:
        filtered = [c for c in filtered if c.get("checklist_type") == checklist_type]

    return {
        "checklists": filtered,
        "total": len(filtered),
        "ifa_version": ifa_version
    }


@app.get("/checklists/{checklist_id}/items")
async def get_checklist_items(
    checklist_id: str,
    category: Optional[ChecklistCategory] = Query(None),
    compliance_level: Optional[ComplianceLevel] = Query(None),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get checklist items (control points)
    الحصول على عناصر قائمة المراجعة (نقاط التحكم)
    """
    # Filter items | تصفية العناصر
    filtered = [
        item for item in _checklist_items.values()
        if item.get("is_active", True)
    ]

    if category:
        filtered = [item for item in filtered if item.get("category") == category.value]

    if compliance_level:
        filtered = [item for item in filtered if item.get("compliance_level") == compliance_level.value]

    return {
        "checklist_id": checklist_id,
        "items": filtered,
        "total": len(filtered)
    }


@app.post("/farms/{farm_id}/assessments", status_code=201)
async def create_assessment(
    farm_id: str,
    assessment: ChecklistAssessment,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create or update a checklist assessment for a farm
    إنشاء أو تحديث تقييم قائمة المراجعة للمزرعة
    """
    # Validate tenant and farm | التحقق من المستأجر والمزرعة
    if assessment.tenant_id != tenant_id or assessment.farm_id != farm_id:
        raise HTTPException(status_code=403, detail="Tenant or Farm ID mismatch")

    assessment_id = str(uuid4())
    assessment_data = assessment.model_dump()
    assessment_data["id"] = assessment_id

    _assessments[assessment_id] = assessment_data

    logger.info(
        "assessment_created",
        farm_id=farm_id,
        control_point=assessment.control_point_number,
        status=assessment.status.value
    )

    return assessment_data


@app.get("/farms/{farm_id}/assessments")
async def get_farm_assessments(
    farm_id: str,
    status: Optional[ControlPointStatus] = Query(None),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get all assessments for a farm
    الحصول على جميع التقييمات للمزرعة
    """
    # Filter assessments | تصفية التقييمات
    filtered = [
        a for a in _assessments.values()
        if a.get("farm_id") == farm_id and a.get("tenant_id") == tenant_id
    ]

    if status:
        filtered = [a for a in filtered if a.get("status") == status.value]

    return {
        "farm_id": farm_id,
        "assessments": filtered,
        "total": len(filtered)
    }


# ============== Audit Endpoints ==============


@app.post("/audits", status_code=201)
async def create_audit(
    farm_id: str = Query(..., description="Farm identifier"),
    audit_type: str = Query("internal", description="internal, external, certification"),
    auditor_name: str = Query(..., description="Name of auditor"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Prepare and create an audit report
    إعداد وإنشاء تقرير تدقيق
    """
    compliance_service = app.state.compliance_service
    audit_service = app.state.audit_service

    # Get compliance record | الحصول على سجل الامتثال
    compliance_record = await compliance_service.get_farm_compliance(farm_id, tenant_id)

    if not compliance_record:
        raise HTTPException(
            status_code=404,
            detail="No compliance record found for this farm. Please assess compliance first."
        )

    # Get non-conformities | الحصول على عدم المطابقات
    non_conformities = await compliance_service.get_non_conformities(farm_id, tenant_id)

    # Prepare audit report | إعداد تقرير التدقيق
    audit_result = await audit_service.prepare_audit_report(
        farm_id=farm_id,
        tenant_id=tenant_id,
        compliance_record=compliance_record,
        non_conformities=non_conformities,
        audit_type=audit_type,
        auditor_name=auditor_name
    )

    # Save audit result | حفظ نتيجة التدقيق
    saved_audit = await audit_service.save_audit_result(audit_result)

    logger.info(
        "audit_created",
        farm_id=farm_id,
        audit_type=audit_type,
        audit_status=saved_audit.audit_status,
        overall_score=saved_audit.overall_score
    )

    return saved_audit


@app.get("/audits/{audit_id}")
async def get_audit(
    audit_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get audit result by ID
    الحصول على نتيجة التدقيق حسب المعرف
    """
    audit_service = app.state.audit_service
    audit_result = await audit_service.get_audit_result(audit_id)

    if not audit_result:
        raise HTTPException(status_code=404, detail="Audit not found")

    # Validate tenant access | التحقق من وصول المستأجر
    if audit_result.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return audit_result


@app.get("/farms/{farm_id}/audits")
async def get_farm_audits(
    farm_id: str,
    limit: int = Query(10, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get audit history for a farm
    الحصول على سجل التدقيق للمزرعة
    """
    audit_service = app.state.audit_service
    audits = await audit_service.get_farm_audit_history(farm_id, tenant_id, limit)

    return {
        "farm_id": farm_id,
        "audits": audits,
        "total": len(audits)
    }


# ============== Non-Conformity Endpoints ==============


@app.get("/farms/{farm_id}/non-conformities")
async def get_farm_non_conformities(
    farm_id: str,
    severity: Optional[SeverityLevel] = Query(None),
    resolved: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get non-conformities for a farm
    الحصول على عدم المطابقات للمزرعة
    """
    compliance_service = app.state.compliance_service
    non_conformities = await compliance_service.get_non_conformities(
        farm_id=farm_id,
        tenant_id=tenant_id,
        severity=severity,
        resolved=resolved
    )

    return {
        "farm_id": farm_id,
        "non_conformities": non_conformities,
        "total": len(non_conformities),
        "filters": {
            "severity": severity.value if severity else None,
            "resolved": resolved
        }
    }


@app.post("/non-conformities", status_code=201)
async def create_non_conformity(
    non_conformity: NonConformity,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new non-conformity record
    إنشاء سجل عدم مطابقة جديد
    """
    compliance_service = app.state.compliance_service
    created = await compliance_service.create_non_conformity(non_conformity)

    logger.info(
        "non_conformity_created",
        control_point=non_conformity.control_point_number,
        severity=non_conformity.severity.value
    )

    return created


# ============== Certificate Endpoints ==============


@app.get("/farms/{farm_id}/certificates")
async def get_farm_certificates(
    farm_id: str,
    status: Optional[CertificateStatus] = Query(None),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get GGN certificates for a farm
    الحصول على شهادات GGN للمزرعة
    """
    # Filter certificates | تصفية الشهادات
    filtered = [
        cert for cert in _certificates.values()
        if cert.get("farm_id") == farm_id and cert.get("tenant_id") == tenant_id
    ]

    if status:
        filtered = [cert for cert in filtered if cert.get("status") == status.value]

    return {
        "farm_id": farm_id,
        "certificates": filtered,
        "total": len(filtered)
    }


@app.post("/certificates", status_code=201)
async def create_certificate(
    certificate: GGNCertificate,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Create a new GGN certificate
    إنشاء شهادة GGN جديدة
    """
    # Validate tenant | التحقق من المستأجر
    if certificate.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    cert_id = str(uuid4())
    cert_data = certificate.model_dump()
    cert_data["id"] = cert_id

    _certificates[cert_id] = cert_data

    logger.info(
        "certificate_created",
        farm_id=certificate.farm_id,
        ggn_number=certificate.ggn_number,
        status=certificate.status.value
    )

    return cert_data


@app.get("/certificates/{certificate_id}")
async def get_certificate(
    certificate_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get certificate by ID
    الحصول على الشهادة حسب المعرف
    """
    certificate = _certificates.get(certificate_id)

    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Validate tenant access | التحقق من وصول المستأجر
    if certificate.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return certificate


# ============== Main Entry Point ==============


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", settings.service_port))
    uvicorn.run(app, host="0.0.0.0", port=port)
