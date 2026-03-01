"""
Dashboard Data Aggregation Module | وحدة تجميع بيانات لوحة المعلومات
Provides unified farm overview data from multiple services.
"""

from __future__ import annotations

import os
import logging
from datetime import UTC, datetime
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NDVIOverview:
    """NDVI overview data | بيانات نظرة عامة NDVI"""

    average_ndvi: float = 0.0
    health_status: str = "unknown"
    health_status_ar: str = "غير معروف"
    fields_analyzed: int = 0
    last_update: str = ""


@dataclass
class IrrigationOverview:
    """Irrigation overview | نظرة عامة على الري"""

    next_irrigation_days: int = -1
    water_usage_m3: float = 0.0
    efficiency_percent: float = 0.0
    schedule_status: str = "unknown"
    schedule_status_ar: str = "غير معروف"


@dataclass
class WeatherOverview:
    """Weather overview | نظرة عامة على الطقس"""

    temperature_c: float = 0.0
    humidity_percent: float = 0.0
    wind_speed_kmh: float = 0.0
    forecast_summary: str = ""
    forecast_summary_ar: str = ""
    rain_probability: float = 0.0


@dataclass
class PestOverview:
    """Pest alerts overview | نظرة عامة على تنبيهات الآفات"""

    active_alerts: int = 0
    critical_alerts: int = 0
    recent_detections: list = field(default_factory=list)
    risk_level: str = "low"
    risk_level_ar: str = "منخفض"


@dataclass
class YieldOverview:
    """Yield prediction overview | نظرة عامة على تنبؤ الإنتاجية"""

    predicted_yield_ton_ha: float = 0.0
    yield_change_percent: float = 0.0
    confidence: float = 0.0
    crop_type: str = ""
    crop_type_ar: str = ""


@dataclass
class CostOverview:
    """Cost overview | نظرة عامة على التكاليف"""

    total_revenue_sar: float = 0.0
    total_costs_sar: float = 0.0
    profit_sar: float = 0.0
    roi_percent: float = 0.0


@dataclass
class TaskOverview:
    """Upcoming tasks overview | نظرة عامة على المهام القادمة"""

    pending_tasks: int = 0
    overdue_tasks: int = 0
    upcoming: list = field(default_factory=list)


@dataclass
class FarmDashboard:
    """Complete farm dashboard data | بيانات لوحة بيانات المزرعة الكاملة"""

    tenant_id: str = ""
    farm_name: str = ""
    farm_name_ar: str = ""
    total_fields: int = 0
    total_area_hectares: float = 0.0
    ndvi: NDVIOverview = field(default_factory=NDVIOverview)
    irrigation: IrrigationOverview = field(default_factory=IrrigationOverview)
    weather: WeatherOverview = field(default_factory=WeatherOverview)
    pests: PestOverview = field(default_factory=PestOverview)
    yield_prediction: YieldOverview = field(default_factory=YieldOverview)
    costs: CostOverview = field(default_factory=CostOverview)
    tasks: TaskOverview = field(default_factory=TaskOverview)
    generated_at: str = ""
    message: str = "Farm dashboard data loaded successfully"
    message_ar: str = "تم تحميل بيانات لوحة المعلومات بنجاح"


