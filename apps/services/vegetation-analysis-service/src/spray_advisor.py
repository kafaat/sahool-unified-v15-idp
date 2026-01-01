"""
SAHOOL Spray Time Advisor - OneSoil-style feature
مستشار وقت الرش - ميزة مشابهة لـ OneSoil

Recommend optimal spray times based on weather conditions:
- Temperature, humidity, wind speed, rain probability
- Product-specific requirements (herbicide, fungicide, insecticide)
- Delta-T calculation (wet bulb depression)
- Risk assessment (drift, wash-off, evaporation, phytotoxicity)
- Bilingual recommendations (Arabic/English)

Based on Open-Meteo weather API.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from enum import Enum
import httpx
import logging
import math

logger = logging.getLogger(__name__)


class SprayCondition(Enum):
    EXCELLENT = "excellent"  # Perfect conditions
    GOOD = "good"  # Safe to spray
    MARGINAL = "marginal"  # Some risk
    POOR = "poor"  # Not recommended
    DANGEROUS = "dangerous"  # Do not spray


class SprayProduct(Enum):
    HERBICIDE = "herbicide"
    INSECTICIDE = "insecticide"
    FUNGICIDE = "fungicide"
    FOLIAR_FERTILIZER = "foliar_fertilizer"
    GROWTH_REGULATOR = "growth_regulator"


@dataclass
class SprayWindow:
    """A window of time suitable for spraying"""

    start_time: datetime
    end_time: datetime
    duration_hours: float
    condition: SprayCondition
    score: float  # 0-100

    # Weather during window
    temp_avg: float
    humidity_avg: float
    wind_speed_avg: float
    precipitation_prob: float

    # Risks
    risks: List[str]
    recommendations_ar: List[str]
    recommendations_en: List[str]

    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_hours": round(self.duration_hours, 1),
            "condition": self.condition.value,
            "score": round(self.score, 1),
            "weather": {
                "temperature_c": round(self.temp_avg, 1),
                "humidity_percent": round(self.humidity_avg, 1),
                "wind_speed_kmh": round(self.wind_speed_avg, 1),
                "precipitation_probability": round(self.precipitation_prob, 1),
            },
            "risks": self.risks,
            "recommendations_ar": self.recommendations_ar,
            "recommendations_en": self.recommendations_en,
        }


@dataclass
class DailySprayForecast:
    """Daily spray forecast with all windows"""

    date: date
    overall_condition: SprayCondition
    best_window: Optional[SprayWindow]
    all_windows: List[SprayWindow]
    hours_suitable: float

    # Daily summary
    sunrise: datetime
    sunset: datetime
    temp_min: float
    temp_max: float
    rain_prob: float
    wind_max: float

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "overall_condition": self.overall_condition.value,
            "best_window": self.best_window.to_dict() if self.best_window else None,
            "all_windows": [w.to_dict() for w in self.all_windows],
            "hours_suitable": round(self.hours_suitable, 1),
            "daily_summary": {
                "sunrise": self.sunrise.isoformat(),
                "sunset": self.sunset.isoformat(),
                "temp_min_c": round(self.temp_min, 1),
                "temp_max_c": round(self.temp_max, 1),
                "rain_probability": round(self.rain_prob, 1),
                "wind_max_kmh": round(self.wind_max, 1),
            },
        }


class SprayAdvisor:
    """
    Recommend optimal spray times based on weather conditions.

    Uses Open-Meteo hourly forecast data to identify safe spray windows
    with product-specific requirements.
    """

    BASE_URL = "https://api.open-meteo.com/v1"

    # Ideal conditions for spraying (general)
    IDEAL_CONDITIONS = {
        "temp_min": 10,  # °C
        "temp_max": 30,  # °C
        "humidity_min": 40,  # %
        "humidity_max": 80,  # %
        "wind_max": 15,  # km/h (spray drift risk)
        "rain_prob_max": 20,  # % (wash-off risk)
        "rain_hours_after": 4,  # Hours needed without rain
        "delta_t_min": 2,  # °C (wet bulb depression)
        "delta_t_max": 8,  # °C
    }

    # Product-specific adjustments
    PRODUCT_CONDITIONS = {
        SprayProduct.HERBICIDE: {
            "temp_min": 15,  # Higher temp for absorption
            "temp_max": 28,
            "humidity_min": 50,
            "rain_hours_after": 6,  # Need more time for absorption
        },
        SprayProduct.FUNGICIDE: {
            "humidity_max": 70,  # Lower humidity to reduce spread
            "temp_max": 25,
            "wind_max": 12,
        },
        SprayProduct.INSECTICIDE: {
            "wind_max": 10,  # Lower wind for contact
            "temp_min": 12,
            "temp_max": 28,
        },
        SprayProduct.FOLIAR_FERTILIZER: {
            "humidity_min": 60,  # Higher humidity for absorption
            "temp_max": 28,
            "rain_hours_after": 4,
        },
        SprayProduct.GROWTH_REGULATOR: {
            "temp_min": 15,
            "temp_max": 25,
            "humidity_min": 50,
            "wind_max": 12,
        },
    }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_spray_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        product_type: Optional[SprayProduct] = None,
    ) -> List[DailySprayForecast]:
        """
        Get spray time recommendations for next N days.
        Uses weather forecast to identify optimal windows.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of forecast days (1-16)
            product_type: Type of spray product (optional)

        Returns:
            List of daily spray forecasts with optimal windows
        """
        days = min(max(days, 1), 16)

        # Fetch hourly weather forecast
        hourly_data = await self._fetch_hourly_forecast(latitude, longitude, days)

        # Group by day and identify spray windows
        daily_forecasts = []
        grouped_by_day = self._group_by_day(hourly_data)

        for day_date, hours in grouped_by_day.items():
            # Find spray windows for this day
            windows = self._identify_spray_windows(hours, product_type)

            # Calculate daily summary
            temps = [h["temp"] for h in hours]
            humidities = [h["humidity"] for h in hours]
            winds = [h["wind_speed"] for h in hours]
            rain_probs = [h["precipitation_prob"] for h in hours]

            # Determine overall condition for the day
            if windows:
                best_window = max(windows, key=lambda w: w.score)
                overall_condition = best_window.condition
                hours_suitable = sum(w.duration_hours for w in windows)
            else:
                best_window = None
                overall_condition = SprayCondition.POOR
                hours_suitable = 0

            daily_forecasts.append(
                DailySprayForecast(
                    date=day_date,
                    overall_condition=overall_condition,
                    best_window=best_window,
                    all_windows=windows,
                    hours_suitable=hours_suitable,
                    sunrise=hours[0]["time"].replace(hour=6, minute=0),  # Approximate
                    sunset=hours[0]["time"].replace(hour=18, minute=0),
                    temp_min=min(temps),
                    temp_max=max(temps),
                    rain_prob=max(rain_probs),
                    wind_max=max(winds),
                )
            )

        return daily_forecasts

    async def get_best_spray_time(
        self,
        latitude: float,
        longitude: float,
        product_type: SprayProduct,
        within_days: int = 3,
    ) -> Optional[SprayWindow]:
        """
        Find the single best spray window in the next N days.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            product_type: Type of spray product
            within_days: Search within next N days

        Returns:
            Best spray window or None if no suitable windows found
        """
        forecast = await self.get_spray_forecast(
            latitude, longitude, within_days, product_type
        )

        # Find best window across all days
        all_windows = []
        for day in forecast:
            all_windows.extend(day.all_windows)

        if not all_windows:
            return None

        # Return window with highest score
        return max(all_windows, key=lambda w: w.score)

    async def evaluate_spray_time(
        self,
        latitude: float,
        longitude: float,
        target_datetime: datetime,
        product_type: Optional[SprayProduct] = None,
    ) -> SprayWindow:
        """
        Evaluate if a specific time is suitable for spraying.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            target_datetime: Target spray time
            product_type: Type of spray product (optional)

        Returns:
            SprayWindow evaluation for the target time
        """
        # Fetch hourly forecast around target time
        days_ahead = (target_datetime.date() - datetime.now().date()).days
        days_ahead = max(1, min(days_ahead + 1, 16))

        hourly_data = await self._fetch_hourly_forecast(latitude, longitude, days_ahead)

        # Find closest hour to target time
        target_hour = None
        min_diff = timedelta.max

        for hour in hourly_data:
            diff = abs(hour["time"] - target_datetime)
            if diff < min_diff:
                min_diff = diff
                target_hour = hour

        if not target_hour:
            raise Exception("Could not find weather data for target time")

        # Evaluate this specific hour
        score, condition, risks = self.calculate_spray_score(
            target_hour["temp"],
            target_hour["humidity"],
            target_hour["wind_speed"],
            target_hour["precipitation_prob"],
            product_type,
        )

        recommendations = self.get_recommendations(condition, risks, product_type)

        return SprayWindow(
            start_time=target_hour["time"],
            end_time=target_hour["time"] + timedelta(hours=1),
            duration_hours=1.0,
            condition=condition,
            score=score,
            temp_avg=target_hour["temp"],
            humidity_avg=target_hour["humidity"],
            wind_speed_avg=target_hour["wind_speed"],
            precipitation_prob=target_hour["precipitation_prob"],
            risks=risks,
            recommendations_ar=recommendations["ar"],
            recommendations_en=recommendations["en"],
        )

    def calculate_spray_score(
        self,
        temp: float,
        humidity: float,
        wind_speed: float,
        rain_prob: float,
        product_type: Optional[SprayProduct] = None,
    ) -> Tuple[float, SprayCondition, List[str]]:
        """
        Calculate spray suitability score (0-100).

        Args:
            temp: Temperature in °C
            humidity: Relative humidity in %
            wind_speed: Wind speed in km/h
            rain_prob: Precipitation probability in %
            product_type: Type of spray product (optional)

        Returns:
            Tuple of (score, condition, risks)
        """
        # Get conditions (base or product-specific)
        conditions = self.IDEAL_CONDITIONS.copy()
        if product_type and product_type in self.PRODUCT_CONDITIONS:
            conditions.update(self.PRODUCT_CONDITIONS[product_type])

        score = 100.0
        risks = []

        # Temperature scoring
        if temp < conditions["temp_min"]:
            penalty = (conditions["temp_min"] - temp) * 5
            score -= min(penalty, 40)
            risks.append("low_temperature")
        elif temp > conditions["temp_max"]:
            penalty = (temp - conditions["temp_max"]) * 5
            score -= min(penalty, 40)
            risks.append("high_temperature")

        # Humidity scoring
        if humidity < conditions["humidity_min"]:
            penalty = (conditions["humidity_min"] - humidity) * 0.5
            score -= min(penalty, 20)
            risks.append("low_humidity")
        elif humidity > conditions["humidity_max"]:
            penalty = (humidity - conditions["humidity_max"]) * 0.5
            score -= min(penalty, 20)
            risks.append("high_humidity")

        # Wind speed scoring (critical for drift)
        if wind_speed > conditions["wind_max"]:
            penalty = (wind_speed - conditions["wind_max"]) * 3
            score -= min(penalty, 50)
            risks.append("high_wind")
        elif wind_speed < 3:  # Too calm can cause droplet settling
            score -= 5

        # Rain probability scoring (critical for wash-off)
        if rain_prob > conditions["rain_prob_max"]:
            penalty = (rain_prob - conditions["rain_prob_max"]) * 2
            score -= min(penalty, 40)
            risks.append("rain_forecast")

        # Calculate Delta-T if possible (wet bulb depression)
        delta_t = self._calculate_delta_t(temp, humidity)
        if delta_t is not None:
            if delta_t < conditions.get("delta_t_min", 2):
                score -= 15
                risks.append("low_delta_t")
            elif delta_t > conditions.get("delta_t_max", 8):
                score -= 20
                risks.append("high_delta_t")

        # Determine condition level
        score = max(0, min(100, score))

        if score >= 85:
            condition = SprayCondition.EXCELLENT
        elif score >= 70:
            condition = SprayCondition.GOOD
        elif score >= 50:
            condition = SprayCondition.MARGINAL
        elif score >= 30:
            condition = SprayCondition.POOR
        else:
            condition = SprayCondition.DANGEROUS

        return score, condition, risks

    def identify_risks(
        self,
        temp: float,
        humidity: float,
        wind_speed: float,
        rain_prob: float,
        delta_t: Optional[float] = None,
    ) -> List[str]:
        """
        Identify specific risks for current conditions.

        Returns list of risk identifiers:
        - spray_drift: High wind risk
        - wash_off: Rain forecast risk
        - evaporation: Low humidity, high temp
        - poor_absorption: Low humidity
        - phytotoxicity: High temperature
        - reduced_efficacy: Low temperature
        - inversion_risk: Low delta-T (temperature inversion)
        """
        risks = []

        # Spray drift risk
        if wind_speed > 15:
            risks.append("spray_drift")

        # Wash-off risk
        if rain_prob > 20:
            risks.append("wash_off")

        # Evaporation risk (droplets evaporate before reaching target)
        if humidity < 40 and temp > 25:
            risks.append("evaporation")

        # Poor absorption
        if humidity < 50:
            risks.append("poor_absorption")

        # Phytotoxicity (plant damage from heat + chemicals)
        if temp > 30:
            risks.append("phytotoxicity")

        # Reduced efficacy
        if temp < 10:
            risks.append("reduced_efficacy")

        # Temperature inversion risk
        if delta_t is not None and delta_t < 2:
            risks.append("inversion_risk")

        # High delta-T (rapid evaporation)
        if delta_t is not None and delta_t > 8:
            risks.append("high_delta_t")

        return risks

    def get_recommendations(
        self,
        condition: SprayCondition,
        risks: List[str],
        product_type: Optional[SprayProduct] = None,
    ) -> Dict[str, List[str]]:
        """
        Get bilingual recommendations based on conditions.

        Returns:
            Dict with "ar" and "en" keys containing recommendation lists
        """
        recommendations_ar = []
        recommendations_en = []

        # General condition recommendations
        if condition == SprayCondition.EXCELLENT:
            recommendations_ar.append("ظروف ممتازة للرش - المضي قدماً بثقة")
            recommendations_en.append(
                "Excellent conditions for spraying - proceed with confidence"
            )
        elif condition == SprayCondition.GOOD:
            recommendations_ar.append("ظروف جيدة للرش - آمن للمضي قدماً")
            recommendations_en.append("Good conditions for spraying - safe to proceed")
        elif condition == SprayCondition.MARGINAL:
            recommendations_ar.append("ظروف هامشية - توخى الحذر")
            recommendations_en.append("Marginal conditions - exercise caution")
        elif condition == SprayCondition.POOR:
            recommendations_ar.append("ظروف غير موصى بها للرش - فكر في التأجيل")
            recommendations_en.append("Poor conditions - consider postponing")
        else:  # DANGEROUS
            recommendations_ar.append("⚠️ لا ترش! ظروف خطيرة")
            recommendations_en.append("⚠️ DO NOT SPRAY! Dangerous conditions")

        # Risk-specific recommendations
        risk_recommendations = {
            "spray_drift": {
                "ar": "رياح قوية - خطر انجراف الرذاذ إلى مناطق غير مستهدفة",
                "en": "High wind - risk of spray drift to non-target areas",
            },
            "wash_off": {
                "ar": "أمطار متوقعة - قد يتم غسل المبيد قبل الامتصاص",
                "en": "Rain forecast - product may wash off before absorption",
            },
            "evaporation": {
                "ar": "تبخر سريع - قد تجف القطرات قبل الوصول للهدف",
                "en": "Rapid evaporation - droplets may dry before reaching target",
            },
            "poor_absorption": {
                "ar": "رطوبة منخفضة - قد يقل امتصاص النبات للمبيد",
                "en": "Low humidity - reduced plant absorption of product",
            },
            "phytotoxicity": {
                "ar": "حرارة مرتفعة - خطر إتلاف النبات",
                "en": "High temperature - risk of plant damage",
            },
            "reduced_efficacy": {
                "ar": "حرارة منخفضة - فعالية منخفضة للمبيد",
                "en": "Low temperature - reduced product efficacy",
            },
            "inversion_risk": {
                "ar": "خطر انعكاس حراري - قد تعلق القطرات في الهواء",
                "en": "Temperature inversion risk - droplets may suspend in air",
            },
            "low_delta_t": {
                "ar": "دلتا-T منخفض - ظروف غير مستقرة",
                "en": "Low Delta-T - unstable atmospheric conditions",
            },
            "high_delta_t": {
                "ar": "دلتا-T مرتفع - تبخر سريع للقطرات",
                "en": "High Delta-T - rapid droplet evaporation",
            },
            "high_humidity": {
                "ar": "رطوبة عالية - قد يبطئ الجفاف",
                "en": "High humidity - may slow drying",
            },
            "low_humidity": {
                "ar": "رطوبة منخفضة - استخدم مساعدات الالتصاق",
                "en": "Low humidity - use spray adjuvants",
            },
            "high_wind": {
                "ar": "رياح قوية - قلل ضغط الرش أو أجّل",
                "en": "High wind - reduce pressure or postpone",
            },
            "low_temperature": {
                "ar": "حرارة منخفضة - انتظر حتى ترتفع الحرارة",
                "en": "Low temperature - wait for warmer conditions",
            },
            "high_temperature": {
                "ar": "حرارة مرتفعة - ارش في الصباح الباكر أو المساء",
                "en": "High temperature - spray early morning or evening",
            },
            "rain_forecast": {
                "ar": "أمطار متوقعة - انتظر على الأقل ٤ ساعات بدون مطر",
                "en": "Rain forecast - need at least 4 hours without rain",
            },
        }

        for risk in risks:
            if risk in risk_recommendations:
                recommendations_ar.append(risk_recommendations[risk]["ar"])
                recommendations_en.append(risk_recommendations[risk]["en"])

        # Product-specific recommendations
        if product_type == SprayProduct.HERBICIDE:
            if "low_humidity" in risks:
                recommendations_ar.append(
                    "مبيدات الأعشاب: أضف مساعد التصاق لتحسين الامتصاص"
                )
                recommendations_en.append(
                    "Herbicides: Add surfactant to improve absorption"
                )
        elif product_type == SprayProduct.FUNGICIDE:
            if "high_humidity" in risks:
                recommendations_ar.append(
                    "مبيدات الفطريات: الرطوبة العالية قد تزيد انتشار الجراثيم"
                )
                recommendations_en.append(
                    "Fungicides: High humidity may increase spore spread"
                )
        elif product_type == SprayProduct.INSECTICIDE:
            if "high_temperature" in risks:
                recommendations_ar.append(
                    "مبيدات الحشرات: ارش عند غروب الشمس للحصول على أفضل نتيجة"
                )
                recommendations_en.append(
                    "Insecticides: Spray at dusk for best contact with insects"
                )

        # Safety reminders
        if condition in [
            SprayCondition.MARGINAL,
            SprayCondition.POOR,
            SprayCondition.DANGEROUS,
        ]:
            recommendations_ar.append("ارتدِ معدات الحماية الشخصية دائماً")
            recommendations_en.append("Always wear personal protective equipment")

        return {"ar": recommendations_ar, "en": recommendations_en}

    async def _fetch_hourly_forecast(
        self, latitude: float, longitude: float, days: int
    ) -> List[Dict]:
        """
        Fetch hourly weather forecast from Open-Meteo.

        Returns list of hourly data points with:
        - time, temp, humidity, wind_speed, precipitation_prob
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "precipitation_probability",
                "precipitation",
            ],
            "forecast_days": days,
            "timezone": "auto",
        }

        try:
            url = f"{self.BASE_URL}/forecast"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Parse hourly data
            hourly_data = []
            hourly_times = data.get("hourly", {}).get("time", [])
            hourly_temp = data.get("hourly", {}).get("temperature_2m", [])
            hourly_humidity = data.get("hourly", {}).get("relative_humidity_2m", [])
            hourly_wind = data.get("hourly", {}).get("wind_speed_10m", [])
            hourly_precip_prob = data.get("hourly", {}).get(
                "precipitation_probability", []
            )
            hourly_precip = data.get("hourly", {}).get("precipitation", [])

            for i in range(len(hourly_times)):
                hourly_data.append(
                    {
                        "time": datetime.fromisoformat(hourly_times[i]),
                        "temp": hourly_temp[i] if i < len(hourly_temp) else 20,
                        "humidity": (
                            hourly_humidity[i] if i < len(hourly_humidity) else 60
                        ),
                        "wind_speed": (
                            hourly_wind[i] * 3.6 if i < len(hourly_wind) else 0
                        ),  # m/s to km/h
                        "precipitation_prob": (
                            hourly_precip_prob[i] if i < len(hourly_precip_prob) else 0
                        ),
                        "precipitation": (
                            hourly_precip[i] if i < len(hourly_precip) else 0
                        ),
                    }
                )

            return hourly_data

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch hourly forecast: {e}")
            raise Exception(f"Weather API error: {str(e)}")

    def _group_by_day(self, hourly_data: List[Dict]) -> Dict[date, List[Dict]]:
        """Group hourly data by day"""
        grouped = {}
        for hour in hourly_data:
            day = hour["time"].date()
            if day not in grouped:
                grouped[day] = []
            grouped[day].append(hour)
        return grouped

    def _identify_spray_windows(
        self, hours: List[Dict], product_type: Optional[SprayProduct]
    ) -> List[SprayWindow]:
        """
        Identify spray windows from hourly data for a single day.

        A spray window is a continuous period of suitable conditions
        during daylight hours (6 AM - 6 PM).
        """
        windows = []
        current_window_hours = []

        for hour in hours:
            # Only consider daylight hours (6 AM - 6 PM)
            hour_of_day = hour["time"].hour
            if hour_of_day < 6 or hour_of_day >= 18:
                continue

            # Calculate score for this hour
            score, condition, risks = self.calculate_spray_score(
                hour["temp"],
                hour["humidity"],
                hour["wind_speed"],
                hour["precipitation_prob"],
                product_type,
            )

            # Check if this hour is suitable (score >= 50)
            if score >= 50:
                current_window_hours.append(
                    {
                        "hour": hour,
                        "score": score,
                        "condition": condition,
                        "risks": risks,
                    }
                )
            else:
                # End current window if exists
                if current_window_hours:
                    windows.append(
                        self._create_window(current_window_hours, product_type)
                    )
                    current_window_hours = []

        # Add last window if exists
        if current_window_hours:
            windows.append(self._create_window(current_window_hours, product_type))

        return windows

    def _create_window(
        self, window_hours: List[Dict], product_type: Optional[SprayProduct]
    ) -> SprayWindow:
        """Create SprayWindow from continuous suitable hours"""
        start_time = window_hours[0]["hour"]["time"]
        end_time = window_hours[-1]["hour"]["time"] + timedelta(hours=1)
        duration = len(window_hours)

        # Calculate averages
        avg_temp = sum(h["hour"]["temp"] for h in window_hours) / len(window_hours)
        avg_humidity = sum(h["hour"]["humidity"] for h in window_hours) / len(
            window_hours
        )
        avg_wind = sum(h["hour"]["wind_speed"] for h in window_hours) / len(
            window_hours
        )
        avg_precip_prob = sum(
            h["hour"]["precipitation_prob"] for h in window_hours
        ) / len(window_hours)

        # Overall score and condition (use best hour)
        best_hour = max(window_hours, key=lambda h: h["score"])
        score = best_hour["score"]
        condition = best_hour["condition"]

        # Aggregate risks
        all_risks = set()
        for h in window_hours:
            all_risks.update(h["risks"])
        risks = list(all_risks)

        # Get recommendations
        recommendations = self.get_recommendations(condition, risks, product_type)

        return SprayWindow(
            start_time=start_time,
            end_time=end_time,
            duration_hours=duration,
            condition=condition,
            score=score,
            temp_avg=avg_temp,
            humidity_avg=avg_humidity,
            wind_speed_avg=avg_wind,
            precipitation_prob=avg_precip_prob,
            risks=risks,
            recommendations_ar=recommendations["ar"],
            recommendations_en=recommendations["en"],
        )

    def _calculate_delta_t(self, temp: float, humidity: float) -> Optional[float]:
        """
        Calculate Delta-T (wet bulb depression).

        Delta-T = Dry bulb temp - Wet bulb temp

        Optimal Delta-T for spraying: 2-8°C
        - < 2°C: Temperature inversion risk
        - 2-8°C: Ideal conditions
        - > 8°C: Rapid evaporation

        Uses simplified approximation formula.
        """
        try:
            # Simplified wet bulb calculation (approximation)
            # More accurate methods exist but require atmospheric pressure

            # Calculate wet bulb using simplified formula
            # Tw = T * arctan(0.151977 * sqrt(RH + 8.313659))
            #      + arctan(T + RH) - arctan(RH - 1.676331)
            #      + 0.00391838 * RH^(3/2) * arctan(0.023101 * RH)
            #      - 4.686035

            # Even simpler approximation for agricultural purposes:
            # Tw ≈ T * arctan(0.151977 * (RH% + 8.313659)^0.5)
            #      + arctan(T + RH%) - arctan(RH% - 1.676331)
            #      + 0.00391838 * (RH%)^1.5 * arctan(0.023101 * RH%)
            #      - 4.686035

            # For simplicity, use empirical approximation:
            # Delta-T ≈ (100 - RH) / 5  when RH is in %
            # This is a rough approximation but useful for field use

            if humidity >= 100:
                return 0

            # Simple approximation
            delta_t = (100 - humidity) / 5

            return round(delta_t, 1)

        except Exception as e:
            logger.warning(f"Failed to calculate Delta-T: {e}")
            return None


# Global instance
_spray_advisor = None


def get_spray_advisor() -> SprayAdvisor:
    """Get global spray advisor instance"""
    global _spray_advisor
    if _spray_advisor is None:
        _spray_advisor = SprayAdvisor()
    return _spray_advisor
