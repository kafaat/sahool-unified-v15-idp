"""
Scout Reports API
واجهة برمجة تقارير المسح الحقلي

Endpoints for managing field scouting and pest observations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Enums
# ============================================================================


class InfestationLevel(str, Enum):
    """Infestation level assessment."""
    NONE = "none"
    TRACE = "trace"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class ReportStatus(str, Enum):
    """Scout report status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    ACTION_REQUIRED = "action_required"
    RESOLVED = "resolved"


# ============================================================================
# Models
# ============================================================================


class GPSLocation(BaseModel):
    """GPS coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_m: Optional[float] = None


class Observation(BaseModel):
    """Single pest observation."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    pest_id: str
    pest_name_en: Optional[str] = None
    pest_name_ar: Optional[str] = None
    location: Optional[GPSLocation] = None
    infestation_level: InfestationLevel
    affected_area_percent: float = Field(..., ge=0, le=100)
    life_stage: Optional[str] = None
    count: Optional[int] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    image_urls: list[str] = []
    observed_at: datetime = Field(default_factory=datetime.utcnow)


class ScoutReportCreate(BaseModel):
    """Create scout report request."""
    field_id: str
    crop: str
    growth_stage: Optional[str] = None
    scout_name: Optional[str] = None
    observations: list[Observation] = []
    weather_conditions: Optional[str] = None
    general_notes: Optional[str] = None
    general_notes_ar: Optional[str] = None


class ScoutReport(BaseModel):
    """Scout report model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    field_id: str
    crop: str
    growth_stage: Optional[str] = None
    scout_name: Optional[str] = None
    status: ReportStatus = ReportStatus.DRAFT
    observations: list[Observation] = []
    weather_conditions: Optional[str] = None
    general_notes: Optional[str] = None
    general_notes_ar: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class ObservationCreate(BaseModel):
    """Add observation to report."""
    pest_id: str
    location: Optional[GPSLocation] = None
    infestation_level: InfestationLevel
    affected_area_percent: float = Field(..., ge=0, le=100)
    life_stage: Optional[str] = None
    count: Optional[int] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    image_urls: list[str] = []


# ============================================================================
# In-memory storage (would be PostgreSQL in production)
# ============================================================================

REPORTS_DB: dict[str, ScoutReport] = {}


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/scouts/reports")
async def list_reports(
    field_id: Optional[str] = None,
    status: Optional[ReportStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List scout reports.
    قائمة تقارير المسح الحقلي.
    """
    reports = list(REPORTS_DB.values())

    if field_id:
        reports = [r for r in reports if r.field_id == field_id]

    if status:
        reports = [r for r in reports if r.status == status]

    # Sort by created_at descending
    reports.sort(key=lambda x: x.created_at, reverse=True)

    return {
        "total": len(reports),
        "reports": reports[offset : offset + limit],
    }


@router.post("/scouts/reports", response_model=ScoutReport)
async def create_report(report_data: ScoutReportCreate):
    """
    Create a new scout report.
    إنشاء تقرير مسح حقلي جديد.
    """
    report = ScoutReport(
        field_id=report_data.field_id,
        crop=report_data.crop,
        growth_stage=report_data.growth_stage,
        scout_name=report_data.scout_name,
        observations=report_data.observations,
        weather_conditions=report_data.weather_conditions,
        general_notes=report_data.general_notes,
        general_notes_ar=report_data.general_notes_ar,
    )

    REPORTS_DB[report.id] = report

    logger.info(
        "scout_report_created",
        report_id=report.id,
        field_id=report.field_id,
        observation_count=len(report.observations),
    )

    return report


@router.get("/scouts/reports/{report_id}", response_model=ScoutReport)
async def get_report(report_id: str):
    """
    Get scout report by ID.
    الحصول على تقرير المسح بواسطة المعرف.
    """
    report = REPORTS_DB.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    return report


