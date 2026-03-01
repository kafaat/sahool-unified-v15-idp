"""
SAHOOL Logistics Service - API v1 Reports Routes
خدمة اللوجستيات - مسارات تقارير API الإصدار الأول

This module contains report endpoints for the logistics service.
The main CRUD routes are defined in src/main.py.

Report endpoints:
- /api/v1/reports/daily - Daily logistics report (تقرير يومي)
- /api/v1/reports/weekly - Weekly logistics report (تقرير أسبوعي)
- /api/v1/reports/monthly - Monthly logistics report (تقرير شهري)
"""

import calendar
import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create a router for report endpoints
router = APIRouter(prefix="/api/v1", tags=["logistics-reports"])


# ─────────────────────────────────────────────────────────────────────────────
# Response Models - نماذج الاستجابة
# ─────────────────────────────────────────────────────────────────────────────


class VehicleSummary(BaseModel):
    """Vehicle fleet summary | ملخص أسطول المركبات"""

    total: int = Field(description="Total vehicles | إجمالي المركبات")
    active: int = Field(description="Active vehicles (in_transit + loading + unloading) | المركبات النشطة")
    idle: int = Field(description="Idle vehicles (available) | المركبات الخاملة")
    maintenance: int = Field(description="In maintenance | في الصيانة")
    out_of_service: int = Field(0, description="Out of service | خارج الخدمة")
    utilization_rate: float = Field(description="Utilization rate % | نسبة الاستخدام")
    message: str = Field("", description="Summary message")
    message_ar: str = Field("", description="ملخص بالعربية")


class ShipmentSummary(BaseModel):
    """Shipment status summary | ملخص حالة الشحنات"""

    total: int = Field(description="Total shipments | إجمالي الشحنات")
    pending: int = Field(description="Pending (scheduled + collecting) | معلقة")
    in_transit: int = Field(description="In transit | في الطريق")
    delivered: int = Field(description="Delivered | تم التسليم")
    cancelled: int = Field(description="Cancelled | ملغاة")
    on_time_rate: float = Field(description="On-time delivery rate % | نسبة التسليم في الوقت")
    message: str = Field("", description="Summary message")
    message_ar: str = Field("", description="ملخص بالعربية")


class CollectionSummary(BaseModel):
    """Harvest collection summary | ملخص جمع المحاصيل"""

    total_collections: int = Field(description="Total collections | إجمالي عمليات الجمع")
    total_weight_kg: float = Field(description="Total estimated weight (kg) | الوزن الإجمالي المقدر (كجم)")
    actual_weight_kg: float = Field(0.0, description="Total actual weight (kg) | الوزن الفعلي (كجم)")
    fields_covered: int = Field(description="Distinct fields covered | الحقول المغطاة")
    by_crop: list[dict[str, Any]] = Field(
        default_factory=list, description="Breakdown by crop type | تفصيل حسب نوع المحصول"
    )
    by_priority: dict[str, int] = Field(
        default_factory=dict, description="Breakdown by priority | تفصيل حسب الأولوية"
    )
    message: str = Field("", description="Summary message")
    message_ar: str = Field("", description="ملخص بالعربية")


class CostSummary(BaseModel):
    """Cost summary | ملخص التكاليف"""

    fuel_cost: float = Field(description="Estimated fuel cost (SAR) | تكلفة الوقود المقدرة")
    maintenance_cost: float = Field(description="Estimated maintenance cost (SAR) | تكلفة الصيانة المقدرة")
    labor_cost: float = Field(description="Estimated labor cost (SAR) | تكلفة العمالة المقدرة")
    total_cost: float = Field(description="Total estimated cost (SAR) | التكلفة الإجمالية المقدرة")
    cost_per_delivery: float = Field(description="Cost per delivery (SAR) | تكلفة التسليم الواحد")
    route_optimization_savings: float = Field(
        0.0, description="Savings from route optimization (SAR) | وفورات تحسين المسارات"
    )
    currency: str = "SAR"
    message: str = Field("", description="Summary message")
    message_ar: str = Field("", description="ملخص بالعربية")


class DailyReportResponse(BaseModel):
    """Daily logistics report | التقرير اليومي للوجستيات"""

    report_type: str = "daily"
    report_type_ar: str = "يومي"
    report_date: str = Field(description="Report date (YYYY-MM-DD) | تاريخ التقرير")
    tenant_id: str = Field(description="Tenant ID | معرف المستأجر")
    vehicles: VehicleSummary
    shipments: ShipmentSummary
    collections: CollectionSummary
    message: str = Field("", description="Report summary")
    message_ar: str = Field("", description="ملخص التقرير")
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


