"""
🌤️ SAHOOL Advanced Weather Service v15.4
خدمة الطقس المتقدمة - 7-Day Forecasting & Agricultural Alerts
Real Weather API Integration: Open-Meteo & OpenWeatherMap

⚠️ DEPRECATED: This service is deprecated and will be removed in a future release.
Please use 'weather-service' instead.
"""

import logging
import math
import os
import uuid
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query, Request

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

from errors_py import setup_exception_handlers, add_request_id_middleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather API Configuration
WEATHER_API_PROVIDER = os.getenv(
    "WEATHER_API_PROVIDER", "open-meteo"
)  # open-meteo, openweathermap
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
WEATHER_CACHE_TTL_MINUTES = int(os.getenv("WEATHER_CACHE_TTL_MINUTES", "30"))

# Weather data cache
_weather_cache: dict[str, dict[str, Any]] = {}

app = FastAPI(
    title="SAHOOL Advanced Weather Service | خدمة الطقس المتقدمة",
    version="15.4.0",
    description="⚠️ DEPRECATED - Use weather-service instead. 7-day forecasting with real weather APIs, agricultural weather alerts, and crop-specific recommendations",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)


@app.on_event("startup")
async def startup_event():
    """Log deprecation warning on startup"""
    logger.warning("=" * 80)
    logger.warning("⚠️  DEPRECATION WARNING")
    logger.warning("=" * 80)
    logger.warning(
        "This service (weather-advanced) is DEPRECATED and will be removed in a future release."
    )
    logger.warning("Please migrate to 'weather-service' instead.")
    logger.warning("Replacement service: weather-service")
    logger.warning("Deprecation date: 2025-01-01")
    logger.warning("=" * 80)


@app.middleware("http")
async def add_deprecation_header(request: Request, call_next):
    """Add deprecation headers to all responses"""
    response = await call_next(request)
    response.headers["X-API-Deprecated"] = "true"
    response.headers["X-API-Deprecation-Date"] = "2025-01-01"
    response.headers["X-API-Deprecation-Info"] = (
        "This service is deprecated. Use weather-service instead."
    )
    response.headers["X-API-Sunset"] = "2025-06-01"
    response.headers["Link"] = '<http://weather-service:8108>; rel="successor-version"'
    response.headers["Deprecation"] = "true"
    return response


# =============================================================================
# Enums & Models
# =============================================================================


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    DUST = "dust"
    FOG = "fog"
    HAZE = "haze"


class AlertType(str, Enum):
    HEAT_WAVE = "heat_wave"
    FROST = "frost"
    HEAVY_RAIN = "heavy_rain"
    DROUGHT = "drought"
    HIGH_WIND = "high_wind"
    HIGH_HUMIDITY = "high_humidity"
    LOW_HUMIDITY = "low_humidity"
    DUST_STORM = "dust_storm"


class AlertSeverity(str, Enum):
    ADVISORY = "advisory"
    WATCH = "watch"
    WARNING = "warning"
    EMERGENCY = "emergency"


class HourlyForecast(BaseModel):
    datetime: datetime
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    wind_speed_kmh: float
    wind_direction: str
    precipitation_mm: float
    precipitation_probability: float
    cloud_cover_percent: float
    uv_index: float
    condition: WeatherCondition
    condition_ar: str


class DailyForecast(BaseModel):
    date: date
    temp_max_c: float
    temp_min_c: float
    humidity_avg: float
    wind_speed_avg_kmh: float
    precipitation_total_mm: float
    precipitation_probability: float
    sunrise: str
    sunset: str
    uv_index_max: float
    condition: WeatherCondition
    condition_ar: str
    agricultural_summary_ar: str
    agricultural_summary_en: str


class CurrentWeather(BaseModel):
    location_id: str
    location_name_ar: str
    latitude: float
    longitude: float
    timestamp: datetime
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction: str
    wind_gust_kmh: float
    visibility_km: float
    cloud_cover_percent: float
    uv_index: float
    dew_point_c: float
    condition: WeatherCondition
    condition_ar: str


class WeatherAlert(BaseModel):
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    start_time: datetime
    end_time: datetime
    affected_crops_ar: list[str]
    recommendations_ar: list[str]
    recommendations_en: list[str]


class AgriculturalWeatherReport(BaseModel):
    location_id: str
    location_name_ar: str
    generated_at: datetime
    current: CurrentWeather
    hourly_forecast: list[HourlyForecast]
    daily_forecast: list[DailyForecast]
    alerts: list[WeatherAlert]
    growing_degree_days: float
    evapotranspiration_mm: float
    spray_window_hours: list[str]
    irrigation_recommendation_ar: str
    irrigation_recommendation_en: str


# =============================================================================
# Yemen Locations & Weather Data
# =============================================================================

