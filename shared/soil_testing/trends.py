"""
Soil Test Trend Analysis - تحليل اتجاهات تحليل التربة

Analyzes historical soil test data to identify trends, patterns,
and long-term soil health changes.

Features:
- Multi-year trend detection
- Seasonal pattern analysis
- Soil health scoring over time
- Management practice correlation
- Bilingual reporting

Author: SAHOOL Platform Team
Version: 1.0.0
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .interpreter import NUTRIENT_THRESHOLDS, SoilTestInterpreter
from .models import (
    NutrientStatus,
    NutrientTrend,
    SoilTestResult,
    TrendDataPoint,
    TrendReport,
)


@dataclass
class TrendAnalysisConfig:
    """Configuration for trend analysis - إعدادات تحليل الاتجاهات"""

    # Minimum data points for trend analysis
    min_data_points: int = 3

    # Trend significance thresholds
    significant_change_percent: float = 10.0
    slope_threshold: float = 0.5  # units/year

    # Analysis period
    default_years: int = 5

    # Language
    language: str = "both"


class SoilTrendAnalyzer:
    """
    Analyzer for historical soil test trends.
    محلل اتجاهات تحليل التربة التاريخية

    Tracks changes in soil nutrients and properties over time,
    identifies trends, and provides management recommendations.

    Usage:
        analyzer = SoilTrendAnalyzer()
        report = analyzer.analyze_trends(field_id, soil_tests)
        print(report.summary_ar)
    """

    def __init__(
        self,
        config: TrendAnalysisConfig | None = None,
    ):
        """
        Initialize the trend analyzer.

        Args:
            config: Analysis configuration
        """
        self.config = config or TrendAnalysisConfig()
        self.interpreter = SoilTestInterpreter()
        self.thresholds = NUTRIENT_THRESHOLDS

    def analyze_trends(
        self,
        field_id: str,
        tenant_id: str,
        soil_tests: list[SoilTestResult],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> TrendReport:
        """
        Analyze trends across multiple soil tests.

        Args:
            field_id: Field identifier
            tenant_id: Tenant identifier
            soil_tests: List of soil test results (chronologically ordered)
            start_date: Analysis start date (optional)
            end_date: Analysis end date (optional)

        Returns:
            TrendReport with comprehensive trend analysis
        """
        # Filter tests by field and date range
        filtered_tests = [t for t in soil_tests if t.field_id == field_id]

        if start_date:
            filtered_tests = [t for t in filtered_tests if t.sample_date >= start_date]
        if end_date:
            filtered_tests = [t for t in filtered_tests if t.sample_date <= end_date]

        # Sort by date
        filtered_tests.sort(key=lambda x: x.sample_date)

        if len(filtered_tests) < self.config.min_data_points:
            return self._insufficient_data_report(field_id, tenant_id, len(filtered_tests))

        # Determine analysis period
        period_start = filtered_tests[0].sample_date
        period_end = filtered_tests[-1].sample_date

        # Analyze nutrient trends
        nutrient_trends = self._analyze_nutrient_trends(filtered_tests)

        # Analyze soil property trends
        ph_trend = self._analyze_single_trend(
            filtered_tests,
            lambda t: t.soil_properties.ph if t.soil_properties else None,
            "pH",
            "pH",
            "درجة الحموضة",
            "",
        )
        ec_trend = self._analyze_single_trend(
            filtered_tests,
            lambda t: t.soil_properties.ec_ds_m if t.soil_properties else None,
            "EC",
            "Electrical Conductivity",
            "التوصيل الكهربائي",
            "dS/m",
        )
        om_trend = self._analyze_single_trend(
            filtered_tests,
            lambda t: t.soil_properties.organic_matter_percent if t.soil_properties else None,
            "OM",
            "Organic Matter",
            "المادة العضوية",
            "%",
        )

        # Categorize nutrients by trend
        improving = []
        improving_ar = []
        declining = []
        declining_ar = []
        stable = []
        stable_ar = []

        for trend in nutrient_trends:
            if trend.trend_direction == "increasing":
                # Check if increasing is good (for most nutrients) or bad (for some)
                if trend.nutrient_code in ["Na", "Cl"] or (trend.data_points and self._is_excessive(trend)):
                    declining.append(trend.nutrient_name)
                    declining_ar.append(trend.nutrient_name_ar)
                else:
                    improving.append(trend.nutrient_name)
                    improving_ar.append(trend.nutrient_name_ar)
            elif trend.trend_direction == "decreasing":
                # Decreasing is usually concerning for nutrients
                if trend.nutrient_code in ["Na", "Cl", "EC"]:
                    improving.append(trend.nutrient_name)
                    improving_ar.append(trend.nutrient_name_ar)
                else:
                    declining.append(trend.nutrient_name)
                    declining_ar.append(trend.nutrient_name_ar)
            else:
                stable.append(trend.nutrient_name)
                stable_ar.append(trend.nutrient_name_ar)

        # Determine overall trend
        overall_trend, overall_trend_ar = self._determine_overall_trend(improving, declining, stable)

        # Calculate soil health scores over time
        health_scores = self._calculate_health_scores(filtered_tests)

        # Generate recommendations
        recommendations, recommendations_ar = self._generate_trend_recommendations(
            nutrient_trends, ph_trend, ec_trend, om_trend
        )

        # Generate summary
        summary_en, summary_ar = self._generate_trend_summary(filtered_tests, overall_trend, improving, declining)

        return TrendReport(
            field_id=field_id,
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            number_of_tests=len(filtered_tests),
            nutrient_trends=nutrient_trends,
            ph_trend=ph_trend,
            ec_trend=ec_trend,
            om_trend=om_trend,
            improving_nutrients=improving,
            improving_nutrients_ar=improving_ar,
            declining_nutrients=declining,
            declining_nutrients_ar=declining_ar,
            stable_nutrients=stable,
            stable_nutrients_ar=stable_ar,
            overall_trend=overall_trend,
            overall_trend_ar=overall_trend_ar,
            soil_health_score_history=health_scores,
            management_recommendations=recommendations,
            management_recommendations_ar=recommendations_ar,
            summary_en=summary_en,
            summary_ar=summary_ar,
        )

    def analyze_single_nutrient(
        self,
        soil_tests: list[SoilTestResult],
        nutrient_code: str,
    ) -> NutrientTrend:
        """
        Analyze trend for a single nutrient.

        Args:
            soil_tests: List of soil tests
            nutrient_code: Nutrient code (N, P, K, etc.)

        Returns:
            NutrientTrend for the specified nutrient
        """
        # Map nutrient code to extraction function
        extractors = {
            "N": lambda t: t.macronutrients.available_nitrogen_ppm if t.macronutrients else None,
            "P": lambda t: t.macronutrients.phosphorus_ppm if t.macronutrients else None,
            "K": lambda t: t.macronutrients.potassium_ppm if t.macronutrients else None,
            "Ca": lambda t: t.macronutrients.calcium_ppm if t.macronutrients else None,
            "Mg": lambda t: t.macronutrients.magnesium_ppm if t.macronutrients else None,
            "S": lambda t: t.macronutrients.sulfur_ppm if t.macronutrients else None,
            "Fe": lambda t: t.micronutrients.iron_ppm if t.micronutrients else None,
            "Zn": lambda t: t.micronutrients.zinc_ppm if t.micronutrients else None,
            "Mn": lambda t: t.micronutrients.manganese_ppm if t.micronutrients else None,
            "Cu": lambda t: t.micronutrients.copper_ppm if t.micronutrients else None,
            "B": lambda t: t.micronutrients.boron_ppm if t.micronutrients else None,
            "Mo": lambda t: t.micronutrients.molybdenum_ppm if t.micronutrients else None,
        }

        extractor = extractors.get(nutrient_code)
        if not extractor:
            return self._empty_trend(nutrient_code)

        thresholds = self.thresholds.get(nutrient_code, self.thresholds.get("P_olsen", {}))

        return self._analyze_single_trend(
            soil_tests,
            extractor,
            nutrient_code,
            thresholds.get("name", nutrient_code),
            thresholds.get("name_ar", nutrient_code),
            thresholds.get("unit", "ppm"),
        )

    def compare_periods(
        self,
        soil_tests: list[SoilTestResult],
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
    ) -> dict[str, Any]:
        """
        Compare soil health between two time periods.

        Args:
            soil_tests: All soil tests
            period1_*: First period boundaries
            period2_*: Second period boundaries

        Returns:
            Comparison dictionary
        """
        period1_tests = [t for t in soil_tests if period1_start <= t.sample_date <= period1_end]
        period2_tests = [t for t in soil_tests if period2_start <= t.sample_date <= period2_end]

        comparison = {
            "period1": {
                "start": period1_start.isoformat(),
                "end": period1_end.isoformat(),
                "test_count": len(period1_tests),
            },
            "period2": {
                "start": period2_start.isoformat(),
                "end": period2_end.isoformat(),
                "test_count": len(period2_tests),
            },
            "nutrient_changes": {},
            "property_changes": {},
            "improvement_summary": {},
        }

        if not period1_tests or not period2_tests:
            return comparison

        # Compare nutrients
        nutrients = ["N", "P", "K", "Ca", "Mg", "Fe", "Zn"]
        extractors = {
            "N": lambda t: t.macronutrients.available_nitrogen_ppm if t.macronutrients else None,
            "P": lambda t: t.macronutrients.phosphorus_ppm if t.macronutrients else None,
            "K": lambda t: t.macronutrients.potassium_ppm if t.macronutrients else None,
            "Ca": lambda t: t.macronutrients.calcium_ppm if t.macronutrients else None,
            "Mg": lambda t: t.macronutrients.magnesium_ppm if t.macronutrients else None,
            "Fe": lambda t: t.micronutrients.iron_ppm if t.micronutrients else None,
            "Zn": lambda t: t.micronutrients.zinc_ppm if t.micronutrients else None,
        }

        for nutrient in nutrients:
            extractor = extractors[nutrient]
            p1_values = [extractor(t) for t in period1_tests if extractor(t) is not None]
            p2_values = [extractor(t) for t in period2_tests if extractor(t) is not None]

            if p1_values and p2_values:
                p1_mean = statistics.mean(p1_values)
                p2_mean = statistics.mean(p2_values)
                change = p2_mean - p1_mean
                change_percent = (change / p1_mean * 100) if p1_mean != 0 else 0

                comparison["nutrient_changes"][nutrient] = {
                    "period1_mean": round(p1_mean, 2),
                    "period2_mean": round(p2_mean, 2),
                    "absolute_change": round(change, 2),
                    "percent_change": round(change_percent, 1),
                    "direction": "increased" if change > 0 else "decreased" if change < 0 else "stable",
                }

        # Compare properties
        for prop, extractor_fn, name in [
            ("pH", lambda t: t.soil_properties.ph if t.soil_properties else None, "pH"),
            ("EC", lambda t: t.soil_properties.ec_ds_m if t.soil_properties else None, "EC"),
            (
                "OM",
                lambda t: t.soil_properties.organic_matter_percent if t.soil_properties else None,
                "OM%",
            ),
        ]:
            p1_values = [extractor_fn(t) for t in period1_tests if extractor_fn(t) is not None]
            p2_values = [extractor_fn(t) for t in period2_tests if extractor_fn(t) is not None]

            if p1_values and p2_values:
                p1_mean = statistics.mean(p1_values)
                p2_mean = statistics.mean(p2_values)
                change = p2_mean - p1_mean

                comparison["property_changes"][prop] = {
                    "period1_mean": round(p1_mean, 2),
                    "period2_mean": round(p2_mean, 2),
                    "change": round(change, 2),
                }

        return comparison

    def _analyze_nutrient_trends(
        self,
        soil_tests: list[SoilTestResult],
    ) -> list[NutrientTrend]:
        """Analyze trends for all nutrients"""
        trends = []

        # Macronutrients
        macro_extractors = [
            ("N", lambda t: t.macronutrients.available_nitrogen_ppm if t.macronutrients else None),
            ("P", lambda t: t.macronutrients.phosphorus_ppm if t.macronutrients else None),
            ("K", lambda t: t.macronutrients.potassium_ppm if t.macronutrients else None),
            ("Ca", lambda t: t.macronutrients.calcium_ppm if t.macronutrients else None),
            ("Mg", lambda t: t.macronutrients.magnesium_ppm if t.macronutrients else None),
            ("S", lambda t: t.macronutrients.sulfur_ppm if t.macronutrients else None),
        ]

        for code, extractor in macro_extractors:
            thresholds = self.thresholds.get(code, self.thresholds.get("P_olsen", {}))
            trend = self._analyze_single_trend(
                soil_tests,
                extractor,
                code,
                thresholds.get("name", code),
                thresholds.get("name_ar", code),
                thresholds.get("unit", "ppm"),
            )
            if trend.data_points:
                trends.append(trend)

        # Micronutrients
        micro_extractors = [
            ("Fe", lambda t: t.micronutrients.iron_ppm if t.micronutrients else None),
            ("Zn", lambda t: t.micronutrients.zinc_ppm if t.micronutrients else None),
            ("Mn", lambda t: t.micronutrients.manganese_ppm if t.micronutrients else None),
            ("Cu", lambda t: t.micronutrients.copper_ppm if t.micronutrients else None),
            ("B", lambda t: t.micronutrients.boron_ppm if t.micronutrients else None),
        ]

        for code, extractor in micro_extractors:
            thresholds = self.thresholds.get(code, {})
            trend = self._analyze_single_trend(
                soil_tests,
                extractor,
                code,
                thresholds.get("name", code),
                thresholds.get("name_ar", code),
                thresholds.get("unit", "ppm"),
            )
            if trend.data_points:
                trends.append(trend)

        return trends

    def _analyze_single_trend(
        self,
        soil_tests: list[SoilTestResult],
        value_extractor: callable,
        code: str,
        name: str,
        name_ar: str,
        unit: str,
    ) -> NutrientTrend:
        """Analyze trend for a single parameter"""
        data_points = []

        for test in soil_tests:
            value = value_extractor(test)
            if value is not None and value >= 0:
                data_points.append(
                    TrendDataPoint(
                        date=test.sample_date,
                        value=value,
                        soil_test_id=test.id,
                    )
                )

        if len(data_points) < 2:
            return self._empty_trend(code, name, name_ar, unit)

        # Calculate statistics
        values = [dp.value for dp in data_points]
        min_val = min(values)
        max_val = max(values)
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        # Calculate linear regression for trend
        slope, r_squared = self._calculate_trend(data_points)

        # Determine trend direction
        direction, direction_ar = self._interpret_trend_direction(slope, mean_val, std_dev)

        # Generate interpretation
        interpretation_en, interpretation_ar = self._generate_trend_interpretation(
            code, name, name_ar, direction, slope, mean_val
        )

        # Generate action recommendation
        action_en, action_ar = self._generate_trend_action(code, direction, slope, mean_val)

        # Build status history
        status_history = self._build_status_history(code, data_points)

        return NutrientTrend(
            nutrient_code=code,
            nutrient_name=name,
            nutrient_name_ar=name_ar,
            unit=unit,
            data_points=data_points,
            min_value=min_val,
            max_value=max_val,
            mean_value=mean_val,
            std_deviation=std_dev,
            trend_direction=direction,
            trend_direction_ar=direction_ar,
            trend_slope=slope,
            trend_r_squared=r_squared,
            status_history=status_history,
            interpretation_en=interpretation_en,
            interpretation_ar=interpretation_ar,
            trend_based_action=action_en,
            trend_based_action_ar=action_ar,
        )

    def _calculate_trend(
        self,
        data_points: list[TrendDataPoint],
    ) -> tuple[float, float]:
        """
        Calculate linear regression trend.

        Returns:
            (slope per year, r-squared)
        """
        if len(data_points) < 2:
            return 0.0, 0.0

        # Convert dates to days from first date
        first_date = data_points[0].date
        x = [(dp.date - first_date).days / 365.25 for dp in data_points]  # Years
        y = [dp.value for dp in data_points]

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        sum_y2 = sum(yi**2 for yi in y)

        # Calculate slope
        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            return 0.0, 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Calculate r-squared
        numerator = (n * sum_xy - sum_x * sum_y) ** 2
        denom_y = n * sum_y2 - sum_y**2
        if denom_y == 0 or denominator == 0:
            r_squared = 0.0
        else:
            r_squared = numerator / (denominator * denom_y)

        return round(slope, 3), round(r_squared, 3)

    def _interpret_trend_direction(
        self,
        slope: float,
        mean: float,
        std_dev: float,
    ) -> tuple[str, str]:
        """Interpret the trend direction"""
        # Use coefficient of variation for significance
        if mean == 0:
            return "stable", "مستقر"

        (std_dev / mean) * 100 if mean != 0 else 0
        slope_percent = (slope / mean) * 100 if mean != 0 else 0

        if abs(slope_percent) < 2 or abs(slope) < self.config.slope_threshold:
            return "stable", "مستقر"
        elif slope > 0:
            if slope_percent > 10:
                return "increasing_rapidly", "يزداد بسرعة"
            return "increasing", "يزداد"
        else:
            if slope_percent < -10:
                return "decreasing_rapidly", "يتناقص بسرعة"
            return "decreasing", "يتناقص"

    def _generate_trend_interpretation(
        self,
        code: str,
        name: str,
        name_ar: str,
        direction: str,
        slope: float,
        mean: float,
    ) -> tuple[str, str]:
        """Generate human-readable trend interpretation"""
        if direction == "stable":
            return (
                f"{name} levels have remained stable around {mean:.1f} ppm",
                f"مستويات {name_ar} بقيت مستقرة حول {mean:.1f} جزء بالمليون",
            )
        elif "increasing" in direction:
            rate = "rapidly " if "rapidly" in direction else ""
            rate_ar = "بسرعة " if "rapidly" in direction else ""
            return (
                f"{name} is {rate}increasing at {abs(slope):.2f} ppm/year",
                f"{name_ar} {rate_ar}يزداد بمعدل {abs(slope):.2f} جزء بالمليون/سنة",
            )
        else:
            rate = "rapidly " if "rapidly" in direction else ""
            rate_ar = "بسرعة " if "rapidly" in direction else ""
            return (
                f"{name} is {rate}declining at {abs(slope):.2f} ppm/year",
                f"{name_ar} {rate_ar}يتناقص بمعدل {abs(slope):.2f} جزء بالمليون/سنة",
            )

    def _generate_trend_action(
        self,
        code: str,
        direction: str,
        slope: float,
        mean: float,
    ) -> tuple[str, str]:
        """Generate trend-based action recommendation"""
        if direction == "stable":
            return (
                "Maintain current management practices",
                "حافظ على ممارسات الإدارة الحالية",
            )
        elif "increasing" in direction:
            if code in ["Na", "Cl", "EC"]:
                return (
                    "Monitor and consider salinity management",
                    "راقب ونظر في إدارة الملوحة",
                )
            # Check if approaching excessive
            return (
                "Monitor levels; may reduce application rates",
                "راقب المستويات؛ قد تقلل معدلات التطبيق",
            )
        else:  # decreasing
            if code in ["Na", "Cl", "EC"]:
                return (
                    "Positive trend; continue management",
                    "اتجاه إيجابي؛ استمر في الإدارة",
                )
            return (
                f"Address declining {code}; increase application or adjust management",
                f"عالج تناقص {code}؛ زد التطبيق أو عدّل الإدارة",
            )

    def _build_status_history(
        self,
        code: str,
        data_points: list[TrendDataPoint],
    ) -> list[dict]:
        """Build status history from data points"""
        history = []
        for dp in data_points:
            status = self._get_status_for_value(code, dp.value)
            history.append(
                {
                    "date": dp.date.isoformat(),
                    "value": dp.value,
                    "status": status.value,
                }
            )
        return history

    def _get_status_for_value(self, code: str, value: float) -> NutrientStatus:
        """Get nutrient status for a value"""
        thresholds = self.thresholds.get(code, self.thresholds.get("P_olsen", {}))

        if value <= thresholds.get("very_deficient", 0):
            return NutrientStatus.VERY_DEFICIENT
        elif value <= thresholds.get("deficient", 0):
            return NutrientStatus.DEFICIENT
        elif value <= thresholds.get("low", 0):
            return NutrientStatus.LOW
        elif value <= thresholds.get("adequate", 0):
            return NutrientStatus.ADEQUATE
        elif value <= thresholds.get("high", 0):
            return NutrientStatus.OPTIMAL
        else:
            return NutrientStatus.HIGH

    def _empty_trend(
        self,
        code: str,
        name: str = "",
        name_ar: str = "",
        unit: str = "ppm",
    ) -> NutrientTrend:
        """Return empty trend for insufficient data"""
        thresholds = self.thresholds.get(code, {})
        return NutrientTrend(
            nutrient_code=code,
            nutrient_name=name or thresholds.get("name", code),
            nutrient_name_ar=name_ar or thresholds.get("name_ar", code),
            unit=unit,
            data_points=[],
            trend_direction="unknown",
            trend_direction_ar="غير معروف",
            interpretation_en="Insufficient data for trend analysis",
            interpretation_ar="بيانات غير كافية لتحليل الاتجاه",
        )

    def _is_excessive(self, trend: NutrientTrend) -> bool:
        """Check if trend indicates excessive levels"""
        if not trend.data_points:
            return False
        thresholds = self.thresholds.get(trend.nutrient_code, {})
        high_threshold = thresholds.get("high", float("inf"))
        return trend.mean_value > high_threshold

    def _determine_overall_trend(
        self,
        improving: list[str],
        declining: list[str],
        stable: list[str],
    ) -> tuple[str, str]:
        """Determine overall soil health trend"""
        if len(declining) > len(improving) + len(stable) // 2:
            return "declining", "متراجع"
        elif len(improving) > len(declining) + len(stable) // 2:
            return "improving", "متحسن"
        else:
            return "stable", "مستقر"

    def _calculate_health_scores(
        self,
        soil_tests: list[SoilTestResult],
    ) -> list[dict]:
        """Calculate soil health scores for each test"""
        scores = []
        for test in soil_tests:
            interpretation = self.interpreter.interpret(test)
            scores.append(
                {
                    "date": test.sample_date.isoformat(),
                    "score": interpretation.overall_fertility_score,
                    "grade": interpretation.overall_fertility_grade,
                }
            )
        return scores

    def _generate_trend_recommendations(
        self,
        nutrient_trends: list[NutrientTrend],
        ph_trend: NutrientTrend | None,
        ec_trend: NutrientTrend | None,
        om_trend: NutrientTrend | None,
    ) -> tuple[list[str], list[str]]:
        """Generate management recommendations based on trends"""
        recommendations_en = []
        recommendations_ar = []

        # Check for declining major nutrients
        for trend in nutrient_trends:
            if trend.trend_direction in ["decreasing", "decreasing_rapidly"]:
                if trend.nutrient_code in ["N", "P", "K"]:
                    recommendations_en.append(
                        f"Increase {trend.nutrient_name} fertilization to reverse declining trend"
                    )
                    recommendations_ar.append(f"زد تسميد {trend.nutrient_name_ar} لعكس الاتجاه المتراجع")

        # pH trends
        if ph_trend and ph_trend.trend_direction == "decreasing" and ph_trend.mean_value < 6.5:
            recommendations_en.append("Apply lime to prevent further pH decline")
            recommendations_ar.append("طبق الجير لمنع المزيد من انخفاض الحموضة")
        elif ph_trend and ph_trend.trend_direction == "increasing" and ph_trend.mean_value > 7.5:
            recommendations_en.append("Monitor alkalinity; consider acidifying amendments if needed")
            recommendations_ar.append("راقب القلوية؛ نظر في التعديلات المحمضة إذا لزم الأمر")

        # EC/salinity trends
        if ec_trend and ec_trend.trend_direction in ["increasing", "increasing_rapidly"]:
            recommendations_en.append("Implement salinity management: leaching, drainage improvement")
            recommendations_ar.append("طبق إدارة الملوحة: غسيل، تحسين الصرف")

        # Organic matter trends
        if om_trend and om_trend.trend_direction in ["decreasing", "decreasing_rapidly"]:
            recommendations_en.append("Increase organic inputs to reverse declining organic matter")
            recommendations_ar.append("زد المدخلات العضوية لعكس تراجع المادة العضوية")

        # General maintenance
        if not recommendations_en:
            recommendations_en.append("Continue current management; soil health is stable")
            recommendations_ar.append("استمر في الإدارة الحالية؛ صحة التربة مستقرة")

        return recommendations_en, recommendations_ar

    def _generate_trend_summary(
        self,
        soil_tests: list[SoilTestResult],
        overall_trend: str,
        improving: list[str],
        declining: list[str],
    ) -> tuple[str, str]:
        """Generate trend analysis summary"""
        n_tests = len(soil_tests)
        years = (soil_tests[-1].sample_date - soil_tests[0].sample_date).days / 365.25

        summary_en = f"Analysis of {n_tests} soil tests over {years:.1f} years shows "
        summary_ar = f"تحليل {n_tests} اختبار تربة على مدى {years:.1f} سنة يظهر "

        if overall_trend == "improving":
            summary_en += "overall improvement in soil health. "
            summary_ar += "تحسن عام في صحة التربة. "
        elif overall_trend == "declining":
            summary_en += "declining soil health requiring attention. "
            summary_ar += "تراجع في صحة التربة يتطلب انتباه. "
        else:
            summary_en += "stable soil conditions. "
            summary_ar += "ظروف تربة مستقرة. "

        if improving:
            summary_en += f"Improving: {', '.join(improving[:3])}. "
            improving_ar_text = "، ".join([self._translate_nutrient(n) for n in improving[:3]])
            summary_ar += f"متحسن: {improving_ar_text}. "

        if declining:
            summary_en += f"Needs attention: {', '.join(declining[:3])}."
            declining_ar_text = "، ".join([self._translate_nutrient(n) for n in declining[:3]])
            summary_ar += f"يحتاج انتباه: {declining_ar_text}."

        return summary_en, summary_ar

    def _translate_nutrient(self, name: str) -> str:
        """Translate nutrient name to Arabic"""
        translations = {
            "Nitrogen": "نيتروجين",
            "Phosphorus": "فسفور",
            "Potassium": "بوتاسيوم",
            "Calcium": "كالسيوم",
            "Magnesium": "مغنيسيوم",
            "Sulfur": "كبريت",
            "Iron": "حديد",
            "Zinc": "زنك",
            "Manganese": "منجنيز",
            "Copper": "نحاس",
            "Boron": "بورون",
            "Molybdenum": "موليبدنوم",
            "pH": "درجة الحموضة",
            "EC": "التوصيل الكهربائي",
            "OM": "المادة العضوية",
        }
        return translations.get(name, name)

    def _insufficient_data_report(
        self,
        field_id: str,
        tenant_id: str,
        test_count: int,
    ) -> TrendReport:
        """Generate report for insufficient data"""
        return TrendReport(
            field_id=field_id,
            tenant_id=tenant_id,
            number_of_tests=test_count,
            overall_trend="unknown",
            overall_trend_ar="غير معروف",
            summary_en=f"Insufficient data for trend analysis. Have {test_count} test(s), need at least {self.config.min_data_points}.",
            summary_ar=f"بيانات غير كافية لتحليل الاتجاه. لديك {test_count} اختبار، تحتاج على الأقل {self.config.min_data_points}.",
            management_recommendations=["Collect more soil test samples over time"],
            management_recommendations_ar=["اجمع المزيد من عينات اختبار التربة على مدار الوقت"],
        )


# Convenience functions
def analyze_soil_trends(
    field_id: str,
    tenant_id: str,
    soil_tests: list[SoilTestResult],
) -> TrendReport:
    """
    Quick trend analysis for a field.

    Args:
        field_id: Field identifier
        tenant_id: Tenant identifier
        soil_tests: List of soil test results

    Returns:
        TrendReport
    """
    analyzer = SoilTrendAnalyzer()
    return analyzer.analyze_trends(field_id, tenant_id, soil_tests)


def get_nutrient_trend(
    soil_tests: list[SoilTestResult],
    nutrient: str,
) -> NutrientTrend:
    """
    Get trend for a specific nutrient.

    Args:
        soil_tests: List of soil tests
        nutrient: Nutrient code (N, P, K, etc.)

    Returns:
        NutrientTrend
    """
    analyzer = SoilTrendAnalyzer()
    return analyzer.analyze_single_nutrient(soil_tests, nutrient)


def compare_soil_periods(
    soil_tests: list[SoilTestResult],
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime,
) -> dict:
    """
    Compare soil health between two periods.

    Args:
        soil_tests: All soil tests
        period1_*: First period boundaries
        period2_*: Second period boundaries

    Returns:
        Comparison dictionary
    """
    analyzer = SoilTrendAnalyzer()
    return analyzer.compare_periods(soil_tests, period1_start, period1_end, period2_start, period2_end)