class WeeklyReportResponse(BaseModel):
    """Weekly logistics report | التقرير الأسبوعي للوجستيات"""

    report_type: str = "weekly"
    report_type_ar: str = "أسبوعي"
    week_start: str = Field(description="Week start date (YYYY-MM-DD) | بداية الأسبوع")
    week_end: str = Field(description="Week end date (YYYY-MM-DD) | نهاية الأسبوع")
    tenant_id: str = Field(description="Tenant ID | معرف المستأجر")
    vehicles: VehicleSummary
    shipments: ShipmentSummary
    collections: CollectionSummary
    route_optimization_savings_km: float = Field(
        0.0, description="Estimated distance saved (km) | المسافة الموفرة المقدرة (كم)"
    )
    daily_breakdown: list[dict] = Field(
        default_factory=list, description="Daily breakdown | التفصيل اليومي"
    )
    message: str = Field("", description="Report summary")
    message_ar: str = Field("", description="ملخص التقرير")
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


class MonthlyReportResponse(BaseModel):
    """Monthly logistics report | التقرير الشهري للوجستيات"""

    report_type: str = "monthly"
    report_type_ar: str = "شهري"
    month: str = Field(description="Report month (YYYY-MM) | شهر التقرير")
    month_start: str = Field(description="Month start date | بداية الشهر")
    month_end: str = Field(description="Month end date | نهاية الشهر")
    tenant_id: str = Field(description="Tenant ID | معرف المستأجر")
    vehicles: VehicleSummary
    shipments: ShipmentSummary
    collections: CollectionSummary
    costs: CostSummary
    weekly_breakdown: list[dict] = Field(
        default_factory=list, description="Weekly breakdown | التفصيل الأسبوعي"
    )
    performance_metrics: dict = Field(
        default_factory=dict, description="Performance metrics | مقاييس الأداء"
    )
    message: str = Field("", description="Report summary")
    message_ar: str = Field("", description="ملخص التقرير")
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────


def _get_tenant_id_dependency():
    """
    Lazy-import get_tenant_id from main to avoid circular imports.
    استيراد كسول لدالة معرف المستأجر لتجنب الاستيراد الدائري.
    """
    import main as main_mod

    return main_mod.get_tenant_id


def _get_stores():
    """
    Lazy-import in-memory data stores from main module.
    استيراد كسول لمخازن البيانات من الوحدة الرئيسية.
    """
    import main as main_mod

    return (
        main_mod.VEHICLES,
        main_mod.STORAGE_FACILITIES,
        main_mod.HARVEST_COLLECTIONS,
        main_mod.SHIPMENTS,
    )


def _get_enums():
    """
    Lazy-import enums and translations from main module.
    استيراد كسول للتعدادات والترجمات من الوحدة الرئيسية.
    """
    import main as main_mod

    return {
        "VehicleStatus": main_mod.VehicleStatus,
        "ShipmentStatus": main_mod.ShipmentStatus,
        "CollectionPriority": main_mod.CollectionPriority,
        "VEHICLE_STATUS_AR": main_mod.VEHICLE_STATUS_AR,
        "SHIPMENT_STATUS_AR": main_mod.SHIPMENT_STATUS_AR,
        "PRIORITY_AR": main_mod.PRIORITY_AR,
    }


def _to_aware_dt(val) -> datetime | None:
    """Convert a value to a timezone-aware datetime, or return None."""
    if val is None:
        return None
    if isinstance(val, str):
        try:
            val = datetime.fromisoformat(val)
        except (ValueError, TypeError):
            return None
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=UTC)
        return val
    return None


def _filter_records_by_date(
    records: list[dict],
    start: datetime,
    end: datetime,
    date_field: str = "created_at",
) -> list[dict]:
    """
    Filter records whose date_field falls within [start, end].
    تصفية السجلات التي يقع حقل التاريخ فيها ضمن النطاق.
    """
    result = []
    for r in records:
        dt = _to_aware_dt(r.get(date_field))
        if dt is not None and start <= dt <= end:
            result.append(r)
    return result


