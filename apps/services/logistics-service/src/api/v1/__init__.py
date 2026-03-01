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

import logging
import os
import sys
from datetime import UTC, date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel, Field

# Shared auth imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

try:
    from shared.auth.dependencies import get_current_user

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

    async def get_current_user():
        """Placeholder when auth not available"""
        return None


logger = logging.getLogger(__name__)

# Create a router for report endpoints
router = APIRouter(prefix="/api/v1", tags=["logistics-reports"])


# ─────────────────────────────────────────────────────────────────────────────
# Response Models - نماذج الاستجابة
# ─────────────────────────────────────────────────────────────────────────────


class VehicleSummary(BaseModel):
    """Vehicle fleet summary | ملخص أسطول المركبات"""

    total: int = Field(description="Total vehicles | إجمالي المركبات")
    active: int = Field(description="Active vehicles | المركبات النشطة")
    idle: int = Field(description="Idle vehicles | المركبات الخاملة")
    maintenance: int = Field(description="In maintenance | في الصيانة")
    utilization_rate: float = Field(description="Utilization rate % | نسبة الاستخدام")


class ShipmentSummary(BaseModel):
    """Shipment status summary | ملخص حالة الشحنات"""

    total: int = Field(description="Total shipments | إجمالي الشحنات")
    pending: int = Field(description="Pending shipments | شحنات معلقة")
    in_transit: int = Field(description="In transit | في الطريق")
    delivered: int = Field(description="Delivered | تم التسليم")
    cancelled: int = Field(description="Cancelled | ملغاة")
    on_time_rate: float = Field(description="On-time delivery rate % | نسبة التسليم في الوقت")


class CollectionSummary(BaseModel):
    """Harvest collection summary | ملخص جمع المحاصيل"""

    total_collections: int = Field(description="Total collections | إجمالي عمليات الجمع")
    total_weight_kg: float = Field(description="Total weight (kg) | الوزن الإجمالي (كجم)")
    fields_covered: int = Field(description="Fields covered | الحقول المغطاة")


class CostSummary(BaseModel):
    """Cost summary | ملخص التكاليف"""

    fuel_cost: float = Field(description="Fuel cost | تكلفة الوقود")
    maintenance_cost: float = Field(description="Maintenance cost | تكلفة الصيانة")
    labor_cost: float = Field(description="Labor cost | تكلفة العمالة")
    total_cost: float = Field(description="Total cost | التكلفة الإجمالية")
    cost_per_delivery: float = Field(description="Cost per delivery | تكلفة التسليم الواحد")


class DailyReportResponse(BaseModel):
    """Daily logistics report | التقرير اليومي للوجستيات"""

    report_type: str = "daily"
    report_date: str = Field(description="Report date | تاريخ التقرير")
    tenant_id: str = Field(description="Tenant ID | معرف المستأجر")
    vehicles: VehicleSummary
    shipments: ShipmentSummary
    collections: CollectionSummary
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


class WeeklyReportResponse(BaseModel):
    """Weekly logistics report | التقرير الأسبوعي للوجستيات"""

    report_type: str = "weekly"
    week_start: str = Field(description="Week start date | بداية الأسبوع")
    week_end: str = Field(description="Week end date | نهاية الأسبوع")
    tenant_id: str = Field(description="Tenant ID | معرف المستأجر")
    vehicles: VehicleSummary
    shipments: ShipmentSummary
    collections: CollectionSummary
    daily_breakdown: list[dict] = Field(
        default_factory=list, description="Daily breakdown | التفصيل اليومي"
    )
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


class MonthlyReportResponse(BaseModel):
    """Monthly logistics report | التقرير الشهري للوجستيات"""

    report_type: str = "monthly"
    month: str = Field(description="Report month (YYYY-MM) | شهر التقرير")
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
    generated_at: str = Field(description="Generation timestamp | وقت الإنشاء")


# ─────────────────────────────────────────────────────────────────────────────
# Helper - Extract tenant_id from header
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
) -> str:
    """Extract tenant ID from header | استخراج معرف المستأجر من الترويسة"""
    return x_tenant_id or "default"