# جميع محافظات اليمن الـ 22 - All 22 Yemen Governorates
YEMEN_LOCATIONS = {
    # المنطقة الشمالية - Northern Region
    "sanaa": {
        "lat": 15.3694,
        "lon": 44.1910,
        "name_ar": "صنعاء",
        "elevation": 2250,
        "region": "highland",
    },
    "amanat_al_asimah": {
        "lat": 15.3556,
        "lon": 44.2067,
        "name_ar": "أمانة العاصمة",
        "elevation": 2200,
        "region": "highland",
    },
    "amran": {
        "lat": 15.6594,
        "lon": 43.9439,
        "name_ar": "عمران",
        "elevation": 2300,
        "region": "highland",
    },
    "saadah": {
        "lat": 16.9400,
        "lon": 43.7614,
        "name_ar": "صعدة",
        "elevation": 1850,
        "region": "highland",
    },
    "al_jawf": {
        "lat": 16.5833,
        "lon": 45.5000,
        "name_ar": "الجوف",
        "elevation": 1200,
        "region": "desert",
    },
    "hajjah": {
        "lat": 15.6917,
        "lon": 43.6028,
        "name_ar": "حجة",
        "elevation": 1800,
        "region": "highland",
    },
    "al_mahwit": {
        "lat": 15.4700,
        "lon": 43.5447,
        "name_ar": "المحويت",
        "elevation": 2100,
        "region": "highland",
    },
    # المنطقة الوسطى - Central Region
    "dhamar": {
        "lat": 14.5500,
        "lon": 44.4000,
        "name_ar": "ذمار",
        "elevation": 2400,
        "region": "highland",
    },
    "ibb": {
        "lat": 13.9667,
        "lon": 44.1667,
        "name_ar": "إب",
        "elevation": 2050,
        "region": "highland",
    },
    "taiz": {
        "lat": 13.5789,
        "lon": 44.0219,
        "name_ar": "تعز",
        "elevation": 1400,
        "region": "highland",
    },
    "al_bayda": {
        "lat": 13.9833,
        "lon": 45.5667,
        "name_ar": "البيضاء",
        "elevation": 2250,
        "region": "highland",
    },
    "raymah": {
        "lat": 14.6333,
        "lon": 43.7167,
        "name_ar": "ريمة",
        "elevation": 2600,
        "region": "highland",
    },
    "marib": {
        "lat": 15.4667,
        "lon": 45.3500,
        "name_ar": "مأرب",
        "elevation": 1100,
        "region": "desert",
    },
    # المنطقة الساحلية الغربية - Western Coastal Region
    "hodeidah": {
        "lat": 14.7979,
        "lon": 42.9540,
        "name_ar": "الحديدة",
        "elevation": 12,
        "region": "coastal",
    },
    # المنطقة الجنوبية - Southern Region
    "aden": {
        "lat": 12.7855,
        "lon": 45.0187,
        "name_ar": "عدن",
        "elevation": 6,
        "region": "coastal",
    },
    "lahij": {
        "lat": 13.0500,
        "lon": 44.8833,
        "name_ar": "لحج",
        "elevation": 150,
        "region": "highland",
    },
    "ad_dali": {
        "lat": 13.7000,
        "lon": 44.7333,
        "name_ar": "الضالع",
        "elevation": 1500,
        "region": "highland",
    },
    "abyan": {
        "lat": 13.0167,
        "lon": 45.3667,
        "name_ar": "أبين",
        "elevation": 50,
        "region": "coastal",
    },
    # المنطقة الشرقية - Eastern Region
    "hadramaut": {
        "lat": 15.9500,
        "lon": 48.7833,
        "name_ar": "حضرموت",
        "elevation": 650,
        "region": "desert",
    },
    "shabwah": {
        "lat": 14.5333,
        "lon": 46.8333,
        "name_ar": "شبوة",
        "elevation": 900,
        "region": "desert",
    },
    "al_mahrah": {
        "lat": 16.0667,
        "lon": 52.2333,
        "name_ar": "المهرة",
        "elevation": 200,
        "region": "coastal",
    },
    # الجزر - Islands
    "socotra": {
        "lat": 12.4634,
        "lon": 53.8237,
        "name_ar": "سقطرى",
        "elevation": 250,
        "region": "island",
    },
}

CONDITION_TRANSLATIONS = {
    WeatherCondition.CLEAR: "صافي",
    WeatherCondition.PARTLY_CLOUDY: "غائم جزئياً",
    WeatherCondition.CLOUDY: "غائم",
    WeatherCondition.RAIN: "ممطر",
    WeatherCondition.HEAVY_RAIN: "أمطار غزيرة",
    WeatherCondition.THUNDERSTORM: "عواصف رعدية",
    WeatherCondition.DUST: "غبار",
    WeatherCondition.FOG: "ضباب",
    WeatherCondition.HAZE: "ضباب خفيف",
}

WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
WIND_DIRECTIONS_AR = {
    "N": "شمال",
    "NE": "شمال شرق",
    "E": "شرق",
    "SE": "جنوب شرق",
    "S": "جنوب",
    "SW": "جنوب غرب",
    "W": "غرب",
    "NW": "شمال غرب",
}


# =============================================================================
# Real Weather API Integration - تكامل API الطقس الحقيقي
# =============================================================================

# Open-Meteo WMO weather code mapping
WMO_CODE_TO_CONDITION = {
    0: WeatherCondition.CLEAR,  # Clear sky
    1: WeatherCondition.CLEAR,  # Mainly clear
    2: WeatherCondition.PARTLY_CLOUDY,  # Partly cloudy
    3: WeatherCondition.CLOUDY,  # Overcast
    45: WeatherCondition.FOG,  # Fog
    48: WeatherCondition.FOG,  # Depositing rime fog
    51: WeatherCondition.RAIN,  # Light drizzle
    53: WeatherCondition.RAIN,  # Moderate drizzle
    55: WeatherCondition.RAIN,  # Dense drizzle
    61: WeatherCondition.RAIN,  # Slight rain
    63: WeatherCondition.RAIN,  # Moderate rain
    65: WeatherCondition.HEAVY_RAIN,  # Heavy rain
    80: WeatherCondition.RAIN,  # Slight rain showers
    81: WeatherCondition.RAIN,  # Moderate rain showers
    82: WeatherCondition.HEAVY_RAIN,  # Violent rain showers
    95: WeatherCondition.THUNDERSTORM,  # Thunderstorm
    96: WeatherCondition.THUNDERSTORM,  # Thunderstorm with slight hail
    99: WeatherCondition.THUNDERSTORM,  # Thunderstorm with heavy hail
}

# OpenWeatherMap condition mapping
OWM_CONDITION_MAP = {
    "Clear": WeatherCondition.CLEAR,
    "Clouds": WeatherCondition.PARTLY_CLOUDY,
    "Rain": WeatherCondition.RAIN,
    "Drizzle": WeatherCondition.RAIN,
    "Thunderstorm": WeatherCondition.THUNDERSTORM,
    "Fog": WeatherCondition.FOG,
    "Mist": WeatherCondition.HAZE,
    "Haze": WeatherCondition.HAZE,
    "Dust": WeatherCondition.DUST,
    "Sand": WeatherCondition.DUST,
}


