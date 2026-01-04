"""
SAHOOL Field Service - Main API
خدمة إدارة الحقول الزراعية والحدود الجغرافية
Port: 3000
"""

import os
import sys
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../shared/config"))
try:
    from cors_config import setup_cors_middleware
except ImportError:
    # Fallback if shared config not available
    setup_cors_middleware = None

import logging

from .events import get_publisher
from .geo import (
    calculate_centroid,
    calculate_polygon_area,
    check_polygon_overlap,
    polygon_to_geojson,
    polygon_to_kml,
    validate_polygon,
)
from .models import (
    AreaCalculationResponse,
    BoundaryUpdate,
    CropSeasonClose,
    CropSeasonCreate,
    CropSeasonResponse,
    CropSeasonStatus,
    FieldCreate,
    FieldDetailResponse,
    FieldResponse,
    FieldStatsResponse,
    FieldStatus,
    FieldUpdate,
    GeoPoint,
    NDVIRecord,
    OverlapCheckRequest,
    OverlapCheckResponse,
    UserFieldsStats,
    ZoneCreate,
    ZoneResponse,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============== Authentication ==============


def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")
) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ============== In-Memory Data Store ==============
# للتطوير فقط - استخدم قاعدة بيانات في الإنتاج

_fields: dict = {}
_seasons: dict = {}
_zones: dict = {}
_ndvi_history: dict = {}  # field_id -> [NDVIRecord]


# ============== Application Lifecycle ==============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    logger.info("Starting Field Service...")

    # الاتصال بـ NATS
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        if publisher:
            logger.info("NATS connected")
    except Exception as e:
        logger.warning(f"NATS connection failed: {e}")
        app.state.publisher = None

    logger.info("Field Service ready on port 8115")
    yield

    # التنظيف
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.close()
    logger.info("Field Service shutting down")


# ============== Application Setup ==============


app = FastAPI(
    title="SAHOOL Field Service",
    description="""
    خدمة إدارة الحقول الزراعية والحدود الجغرافية والمواسم

    ## الميزات الرئيسية

    - إدارة الحقول (إنشاء، تحديث، حذف)
    - إدارة الحدود الجغرافية (GeoJSON)
    - تقسيم الحقول إلى مناطق
    - تتبع مواسم المحاصيل
    - سجل NDVI للحقل
    - تصدير KML لـ Google Earth
    """,
    version="16.0.0",
    lifespan=lifespan,
)

# CORS - Use centralized secure configuration
if setup_cors_middleware:
    setup_cors_middleware(app)
else:
    # Fallback CORS configuration if shared config not available
    from fastapi.middleware.cors import CORSMiddleware

    CORS_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:8080",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )


# ============== Health Endpoints ==============


@app.get("/health")
def health():
    """فحص الصحة - Health check with dependencies"""
    return {
        "status": "healthy",
        "service": "field-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "dependencies": {
            "nats": (
                "connected"
                if (hasattr(app.state, "publisher") and app.state.publisher is not None)
                else "disconnected"
            )
        },
    }


@app.get("/healthz")
def healthz():
    """فحص الصحة - Kubernetes liveness probe"""
    return {
        "status": "healthy",
        "service": "field-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz")
def readiness():
    """فحص الجاهزية - Kubernetes readiness probe"""
    return {
        "status": "ready",
        "nats": hasattr(app.state, "publisher") and app.state.publisher is not None,
    }


# ============== Field CRUD Endpoints ==============


