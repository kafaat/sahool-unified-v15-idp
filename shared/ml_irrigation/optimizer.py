"""
Irrigation Water Optimizer
==========================
محسّن مياه الري

Water usage optimization and anomaly detection including:
- Water savings recommendations
- Schedule optimization
- Anomaly detection for irrigation systems
- Historical pattern analysis
- Cost-benefit analysis

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .models import (
    AnomalySeverity,
    AnomalyType,
    HistoricalPattern,
    IrrigationAnomaly,
    IrrigationFeatures,
    IrrigationRecord,
    WaterOptimizationResult,
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizerConfig:
    """
    Configuration for water optimizer
    إعدادات محسّن المياه
    """

    # Anomaly detection thresholds
    consumption_deviation_threshold: float = 0.30  # 30% deviation triggers anomaly
    pressure_drop_threshold: float = 0.15  # 15% pressure drop
    flow_variance_threshold: float = 0.25  # 25% flow variance

    # Optimization parameters
    target_efficiency: float = 0.85  # Target irrigation efficiency
    min_irrigation_interval_hours: float = 12  # Minimum hours between irrigations
    max_irrigation_interval_days: float = 7  # Maximum days between irrigations

    # Cost parameters
    water_cost_per_m3: float = 2.50  # Default water cost (SAR/m3)
    energy_cost_per_kwh: float = 0.18  # Default energy cost (SAR/kWh)

    # Schedule optimization
    preferred_start_hour: int = 5  # Preferred start time (5 AM)
    preferred_end_hour: int = 8  # Preferred end time (8 AM)
    avoid_peak_hours: bool = True  # Avoid peak electricity hours

    # Pattern analysis
    pattern_analysis_min_records: int = 10  # Minimum records for pattern analysis
    seasonal_adjustment: bool = True  # Apply seasonal adjustments


# Optimal irrigation timing by irrigation type and season
OPTIMAL_TIMING = {
    "drip": {
        "summer": {"start": 5, "end": 7},
        "winter": {"start": 7, "end": 10},
        "spring": {"start": 6, "end": 9},
        "fall": {"start": 6, "end": 9},
    },
    "sprinkler": {
        "summer": {"start": 4, "end": 6},
        "winter": {"start": 8, "end": 11},
        "spring": {"start": 5, "end": 8},
        "fall": {"start": 5, "end": 8},
    },
    "flood": {
        "summer": {"start": 18, "end": 21},
        "winter": {"start": 9, "end": 12},
        "spring": {"start": 17, "end": 20},
        "fall": {"start": 17, "end": 20},
    },
}

# Bilingual anomaly descriptions
ANOMALY_DESCRIPTIONS = {
    AnomalyType.LEAK: {
        "en": "Potential water leak detected in irrigation system",
        "ar": "تم اكتشاف تسرب محتمل في نظام الري",
    },
    AnomalyType.BLOCKAGE: {
        "en": "Possible blockage or clogging in irrigation lines",
        "ar": "انسداد محتمل في خطوط الري",
    },
    AnomalyType.PRESSURE_DROP: {
        "en": "Abnormal pressure drop detected in irrigation system",
        "ar": "انخفاض غير طبيعي في ضغط نظام الري",
    },
    AnomalyType.OVERCONSUMPTION: {
        "en": "Water consumption significantly higher than expected",
        "ar": "استهلاك المياه أعلى بكثير من المتوقع",
    },
    AnomalyType.UNDERCONSUMPTION: {
        "en": "Water consumption significantly lower than expected",
        "ar": "استهلاك المياه أقل بكثير من المتوقع",
    },
    AnomalyType.SENSOR_MALFUNCTION: {
        "en": "Irrigation sensor may be malfunctioning",
        "ar": "قد يكون حساس الري معطلاً",
    },
    AnomalyType.SCHEDULING_ERROR: {
        "en": "Irrigation scheduling deviation detected",
        "ar": "تم اكتشاف انحراف في جدولة الري",
    },
    AnomalyType.PUMP_FAILURE: {
        "en": "Potential pump failure or malfunction",
        "ar": "احتمال عطل أو خلل في المضخة",
    },
}

# Bilingual recommendations for anomalies
ANOMALY_RECOMMENDATIONS = {
    AnomalyType.LEAK: {
        "en": "Inspect all irrigation lines and connections. Check for wet spots or unusual water pooling.",
        "ar": "افحص جميع خطوط الري والوصلات. ابحث عن البقع الرطبة أو تجمعات المياه غير العادية.",
    },
    AnomalyType.BLOCKAGE: {
        "en": "Check filters, emitters, and sprinkler heads. Flush irrigation lines if necessary.",
        "ar": "افحص الفلاتر والنقاطات ورؤوس الرشاشات. اغسل خطوط الري إذا لزم الأمر.",
    },
    AnomalyType.PRESSURE_DROP: {
        "en": "Check pump performance, filter condition, and mainline for leaks.",
        "ar": "افحص أداء المضخة وحالة الفلتر والخط الرئيسي للتسربات.",
    },
    AnomalyType.OVERCONSUMPTION: {
        "en": "Review irrigation schedule and check for system leaks or stuck valves.",
        "ar": "راجع جدول الري وتحقق من تسربات النظام أو الصمامات العالقة.",
    },
    AnomalyType.UNDERCONSUMPTION: {
        "en": "Check for clogged emitters, closed valves, or pump issues.",
        "ar": "تحقق من النقاطات المسدودة أو الصمامات المغلقة أو مشاكل المضخة.",
    },
    AnomalyType.SENSOR_MALFUNCTION: {
        "en": "Calibrate or replace the malfunctioning sensor. Verify sensor connections.",
        "ar": "معايرة أو استبدال الحساس المعطل. تحقق من توصيلات الحساس.",
    },
    AnomalyType.SCHEDULING_ERROR: {
        "en": "Review and correct the irrigation schedule. Check controller settings.",
        "ar": "راجع وصحح جدول الري. تحقق من إعدادات المتحكم.",
    },
    AnomalyType.PUMP_FAILURE: {
        "en": "Inspect pump motor, impeller, and electrical connections. Schedule maintenance.",
        "ar": "افحص محرك المضخة والريشة والتوصيلات الكهربائية. جدول الصيانة.",
    },
}


class WaterOptimizer:
    """
    Water usage optimization engine
    محرك تحسين استخدام المياه

    Analyzes irrigation patterns, detects anomalies,
    and provides water saving recommendations.

    Features:
    - Water usage optimization
    - Anomaly detection
    - Historical pattern analysis
    - Cost-benefit analysis
    - Bilingual output (Arabic/English)

    Usage:
        optimizer = WaterOptimizer()

        # Optimize water usage
        result = optimizer.optimize(
            records=irrigation_records,
            features=current_features,
            area_ha=10.5,
        )

        print(f"Potential savings: {result.savings_percent:.1f}%")

        # Detect anomalies
        anomalies = optimizer.detect_anomalies(
            records=irrigation_records,
            current_reading=flow_reading,
        )

        for anomaly in anomalies:
            print(f"{anomaly.anomaly_type.value}: {anomaly.description}")
    """

    def __init__(self, config: OptimizerConfig | None = None):
        """
        Initialize the water optimizer

        Args:
            config: Optimizer configuration
        """
        self.config = config or OptimizerConfig()

    def optimize(
        self,
        records: list[IrrigationRecord],
        features: IrrigationFeatures | None = None,
        area_ha: float | None = None,
        forecast_days: int = 7,
    ) -> WaterOptimizationResult:
        """
        Optimize water usage based on historical records
        تحسين استخدام المياه بناءً على السجلات التاريخية

        Args:
            records: Historical irrigation records
            features: Current field features (optional)
            area_ha: Field area in hectares
            forecast_days: Number of days to optimize for

        Returns:
            WaterOptimizationResult with savings and schedule
        """
        if not records:
            return WaterOptimizationResult(
                current_usage_mm=0,
                optimized_usage_mm=0,
                savings_mm=0,
                savings_percent=0,
            )

        # Calculate current water usage
        recent_records = self._get_recent_records(records, days=30)
        current_usage_mm = sum(r.amount_mm for r in recent_records)

        # Calculate daily average
        total_days = max(
            1,
            (
                (recent_records[-1].irrigation_date - recent_records[0].irrigation_date).days
                if len(recent_records) > 1
                else 1
            ),
        )
        daily_avg_mm = current_usage_mm / total_days

        # Calculate optimal water requirement
        optimal_daily_mm = self._calculate_optimal_requirement(
            records,
            features,
            forecast_days,
        )

        # Calculate optimized usage
        optimized_usage_mm = optimal_daily_mm * forecast_days

        # Calculate equivalent values for the same period
        current_for_period = daily_avg_mm * forecast_days
        savings_mm = max(0, current_for_period - optimized_usage_mm)
        savings_percent = (savings_mm / current_for_period * 100) if current_for_period > 0 else 0

        # Calculate volumes if area known
        current_volume_m3 = None
        optimized_volume_m3 = None
        savings_volume_m3 = None
        if area_ha:
            current_volume_m3 = current_for_period * area_ha * 10  # mm to m3/ha
            optimized_volume_m3 = optimized_usage_mm * area_ha * 10
            savings_volume_m3 = savings_mm * area_ha * 10

        # Calculate costs
        water_cost = self.config.water_cost_per_m3
        current_cost = current_volume_m3 * water_cost if current_volume_m3 else None
        optimized_cost = optimized_volume_m3 * water_cost if optimized_volume_m3 else None
        cost_savings = (current_cost - optimized_cost) if current_cost and optimized_cost else None

        # Generate optimized schedule
        schedule = self._generate_optimized_schedule(
            optimal_daily_mm,
            features,
            forecast_days,
        )

        # Generate recommendations
        recommendations, recommendations_ar = self._generate_optimization_recommendations(
            current_for_period,
            optimized_usage_mm,
            savings_percent,
            records,
            features,
        )

        return WaterOptimizationResult(
            field_id=features.field_id if features else "",
            current_usage_mm=round(current_for_period, 1),
            optimized_usage_mm=round(optimized_usage_mm, 1),
            savings_mm=round(savings_mm, 1),
            savings_percent=round(savings_percent, 1),
            current_volume_m3=round(current_volume_m3, 1) if current_volume_m3 else None,
            optimized_volume_m3=round(optimized_volume_m3, 1) if optimized_volume_m3 else None,
            savings_volume_m3=round(savings_volume_m3, 1) if savings_volume_m3 else None,
            water_cost_per_m3=water_cost,
            current_cost=round(current_cost, 2) if current_cost else None,
            optimized_cost=round(optimized_cost, 2) if optimized_cost else None,
            cost_savings=round(cost_savings, 2) if cost_savings else None,
            optimized_schedule=schedule,
            recommendations=recommendations,
            recommendations_ar=recommendations_ar,
            analysis_period_days=forecast_days,
        )

    def detect_anomalies(
        self,
        records: list[IrrigationRecord],
        current_reading: float | None = None,
        expected_value: float | None = None,
        field_id: str = "",
    ) -> list[IrrigationAnomaly]:
        """
        Detect anomalies in irrigation system
        اكتشاف الشذوذ في نظام الري

        Args:
            records: Historical irrigation records
            current_reading: Current sensor reading (optional)
            expected_value: Expected value for comparison
            field_id: Field identifier

        Returns:
            List of detected anomalies
        """
        anomalies = []

        if not records or len(records) < 5:
            return anomalies

        # Calculate statistics from historical data
        amounts = [r.amount_mm for r in records]
        mean_amount = statistics.mean(amounts)
        statistics.stdev(amounts) if len(amounts) > 1 else 0

        # Detect consumption anomalies
        if current_reading is not None and mean_amount > 0:
            deviation = abs(current_reading - mean_amount) / mean_amount

            if deviation > self.config.consumption_deviation_threshold:
                if current_reading > mean_amount:
                    anomaly_type = AnomalyType.OVERCONSUMPTION
                    severity = AnomalySeverity.HIGH if deviation > 0.5 else AnomalySeverity.MEDIUM
                else:
                    anomaly_type = AnomalyType.UNDERCONSUMPTION
                    severity = AnomalySeverity.MEDIUM if deviation > 0.5 else AnomalySeverity.LOW

                anomaly = self._create_anomaly(
                    anomaly_type=anomaly_type,
                    severity=severity,
                    detected_value=current_reading,
                    expected_value=mean_amount,
                    deviation_percent=deviation * 100,
                    field_id=field_id,
                    detection_method="statistical_deviation",
                )
                anomalies.append(anomaly)

        # Detect scheduling anomalies (irregular intervals)
        intervals = self._calculate_intervals(records)
        if intervals:
            mean_interval = statistics.mean(intervals)
            interval_std = statistics.stdev(intervals) if len(intervals) > 1 else 0

            # Check for too frequent irrigations
            if mean_interval < self.config.min_irrigation_interval_hours:
                anomaly = self._create_anomaly(
                    anomaly_type=AnomalyType.SCHEDULING_ERROR,
                    severity=AnomalySeverity.MEDIUM,
                    detected_value=mean_interval,
                    expected_value=self.config.min_irrigation_interval_hours,
                    deviation_percent=(
                        (self.config.min_irrigation_interval_hours - mean_interval)
                        / self.config.min_irrigation_interval_hours
                        * 100
                    ),
                    field_id=field_id,
                    detection_method="interval_analysis",
                )
                anomaly.impact_description = "Too frequent irrigation may cause waterlogging"
                anomaly.impact_description_ar = "الري المتكرر جداً قد يسبب تشبع التربة بالماء"
                anomalies.append(anomaly)

            # Check for highly irregular intervals
            if interval_std > mean_interval * 0.5:
                anomaly = self._create_anomaly(
                    anomaly_type=AnomalyType.SCHEDULING_ERROR,
                    severity=AnomalySeverity.LOW,
                    detected_value=interval_std,
                    expected_value=mean_interval * 0.25,
                    deviation_percent=(interval_std / mean_interval * 100),
                    field_id=field_id,
                    detection_method="interval_variance",
                )
                anomaly.description = "Irrigation intervals are highly irregular"
                anomaly.description_ar = "فترات الري غير منتظمة بشكل كبير"
                anomalies.append(anomaly)

        # Detect potential sensor malfunction (stuck values)
        if len(records) >= 5:
            recent_amounts = [r.amount_mm for r in records[-5:]]
            if len(set(recent_amounts)) == 1:
                anomaly = self._create_anomaly(
                    anomaly_type=AnomalyType.SENSOR_MALFUNCTION,
                    severity=AnomalySeverity.MEDIUM,
                    detected_value=recent_amounts[0],
                    expected_value=mean_amount,
                    deviation_percent=0,
                    field_id=field_id,
                    detection_method="stuck_value_detection",
                )
                anomaly.description = "Sensor readings unchanged for 5 consecutive irrigations"
                anomaly.description_ar = "قراءات الحساس لم تتغير لـ 5 ريات متتالية"
                anomalies.append(anomaly)

        return anomalies

    def analyze_patterns(
        self,
        records: list[IrrigationRecord],
        field_id: str = "",
    ) -> HistoricalPattern:
        """
        Analyze historical irrigation patterns
        تحليل أنماط الري التاريخية

        Args:
            records: Historical irrigation records
            field_id: Field identifier

        Returns:
            HistoricalPattern with insights
        """
        if not records:
            return HistoricalPattern(
                field_id=field_id,
                start_date=datetime.now(UTC),
                end_date=datetime.now(UTC),
                total_days=0,
                total_irrigations=0,
                total_water_mm=0,
                average_amount_mm=0,
                average_interval_days=0,
                calculated_efficiency=0,
            )

        # Sort records by date
        sorted_records = sorted(records, key=lambda r: r.irrigation_date)

        # Basic statistics
        start_date = sorted_records[0].irrigation_date
        end_date = sorted_records[-1].irrigation_date
        total_days = max(1, (end_date - start_date).days)

        total_irrigations = len(records)
        total_water_mm = sum(r.amount_mm for r in records)
        average_amount_mm = total_water_mm / total_irrigations if total_irrigations > 0 else 0

        # Calculate average interval
        intervals = self._calculate_intervals(sorted_records)
        average_interval_days = statistics.mean(intervals) / 24 if intervals else 0

        # Calculate efficiency from effectiveness ratings
        effectiveness_ratings = [r.effectiveness_rating for r in records if r.effectiveness_rating]
        calculated_efficiency = statistics.mean(effectiveness_ratings) / 5.0 if effectiveness_ratings else 0.75

        # Analyze temporal patterns
        most_common_day, most_common_hour = self._analyze_temporal_patterns(sorted_records)

        # Identify patterns
        patterns, patterns_ar = self._identify_patterns(sorted_records, intervals)

        # Generate insights
        insights, insights_ar = self._generate_insights(
            total_water_mm,
            average_amount_mm,
            average_interval_days,
            calculated_efficiency,
            patterns,
        )

        # Generate recommendations
        recommendations, recommendations_ar = self._generate_pattern_recommendations(
            average_amount_mm,
            average_interval_days,
            calculated_efficiency,
            most_common_hour,
        )

        return HistoricalPattern(
            field_id=field_id,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_irrigations=total_irrigations,
            total_water_mm=round(total_water_mm, 1),
            average_amount_mm=round(average_amount_mm, 1),
            average_interval_days=round(average_interval_days, 1),
            calculated_efficiency=round(calculated_efficiency, 2),
            most_common_day=most_common_day,
            most_common_hour=most_common_hour,
            patterns_identified=patterns,
            patterns_identified_ar=patterns_ar,
            insights=insights,
            insights_ar=insights_ar,
            recommendations=recommendations,
            recommendations_ar=recommendations_ar,
        )

    def _get_recent_records(
        self,
        records: list[IrrigationRecord],
        days: int = 30,
    ) -> list[IrrigationRecord]:
        """Get records from recent period"""
        cutoff = datetime.now(UTC) - timedelta(days=days)
        recent = [r for r in records if r.irrigation_date >= cutoff]
        return sorted(recent, key=lambda r: r.irrigation_date)

    def _calculate_optimal_requirement(
        self,
        records: list[IrrigationRecord],
        features: IrrigationFeatures | None,
        forecast_days: int,
    ) -> float:
        """Calculate optimal daily water requirement"""
        # Base calculation from ET if features available
        if features:
            # ETc = ET0 * Kc
            kc = features.crop.kc if hasattr(features.crop, "kc") else 1.0
            etc = features.weather.et0 * kc

            # Account for efficiency
            efficiency = features.system_efficiency
            optimal_daily = etc / efficiency if efficiency > 0 else etc

            # Adjust for soil type (sandy needs more frequent, less amount)
            if hasattr(features.soil, "soil_type"):
                from .models import SoilType

                if features.soil.soil_type == SoilType.SANDY:
                    optimal_daily *= 0.9  # Smaller amounts more frequently
                elif features.soil.soil_type == SoilType.CLAY:
                    optimal_daily *= 1.1  # Larger amounts less frequently

            return optimal_daily

        # Fallback: Calculate from historical data
        if records:
            recent = self._get_recent_records(records, days=30)
            if recent:
                total_mm = sum(r.amount_mm for r in recent)
                total_days = max(1, (recent[-1].irrigation_date - recent[0].irrigation_date).days)
                historical_daily = total_mm / total_days

                # Apply target efficiency factor
                current_efficiency = self._estimate_current_efficiency(recent)
                if current_efficiency < self.config.target_efficiency:
                    # Current irrigation is inefficient, reduce to target
                    return historical_daily * (current_efficiency / self.config.target_efficiency)

                return historical_daily

        # Default fallback
        return 5.0  # 5mm/day as default

    def _estimate_current_efficiency(
        self,
        records: list[IrrigationRecord],
    ) -> float:
        """Estimate current irrigation efficiency from records"""
        ratings = [r.effectiveness_rating for r in records if r.effectiveness_rating]
        if ratings:
            avg_rating = statistics.mean(ratings)
            return min(0.95, avg_rating / 5.0)
        return 0.75  # Default assumption

    def _generate_optimized_schedule(
        self,
        optimal_daily_mm: float,
        features: IrrigationFeatures | None,
        forecast_days: int,
    ) -> list[dict[str, Any]]:
        """Generate optimized irrigation schedule"""
        schedule = []
        current_date = datetime.now(UTC)

        # Determine irrigation type and get optimal timing
        irr_type = features.irrigation_type.value if features else "drip"
        season = self._get_season(current_date)
        timing = OPTIMAL_TIMING.get(irr_type, OPTIMAL_TIMING["drip"]).get(season, {"start": 6, "end": 8})

        # Calculate irrigation frequency based on amount
        # Typical single application: 15-25mm
        single_application = min(25, max(15, optimal_daily_mm * 2))
        interval_days = single_application / optimal_daily_mm if optimal_daily_mm > 0 else 2

        # Generate schedule
        next_irrigation = current_date
        while next_irrigation < current_date + timedelta(days=forecast_days):
            irrigation_datetime = next_irrigation.replace(
                hour=timing["start"],
                minute=0,
                second=0,
            )

            schedule.append(
                {
                    "date": irrigation_datetime.date().isoformat(),
                    "time": f"{timing['start']:02d}:00",
                    "amount_mm": round(single_application, 1),
                    "duration_minutes": self._estimate_duration(single_application, irr_type),
                    "notes": f"Optimal timing for {season}",
                    "notes_ar": f"التوقيت الأمثل لموسم {self._get_season_ar(season)}",
                }
            )

            next_irrigation += timedelta(days=interval_days)

        return schedule

    def _get_season(self, date: datetime) -> str:
        """Determine season from date"""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    def _get_season_ar(self, season: str) -> str:
        """Get Arabic season name"""
        seasons_ar = {
            "winter": "الشتاء",
            "spring": "الربيع",
            "summer": "الصيف",
            "fall": "الخريف",
        }
        return seasons_ar.get(season, season)

    def _estimate_duration(self, amount_mm: float, irr_type: str) -> int:
        """Estimate irrigation duration in minutes"""
        # Approximate flow rates (mm/hour)
        flow_rates = {
            "drip": 4.0,
            "sprinkler": 10.0,
            "flood": 25.0,
            "center_pivot": 8.0,
            "furrow": 15.0,
            "subsurface": 3.0,
        }
        flow_rate = flow_rates.get(irr_type, 6.0)
        duration_hours = amount_mm / flow_rate
        return int(duration_hours * 60)

    def _generate_optimization_recommendations(
        self,
        current_usage: float,
        optimized_usage: float,
        savings_percent: float,
        records: list[IrrigationRecord],
        features: IrrigationFeatures | None,
    ) -> tuple[list[str], list[str]]:
        """Generate optimization recommendations"""
        recommendations = []
        recommendations_ar = []

        # Savings recommendation
        if savings_percent >= 10:
            recommendations.append(
                f"Potential water savings of {savings_percent:.0f}% identified. "
                "Implement the optimized schedule to reduce water usage."
            )
            recommendations_ar.append(
                f"تم تحديد توفير محتمل للمياه بنسبة {savings_percent:.0f}%. نفذ الجدول المحسّن لتقليل استخدام المياه."
            )

        # Timing recommendation
        if features:
            optimal_hour = (
                OPTIMAL_TIMING.get(features.irrigation_type.value, OPTIMAL_TIMING["drip"])
                .get(self._get_season(datetime.now(UTC)), {})
                .get("start", 6)
            )

            recommendations.append(f"Schedule irrigation around {optimal_hour}:00 for minimum evaporation losses.")
            recommendations_ar.append(f"جدول الري حوالي الساعة {optimal_hour}:00 لتقليل خسائر التبخر.")

        # Frequency recommendation
        if records:
            intervals = self._calculate_intervals(records)
            if intervals:
                avg_interval = statistics.mean(intervals) / 24
                if avg_interval < 1:
                    recommendations.append("Consider less frequent, deeper irrigation to encourage root growth.")
                    recommendations_ar.append("فكر في ري أقل تكراراً وأعمق لتشجيع نمو الجذور.")

        # Efficiency recommendation
        if features and features.system_efficiency < 0.8:
            recommendations.append("System efficiency is below optimal. Consider maintenance or upgrade.")
            recommendations_ar.append("كفاءة النظام أقل من المستوى الأمثل. فكر في الصيانة أو الترقية.")

        # Soil moisture monitoring
        if features and features.soil.moisture_current > 60:
            recommendations.append(
                "Current soil moisture is adequate. Delay irrigation until moisture drops below 50%."
            )
            recommendations_ar.append("رطوبة التربة الحالية كافية. أخّر الري حتى تنخفض الرطوبة تحت 50%.")

        return recommendations, recommendations_ar

    def _calculate_intervals(
        self,
        records: list[IrrigationRecord],
    ) -> list[float]:
        """Calculate intervals between irrigations in hours"""
        if len(records) < 2:
            return []

        sorted_records = sorted(records, key=lambda r: r.irrigation_date)
        intervals = []

        for i in range(1, len(sorted_records)):
            delta = sorted_records[i].irrigation_date - sorted_records[i - 1].irrigation_date
            intervals.append(delta.total_seconds() / 3600)  # Convert to hours

        return intervals

    def _create_anomaly(
        self,
        anomaly_type: AnomalyType,
        severity: AnomalySeverity,
        detected_value: float,
        expected_value: float,
        deviation_percent: float,
        field_id: str,
        detection_method: str,
    ) -> IrrigationAnomaly:
        """Create an anomaly object"""
        descriptions = ANOMALY_DESCRIPTIONS.get(
            anomaly_type,
            {
                "en": "Unknown anomaly detected",
                "ar": "تم اكتشاف شذوذ غير معروف",
            },
        )
        recommendations = ANOMALY_RECOMMENDATIONS.get(
            anomaly_type,
            {
                "en": "Inspect irrigation system",
                "ar": "افحص نظام الري",
            },
        )

        return IrrigationAnomaly(
            field_id=field_id,
            anomaly_type=anomaly_type,
            severity=severity,
            detected_value=round(detected_value, 2),
            expected_value=round(expected_value, 2),
            deviation_percent=round(deviation_percent, 1),
            description=descriptions["en"],
            description_ar=descriptions["ar"],
            recommended_action=recommendations["en"],
            recommended_action_ar=recommendations["ar"],
            detection_method=detection_method,
        )

    def _analyze_temporal_patterns(
        self,
        records: list[IrrigationRecord],
    ) -> tuple[str | None, int | None]:
        """Analyze temporal patterns in irrigation"""
        if not records:
            return None, None

        # Day of week analysis
        day_counts: dict[str, int] = defaultdict(int)
        hour_counts: dict[int, int] = defaultdict(int)

        for record in records:
            day_name = record.irrigation_date.strftime("%A")
            hour = record.irrigation_date.hour
            day_counts[day_name] += 1
            hour_counts[hour] += 1

        most_common_day = max(day_counts, key=day_counts.get) if day_counts else None
        most_common_hour = max(hour_counts, key=hour_counts.get) if hour_counts else None

        return most_common_day, most_common_hour

    def _identify_patterns(
        self,
        records: list[IrrigationRecord],
        intervals: list[float],
    ) -> tuple[list[str], list[str]]:
        """Identify patterns in historical data"""
        patterns = []
        patterns_ar = []

        if not records:
            return patterns, patterns_ar

        # Regular interval pattern
        if intervals and len(intervals) >= 3:
            interval_std = statistics.stdev(intervals)
            interval_mean = statistics.mean(intervals)
            if interval_std < interval_mean * 0.2:
                patterns.append(f"Regular irrigation pattern with ~{interval_mean / 24:.1f} day interval")
                patterns_ar.append(f"نمط ري منتظم بفترة ~{interval_mean / 24:.1f} يوم")

        # Morning vs evening pattern
        morning_count = sum(1 for r in records if r.irrigation_date.hour < 12)
        evening_count = len(records) - morning_count

        if morning_count > evening_count * 2:
            patterns.append("Predominantly morning irrigation")
            patterns_ar.append("ري صباحي في الغالب")
        elif evening_count > morning_count * 2:
            patterns.append("Predominantly evening irrigation")
            patterns_ar.append("ري مسائي في الغالب")

        # Increasing/decreasing trend
        if len(records) >= 10:
            amounts = [r.amount_mm for r in records]
            first_half = statistics.mean(amounts[: len(amounts) // 2])
            second_half = statistics.mean(amounts[len(amounts) // 2 :])

            if second_half > first_half * 1.2:
                patterns.append("Increasing irrigation amounts over time")
                patterns_ar.append("زيادة كميات الري مع مرور الوقت")
            elif second_half < first_half * 0.8:
                patterns.append("Decreasing irrigation amounts over time")
                patterns_ar.append("تناقص كميات الري مع مرور الوقت")

        return patterns, patterns_ar

    def _generate_insights(
        self,
        total_water_mm: float,
        average_amount_mm: float,
        average_interval_days: float,
        efficiency: float,
        patterns: list[str],
    ) -> tuple[list[str], list[str]]:
        """Generate insights from pattern analysis"""
        insights = []
        insights_ar = []

        # Efficiency insight
        if efficiency >= 0.85:
            insights.append(f"Good irrigation efficiency ({efficiency * 100:.0f}%)")
            insights_ar.append(f"كفاءة ري جيدة ({efficiency * 100:.0f}%)")
        elif efficiency >= 0.70:
            insights.append(f"Moderate irrigation efficiency ({efficiency * 100:.0f}%), room for improvement")
            insights_ar.append(f"كفاءة ري متوسطة ({efficiency * 100:.0f}%)، مجال للتحسين")
        else:
            insights.append(f"Low irrigation efficiency ({efficiency * 100:.0f}%), significant improvement needed")
            insights_ar.append(f"كفاءة ري منخفضة ({efficiency * 100:.0f}%)، تحسين كبير مطلوب")

        # Interval insight
        if average_interval_days < 1:
            insights.append("Very frequent irrigation may cause waterlogging")
            insights_ar.append("الري المتكرر جداً قد يسبب تشبع التربة")
        elif average_interval_days > 5:
            insights.append("Infrequent irrigation may cause water stress")
            insights_ar.append("قلة الري قد تسبب إجهاد مائي")

        # Amount insight
        if average_amount_mm > 40:
            insights.append("Large irrigation amounts - consider splitting into smaller applications")
            insights_ar.append("كميات ري كبيرة - فكر في تقسيمها إلى تطبيقات أصغر")
        elif average_amount_mm < 10:
            insights.append("Small irrigation amounts - consider deeper, less frequent irrigation")
            insights_ar.append("كميات ري صغيرة - فكر في ري أعمق وأقل تكراراً")

        return insights, insights_ar

    def _generate_pattern_recommendations(
        self,
        average_amount_mm: float,
        average_interval_days: float,
        efficiency: float,
        most_common_hour: int | None,
    ) -> tuple[list[str], list[str]]:
        """Generate recommendations from pattern analysis"""
        recommendations = []
        recommendations_ar = []

        # Timing recommendation
        if most_common_hour is not None:
            optimal_hours = [5, 6, 7]
            if most_common_hour not in optimal_hours:
                recommendations.append(
                    f"Current irrigation typically at {most_common_hour}:00. "
                    "Consider shifting to 5:00-7:00 for lower evaporation."
                )
                recommendations_ar.append(
                    f"الري الحالي عادة في الساعة {most_common_hour}:00. فكر في التحويل إلى 5:00-7:00 لتبخر أقل."
                )

        # Efficiency recommendation
        if efficiency < 0.80:
            recommendations.append(
                "Check system for leaks, clogged emitters, or pressure issues to improve efficiency."
            )
            recommendations_ar.append(
                "افحص النظام بحثاً عن التسربات أو النقاطات المسدودة أو مشاكل الضغط لتحسين الكفاءة."
            )

        # Interval recommendation
        optimal_interval = 2.5  # Typical optimal interval in days
        if average_interval_days < optimal_interval * 0.5:
            recommendations.append("Consider reducing irrigation frequency with larger amounts per application.")
            recommendations_ar.append("فكر في تقليل تكرار الري مع كميات أكبر لكل تطبيق.")
        elif average_interval_days > optimal_interval * 2:
            recommendations.append(
                "Consider more frequent irrigation with smaller amounts to maintain consistent moisture."
            )
            recommendations_ar.append("فكر في ري أكثر تكراراً بكميات أصغر للحفاظ على رطوبة متسقة.")

        return recommendations, recommendations_ar


# Convenience functions
_default_optimizer: WaterOptimizer | None = None


def get_optimizer(config: OptimizerConfig | None = None) -> WaterOptimizer:
    """Get or create the default optimizer instance"""
    global _default_optimizer
    if _default_optimizer is None or config is not None:
        _default_optimizer = WaterOptimizer(config=config)
    return _default_optimizer


def optimize_water_usage(
    records: list[IrrigationRecord],
    features: IrrigationFeatures | None = None,
    area_ha: float | None = None,
) -> WaterOptimizationResult:
    """
    Convenience function for water optimization
    دالة مساعدة لتحسين استخدام المياه

    Args:
        records: Historical irrigation records
        features: Current field features
        area_ha: Field area in hectares

    Returns:
        WaterOptimizationResult with recommendations
    """
    optimizer = get_optimizer()
    return optimizer.optimize(records, features, area_ha)


def detect_irrigation_anomalies(
    records: list[IrrigationRecord],
    current_reading: float | None = None,
    field_id: str = "",
) -> list[IrrigationAnomaly]:
    """
    Convenience function for anomaly detection
    دالة مساعدة لاكتشاف الشذوذ

    Args:
        records: Historical irrigation records
        current_reading: Current sensor reading
        field_id: Field identifier

    Returns:
        List of detected anomalies
    """
    optimizer = get_optimizer()
    return optimizer.detect_anomalies(records, current_reading, field_id=field_id)


def analyze_irrigation_patterns(
    records: list[IrrigationRecord],
    field_id: str = "",
) -> HistoricalPattern:
    """
    Convenience function for pattern analysis
    دالة مساعدة لتحليل الأنماط

    Args:
        records: Historical irrigation records
        field_id: Field identifier

    Returns:
        HistoricalPattern with insights
    """
    optimizer = get_optimizer()
    return optimizer.analyze_patterns(records, field_id)