def get_cache_key(location_id: str, data_type: str) -> str:
    """Generate cache key for weather data"""
    return f"{location_id}:{data_type}"


def is_cache_valid(cache_entry: dict[str, Any]) -> bool:
    """Check if cache entry is still valid"""
    if not cache_entry:
        return False
    cached_at = cache_entry.get("cached_at")
    if not cached_at:
        return False
    age_minutes = (datetime.utcnow() - cached_at).total_seconds() / 60
    return age_minutes < WEATHER_CACHE_TTL_MINUTES


async def fetch_open_meteo_current(lat: float, lon: float) -> dict[str, Any] | None:
    """
    Fetch current weather from Open-Meteo API (free, no API key required)
    جلب الطقس الحالي من Open-Meteo API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ],
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Open-Meteo current weather fetched for ({lat}, {lon})")
            return data
    except Exception as e:
        logger.error(f"Open-Meteo API error: {e}")
        return None


async def fetch_open_meteo_forecast(
    lat: float, lon: float, days: int = 7
) -> dict[str, Any] | None:
    """
    Fetch weather forecast from Open-Meteo API
    جلب توقعات الطقس من Open-Meteo API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m",
            "uv_index",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "weather_code",
            "wind_speed_10m_max",
            "uv_index_max",
            "sunrise",
            "sunset",
        ],
        "forecast_days": min(days, 16),
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Open-Meteo forecast fetched for ({lat}, {lon}), {days} days")
            return data
    except Exception as e:
        logger.error(f"Open-Meteo forecast API error: {e}")
        return None


async def fetch_openweathermap_current(
    lat: float, lon: float
) -> dict[str, Any] | None:
    """
    Fetch current weather from OpenWeatherMap API
    جلب الطقس الحالي من OpenWeatherMap API
    """
    if not OPENWEATHERMAP_API_KEY:
        logger.warning("OpenWeatherMap API key not configured")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"OpenWeatherMap current weather fetched for ({lat}, {lon})")
            return data
    except Exception as e:
        logger.error(f"OpenWeatherMap API error: {e}")
        return None


async def fetch_openweathermap_forecast(
    lat: float, lon: float
) -> dict[str, Any] | None:
    """
    Fetch 5-day forecast from OpenWeatherMap API (free tier)
    جلب توقعات 5 أيام من OpenWeatherMap API
    """
    if not OPENWEATHERMAP_API_KEY:
        return None

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"OpenWeatherMap forecast fetched for ({lat}, {lon})")
            return data
    except Exception as e:
        logger.error(f"OpenWeatherMap forecast API error: {e}")
        return None


def parse_open_meteo_current(data: dict[str, Any], location_id: str) -> CurrentWeather:
    """Parse Open-Meteo current weather response"""
    location = YEMEN_LOCATIONS[location_id]
    current = data.get("current", {})

    weather_code = current.get("weather_code", 0)
    condition = WMO_CODE_TO_CONDITION.get(weather_code, WeatherCondition.CLEAR)

    wind_deg = current.get("wind_direction_10m", 0)
    wind_dir = WIND_DIRECTIONS[int((wind_deg + 22.5) / 45) % 8]

    temp = current.get("temperature_2m", 25)
    humidity = current.get("relative_humidity_2m", 50)

    return CurrentWeather(
        location_id=location_id,
        location_name_ar=location["name_ar"],
        latitude=location["lat"],
        longitude=location["lon"],
        timestamp=datetime.utcnow(),
        temperature_c=round(temp, 1),
        feels_like_c=round(current.get("apparent_temperature", temp), 1),
        humidity_percent=round(humidity, 0),
        pressure_hpa=round(current.get("pressure_msl", 1013), 0),
        wind_speed_kmh=round(current.get("wind_speed_10m", 0), 1),
        wind_direction=wind_dir,
        wind_gust_kmh=round(current.get("wind_gusts_10m", 0), 1),
        visibility_km=10.0,  # Not available in Open-Meteo free tier
        cloud_cover_percent=round(current.get("cloud_cover", 0), 0),
        uv_index=5.0,  # Current UV not in Open-Meteo current
        dew_point_c=round(temp - (100 - humidity) / 5, 1),
        condition=condition,
        condition_ar=CONDITION_TRANSLATIONS[condition],
    )