@app.post("/fields", response_model=FieldResponse, status_code=201)
async def create_field(field: FieldCreate, tenant_id: str = Depends(get_tenant_id)):
    """إنشاء حقل جديد"""
    # Validate tenant matches the request
    if field.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    field_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    # التحقق من الحدود إذا وجدت
    if field.boundary:
        is_valid, error = validate_polygon(field.boundary.coordinates)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"حدود غير صالحة: {error}")

    field_data = {
        "id": field_id,
        "tenant_id": field.tenant_id,
        "user_id": field.user_id,
        "name": field.name,
        "name_en": field.name_en,
        "status": FieldStatus.ACTIVE.value,
        "location": field.location.model_dump(),
        "boundary": field.boundary.model_dump() if field.boundary else None,
        "area_hectares": field.area_hectares,
        "soil_type": field.soil_type.value if field.soil_type else None,
        "irrigation_source": (
            field.irrigation_source.value if field.irrigation_source else None
        ),
        "current_crop": field.current_crop,
        "metadata": field.metadata or {},
        "created_at": now,
        "updated_at": now,
    }

    _fields[field_id] = field_data
    _ndvi_history[field_id] = []

    # نشر الحدث
    if app.state.publisher:
        try:
            await app.state.publisher.publish_field_created(
                tenant_id=field.tenant_id,
                field_id=field_id,
                user_id=field.user_id,
                field_name=field.name,
                area_hectares=field.area_hectares,
                location=field.location.model_dump(),
            )
        except Exception as e:
            logger.warning(f"Failed to publish field.created event: {e}")

    return FieldResponse(**field_data)


@app.get("/fields/{field_id}", response_model=FieldDetailResponse)
async def get_field(field_id: str, tenant_id: str = Depends(get_tenant_id)):
    """جلب تفاصيل حقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]
    # Validate tenant access
    if field_data["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # جلب البيانات الإضافية
    field_zones = [z for z in _zones.values() if z["field_id"] == field_id]
    field_seasons = [s for s in _seasons.values() if s["field_id"] == field_id]

    # أحدث NDVI
    ndvi_records = _ndvi_history.get(field_id, [])
    latest_ndvi = ndvi_records[-1] if ndvi_records else None

    # اتجاه NDVI
    ndvi_trend = None
    if len(ndvi_records) >= 2:
        first = ndvi_records[0]["mean"]
        last = ndvi_records[-1]["mean"]
        change_pct = ((last - first) / abs(first)) * 100 if first != 0 else 0

        if change_pct > 5:
            direction = "increasing"
        elif change_pct < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        ndvi_trend = {
            "direction": direction,
            "change_percent": round(change_pct, 2),
            "period_days": 30,
            "start_value": first,
            "end_value": last,
        }

    return FieldDetailResponse(
        **field_data,
        zones_count=len(field_zones),
        seasons_count=len(field_seasons),
        latest_ndvi=latest_ndvi,
        ndvi_trend=ndvi_trend,
    )


@app.get("/fields")
async def list_fields(
    user_id: str = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
):
    """قائمة الحقول"""
    # Filter by tenant from header (required)
    filtered = [f for f in _fields.values() if f["tenant_id"] == tenant_id]
    if user_id:
        filtered = [f for f in filtered if f["user_id"] == user_id]
    if status:
        filtered = [f for f in filtered if f["status"] == status]

    total = len(filtered)
    items = filtered[skip : skip + limit]

    return {
        "items": [FieldResponse(**f) for f in items],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@app.patch("/fields/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: str, update: FieldUpdate, tenant_id: str = Depends(get_tenant_id)
):
    """تحديث بيانات حقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]
    # Validate tenant access
    if field_data["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    update_dict = update.model_dump(exclude_unset=True)
    updated_fields = []

    for key, value in update_dict.items():
        if value is not None:
            if key == "location":
                field_data[key] = (
                    value.model_dump() if hasattr(value, "model_dump") else value
                )
            elif key in ["soil_type", "irrigation_source", "status"]:
                field_data[key] = value.value if hasattr(value, "value") else value
            else:
                field_data[key] = value
            updated_fields.append(key)

    field_data["updated_at"] = datetime.now(UTC).isoformat()
    _fields[field_id] = field_data

    # نشر الحدث
    if app.state.publisher and updated_fields:
        with suppress(Exception):
            await app.state.publisher.publish_field_updated(
                tenant_id=field_data["tenant_id"],
                field_id=field_id,
                updated_fields=updated_fields,
            )

    return FieldResponse(**field_data)


@app.delete("/fields/{field_id}")
async def delete_field(field_id: str, tenant_id: str = Depends(get_tenant_id)):
    """حذف حقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]
    # Validate tenant access
    if field_data["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    del _fields[field_id]

    # حذف البيانات المرتبطة
    _ndvi_history.pop(field_id, None)

    zones_to_delete = [z_id for z_id, z in _zones.items() if z["field_id"] == field_id]
    for z_id in zones_to_delete:
        del _zones[z_id]

    seasons_to_delete = [
        s_id for s_id, s in _seasons.items() if s["field_id"] == field_id
    ]
    for s_id in seasons_to_delete:
        del _seasons[s_id]

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_field_deleted(
                tenant_id=field_data["tenant_id"],
                field_id=field_id,
                user_id=field_data["user_id"],
            )

    return {"status": "deleted", "field_id": field_id}


# ============== Boundary Endpoints ==============


@app.put("/fields/{field_id}/boundary", response_model=AreaCalculationResponse)
async def update_boundary(field_id: str, update: BoundaryUpdate):
    """تحديث حدود الحقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    # التحقق من الحدود
    is_valid, error = validate_polygon(update.boundary.coordinates)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"حدود غير صالحة: {error}")

    field_data = _fields[field_id]
    old_area = field_data["area_hectares"]

    # حساب المساحة الجديدة
    new_area = calculate_polygon_area(update.boundary.coordinates)
    centroid_lat, centroid_lng = calculate_centroid(update.boundary.coordinates)

    field_data["boundary"] = update.boundary.model_dump()
    if update.recalculate_area:
        field_data["area_hectares"] = round(new_area, 4)

    field_data["updated_at"] = datetime.now(UTC).isoformat()
    _fields[field_id] = field_data

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_boundary_updated(
                tenant_id=field_data["tenant_id"],
                field_id=field_id,
                new_area_hectares=new_area,
                centroid={"lat": centroid_lat, "lng": centroid_lng},
            )

    diff_pct = ((new_area - old_area) / old_area * 100) if old_area > 0 else 0

    return AreaCalculationResponse(
        field_id=field_id,
        calculated_area_hectares=round(new_area, 4),
        stored_area_hectares=field_data["area_hectares"],
        difference_percent=round(diff_pct, 2),
        centroid=GeoPoint(lat=centroid_lat, lng=centroid_lng),
    )


