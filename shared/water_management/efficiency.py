"""
Irrigation Efficiency Module - وحدة كفاءة الري
===============================================

Provides irrigation efficiency calculations and optimization:
- Water Use Efficiency (WUE)
- Irrigation Application Efficiency
- Distribution Uniformity
- Conveyance Efficiency
- Economic Water Productivity

Follows FAO guidelines and Saudi MEWA conservation standards.

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import statistics
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from .models import (
    AlertSeverity,
    IrrigationEvent,
    IrrigationMethod,
    WaterAlert,
    WaterAllocation,
)

# =============================================================================
# Efficiency Metrics Models - نماذج مقاييس الكفاءة
# =============================================================================


@dataclass
class EfficiencyBenchmarks:
    """
    Irrigation efficiency benchmarks - معايير كفاءة الري

    Standard efficiency values for different irrigation methods.
    Based on FAO and Saudi MEWA guidelines.
    """

    # Application efficiency (%) - كفاءة الإضافة
    APP_EFF_DRIP_MIN: float = 85.0
    APP_EFF_DRIP_GOOD: float = 90.0
    APP_EFF_DRIP_EXCELLENT: float = 95.0

    APP_EFF_SPRINKLER_MIN: float = 70.0
    APP_EFF_SPRINKLER_GOOD: float = 80.0
    APP_EFF_SPRINKLER_EXCELLENT: float = 85.0

    APP_EFF_PIVOT_MIN: float = 75.0
    APP_EFF_PIVOT_GOOD: float = 85.0
    APP_EFF_PIVOT_EXCELLENT: float = 90.0

    APP_EFF_FLOOD_MIN: float = 40.0
    APP_EFF_FLOOD_GOOD: float = 55.0
    APP_EFF_FLOOD_EXCELLENT: float = 65.0

    APP_EFF_FURROW_MIN: float = 50.0
    APP_EFF_FURROW_GOOD: float = 65.0
    APP_EFF_FURROW_EXCELLENT: float = 75.0

    # Distribution uniformity (%) - انتظام التوزيع
    DU_DRIP_MIN: float = 85.0
    DU_DRIP_GOOD: float = 90.0
    DU_SPRINKLER_MIN: float = 75.0
    DU_SPRINKLER_GOOD: float = 85.0
    DU_PIVOT_MIN: float = 80.0
    DU_PIVOT_GOOD: float = 88.0

    # Conveyance efficiency (%) - كفاءة النقل
    CONV_LINED_CANAL: float = 90.0
    CONV_UNLINED_CANAL: float = 70.0
    CONV_PIPE: float = 98.0

    # Water productivity (kg/m3) for major crops in Saudi Arabia
    WP_WHEAT_MIN: float = 0.8
    WP_WHEAT_GOOD: float = 1.2
    WP_WHEAT_EXCELLENT: float = 1.5

    WP_BARLEY_MIN: float = 0.6
    WP_BARLEY_GOOD: float = 1.0
    WP_BARLEY_EXCELLENT: float = 1.3

    WP_DATE_PALM_MIN: float = 1.5
    WP_DATE_PALM_GOOD: float = 2.5
    WP_DATE_PALM_EXCELLENT: float = 3.5

    WP_ALFALFA_MIN: float = 1.5
    WP_ALFALFA_GOOD: float = 2.0
    WP_ALFALFA_EXCELLENT: float = 2.8

    WP_TOMATO_MIN: float = 8.0
    WP_TOMATO_GOOD: float = 15.0
    WP_TOMATO_EXCELLENT: float = 25.0

    @classmethod
    def get_app_efficiency_benchmark(cls, method: IrrigationMethod) -> tuple[float, float, float]:
        """Get (min, good, excellent) benchmarks for irrigation method"""
        benchmarks = {
            IrrigationMethod.DRIP: (
                cls.APP_EFF_DRIP_MIN,
                cls.APP_EFF_DRIP_GOOD,
                cls.APP_EFF_DRIP_EXCELLENT,
            ),
            IrrigationMethod.SPRINKLER: (
                cls.APP_EFF_SPRINKLER_MIN,
                cls.APP_EFF_SPRINKLER_GOOD,
                cls.APP_EFF_SPRINKLER_EXCELLENT,
            ),
            IrrigationMethod.CENTER_PIVOT: (
                cls.APP_EFF_PIVOT_MIN,
                cls.APP_EFF_PIVOT_GOOD,
                cls.APP_EFF_PIVOT_EXCELLENT,
            ),
            IrrigationMethod.FLOOD: (
                cls.APP_EFF_FLOOD_MIN,
                cls.APP_EFF_FLOOD_GOOD,
                cls.APP_EFF_FLOOD_EXCELLENT,
            ),
            IrrigationMethod.FURROW: (
                cls.APP_EFF_FURROW_MIN,
                cls.APP_EFF_FURROW_GOOD,
                cls.APP_EFF_FURROW_EXCELLENT,
            ),
        }
        return benchmarks.get(method, (50.0, 70.0, 85.0))

    @classmethod
    def get_water_productivity_benchmark(cls, crop_type: str) -> tuple[float, float, float]:
        """Get (min, good, excellent) water productivity for crop (kg/m3)"""
        crop_lower = crop_type.lower()
        benchmarks = {
            "wheat": (cls.WP_WHEAT_MIN, cls.WP_WHEAT_GOOD, cls.WP_WHEAT_EXCELLENT),
            "قمح": (cls.WP_WHEAT_MIN, cls.WP_WHEAT_GOOD, cls.WP_WHEAT_EXCELLENT),
            "barley": (cls.WP_BARLEY_MIN, cls.WP_BARLEY_GOOD, cls.WP_BARLEY_EXCELLENT),
            "شعير": (cls.WP_BARLEY_MIN, cls.WP_BARLEY_GOOD, cls.WP_BARLEY_EXCELLENT),
            "date_palm": (
                cls.WP_DATE_PALM_MIN,
                cls.WP_DATE_PALM_GOOD,
                cls.WP_DATE_PALM_EXCELLENT,
            ),
            "date palm": (
                cls.WP_DATE_PALM_MIN,
                cls.WP_DATE_PALM_GOOD,
                cls.WP_DATE_PALM_EXCELLENT,
            ),
            "نخيل": (
                cls.WP_DATE_PALM_MIN,
                cls.WP_DATE_PALM_GOOD,
                cls.WP_DATE_PALM_EXCELLENT,
            ),
            "alfalfa": (
                cls.WP_ALFALFA_MIN,
                cls.WP_ALFALFA_GOOD,
                cls.WP_ALFALFA_EXCELLENT,
            ),
            "برسيم": (
                cls.WP_ALFALFA_MIN,
                cls.WP_ALFALFA_GOOD,
                cls.WP_ALFALFA_EXCELLENT,
            ),
            "tomato": (cls.WP_TOMATO_MIN, cls.WP_TOMATO_GOOD, cls.WP_TOMATO_EXCELLENT),
            "طماطم": (cls.WP_TOMATO_MIN, cls.WP_TOMATO_GOOD, cls.WP_TOMATO_EXCELLENT),
        }
        return benchmarks.get(crop_lower, (0.5, 1.0, 2.0))


@dataclass
class IrrigationEfficiencyMetrics:
    """
    Comprehensive irrigation efficiency metrics
    مقاييس كفاءة الري الشاملة
    """

    id: str
    tenant_id: str
    farm_id: str
    field_id: str
    calculation_date: datetime

    # Time period
    period_start: date | None = None
    period_end: date | None = None

    # Irrigation method
    irrigation_method: IrrigationMethod = IrrigationMethod.DRIP

    # Water volumes
    water_supplied_m3: float = 0.0  # Total water supplied
    water_stored_root_zone_m3: float | None = None  # Water in root zone
    water_lost_m3: float | None = None  # Losses (evap, runoff, deep percolation)

    # Application efficiency (Ea) - كفاءة الإضافة
    # Ea = (Water stored in root zone / Water applied) × 100
    application_efficiency: float | None = None

    # Distribution uniformity (DU) - انتظام التوزيع
    # DU = (Avg low quarter depth / Avg depth) × 100
    distribution_uniformity: float | None = None

    # Uniformity coefficient (UC) - معامل الانتظام
    # Christiansen's UC
    uniformity_coefficient: float | None = None

    # Conveyance efficiency - كفاءة النقل
    # Water delivered to field / Water taken from source
    conveyance_efficiency: float | None = None

    # Overall efficiency - الكفاءة الكلية
    # Ea × DU/100 × Conveyance/100
    overall_efficiency: float | None = None

    # Water use efficiency (WUE) - كفاءة استخدام المياه
    crop_yield_kg: float | None = None
    area_ha: float | None = None
    water_use_efficiency_kg_m3: float | None = None  # kg yield per m3 water

    # Economic water productivity - الإنتاجية المائية الاقتصادية
    crop_value_sar: float | None = None
    economic_water_productivity_sar_m3: float | None = None

    # Comparison to benchmarks
    efficiency_rating: str = "adequate"  # poor, adequate, good, excellent
    efficiency_rating_ar: str = "مقبول"

    # Recommendations
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Potential savings
    potential_water_savings_m3: float | None = None
    potential_water_savings_percent: float | None = None
    potential_cost_savings_sar: float | None = None

    def calculate_overall_efficiency(self) -> float | None:
        """Calculate overall irrigation efficiency"""
        if self.application_efficiency is None:
            return None

        overall = self.application_efficiency

        if self.distribution_uniformity is not None:
            overall *= self.distribution_uniformity / 100

        if self.conveyance_efficiency is not None:
            overall *= self.conveyance_efficiency / 100

        self.overall_efficiency = overall
        return overall

    def calculate_wue(self) -> float | None:
        """Calculate Water Use Efficiency (kg/m3)"""
        if self.crop_yield_kg is not None and self.water_supplied_m3 > 0:
            self.water_use_efficiency_kg_m3 = self.crop_yield_kg / self.water_supplied_m3
            return self.water_use_efficiency_kg_m3
        return None

    def calculate_economic_productivity(self) -> float | None:
        """Calculate economic water productivity (SAR/m3)"""
        if self.crop_value_sar is not None and self.water_supplied_m3 > 0:
            self.economic_water_productivity_sar_m3 = self.crop_value_sar / self.water_supplied_m3
            return self.economic_water_productivity_sar_m3
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "calculation_date": self.calculation_date.isoformat(),
            "period": {
                "start": self.period_start.isoformat() if self.period_start else None,
                "end": self.period_end.isoformat() if self.period_end else None,
            },
            "irrigation_method": self.irrigation_method.value,
            "water_volumes": {
                "supplied_m3": self.water_supplied_m3,
                "stored_root_zone_m3": self.water_stored_root_zone_m3,
                "lost_m3": self.water_lost_m3,
            },
            "efficiency_metrics": {
                "application_efficiency": self.application_efficiency,
                "distribution_uniformity": self.distribution_uniformity,
                "uniformity_coefficient": self.uniformity_coefficient,
                "conveyance_efficiency": self.conveyance_efficiency,
                "overall_efficiency": self.overall_efficiency,
            },
            "water_productivity": {
                "crop_yield_kg": self.crop_yield_kg,
                "area_ha": self.area_ha,
                "wue_kg_m3": self.water_use_efficiency_kg_m3,
                "crop_value_sar": self.crop_value_sar,
                "economic_productivity_sar_m3": self.economic_water_productivity_sar_m3,
            },
            "rating": {
                "level": self.efficiency_rating,
                "level_ar": self.efficiency_rating_ar,
            },
            "recommendations": {
                "en": self.recommendations_en,
                "ar": self.recommendations_ar,
            },
            "potential_savings": {
                "water_m3": self.potential_water_savings_m3,
                "water_percent": self.potential_water_savings_percent,
                "cost_sar": self.potential_cost_savings_sar,
            },
        }


@dataclass
class FieldWaterBalance:
    """
    Field water balance calculation
    حساب ميزان المياه في الحقل
    """

    field_id: str
    tenant_id: str
    period_start: date
    period_end: date

    # Inputs - المدخلات
    irrigation_m3: float = 0.0  # الري
    rainfall_mm: float = 0.0  # الأمطار
    rainfall_m3: float = 0.0  # Rainfall converted to m3
    capillary_rise_m3: float = 0.0  # الارتفاع الشعري

    # Outputs - المخرجات
    et_crop_mm: float = 0.0  # التبخر-نتح
    et_crop_m3: float = 0.0
    deep_percolation_m3: float = 0.0  # التسرب العميق
    runoff_m3: float = 0.0  # الجريان السطحي

    # Storage change - تغير التخزين
    soil_water_start_m3: float = 0.0
    soil_water_end_m3: float = 0.0
    storage_change_m3: float = 0.0

    # Field area
    area_ha: float = 0.0

    # Balance - الميزان
    # Inputs = Outputs + Storage Change
    balance_error_m3: float = 0.0
    balance_error_percent: float = 0.0

    def calculate_balance(self) -> float:
        """
        Calculate water balance.
        Inputs - Outputs = Storage Change
        """
        total_inputs = self.irrigation_m3 + self.rainfall_m3 + self.capillary_rise_m3
        total_outputs = self.et_crop_m3 + self.deep_percolation_m3 + self.runoff_m3
        calculated_storage_change = total_inputs - total_outputs

        self.storage_change_m3 = self.soil_water_end_m3 - self.soil_water_start_m3
        self.balance_error_m3 = calculated_storage_change - self.storage_change_m3

        if total_inputs > 0:
            self.balance_error_percent = (self.balance_error_m3 / total_inputs) * 100

        return self.balance_error_m3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "tenant_id": self.tenant_id,
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
            },
            "area_ha": self.area_ha,
            "inputs": {
                "irrigation_m3": self.irrigation_m3,
                "rainfall_mm": self.rainfall_mm,
                "rainfall_m3": self.rainfall_m3,
                "capillary_rise_m3": self.capillary_rise_m3,
                "total_m3": (self.irrigation_m3 + self.rainfall_m3 + self.capillary_rise_m3),
            },
            "outputs": {
                "et_crop_mm": self.et_crop_mm,
                "et_crop_m3": self.et_crop_m3,
                "deep_percolation_m3": self.deep_percolation_m3,
                "runoff_m3": self.runoff_m3,
                "total_m3": (self.et_crop_m3 + self.deep_percolation_m3 + self.runoff_m3),
            },
            "storage": {
                "start_m3": self.soil_water_start_m3,
                "end_m3": self.soil_water_end_m3,
                "change_m3": self.storage_change_m3,
            },
            "balance": {
                "error_m3": self.balance_error_m3,
                "error_percent": self.balance_error_percent,
            },
        }


# =============================================================================
# Efficiency Calculator - حاسبة الكفاءة
# =============================================================================


class IrrigationEfficiencyCalculator:
    """
    Irrigation efficiency calculator - حاسبة كفاءة الري

    Calculates various irrigation efficiency metrics and
    provides recommendations for improvement.
    """

    def __init__(self, tenant_id: str):
        """Initialize calculator for tenant"""
        self.tenant_id = tenant_id
        self.benchmarks = EfficiencyBenchmarks()

    def calculate_application_efficiency(
        self,
        water_applied_m3: float,
        water_stored_root_zone_m3: float,
    ) -> float:
        """
        Calculate irrigation application efficiency.
        حساب كفاءة إضافة الري

        Ea = (Water stored in root zone / Water applied) × 100
        """
        if water_applied_m3 <= 0:
            return 0.0
        return (water_stored_root_zone_m3 / water_applied_m3) * 100

    def calculate_distribution_uniformity(
        self,
        catch_can_depths_mm: list[float],
    ) -> float:
        """
        Calculate distribution uniformity from catch can test.
        حساب انتظام التوزيع من اختبار علب الالتقاط

        DU = (Average of lowest 25% / Overall average) × 100
        """
        if not catch_can_depths_mm or len(catch_can_depths_mm) < 4:
            return 0.0

        sorted_depths = sorted(catch_can_depths_mm)
        n_low_quarter = max(1, len(sorted_depths) // 4)
        low_quarter_avg = statistics.mean(sorted_depths[:n_low_quarter])
        overall_avg = statistics.mean(sorted_depths)

        if overall_avg <= 0:
            return 0.0

        return (low_quarter_avg / overall_avg) * 100

    def calculate_uniformity_coefficient(
        self,
        catch_can_depths_mm: list[float],
    ) -> float:
        """
        Calculate Christiansen's Uniformity Coefficient.
        حساب معامل انتظام كريستيانسن

        UC = 100 × (1 - (sum of deviations from mean / (n × mean)))
        """
        if not catch_can_depths_mm or len(catch_can_depths_mm) < 2:
            return 0.0

        mean_depth = statistics.mean(catch_can_depths_mm)
        if mean_depth <= 0:
            return 0.0

        sum_deviations = sum(abs(d - mean_depth) for d in catch_can_depths_mm)
        n = len(catch_can_depths_mm)

        return 100 * (1 - (sum_deviations / (n * mean_depth)))

    def calculate_conveyance_efficiency(
        self,
        water_diverted_m3: float,
        water_delivered_m3: float,
    ) -> float:
        """
        Calculate conveyance efficiency.
        حساب كفاءة النقل

        Ec = (Water delivered to field / Water diverted from source) × 100
        """
        if water_diverted_m3 <= 0:
            return 0.0
        return (water_delivered_m3 / water_diverted_m3) * 100

    def calculate_water_productivity(
        self,
        yield_kg: float,
        water_consumed_m3: float,
    ) -> float:
        """
        Calculate water productivity (Water Use Efficiency).
        حساب الإنتاجية المائية (كفاءة استخدام المياه)

        WP = Yield (kg) / Water consumed (m3)
        """
        if water_consumed_m3 <= 0:
            return 0.0
        return yield_kg / water_consumed_m3

    def calculate_economic_productivity(
        self,
        crop_value_sar: float,
        water_consumed_m3: float,
    ) -> float:
        """
        Calculate economic water productivity.
        حساب الإنتاجية المائية الاقتصادية

        EWP = Crop value (SAR) / Water consumed (m3)
        """
        if water_consumed_m3 <= 0:
            return 0.0
        return crop_value_sar / water_consumed_m3

    def evaluate_field_efficiency(
        self,
        field_id: str,
        farm_id: str,
        irrigation_events: list[IrrigationEvent],
        crop_type: str | None = None,
        crop_yield_kg: float | None = None,
        crop_value_sar: float | None = None,
        area_ha: float | None = None,
    ) -> IrrigationEfficiencyMetrics:
        """
        Evaluate overall field irrigation efficiency.
        تقييم كفاءة ري الحقل الكلية
        """
        if not irrigation_events:
            return IrrigationEfficiencyMetrics(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                farm_id=farm_id,
                field_id=field_id,
                calculation_date=datetime.now(UTC),
                efficiency_rating="insufficient_data",
                efficiency_rating_ar="بيانات غير كافية",
            )

        # Determine period
        events_sorted = sorted(irrigation_events, key=lambda e: e.started_at or datetime.now(UTC))
        period_start = (events_sorted[0].started_at or datetime.now(UTC)).date()
        period_end = (events_sorted[-1].ended_at or datetime.now(UTC)).date()

        # Get dominant irrigation method
        method_counts: dict[IrrigationMethod, int] = {}
        for event in irrigation_events:
            method_counts[event.irrigation_method] = method_counts.get(event.irrigation_method, 0) + 1
        irrigation_method = max(method_counts, key=method_counts.get)  # type: ignore

        # Calculate totals
        total_water_m3 = sum(e.volume_m3 for e in irrigation_events)
        total_area_ha = area_ha or (
            max(e.area_irrigated_ha for e in irrigation_events if e.area_irrigated_ha)
            if any(e.area_irrigated_ha for e in irrigation_events)
            else 0.0
        )

        # Calculate average application efficiency from events
        efficiencies = [e.application_efficiency for e in irrigation_events if e.application_efficiency is not None]
        avg_app_efficiency = statistics.mean(efficiencies) if efficiencies else None

        # Calculate average uniformity from events
        uniformities = [e.uniformity_coefficient for e in irrigation_events if e.uniformity_coefficient is not None]
        avg_uniformity = statistics.mean(uniformities) if uniformities else None

        # Create metrics object
        metrics = IrrigationEfficiencyMetrics(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            farm_id=farm_id,
            field_id=field_id,
            calculation_date=datetime.now(UTC),
            period_start=period_start,
            period_end=period_end,
            irrigation_method=irrigation_method,
            water_supplied_m3=total_water_m3,
            application_efficiency=avg_app_efficiency,
            uniformity_coefficient=avg_uniformity,
            crop_yield_kg=crop_yield_kg,
            crop_value_sar=crop_value_sar,
            area_ha=total_area_ha,
        )

        # Calculate WUE and economic productivity
        metrics.calculate_wue()
        metrics.calculate_economic_productivity()
        metrics.calculate_overall_efficiency()

        # Rate efficiency and generate recommendations
        self._rate_efficiency(metrics, crop_type)
        self._generate_recommendations(metrics, crop_type)
        self._calculate_potential_savings(metrics)

        return metrics

    def _rate_efficiency(
        self,
        metrics: IrrigationEfficiencyMetrics,
        crop_type: str | None = None,
    ) -> None:
        """Rate efficiency against benchmarks"""
        min_eff, good_eff, excellent_eff = self.benchmarks.get_app_efficiency_benchmark(metrics.irrigation_method)

        if metrics.application_efficiency is not None:
            eff = metrics.application_efficiency
            if eff >= excellent_eff:
                metrics.efficiency_rating = "excellent"
                metrics.efficiency_rating_ar = "ممتاز"
            elif eff >= good_eff:
                metrics.efficiency_rating = "good"
                metrics.efficiency_rating_ar = "جيد"
            elif eff >= min_eff:
                metrics.efficiency_rating = "adequate"
                metrics.efficiency_rating_ar = "مقبول"
            else:
                metrics.efficiency_rating = "poor"
                metrics.efficiency_rating_ar = "ضعيف"

    def _generate_recommendations(
        self,
        metrics: IrrigationEfficiencyMetrics,
        crop_type: str | None = None,
    ) -> None:
        """Generate efficiency improvement recommendations"""
        recommendations_en: list[str] = []
        recommendations_ar: list[str] = []

        # Application efficiency recommendations
        if metrics.application_efficiency is not None:
            min_eff, _, _ = self.benchmarks.get_app_efficiency_benchmark(metrics.irrigation_method)
            if metrics.application_efficiency < min_eff:
                if metrics.irrigation_method == IrrigationMethod.FLOOD:
                    recommendations_en.append(
                        "Consider upgrading to drip or sprinkler irrigation to improve efficiency by 30-50%"
                    )
                    recommendations_ar.append("فكر في الترقية إلى الري بالتنقيط أو الرش لتحسين الكفاءة بنسبة 30-50%")
                elif metrics.irrigation_method == IrrigationMethod.FURROW:
                    recommendations_en.append(
                        "Improve furrow inflow management or consider surge irrigation to reduce deep percolation"
                    )
                    recommendations_ar.append("حسّن إدارة تدفق الأخاديد أو فكر في الري النبضي لتقليل التسرب العميق")
                else:
                    recommendations_en.append(
                        "Check for system leaks and ensure proper system pressure and maintenance"
                    )
                    recommendations_ar.append("تحقق من تسربات النظام وتأكد من الضغط والصيانة المناسبين للنظام")

        # Uniformity recommendations
        if metrics.uniformity_coefficient is not None:
            if metrics.uniformity_coefficient < 80:
                recommendations_en.append("Perform system audit to identify emitter clogging or pressure variations")
                recommendations_ar.append("أجرِ تدقيقاً للنظام لتحديد انسداد النقاطات أو تغيرات الضغط")

        # Water productivity recommendations
        if crop_type and metrics.water_use_efficiency_kg_m3 is not None:
            min_wp, good_wp, _ = self.benchmarks.get_water_productivity_benchmark(crop_type)
            if metrics.water_use_efficiency_kg_m3 < min_wp:
                recommendations_en.append(
                    f"Water productivity is below benchmark for {crop_type}. "
                    "Review irrigation scheduling and crop variety selection"
                )
                recommendations_ar.append(
                    f"الإنتاجية المائية أقل من المعيار لـ {crop_type}. راجع جدولة الري واختيار الصنف"
                )

        # Method-specific recommendations
        if metrics.irrigation_method == IrrigationMethod.CENTER_PIVOT:
            recommendations_en.append(
                "Consider LEPA (Low Energy Precision Application) nozzles to reduce evaporation losses"
            )
            recommendations_ar.append("فكر في فوهات LEPA (التطبيق الدقيق منخفض الطاقة) لتقليل فقد التبخر")

        if metrics.irrigation_method == IrrigationMethod.DRIP:
            recommendations_en.append("Monitor filter pressure differential and flush laterals regularly")
            recommendations_ar.append("راقب فرق ضغط المرشح واغسل الأنابيب الجانبية بانتظام")

        metrics.recommendations_en = recommendations_en
        metrics.recommendations_ar = recommendations_ar

    def _calculate_potential_savings(
        self,
        metrics: IrrigationEfficiencyMetrics,
        water_cost_sar_m3: float = 0.5,
    ) -> None:
        """Calculate potential water and cost savings"""
        if metrics.application_efficiency is None or metrics.water_supplied_m3 <= 0:
            return

        _, good_eff, _ = self.benchmarks.get_app_efficiency_benchmark(metrics.irrigation_method)

        if metrics.application_efficiency < good_eff:
            # Calculate water that could be saved
            current_eff = metrics.application_efficiency / 100
            target_eff = good_eff / 100

            # Water needed at target efficiency
            useful_water = metrics.water_supplied_m3 * current_eff
            water_at_target = useful_water / target_eff

            potential_savings = metrics.water_supplied_m3 - water_at_target

            if potential_savings > 0:
                metrics.potential_water_savings_m3 = potential_savings
                metrics.potential_water_savings_percent = (potential_savings / metrics.water_supplied_m3) * 100
                metrics.potential_cost_savings_sar = potential_savings * water_cost_sar_m3


# =============================================================================
# Efficiency Alerts - تنبيهات الكفاءة
# =============================================================================


class EfficiencyAlertGenerator:
    """
    Generate alerts for irrigation efficiency issues.
    إنشاء تنبيهات لمشاكل كفاءة الري
    """

    def __init__(self, tenant_id: str):
        """Initialize alert generator"""
        self.tenant_id = tenant_id
        self.benchmarks = EfficiencyBenchmarks()

    def check_efficiency_alerts(
        self,
        metrics: IrrigationEfficiencyMetrics,
    ) -> list[WaterAlert]:
        """
        Check efficiency metrics and generate alerts.
        فحص مقاييس الكفاءة وإنشاء التنبيهات
        """
        alerts: list[WaterAlert] = []

        # Check application efficiency
        if metrics.application_efficiency is not None:
            min_eff, _, _ = self.benchmarks.get_app_efficiency_benchmark(metrics.irrigation_method)
            if metrics.application_efficiency < min_eff:
                alerts.append(
                    WaterAlert(
                        id=str(uuid.uuid4()),
                        tenant_id=self.tenant_id,
                        farm_id=metrics.farm_id,
                        field_id=metrics.field_id,
                        alert_type="low_irrigation_efficiency",
                        severity=AlertSeverity.HIGH,
                        title_en="Low Irrigation Efficiency",
                        title_ar="كفاءة ري منخفضة",
                        message_en=f"Application efficiency ({metrics.application_efficiency:.1f}%) "
                        f"is below minimum standard ({min_eff:.0f}%)",
                        message_ar=f"كفاءة الإضافة ({metrics.application_efficiency:.1f}%) "
                        f"أقل من الحد الأدنى المعياري ({min_eff:.0f}%)",
                        triggered_value=metrics.application_efficiency,
                        threshold_value=min_eff,
                        unit="%",
                        recommended_action_en="Review irrigation system for leaks, clogging, or scheduling issues",
                        recommended_action_ar="راجع نظام الري للتسربات أو الانسداد أو مشاكل الجدولة",
                    )
                )

        # Check uniformity
        if metrics.uniformity_coefficient is not None:
            if metrics.uniformity_coefficient < 75:
                alerts.append(
                    WaterAlert(
                        id=str(uuid.uuid4()),
                        tenant_id=self.tenant_id,
                        farm_id=metrics.farm_id,
                        field_id=metrics.field_id,
                        alert_type="poor_distribution_uniformity",
                        severity=AlertSeverity.MEDIUM,
                        title_en="Poor Water Distribution Uniformity",
                        title_ar="ضعف انتظام توزيع المياه",
                        message_en=f"Uniformity coefficient ({metrics.uniformity_coefficient:.1f}%) "
                        "indicates uneven water distribution",
                        message_ar=f"معامل الانتظام ({metrics.uniformity_coefficient:.1f}%) "
                        "يشير إلى توزيع مياه غير متساوٍ",
                        triggered_value=metrics.uniformity_coefficient,
                        threshold_value=75.0,
                        unit="%",
                        recommended_action_en="Perform catch can test and "
                        "check for emitter clogging or pressure issues",
                        recommended_action_ar="أجرِ اختبار علب الالتقاط وتحقق من انسداد النقاطات أو مشاكل الضغط",
                    )
                )

        # Check for significant water losses
        if metrics.water_lost_m3 is not None and metrics.water_supplied_m3 > 0:
            loss_percent = (metrics.water_lost_m3 / metrics.water_supplied_m3) * 100
            if loss_percent > 40:
                alerts.append(
                    WaterAlert(
                        id=str(uuid.uuid4()),
                        tenant_id=self.tenant_id,
                        farm_id=metrics.farm_id,
                        field_id=metrics.field_id,
                        alert_type="high_water_losses",
                        severity=AlertSeverity.HIGH,
                        title_en="High Water Losses Detected",
                        title_ar="اكتشاف فقد مياه مرتفع",
                        message_en=f"Water losses at {loss_percent:.1f}% of supplied water",
                        message_ar=f"فقد المياه يبلغ {loss_percent:.1f}% من المياه المقدمة",
                        triggered_value=loss_percent,
                        threshold_value=40.0,
                        unit="%",
                        recommended_action_en="Investigate sources of water loss: "
                        "deep percolation, runoff, or evaporation",
                        recommended_action_ar="حقق في مصادر فقد المياه: التسرب العميق أو الجريان السطحي أو التبخر",
                    )
                )

        return alerts

    def check_allocation_usage(
        self,
        allocation: WaterAllocation,
        warning_threshold: float = 80.0,
        critical_threshold: float = 95.0,
    ) -> list[WaterAlert]:
        """
        Check allocation usage and generate alerts.
        فحص استخدام التخصيص وإنشاء التنبيهات
        """
        alerts: list[WaterAlert] = []
        utilization = allocation.utilization_percent

        if utilization >= critical_threshold:
            alerts.append(
                WaterAlert(
                    id=str(uuid.uuid4()),
                    tenant_id=allocation.tenant_id,
                    farm_id=allocation.farm_id,
                    field_id=allocation.field_id,
                    alert_type="allocation_critical",
                    severity=AlertSeverity.CRITICAL,
                    title_en="Water Allocation Nearly Exhausted",
                    title_ar="تخصيص المياه على وشك النفاد",
                    message_en=f"Used {utilization:.1f}% of water allocation. "
                    f"Only {allocation.remaining_m3:.0f} m3 remaining",
                    message_ar=f"استُخدم {utilization:.1f}% من تخصيص المياه. يتبقى فقط {allocation.remaining_m3:.0f} م3",
                    triggered_value=utilization,
                    threshold_value=critical_threshold,
                    unit="%",
                    recommended_action_en="Immediately review irrigation schedule and consider water-saving measures",
                    recommended_action_ar="راجع جدول الري فوراً وفكر في إجراءات توفير المياه",
                )
            )
        elif utilization >= warning_threshold:
            alerts.append(
                WaterAlert(
                    id=str(uuid.uuid4()),
                    tenant_id=allocation.tenant_id,
                    farm_id=allocation.farm_id,
                    field_id=allocation.field_id,
                    alert_type="allocation_warning",
                    severity=AlertSeverity.HIGH,
                    title_en="Water Allocation High Usage Warning",
                    title_ar="تحذير استخدام مرتفع لتخصيص المياه",
                    message_en=f"Used {utilization:.1f}% of water allocation. "
                    f"{allocation.remaining_m3:.0f} m3 remaining",
                    message_ar=f"استُخدم {utilization:.1f}% من تخصيص المياه. يتبقى {allocation.remaining_m3:.0f} م3",
                    triggered_value=utilization,
                    threshold_value=warning_threshold,
                    unit="%",
                    recommended_action_en="Plan irrigation carefully for remaining season",
                    recommended_action_ar="خطط للري بعناية لبقية الموسم",
                )
            )

        return alerts


# =============================================================================
# Water Conservation Calculator - حاسبة الحفاظ على المياه
# =============================================================================


class WaterConservationCalculator:
    """
    Calculate water conservation metrics and recommendations.
    حساب مقاييس وتوصيات الحفاظ على المياه
    """

    def __init__(self, tenant_id: str):
        """Initialize calculator"""
        self.tenant_id = tenant_id

    def calculate_deficit_irrigation_savings(
        self,
        full_et_mm: float,
        deficit_percent: float,
        area_ha: float,
        expected_yield_reduction_percent: float = 0.0,
    ) -> dict[str, Any]:
        """
        Calculate water savings from deficit irrigation.
        حساب توفير المياه من الري الناقص

        Deficit irrigation applies less than full crop ET,
        accepting some yield reduction for significant water savings.
        """
        full_water_m3 = (full_et_mm / 1000) * (area_ha * 10000)
        deficit_water_m3 = full_water_m3 * (1 - deficit_percent / 100)
        savings_m3 = full_water_m3 - deficit_water_m3

        return {
            "full_water_requirement_m3": full_water_m3,
            "deficit_irrigation_m3": deficit_water_m3,
            "water_savings_m3": savings_m3,
            "water_savings_percent": deficit_percent,
            "expected_yield_reduction_percent": expected_yield_reduction_percent,
            "recommendation_en": f"Apply {100 - deficit_percent:.0f}% of full ET "
            f"to save {savings_m3:.0f} m3 with {expected_yield_reduction_percent:.0f}% yield impact",
            "recommendation_ar": f"طبق {100 - deficit_percent:.0f}% من التبخر-نتح الكامل "
            f"لتوفير {savings_m3:.0f} م3 مع تأثير {expected_yield_reduction_percent:.0f}% على المحصول",
        }

    def calculate_mulching_savings(
        self,
        et_without_mulch_mm_day: float,
        mulch_reduction_percent: float,
        area_ha: float,
        season_days: int,
    ) -> dict[str, Any]:
        """
        Calculate water savings from mulching.
        حساب توفير المياه من التغطية

        Mulching reduces soil evaporation by 20-40%.
        """
        daily_et_m3 = (et_without_mulch_mm_day / 1000) * (area_ha * 10000)
        daily_savings_m3 = daily_et_m3 * (mulch_reduction_percent / 100)
        season_savings_m3 = daily_savings_m3 * season_days

        return {
            "daily_et_without_mulch_m3": daily_et_m3,
            "daily_savings_m3": daily_savings_m3,
            "season_savings_m3": season_savings_m3,
            "savings_percent": mulch_reduction_percent,
            "recommendation_en": f"Apply mulch to save approximately {season_savings_m3:.0f} m3 "
            f"over {season_days} days",
            "recommendation_ar": f"طبق التغطية لتوفير حوالي {season_savings_m3:.0f} م3 خلال {season_days} يوم",
        }

    def calculate_irrigation_upgrade_savings(
        self,
        current_method: IrrigationMethod,
        proposed_method: IrrigationMethod,
        current_water_use_m3: float,
    ) -> dict[str, Any]:
        """
        Calculate water savings from irrigation method upgrade.
        حساب توفير المياه من ترقية طريقة الري
        """
        benchmarks = EfficiencyBenchmarks()
        current_eff = benchmarks.get_app_efficiency_benchmark(current_method)[1] / 100
        proposed_eff = benchmarks.get_app_efficiency_benchmark(proposed_method)[1] / 100

        if proposed_eff <= current_eff:
            return {
                "current_method": current_method.value,
                "proposed_method": proposed_method.value,
                "message": "Proposed method is not more efficient",
                "message_ar": "الطريقة المقترحة ليست أكثر كفاءة",
            }

        # Water needed at proposed efficiency
        useful_water = current_water_use_m3 * current_eff
        proposed_water_use = useful_water / proposed_eff
        savings_m3 = current_water_use_m3 - proposed_water_use
        savings_percent = (savings_m3 / current_water_use_m3) * 100

        return {
            "current_method": current_method.value,
            "proposed_method": proposed_method.value,
            "current_efficiency_percent": current_eff * 100,
            "proposed_efficiency_percent": proposed_eff * 100,
            "current_water_use_m3": current_water_use_m3,
            "proposed_water_use_m3": proposed_water_use,
            "water_savings_m3": savings_m3,
            "water_savings_percent": savings_percent,
            "recommendation_en": f"Upgrade from {current_method.value} to {proposed_method.value} "
            f"to save {savings_m3:.0f} m3 ({savings_percent:.0f}%)",
            "recommendation_ar": f"قم بالترقية من {current_method.value} إلى {proposed_method.value} "
            f"لتوفير {savings_m3:.0f} م3 ({savings_percent:.0f}%)",
        }