def parse_open_meteo_forecast(
    data: dict[str, Any],
    location_id: str,
    days: int,
) -> tuple[list[HourlyForecast], list[DailyForecast]]:
    """Parse Open-Meteo forecast response"""
    hourly_data = data.get("hourly", {})
    daily_data = data.get("daily", {})

    # Parse hourly forecast (48 hours)
    hourly_forecast = []
    hourly_times = hourly_data.get("time", [])[:48]

    for i, time_str in enumerate(hourly_times):
        weather_code = hourly_data.get("weather_code", [0] * 48)[i]
        condition = WMO_CODE_TO_CONDITION.get(weather_code, WeatherCondition.CLEAR)

        wind_deg = hourly_data.get("wind_direction_10m", [0] * 48)[i]
        wind_dir = WIND_DIRECTIONS[int((wind_deg + 22.5) / 45) % 8]

        hourly_forecast.append(
            HourlyForecast(
                datetime=datetime.fromisoformat(time_str),
                temperature_c=round(hourly_data.get("temperature_2m", [25] * 48)[i], 1),
                feels_like_c=round(
                    hourly_data.get("apparent_temperature", [25] * 48)[i], 1
                ),
                humidity_percent=round(
                    hourly_data.get("relative_humidity_2m", [50] * 48)[i], 0
                ),
                wind_speed_kmh=round(
                    hourly_data.get("wind_speed_10m", [10] * 48)[i], 1
                ),
                wind_direction=wind_dir,
                precipitation_mm=round(
                    hourly_data.get("precipitation", [0] * 48)[i], 1
                ),
                precipitation_probability=round(
                    hourly_data.get("precipitation_probability", [0] * 48)[i], 0
                ),
                cloud_cover_percent=round(
                    hourly_data.get("cloud_cover", [0] * 48)[i], 0
                ),
                uv_index=round(hourly_data.get("uv_index", [5] * 48)[i], 1),
                condition=condition,
                condition_ar=CONDITION_TRANSLATIONS[condition],
            )
        )

    # Parse daily forecast
    daily_forecast = []
    daily_times = daily_data.get("time", [])[:days]

    for i, date_str in enumerate(daily_times):
        weather_code = daily_data.get("weather_code", [0] * 14)[i]
        condition = WMO_CODE_TO_CONDITION.get(weather_code, WeatherCondition.CLEAR)

        temp_max = daily_data.get("temperature_2m_max", [30] * 14)[i]
        temp_min = daily_data.get("temperature_2m_min", [20] * 14)[i]
        precip = daily_data.get("precipitation_sum", [0] * 14)[i]

        # Agricultural summary based on conditions
        if temp_max > 38:
            summary_ar = "⚠️ حرارة مرتفعة - ري إضافي مطلوب وتجنب العمل وقت الذروة"
            summary_en = (
                "⚠️ High heat - extra irrigation needed, avoid work during peak hours"
            )
        elif precip > 20:
            summary_ar = "🌧️ أمطار متوقعة - تأجيل الرش والتسميد"
            summary_en = "🌧️ Rain expected - postpone spraying and fertilization"
        else:
            summary_ar = "✅ ظروف مناسبة للعمليات الزراعية"
            summary_en = "✅ Suitable conditions for agricultural operations"

        sunrise = daily_data.get("sunrise", ["05:45"] * 14)[i]
        sunset = daily_data.get("sunset", ["18:30"] * 14)[i]
        if isinstance(sunrise, str) and "T" in sunrise:
            sunrise = sunrise.split("T")[1][:5]
        if isinstance(sunset, str) and "T" in sunset:
            sunset = sunset.split("T")[1][:5]

        daily_forecast.append(
            DailyForecast(
                date=date.fromisoformat(date_str),
                temp_max_c=round(temp_max, 1),
                temp_min_c=round(temp_min, 1),
                humidity_avg=50,  # Average not directly available
                wind_speed_avg_kmh=round(
                    daily_data.get("wind_speed_10m_max", [15] * 14)[i] * 0.7, 1
                ),
                precipitation_total_mm=round(precip, 1),
                precipitation_probability=round(
                    daily_data.get("precipitation_probability_max", [0] * 14)[i], 0
                ),
                sunrise=sunrise,
                sunset=sunset,
                uv_index_max=round(daily_data.get("uv_index_max", [8] * 14)[i], 1),
                condition=condition,
                condition_ar=CONDITION_TRANSLATIONS[condition],
                agricultural_summary_ar=summary_ar,
                agricultural_summary_en=summary_en,
            )
        )

    return hourly_forecast, daily_forecast


async def get_real_current_weather(location_id: str) -> CurrentWeather | None:
    """
    Get real current weather from configured API provider
    جلب الطقس الحالي الحقيقي من مزود API المكون
    """
    if location_id not in YEMEN_LOCATIONS:
        return None

    # Check cache first
    cache_key = get_cache_key(location_id, "current")
    if cache_key in _weather_cache and is_cache_valid(_weather_cache[cache_key]):
        logger.debug(f"Returning cached current weather for {location_id}")
        return _weather_cache[cache_key]["data"]

    location = YEMEN_LOCATIONS[location_id]
    lat, lon = location["lat"], location["lon"]

    # Try Open-Meteo first (no API key required)
    if WEATHER_API_PROVIDER == "open-meteo" or not OPENWEATHERMAP_API_KEY:
        data = await fetch_open_meteo_current(lat, lon)
        if data:
            result = parse_open_meteo_current(data, location_id)
            _weather_cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
            return result

    # Try OpenWeatherMap if configured
    if OPENWEATHERMAP_API_KEY:
        data = await fetch_openweathermap_current(lat, lon)
        if data:
            # Parse OpenWeatherMap response
            main = data.get("main", {})
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            weather = data.get("weather", [{}])[0]

            condition_main = weather.get("main", "Clear")
            condition = OWM_CONDITION_MAP.get(condition_main, WeatherCondition.CLEAR)

            wind_deg = wind.get("deg", 0)
            wind_dir = WIND_DIRECTIONS[int((wind_deg + 22.5) / 45) % 8]

            result = CurrentWeather(
                location_id=location_id,
                location_name_ar=location["name_ar"],
                latitude=lat,
                longitude=lon,
                timestamp=datetime.utcnow(),
                temperature_c=round(main.get("temp", 25), 1),
                feels_like_c=round(main.get("feels_like", 25), 1),
                humidity_percent=round(main.get("humidity", 50), 0),
                pressure_hpa=round(main.get("pressure", 1013), 0),
                wind_speed_kmh=round(wind.get("speed", 0) * 3.6, 1),  # m/s to km/h
                wind_direction=wind_dir,
                wind_gust_kmh=round(wind.get("gust", 0) * 3.6, 1),
                visibility_km=round(data.get("visibility", 10000) / 1000, 1),
                cloud_cover_percent=round(clouds.get("all", 0), 0),
                uv_index=5.0,  # Not in basic OWM API
                dew_point_c=round(
                    main.get("temp", 25) - (100 - main.get("humidity", 50)) / 5, 1
                ),
                condition=condition,
                condition_ar=CONDITION_TRANSLATIONS[condition],
            )
            _weather_cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
            return result

    return None


async def get_real_forecast(
    location_id: str, days: int = 7
) -> tuple[list[HourlyForecast], list[DailyForecast]] | None:
    """
    Get real weather forecast from configured API provider
    جلب توقعات الطقس الحقيقية من مزود API المكون
    """
    if location_id not in YEMEN_LOCATIONS:
        return None

    # Check cache
    cache_key = get_cache_key(location_id, f"forecast_{days}")
    if cache_key in _weather_cache and is_cache_valid(_weather_cache[cache_key]):
        logger.debug(f"Returning cached forecast for {location_id}")
        return _weather_cache[cache_key]["data"]

    location = YEMEN_LOCATIONS[location_id]
    lat, lon = location["lat"], location["lon"]

    # Open-Meteo provides 16-day forecast for free
    data = await fetch_open_meteo_forecast(lat, lon, days)
    if data:
        result = parse_open_meteo_forecast(data, location_id, days)
        _weather_cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
        return result

    return None