class DashboardAggregator:
    """Aggregates data from multiple services for the unified dashboard.

    مجمّع البيانات من عدة خدمات للوحة المعلومات الموحدة.
    """

    # Health status mapping based on NDVI ranges
    NDVI_HEALTH = {
        (0.6, 1.0): ("healthy", "صحي"),
        (0.4, 0.6): ("moderate", "معتدل"),
        (0.2, 0.4): ("stressed", "مجهد"),
        (0.0, 0.2): ("critical", "حرج"),
    }

    # Pest risk levels
    PEST_RISK = {
        (0, 0): ("none", "لا يوجد"),
        (1, 2): ("low", "منخفض"),
        (3, 5): ("moderate", "متوسط"),
        (6, 10): ("high", "مرتفع"),
        (11, 999): ("critical", "حرج"),
    }

    def __init__(self, tenant_id: str = ""):
        self.tenant_id = tenant_id

    def get_ndvi_health(self, ndvi_value: float) -> tuple[str, str]:
        """Get health status from NDVI value."""
        for (low, high), (status_en, status_ar) in self.NDVI_HEALTH.items():
            if low <= ndvi_value < high:
                return status_en, status_ar
        return "unknown", "غير معروف"

    def get_pest_risk(self, alert_count: int) -> tuple[str, str]:
        """Get pest risk level from alert count."""
        for (low, high), (risk_en, risk_ar) in self.PEST_RISK.items():
            if low <= alert_count <= high:
                return risk_en, risk_ar
        return "unknown", "غير معروف"

    def calculate_roi(self, revenue: float, costs: float) -> float:
        """Calculate ROI percentage."""
        if costs <= 0:
            return 0.0
        return round(((revenue - costs) / costs) * 100, 1)

    async def build_dashboard(
        self,
        farm_name: str = "المزرعة",
        farm_name_ar: str = "المزرعة",
        ndvi_data: dict | None = None,
        irrigation_data: dict | None = None,
        weather_data: dict | None = None,
        pest_data: dict | None = None,
        yield_data: dict | None = None,
        cost_data: dict | None = None,
        task_data: dict | None = None,
    ) -> FarmDashboard:
        """Build unified dashboard from service data.

        بناء لوحة معلومات موحدة من بيانات الخدمات.
        """
        dashboard = FarmDashboard(
            tenant_id=self.tenant_id,
            farm_name=farm_name,
            farm_name_ar=farm_name_ar,
            generated_at=datetime.now(UTC).isoformat(),
        )

        # NDVI data
        if ndvi_data:
            avg = ndvi_data.get("average", 0.0)
            status_en, status_ar = self.get_ndvi_health(avg)
            dashboard.ndvi = NDVIOverview(
                average_ndvi=avg,
                health_status=status_en,
                health_status_ar=status_ar,
                fields_analyzed=ndvi_data.get("fields_count", 0),
                last_update=ndvi_data.get("last_update", ""),
            )

        # Irrigation data
        if irrigation_data:
            dashboard.irrigation = IrrigationOverview(
                next_irrigation_days=irrigation_data.get("next_days", -1),
                water_usage_m3=irrigation_data.get("usage_m3", 0.0),
                efficiency_percent=irrigation_data.get("efficiency", 0.0),
                schedule_status=irrigation_data.get("status", "unknown"),
                schedule_status_ar=irrigation_data.get("status_ar", "غير معروف"),
            )

        # Weather data
        if weather_data:
            dashboard.weather = WeatherOverview(
                temperature_c=weather_data.get("temp", 0.0),
                humidity_percent=weather_data.get("humidity", 0.0),
                wind_speed_kmh=weather_data.get("wind", 0.0),
                forecast_summary=weather_data.get("summary", ""),
                forecast_summary_ar=weather_data.get("summary_ar", ""),
                rain_probability=weather_data.get("rain_prob", 0.0),
            )

        # Pest data
        if pest_data:
            alert_count = pest_data.get("active_alerts", 0)
            risk_en, risk_ar = self.get_pest_risk(alert_count)
            dashboard.pests = PestOverview(
                active_alerts=alert_count,
                critical_alerts=pest_data.get("critical", 0),
                recent_detections=pest_data.get("recent", []),
                risk_level=risk_en,
                risk_level_ar=risk_ar,
            )

        # Yield data
        if yield_data:
            dashboard.yield_prediction = YieldOverview(
                predicted_yield_ton_ha=yield_data.get("yield", 0.0),
                yield_change_percent=yield_data.get("change", 0.0),
                confidence=yield_data.get("confidence", 0.0),
                crop_type=yield_data.get("crop", ""),
                crop_type_ar=yield_data.get("crop_ar", ""),
            )

        # Cost data
        if cost_data:
            revenue = cost_data.get("revenue", 0.0)
            costs = cost_data.get("costs", 0.0)
            dashboard.costs = CostOverview(
                total_revenue_sar=revenue,
                total_costs_sar=costs,
                profit_sar=revenue - costs,
                roi_percent=self.calculate_roi(revenue, costs),
            )

        # Task data
        if task_data:
            dashboard.tasks = TaskOverview(
                pending_tasks=task_data.get("pending", 0),
                overdue_tasks=task_data.get("overdue", 0),
                upcoming=task_data.get("upcoming", []),
            )

        return dashboard
