"""
SAHOOL Crop Intelligence Service
خدمة ذكاء المحاصيل - تشخيص ذكي للحقول الزراعية
Port: 8095
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query

# Shared middleware imports - add apps/services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers
    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False
    def setup_security_headers(app):
        pass

from .decision_engine import (
    GrowthStage,
    Indices,
    ZoneObservation,
    classify_zone_status,
    diagnose_zone,
    generate_vrt_properties,
)
from .disease_detection import (
    CropType,
    DiseaseDetection,
    DiseaseSeverity,
    detect_diseases,
    get_overall_health_status,
)
from .nutrient_deficiency import (
    DeficiencySeverity,
    NutrientDeficiency,
    NutrientType,
    detect_nutrient_deficiencies,
    generate_fertilizer_plan,
    get_nutrient_status_summary,
)
from .pest_assessment import (
    RiskLevel,
    assess_pest_risks,
    get_pest_summary,
    get_pest_types,
)
from .yield_prediction import (
    CropType as YieldCropType,
    get_crop_parameters,
    predict_yield,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Schemas
# ═══════════════════════════════════════════════════════════════════════════════


class IndicesIn(BaseModel):
    """مؤشرات الغطاء النباتي المدخلة"""

    ndvi: float = Field(..., ge=-1, le=1, description="Normalized Difference Vegetation Index")
    evi: float = Field(..., ge=-1, le=1, description="Enhanced Vegetation Index")
    ndre: float = Field(..., ge=-1, le=1, description="Normalized Difference Red Edge")
    lci: float = Field(..., ge=-1, le=1, description="Leaf Chlorophyll Index")
    ndwi: float = Field(..., ge=-1, le=1, description="Normalized Difference Water Index")
    savi: float = Field(..., ge=-1, le=1, description="Soil-Adjusted Vegetation Index")


class ObservationIn(BaseModel):
    """طلب تسجيل رصد جديد"""

    captured_at: datetime = Field(..., description="وقت الالتقاط")
    source: Literal["sentinel-2", "drone", "planet", "landsat", "other"] = Field(
        ..., description="مصدر البيانات"
    )
    growth_stage: GrowthStage = Field(..., description="مرحلة النمو")
    indices: IndicesIn = Field(..., description="المؤشرات")
    cloud_pct: float = Field(default=0.0, ge=0, le=100, description="نسبة الغيوم")
    notes: str | None = Field(default=None, description="ملاحظات")


class ObservationOut(BaseModel):
    """استجابة تسجيل الرصد"""

    observation_id: str
    status: Literal["stored"]
    zone_id: str
    field_id: str


class ActionOut(BaseModel):
    """إجراء موصى به"""

    zone_id: str
    type: Literal["irrigation", "fertilization", "scouting", "none"]
    priority: Literal["P0", "P1", "P2", "P3"]
    title: str
    title_en: str | None = None
    reason: str
    reason_en: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    recommended_window_hours: int | None = None
    recommended_dose_hint: Literal["low", "medium", "high"] | None = None
    severity: str | None = None


class SummaryOut(BaseModel):
    """ملخص تشخيص الحقل"""

    zones_total: int
    zones_critical: int
    zones_warning: int
    zones_ok: int


class MapLayersOut(BaseModel):
    """روابط طبقات الخريطة"""

    ndvi_raster_url: str | None = None
    ndwi_raster_url: str | None = None
    ndre_raster_url: str | None = None
    zones_geojson_url: str


class FieldDiagnosisOut(BaseModel):
    """استجابة تشخيص الحقل الكاملة"""

    field_id: str
    date: str
    summary: SummaryOut
    actions: list[ActionOut]
    map_layers: MapLayersOut


class TimelinePoint(BaseModel):
    """نقطة في السلسلة الزمنية"""

    date: str
    ndvi: float
    evi: float | None = None
    ndre: float | None = None
    ndwi: float | None = None
    lci: float | None = None
    savi: float | None = None


class ZoneTimelineOut(BaseModel):
    """السلسلة الزمنية للمنطقة"""

    zone_id: str
    field_id: str
    series: list[TimelinePoint]


class ZoneCreate(BaseModel):
    """إنشاء منطقة جديدة"""

    name: str
    name_ar: str | None = None
    geometry: dict[str, Any] | None = None
    area_hectares: float | None = None


class VRTFeature(BaseModel):
    """خاصية VRT للتصدير"""

    type: str = "Feature"
    properties: dict[str, Any]
    geometry: dict[str, Any] | None = None


class VRTExportOut(BaseModel):
    """تصدير VRT كـ GeoJSON FeatureCollection"""

    type: str = "FeatureCollection"
    features: list[VRTFeature]
    metadata: dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (استبدله بـ PostgreSQL + PostGIS لاحقاً)
# ═══════════════════════════════════════════════════════════════════════════════

# field_id -> zone_id -> list of observations
OBSERVATIONS: dict[str, dict[str, list[dict[str, Any]]]] = {}

# field_id -> zone_id -> zone_metadata
ZONES: dict[str, dict[str, dict[str, Any]]] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# Application Setup
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌱 Starting Crop Intelligence Service...")

    # Initialize sample data for demo
    _init_sample_data()

    port = os.getenv("PORT", "8095")
    print(f"✅ Crop Intelligence Service ready on port {port}")
    yield
    print("👋 Crop Intelligence Service shutting down")


def _init_sample_data():
    """تهيئة بيانات تجريبية للعرض"""
    field_id = "field_demo"
    ZONES[field_id] = {
        "zone_a": {"name": "Zone A", "name_ar": "المنطقة أ", "area_hectares": 5.2},
        "zone_b": {"name": "Zone B", "name_ar": "المنطقة ب", "area_hectares": 4.8},
        "zone_c": {"name": "Zone C", "name_ar": "المنطقة ج", "area_hectares": 6.1},
    }

    # Sample observations
    OBSERVATIONS[field_id] = {
        "zone_a": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.78,
                    "evi": 0.62,
                    "ndre": 0.21,
                    "lci": 0.32,
                    "ndwi": -0.05,
                    "savi": 0.65,
                },
                "cloud_pct": 5.0,
            }
        ],
        "zone_b": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.65,
                    "evi": 0.52,
                    "ndre": 0.35,
                    "lci": 0.28,
                    "ndwi": 0.02,
                    "savi": 0.55,
                },
                "cloud_pct": 5.0,
            }
        ],
        "zone_c": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.41,
                    "evi": 0.32,
                    "ndre": 0.18,
                    "lci": 0.15,
                    "ndwi": -0.12,
                    "savi": 0.35,
                },
                "cloud_pct": 5.0,
            }
        ],
    }


app = FastAPI(
    title="SAHOOL Crop Health Service",
    description="خدمة تشخيص صحة المحاصيل - Intelligent crop health diagnostics with decision support",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Secure configuration
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "service": "crop_health",
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {
        "service": "SAHOOL Crop Health",
        "version": "1.0.0",
        "description_ar": "خدمة تشخيص صحة المحاصيل",
        "description_en": "Crop health diagnostic service",
        "endpoints": {
            "observations": "/api/v1/fields/{field_id}/zones/{zone_id}/observations",
            "diagnosis": "/api/v1/fields/{field_id}/diagnosis",
            "timeline": "/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            "vrt_export": "/api/v1/fields/{field_id}/vrt",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Zone Management
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/fields/{field_id}/zones")
def create_zone(field_id: str, zone: ZoneCreate):
    """إنشاء منطقة جديدة في الحقل"""
    zone_id = f"zone_{uuid4().hex[:8]}"

    if field_id not in ZONES:
        ZONES[field_id] = {}

    ZONES[field_id][zone_id] = {
        "name": zone.name,
        "name_ar": zone.name_ar,
        "geometry": zone.geometry,
        "area_hectares": zone.area_hectares,
        "created_at": datetime.utcnow().isoformat(),
    }

    return {"zone_id": zone_id, "status": "created"}


@app.get("/api/v1/fields/{field_id}/zones")
def list_zones(field_id: str):
    """قائمة المناطق في الحقل"""
    if field_id not in ZONES:
        return {"zones": [], "count": 0}

    zones = [{"zone_id": zid, **zdata} for zid, zdata in ZONES[field_id].items()]
    return {"zones": zones, "count": len(zones)}


@app.get("/api/v1/fields/{field_id}/zones.geojson")
def get_zones_geojson(field_id: str):
    """تصدير المناطق كـ GeoJSON"""
    if field_id not in ZONES:
        raise HTTPException(status_code=404, detail="Field not found")

    features = []
    for zone_id, zone_data in ZONES[field_id].items():
        features.append(
            {
                "type": "Feature",
                "id": zone_id,
                "properties": {
                    "zone_id": zone_id,
                    "name": zone_data.get("name"),
                    "name_ar": zone_data.get("name_ar"),
                    "area_hectares": zone_data.get("area_hectares"),
                },
                "geometry": zone_data.get("geometry"),
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Observations (Ingest)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post(
    "/api/v1/fields/{field_id}/zones/{zone_id}/observations",
    response_model=ObservationOut,
)
def ingest_observation(field_id: str, zone_id: str, body: ObservationIn):
    """
    تسجيل رصد جديد لمؤشرات الغطاء النباتي

    يستقبل بيانات من Sentinel-2 أو الدرونز أو مصادر أخرى
    """
    obs = body.model_dump()
    obs["captured_at"] = body.captured_at.isoformat()
    obs["indices"] = body.indices.model_dump()

    # Initialize storage
    if field_id not in OBSERVATIONS:
        OBSERVATIONS[field_id] = {}
    if zone_id not in OBSERVATIONS[field_id]:
        OBSERVATIONS[field_id][zone_id] = []

    OBSERVATIONS[field_id][zone_id].append(obs)

    observation_id = f"obs_{field_id}_{zone_id}_{int(body.captured_at.timestamp())}"

    return ObservationOut(
        observation_id=observation_id,
        status="stored",
        zone_id=zone_id,
        field_id=field_id,
    )


@app.get("/api/v1/fields/{field_id}/zones/{zone_id}/observations")
def list_observations(
    field_id: str,
    zone_id: str,
    limit: int = Query(default=50, le=200),
):
    """قائمة الأرصاد للمنطقة"""
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        return {"observations": [], "count": 0}

    obs_list = OBSERVATIONS[field_id][zone_id][-limit:]
    return {"observations": obs_list, "count": len(obs_list)}


# ═══════════════════════════════════════════════════════════════════════════════
# Diagnosis (Decision Engine Output)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/diagnosis")
def get_field_diagnosis(
    field_id: str,
    date_str: str = Query(..., alias="date", description="التاريخ (YYYY-MM-DD)"),
):
    """
    تشخيص كامل للحقل - "الطبيب الزراعي"

    يُرجع:
    - ملخص حالة المناطق
    - قائمة الإجراءات المطلوبة مرتبة بالأولوية
    - روابط طبقات الخريطة
    """
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح، استخدم YYYY-MM-DD")

    if field_id not in OBSERVATIONS:
        raise HTTPException(status_code=404, detail="الحقل غير موجود أو لا توجد أرصاد")

    all_actions: list[dict[str, Any]] = []
    zones = OBSERVATIONS[field_id]

    for zone_id, obs_list in zones.items():
        if not obs_list:
            continue

        # اختر آخر رصد في التاريخ المطلوب أو آخر رصد متاح
        same_day = [
            o for o in obs_list if datetime.fromisoformat(o["captured_at"]).date() == target
        ]
        chosen = same_day[-1] if same_day else obs_list[-1]

        # بناء كائن المؤشرات
        idx_in = chosen["indices"]
        idx = Indices(
            ndvi=idx_in["ndvi"],
            evi=idx_in["evi"],
            ndre=idx_in["ndre"],
            lci=idx_in["lci"],
            ndwi=idx_in["ndwi"],
            savi=idx_in["savi"],
        )

        zone_obs = ZoneObservation(
            zone_id=zone_id,
            growth_stage=GrowthStage(chosen["growth_stage"]),
            indices=idx,
        )

        # تشخيص المنطقة
        actions = diagnose_zone(zone_obs)
        all_actions.extend(actions)

    # حساب الملخص
    zones_total = len(zones)
    zone_statuses = {}
    for action in all_actions:
        zid = action["zone_id"]
        if zid not in zone_statuses:
            zone_statuses[zid] = "ok"
        if action["priority"] == "P0":
            zone_statuses[zid] = "critical"
        elif action["priority"] in ("P1", "P2") and zone_statuses[zid] != "critical":
            zone_statuses[zid] = "warning"

    crit = sum(1 for s in zone_statuses.values() if s == "critical")
    warn = sum(1 for s in zone_statuses.values() if s == "warning")
    ok_count = zones_total - crit - warn

    # ترتيب الإجراءات حسب الأولوية
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    all_actions.sort(key=lambda a: priority_order.get(a["priority"], 9))

    base_url = os.getenv("CDN_BASE_URL", "https://cdn.sahool.io")

    return {
        "field_id": field_id,
        "date": target.isoformat(),
        "summary": {
            "zones_total": zones_total,
            "zones_critical": crit,
            "zones_warning": warn,
            "zones_ok": max(ok_count, 0),
        },
        "actions": all_actions,
        "map_layers": {
            "ndvi_raster_url": f"{base_url}/maps/{field_id}/{target}/ndvi.tiff",
            "ndwi_raster_url": f"{base_url}/maps/{field_id}/{target}/ndwi.tiff",
            "ndre_raster_url": f"{base_url}/maps/{field_id}/{target}/ndre.tiff",
            "zones_geojson_url": f"/api/v1/fields/{field_id}/zones.geojson",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Timeline
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/zones/{zone_id}/timeline")
def get_zone_timeline(
    field_id: str,
    zone_id: str,
    from_date: str = Query(..., alias="from", description="من تاريخ (YYYY-MM-DD)"),
    to_date: str = Query(..., alias="to", description="إلى تاريخ (YYYY-MM-DD)"),
):
    """
    السلسلة الزمنية لمؤشرات المنطقة

    مفيدة لتتبع التغيرات وعرضها في رسم بياني
    """
    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح")

    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        return {"zone_id": zone_id, "field_id": field_id, "series": []}

    obs_list = OBSERVATIONS[field_id][zone_id]

    # فلترة حسب النطاق الزمني
    series = []
    for obs in obs_list:
        obs_date = datetime.fromisoformat(obs["captured_at"]).date()
        if start <= obs_date <= end:
            idx = obs["indices"]
            series.append(
                {
                    "date": obs_date.isoformat(),
                    "ndvi": idx["ndvi"],
                    "evi": idx.get("evi"),
                    "ndre": idx.get("ndre"),
                    "ndwi": idx.get("ndwi"),
                    "lci": idx.get("lci"),
                    "savi": idx.get("savi"),
                }
            )

    # ترتيب زمني
    series.sort(key=lambda x: x["date"])

    return {
        "zone_id": zone_id,
        "field_id": field_id,
        "series": series,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VRT Export (Variable Rate Technology)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/vrt")
def export_vrt(
    field_id: str,
    date_str: str = Query(..., alias="date", description="التاريخ (YYYY-MM-DD)"),
    action_type: str | None = Query(
        default=None, description="نوع الإجراء: irrigation, fertilization, all"
    ),
):
    """
    تصدير VRT للعمليات الزراعية الدقيقة

    يُنتج GeoJSON مع خصائص قابلة للاستخدام مباشرة في:
    - أنظمة الري الذكي
    - آلات التسميد المتغير (VRT)
    - تطبيقات الطيران الزراعي
    """
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح")

    if field_id not in OBSERVATIONS:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    features = []
    zones = OBSERVATIONS[field_id]
    zone_metadata = ZONES.get(field_id, {})

    for zone_id, obs_list in zones.items():
        if not obs_list:
            continue

        # آخر رصد
        same_day = [
            o for o in obs_list if datetime.fromisoformat(o["captured_at"]).date() == target
        ]
        chosen = same_day[-1] if same_day else obs_list[-1]

        idx_in = chosen["indices"]
        idx = Indices(
            ndvi=idx_in["ndvi"],
            evi=idx_in["evi"],
            ndre=idx_in["ndre"],
            lci=idx_in["lci"],
            ndwi=idx_in["ndwi"],
            savi=idx_in["savi"],
        )

        zone_obs = ZoneObservation(
            zone_id=zone_id,
            growth_stage=GrowthStage(chosen["growth_stage"]),
            indices=idx,
        )

        actions = diagnose_zone(zone_obs)

        # فلترة حسب نوع الإجراء
        if action_type and action_type != "all":
            actions = [a for a in actions if a["type"] == action_type]

        # توليد خصائص VRT
        vrt_props = generate_vrt_properties(zone_id, actions)

        # إضافة معلومات المنطقة
        z_meta = zone_metadata.get(zone_id, {})
        vrt_props["name"] = z_meta.get("name", zone_id)
        vrt_props["name_ar"] = z_meta.get("name_ar")
        vrt_props["area_hectares"] = z_meta.get("area_hectares")

        # إضافة المؤشرات الخام
        vrt_props["indices"] = {
            "ndvi": idx.ndvi,
            "ndre": idx.ndre,
            "ndwi": idx.ndwi,
        }

        features.append(
            {
                "type": "Feature",
                "id": zone_id,
                "properties": vrt_props,
                "geometry": z_meta.get("geometry"),
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "field_id": field_id,
            "date": target.isoformat(),
            "export_type": "vrt",
            "generated_at": datetime.utcnow().isoformat(),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Diagnosis (Single Zone)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/diagnose")
def quick_diagnose(body: ObservationIn, zone_id: str = Query(default="zone_temp")):
    """
    تشخيص سريع بدون حفظ

    مفيد للاختبار أو التشخيص الفوري
    """
    idx = Indices(
        ndvi=body.indices.ndvi,
        evi=body.indices.evi,
        ndre=body.indices.ndre,
        lci=body.indices.lci,
        ndwi=body.indices.ndwi,
        savi=body.indices.savi,
    )

    zone_obs = ZoneObservation(
        zone_id=zone_id,
        growth_stage=body.growth_stage,
        indices=idx,
    )

    actions = diagnose_zone(zone_obs)

    return {
        "zone_id": zone_id,
        "status": classify_zone_status(actions),
        "actions": actions,
        "indices_received": body.indices.model_dump(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Disease Detection Endpoints
# نقاط نهاية كشف الأمراض
# ═══════════════════════════════════════════════════════════════════════════════


class DiseaseDetectionRequest(BaseModel):
    """طلب كشف الأمراض"""

    ndvi: float = Field(..., ge=-1, le=1, description="NDVI value")
    evi: float = Field(..., ge=-1, le=1, description="EVI value")
    ndre: float = Field(..., ge=-1, le=1, description="NDRE value")
    ndwi: float = Field(..., ge=-1, le=1, description="NDWI value")
    lci: float = Field(..., ge=-1, le=1, description="LCI value")
    savi: float = Field(..., ge=-1, le=1, description="SAVI value")
    crop_type: CropType = Field(default=CropType.UNKNOWN, description="نوع المحصول")
    humidity_pct: float | None = Field(default=None, ge=0, le=100, description="الرطوبة %")
    temp_c: float | None = Field(default=None, ge=-50, le=60, description="الحرارة °C")


@app.post("/api/v1/disease/detect")
def detect_crop_diseases(body: DiseaseDetectionRequest):
    """
    كشف الأمراض المحتملة من المؤشرات النباتية
    Detect potential diseases from vegetation indices

    Returns diseases with severity, confidence, and treatment recommendations.
    """
    detections = detect_diseases(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
        crop_type=body.crop_type,
        humidity_pct=body.humidity_pct,
        temp_c=body.temp_c,
    )

    health_en, health_ar = get_overall_health_status(detections)

    return {
        "overall_health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
        "detection_count": len(detections),
        "detections": [d.to_dict() for d in detections],
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndre": body.ndre,
            "ndwi": body.ndwi,
            "lci": body.lci,
            "savi": body.savi,
        },
        "environmental_context": {
            "crop_type": body.crop_type.value,
            "humidity_pct": body.humidity_pct,
            "temp_c": body.temp_c,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis")
def analyze_zone_diseases(
    field_id: str,
    zone_id: str,
    humidity_pct: float | None = Query(default=None, ge=0, le=100),
    temp_c: float | None = Query(default=None, ge=-50, le=60),
    crop_type: CropType = Query(default=CropType.UNKNOWN),
):
    """
    تحليل أمراض المنطقة من آخر رصد
    Analyze zone diseases from latest observation

    Combines the latest observation data with optional environmental
    context to detect potential diseases.
    """
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        raise HTTPException(status_code=404, detail="Zone not found or no observations")

    obs_list = OBSERVATIONS[field_id][zone_id]
    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    # Get latest observation
    latest = obs_list[-1]
    idx = latest["indices"]

    # Detect diseases
    detections = detect_diseases(
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndre=idx["ndre"],
        ndwi=idx["ndwi"],
        lci=idx["lci"],
        savi=idx["savi"],
        crop_type=crop_type,
        humidity_pct=humidity_pct,
        temp_c=temp_c,
    )

    health_en, health_ar = get_overall_health_status(detections)

    # Get zone metadata
    zone_meta = ZONES.get(field_id, {}).get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "zone_name_ar": zone_meta.get("name_ar"),
        "observation_date": latest.get("captured_at"),
        "overall_health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
        "detection_count": len(detections),
        "detections": [d.to_dict() for d in detections],
        "indices": idx,
    }


@app.get("/api/v1/disease/types")
def list_disease_types():
    """
    قائمة أنواع الأمراض المدعومة
    List supported disease types
    """
    from .disease_detection import DiseaseType, TreatmentType

    return {
        "disease_types": [{"value": dt.value, "name": dt.name} for dt in DiseaseType],
        "treatment_types": [{"value": tt.value, "name": tt.name} for tt in TreatmentType],
        "crop_types": [{"value": ct.value, "name": ct.name} for ct in CropType],
        "severity_levels": [{"value": ds.value, "name": ds.name} for ds in DiseaseSeverity],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Nutrient Deficiency Endpoints
# نقاط نهاية كشف نقص العناصر الغذائية
# ═══════════════════════════════════════════════════════════════════════════════


class NutrientDetectionRequest(BaseModel):
    """طلب كشف نقص العناصر الغذائية"""

    ndvi: float = Field(..., ge=-1, le=1, description="NDVI value")
    evi: float = Field(..., ge=-1, le=1, description="EVI value")
    ndre: float = Field(..., ge=-1, le=1, description="NDRE value")
    ndwi: float = Field(..., ge=-1, le=1, description="NDWI value")
    lci: float = Field(..., ge=-1, le=1, description="LCI value")
    savi: float = Field(..., ge=-1, le=1, description="SAVI value")
    growth_stage: str = Field(default="vegetative", description="مرحلة النمو")


class FertilizerPlanRequest(BaseModel):
    """طلب خطة التسميد"""

    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)
    field_area_hectares: float = Field(default=1.0, gt=0, description="مساحة الحقل بالهكتار")
    budget_usd: float | None = Field(default=None, ge=0, description="الميزانية بالدولار")


@app.post("/api/v1/nutrients/detect")
def detect_nutrients(body: NutrientDetectionRequest):
    """
    كشف نقص العناصر الغذائية من المؤشرات النباتية
    Detect nutrient deficiencies from vegetation indices

    Returns deficiencies with severity, confidence, and fertilizer recommendations.
    """
    deficiencies = detect_nutrient_deficiencies(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
        growth_stage=body.growth_stage,
    )

    summary = get_nutrient_status_summary(deficiencies)

    return {
        "nutrient_status": summary,
        "deficiency_count": len(deficiencies),
        "deficiencies": [d.to_dict() for d in deficiencies],
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndre": body.ndre,
            "ndwi": body.ndwi,
            "lci": body.lci,
            "savi": body.savi,
        },
        "growth_stage": body.growth_stage,
    }


@app.post("/api/v1/nutrients/fertilizer-plan")
def create_fertilizer_plan(body: FertilizerPlanRequest):
    """
    إنشاء خطة تسميد مخصصة
    Generate a customized fertilizer plan

    Creates a detailed fertilizer application plan based on detected
    deficiencies, field area, and optional budget constraints.
    """
    deficiencies = detect_nutrient_deficiencies(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
    )

    plan = generate_fertilizer_plan(
        deficiencies=deficiencies,
        field_area_hectares=body.field_area_hectares,
        budget_usd=body.budget_usd,
    )

    summary = get_nutrient_status_summary(deficiencies)

    return {
        "nutrient_status": summary,
        "fertilizer_plan": plan,
        "deficiencies_detected": len(deficiencies),
        "field_area_hectares": body.field_area_hectares,
        "budget_usd": body.budget_usd,
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis")
def analyze_zone_nutrients(
    field_id: str,
    zone_id: str,
    field_area_hectares: float = Query(default=1.0, gt=0),
):
    """
    تحليل العناصر الغذائية في المنطقة من آخر رصد
    Analyze zone nutrients from latest observation

    Uses the latest observation data to detect nutrient deficiencies
    and generate fertilizer recommendations.
    """
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        raise HTTPException(status_code=404, detail="Zone not found or no observations")

    obs_list = OBSERVATIONS[field_id][zone_id]
    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    # Get latest observation
    latest = obs_list[-1]
    idx = latest["indices"]

    # Detect deficiencies
    deficiencies = detect_nutrient_deficiencies(
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndre=idx["ndre"],
        ndwi=idx["ndwi"],
        lci=idx["lci"],
        savi=idx["savi"],
        growth_stage=latest.get("growth_stage", "vegetative"),
    )

    summary = get_nutrient_status_summary(deficiencies)
    plan = generate_fertilizer_plan(
        deficiencies=deficiencies,
        field_area_hectares=field_area_hectares,
    )

    # Get zone metadata
    zone_meta = ZONES.get(field_id, {}).get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "zone_name_ar": zone_meta.get("name_ar"),
        "observation_date": latest.get("captured_at"),
        "nutrient_status": summary,
        "deficiency_count": len(deficiencies),
        "deficiencies": [d.to_dict() for d in deficiencies],
        "fertilizer_plan": plan,
        "indices": idx,
    }


@app.get("/api/v1/nutrients/types")
def list_nutrient_types():
    """
    قائمة أنواع العناصر الغذائية المدعومة
    List supported nutrient types
    """
    return {
        "nutrient_types": [{"value": nt.value, "name": nt.name} for nt in NutrientType],
        "severity_levels": [{"value": ds.value, "name": ds.name} for ds in DeficiencySeverity],
        "macronutrients": [
            {"value": nt.value, "name_en": nt.name, "name_ar": _get_nutrient_name_ar(nt)}
            for nt in [
                NutrientType.NITROGEN,
                NutrientType.PHOSPHORUS,
                NutrientType.POTASSIUM,
                NutrientType.CALCIUM,
                NutrientType.MAGNESIUM,
                NutrientType.SULFUR,
            ]
        ],
        "micronutrients": [
            {"value": nt.value, "name_en": nt.name, "name_ar": _get_nutrient_name_ar(nt)}
            for nt in [
                NutrientType.IRON,
                NutrientType.ZINC,
                NutrientType.MANGANESE,
                NutrientType.COPPER,
                NutrientType.BORON,
                NutrientType.MOLYBDENUM,
            ]
        ],
    }


def _get_nutrient_name_ar(nutrient: NutrientType) -> str:
    """Get Arabic name for nutrient"""
    names = {
        NutrientType.NITROGEN: "نيتروجين",
        NutrientType.PHOSPHORUS: "فوسفور",
        NutrientType.POTASSIUM: "بوتاسيوم",
        NutrientType.CALCIUM: "كالسيوم",
        NutrientType.MAGNESIUM: "مغنيسيوم",
        NutrientType.SULFUR: "كبريت",
        NutrientType.IRON: "حديد",
        NutrientType.ZINC: "زنك",
        NutrientType.MANGANESE: "منجنيز",
        NutrientType.COPPER: "نحاس",
        NutrientType.BORON: "بورون",
        NutrientType.MOLYBDENUM: "موليبدنوم",
    }
    return names.get(nutrient, nutrient.value)


# ═══════════════════════════════════════════════════════════════════════════════
# Yield Prediction Endpoints
# نقاط نهاية تنبؤ المحصول
# ═══════════════════════════════════════════════════════════════════════════════


class YieldPredictionRequest(BaseModel):
    """طلب تنبؤ المحصول"""

    crop_type: str = Field(..., description="نوع المحصول")
    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)
    field_area_hectares: float = Field(default=1.0, gt=0, description="مساحة الحقل بالهكتار")
    growth_stage_percent: float = Field(default=50.0, ge=0, le=100, description="نسبة مرحلة النمو")
    historical_yield_kg_ha: float | None = Field(default=None, description="المحصول التاريخي")


@app.post("/api/v1/yield/predict")
def predict_crop_yield(body: YieldPredictionRequest):
    """
    تنبؤ المحصول من المؤشرات النباتية
    Predict crop yield from vegetation indices

    Returns predicted yield with confidence interval and recommendations.
    """
    # Convert crop type string to enum
    try:
        crop = YieldCropType(body.crop_type.lower())
    except ValueError:
        crop = YieldCropType.WHEAT  # Default to wheat if unknown

    prediction = predict_yield(
        crop_type=crop,
        ndvi=body.ndvi,
        evi=body.evi,
        ndwi=body.ndwi,
        ndre=body.ndre,
        lci=body.lci,
        savi=body.savi,
        field_area_hectares=body.field_area_hectares,
        growth_stage_percent=body.growth_stage_percent,
        historical_yield_kg_ha=body.historical_yield_kg_ha,
    )

    return {
        "prediction": prediction.to_dict(),
        "field_area_hectares": body.field_area_hectares,
        "total_predicted_yield_kg": round(
            prediction.predicted_yield_kg_ha * body.field_area_hectares
        ),
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndwi": body.ndwi,
            "ndre": body.ndre,
            "lci": body.lci,
            "savi": body.savi,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction")
def predict_zone_yield(
    field_id: str,
    zone_id: str,
    crop_type: str = Query(default="wheat", description="نوع المحصول"),
    field_area_hectares: float = Query(default=1.0, gt=0),
    growth_stage_percent: float = Query(default=50.0, ge=0, le=100),
):
    """
    تنبؤ محصول المنطقة من آخر رصد
    Predict zone yield from latest observation
    """
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        raise HTTPException(status_code=404, detail="Zone not found or no observations")

    obs_list = OBSERVATIONS[field_id][zone_id]
    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    # Get latest observation
    latest = obs_list[-1]
    idx = latest["indices"]

    # Convert crop type
    try:
        crop = YieldCropType(crop_type.lower())
    except ValueError:
        crop = YieldCropType.WHEAT

    prediction = predict_yield(
        crop_type=crop,
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndwi=idx["ndwi"],
        ndre=idx["ndre"],
        lci=idx["lci"],
        savi=idx["savi"],
        field_area_hectares=field_area_hectares,
        growth_stage_percent=growth_stage_percent,
    )

    zone_meta = ZONES.get(field_id, {}).get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "observation_date": latest.get("captured_at"),
        "prediction": prediction.to_dict(),
        "indices": idx,
    }


@app.get("/api/v1/yield/crop-parameters")
def get_all_crop_parameters(crop_type: str | None = Query(default=None)):
    """
    الحصول على معاملات المحاصيل
    Get crop parameters for yield calculations
    """
    if crop_type:
        try:
            crop = YieldCropType(crop_type.lower())
            return get_crop_parameters(crop)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown crop type: {crop_type}")

    return get_crop_parameters()


# ═══════════════════════════════════════════════════════════════════════════════
# Pest Risk Assessment Endpoints
# نقاط نهاية تقييم مخاطر الآفات
# ═══════════════════════════════════════════════════════════════════════════════


class PestAssessmentRequest(BaseModel):
    """طلب تقييم مخاطر الآفات"""

    temp_c: float = Field(..., ge=-50, le=60, description="الحرارة °م")
    humidity_pct: float = Field(..., ge=0, le=100, description="الرطوبة %")
    ndvi: float = Field(..., ge=-1, le=1, description="NDVI")
    crop_type: str = Field(default="general", description="نوع المحصول")
    season: str = Field(default="summer", description="الموسم")


@app.post("/api/v1/pests/assess")
def assess_pests(body: PestAssessmentRequest):
    """
    تقييم مخاطر الآفات بناءً على الظروف البيئية
    Assess pest risks based on environmental conditions

    Returns list of pest risks sorted by severity.
    """
    risks = assess_pest_risks(
        temp_c=body.temp_c,
        humidity_pct=body.humidity_pct,
        ndvi=body.ndvi,
        crop_type=body.crop_type,
        season=body.season,
    )

    summary = get_pest_summary(risks)

    return {
        "pest_assessment": summary,
        "risks_count": len(risks),
        "risks": [r.to_dict() for r in risks],
        "environmental_conditions": {
            "temp_c": body.temp_c,
            "humidity_pct": body.humidity_pct,
            "ndvi": body.ndvi,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment")
def assess_zone_pests(
    field_id: str,
    zone_id: str,
    temp_c: float = Query(..., ge=-50, le=60),
    humidity_pct: float = Query(..., ge=0, le=100),
    crop_type: str = Query(default="general"),
    season: str = Query(default="summer"),
):
    """
    تقييم مخاطر الآفات في المنطقة
    Assess pest risks for a specific zone
    """
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        raise HTTPException(status_code=404, detail="Zone not found or no observations")

    obs_list = OBSERVATIONS[field_id][zone_id]
    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    # Get latest observation
    latest = obs_list[-1]
    idx = latest["indices"]

    risks = assess_pest_risks(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        ndvi=idx["ndvi"],
        crop_type=crop_type,
        season=season,
    )

    summary = get_pest_summary(risks)
    zone_meta = ZONES.get(field_id, {}).get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "observation_date": latest.get("captured_at"),
        "pest_assessment": summary,
        "risks_count": len(risks),
        "risks": [r.to_dict() for r in risks],
        "indices": idx,
    }


@app.get("/api/v1/pests/types")
def list_pest_types():
    """
    قائمة أنواع الآفات المدعومة
    List supported pest types
    """
    return {
        "pest_types": get_pest_types(),
        "risk_levels": [{"value": rl.value, "name": rl.name} for rl in RiskLevel],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Comprehensive Analysis Endpoint
# نقطة نهاية التحليل الشامل
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/comprehensive-analysis")
def comprehensive_analysis(
    ndvi: float = Query(..., ge=-1, le=1),
    evi: float = Query(..., ge=-1, le=1),
    ndre: float = Query(..., ge=-1, le=1),
    ndwi: float = Query(..., ge=-1, le=1),
    lci: float = Query(..., ge=-1, le=1),
    savi: float = Query(..., ge=-1, le=1),
    crop_type: str = Query(default="wheat"),
    temp_c: float = Query(default=25, ge=-50, le=60),
    humidity_pct: float = Query(default=50, ge=0, le=100),
    field_area_hectares: float = Query(default=1.0, gt=0),
):
    """
    تحليل شامل للحقل
    Comprehensive field analysis

    Combines disease detection, nutrient analysis, yield prediction, and pest assessment.
    """
    # Convert crop type
    try:
        yield_crop = YieldCropType(crop_type.lower())
    except ValueError:
        yield_crop = YieldCropType.WHEAT

    try:
        disease_crop = CropType(crop_type.lower())
    except ValueError:
        disease_crop = CropType.UNKNOWN

    # Disease detection
    diseases = detect_diseases(
        ndvi=ndvi,
        evi=evi,
        ndre=ndre,
        ndwi=ndwi,
        lci=lci,
        savi=savi,
        crop_type=disease_crop,
        humidity_pct=humidity_pct,
        temp_c=temp_c,
    )
    health_en, health_ar = get_overall_health_status(diseases)

    # Nutrient deficiencies
    deficiencies = detect_nutrient_deficiencies(
        ndvi=ndvi,
        evi=evi,
        ndre=ndre,
        ndwi=ndwi,
        lci=lci,
        savi=savi,
    )
    nutrient_summary = get_nutrient_status_summary(deficiencies)

    # Yield prediction
    yield_pred = predict_yield(
        crop_type=yield_crop,
        ndvi=ndvi,
        evi=evi,
        ndwi=ndwi,
        ndre=ndre,
        lci=lci,
        savi=savi,
        field_area_hectares=field_area_hectares,
    )

    # Pest assessment
    pest_risks = assess_pest_risks(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        ndvi=ndvi,
        crop_type=crop_type,
    )
    pest_summary = get_pest_summary(pest_risks)

    # Overall status
    if health_en in ["critical", "poor"] or nutrient_summary["overall_status_en"] == "Critical":
        overall_status = "critical"
    elif health_en == "fair" or nutrient_summary["overall_status_en"] == "Deficient":
        overall_status = "warning"
    else:
        overall_status = "good"

    return {
        "overall_status": overall_status,
        "crop_type": crop_type,
        "field_area_hectares": field_area_hectares,
        "health_assessment": {
            "status_en": health_en,
            "status_ar": health_ar,
            "disease_count": len(diseases),
            "diseases": [d.to_dict() for d in diseases[:3]],  # Top 3
        },
        "nutrient_assessment": {
            **nutrient_summary,
            "deficiency_count": len(deficiencies),
            "deficiencies": [d.to_dict() for d in deficiencies[:3]],  # Top 3
        },
        "yield_prediction": yield_pred.to_dict(),
        "pest_assessment": {
            **pest_summary,
            "risks": [r.to_dict() for r in pest_risks[:3]],  # Top 3
        },
        "input_indices": {
            "ndvi": ndvi,
            "evi": evi,
            "ndre": ndre,
            "ndwi": ndwi,
            "lci": lci,
            "savi": savi,
        },
        "environmental_context": {
            "temp_c": temp_c,
            "humidity_pct": humidity_pct,
        },
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8095))
    uvicorn.run(app, host="0.0.0.0", port=port)
