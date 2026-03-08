"""
Spray Window Optimization Module
================================
وحدة تحسين نافذة الرش

Calculates optimal spray windows based on weather conditions including:
- Temperature ranges and phytotoxicity risk
- Wind speed thresholds and drift risk
- Humidity considerations for drying and absorption
- Temperature inversion detection
- Rain forecast impact

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any

from .models import (
    AlertThresholds,
    SprayCondition,
    SprayWindow,
    WeatherForecast,
)


@dataclass
class SprayWindowConfig:
    """Configuration for spray window calculation"""

    thresholds: AlertThresholds = None

    # Temperature range (Celsius)
    temp_min: float = 10.0
    temp_max: float = 30.0
    temp_optimal_min: float = 15.0
    temp_optimal_max: float = 25.0

    # Wind thresholds (km/h)
    wind_max: float = 15.0
    wind_optimal_max: float = 8.0
    wind_min: float = 2.0  # Some air movement helps coverage

    # Humidity range (%)
    humidity_min: float = 40.0
    humidity_max: float = 85.0
    humidity_optimal_min: float = 50.0
    humidity_optimal_max: float = 75.0

    # Rain threshold
    rain_probability_max: float = 20.0  # % chance
    hours_without_rain_before: float = 2.0
    hours_without_rain_after: float = 4.0

    # Inversion settings
    detect_inversions: bool = True
    inversion_typical_start_hour: int = 18  # 6 PM
    inversion_typical_end_hour: int = 8  # 8 AM

    # Time-of-day preferences
    preferred_start_hour: int = 6
    preferred_end_hour: int = 20
    avoid_midday_heat: bool = True
    midday_start_hour: int = 11
    midday_end_hour: int = 15

    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = AlertThresholds()


# Drift risk translations
DRIFT_RISK_TRANSLATIONS = {
    "low": "منخفض",
    "medium": "متوسط",
    "high": "مرتفع",
    "very_high": "مرتفع جداً",
}

EVAPORATION_RISK_TRANSLATIONS = {
    "low": "منخفض",
    "medium": "متوسط",
    "high": "مرتفع",
}

PHYTOTOXICITY_RISK_TRANSLATIONS = {
    "low": "منخفض",
    "medium": "متوسط",
    "high": "مرتفع",
}


class SprayWindowCalculator:
    """
    Spray Window Calculator
    حاسبة نافذة الرش

    Calculates optimal spray windows based on weather conditions with
    consideration for:
    - Temperature and phytotoxicity risk
    - Wind speed and drift risk
    - Humidity for drying and absorption
    - Temperature inversions
    - Rain forecast

    Usage:
        calculator = SprayWindowCalculator()

        # Get spray windows for next 48 hours
        windows = calculator.find_spray_windows(
            hourly_forecasts=forecasts,
            min_duration_hours=2.0
        )

        for window in windows:
            print(f"Window: {window.start_time} - {window.end_time}")
            print(f"Score: {window.score}/100 ({window.overall_condition.value})")
            print(f"Recommendation: {window.recommendation}")
            print(f"التوصية: {window.recommendation_ar}")
    """

    def __init__(self, config: SprayWindowConfig | None = None):
        """Initialize the spray window calculator"""
        self.config = config or SprayWindowConfig()

    def find_spray_windows(
        self,
        hourly_forecasts: list[WeatherForecast],
        min_duration_hours: float = 2.0,
        max_windows: int = 5,
    ) -> list[SprayWindow]:
        """
        Find optimal spray windows from hourly forecast data

        Args:
            hourly_forecasts: List of hourly weather forecasts
            min_duration_hours: Minimum window duration in hours
            max_windows: Maximum number of windows to return

        Returns:
            List of spray windows sorted by score (best first)
        """
        if not hourly_forecasts:
            return []

        # Score each hour
        scored_hours: list[tuple[WeatherForecast, float, dict[str, Any]]] = []

        for forecast in hourly_forecasts:
            score, details = self._score_hour(forecast)
            scored_hours.append((forecast, score, details))

        # Find contiguous windows
        windows: list[SprayWindow] = []
        current_window_start = None
        current_window_forecasts: list[tuple[WeatherForecast, float, dict]] = []

        for forecast, score, details in scored_hours:
            # Consider suitable if score >= 50
            if score >= 50:
                if current_window_start is None:
                    current_window_start = forecast
                current_window_forecasts.append((forecast, score, details))
            else:
                # End current window if exists
                if current_window_forecasts:
                    window = self._create_window(current_window_forecasts)
                    if window.duration_hours >= min_duration_hours:
                        windows.append(window)
                current_window_start = None
                current_window_forecasts = []

        # Don't forget the last window
        if current_window_forecasts:
            window = self._create_window(current_window_forecasts)
            if window.duration_hours >= min_duration_hours:
                windows.append(window)

        # Sort by score (highest first)
        windows.sort(key=lambda w: w.score, reverse=True)

        return windows[:max_windows]

    def evaluate_time_slot(
        self,
        forecast: WeatherForecast,
    ) -> SprayWindow:
        """
        Evaluate a single time slot for spraying

        Args:
            forecast: Weather forecast for the time slot

        Returns:
            SprayWindow with detailed evaluation
        """
        score, details = self._score_hour(forecast)
        return self._create_single_window(forecast, score, details)

    def _score_hour(
        self,
        forecast: WeatherForecast,
    ) -> tuple[float, dict[str, Any]]:
        """Score a single hour for spray suitability"""
        scores = {
            "temperature": 0.0,
            "humidity": 0.0,
            "wind": 0.0,
            "rain": 0.0,
            "inversion": 0.0,
        }
        risks = {
            "drift": "low",
            "evaporation": "low",
            "phytotoxicity": "low",
        }

        # Temperature score (0-100)
        temp = forecast.temperature
        if self.config.temp_optimal_min <= temp <= self.config.temp_optimal_max:
            scores["temperature"] = 100.0
        elif self.config.temp_min <= temp <= self.config.temp_max:
            # Linear interpolation
            if temp < self.config.temp_optimal_min:
                scores["temperature"] = 70.0 + 30.0 * (
                    (temp - self.config.temp_min) / (self.config.temp_optimal_min - self.config.temp_min)
                )
            else:
                scores["temperature"] = 70.0 + 30.0 * (
                    (self.config.temp_max - temp) / (self.config.temp_max - self.config.temp_optimal_max)
                )
        else:
            scores["temperature"] = 0.0
            if temp > self.config.temp_max:
                risks["phytotoxicity"] = "high"
                risks["evaporation"] = "high"
            else:
                risks["phytotoxicity"] = "medium"

        # Humidity score (0-100)
        humidity = forecast.humidity
        if self.config.humidity_optimal_min <= humidity <= self.config.humidity_optimal_max:
            scores["humidity"] = 100.0
        elif self.config.humidity_min <= humidity <= self.config.humidity_max:
            if humidity < self.config.humidity_optimal_min:
                scores["humidity"] = 70.0 + 30.0 * (
                    (humidity - self.config.humidity_min)
                    / (self.config.humidity_optimal_min - self.config.humidity_min)
                )
                risks["evaporation"] = "medium"
            else:
                scores["humidity"] = 70.0 + 30.0 * (
                    (self.config.humidity_max - humidity)
                    / (self.config.humidity_max - self.config.humidity_optimal_max)
                )
        else:
            scores["humidity"] = 0.0
            if humidity < self.config.humidity_min:
                risks["evaporation"] = "high"

        # Wind score (0-100)
        wind = forecast.wind_gust or forecast.wind_speed
        if self.config.wind_min <= wind <= self.config.wind_optimal_max:
            scores["wind"] = 100.0
        elif wind <= self.config.wind_max:
            scores["wind"] = 70.0 + 30.0 * (
                (self.config.wind_max - wind) / (self.config.wind_max - self.config.wind_optimal_max)
            )
            risks["drift"] = "medium"
        else:
            scores["wind"] = 0.0
            if wind > self.config.wind_max * 1.5:
                risks["drift"] = "very_high"
            else:
                risks["drift"] = "high"

        # Rain score (0-100)
        rain_prob = forecast.precipitation_probability
        if rain_prob <= self.config.rain_probability_max:
            scores["rain"] = 100.0 - (rain_prob / self.config.rain_probability_max * 30.0)
        elif rain_prob <= 50:
            scores["rain"] = 50.0
        else:
            scores["rain"] = 0.0

        # Inversion score (0-100)
        if self.config.detect_inversions and forecast.is_inversion_likely:
            scores["inversion"] = 0.0
            risks["drift"] = "very_high"
        else:
            # Check for typical inversion hours if no explicit flag
            hour = forecast.hour
            if hour is not None:
                is_inversion_hour = (
                    hour >= self.config.inversion_typical_start_hour or hour < self.config.inversion_typical_end_hour
                )
                if is_inversion_hour and forecast.wind_speed < 3:
                    # Low wind during typical inversion hours - likely inversion
                    scores["inversion"] = 30.0
                    risks["drift"] = "high"
                else:
                    scores["inversion"] = 100.0
            else:
                scores["inversion"] = 80.0  # Unknown, assume slightly risky

        # Calculate weighted average
        weights = {
            "temperature": 0.20,
            "humidity": 0.20,
            "wind": 0.30,
            "rain": 0.15,
            "inversion": 0.15,
        }

        total_score = sum(scores[key] * weights[key] for key in scores)

        details = {
            "scores": scores,
            "risks": risks,
            "weights": weights,
        }

        return total_score, details

    def _create_window(
        self,
        forecasts_with_scores: list[tuple[WeatherForecast, float, dict]],
    ) -> SprayWindow:
        """Create a SprayWindow from a list of consecutive suitable hours"""
        if not forecasts_with_scores:
            return SprayWindow()

        forecasts = [f[0] for f in forecasts_with_scores]
        scores = [f[1] for f in forecasts_with_scores]
        all_details = [f[2] for f in forecasts_with_scores]

        # Calculate averages
        avg_score = sum(scores) / len(scores)
        avg_temp = sum(f.temperature for f in forecasts) / len(forecasts)
        min_temp = min(f.temperature for f in forecasts)
        max_temp = max(f.temperature for f in forecasts)
        avg_humidity = sum(f.humidity for f in forecasts) / len(forecasts)
        avg_wind = sum(f.wind_gust or f.wind_speed for f in forecasts) / len(forecasts)
        max_wind = max(f.wind_gust or f.wind_speed for f in forecasts)

        # Aggregate scores
        avg_temp_score = sum(d["scores"]["temperature"] for d in all_details) / len(all_details)
        avg_humidity_score = sum(d["scores"]["humidity"] for d in all_details) / len(all_details)
        avg_wind_score = sum(d["scores"]["wind"] for d in all_details) / len(all_details)
        avg_inversion_score = sum(d["scores"]["inversion"] for d in all_details) / len(all_details)
        avg_rain_score = sum(d["scores"]["rain"] for d in all_details) / len(all_details)

        # Determine overall risks (use worst case)
        drift_risks = [d["risks"]["drift"] for d in all_details]
        evap_risks = [d["risks"]["evaporation"] for d in all_details]
        phyto_risks = [d["risks"]["phytotoxicity"] for d in all_details]

        risk_order = ["low", "medium", "high", "very_high"]
        drift_risk = max(drift_risks, key=lambda r: risk_order.index(r) if r in risk_order else 0)
        evap_risk = max(evap_risks, key=lambda r: risk_order.index(r) if r in risk_order else 0)
        phyto_risk = max(phyto_risks, key=lambda r: risk_order.index(r) if r in risk_order else 0)

        # Determine overall condition
        if avg_score >= 85:
            condition = SprayCondition.OPTIMAL
        elif avg_score >= 70:
            condition = SprayCondition.ACCEPTABLE
        elif avg_score >= 50:
            condition = SprayCondition.MARGINAL
        elif drift_risk in ["high", "very_high"] or phyto_risk == "high":
            condition = SprayCondition.DANGEROUS
        else:
            condition = SprayCondition.UNSUITABLE

        # Check for inversion
        is_inversion = any(f.is_inversion_likely for f in forecasts)
        inversion_warning = ""
        inversion_warning_ar = ""
        if is_inversion:
            inversion_warning = "Temperature inversion detected. High drift risk - avoid spraying."
            inversion_warning_ar = "انقلاب حراري مكتشف. خطر انجراف عالي - تجنب الرش."

        # Generate recommendation
        recommendation, recommendation_ar = self._generate_recommendation(
            condition, drift_risk, evap_risk, phyto_risk, is_inversion
        )

        # Generate cautions and adjustments
        cautions, cautions_ar = self._generate_cautions(
            drift_risk, evap_risk, phyto_risk, max_wind, avg_humidity, avg_temp
        )
        adjustments, adjustments_ar = self._generate_adjustments(
            drift_risk, evap_risk, avg_wind, avg_humidity, avg_temp
        )

        # Determine product suitability
        suitable_volatile = avg_temp <= 25 and avg_humidity >= 60 and drift_risk not in ["high", "very_high"]

        first_forecast = forecasts[0]
        last_forecast = forecasts[-1]

        start_time = datetime.combine(first_forecast.forecast_date, time(hour=first_forecast.hour or 0))
        end_time = datetime.combine(last_forecast.forecast_date, time(hour=(last_forecast.hour or 0) + 1))

        return SprayWindow(
            start_time=start_time,
            end_time=end_time,
            duration_hours=float(len(forecasts)),
            overall_condition=condition,
            score=avg_score,
            temperature_score=avg_temp_score,
            humidity_score=avg_humidity_score,
            wind_score=avg_wind_score,
            inversion_score=avg_inversion_score,
            rain_score=avg_rain_score,
            temperature_avg=avg_temp,
            temperature_min=min_temp,
            temperature_max=max_temp,
            humidity_avg=avg_humidity,
            wind_speed_avg=avg_wind,
            wind_speed_max=max_wind,
            drift_risk=drift_risk,
            drift_risk_ar=DRIFT_RISK_TRANSLATIONS.get(drift_risk, drift_risk),
            evaporation_risk=evap_risk,
            evaporation_risk_ar=EVAPORATION_RISK_TRANSLATIONS.get(evap_risk, evap_risk),
            phytotoxicity_risk=phyto_risk,
            phytotoxicity_risk_ar=PHYTOTOXICITY_RISK_TRANSLATIONS.get(phyto_risk, phyto_risk),
            recommendation=recommendation,
            cautions=cautions,
            adjustments=adjustments,
            recommendation_ar=recommendation_ar,
            cautions_ar=cautions_ar,
            adjustments_ar=adjustments_ar,
            is_inversion_period=is_inversion,
            inversion_warning=inversion_warning,
            inversion_warning_ar=inversion_warning_ar,
            suitable_for_systemic=True,
            suitable_for_contact=condition in [SprayCondition.OPTIMAL, SprayCondition.ACCEPTABLE],
            suitable_for_volatile=suitable_volatile,
        )

    def _create_single_window(
        self,
        forecast: WeatherForecast,
        score: float,
        details: dict[str, Any],
    ) -> SprayWindow:
        """Create a SprayWindow for a single hour evaluation"""
        return self._create_window([(forecast, score, details)])

    def _generate_recommendation(
        self,
        condition: SprayCondition,
        drift_risk: str,
        evap_risk: str,
        phyto_risk: str,
        is_inversion: bool,
    ) -> tuple[str, str]:
        """Generate recommendation text"""
        if condition == SprayCondition.OPTIMAL:
            return (
                "Excellent conditions for spraying. All parameters within optimal range.",
                "ظروف ممتازة للرش. جميع المعايير ضمن النطاق المثالي.",
            )
        elif condition == SprayCondition.ACCEPTABLE:
            return (
                "Good conditions for spraying. Proceed with standard precautions.",
                "ظروف جيدة للرش. استمر مع الاحتياطات القياسية.",
            )
        elif condition == SprayCondition.MARGINAL:
            return (
                "Marginal conditions. Consider adjusting spray parameters or waiting for better conditions.",
                "ظروف هامشية. فكر في تعديل معايير الرش أو انتظار ظروف أفضل.",
            )
        elif condition == SprayCondition.DANGEROUS:
            if is_inversion:
                return (
                    "DANGEROUS: Temperature inversion present. DO NOT spray - extreme drift risk.",
                    "خطر: انقلاب حراري موجود. لا ترش - خطر انجراف شديد.",
                )
            elif drift_risk in ["high", "very_high"]:
                return (
                    "DANGEROUS: High drift risk due to wind. DO NOT spray.",
                    "خطر: خطر انجراف عالي بسبب الرياح. لا ترش.",
                )
            elif phyto_risk == "high":
                return (
                    "DANGEROUS: High phytotoxicity risk due to temperature. DO NOT spray.",
                    "خطر: خطر سمية نباتية عالي بسبب الحرارة. لا ترش.",
                )
            else:
                return (
                    "DANGEROUS: Conditions unsuitable for safe spraying.",
                    "خطر: الظروف غير مناسبة للرش الآمن.",
                )
        else:  # UNSUITABLE
            return (
                "Conditions not suitable for spraying. Wait for better weather.",
                "الظروف غير مناسبة للرش. انتظر طقساً أفضل.",
            )

    def _generate_cautions(
        self,
        drift_risk: str,
        evap_risk: str,
        phyto_risk: str,
        wind_speed: float,
        humidity: float,
        temperature: float,
    ) -> tuple[list[str], list[str]]:
        """Generate caution messages"""
        cautions_en: list[str] = []
        cautions_ar: list[str] = []

        if drift_risk == "medium":
            cautions_en.append(f"Wind speed ({wind_speed:.1f} km/h) approaching drift threshold")
            cautions_ar.append(f"سرعة الرياح ({wind_speed:.1f} كم/ساعة) تقترب من عتبة الانجراف")

        if evap_risk in ["medium", "high"]:
            cautions_en.append(f"Low humidity ({humidity:.0f}%) may cause droplet evaporation")
            cautions_ar.append(f"الرطوبة المنخفضة ({humidity:.0f}%) قد تسبب تبخر القطرات")

        if phyto_risk == "medium":
            cautions_en.append(f"Temperature ({temperature:.1f}C) may increase phytotoxicity risk")
            cautions_ar.append(f"درجة الحرارة ({temperature:.1f}م) قد تزيد خطر السمية النباتية")

        if temperature > 28:
            cautions_en.append("Avoid spraying oil-based products in high heat")
            cautions_ar.append("تجنب رش المنتجات الزيتية في الحرارة العالية")

        if humidity > 80:
            cautions_en.append("High humidity may slow drying - allow extra time before rain")
            cautions_ar.append("الرطوبة العالية قد تبطئ الجفاف - اترك وقتاً إضافياً قبل المطر")

        return cautions_en, cautions_ar

    def _generate_adjustments(
        self,
        drift_risk: str,
        evap_risk: str,
        wind_speed: float,
        humidity: float,
        temperature: float,
    ) -> tuple[list[str], list[str]]:
        """Generate spray parameter adjustments"""
        adjustments_en: list[str] = []
        adjustments_ar: list[str] = []

        if drift_risk == "medium" or wind_speed > 10:
            adjustments_en.append("Use drift-reducing nozzles (air induction type)")
            adjustments_ar.append("استخدم فوهات تقليل الانجراف (نوع الحقن الهوائي)")
            adjustments_en.append("Lower boom height to minimum effective distance")
            adjustments_ar.append("خفض ارتفاع الذراع إلى الحد الأدنى الفعال")
            adjustments_en.append("Reduce spray pressure to produce coarser droplets")
            adjustments_ar.append("قلل ضغط الرش لإنتاج قطرات أكبر")

        if evap_risk == "medium" or humidity < 50:
            adjustments_en.append("Add humectant adjuvant to reduce evaporation")
            adjustments_ar.append("أضف مادة مساعدة مرطبة لتقليل التبخر")
            adjustments_en.append("Increase water volume by 10-15%")
            adjustments_ar.append("زد حجم الماء بنسبة 10-15%")

        if temperature > 25:
            adjustments_en.append("Schedule spraying for early morning hours")
            adjustments_ar.append("جدول الرش لساعات الصباح الباكر")
            adjustments_en.append("Avoid oil-based formulations")
            adjustments_ar.append("تجنب التركيبات الزيتية")

        return adjustments_en, adjustments_ar

    def detect_inversion(
        self,
        forecasts: list[WeatherForecast],
    ) -> list[tuple[datetime, datetime]]:
        """
        Detect temperature inversion periods from forecast data

        Temperature inversions occur when:
        - Calm winds (< 3 km/h)
        - Clear skies (cloud cover < 30%)
        - Temperature increases with height (detected by rapid surface cooling)
        - Typically evening through early morning

        Args:
            forecasts: Hourly weather forecasts

        Returns:
            List of (start, end) datetime tuples for inversion periods
        """
        inversion_periods: list[tuple[datetime, datetime]] = []
        current_start: datetime | None = None

        for i, forecast in enumerate(forecasts):
            is_inversion = self._check_inversion_conditions(forecast, forecasts, i)

            if is_inversion:
                if current_start is None:
                    current_start = datetime.combine(forecast.forecast_date, time(hour=forecast.hour or 0))
            else:
                if current_start is not None:
                    end_time = datetime.combine(forecast.forecast_date, time(hour=forecast.hour or 0))
                    inversion_periods.append((current_start, end_time))
                    current_start = None

        # Close any open period
        if current_start is not None and forecasts:
            last = forecasts[-1]
            end_time = datetime.combine(last.forecast_date, time(hour=(last.hour or 0) + 1))
            inversion_periods.append((current_start, end_time))

        return inversion_periods

    def _check_inversion_conditions(
        self,
        forecast: WeatherForecast,
        all_forecasts: list[WeatherForecast],
        index: int,
    ) -> bool:
        """Check if conditions indicate a temperature inversion"""
        # If explicitly flagged
        if forecast.is_inversion_likely:
            return True

        # Check conditions
        wind_calm = forecast.wind_speed < 3
        clear_sky = (forecast.cloud_cover or 0) < 30

        # Check for typical inversion hours
        hour = forecast.hour
        if hour is not None:
            is_inversion_hour = (
                hour >= self.config.inversion_typical_start_hour or hour < self.config.inversion_typical_end_hour
            )
        else:
            is_inversion_hour = False

        # Check for temperature cooling rate (if previous hour available)
        rapid_cooling = False
        if index > 0:
            prev_forecast = all_forecasts[index - 1]
            temp_drop = prev_forecast.temperature - forecast.temperature
            rapid_cooling = temp_drop > 2  # More than 2C drop per hour

        # Inversion likely if: calm + clear + (inversion hours OR rapid cooling)
        return wind_calm and clear_sky and (is_inversion_hour or rapid_cooling)

    def get_best_spray_time(
        self,
        hourly_forecasts: list[WeatherForecast],
        required_duration_hours: float = 2.0,
    ) -> SprayWindow | None:
        """
        Get the single best spray window

        Args:
            hourly_forecasts: Hourly weather forecasts
            required_duration_hours: Minimum required duration

        Returns:
            Best spray window or None if no suitable window found
        """
        windows = self.find_spray_windows(
            hourly_forecasts=hourly_forecasts,
            min_duration_hours=required_duration_hours,
            max_windows=1,
        )
        return windows[0] if windows else None

    def format_window_summary(
        self,
        window: SprayWindow,
        language: str = "both",
    ) -> str:
        """
        Format spray window as readable summary

        Args:
            window: Spray window to format
            language: "en", "ar", or "both"

        Returns:
            Formatted summary string
        """
        lines = []

        if language in ["en", "both"]:
            lines.append("=== Spray Window Summary ===")
            if window.start_time and window.end_time:
                lines.append(
                    f"Time: {window.start_time.strftime('%Y-%m-%d %H:%M')} - {window.end_time.strftime('%H:%M')}"
                )
            lines.append(f"Duration: {window.duration_hours:.1f} hours")
            lines.append(f"Condition: {window.overall_condition.value.upper()}")
            lines.append(f"Score: {window.score:.0f}/100")
            lines.append("")
            lines.append(
                f"Temperature: {window.temperature_min:.1f}-{window.temperature_max:.1f}C "
                f"(avg {window.temperature_avg:.1f}C)"
            )
            lines.append(f"Humidity: {window.humidity_avg:.0f}%")
            lines.append(f"Wind: avg {window.wind_speed_avg:.1f}, max {window.wind_speed_max:.1f} km/h")
            lines.append("")
            lines.append(f"Drift Risk: {window.drift_risk}")
            lines.append(f"Evaporation Risk: {window.evaporation_risk}")
            lines.append(f"Phytotoxicity Risk: {window.phytotoxicity_risk}")
            lines.append("")
            lines.append(f"Recommendation: {window.recommendation}")
            if window.cautions:
                lines.append("Cautions:")
                for c in window.cautions:
                    lines.append(f"  - {c}")
            if window.adjustments:
                lines.append("Adjustments:")
                for a in window.adjustments:
                    lines.append(f"  - {a}")

        if language == "both":
            lines.append("")
            lines.append("-" * 40)
            lines.append("")

        if language in ["ar", "both"]:
            lines.append("=== ملخص نافذة الرش ===")
            if window.start_time and window.end_time:
                lines.append(
                    f"الوقت: {window.start_time.strftime('%Y-%m-%d %H:%M')} - {window.end_time.strftime('%H:%M')}"
                )
            lines.append(f"المدة: {window.duration_hours:.1f} ساعات")
            lines.append(f"الحالة: {window.overall_condition.value.upper()}")
            lines.append(f"النتيجة: {window.score:.0f}/100")
            lines.append("")
            lines.append(
                f"الحرارة: {window.temperature_min:.1f}-{window.temperature_max:.1f}م "
                f"(متوسط {window.temperature_avg:.1f}م)"
            )
            lines.append(f"الرطوبة: {window.humidity_avg:.0f}%")
            lines.append(f"الرياح: متوسط {window.wind_speed_avg:.1f}، أقصى {window.wind_speed_max:.1f} كم/ساعة")
            lines.append("")
            lines.append(f"خطر الانجراف: {window.drift_risk_ar}")
            lines.append(f"خطر التبخر: {window.evaporation_risk_ar}")
            lines.append(f"خطر السمية النباتية: {window.phytotoxicity_risk_ar}")
            lines.append("")
            lines.append(f"التوصية: {window.recommendation_ar}")
            if window.cautions_ar:
                lines.append("التحذيرات:")
                for c in window.cautions_ar:
                    lines.append(f"  - {c}")
            if window.adjustments_ar:
                lines.append("التعديلات:")
                for a in window.adjustments_ar:
                    lines.append(f"  - {a}")

        return "\n".join(lines)


# Convenience functions
def find_spray_windows(
    hourly_forecasts: list[WeatherForecast],
    min_duration_hours: float = 2.0,
) -> list[SprayWindow]:
    """
    Find optimal spray windows from hourly forecast data

    Args:
        hourly_forecasts: List of hourly weather forecasts
        min_duration_hours: Minimum window duration

    Returns:
        List of spray windows sorted by score
    """
    calculator = SprayWindowCalculator()
    return calculator.find_spray_windows(
        hourly_forecasts=hourly_forecasts,
        min_duration_hours=min_duration_hours,
    )


def get_best_spray_time(
    hourly_forecasts: list[WeatherForecast],
    required_duration_hours: float = 2.0,
) -> SprayWindow | None:
    """
    Get the single best spray window

    Args:
        hourly_forecasts: Hourly weather forecasts
        required_duration_hours: Minimum required duration

    Returns:
        Best spray window or None if no suitable window found
    """
    calculator = SprayWindowCalculator()
    return calculator.get_best_spray_time(
        hourly_forecasts=hourly_forecasts,
        required_duration_hours=required_duration_hours,
    )


def detect_inversions(
    hourly_forecasts: list[WeatherForecast],
) -> list[tuple[datetime, datetime]]:
    """
    Detect temperature inversion periods

    Args:
        hourly_forecasts: Hourly weather forecasts

    Returns:
        List of (start, end) datetime tuples for inversion periods
    """
    calculator = SprayWindowCalculator()
    return calculator.detect_inversion(hourly_forecasts)