@app.get("/fields/{field_id}/area", response_model=AreaCalculationResponse)
async def calculate_field_area(field_id: str):
    """حساب مساحة الحقل من الحدود"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]

    if not field_data.get("boundary"):
        raise HTTPException(status_code=400, detail="لا توجد حدود محددة للحقل")

    coords = field_data["boundary"]["coordinates"]
    calculated = calculate_polygon_area(coords)
    centroid_lat, centroid_lng = calculate_centroid(coords)

    stored = field_data["area_hectares"]
    diff_pct = ((calculated - stored) / stored * 100) if stored > 0 else 0

    return AreaCalculationResponse(
        field_id=field_id,
        calculated_area_hectares=round(calculated, 4),
        stored_area_hectares=stored,
        difference_percent=round(diff_pct, 2),
        centroid=GeoPoint(lat=centroid_lat, lng=centroid_lng),
    )


@app.post("/fields/check-overlap", response_model=OverlapCheckResponse)
async def check_overlap(request: OverlapCheckRequest):
    """فحص تداخل الحدود مع حقول أخرى"""
    overlapping = []
    total_overlap = 0.0

    for fid, field in _fields.items():
        if request.exclude_field_id and fid == request.exclude_field_id:
            continue

        if not field.get("boundary"):
            continue

        has_overlap, overlap_area = check_polygon_overlap(
            request.boundary.coordinates, field["boundary"]["coordinates"]
        )

        if has_overlap:
            overlapping.append(
                {
                    "field_id": fid,
                    "field_name": field["name"],
                    "overlap_area_hectares": round(overlap_area, 4),
                }
            )
            total_overlap += overlap_area

    return OverlapCheckResponse(
        has_overlap=len(overlapping) > 0,
        overlapping_fields=overlapping,
        overlap_area_hectares=round(total_overlap, 4),
    )


# ============== Export Endpoints ==============


@app.get("/fields/{field_id}/export/kml")
async def export_field_kml(field_id: str):
    """تصدير الحقل بصيغة KML"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]

    if not field_data.get("boundary"):
        raise HTTPException(status_code=400, detail="لا توجد حدود للتصدير")

    kml_content = polygon_to_kml(
        field_id=field_id,
        field_name=field_data["name"],
        coordinates=field_data["boundary"]["coordinates"],
        description=f"Area: {field_data['area_hectares']} hectares",
    )

    return Response(
        content=kml_content,
        media_type="application/vnd.google-earth.kml+xml",
        headers={"Content-Disposition": f'attachment; filename="{field_id}.kml"'},
    )