# =============================================================================
# Weather Generation Functions (Fallback/Simulation)
# =============================================================================


def get_seasonal_base_temp(location_id: str, day_of_year: int) -> tuple[float, float]:
    """Get seasonal base temperature for location"""
    location = YEMEN_LOCATIONS.get(location_id, YEMEN_LOCATIONS["sanaa"])
    elevation = location["elevation"]

    # Base temperature adjusted for elevation (-6.5°C per 1000m)
    base_temp = 30 - (elevation / 1000) * 6.5

    # Seasonal variation (summer peak around day 200)
    seasonal_offset = 8 * math.sin((day_of_year - 80) * 2 * math.pi / 365)

    daily_high = base_temp + seasonal_offset + 5
    daily_low = base_temp + seasonal_offset - 8

    return daily_high, daily_low


def generate_weather_condition(
    temp: float, humidity: float, month: int
) -> WeatherCondition:
    """Generate realistic weather condition"""
    import random

    # Rainy season in Yemen: March-May and July-September
    rainy_months = [3, 4, 5, 7, 8, 9]

    if month in rainy_months and humidity > 60:
        if random.random() < 0.3:
            return random.choice([WeatherCondition.RAIN, WeatherCondition.THUNDERSTORM])
        elif random.random() < 0.2:
            return WeatherCondition.HEAVY_RAIN

    if humidity < 30 and random.random() < 0.2:
        return WeatherCondition.DUST

    if humidity > 80 and temp < 20 and random.random() < 0.3:
        return WeatherCondition.FOG

    if random.random() < 0.6:
        return WeatherCondition.CLEAR
    elif random.random() < 0.7:
        return WeatherCondition.PARTLY_CLOUDY
    else:
        return WeatherCondition.CLOUDY


def calculate_evapotranspiration(
    temp: float, humidity: float, wind_speed: float, solar_radiation: float = 20
) -> float:
    """Calculate reference evapotranspiration using simplified Penman-Monteith"""
    # Simplified ET0 calculation
    # ET0 = 0.0023 * (Tmean + 17.8) * (Tmax - Tmin)^0.5 * Ra
    temp_factor = 0.0023 * (temp + 17.8)
    humidity_factor = max(0.5, 1 - humidity / 200)
    wind_factor = 1 + wind_speed / 50
    et0 = temp_factor * solar_radiation * humidity_factor * wind_factor * 0.5
    return round(max(0, et0), 2)


def calculate_growing_degree_days(
    temp_max: float, temp_min: float, base_temp: float = 10
) -> float:
    """Calculate Growing Degree Days"""
    avg_temp = (temp_max + temp_min) / 2
    gdd = max(0, avg_temp - base_temp)
    return round(gdd, 1)


def check_for_alerts(
    forecast: list[DailyForecast], location_id: str
) -> list[WeatherAlert]:
    """Check forecast for agricultural weather alerts"""
    alerts = []

    for _i, day in enumerate(forecast):
        # Heat wave check
        if day.temp_max_c >= 40:
            alerts.append(
                WeatherAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.HEAT_WAVE,
                    severity=(
                        AlertSeverity.WARNING
                        if day.temp_max_c < 45
                        else AlertSeverity.EMERGENCY
                    ),
                    title_ar="تحذير: موجة حر شديدة",
                    title_en="Warning: Extreme Heat Wave",
                    description_ar=f"درجات حرارة مرتفعة جداً متوقعة تصل إلى {day.temp_max_c}°م",
                    description_en=f"Extremely high temperatures expected up to {day.temp_max_c}°C",
                    start_time=datetime.combine(day.date, datetime.min.time()),
                    end_time=datetime.combine(day.date, datetime.max.time()),
                    affected_crops_ar=["طماطم", "خيار", "فلفل", "باذنجان"],
                    recommendations_ar=[
                        "الري في الصباح الباكر أو المساء فقط",
                        "توفير ظل للمحاصيل الحساسة",
                        "زيادة كمية الري بنسبة 20%",
                        "تجنب التسميد خلال ذروة الحرارة",
                    ],
                    recommendations_en=[
                        "Irrigate only in early morning or evening",
                        "Provide shade for sensitive crops",
                        "Increase irrigation by 20%",
                        "Avoid fertilization during peak heat",
                    ],
                )
            )

        # Heavy rain check
        if day.precipitation_total_mm >= 30:
            alerts.append(
                WeatherAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.HEAVY_RAIN,
                    severity=(
                        AlertSeverity.WATCH
                        if day.precipitation_total_mm < 50
                        else AlertSeverity.WARNING
                    ),
                    title_ar="تنبيه: أمطار غزيرة متوقعة",
                    title_en="Alert: Heavy Rain Expected",
                    description_ar=f"كميات أمطار تصل إلى {day.precipitation_total_mm} ملم متوقعة",
                    description_en=f"Rainfall amounts up to {day.precipitation_total_mm}mm expected",
                    start_time=datetime.combine(day.date, datetime.min.time()),
                    end_time=datetime.combine(day.date, datetime.max.time()),
                    affected_crops_ar=["جميع المحاصيل"],
                    recommendations_ar=[
                        "التأكد من صرف المياه الزائدة",
                        "تأجيل الرش والتسميد",
                        "حماية الشتلات الصغيرة",
                        "فحص التربة بعد المطر",
                    ],
                    recommendations_en=[
                        "Ensure proper drainage",
                        "Postpone spraying and fertilization",
                        "Protect young seedlings",
                        "Check soil after rain",
                    ],
                )
            )

        # High humidity (disease risk)
        if day.humidity_avg >= 85:
            alerts.append(
                WeatherAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.HIGH_HUMIDITY,
                    severity=AlertSeverity.ADVISORY,
                    title_ar="تنبيه: رطوبة عالية - خطر الأمراض الفطرية",
                    title_en="Advisory: High Humidity - Fungal Disease Risk",
                    description_ar=f"رطوبة مرتفعة {day.humidity_avg}% تزيد من خطر الأمراض",
                    description_en=f"High humidity {day.humidity_avg}% increases disease risk",
                    start_time=datetime.combine(day.date, datetime.min.time()),
                    end_time=datetime.combine(day.date, datetime.max.time()),
                    affected_crops_ar=["طماطم", "بطاطس", "عنب", "خيار"],
                    recommendations_ar=[
                        "رش مبيدات فطرية وقائية",
                        "تحسين التهوية بين النباتات",
                        "تجنب الري العلوي",
                        "مراقبة علامات البياض الدقيقي",
                    ],
                    recommendations_en=[
                        "Apply preventive fungicides",
                        "Improve air circulation between plants",
                        "Avoid overhead irrigation",
                        "Monitor for powdery mildew signs",
                    ],
                )
            )

        # Strong wind
        if day.wind_speed_avg_kmh >= 40:
            alerts.append(
                WeatherAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.HIGH_WIND,
                    severity=AlertSeverity.WATCH,
                    title_ar="تنبيه: رياح قوية متوقعة",
                    title_en="Watch: Strong Winds Expected",
                    description_ar=f"سرعة رياح تصل إلى {day.wind_speed_avg_kmh} كم/س",
                    description_en=f"Wind speeds up to {day.wind_speed_avg_kmh} km/h",
                    start_time=datetime.combine(day.date, datetime.min.time()),
                    end_time=datetime.combine(day.date, datetime.max.time()),
                    affected_crops_ar=["موز", "نخيل", "ذرة", "محاصيل طويلة"],
                    recommendations_ar=[
                        "تأمين البيوت المحمية",
                        "دعم النباتات الطويلة",
                        "تأجيل عمليات الرش",
                        "حماية الشتلات",
                    ],
                    recommendations_en=[
                        "Secure greenhouses",
                        "Support tall plants",
                        "Postpone spraying operations",
                        "Protect seedlings",
                    ],
                )
            )

    return alerts


