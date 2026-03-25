"""
Smart Financial Reports Module | وحدة التقارير المالية الذكية

Provides per-field cost analysis, profitability, season comparison,
and ROI estimation for agricultural recommendations.

Competitive reference: Agworld, FarmLogs
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class CostCategory(StrEnum):
    """Cost categories | فئات التكاليف"""

    SEED = "seed"  # بذور
    FERTILIZER = "fertilizer"  # أسمدة
    PESTICIDE = "pesticide"  # مبيدات
    IRRIGATION = "irrigation"  # ري
    LABOR = "labor"  # عمالة
    EQUIPMENT = "equipment"  # معدات
    FUEL = "fuel"  # وقود
    TRANSPORT = "transport"  # نقل
    STORAGE = "storage"  # تخزين
    CERTIFICATION = "certification"  # شهادات
    INSURANCE = "insurance"  # تأمين
    OTHER = "other"  # أخرى


class Season(StrEnum):
    """Agricultural seasons | المواسم الزراعية"""

    WINTER = "winter"  # شتاء
    SUMMER = "summer"  # صيف
    SPRING = "spring"  # ربيع
    FALL = "fall"  # خريف


COST_CATEGORY_AR = {
    CostCategory.SEED: "بذور",
    CostCategory.FERTILIZER: "أسمدة",
    CostCategory.PESTICIDE: "مبيدات",
    CostCategory.IRRIGATION: "ري",
    CostCategory.LABOR: "عمالة",
    CostCategory.EQUIPMENT: "معدات",
    CostCategory.FUEL: "وقود",
    CostCategory.TRANSPORT: "نقل",
    CostCategory.STORAGE: "تخزين",
    CostCategory.CERTIFICATION: "شهادات",
    CostCategory.INSURANCE: "تأمين",
    CostCategory.OTHER: "أخرى",
}


@dataclass
class CostEntry:
    """A single cost entry | إدخال تكلفة واحد"""

    entry_id: str = ""
    category: CostCategory = CostCategory.OTHER
    category_ar: str = ""
    description: str = ""
    description_ar: str = ""
    amount_sar: float = 0.0
    amount_per_hectare: float = 0.0
    date: str = ""
    field_id: str = ""
    quantity: float = 0.0
    unit: str = ""


@dataclass
class RevenueEntry:
    """A revenue entry | إدخال إيراد"""

    entry_id: str = ""
    crop_type: str = ""
    crop_type_ar: str = ""
    yield_ton: float = 0.0
    price_per_ton_sar: float = 0.0
    total_revenue_sar: float = 0.0
    quality_grade: str = ""
    buyer: str = ""
    date: str = ""
    field_id: str = ""


@dataclass
class FieldFinancialReport:
    """Financial report for a single field | تقرير مالي لحقل واحد"""

    report_id: str = ""
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""
    tenant_id: str = ""
    season: Season = Season.WINTER
    crop_type: str = ""
    crop_type_ar: str = ""
    area_hectares: float = 0.0

    # Costs
    costs: list[CostEntry] = field(default_factory=list)
    total_costs_sar: float = 0.0
    cost_per_hectare_sar: float = 0.0
    cost_breakdown: dict[str, float] = field(default_factory=dict)

    # Revenue
    revenues: list[RevenueEntry] = field(default_factory=list)
    total_revenue_sar: float = 0.0
    revenue_per_hectare_sar: float = 0.0

    # Profitability
    profit_sar: float = 0.0
    profit_per_hectare_sar: float = 0.0
    roi_percent: float = 0.0
    break_even_yield_ton: float = 0.0

    # Metadata
    generated_at: str = ""
    message: str = ""
    message_ar: str = ""


@dataclass
class SeasonComparison:
    """Season-over-season comparison | مقارنة بين المواسم"""

    field_id: str = ""
    current_season: str = ""
    previous_season: str = ""
    cost_change_percent: float = 0.0
    revenue_change_percent: float = 0.0
    profit_change_percent: float = 0.0
    yield_change_percent: float = 0.0
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


@dataclass
class RecommendationROI:
    """ROI estimation for a recommendation | تقدير العائد على الاستثمار لتوصية"""

    recommendation_id: str = ""
    recommendation_type: str = ""
    recommendation_type_ar: str = ""
    investment_sar: float = 0.0
    expected_return_sar: float = 0.0
    expected_roi_percent: float = 0.0
    payback_period_days: int = 0
    confidence_percent: float = 0.0
    risk_level: str = "medium"
    risk_level_ar: str = "متوسط"


class FinancialReportGenerator:
    """Generates financial reports for fields and farms.

    يولّد التقارير المالية للحقول والمزارع.
    """

    # Average crop prices in SAR/ton
    CROP_PRICES = {
        "wheat": 1850,
        "barley": 1500,
        "date_palm": 8000,
        "tomato": 2500,
        "cucumber": 3000,
        "alfalfa": 1200,
        "corn": 1600,
        "rice": 2800,
    }

    # Average production costs (SAR/ha)
    AVG_COSTS_PER_HA = {
        "wheat": 4200,
        "barley": 3500,
        "date_palm": 12000,
        "tomato": 25000,
        "cucumber": 20000,
        "alfalfa": 3000,
        "corn": 5500,
        "rice": 8000,
    }

    def calculate_cost_breakdown(self, costs: list[CostEntry]) -> dict[str, float]:
        """Calculate cost breakdown by category."""
        breakdown: dict[str, float] = {}
        for cost in costs:
            cat_name = COST_CATEGORY_AR.get(cost.category, cost.category.value)
            breakdown[cat_name] = breakdown.get(cat_name, 0.0) + cost.amount_sar
        return breakdown

    def calculate_break_even(
        self,
        total_costs: float,
        price_per_ton: float,
        area_hectares: float,
    ) -> float:
        """Calculate break-even yield in tons/ha."""
        if price_per_ton <= 0 or area_hectares <= 0:
            return 0.0
        return round(total_costs / (price_per_ton * area_hectares), 2)

    def estimate_recommendation_roi(
        self,
        recommendation_type: str,
        investment_sar: float,
        crop_type: str = "wheat",
        area_hectares: float = 1.0,
        expected_yield_increase_percent: float = 10.0,
        current_yield_ton_ha: float = 4.0,
    ) -> RecommendationROI:
        """Estimate ROI for an agricultural recommendation.

        تقدير العائد على الاستثمار لتوصية زراعية.
        """
        price = self.CROP_PRICES.get(crop_type, 1500)
        additional_yield = current_yield_ton_ha * (expected_yield_increase_percent / 100) * area_hectares
        expected_return = additional_yield * price

        roi = ((expected_return - investment_sar) / investment_sar * 100) if investment_sar > 0 else 0
        payback_days = int(investment_sar / expected_return * 180) if expected_return > 0 else 999

        risk_levels = {
            (500, 9999): ("low", "منخفض"),
            (200, 500): ("medium", "متوسط"),
            (0, 200): ("high", "مرتفع"),
        }
        risk_en, risk_ar = "medium", "متوسط"
        for (low, high), (r_en, r_ar) in risk_levels.items():
            if low <= roi <= high:
                risk_en, risk_ar = r_en, r_ar
                break

        type_ar_map = {
            "fertilizer": "تسميد",
            "irrigation": "ري",
            "pesticide": "مبيد",
            "seed": "بذور",
            "equipment": "معدات",
        }

        return RecommendationROI(
            recommendation_type=recommendation_type,
            recommendation_type_ar=type_ar_map.get(recommendation_type, recommendation_type),
            investment_sar=round(investment_sar, 2),
            expected_return_sar=round(expected_return, 2),
            expected_roi_percent=round(roi, 1),
            payback_period_days=payback_days,
            confidence_percent=75.0,
            risk_level=risk_en,
            risk_level_ar=risk_ar,
        )

    def generate_field_report(
        self,
        field_id: str,
        field_name: str,
        field_name_ar: str,
        tenant_id: str,
        area_hectares: float,
        crop_type: str,
        crop_type_ar: str,
        season: Season,
        costs: list[CostEntry] | None = None,
        revenues: list[RevenueEntry] | None = None,
    ) -> FieldFinancialReport:
        """Generate a comprehensive financial report for a field.

        إنشاء تقرير مالي شامل لحقل.
        """
        costs = costs or []
        revenues = revenues or []

        total_costs = sum(c.amount_sar for c in costs)
        total_revenue = sum(r.total_revenue_sar for r in revenues)
        profit = total_revenue - total_costs

        cost_per_ha = total_costs / area_hectares if area_hectares > 0 else 0
        revenue_per_ha = total_revenue / area_hectares if area_hectares > 0 else 0
        profit_per_ha = profit / area_hectares if area_hectares > 0 else 0
        roi = ((profit / total_costs) * 100) if total_costs > 0 else 0

        price = self.CROP_PRICES.get(crop_type, 1500)
        break_even = self.calculate_break_even(total_costs, price, area_hectares)

        return FieldFinancialReport(
            report_id=f"FIN-{field_id}-{season.value}-{datetime.now().strftime('%Y%m%d')}",
            field_id=field_id,
            field_name=field_name,
            field_name_ar=field_name_ar,
            tenant_id=tenant_id,
            season=season,
            crop_type=crop_type,
            crop_type_ar=crop_type_ar,
            area_hectares=area_hectares,
            costs=costs,
            total_costs_sar=round(total_costs, 2),
            cost_per_hectare_sar=round(cost_per_ha, 2),
            cost_breakdown=self.calculate_cost_breakdown(costs),
            revenues=revenues,
            total_revenue_sar=round(total_revenue, 2),
            revenue_per_hectare_sar=round(revenue_per_ha, 2),
            profit_sar=round(profit, 2),
            profit_per_hectare_sar=round(profit_per_ha, 2),
            roi_percent=round(roi, 1),
            break_even_yield_ton=break_even,
            generated_at=datetime.now(UTC).isoformat(),
            message=f"Financial report for {field_name}: ROI {roi:.1f}%",
            message_ar=f"تقرير مالي لـ {field_name_ar}: العائد {roi:.1f}%",
        )

    def compare_seasons(
        self,
        current: FieldFinancialReport,
        previous: FieldFinancialReport,
    ) -> SeasonComparison:
        """Compare two seasons for a field.

        مقارنة موسمين لحقل.
        """
        cost_change = (
            ((current.total_costs_sar - previous.total_costs_sar) / previous.total_costs_sar * 100)
            if previous.total_costs_sar > 0
            else 0
        )
        rev_change = (
            ((current.total_revenue_sar - previous.total_revenue_sar) / previous.total_revenue_sar * 100)
            if previous.total_revenue_sar > 0
            else 0
        )
        profit_change = (
            ((current.profit_sar - previous.profit_sar) / abs(previous.profit_sar) * 100)
            if previous.profit_sar != 0
            else 0
        )

        recommendations = []
        recommendations_ar = []

        if cost_change > 15:
            recommendations.append("Review cost optimization opportunities")
            recommendations_ar.append("مراجعة فرص تحسين التكاليف")
        if rev_change < 0:
            recommendations.append("Consider crop variety change or market diversification")
            recommendations_ar.append("النظر في تغيير الصنف أو تنويع الأسواق")
        if current.roi_percent > previous.roi_percent:
            recommendations.append("Current practices are improving ROI - continue")
            recommendations_ar.append("الممارسات الحالية تحسّن العائد - استمر")

        return SeasonComparison(
            field_id=current.field_id,
            current_season=f"{current.season.value} {current.generated_at[:4]}",
            previous_season=f"{previous.season.value} {previous.generated_at[:4]}",
            cost_change_percent=round(cost_change, 1),
            revenue_change_percent=round(rev_change, 1),
            profit_change_percent=round(profit_change, 1),
            recommendations=recommendations,
            recommendations_ar=recommendations_ar,
        )
