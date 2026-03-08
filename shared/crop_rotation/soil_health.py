"""
Soil Health Tracking Module - وحدة تتبع صحة التربة

Tracks soil health improvements over crop rotations:
- Organic matter changes
- Nutrient levels and trends
- Soil structure indicators
- Biological activity
- Impact analysis of rotation decisions

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any

from .models import (
    CropType,
    SoilHealthIndicator,
    SoilHealthMeasurement,
    SoilHealthReport,
    SoilHealthTrend,
)

# =============================================================================
# Enums and Constants - التعدادات والثوابت
# =============================================================================


class SoilHealthRating(StrEnum):
    """Overall soil health rating"""

    EXCELLENT = "excellent"  # ممتاز
    GOOD = "good"  # جيد
    FAIR = "fair"  # مقبول
    POOR = "poor"  # ضعيف
    CRITICAL = "critical"  # حرج


class TrendDirection(StrEnum):
    """Trend direction for indicators"""

    IMPROVING = "improving"  # تحسن
    STABLE = "stable"  # مستقر
    DECLINING = "declining"  # تراجع


# Optimal ranges for soil health indicators (Middle East agricultural context)
OPTIMAL_RANGES: dict[SoilHealthIndicator, dict[str, float]] = {
    SoilHealthIndicator.ORGANIC_MATTER: {
        "critical_low": 0.5,
        "low": 1.0,
        "optimal_min": 2.0,
        "optimal_max": 5.0,
        "high": 8.0,
        "unit": "%",
    },
    SoilHealthIndicator.NITROGEN: {
        "critical_low": 10,
        "low": 25,
        "optimal_min": 40,
        "optimal_max": 80,
        "high": 120,
        "unit": "kg/ha",
    },
    SoilHealthIndicator.PHOSPHORUS: {
        "critical_low": 5,
        "low": 15,
        "optimal_min": 25,
        "optimal_max": 50,
        "high": 80,
        "unit": "ppm",
    },
    SoilHealthIndicator.POTASSIUM: {
        "critical_low": 80,
        "low": 150,
        "optimal_min": 200,
        "optimal_max": 400,
        "high": 600,
        "unit": "ppm",
    },
    SoilHealthIndicator.PH: {
        "critical_low": 5.0,
        "low": 5.5,
        "optimal_min": 6.5,
        "optimal_max": 7.5,
        "high": 8.5,
        "unit": "pH",
    },
    SoilHealthIndicator.EC: {
        "critical_low": 0.0,
        "low": 0.5,
        "optimal_min": 0.0,
        "optimal_max": 2.0,
        "high": 4.0,  # High salinity is bad
        "unit": "dS/m",
    },
    SoilHealthIndicator.MICROBIAL_ACTIVITY: {
        "critical_low": 50,
        "low": 100,
        "optimal_min": 200,
        "optimal_max": 500,
        "high": 800,
        "unit": "mg/kg",
    },
}


# Expected soil health impacts from different crop types
CROP_SOIL_IMPACT: dict[CropType, dict[str, float]] = {
    CropType.WHEAT: {
        "organic_matter_change": 0.02,  # Small increase from residues
        "nitrogen_change": -80,  # High N uptake
        "soil_structure_impact": 0.5,  # Moderate - fibrous roots
    },
    CropType.BARLEY: {
        "organic_matter_change": 0.02,
        "nitrogen_change": -50,
        "soil_structure_impact": 0.5,
    },
    CropType.MAIZE: {
        "organic_matter_change": 0.03,  # Good residue
        "nitrogen_change": -100,
        "soil_structure_impact": 0.6,
    },
    CropType.SORGHUM: {
        "organic_matter_change": 0.03,
        "nitrogen_change": -60,
        "soil_structure_impact": 0.7,  # Deep roots
    },
    CropType.ALFALFA: {
        "organic_matter_change": 0.15,  # High organic matter
        "nitrogen_change": 150,  # Fixes N
        "soil_structure_impact": 0.9,  # Deep taproot
    },
    CropType.CLOVER: {
        "organic_matter_change": 0.10,
        "nitrogen_change": 100,
        "soil_structure_impact": 0.7,
    },
    CropType.FABA_BEAN: {
        "organic_matter_change": 0.05,
        "nitrogen_change": 80,
        "soil_structure_impact": 0.6,
    },
    CropType.CHICKPEA: {
        "organic_matter_change": 0.03,
        "nitrogen_change": 60,
        "soil_structure_impact": 0.5,
    },
    CropType.TOMATO: {
        "organic_matter_change": 0.01,
        "nitrogen_change": -70,
        "soil_structure_impact": 0.3,
    },
    CropType.POTATO: {
        "organic_matter_change": 0.0,
        "nitrogen_change": -60,
        "soil_structure_impact": 0.2,  # Soil disturbance from harvest
    },
    CropType.ONION: {
        "organic_matter_change": 0.0,
        "nitrogen_change": -40,
        "soil_structure_impact": 0.2,
    },
    CropType.GREEN_MANURE: {
        "organic_matter_change": 0.20,  # High incorporation
        "nitrogen_change": 80,
        "soil_structure_impact": 0.8,
    },
    CropType.FALLOW: {
        "organic_matter_change": -0.05,  # Slight decline without cover
        "nitrogen_change": 0,
        "soil_structure_impact": 0.3,
    },
}


# =============================================================================
# Soil Health Tracker Class - فئة تتبع صحة التربة
# =============================================================================


@dataclass
class SoilHealthTrackerConfig:
    """Configuration for soil health tracking"""

    # Measurement frequency
    recommended_test_frequency_months: int = 6
    minimum_measurements_for_trend: int = 3

    # Scoring weights
    weight_organic_matter: float = 0.25
    weight_nutrients: float = 0.25
    weight_physical: float = 0.20
    weight_biological: float = 0.15
    weight_chemical_balance: float = 0.15

    # Alert thresholds
    critical_decline_threshold_percent: float = 15.0  # Alert if indicator drops > 15%
    improvement_threshold_percent: float = 10.0  # Notable improvement


class SoilHealthTracker:
    """
    Soil health tracking and analysis engine
    محرك تتبع وتحليل صحة التربة

    Features:
    - Track soil health measurements over time
    - Analyze trends for key indicators
    - Assess impact of crop rotations
    - Generate recommendations for improvement
    - Calculate soil health scores
    """

    def __init__(self, config: SoilHealthTrackerConfig | None = None):
        """Initialize tracker with configuration"""
        self.config = config or SoilHealthTrackerConfig()
        self.measurements: dict[str, list[SoilHealthMeasurement]] = {}  # field_id -> measurements

    def add_measurement(self, measurement: SoilHealthMeasurement) -> None:
        """Add a soil health measurement for tracking"""
        field_id = measurement.field_id
        if field_id not in self.measurements:
            self.measurements[field_id] = []
        self.measurements[field_id].append(measurement)
        # Sort by date
        self.measurements[field_id].sort(key=lambda m: m.measurement_date)

    def get_measurements(
        self,
        field_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[SoilHealthMeasurement]:
        """Get measurements for a field within date range"""
        measurements = self.measurements.get(field_id, [])

        if start_date:
            measurements = [m for m in measurements if m.measurement_date >= start_date]
        if end_date:
            measurements = [m for m in measurements if m.measurement_date <= end_date]

        return measurements

    def calculate_indicator_trend(
        self,
        field_id: str,
        indicator: SoilHealthIndicator,
        years: int = 3,
    ) -> SoilHealthTrend:
        """
        Calculate trend for a specific soil health indicator
        حساب الاتجاه لمؤشر صحة تربة محدد
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=years * 365)

        measurements = self.get_measurements(field_id, start_date, end_date)

        # Extract values for the indicator
        values = []
        dates = []
        for m in measurements:
            value = self._get_indicator_value(m, indicator)
            if value is not None:
                values.append(value)
                dates.append(m.measurement_date)

        trend = SoilHealthTrend(
            field_id=field_id,
            indicator=indicator,
            start_date=start_date,
            end_date=end_date,
            measurement_count=len(values),
        )

        if len(values) < 2:
            trend.trend_direction = "stable"
            trend.status = "unknown"
            trend.status_ar = "غير معروف"
            return trend

        # Calculate statistics
        trend.initial_value = values[0]
        trend.current_value = values[-1]
        trend.min_value = min(values)
        trend.max_value = max(values)
        trend.avg_value = statistics.mean(values)

        if len(values) > 1:
            trend.std_deviation = statistics.stdev(values)

        # Calculate change
        if trend.initial_value and trend.initial_value != 0:
            trend.change_percent = (trend.current_value - trend.initial_value) / trend.initial_value * 100

        # Calculate annual rate of change
        if dates and len(dates) >= 2:
            days_span = (dates[-1] - dates[0]).days
            if days_span > 0:
                trend.change_rate_per_year = (values[-1] - values[0]) / (days_span / 365)

        # Determine trend direction
        if trend.change_percent > 5:
            trend.trend_direction = TrendDirection.IMPROVING.value
        elif trend.change_percent < -5:
            trend.trend_direction = TrendDirection.DECLINING.value
        else:
            trend.trend_direction = TrendDirection.STABLE.value

        # Determine status based on optimal ranges
        trend.status, trend.status_ar = self._assess_indicator_status(indicator, trend.current_value)

        # Get target value
        optimal = OPTIMAL_RANGES.get(indicator, {})
        if optimal:
            trend.target_value = (optimal.get("optimal_min", 0) + optimal.get("optimal_max", 0)) / 2

        # Generate recommendations
        trend.recommendations, trend.recommendations_ar = self._generate_indicator_recommendations(indicator, trend)

        return trend

    def _get_indicator_value(
        self,
        measurement: SoilHealthMeasurement,
        indicator: SoilHealthIndicator,
    ) -> float | None:
        """Extract indicator value from measurement"""
        mapping = {
            SoilHealthIndicator.ORGANIC_MATTER: measurement.organic_matter_percent,
            SoilHealthIndicator.NITROGEN: measurement.nitrogen_available_kg_ha,
            SoilHealthIndicator.PHOSPHORUS: measurement.phosphorus_ppm,
            SoilHealthIndicator.POTASSIUM: measurement.potassium_ppm,
            SoilHealthIndicator.PH: measurement.ph,
            SoilHealthIndicator.EC: measurement.ec_ds_m,
            SoilHealthIndicator.MICROBIAL_ACTIVITY: measurement.microbial_biomass_mg_kg,
            SoilHealthIndicator.WATER_RETENTION: measurement.water_holding_capacity_mm_m,
        }
        return mapping.get(indicator)

    def _assess_indicator_status(
        self,
        indicator: SoilHealthIndicator,
        value: float | None,
    ) -> tuple[str, str]:
        """Assess status of an indicator value"""
        if value is None:
            return "unknown", "غير معروف"

        ranges = OPTIMAL_RANGES.get(indicator, {})
        if not ranges:
            return "adequate", "كافي"

        # Special handling for EC (lower is better for salinity)
        if indicator == SoilHealthIndicator.EC:
            if value <= ranges.get("optimal_max", 2.0):
                return "optimal", "مثالي"
            elif value <= ranges.get("high", 4.0):
                return "elevated", "مرتفع"
            else:
                return "excessive", "مفرط"

        # Standard assessment
        if value < ranges.get("critical_low", 0):
            return "critical", "حرج"
        elif value < ranges.get("low", 0):
            return "deficient", "ناقص"
        elif value < ranges.get("optimal_min", 0):
            return "low", "منخفض"
        elif value <= ranges.get("optimal_max", float("inf")):
            return "optimal", "مثالي"
        elif value <= ranges.get("high", float("inf")):
            return "high", "مرتفع"
        else:
            return "excessive", "مفرط"

    def _generate_indicator_recommendations(
        self,
        indicator: SoilHealthIndicator,
        trend: SoilHealthTrend,
    ) -> tuple[list[str], list[str]]:
        """Generate recommendations for an indicator"""
        recs_en = []
        recs_ar = []

        status = trend.status
        direction = trend.trend_direction

        # Organic matter recommendations
        if indicator == SoilHealthIndicator.ORGANIC_MATTER:
            if status in ["critical", "deficient", "low"]:
                recs_en.extend(
                    [
                        "Add organic amendments (compost, manure)",
                        "Include green manure crops in rotation",
                        "Return crop residues to field",
                        "Consider cover cropping",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة مصلحات عضوية (كمبوست، سماد حيواني)",
                        "إدراج محاصيل السماد الأخضر في الدورة",
                        "إعادة مخلفات المحاصيل للحقل",
                        "النظر في المحاصيل الغطائية",
                    ]
                )
            if direction == TrendDirection.DECLINING.value:
                recs_en.append("Urgent: Halt organic matter decline with cover crops")
                recs_ar.append("عاجل: وقف تراجع المادة العضوية بالمحاصيل الغطائية")

        # Nitrogen recommendations
        elif indicator == SoilHealthIndicator.NITROGEN:
            if status in ["critical", "deficient", "low"]:
                recs_en.extend(
                    [
                        "Increase legume frequency in rotation",
                        "Apply nitrogen fertilizer based on crop needs",
                        "Consider split nitrogen applications",
                    ]
                )
                recs_ar.extend(
                    [
                        "زيادة تكرار البقوليات في الدورة",
                        "إضافة سماد نيتروجيني حسب احتياج المحصول",
                        "النظر في تجزئة إضافة النيتروجين",
                    ]
                )
            elif status in ["high", "excessive"]:
                recs_en.append("Reduce nitrogen inputs to prevent leaching")
                recs_ar.append("تقليل مدخلات النيتروجين لمنع الغسيل")

        # Phosphorus recommendations
        elif indicator == SoilHealthIndicator.PHOSPHORUS:
            if status in ["critical", "deficient", "low"]:
                recs_en.extend(
                    [
                        "Apply phosphorus fertilizer",
                        "Consider mycorrhizal inoculants to improve P uptake",
                        "Maintain soil pH 6.5-7.0 for optimal P availability",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة سماد فسفوري",
                        "استخدام لقاحات الميكوريزا لتحسين امتصاص الفسفور",
                        "الحفاظ على pH التربة 6.5-7.0 لتوفر الفسفور المثالي",
                    ]
                )

        # Potassium recommendations
        elif indicator == SoilHealthIndicator.POTASSIUM:
            if status in ["critical", "deficient", "low"]:
                recs_en.extend(
                    [
                        "Apply potassium fertilizer",
                        "Return crop residues (high in K)",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة سماد بوتاسي",
                        "إعادة مخلفات المحاصيل (غنية بالبوتاسيوم)",
                    ]
                )

        # pH recommendations
        elif indicator == SoilHealthIndicator.PH:
            if status == "low":
                recs_en.extend(
                    [
                        "Apply agricultural lime to raise pH",
                        "Monitor lime application effects over time",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة الجير الزراعي لرفع pH",
                        "مراقبة تأثير إضافة الجير بمرور الوقت",
                    ]
                )
            elif status in ["high", "excessive"]:
                recs_en.extend(
                    [
                        "Apply sulfur or acidifying amendments",
                        "Use ammonium-based fertilizers",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة الكبريت أو مصلحات محمضة",
                        "استخدام أسمدة أمونيومية",
                    ]
                )

        # EC (Salinity) recommendations
        elif indicator == SoilHealthIndicator.EC:
            if status in ["elevated", "excessive"]:
                recs_en.extend(
                    [
                        "Improve drainage",
                        "Apply leaching irrigation",
                        "Use salt-tolerant crops",
                        "Add gypsum to improve soil structure",
                    ]
                )
                recs_ar.extend(
                    [
                        "تحسين الصرف",
                        "تطبيق ري غسيل",
                        "استخدام محاصيل متحملة للملوحة",
                        "إضافة الجبس لتحسين بنية التربة",
                    ]
                )

        # Microbial activity recommendations
        elif indicator == SoilHealthIndicator.MICROBIAL_ACTIVITY:
            if status in ["critical", "deficient", "low"]:
                recs_en.extend(
                    [
                        "Add organic matter to feed soil microbes",
                        "Reduce tillage to protect soil biology",
                        "Diversify crop rotation",
                        "Avoid excessive pesticide use",
                    ]
                )
                recs_ar.extend(
                    [
                        "إضافة مادة عضوية لتغذية ميكروبات التربة",
                        "تقليل الحراثة لحماية الحياة الحيوية للتربة",
                        "تنويع الدورة الزراعية",
                        "تجنب الاستخدام المفرط للمبيدات",
                    ]
                )

        return recs_en, recs_ar

    def calculate_soil_health_score(
        self,
        measurement: SoilHealthMeasurement,
    ) -> tuple[float, dict[str, float]]:
        """
        Calculate overall soil health score from measurement
        حساب درجة صحة التربة الإجمالية من القياس

        Returns (overall_score, component_scores) where scores are 0-100
        """
        component_scores = {}

        # Organic matter score (25%)
        if measurement.organic_matter_percent is not None:
            om_score = self._calculate_component_score(
                SoilHealthIndicator.ORGANIC_MATTER, measurement.organic_matter_percent
            )
            component_scores["organic_matter"] = om_score
        else:
            component_scores["organic_matter"] = 50.0  # Default if not measured

        # Nutrient score (25%) - average of N, P, K
        nutrient_scores = []
        if measurement.nitrogen_available_kg_ha is not None:
            nutrient_scores.append(
                self._calculate_component_score(SoilHealthIndicator.NITROGEN, measurement.nitrogen_available_kg_ha)
            )
        if measurement.phosphorus_ppm is not None:
            nutrient_scores.append(
                self._calculate_component_score(SoilHealthIndicator.PHOSPHORUS, measurement.phosphorus_ppm)
            )
        if measurement.potassium_ppm is not None:
            nutrient_scores.append(
                self._calculate_component_score(SoilHealthIndicator.POTASSIUM, measurement.potassium_ppm)
            )

        if nutrient_scores:
            component_scores["nutrients"] = statistics.mean(nutrient_scores)
        else:
            component_scores["nutrients"] = 50.0

        # Physical score (20%) - structure, water retention
        physical_scores = []
        if measurement.water_holding_capacity_mm_m is not None:
            # Normalize to 0-100 (assuming 50-200 mm/m is good range)
            whc_score = min(100, max(0, (measurement.water_holding_capacity_mm_m - 30) / 1.7))
            physical_scores.append(whc_score)
        if measurement.bulk_density_g_cm3 is not None:
            # Lower bulk density generally better (1.0-1.4 is good)
            bd_score = max(0, min(100, (1.6 - measurement.bulk_density_g_cm3) / 0.006))
            physical_scores.append(bd_score)
        if measurement.infiltration_rate_mm_hr is not None:
            # 10-25 mm/hr is good
            inf_score = min(100, max(0, measurement.infiltration_rate_mm_hr * 4))
            physical_scores.append(inf_score)

        if physical_scores:
            component_scores["physical"] = statistics.mean(physical_scores)
        else:
            component_scores["physical"] = 50.0

        # Biological score (15%)
        if measurement.microbial_biomass_mg_kg is not None:
            bio_score = self._calculate_component_score(
                SoilHealthIndicator.MICROBIAL_ACTIVITY, measurement.microbial_biomass_mg_kg
            )
            component_scores["biological"] = bio_score
        else:
            component_scores["biological"] = 50.0

        # Chemical balance score (15%) - pH and EC
        chemical_scores = []
        if measurement.ph is not None:
            chemical_scores.append(self._calculate_component_score(SoilHealthIndicator.PH, measurement.ph))
        if measurement.ec_ds_m is not None:
            # For EC, lower is better (invert the score)
            ec_score = max(0, min(100, (4.0 - measurement.ec_ds_m) * 25))
            chemical_scores.append(ec_score)

        if chemical_scores:
            component_scores["chemical"] = statistics.mean(chemical_scores)
        else:
            component_scores["chemical"] = 50.0

        # Calculate weighted overall score
        overall_score = (
            component_scores["organic_matter"] * self.config.weight_organic_matter
            + component_scores["nutrients"] * self.config.weight_nutrients
            + component_scores["physical"] * self.config.weight_physical
            + component_scores["biological"] * self.config.weight_biological
            + component_scores["chemical"] * self.config.weight_chemical_balance
        )

        return overall_score, component_scores

    def _calculate_component_score(
        self,
        indicator: SoilHealthIndicator,
        value: float,
    ) -> float:
        """Calculate score (0-100) for a single component"""
        ranges = OPTIMAL_RANGES.get(indicator, {})
        if not ranges:
            return 50.0

        optimal_min = ranges.get("optimal_min", 0)
        optimal_max = ranges.get("optimal_max", 100)
        low = ranges.get("low", optimal_min * 0.5)
        critical_low = ranges.get("critical_low", low * 0.5)
        high = ranges.get("high", optimal_max * 1.5)

        # Within optimal range
        if optimal_min <= value <= optimal_max:
            return 100.0

        # Below optimal
        if value < optimal_min:
            if value < critical_low:
                return 10.0
            elif value < low:
                # Scale between 10-50
                return 10 + 40 * (value - critical_low) / (low - critical_low)
            else:
                # Scale between 50-100
                return 50 + 50 * (value - low) / (optimal_min - low)

        # Above optimal
        if value > optimal_max:
            if value > high:
                return 50.0  # Too high is not as bad as too low for most nutrients
            else:
                # Scale between 100-50
                return 100 - 50 * (value - optimal_max) / (high - optimal_max)

        return 50.0

    def analyze_rotation_impact(
        self,
        field_id: str,
        crop_history: list[tuple[CropType, date, date]],  # (crop, planting_date, harvest_date)
    ) -> dict[str, Any]:
        """
        Analyze impact of crop rotation on soil health
        تحليل تأثير الدورة الزراعية على صحة التربة
        """
        analysis = {
            "field_id": field_id,
            "rotation_length": len(crop_history),
            "organic_matter_impact": 0.0,
            "nitrogen_balance": 0.0,
            "soil_structure_score": 0.0,
            "legume_frequency_percent": 0.0,
            "biodiversity_score": 0.0,
            "overall_impact_rating": "neutral",
            "overall_impact_rating_ar": "محايد",
            "recommendations": [],
            "recommendations_ar": [],
        }

        if not crop_history:
            return analysis

        # Calculate impacts
        total_om_change = 0.0
        total_n_change = 0.0
        structure_impacts = []
        legume_count = 0
        crop_families = set()

        for crop_type, _, _ in crop_history:
            impact = CROP_SOIL_IMPACT.get(crop_type, {})
            total_om_change += impact.get("organic_matter_change", 0)
            total_n_change += impact.get("nitrogen_change", 0)
            structure_impacts.append(impact.get("soil_structure_impact", 0.5))

            # Track legumes and families
            from .planner import CROP_DATABASE

            crop_info = CROP_DATABASE.get(crop_type)
            if crop_info:
                crop_families.add(crop_info.crop_family)
                if crop_info.is_nitrogen_fixer:
                    legume_count += 1

        analysis["organic_matter_impact"] = total_om_change
        analysis["nitrogen_balance"] = total_n_change
        analysis["soil_structure_score"] = statistics.mean(structure_impacts) * 100 if structure_impacts else 50
        analysis["legume_frequency_percent"] = (legume_count / len(crop_history) * 100) if crop_history else 0
        analysis["biodiversity_score"] = min(100, len(crop_families) * 20)  # More families = better

        # Overall rating
        impact_score = (
            (total_om_change * 100)  # OM change weighted heavily
            + (total_n_change * 0.5)  # N balance
            + analysis["soil_structure_score"] * 0.3
            + analysis["legume_frequency_percent"] * 0.5
            + analysis["biodiversity_score"] * 0.2
        )

        if impact_score > 30:
            analysis["overall_impact_rating"] = "highly_positive"
            analysis["overall_impact_rating_ar"] = "إيجابي للغاية"
        elif impact_score > 10:
            analysis["overall_impact_rating"] = "positive"
            analysis["overall_impact_rating_ar"] = "إيجابي"
        elif impact_score > -10:
            analysis["overall_impact_rating"] = "neutral"
            analysis["overall_impact_rating_ar"] = "محايد"
        elif impact_score > -30:
            analysis["overall_impact_rating"] = "negative"
            analysis["overall_impact_rating_ar"] = "سلبي"
        else:
            analysis["overall_impact_rating"] = "highly_negative"
            analysis["overall_impact_rating_ar"] = "سلبي للغاية"

        # Generate recommendations
        if total_om_change < 0:
            analysis["recommendations"].append("Add more organic matter through residue return or amendments")
            analysis["recommendations_ar"].append("إضافة المزيد من المادة العضوية من خلال إعادة المخلفات أو المصلحات")

        if analysis["legume_frequency_percent"] < 25:
            analysis["recommendations"].append("Increase legume frequency to improve nitrogen cycling")
            analysis["recommendations_ar"].append("زيادة تكرار البقوليات لتحسين دورة النيتروجين")

        if analysis["biodiversity_score"] < 60:
            analysis["recommendations"].append("Diversify crop families in rotation for better soil health")
            analysis["recommendations_ar"].append("تنويع عائلات المحاصيل في الدورة لصحة تربة أفضل")

        return analysis

    def generate_soil_health_report(
        self,
        field_id: str,
        tenant_id: str,
        field_name: str,
        field_name_ar: str,
        years: int = 3,
    ) -> SoilHealthReport:
        """
        Generate comprehensive soil health report
        توليد تقرير شامل عن صحة التربة
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=years * 365)

        measurements = self.get_measurements(field_id, start_date, end_date)

        report = SoilHealthReport(
            tenant_id=tenant_id,
            field_id=field_id,
            field_name=field_name,
            field_name_ar=field_name_ar,
            report_date=date.today(),
            reporting_period_years=years,
        )

        if not measurements:
            report.key_findings.append("No soil health measurements available for this period")
            report.key_findings_ar.append("لا تتوفر قياسات صحة التربة لهذه الفترة")
            report.recommendations.append("Schedule soil testing to establish baseline measurements")
            report.recommendations_ar.append("جدولة اختبار التربة لإنشاء قياسات أساسية")
            return report

        # Latest measurement
        report.latest_measurement = measurements[-1]

        # Calculate overall score
        if report.latest_measurement:
            overall_score, component_scores = self.calculate_soil_health_score(report.latest_measurement)
            report.overall_score = overall_score
            report.physical_health_score = component_scores.get("physical", 50)
            report.chemical_health_score = component_scores.get("chemical", 50)
            report.biological_health_score = component_scores.get("biological", 50)

            # Determine rating
            if overall_score >= 80:
                report.overall_rating = "excellent"
                report.overall_rating_ar = "ممتاز"
            elif overall_score >= 65:
                report.overall_rating = "good"
                report.overall_rating_ar = "جيد"
            elif overall_score >= 50:
                report.overall_rating = "fair"
                report.overall_rating_ar = "مقبول"
            elif overall_score >= 35:
                report.overall_rating = "poor"
                report.overall_rating_ar = "ضعيف"
            else:
                report.overall_rating = "critical"
                report.overall_rating_ar = "حرج"

        # Calculate trends for key indicators
        key_indicators = [
            SoilHealthIndicator.ORGANIC_MATTER,
            SoilHealthIndicator.NITROGEN,
            SoilHealthIndicator.PHOSPHORUS,
            SoilHealthIndicator.POTASSIUM,
            SoilHealthIndicator.PH,
            SoilHealthIndicator.EC,
        ]

        for indicator in key_indicators:
            trend = self.calculate_indicator_trend(field_id, indicator, years)
            if trend.measurement_count >= 2:
                report.trends.append(trend)

        # Generate key findings
        declining_indicators = []
        improving_indicators = []

        for trend in report.trends:
            if trend.trend_direction == TrendDirection.DECLINING.value:
                declining_indicators.append(trend.indicator.value)
            elif trend.trend_direction == TrendDirection.IMPROVING.value:
                improving_indicators.append(trend.indicator.value)

        if improving_indicators:
            report.key_findings.append(f"Improving indicators: {', '.join(improving_indicators)}")
            report.key_findings_ar.append(f"مؤشرات متحسنة: {', '.join(improving_indicators)}")

        if declining_indicators:
            report.key_findings.append(f"Declining indicators requiring attention: {', '.join(declining_indicators)}")
            report.key_findings_ar.append(f"مؤشرات متراجعة تتطلب انتباه: {', '.join(declining_indicators)}")

        # Identify improvement areas
        for trend in report.trends:
            if trend.status in ["critical", "deficient", "low"]:
                report.improvement_areas.append(f"{trend.indicator.value}: Currently {trend.status}")
                report.improvement_areas_ar.append(f"{trend.indicator.value}: حاليًا {trend.status_ar}")

        # Collect recommendations from all trends
        for trend in report.trends:
            report.recommendations.extend(trend.recommendations)
            report.recommendations_ar.extend(trend.recommendations_ar)

        # Remove duplicates
        report.recommendations = list(dict.fromkeys(report.recommendations))
        report.recommendations_ar = list(dict.fromkeys(report.recommendations_ar))

        return report

    def estimate_rotation_impact(
        self,
        field_id: str,
        planned_crops: list[CropType],
        current_organic_matter: float | None = None,
        current_nitrogen: float | None = None,
    ) -> dict[str, Any]:
        """
        Estimate future soil health impact of planned rotation
        تقدير تأثير صحة التربة المستقبلي للدورة المخططة
        """
        estimate = {
            "planned_crops": [c.value for c in planned_crops],
            "years": len(planned_crops) / 2,  # Assuming 2 crops per year
            "projected_organic_matter_change": 0.0,
            "projected_nitrogen_balance": 0.0,
            "projected_soil_health_trend": "stable",
            "projected_soil_health_trend_ar": "مستقر",
            "benefits_expected": [],
            "benefits_expected_ar": [],
            "risks_identified": [],
            "risks_identified_ar": [],
        }

        # Calculate cumulative impacts
        total_om_change = 0.0
        total_n_change = 0.0
        legume_count = 0

        for crop in planned_crops:
            impact = CROP_SOIL_IMPACT.get(crop, {})
            total_om_change += impact.get("organic_matter_change", 0)
            total_n_change += impact.get("nitrogen_change", 0)

            from .planner import CROP_DATABASE

            crop_info = CROP_DATABASE.get(crop)
            if crop_info and crop_info.is_nitrogen_fixer:
                legume_count += 1

        estimate["projected_organic_matter_change"] = total_om_change
        estimate["projected_nitrogen_balance"] = total_n_change

        # Determine projected trend
        if total_om_change > 0.1:
            estimate["projected_soil_health_trend"] = "improving"
            estimate["projected_soil_health_trend_ar"] = "متحسن"
        elif total_om_change < -0.1:
            estimate["projected_soil_health_trend"] = "declining"
            estimate["projected_soil_health_trend_ar"] = "متراجع"

        # Expected benefits
        if total_om_change > 0:
            estimate["benefits_expected"].append("Organic matter increase")
            estimate["benefits_expected_ar"].append("زيادة المادة العضوية")

        if total_n_change > 0:
            estimate["benefits_expected"].append("Net nitrogen contribution")
            estimate["benefits_expected_ar"].append("مساهمة صافية في النيتروجين")

        if legume_count >= len(planned_crops) * 0.25:
            estimate["benefits_expected"].append("Good legume frequency for soil biology")
            estimate["benefits_expected_ar"].append("تكرار جيد للبقوليات لحياة التربة")

        # Risks
        if total_om_change < -0.1:
            estimate["risks_identified"].append("Organic matter may decline")
            estimate["risks_identified_ar"].append("قد تتراجع المادة العضوية")

        if total_n_change < -100:
            estimate["risks_identified"].append("High nitrogen depletion expected")
            estimate["risks_identified_ar"].append("متوقع استنزاف نيتروجين عالي")

        if legume_count == 0:
            estimate["risks_identified"].append("No legumes in rotation - nitrogen depletion risk")
            estimate["risks_identified_ar"].append("لا توجد بقوليات في الدورة - خطر استنزاف النيتروجين")

        return estimate

    def get_recommended_test_schedule(
        self,
        field_id: str,
    ) -> list[dict[str, Any]]:
        """
        Get recommended soil testing schedule
        الحصول على جدول اختبارات التربة الموصى به
        """
        measurements = self.measurements.get(field_id, [])
        schedule = []

        today = date.today()

        # Basic tests every 6 months
        basic_tests = {
            "name": "Basic Soil Test",
            "name_ar": "اختبار التربة الأساسي",
            "parameters": ["pH", "EC", "N", "P", "K", "organic_matter"],
            "frequency_months": 6,
        }

        # Full panel annually
        full_panel = {
            "name": "Comprehensive Soil Analysis",
            "name_ar": "تحليل التربة الشامل",
            "parameters": [
                "pH",
                "EC",
                "N",
                "P",
                "K",
                "Ca",
                "Mg",
                "S",
                "Fe",
                "Zn",
                "Mn",
                "B",
                "organic_matter",
                "CEC",
                "bulk_density",
                "microbial_biomass",
            ],
            "frequency_months": 12,
        }

        # Determine next test dates
        if measurements:
            last_test = measurements[-1].measurement_date
            next_basic = last_test + timedelta(days=self.config.recommended_test_frequency_months * 30)
            next_full = last_test + timedelta(days=365)
        else:
            next_basic = today
            next_full = today

        if next_basic < today:
            next_basic = today

        if next_full < today:
            next_full = today

        schedule.append(
            {
                **basic_tests,
                "next_date": next_basic.isoformat(),
                "priority": "high" if next_basic == today else "normal",
            }
        )

        schedule.append(
            {
                **full_panel,
                "next_date": next_full.isoformat(),
                "priority": "high" if next_full == today else "normal",
            }
        )

        return schedule


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


def assess_soil_health_from_measurement(
    measurement: SoilHealthMeasurement,
) -> tuple[str, str, float]:
    """
    Quick assessment of soil health from a single measurement
    تقييم سريع لصحة التربة من قياس واحد

    Returns (rating, rating_ar, score)
    """
    tracker = SoilHealthTracker()
    score, _ = tracker.calculate_soil_health_score(measurement)

    if score >= 80:
        return "excellent", "ممتاز", score
    elif score >= 65:
        return "good", "جيد", score
    elif score >= 50:
        return "fair", "مقبول", score
    elif score >= 35:
        return "poor", "ضعيف", score
    else:
        return "critical", "حرج", score


def calculate_nitrogen_credit(
    crop: CropType,
    yield_tons_ha: float | None = None,
) -> float:
    """
    Calculate nitrogen credit from a crop (kg N/ha available for next crop)
    حساب رصيد النيتروجين من محصول (كجم ن/هكتار متاح للمحصول التالي)
    """
    from .planner import CROP_DATABASE

    crop_info = CROP_DATABASE.get(crop)
    if not crop_info:
        return 0.0

    # Base credit from residue
    base_credit = crop_info.residue_nitrogen_kg_ha

    # Adjust for yield if provided
    if yield_tons_ha and crop_info.is_nitrogen_fixer:
        # Higher yield = more N fixed
        yield_factor = min(1.5, yield_tons_ha / 10)  # Normalize
        base_credit *= yield_factor

    # Only about 50% is available for next crop
    available_credit = base_credit * 0.5

    return available_credit


def get_organic_matter_trend_summary(
    measurements: list[SoilHealthMeasurement],
) -> dict[str, Any]:
    """
    Get summary of organic matter trend from measurements
    الحصول على ملخص اتجاه المادة العضوية من القياسات
    """
    if len(measurements) < 2:
        return {
            "status": "insufficient_data",
            "status_ar": "بيانات غير كافية",
            "trend": "unknown",
            "change_percent": 0.0,
        }

    # Get organic matter values
    om_values = [
        (m.measurement_date, m.organic_matter_percent) for m in measurements if m.organic_matter_percent is not None
    ]

    if len(om_values) < 2:
        return {
            "status": "insufficient_data",
            "status_ar": "بيانات غير كافية",
            "trend": "unknown",
            "change_percent": 0.0,
        }

    om_values.sort(key=lambda x: x[0])

    initial = om_values[0][1]
    current = om_values[-1][1]
    change = ((current - initial) / initial * 100) if initial > 0 else 0

    if change > 5:
        trend = "improving"
        trend_ar = "متحسن"
    elif change < -5:
        trend = "declining"
        trend_ar = "متراجع"
    else:
        trend = "stable"
        trend_ar = "مستقر"

    return {
        "status": "analyzed",
        "status_ar": "تم التحليل",
        "trend": trend,
        "trend_ar": trend_ar,
        "initial_value": initial,
        "current_value": current,
        "change_percent": round(change, 2),
        "measurement_count": len(om_values),
    }