def _build_vehicle_summary(vehicles: list[dict]) -> VehicleSummary:
    """
    Build a VehicleSummary from a list of vehicle dicts.
    بناء ملخص المركبات من قائمة المركبات.
    """
    enums = _get_enums()
    VS = enums["VehicleStatus"]

    total = len(vehicles)
    available = len([v for v in vehicles if v["status"] == VS.AVAILABLE.value])
    in_transit = len([v for v in vehicles if v["status"] == VS.IN_TRANSIT.value])
    loading = len([v for v in vehicles if v["status"] == VS.LOADING.value])
    unloading = len([v for v in vehicles if v["status"] == VS.UNLOADING.value])
    maintenance = len([v for v in vehicles if v["status"] == VS.MAINTENANCE.value])
    out_of_service = len([v for v in vehicles if v["status"] == VS.OUT_OF_SERVICE.value])

    active = in_transit + loading + unloading
    idle = available
    utilization = (active / total * 100) if total > 0 else 0.0

    return VehicleSummary(
        total=total,
        active=active,
        idle=idle,
        maintenance=maintenance,
        out_of_service=out_of_service,
        utilization_rate=round(utilization, 1),
        message=f"{total} vehicles: {active} active, {idle} idle, {maintenance} maintenance",
        message_ar=f"{total} مركبة: {active} نشطة، {idle} خاملة، {maintenance} في الصيانة",
    )


def _build_shipment_summary(shipments: list[dict]) -> ShipmentSummary:
    """
    Build a ShipmentSummary from a list of shipment dicts.
    بناء ملخص الشحنات من قائمة الشحنات.
    """
    enums = _get_enums()
    SS = enums["ShipmentStatus"]

    total = len(shipments)
    scheduled = len([s for s in shipments if s["status"] == SS.SCHEDULED.value])
    collecting = len([s for s in shipments if s["status"] == SS.COLLECTING.value])
    in_transit_count = len([s for s in shipments if s["status"] == SS.IN_TRANSIT.value])
    delivering = len([s for s in shipments if s["status"] == SS.DELIVERING.value])
    delivered = len([s for s in shipments if s["status"] == SS.DELIVERED.value])
    cancelled = len([s for s in shipments if s["status"] == SS.CANCELLED.value])
    pending = scheduled + collecting

    # On-time rate: delivered shipments that arrived before or at estimated_arrival
    on_time = 0
    for s in shipments:
        if s["status"] == SS.DELIVERED.value:
            actual = _to_aware_dt(s.get("actual_arrival"))
            estimated = _to_aware_dt(s.get("estimated_arrival"))
            if actual and estimated and actual <= estimated:
                on_time += 1
            elif actual and not estimated:
                # No estimate means we cannot judge; count as on-time
                on_time += 1
    on_time_rate = (on_time / delivered * 100) if delivered > 0 else 0.0

    return ShipmentSummary(
        total=total,
        pending=pending,
        in_transit=in_transit_count + delivering,
        delivered=delivered,
        cancelled=cancelled,
        on_time_rate=round(on_time_rate, 1),
        message=f"{total} shipments: {pending} pending, {in_transit_count + delivering} in transit, {delivered} delivered",
        message_ar=f"{total} شحنة: {pending} معلقة، {in_transit_count + delivering} في الطريق، {delivered} تم التسليم",
    )


