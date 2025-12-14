"""
SAHOOL Crop Health Service
خدمة صحة المحاصيل - تشخيص ذكي للحقول الزراعية
Port: 8100
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .decision_engine import (
    GrowthStage,
    Indices,
    ZoneObservation,
    classify_zone_status,
    diagnose_zone,
    generate_vrt_properties,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Schemas
# ═══════════════════════════════════════════════════════════════════════════════


class IndicesIn(BaseModel):
    """مؤشرات الغطاء النباتي المدخلة"""

    ndvi: float = Field(
        ..., ge=-1, le=1, description="Normalized Difference Vegetation Index"
    )
    evi: float = Field(..., ge=-1, le=1, description="Enhanced Vegetation Index")
    ndre: float = Field(..., ge=-1, le=1, description="Normalized Difference Red Edge")
    lci: float = Field(..., ge=-1, le=1, description="Leaf Chlorophyll Index")
    ndwi: float = Field(
        ..., ge=-1, le=1, description="Normalized Difference Water Index"
    )
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
    notes: Optional[str] = Field(default=None, description="ملاحظات")


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
    title_en: Optional[str] = None
    reason: str
    reason_en: Optional[str] = None
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommended_window_hours: Optional[int] = None
    recommended_dose_hint: Optional[Literal["low", "medium", "high"]] = None
    severity: Optional[str] = None


class SummaryOut(BaseModel):
    """ملخص تشخيص الحقل"""

    zones_total: int
    zones_critical: int
    zones_warning: int
    zones_ok: int


class MapLayersOut(BaseModel):
    """روابط طبقات الخريطة"""

    ndvi_raster_url: Optional[str] = None
    ndwi_raster_url: Optional[str] = None
    ndre_raster_url: Optional[str] = None
    zones_geojson_url: str


class FieldDiagnosisOut(BaseModel):
    """استجابة تشخيص الحقل الكاملة"""

    field_id: str
    date: str
    summary: SummaryOut
    actions: List[ActionOut]
    map_layers: MapLayersOut


class TimelinePoint(BaseModel):
    """نقطة في السلسلة الزمنية"""

    date: str
    ndvi: float
    evi: Optional[float] = None
    ndre: Optional[float] = None
    ndwi: Optional[float] = None
    lci: Optional[float] = None
    savi: Optional[float] = None


class ZoneTimelineOut(BaseModel):
    """السلسلة الزمنية للمنطقة"""

    zone_id: str
    field_id: str
    series: List[TimelinePoint]


class ZoneCreate(BaseModel):
    """إنشاء منطقة جديدة"""

    name: str
    name_ar: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None
    area_hectares: Optional[float] = None


class VRTFeature(BaseModel):
    """خاصية VRT للتصدير"""

    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Optional[Dict[str, Any]] = None


class VRTExportOut(BaseModel):
    """تصدير VRT كـ GeoJSON FeatureCollection"""

    type: str = "FeatureCollection"
    features: List[VRTFeature]
    metadata: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (استبدله بـ PostgreSQL + PostGIS لاحقاً)
# ═══════════════════════════════════════════════════════════════════════════════

# field_id -> zone_id -> list of observations
OBSERVATIONS: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

# field_id -> zone_id -> zone_metadata
ZONES: Dict[str, Dict[str, Dict[str, Any]]] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# Application Setup
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌱 Starting Crop Health Service...")

    # Initialize sample data for demo
    _init_sample_data()

    print("✅ Crop Health Service ready on port 8100")
    yield
    print("👋 Crop Health Service shutting down")


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        raise HTTPException(
            status_code=400, detail="تنسيق تاريخ غير صالح، استخدم YYYY-MM-DD"
        )

    if field_id not in OBSERVATIONS:
        raise HTTPException(status_code=404, detail="الحقل غير موجود أو لا توجد أرصاد")

    all_actions: List[Dict[str, Any]] = []
    zones = OBSERVATIONS[field_id]

    for zone_id, obs_list in zones.items():
        if not obs_list:
            continue

        # اختر آخر رصد في التاريخ المطلوب أو آخر رصد متاح
        same_day = [
            o
            for o in obs_list
            if datetime.fromisoformat(o["captured_at"]).date() == target
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
    action_type: Optional[str] = Query(
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
            o
            for o in obs_list
            if datetime.fromisoformat(o["captured_at"]).date() == target
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8100))
    uvicorn.run(app, host="0.0.0.0", port=port)