def get_spray_windows(hourly: list[HourlyForecast]) -> list[str]:
    """Identify optimal spray windows (low wind, no rain, moderate temp)"""
    windows = []
    for hour in hourly[:48]:  # Next 48 hours
        if (
            hour.wind_speed_kmh < 15
            and hour.precipitation_probability < 20
            and hour.temperature_c < 35
            and hour.temperature_c > 15
        ):
            windows.append(hour.datetime.strftime("%Y-%m-%d %H:00"))
    return windows[:10]  # Return max 10 windows


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health():
    return {
        "status": "healthy",
        "service": "weather-advanced",
        "version": "15.4.0",
        "locations_count": len(YEMEN_LOCATIONS),
        "api_provider": WEATHER_API_PROVIDER,
        "cache_ttl_minutes": WEATHER_CACHE_TTL_MINUTES,
    }


@app.get("/v1/locations")
def list_locations():
    """قائمة المواقع المتاحة"""
    return {
        "locations": [
            {
                "id": loc_id,
                "name_ar": data["name_ar"],
                "latitude": data["lat"],
                "longitude": data["lon"],
                "elevation_m": data["elevation"],
            }
            for loc_id, data in YEMEN_LOCATIONS.items()
        ]
    }


@app.get("/v1/current/{location_id}", response_model=CurrentWeather)
async def get_current_weather(location_id: str):
    """
    الطقس الحالي لموقع معين
    Current weather for a specific location
    Uses real weather API (Open-Meteo/OpenWeatherMap) with fallback to simulation
    """
    import random

    if location_id not in YEMEN_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    # Try real weather API first
    try:
        real_weather = await get_real_current_weather(location_id)
        if real_weather:
            logger.info(f"Returning real weather data for {location_id}")
            return real_weather
    except Exception as e:
        logger.warning(f"Real weather API failed for {location_id}: {e}")

    # Fallback to simulation
    logger.info(f"Falling back to simulated weather for {location_id}")
    location = YEMEN_LOCATIONS[location_id]
    now = datetime.utcnow()
    day_of_year = now.timetuple().tm_yday
    hour = now.hour

    temp_high, temp_low = get_seasonal_base_temp(location_id, day_of_year)

    # Temperature varies by hour
    hour_factor = math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else -0.5
    temp = temp_low + (temp_high - temp_low) * (0.5 + 0.5 * hour_factor)
    temp += random.uniform(-2, 2)

    humidity = random.uniform(30, 80)
    wind_speed = random.uniform(5, 25)
    wind_dir = random.choice(WIND_DIRECTIONS)

    condition = generate_weather_condition(temp, humidity, now.month)

    return CurrentWeather(
        location_id=location_id,
        location_name_ar=location["name_ar"],
        latitude=location["lat"],
        longitude=location["lon"],
        timestamp=now,
        temperature_c=round(temp, 1),
        feels_like_c=round(temp + (humidity - 50) / 20 + wind_speed / 10, 1),
        humidity_percent=round(humidity, 0),
        pressure_hpa=round(1013 - location["elevation"] / 8, 0),
        wind_speed_kmh=round(wind_speed, 1),
        wind_direction=wind_dir,
        wind_gust_kmh=round(wind_speed * random.uniform(1.2, 1.8), 1),
        visibility_km=round(random.uniform(8, 20), 1),
        cloud_cover_percent=round(random.uniform(0, 60), 0),
        uv_index=round(random.uniform(5, 11), 1),
        dew_point_c=round(temp - (100 - humidity) / 5, 1),
        condition=condition,
        condition_ar=CONDITION_TRANSLATIONS[condition],
    )