def _build_collection_summary(collections: list[dict]) -> CollectionSummary:
    """
    Build a CollectionSummary from a list of collection dicts.
    بناء ملخص الجمع من قائمة عمليات الجمع.
    """
    enums = _get_enums()
    CP = enums["CollectionPriority"]
    PRIORITY_AR = enums["PRIORITY_AR"]

    total_estimated = sum(c.get("estimated_quantity_kg", 0) for c in collections)
    total_actual = sum(c.get("actual_quantity_kg", 0) for c in collections if c.get("actual_quantity_kg"))

    # Distinct fields
    fields = {c.get("field_id") for c in collections if c.get("field_id")}

    # Group by crop type
    crop_groups: dict[str, dict[str, Any]] = {}
    for c in collections:
        crop = c.get("crop_type", "unknown")
        if crop not in crop_groups:
            crop_groups[crop] = {
                "crop_type": crop,
                "crop_type_ar": c.get("crop_type_ar", crop),
                "count": 0,
                "estimated_kg": 0.0,
                "actual_kg": 0.0,
            }
        crop_groups[crop]["count"] += 1
        crop_groups[crop]["estimated_kg"] += c.get("estimated_quantity_kg", 0)
        if c.get("actual_quantity_kg"):
            crop_groups[crop]["actual_kg"] += c["actual_quantity_kg"]

    # Group by priority
    by_priority: dict[str, int] = {}
    for pv in CP:
        count = len([c for c in collections if c.get("priority") == pv.value])
        if count > 0:
            label = f"{pv.value} ({PRIORITY_AR.get(pv, pv.value)})"
            by_priority[label] = count

    return CollectionSummary(
        total_collections=len(collections),
        total_weight_kg=round(total_estimated, 2),
        actual_weight_kg=round(total_actual, 2),
        fields_covered=len(fields),
        by_crop=list(crop_groups.values()),
        by_priority=by_priority,
        message=f"{len(collections)} collections, {round(total_estimated, 0)} kg estimated across {len(fields)} fields",
        message_ar=(
            f"{len(collections)} عملية جمع، {round(total_estimated, 0)} كجم مقدرة عبر {len(fields)} حقول"
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tenant ID dependency - wrapper to avoid circular import
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
) -> str:
    """
    Extract tenant ID from header, matching main.py pattern.
    استخراج معرف المستأجر من الترويسة.
    """
    # Lazy-delegate to main.get_tenant_id if accessible; otherwise use header directly
    if x_tenant_id:
        return x_tenant_id
    return "tenant_demo"


# ─────────────────────────────────────────────────────────────────────────────
# Report Endpoints - نقاط نهاية التقارير
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/reports/daily", response_model=DailyReportResponse)
async def get_daily_report(
    report_date: str | None = Query(
        None,
        description="Report date (YYYY-MM-DD), defaults to today | تاريخ التقرير، الافتراضي اليوم",
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate daily logistics report.
    إنشاء تقرير لوجستي يومي.

    Returns daily vehicle counts (active/idle), shipment counts by status
    (pending, in_transit, delivered), and daily collection summaries.
    يعرض أعداد المركبات اليومية (نشطة/خاملة)، أعداد الشحنات حسب الحالة
    (معلقة، في الطريق، تم التسليم)، وملخصات الجمع اليومية.
    """
    if report_date is None:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(report_date)

    logger.info(
        "Generating daily report",
        extra={"tenant_id": str(tenant_id)[:100], "date": str(target_date)},
    )

    VEHICLES, STORAGE_FACILITIES, HARVEST_COLLECTIONS, SHIPMENTS = _get_stores()

    day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=UTC)
    day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=UTC)

    # Filter by tenant
    tenant_vehicles = [v for v in VEHICLES.values() if v["tenant_id"] == tenant_id]
    tenant_shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]
    tenant_collections = [c for c in HARVEST_COLLECTIONS.values() if c["tenant_id"] == tenant_id]

    # Daily shipments: created or updated within the day
    daily_shipments = _filter_records_by_date(tenant_shipments, day_start, day_end, "created_at")
    if not daily_shipments:
        daily_shipments = _filter_records_by_date(tenant_shipments, day_start, day_end, "updated_at")
    # Fallback: show all current shipments if no date-filtered results
    if not daily_shipments:
        daily_shipments = tenant_shipments

    # Daily collections: scheduled for this day or updated this day
    daily_collections = _filter_records_by_date(tenant_collections, day_start, day_end, "scheduled_date")
    if not daily_collections:
        daily_collections = _filter_records_by_date(tenant_collections, day_start, day_end, "updated_at")
    if not daily_collections:
        daily_collections = tenant_collections

    # Build summaries
    vehicles = _build_vehicle_summary(tenant_vehicles)
    shipments = _build_shipment_summary(daily_shipments)
    collections = _build_collection_summary(daily_collections)

    date_str = str(target_date)

    return DailyReportResponse(
        report_date=date_str,
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        message=(
            f"Daily report for {date_str}: "
            f"{vehicles.total} vehicles ({vehicles.active} active, {vehicles.idle} idle), "
            f"{shipments.total} shipments ({shipments.delivered} delivered), "
            f"{collections.total_collections} collections"
        ),
        message_ar=(
            f"التقرير اليومي لـ {date_str}: "
            f"{vehicles.total} مركبة ({vehicles.active} نشطة، {vehicles.idle} خاملة)، "
            f"{shipments.total} شحنة ({shipments.delivered} تم التسليم)، "
            f"{collections.total_collections} عملية جمع"
        ),
        generated_at=datetime.now(UTC).isoformat(),
    )


@router.get("/reports/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_offset: int = Query(
        0,
        ge=-52,
        le=0,
        description=(
            "Week offset from current week (0=current, -1=last week). "
            "إزاحة الأسبوع من الأسبوع الحالي (0=الحالي، -1=الأسبوع الماضي)."
        ),
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate weekly logistics report.
    إنشاء تقرير لوجستي أسبوعي.

    Returns weekly vehicle utilization rates, shipment volume and status
    breakdown, route optimization savings estimate, and per-day breakdown.
    يعرض نسب استخدام المركبات الأسبوعية، حجم الشحنات وتفصيل الحالة،
    وفورات تحسين المسارات المقدرة، والتفصيل اليومي.
    """
    today = date.today()
    week_start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_end_date = week_start_date + timedelta(days=6)
    week_start = datetime(
        week_start_date.year, week_start_date.month, week_start_date.day, 0, 0, 0, tzinfo=UTC
    )
    week_end = datetime(
        week_end_date.year, week_end_date.month, week_end_date.day, 23, 59, 59, tzinfo=UTC
    )

    logger.info(
        "Generating weekly report",
        extra={
            "tenant_id": str(tenant_id)[:100],
            "week_start": str(week_start_date),
            "week_end": str(week_end_date),
        },
    )

    VEHICLES, STORAGE_FACILITIES, HARVEST_COLLECTIONS, SHIPMENTS = _get_stores()
    enums = _get_enums()
    SS = enums["ShipmentStatus"]

    # Filter by tenant
    tenant_vehicles = [v for v in VEHICLES.values() if v["tenant_id"] == tenant_id]
    tenant_shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]
    tenant_collections = [c for c in HARVEST_COLLECTIONS.values() if c["tenant_id"] == tenant_id]

    # Weekly shipments
    weekly_shipments = _filter_records_by_date(tenant_shipments, week_start, week_end, "created_at")
    if not weekly_shipments:
        weekly_shipments = _filter_records_by_date(tenant_shipments, week_start, week_end, "updated_at")
    if not weekly_shipments:
        weekly_shipments = tenant_shipments

    # Weekly collections
    weekly_collections = _filter_records_by_date(tenant_collections, week_start, week_end, "scheduled_date")
    if not weekly_collections:
        weekly_collections = _filter_records_by_date(tenant_collections, week_start, week_end, "updated_at")
    if not weekly_collections:
        weekly_collections = tenant_collections

    # Build summaries
    vehicles = _build_vehicle_summary(tenant_vehicles)
    shipments = _build_shipment_summary(weekly_shipments)
    collections = _build_collection_summary(weekly_collections)

    # Route optimization savings estimate
    # Approximate: 10% distance saving per completed trip, 45 km avg trip
    completed_trips = len([s for s in weekly_shipments if s["status"] == SS.DELIVERED.value])
    avg_distance_per_trip_km = 45.0
    distance_saved = completed_trips * avg_distance_per_trip_km * 0.10

    # Build daily breakdown
    daily_breakdown = []
    for i in range(7):
        day = week_start_date + timedelta(days=i)
        day_dt_start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=UTC)
        day_dt_end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=UTC)

        day_shipments = _filter_records_by_date(weekly_shipments, day_dt_start, day_dt_end, "created_at")
        day_deliveries = len([s for s in day_shipments if s["status"] == SS.DELIVERED.value])
        day_collections = _filter_records_by_date(weekly_collections, day_dt_start, day_dt_end, "scheduled_date")

        daily_breakdown.append({
            "date": str(day),
            "date_label": day.strftime("%A"),
            "shipments": len(day_shipments),
            "deliveries": day_deliveries,
            "collections": len(day_collections),
            "weight_kg": round(sum(s.get("weight_kg", 0) for s in day_shipments), 2),
        })

    return WeeklyReportResponse(
        week_start=str(week_start_date),
        week_end=str(week_end_date),
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        route_optimization_savings_km=round(distance_saved, 2),
        daily_breakdown=daily_breakdown,
        message=(
            f"Weekly report ({week_start_date} to {week_end_date}): "
            f"{vehicles.utilization_rate:.0f}% fleet utilization, "
            f"{shipments.total} shipments, "
            f"~{round(distance_saved, 1)} km saved"
        ),
        message_ar=(
            f"التقرير الأسبوعي ({week_start_date} إلى {week_end_date}): "
            f"{vehicles.utilization_rate:.0f}% استخدام الأسطول، "
            f"{shipments.total} شحنة، "
            f"~{round(distance_saved, 1)} كم موفرة"
        ),
        generated_at=datetime.now(UTC).isoformat(),
    )