@app.get("/fields/{field_id}/export/geojson")
async def export_field_geojson(field_id: str):
    """تصدير الحقل بصيغة GeoJSON"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]

    if not field_data.get("boundary"):
        raise HTTPException(status_code=400, detail="لا توجد حدود للتصدير")

    geojson = polygon_to_geojson(
        field_id=field_id,
        field_name=field_data["name"],
        coordinates=field_data["boundary"]["coordinates"],
        properties={
            "area_hectares": field_data["area_hectares"],
            "crop_type": field_data.get("current_crop"),
            "soil_type": field_data.get("soil_type"),
        },
    )

    return geojson


# ============== Crop Season Endpoints ==============


@app.post(
    "/fields/{field_id}/crops", response_model=CropSeasonResponse, status_code=201
)
async def start_crop_season(field_id: str, season: CropSeasonCreate):
    """بدء موسم محصول جديد"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    # التحقق من عدم وجود موسم نشط
    active_seasons = [
        s
        for s in _seasons.values()
        if s["field_id"] == field_id and s["status"] == CropSeasonStatus.ACTIVE.value
    ]
    if active_seasons:
        raise HTTPException(
            status_code=400, detail="يوجد موسم نشط بالفعل. يجب إنهاءه أولاً"
        )

    season_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    season_data = {
        "id": season_id,
        "field_id": field_id,
        "tenant_id": _fields[field_id]["tenant_id"],
        "crop_type": season.crop_type,
        "variety": season.variety,
        "planting_date": season.planting_date,
        "expected_harvest": season.expected_harvest,
        "harvest_date": None,
        "status": CropSeasonStatus.ACTIVE.value,
        "expected_yield_kg": None,
        "actual_yield_kg": None,
        "seed_source": season.seed_source,
        "notes": season.notes,
        "created_at": now,
    }

    _seasons[season_id] = season_data

    # تحديث المحصول الحالي في الحقل
    _fields[field_id]["current_crop"] = season.crop_type
    _fields[field_id]["updated_at"] = now

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_season_started(
                tenant_id=season_data["tenant_id"],
                field_id=field_id,
                season_id=season_id,
                crop_type=season.crop_type,
                planting_date=season.planting_date,
            )

    return CropSeasonResponse(**season_data)