@app.get("/v1/forecast/{location_id}", response_model=AgriculturalWeatherReport)
async def get_forecast(location_id: str, days: int = Query(default=7, ge=1, le=14)):
    """
    تقرير الطقس الزراعي الشامل مع التنبؤات
    Comprehensive agricultural weather report with forecasts
    Uses real weather API with fallback to simulation
    """
    import random

    if location_id not in YEMEN_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    location = YEMEN_LOCATIONS[location_id]
    now = datetime.utcnow()

    # Get current weather (async)
    current = await get_current_weather(location_id)

    # Try real forecast API first
    real_forecast = None
    try:
        real_forecast = await get_real_forecast(location_id, days)
        if real_forecast:
            logger.info(f"Using real forecast data for {location_id}")
    except Exception as e:
        logger.warning(f"Real forecast API failed for {location_id}: {e}")

    if real_forecast:
        hourly_forecast, daily_forecast = real_forecast

        # Calculate GDD from real forecast
        total_gdd = sum(
            calculate_growing_degree_days(day.temp_max_c, day.temp_min_c)
            for day in daily_forecast
        )

        # Check for alerts
        alerts = check_for_alerts(daily_forecast, location_id)

        # Calculate ET
        et0 = calculate_evapotranspiration(
            current.temperature_c, current.humidity_percent, current.wind_speed_kmh
        )

        # Get spray windows
        spray_windows = get_spray_windows(hourly_forecast)

        # Irrigation recommendation
        if et0 > 6:
            irrig_ar = f"💧 احتياج ري عالي اليوم ({et0} ملم) - ري صباحي ومسائي مطلوب"
            irrig_en = f"💧 High irrigation need today ({et0} mm) - morning and evening irrigation required"
        elif et0 > 4:
            irrig_ar = f"💧 احتياج ري متوسط ({et0} ملم) - ري واحد كافي"
            irrig_en = (
                f"💧 Medium irrigation need ({et0} mm) - one irrigation sufficient"
            )
        else:
            irrig_ar = f"💧 احتياج ري منخفض ({et0} ملم) - تقليل الري ممكن"
            irrig_en = (
                f"💧 Low irrigation need ({et0} mm) - reduced irrigation possible"
            )

        return AgriculturalWeatherReport(
            location_id=location_id,
            location_name_ar=location["name_ar"],
            generated_at=now,
            current=current,
            hourly_forecast=hourly_forecast,
            daily_forecast=daily_forecast,
            alerts=alerts,
            growing_degree_days=round(total_gdd, 1),
            evapotranspiration_mm=et0,
            spray_window_hours=spray_windows,
            irrigation_recommendation_ar=irrig_ar,
            irrigation_recommendation_en=irrig_en,
        )

    # Fallback to simulation
    logger.info(f"Falling back to simulated forecast for {location_id}")

    # Generate hourly forecast (48 hours)
    hourly_forecast = []
    for h in range(48):
        forecast_time = now + timedelta(hours=h)
        day_of_year = forecast_time.timetuple().tm_yday
        hour = forecast_time.hour

        temp_high, temp_low = get_seasonal_base_temp(location_id, day_of_year)
        hour_factor = math.sin((hour - 6) * math.pi / 12) if 6 <= hour <= 18 else -0.5
        temp = temp_low + (temp_high - temp_low) * (0.5 + 0.5 * hour_factor)
        temp += random.uniform(-2, 2)

        humidity = random.uniform(30, 80)
        wind_speed = random.uniform(5, 25)
        condition = generate_weather_condition(temp, humidity, forecast_time.month)
        precip_prob = (
            0.6
            if condition
            in [
                WeatherCondition.RAIN,
                WeatherCondition.HEAVY_RAIN,
                WeatherCondition.THUNDERSTORM,
            ]
            else random.uniform(0, 0.2)
        )

        hourly_forecast.append(
            HourlyForecast(
                datetime=forecast_time,
                temperature_c=round(temp, 1),
                feels_like_c=round(temp + (humidity - 50) / 20, 1),
                humidity_percent=round(humidity, 0),
                wind_speed_kmh=round(wind_speed, 1),
                wind_direction=random.choice(WIND_DIRECTIONS),
                precipitation_mm=round(
                    random.uniform(0, 5) if precip_prob > 0.3 else 0, 1
                ),
                precipitation_probability=round(precip_prob * 100, 0),
                cloud_cover_percent=round(random.uniform(0, 80), 0),
                uv_index=round(random.uniform(0, 11) if 6 <= hour <= 18 else 0, 1),
                condition=condition,
                condition_ar=CONDITION_TRANSLATIONS[condition],
            )
        )

    # Generate daily forecast
    daily_forecast = []
    total_gdd = 0

    for d in range(days):
        forecast_date = (now + timedelta(days=d)).date()
        day_of_year = (now + timedelta(days=d)).timetuple().tm_yday

        temp_high, temp_low = get_seasonal_base_temp(location_id, day_of_year)
        temp_high += random.uniform(-3, 3)
        temp_low += random.uniform(-3, 3)

        humidity_avg = random.uniform(40, 75)
        wind_avg = random.uniform(8, 30)
        condition = generate_weather_condition(
            (temp_high + temp_low) / 2, humidity_avg, forecast_date.month
        )

        precip_total = 0
        precip_prob = 0
        if condition in [
            WeatherCondition.RAIN,
            WeatherCondition.HEAVY_RAIN,
            WeatherCondition.THUNDERSTORM,
        ]:
            precip_total = (
                random.uniform(5, 40)
                if condition != WeatherCondition.HEAVY_RAIN
                else random.uniform(30, 80)
            )
            precip_prob = random.uniform(60, 95)

        gdd = calculate_growing_degree_days(temp_high, temp_low)
        total_gdd += gdd

        # Agricultural summaries
        if temp_high > 38:
            summary_ar = "⚠️ حرارة مرتفعة - ري إضافي مطلوب وتجنب العمل وقت الذروة"
            summary_en = (
                "⚠️ High heat - extra irrigation needed, avoid work during peak hours"
            )
        elif precip_total > 20:
            summary_ar = "🌧️ أمطار متوقعة - تأجيل الرش والتسميد"
            summary_en = "🌧️ Rain expected - postpone spraying and fertilization"
        elif humidity_avg > 80:
            summary_ar = "💧 رطوبة عالية - مراقبة الأمراض الفطرية"
            summary_en = "💧 High humidity - monitor for fungal diseases"
        else:
            summary_ar = "✅ ظروف مناسبة للعمليات الزراعية"
            summary_en = "✅ Suitable conditions for agricultural operations"

        daily_forecast.append(
            DailyForecast(
                date=forecast_date,
                temp_max_c=round(temp_high, 1),
                temp_min_c=round(temp_low, 1),
                humidity_avg=round(humidity_avg, 0),
                wind_speed_avg_kmh=round(wind_avg, 1),
                precipitation_total_mm=round(precip_total, 1),
                precipitation_probability=round(precip_prob, 0),
                sunrise="05:45",
                sunset="18:30",
                uv_index_max=round(random.uniform(8, 11), 1),
                condition=condition,
                condition_ar=CONDITION_TRANSLATIONS[condition],
                agricultural_summary_ar=summary_ar,
                agricultural_summary_en=summary_en,
            )
        )

    # Check for alerts
    alerts = check_for_alerts(daily_forecast, location_id)

    # Calculate ET
    et0 = calculate_evapotranspiration(
        current.temperature_c, current.humidity_percent, current.wind_speed_kmh
    )

    # Get spray windows
    spray_windows = get_spray_windows(hourly_forecast)

    # Irrigation recommendation
    if et0 > 6:
        irrig_ar = f"💧 احتياج ري عالي اليوم ({et0} ملم) - ري صباحي ومسائي مطلوب"
        irrig_en = f"💧 High irrigation need today ({et0} mm) - morning and evening irrigation required"
    elif et0 > 4:
        irrig_ar = f"💧 احتياج ري متوسط ({et0} ملم) - ري واحد كافي"
        irrig_en = (
            f"💧 Medium irrigation need ({et0} mm) - one irrigation sufficient"
        )
    else:
        irrig_ar = f"💧 احتياج ري منخفض ({et0} ملم) - تقليل الري ممكن"
        irrig_en = (
            f"💧 Low irrigation need ({et0} mm) - reduced irrigation possible"
        )

    return AgriculturalWeatherReport(
        location_id=location_id,
        location_name_ar=location["name_ar"],
        generated_at=now,
        current=current,
        hourly_forecast=hourly_forecast,
        daily_forecast=daily_forecast,
        alerts=alerts,
        growing_degree_days=round(total_gdd, 1),
        evapotranspiration_mm=et0,
        spray_window_hours=spray_windows,
        irrigation_recommendation_ar=irrig_ar,
        irrigation_recommendation_en=irrig_en,
    )