@router.get("/reports/monthly", response_model=MonthlyReportResponse)
async def get_monthly_report(
    month: str | None = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Report month (YYYY-MM), defaults to current | شهر التقرير، الافتراضي الشهر الحالي",
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate monthly logistics report.
    إنشاء تقرير لوجستي شهري.

    Returns monthly fleet performance metrics, cost summary,
    shipment and collection breakdown, weekly breakdown, and performance metrics.
    يعرض مقاييس أداء الأسطول الشهري، ملخص التكاليف،
    تفصيل الشحنات والجمع، التفصيل الأسبوعي، ومقاييس الأداء.
    """
    if month is None:
        target_month_str = date.today().strftime("%Y-%m")
    else:
        target_month_str = month

    parts = target_month_str.split("-")
    target_year = int(parts[0])
    target_month = int(parts[1])

    logger.info(
        "Generating monthly report",
        extra={"tenant_id": str(tenant_id)[:100], "month": str(target_month_str)[:7]},
    )

    _, last_day = calendar.monthrange(target_year, target_month)
    month_start_date = date(target_year, target_month, 1)
    month_end_date = date(target_year, target_month, last_day)
    month_start = datetime(target_year, target_month, 1, 0, 0, 0, tzinfo=UTC)
    month_end = datetime(target_year, target_month, last_day, 23, 59, 59, tzinfo=UTC)

    VEHICLES, STORAGE_FACILITIES, HARVEST_COLLECTIONS, SHIPMENTS = _get_stores()
    enums = _get_enums()
    SS = enums["ShipmentStatus"]

    # Filter by tenant
    tenant_vehicles = [v for v in VEHICLES.values() if v["tenant_id"] == tenant_id]
    tenant_shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]
    tenant_collections = [c for c in HARVEST_COLLECTIONS.values() if c["tenant_id"] == tenant_id]

    # Monthly shipments
    monthly_shipments = _filter_records_by_date(tenant_shipments, month_start, month_end, "created_at")
    if not monthly_shipments:
        monthly_shipments = _filter_records_by_date(tenant_shipments, month_start, month_end, "updated_at")
    if not monthly_shipments:
        monthly_shipments = tenant_shipments

    # Monthly collections
    monthly_collections = _filter_records_by_date(tenant_collections, month_start, month_end, "scheduled_date")
    if not monthly_collections:
        monthly_collections = _filter_records_by_date(tenant_collections, month_start, month_end, "updated_at")
    if not monthly_collections:
        monthly_collections = tenant_collections

    # Build summaries
    vehicles = _build_vehicle_summary(tenant_vehicles)
    shipments = _build_shipment_summary(monthly_shipments)
    collections = _build_collection_summary(monthly_collections)

    # ── Cost estimation ──
    completed_trips = len([s for s in monthly_shipments if s["status"] == SS.DELIVERED.value])
    total_weight = sum(s.get("weight_kg", 0) for s in monthly_shipments)

    # Fuel: avg 45 km/trip, 0.12 L/km, 2.5 SAR/L
    avg_km_per_trip = 45.0
    total_distance_km = completed_trips * avg_km_per_trip
    fuel_cost = total_distance_km * 0.12 * 2.5

    # Maintenance: vehicles in maintenance or overdue => 500 SAR each
    now = datetime.now(UTC)
    vehicles_needing_maint = 0
    for v in tenant_vehicles:
        if v["status"] == "maintenance":
            vehicles_needing_maint += 1
        elif v.get("next_maintenance_at"):
            maint_dt = _to_aware_dt(v["next_maintenance_at"])
            if maint_dt and maint_dt < now:
                vehicles_needing_maint += 1
    maintenance_cost = vehicles_needing_maint * 500.0

    # Labor: 200 SAR per completed trip (driver cost estimate)
    labor_cost = completed_trips * 200.0

    # Route optimization savings: 10% of fuel cost
    route_savings = fuel_cost * 0.10
    total_cost = fuel_cost + maintenance_cost + labor_cost - route_savings
    cost_per_delivery = (total_cost / completed_trips) if completed_trips > 0 else 0.0

    costs = CostSummary(
        fuel_cost=round(fuel_cost, 2),
        maintenance_cost=round(maintenance_cost, 2),
        labor_cost=round(labor_cost, 2),
        total_cost=round(total_cost, 2),
        cost_per_delivery=round(cost_per_delivery, 2),
        route_optimization_savings=round(route_savings, 2),
        message=(
            f"Estimated costs: {round(fuel_cost, 0)} SAR fuel, "
            f"{round(maintenance_cost, 0)} SAR maintenance, "
            f"{round(labor_cost, 0)} SAR labor, "
            f"{round(route_savings, 0)} SAR saved"
        ),
        message_ar=(
            f"التكاليف المقدرة: {round(fuel_cost, 0)} ريال وقود، "
            f"{round(maintenance_cost, 0)} ريال صيانة، "
            f"{round(labor_cost, 0)} ريال عمالة، "
            f"{round(route_savings, 0)} ريال موفرة"
        ),
    )

    # ── Weekly breakdown within the month ──
    weekly_breakdown = []
    current_week_start = month_start_date
    week_num = 1
    while current_week_start <= month_end_date:
        current_week_end = min(current_week_start + timedelta(days=6), month_end_date)
        w_start_dt = datetime(
            current_week_start.year, current_week_start.month, current_week_start.day, 0, 0, 0, tzinfo=UTC
        )
        w_end_dt = datetime(
            current_week_end.year, current_week_end.month, current_week_end.day, 23, 59, 59, tzinfo=UTC
        )

        w_shipments = _filter_records_by_date(monthly_shipments, w_start_dt, w_end_dt, "created_at")
        w_collections = _filter_records_by_date(monthly_collections, w_start_dt, w_end_dt, "scheduled_date")
        w_delivered = len([s for s in w_shipments if s["status"] == SS.DELIVERED.value])
        w_weight = sum(s.get("weight_kg", 0) for s in w_shipments)

        weekly_breakdown.append({
            "week": week_num,
            "start": str(current_week_start),
            "end": str(current_week_end),
            "shipments": len(w_shipments),
            "deliveries": w_delivered,
            "collections": len(w_collections),
            "weight_kg": round(w_weight, 2),
        })

        current_week_start = current_week_end + timedelta(days=1)
        week_num += 1

    # ── Performance metrics ──
    avg_fuel_levels = [
        v.get("fuel_level_percent", 0)
        for v in tenant_vehicles
        if v.get("fuel_level_percent") is not None
    ]
    avg_fuel = sum(avg_fuel_levels) / len(avg_fuel_levels) if avg_fuel_levels else 0.0

    # Fleet downtime: (maintenance + out_of_service) / total
    fleet_downtime = (
        (vehicles.maintenance + vehicles.out_of_service) / vehicles.total * 100
        if vehicles.total > 0
        else 0.0
    )

    performance_metrics = {
        "total_trips": completed_trips,
        "total_distance_km": round(total_distance_km, 2),
        "total_weight_kg": round(total_weight, 2),
        "avg_fuel_level_percent": round(avg_fuel, 1),
        "fleet_downtime_percent": round(fleet_downtime, 1),
        "vehicles_needing_maintenance": vehicles_needing_maint,
        "route_optimization_savings_km": round(total_distance_km * 0.10, 2),
        "cost_per_km": round((total_cost / total_distance_km) if total_distance_km > 0 else 0.0, 2),
    }

    return MonthlyReportResponse(
        month=target_month_str,
        month_start=str(month_start_date),
        month_end=str(month_end_date),
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        costs=costs,
        weekly_breakdown=weekly_breakdown,
        performance_metrics=performance_metrics,
        message=(
            f"Monthly report for {target_month_str}: "
            f"{vehicles.total} vehicles at {vehicles.utilization_rate:.0f}% utilization, "
            f"{shipments.total} shipments ({round(total_weight, 0)} kg), "
            f"estimated cost {round(total_cost, 0)} SAR"
        ),
        message_ar=(
            f"التقرير الشهري لـ {target_month_str}: "
            f"{vehicles.total} مركبة بنسبة {vehicles.utilization_rate:.0f}% استخدام، "
            f"{shipments.total} شحنة ({round(total_weight, 0)} كجم)، "
            f"التكلفة المقدرة {round(total_cost, 0)} ريال"
        ),
        generated_at=datetime.now(UTC).isoformat(),
    )