@app.get("/fields/{field_id}/crops/history")
async def get_crop_history(field_id: str):
    """سجل مواسم المحاصيل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_seasons = [
        CropSeasonResponse(**s) for s in _seasons.values() if s["field_id"] == field_id
    ]

    # ترتيب حسب تاريخ الزراعة
    field_seasons.sort(key=lambda x: x.planting_date, reverse=True)

    return {
        "field_id": field_id,
        "seasons": field_seasons,
        "total": len(field_seasons),
    }


@app.post("/fields/{field_id}/crops/current/close", response_model=CropSeasonResponse)
async def close_crop_season(field_id: str, close_data: CropSeasonClose):
    """إنهاء الموسم الحالي"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    # البحث عن الموسم النشط
    active_season = None
    for s_id, s in _seasons.items():
        if s["field_id"] == field_id and s["status"] == CropSeasonStatus.ACTIVE.value:
            active_season = (s_id, s)
            break

    if not active_season:
        raise HTTPException(status_code=404, detail="لا يوجد موسم نشط")

    season_id, season_data = active_season

    season_data["status"] = CropSeasonStatus.HARVESTED.value
    season_data["harvest_date"] = close_data.harvest_date
    season_data["actual_yield_kg"] = close_data.actual_yield_kg
    if close_data.notes:
        season_data["notes"] = (
            season_data.get("notes") or ""
        ) + f"\n{close_data.notes}"

    _seasons[season_id] = season_data

    # مسح المحصول الحالي
    _fields[field_id]["current_crop"] = None
    _fields[field_id]["updated_at"] = datetime.now(UTC).isoformat()

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_season_closed(
                tenant_id=season_data["tenant_id"],
                field_id=field_id,
                season_id=season_id,
                crop_type=season_data["crop_type"],
                harvest_date=close_data.harvest_date,
                actual_yield_kg=close_data.actual_yield_kg,
            )

    return CropSeasonResponse(**season_data)


# ============== Zone Endpoints ==============


@app.post("/fields/{field_id}/zones", response_model=ZoneResponse, status_code=201)
async def create_zone(field_id: str, zone: ZoneCreate):
    """إنشاء منطقة داخل الحقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    # التحقق من الحدود
    is_valid, error = validate_polygon(zone.boundary.coordinates)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"حدود غير صالحة: {error}")

    zone_id = str(uuid4())
    zone_area = calculate_polygon_area(zone.boundary.coordinates)
    now = datetime.now(UTC).isoformat()

    zone_data = {
        "id": zone_id,
        "field_id": field_id,
        "tenant_id": _fields[field_id]["tenant_id"],
        "name": zone.name,
        "name_ar": zone.name_ar,
        "boundary": zone.boundary.model_dump(),
        "area_hectares": round(zone_area, 4),
        "purpose": zone.purpose.value,
        "notes": zone.notes,
        "created_at": now,
    }

    _zones[zone_id] = zone_data

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_zone_created(
                tenant_id=zone_data["tenant_id"],
                field_id=field_id,
                zone_id=zone_id,
                zone_name=zone.name,
                area_hectares=zone_area,
            )

    return ZoneResponse(**zone_data)


@app.get("/fields/{field_id}/zones")
async def list_zones(field_id: str):
    """قائمة مناطق الحقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_zones = [
        ZoneResponse(**z) for z in _zones.values() if z["field_id"] == field_id
    ]

    return {
        "field_id": field_id,
        "zones": field_zones,
        "total": len(field_zones),
    }


@app.delete("/zones/{zone_id}")
async def delete_zone(zone_id: str):
    """حذف منطقة"""
    if zone_id not in _zones:
        raise HTTPException(status_code=404, detail="المنطقة غير موجودة")

    zone_data = _zones[zone_id]
    del _zones[zone_id]

    # نشر الحدث
    if app.state.publisher:
        with suppress(Exception):
            await app.state.publisher.publish_zone_deleted(
                tenant_id=zone_data["tenant_id"],
                field_id=zone_data["field_id"],
                zone_id=zone_id,
            )

    return {"status": "deleted", "zone_id": zone_id}


# ============== NDVI History Endpoints ==============