@app.get("/v1/alerts/{location_id}")
async def get_weather_alerts(location_id: str):
    """تنبيهات الطقس الزراعية"""
    forecast_report = await get_forecast(location_id, days=7)
    return {
        "location_id": location_id,
        "location_name_ar": YEMEN_LOCATIONS[location_id]["name_ar"],
        "alerts_count": len(forecast_report.alerts),
        "alerts": [alert.dict() for alert in forecast_report.alerts],
    }


@app.get("/v1/agricultural-calendar/{location_id}")
def get_agricultural_calendar(
    location_id: str, crop: str = Query(default="tomato", description="نوع المحصول")
):
    """التقويم الزراعي مع توصيات حسب المحصول"""
    import random

    if location_id not in YEMEN_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    now = datetime.utcnow()

    # Crop-specific recommendations
    crops_calendar = {
        "tomato": {
            "name_ar": "طماطم",
            "planting_months": [9, 10, 2, 3],
            "harvest_months": [12, 1, 5, 6],
            "optimal_temp": (20, 30),
            "water_need": "high",
        },
        "wheat": {
            "name_ar": "قمح",
            "planting_months": [10, 11],
            "harvest_months": [4, 5],
            "optimal_temp": (15, 25),
            "water_need": "medium",
        },
        "coffee": {
            "name_ar": "بن",
            "planting_months": [3, 4],
            "harvest_months": [10, 11, 12],
            "optimal_temp": (18, 24),
            "water_need": "medium",
        },
        "banana": {
            "name_ar": "موز",
            "planting_months": [2, 3, 4],
            "harvest_months": list(range(1, 13)),  # Year-round
            "optimal_temp": (25, 35),
            "water_need": "very_high",
        },
    }

    crop_info = crops_calendar.get(crop, crops_calendar["tomato"])
    current_month = now.month

    # Determine current activity
    if current_month in crop_info["planting_months"]:
        activity_ar = "🌱 موسم الزراعة - وقت مثالي للزراعة"
        activity_en = "🌱 Planting season - optimal time for planting"
    elif current_month in crop_info["harvest_months"]:
        activity_ar = "🌾 موسم الحصاد - المحصول جاهز للجمع"
        activity_en = "🌾 Harvest season - crop ready for collection"
    else:
        activity_ar = "🌿 موسم النمو - العناية والمتابعة"
        activity_en = "🌿 Growing season - care and monitoring"

    return {
        "location_id": location_id,
        "location_name_ar": YEMEN_LOCATIONS[location_id]["name_ar"],
        "crop": crop,
        "crop_name_ar": crop_info["name_ar"],
        "current_month": current_month,
        "current_activity_ar": activity_ar,
        "current_activity_en": activity_en,
        "optimal_temperature_range": crop_info["optimal_temp"],
        "water_requirement": crop_info["water_need"],
        "planting_months": crop_info["planting_months"],
        "harvest_months": crop_info["harvest_months"],
        "next_7_days_suitability": [
            {
                "date": (now + timedelta(days=i)).date().isoformat(),
                "planting_suitable": random.random() > 0.3,
                "spraying_suitable": random.random() > 0.4,
                "harvesting_suitable": random.random() > 0.2,
            }
            for i in range(7)
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8092)
