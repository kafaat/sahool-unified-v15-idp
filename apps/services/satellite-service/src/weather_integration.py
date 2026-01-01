"""
SAHOOL Weather Integration - Open-Meteo API
تكامل الطقس - Open-Meteo API

Free weather data for crop modeling and irrigation scheduling:
- 7-day forecast with ET0 (evapotranspiration)
- Historical weather back to 1940
- Growing Degree Days (GDD) calculation
- Water balance (precipitation vs ET)
- Frost risk monitoring for Yemen highlands
- Irrigation recommendations

Based on Open-Meteo free API: https://open-meteo.com
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import httpx
import logging

logger = logging.getLogger(__name__)

# Import crop catalog for Kc values
import sys

sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
try:
    from apps.services.shared.crops import get_crop
except ImportError:

    def get_crop(code: str):
        return None


@dataclass
class WeatherData:
    """Daily weather data point"""

    timestamp: datetime
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    precipitation_mm: float
    humidity_percent: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    solar_radiation_wm2: Optional[float] = None
    et0_mm: Optional[float] = None  # Reference evapotranspiration

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature_c": round(self.temperature_c, 1),
            "temperature_min_c": round(self.temperature_min_c, 1),
            "temperature_max_c": round(self.temperature_max_c, 1),
            "precipitation_mm": round(self.precipitation_mm, 2),
            "humidity_percent": (
                round(self.humidity_percent, 1) if self.humidity_percent else None
            ),
            "wind_speed_ms": (
                round(self.wind_speed_ms, 2) if self.wind_speed_ms else None
            ),
            "solar_radiation_wm2": (
                round(self.solar_radiation_wm2, 1) if self.solar_radiation_wm2 else None
            ),
            "et0_mm": round(self.et0_mm, 2) if self.et0_mm else None,
        }


@dataclass
class WeatherForecast:
    """Weather forecast for a location"""

    location: Dict[str, float]  # {"lat": ..., "lon": ...}
    generated_at: datetime
    daily: List[WeatherData]
    hourly: Optional[List[WeatherData]] = None

    def to_dict(self) -> Dict:
        return {
            "location": self.location,
            "generated_at": self.generated_at.isoformat(),
            "forecast_days": len(self.daily),
            "daily": [d.to_dict() for d in self.daily],
            "hourly": [h.to_dict() for h in self.hourly] if self.hourly else None,
        }


@dataclass
class HistoricalWeather:
    """Historical weather data"""

    location: Dict[str, float]
    start_date: date
    end_date: date
    daily: List[WeatherData]
    summary: Dict  # avg_temp, total_precip, total_et0, gdd

    def to_dict(self) -> Dict:
        return {
            "location": self.location,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "days": len(self.daily),
            "daily": [d.to_dict() for d in self.daily],
            "summary": self.summary,
        }


@dataclass
class FrostRisk:
    """Frost risk assessment"""

    date: date
    min_temp_c: float
    frost_probability: float  # 0-1
    risk_level: str  # "none", "low", "moderate", "high", "severe"
    recommendation_ar: str
    recommendation_en: str

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "min_temp_c": round(self.min_temp_c, 1),
            "frost_probability": round(self.frost_probability, 3),
            "risk_level": self.risk_level,
            "recommendation_ar": self.recommendation_ar,
            "recommendation_en": self.recommendation_en,
        }


@dataclass
class IrrigationRecommendation:
    """Irrigation recommendation based on weather and ET0"""

    field_id: Optional[str]
    crop_type: str
    crop_name_ar: str
    crop_name_en: str
    growth_stage: str
    recommendation_date: datetime
    water_requirement_mm: float  # Daily crop water requirement (ETc)
    precipitation_forecast_mm: float  # Next 7 days
    irrigation_needed_mm: float  # Deficit to cover
    irrigation_frequency_days: int
    recommendation_ar: str
    recommendation_en: str
    confidence: float  # 0-1

    def to_dict(self) -> Dict:
        return {
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "crop_name_ar": self.crop_name_ar,
            "crop_name_en": self.crop_name_en,
            "growth_stage": self.growth_stage,
            "recommendation_date": self.recommendation_date.isoformat(),
            "water_requirement_mm": round(self.water_requirement_mm, 1),
            "precipitation_forecast_mm": round(self.precipitation_forecast_mm, 1),
            "irrigation_needed_mm": round(self.irrigation_needed_mm, 1),
            "irrigation_frequency_days": self.irrigation_frequency_days,
            "recommendation_ar": self.recommendation_ar,
            "recommendation_en": self.recommendation_en,
            "confidence": round(self.confidence, 3),
        }


class WeatherIntegration:
    """
    Integration with Open-Meteo free weather API.
    Provides weather data for crop modeling and irrigation scheduling.

    Free API with no authentication required.
    Rate limit: 10,000 requests/day per IP
    """

    BASE_URL = "https://api.open-meteo.com/v1"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1"

    # Growth stage to Kc mapping (crop coefficient for water requirement)
    GROWTH_STAGE_KC = {
        "initial": 0.5,  # germination/establishment
        "development": 0.7,  # vegetative growth
        "mid": 1.0,  # flowering/peak growth
        "late": 0.8,  # ripening/maturation
        "harvest": 0.6,  # pre-harvest
    }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> WeatherForecast:
        """
        Get weather forecast for next N days.
        Includes ET0 for irrigation planning.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of forecast days (1-16)

        Returns:
            WeatherForecast with daily and hourly data
        """
        days = min(max(days, 1), 16)  # Open-Meteo supports up to 16 days

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "et0_fao_evapotranspiration",
                "sunrise",
                "sunset",
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "shortwave_radiation",
            ],
            "forecast_days": days,
            "timezone": "Asia/Aden",  # Yemen timezone
        }

        try:
            url = f"{self.BASE_URL}/forecast"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Parse daily data
            daily_data = []
            daily_times = data.get("daily", {}).get("time", [])
            daily_temp_max = data.get("daily", {}).get("temperature_2m_max", [])
            daily_temp_min = data.get("daily", {}).get("temperature_2m_min", [])
            daily_temp_mean = data.get("daily", {}).get("temperature_2m_mean", [])
            daily_precip = data.get("daily", {}).get("precipitation_sum", [])
            daily_et0 = data.get("daily", {}).get("et0_fao_evapotranspiration", [])

            for i in range(len(daily_times)):
                daily_data.append(
                    WeatherData(
                        timestamp=datetime.fromisoformat(daily_times[i]),
                        temperature_c=(
                            daily_temp_mean[i]
                            if i < len(daily_temp_mean)
                            else (daily_temp_max[i] + daily_temp_min[i]) / 2
                        ),
                        temperature_min_c=(
                            daily_temp_min[i] if i < len(daily_temp_min) else 0
                        ),
                        temperature_max_c=(
                            daily_temp_max[i] if i < len(daily_temp_max) else 0
                        ),
                        precipitation_mm=(
                            daily_precip[i] if i < len(daily_precip) else 0
                        ),
                        et0_mm=daily_et0[i] if i < len(daily_et0) else None,
                    )
                )

            # Parse hourly data (optional, for detailed analysis)
            hourly_data = []
            hourly_times = data.get("hourly", {}).get("time", [])
            hourly_temp = data.get("hourly", {}).get("temperature_2m", [])
            hourly_humidity = data.get("hourly", {}).get("relative_humidity_2m", [])
            hourly_precip = data.get("hourly", {}).get("precipitation", [])
            hourly_wind = data.get("hourly", {}).get("wind_speed_10m", [])
            hourly_solar = data.get("hourly", {}).get("shortwave_radiation", [])

            for i in range(len(hourly_times)):
                hourly_data.append(
                    WeatherData(
                        timestamp=datetime.fromisoformat(hourly_times[i]),
                        temperature_c=hourly_temp[i] if i < len(hourly_temp) else 0,
                        temperature_min_c=hourly_temp[i] if i < len(hourly_temp) else 0,
                        temperature_max_c=hourly_temp[i] if i < len(hourly_temp) else 0,
                        precipitation_mm=(
                            hourly_precip[i] if i < len(hourly_precip) else 0
                        ),
                        humidity_percent=(
                            hourly_humidity[i] if i < len(hourly_humidity) else None
                        ),
                        wind_speed_ms=hourly_wind[i] if i < len(hourly_wind) else None,
                        solar_radiation_wm2=(
                            hourly_solar[i] if i < len(hourly_solar) else None
                        ),
                    )
                )

            return WeatherForecast(
                location={"lat": latitude, "lon": longitude},
                generated_at=datetime.utcnow(),
                daily=daily_data,
                hourly=hourly_data if hourly_data else None,
            )

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch forecast: {e}")
            raise Exception(f"Weather API error: {str(e)}")

    async def get_historical(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> HistoricalWeather:
        """
        Get historical weather data for analysis.
        Available from 1940 to ~7 days ago.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            HistoricalWeather with daily data and summary statistics
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "et0_fao_evapotranspiration",
            ],
            "timezone": "Asia/Aden",
        }

        try:
            url = f"{self.ARCHIVE_URL}/archive"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Parse daily data
            daily_data = []
            daily_times = data.get("daily", {}).get("time", [])
            daily_temp_max = data.get("daily", {}).get("temperature_2m_max", [])
            daily_temp_min = data.get("daily", {}).get("temperature_2m_min", [])
            daily_temp_mean = data.get("daily", {}).get("temperature_2m_mean", [])
            daily_precip = data.get("daily", {}).get("precipitation_sum", [])
            daily_et0 = data.get("daily", {}).get("et0_fao_evapotranspiration", [])

            for i in range(len(daily_times)):
                daily_data.append(
                    WeatherData(
                        timestamp=datetime.fromisoformat(daily_times[i]),
                        temperature_c=(
                            daily_temp_mean[i]
                            if i < len(daily_temp_mean)
                            else (daily_temp_max[i] + daily_temp_min[i]) / 2
                        ),
                        temperature_min_c=(
                            daily_temp_min[i] if i < len(daily_temp_min) else 0
                        ),
                        temperature_max_c=(
                            daily_temp_max[i] if i < len(daily_temp_max) else 0
                        ),
                        precipitation_mm=(
                            daily_precip[i] if i < len(daily_precip) else 0
                        ),
                        et0_mm=daily_et0[i] if i < len(daily_et0) else None,
                    )
                )

            # Calculate summary statistics
            temps = [d.temperature_c for d in daily_data]
            precips = [d.precipitation_mm for d in daily_data]
            et0s = [d.et0_mm for d in daily_data if d.et0_mm is not None]

            # Calculate GDD (Growing Degree Days) with base temp 10°C
            gdd = sum(max(0, d.temperature_c - 10.0) for d in daily_data)

            summary = {
                "avg_temp_c": round(sum(temps) / len(temps), 1) if temps else 0,
                "min_temp_c": round(min(temps), 1) if temps else 0,
                "max_temp_c": round(max(temps), 1) if temps else 0,
                "total_precipitation_mm": round(sum(precips), 1),
                "avg_daily_precipitation_mm": (
                    round(sum(precips) / len(precips), 2) if precips else 0
                ),
                "total_et0_mm": round(sum(et0s), 1) if et0s else None,
                "avg_daily_et0_mm": round(sum(et0s) / len(et0s), 2) if et0s else None,
                "gdd_base_10": round(gdd, 1),
                "days": len(daily_data),
            }

            return HistoricalWeather(
                location={"lat": latitude, "lon": longitude},
                start_date=start_date,
                end_date=end_date,
                daily=daily_data,
                summary=summary,
            )

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise Exception(f"Weather API error: {str(e)}")

    async def get_growing_degree_days(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        base_temp: float = 10.0,
    ) -> float:
        """
        Calculate accumulated Growing Degree Days (GDD).
        GDD = Σ(max(0, (Tmax + Tmin) / 2 - Tbase)) for each day

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date
            end_date: End date
            base_temp: Base temperature (default 10°C for most crops)

        Returns:
            Total accumulated GDD
        """
        # Get historical data
        historical = await self.get_historical(
            latitude, longitude, start_date, end_date
        )

        # Calculate GDD
        gdd = 0.0
        for day in historical.daily:
            avg_temp = (day.temperature_max_c + day.temperature_min_c) / 2
            gdd += max(0, avg_temp - base_temp)

        return round(gdd, 1)

    async def get_water_balance(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
        kc: float = 1.0,
    ) -> Dict:
        """
        Calculate water balance: Precipitation - ET0 * Kc
        Returns deficit/surplus in mm.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date
            end_date: End date
            kc: Crop coefficient (default 1.0)

        Returns:
            Dict with water balance analysis
        """
        # Get historical data
        historical = await self.get_historical(
            latitude, longitude, start_date, end_date
        )

        # Calculate water balance
        total_precipitation = 0.0
        total_etc = 0.0  # Crop evapotranspiration (ET0 * Kc)
        daily_balance = []

        for day in historical.daily:
            precip = day.precipitation_mm
            et0 = day.et0_mm if day.et0_mm is not None else 0
            etc = et0 * kc
            balance = precip - etc

            total_precipitation += precip
            total_etc += etc

            daily_balance.append(
                {
                    "date": day.timestamp.date().isoformat(),
                    "precipitation_mm": round(precip, 2),
                    "etc_mm": round(etc, 2),
                    "balance_mm": round(balance, 2),
                }
            )

        total_balance = total_precipitation - total_etc

        # Determine status
        if total_balance > 50:
            status = "surplus"
            status_ar = "فائض مائي"
        elif total_balance > -50:
            status = "balanced"
            status_ar = "متوازن"
        else:
            status = "deficit"
            status_ar = "عجز مائي"

        return {
            "location": historical.location,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": len(historical.daily),
            },
            "kc": kc,
            "summary": {
                "total_precipitation_mm": round(total_precipitation, 1),
                "total_etc_mm": round(total_etc, 1),
                "total_balance_mm": round(total_balance, 1),
                "avg_daily_precipitation_mm": round(
                    total_precipitation / len(historical.daily), 2
                ),
                "avg_daily_etc_mm": round(total_etc / len(historical.daily), 2),
                "status": status,
                "status_ar": status_ar,
            },
            "daily_balance": daily_balance,
        }

    async def get_irrigation_recommendation(
        self,
        latitude: float,
        longitude: float,
        crop_type: str,
        growth_stage: str,
        soil_moisture: Optional[float] = None,
        field_id: Optional[str] = None,
    ) -> IrrigationRecommendation:
        """
        Get irrigation recommendation based on weather and ET0.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            crop_type: Crop code (e.g., "WHEAT", "TOMATO")
            growth_stage: Growth stage (initial, development, mid, late, harvest)
            soil_moisture: Current soil moisture (0-1), optional
            field_id: Field identifier, optional

        Returns:
            IrrigationRecommendation with water requirements and advice
        """
        # Get crop info
        crop_info = get_crop(crop_type)
        if crop_info:
            crop_name_ar = crop_info.name_ar
            crop_name_en = crop_info.name_en

            # Get Kc for growth stage
            if growth_stage == "initial" or growth_stage == "germination":
                kc = crop_info.kc_initial or 0.5
            elif (
                growth_stage == "mid"
                or growth_stage == "flowering"
                or growth_stage == "fruiting"
            ):
                kc = crop_info.kc_mid or 1.0
            elif growth_stage == "late" or growth_stage == "ripening":
                kc = crop_info.kc_end or 0.8
            else:
                kc = self.GROWTH_STAGE_KC.get(growth_stage.lower(), 1.0)
        else:
            crop_name_ar = crop_type
            crop_name_en = crop_type
            kc = self.GROWTH_STAGE_KC.get(growth_stage.lower(), 1.0)

        # Get 7-day forecast
        forecast = await self.get_forecast(latitude, longitude, days=7)

        # Calculate water requirements
        total_et0 = sum(day.et0_mm for day in forecast.daily if day.et0_mm is not None)
        total_etc = total_et0 * kc  # Crop water requirement
        total_precip = sum(day.precipitation_mm for day in forecast.daily)

        irrigation_needed = max(0, total_etc - total_precip)

        # Adjust for soil moisture
        if soil_moisture is not None:
            if soil_moisture > 0.6:
                # Soil is wet, reduce irrigation
                irrigation_needed *= 0.7
            elif soil_moisture < 0.3:
                # Soil is dry, increase irrigation
                irrigation_needed *= 1.2

        # Calculate irrigation frequency
        if irrigation_needed < 10:
            freq_days = 7
            recommendation_en = f"Minimal irrigation needed. Monitor soil moisture."
            recommendation_ar = f"حاجة ري ضئيلة. راقب رطوبة التربة."
        elif irrigation_needed < 30:
            freq_days = 5
            recommendation_en = f"Light irrigation recommended every {freq_days} days."
            recommendation_ar = f"ري خفيف موصى به كل {freq_days} أيام."
        elif irrigation_needed < 50:
            freq_days = 3
            recommendation_en = f"Moderate irrigation needed every {freq_days} days."
            recommendation_ar = f"ري معتدل مطلوب كل {freq_days} أيام."
        else:
            freq_days = 2
            recommendation_en = f"Heavy irrigation required every {freq_days} days due to high water demand."
            recommendation_ar = (
                f"ري كثيف مطلوب كل {freq_days} أيام بسبب الطلب المائي العالي."
            )

        # Add growth stage specific advice
        if growth_stage in ["flowering", "mid"]:
            recommendation_en += " Critical stage - maintain consistent moisture."
            recommendation_ar += " مرحلة حرجة - حافظ على رطوبة ثابتة."
        elif growth_stage in ["ripening", "late"]:
            recommendation_en += " Reduce irrigation gradually as harvest approaches."
            recommendation_ar += " قلل الري تدريجياً مع اقتراب الحصاد."

        # Confidence based on forecast quality and soil moisture data
        confidence = 0.8
        if soil_moisture is not None:
            confidence += 0.1
        if total_precip < 5:  # Low expected rain = more certain irrigation need
            confidence += 0.05
        confidence = min(1.0, confidence)

        return IrrigationRecommendation(
            field_id=field_id,
            crop_type=crop_type,
            crop_name_ar=crop_name_ar,
            crop_name_en=crop_name_en,
            growth_stage=growth_stage,
            recommendation_date=datetime.utcnow(),
            water_requirement_mm=total_etc,
            precipitation_forecast_mm=total_precip,
            irrigation_needed_mm=irrigation_needed,
            irrigation_frequency_days=freq_days,
            recommendation_ar=recommendation_ar,
            recommendation_en=recommendation_en,
            confidence=confidence,
        )

    async def get_frost_risk(
        self, latitude: float, longitude: float, days: int = 7
    ) -> List[FrostRisk]:
        """
        Assess frost risk for next N days.
        Important for Yemen highlands (Sanaa, Ibb, Dhamar).

        Frost risk levels:
        - Severe: < -2°C (95%+ probability)
        - High: -2°C to 0°C (70-95% probability)
        - Moderate: 0°C to 2°C (40-70% probability)
        - Low: 2°C to 5°C (10-40% probability)
        - None: > 5°C (<10% probability)

        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of forecast days

        Returns:
            List of FrostRisk assessments
        """
        # Get forecast
        forecast = await self.get_forecast(latitude, longitude, days=days)

        frost_risks = []

        for day in forecast.daily:
            min_temp = day.temperature_min_c

            # Calculate frost probability and risk level
            if min_temp < -2:
                probability = 0.95
                risk_level = "severe"
                rec_ar = "خطر صقيع شديد! احمِ المحاصيل فوراً بالأغطية أو التدفئة"
                rec_en = "Severe frost risk! Protect crops immediately with covers or heating"
            elif min_temp < 0:
                probability = 0.80
                risk_level = "high"
                rec_ar = "خطر صقيع مرتفع - احمِ المحاصيل الحساسة بالأغطية"
                rec_en = "High frost risk - protect sensitive crops with covers"
            elif min_temp < 2:
                probability = 0.55
                risk_level = "moderate"
                rec_ar = "خطر صقيع معتدل - راقب المحاصيل وجهّز الحماية"
                rec_en = "Moderate frost risk - monitor crops and prepare protection"
            elif min_temp < 5:
                probability = 0.25
                risk_level = "low"
                rec_ar = "خطر صقيع منخفض - راقب التوقعات"
                rec_en = "Low frost risk - monitor forecasts"
            else:
                probability = 0.05
                risk_level = "none"
                rec_ar = "لا يوجد خطر صقيع"
                rec_en = "No frost risk"

            frost_risks.append(
                FrostRisk(
                    date=day.timestamp.date(),
                    min_temp_c=min_temp,
                    frost_probability=probability,
                    risk_level=risk_level,
                    recommendation_ar=rec_ar,
                    recommendation_en=rec_en,
                )
            )

        return frost_risks


# Global instance
_weather_service = None


def get_weather_service() -> WeatherIntegration:
    """Get global weather service instance"""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherIntegration()
    return _weather_service