@app.get("/fields/{field_id}/ndvi/history")
async def get_ndvi_history(
    field_id: str,
    limit: int = Query(30, ge=1, le=365),
):
    """سجل NDVI للحقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    records = _ndvi_history.get(field_id, [])
    recent = records[-limit:] if len(records) > limit else records

    return {
        "field_id": field_id,
        "records": recent,
        "total": len(records),
    }


@app.post("/fields/{field_id}/ndvi", status_code=201)
async def add_ndvi_record(field_id: str, record: NDVIRecord):
    """إضافة سجل NDVI"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    if field_id not in _ndvi_history:
        _ndvi_history[field_id] = []

    _ndvi_history[field_id].append(record.model_dump())

    return {"status": "recorded", "field_id": field_id, "date": record.date}


# ============== Statistics Endpoints ==============


@app.get("/fields/{field_id}/stats", response_model=FieldStatsResponse)
async def get_field_stats(field_id: str):
    """إحصائيات الحقل"""
    if field_id not in _fields:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    field_data = _fields[field_id]
    field_seasons = [s for s in _seasons.values() if s["field_id"] == field_id]

    # المحاصيل المزروعة
    crops_grown = list({s["crop_type"] for s in field_seasons})

    # متوسط الإنتاج
    yields = [s["actual_yield_kg"] for s in field_seasons if s.get("actual_yield_kg")]
    avg_yield = None
    if yields and field_data["area_hectares"] > 0:
        avg_yield = sum(yields) / len(yields) / field_data["area_hectares"]

    # أفضل موسم
    best_season = None
    if yields:
        best = max(
            [s for s in field_seasons if s.get("actual_yield_kg")],
            key=lambda x: x["actual_yield_kg"],
        )
        best_season = {
            "crop": best["crop_type"],
            "year": best["planting_date"][:4],
            "yield_kg": best["actual_yield_kg"],
        }

    # إحصائيات NDVI
    ndvi_records = _ndvi_history.get(field_id, [])
    ndvi_stats = None
    if ndvi_records:
        means = [r["mean"] for r in ndvi_records]
        ndvi_stats = {
            "avg": round(sum(means) / len(means), 3),
            "min": round(min(means), 3),
            "max": round(max(means), 3),
            "records_count": len(ndvi_records),
        }

    return FieldStatsResponse(
        field_id=field_id,
        area_hectares=field_data["area_hectares"],
        seasons_count=len(field_seasons),
        crops_grown=crops_grown,
        average_yield_kg_ha=round(avg_yield, 2) if avg_yield else None,
        best_season=best_season,
        ndvi_stats=ndvi_stats,
    )


@app.get("/users/{user_id}/fields/stats", response_model=UserFieldsStats)
async def get_user_fields_stats(user_id: str, tenant_id: str = Query(...)):
    """إحصائيات حقول المستخدم"""
    user_fields = [f for f in _fields.values() if f["user_id"] == user_id]

    if not user_fields:
        return UserFieldsStats(
            user_id=user_id,
            tenant_id=tenant_id,
            fields_count=0,
            total_area_hectares=0,
            active_fields=0,
            active_seasons=0,
            crops_summary={},
        )

    active_fields = [f for f in user_fields if f["status"] == FieldStatus.ACTIVE.value]
    total_area = sum(f["area_hectares"] for f in user_fields)

    # المواسم النشطة
    field_ids = {f["id"] for f in user_fields}
    active_seasons = [
        s
        for s in _seasons.values()
        if s["field_id"] in field_ids and s["status"] == CropSeasonStatus.ACTIVE.value
    ]

    # ملخص المحاصيل
    crops_summary: dict = {}
    for s in _seasons.values():
        if s["field_id"] in field_ids:
            crop = s["crop_type"]
            crops_summary[crop] = crops_summary.get(crop, 0) + 1

    return UserFieldsStats(
        user_id=user_id,
        tenant_id=tenant_id,
        fields_count=len(user_fields),
        total_area_hectares=round(total_area, 2),
        active_fields=len(active_fields),
        active_seasons=len(active_seasons),
        crops_summary=crops_summary,
    )


# ============== Main Entry Point ==============


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8115))
    uvicorn.run(app, host="0.0.0.0", port=port)