# ─────────────────────────────────────────────────────────────────────────────
# Report Endpoints - نقاط نهاية التقارير
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/reports/daily", response_model=DailyReportResponse)
async def get_daily_report(
    report_date: Optional[str] = Query(
        None,
        description="Report date (YYYY-MM-DD), defaults to today | تاريخ التقرير",
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate daily logistics report.
    إنشاء تقرير لوجستي يومي.

    Returns vehicle fleet status, shipment counts by status,
    and harvest collection summaries for the specified date.
    """
    if report_date is None:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(report_date)

    logger.info(
        "Generating daily report",
        extra={"tenant_id": tenant_id, "date": str(target_date)},
    )

    # Aggregate data from in-memory stores (or database when available)
    # In production, these would query the actual database
    vehicles = VehicleSummary(
        total=0,
        active=0,
        idle=0,
        maintenance=0,
        utilization_rate=0.0,
    )
    shipments = ShipmentSummary(
        total=0,
        pending=0,
        in_transit=0,
        delivered=0,
        cancelled=0,
        on_time_rate=0.0,
    )
    collections = CollectionSummary(
        total_collections=0,
        total_weight_kg=0.0,
        fields_covered=0,
    )

    return DailyReportResponse(
        report_date=str(target_date),
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        generated_at=datetime.now(UTC).isoformat(),
    )


@router.get("/reports/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    week_offset: int = Query(
        0,
        description="Week offset from current (0=this week, -1=last week) | إزاحة الأسبوع",
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate weekly logistics report.
    إنشاء تقرير لوجستي أسبوعي.

    Returns weekly vehicle utilization, shipment volumes,
    route optimization savings, and daily breakdown.
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)

    logger.info(
        "Generating weekly report",
        extra={
            "tenant_id": tenant_id,
            "week_start": str(week_start),
            "week_end": str(week_end),
        },
    )

    vehicles = VehicleSummary(
        total=0,
        active=0,
        idle=0,
        maintenance=0,
        utilization_rate=0.0,
    )
    shipments = ShipmentSummary(
        total=0,
        pending=0,
        in_transit=0,
        delivered=0,
        cancelled=0,
        on_time_rate=0.0,
    )
    collections = CollectionSummary(
        total_collections=0,
        total_weight_kg=0.0,
        fields_covered=0,
    )

    # Build daily breakdown for the week
    daily_breakdown = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        daily_breakdown.append(
            {
                "date": str(day),
                "shipments": 0,
                "deliveries": 0,
                "collections": 0,
            }
        )

    return WeeklyReportResponse(
        week_start=str(week_start),
        week_end=str(week_end),
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        daily_breakdown=daily_breakdown,
        generated_at=datetime.now(UTC).isoformat(),
    )


@router.get("/reports/monthly", response_model=MonthlyReportResponse)
async def get_monthly_report(
    month: Optional[str] = Query(
        None,
        description="Report month (YYYY-MM), defaults to current | شهر التقرير",
    ),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Generate monthly logistics report.
    إنشاء تقرير لوجستي شهري.

    Returns monthly fleet performance, cost summary,
    weekly breakdown, and performance metrics.
    """
    if month is None:
        target_month = date.today().strftime("%Y-%m")
    else:
        target_month = month

    logger.info(
        "Generating monthly report",
        extra={"tenant_id": tenant_id, "month": target_month},
    )

    vehicles = VehicleSummary(
        total=0,
        active=0,
        idle=0,
        maintenance=0,
        utilization_rate=0.0,
    )
    shipments = ShipmentSummary(
        total=0,
        pending=0,
        in_transit=0,
        delivered=0,
        cancelled=0,
        on_time_rate=0.0,
    )
    collections = CollectionSummary(
        total_collections=0,
        total_weight_kg=0.0,
        fields_covered=0,
    )
    costs = CostSummary(
        fuel_cost=0.0,
        maintenance_cost=0.0,
        labor_cost=0.0,
        total_cost=0.0,
        cost_per_delivery=0.0,
    )
    performance_metrics = {
        "avg_delivery_time_hours": 0.0,
        "route_optimization_savings_pct": 0.0,
        "fleet_downtime_pct": 0.0,
        "customer_satisfaction_score": 0.0,
    }

    return MonthlyReportResponse(
        month=target_month,
        tenant_id=tenant_id,
        vehicles=vehicles,
        shipments=shipments,
        collections=collections,
        costs=costs,
        weekly_breakdown=[],
        performance_metrics=performance_metrics,
        generated_at=datetime.now(UTC).isoformat(),
    )