@router.put("/scouts/reports/{report_id}", response_model=ScoutReport)
async def update_report(report_id: str, report_data: ScoutReportCreate):
    """
    Update scout report.
    تحديث تقرير المسح الحقلي.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    report = REPORTS_DB[report_id]

    # Update fields
    report.field_id = report_data.field_id
    report.crop = report_data.crop
    report.growth_stage = report_data.growth_stage
    report.scout_name = report_data.scout_name
    report.observations = report_data.observations
    report.weather_conditions = report_data.weather_conditions
    report.general_notes = report_data.general_notes
    report.general_notes_ar = report_data.general_notes_ar
    report.updated_at = datetime.utcnow()

    logger.info("scout_report_updated", report_id=report_id)

    return report


@router.delete("/scouts/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete scout report.
    حذف تقرير المسح الحقلي.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    del REPORTS_DB[report_id]

    logger.info("scout_report_deleted", report_id=report_id)

    return {"message": "Report deleted", "message_ar": "تم حذف التقرير"}


@router.get("/scouts/reports/field/{field_id}")
async def get_reports_by_field(
    field_id: str,
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get all reports for a field.
    الحصول على جميع التقارير لحقل معين.
    """
    reports = [r for r in REPORTS_DB.values() if r.field_id == field_id]
    reports.sort(key=lambda x: x.created_at, reverse=True)

    return {
        "field_id": field_id,
        "total": len(reports),
        "reports": reports[:limit],
    }


@router.post("/scouts/reports/{report_id}/observations", response_model=Observation)
async def add_observation(report_id: str, obs_data: ObservationCreate):
    """
    Add observation to report.
    إضافة ملاحظة إلى التقرير.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    report = REPORTS_DB[report_id]

    observation = Observation(
        pest_id=obs_data.pest_id,
        location=obs_data.location,
        infestation_level=obs_data.infestation_level,
        affected_area_percent=obs_data.affected_area_percent,
        life_stage=obs_data.life_stage,
        count=obs_data.count,
        notes=obs_data.notes,
        notes_ar=obs_data.notes_ar,
        image_urls=obs_data.image_urls,
    )

    report.observations.append(observation)
    report.updated_at = datetime.utcnow()

    logger.info(
        "observation_added",
        report_id=report_id,
        pest_id=observation.pest_id,
        infestation_level=observation.infestation_level,
    )

    return observation


@router.post("/scouts/reports/{report_id}/submit")
async def submit_report(report_id: str):
    """
    Submit report for review.
    تقديم التقرير للمراجعة.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

    report = REPORTS_DB[report_id]

    if not report.observations:
        raise HTTPException(
            status_code=400,
            detail="Cannot submit report without observations",
        )

    report.status = ReportStatus.SUBMITTED
    report.updated_at = datetime.utcnow()

    logger.info("scout_report_submitted", report_id=report_id)

    return {
        "message": "Report submitted",
        "message_ar": "تم تقديم التقرير",
        "status": report.status,
    }


@router.get("/scouts/statistics")
async def get_scouting_statistics(
    field_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
):
    """
    Get scouting statistics.
    الحصول على إحصائيات المسح الحقلي.
    """
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)

    reports = [
        r for r in REPORTS_DB.values()
        if r.created_at >= cutoff
    ]

    if field_id:
        reports = [r for r in reports if r.field_id == field_id]

    # Count observations by pest
    pest_counts: dict[str, int] = {}
    total_observations = 0

    for report in reports:
        for obs in report.observations:
            pest_counts[obs.pest_id] = pest_counts.get(obs.pest_id, 0) + 1
            total_observations += 1

    # Find most common pests
    top_pests = sorted(pest_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "period_days": days,
        "total_reports": len(reports),
        "total_observations": total_observations,
        "top_pests": [{"pest_id": p[0], "count": p[1]} for p in top_pests],
        "reports_by_status": {
            status.value: len([r for r in reports if r.status == status])
            for status in ReportStatus
        },
    }
