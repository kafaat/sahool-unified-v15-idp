"""
🌤️ SAHOOL Advanced Weather Service v15.3
خدمة الطقس المتقدمة - 7-Day Forecasting & Agricultural Alerts
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import math

app = FastAPI(
    title="SAHOOL Advanced Weather Service | خدمة الطقس المتقدمة",
    version="15.3.0",
    description="7-day forecasting, agricultural weather alerts, and crop-specific recommendations",
)


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
    affected_crops_ar: List[str]
    recommendations_ar: List[str]
    recommendations_en: List[str]


class AgriculturalWeatherReport(BaseModel):
    location_id: str
    location_name_ar: str
    generated_at: datetime
    current: CurrentWeather
    hourly_forecast: List[HourlyForecast]
    daily_forecast: List[DailyForecast]
    alerts: List[WeatherAlert]
    growing_degree_days: float
    evapotranspiration_mm: float
    spray_window_hours: List[str]
    irrigation_recommendation_ar: str
    irrigation_recommendation_en: str


# =============================================================================
# Yemen Locations & Weather Data
# =============================================================================

YEMEN_LOCATIONS = {
    "sanaa": {"lat": 15.3694, "lon": 44.1910, "name_ar": "صنعاء", "elevation": 2250},
    "aden": {"lat": 12.7855, "lon": 45.0187, "name_ar": "عدن", "elevation": 6},
    "taiz": {"lat": 13.5789, "lon": 44.0219, "name_ar": "تعز", "elevation": 1400},
    "hodeidah": {"lat": 14.7979, "lon": 42.9540, "name_ar": "الحديدة", "elevation": 12},
    "ibb": {"lat": 13.9667, "lon": 44.1667, "name_ar": "إب", "elevation": 2050},
    "dhamar": {"lat": 14.5500, "lon": 44.4000, "name_ar": "ذمار", "elevation": 2400},
    "hajjah": {"lat": 15.6917, "lon": 43.6028, "name_ar": "حجة", "elevation": 1800},
    "lahij": {"lat": 13.0500, "lon": 44.8833, "name_ar": "لحج", "elevation": 150},
    "marib": {"lat": 15.4667, "lon": 45.3500, "name_ar": "مأرب", "elevation": 1100},
    "hadramaut": {
        "lat": 15.9500,
        "lon": 48.7833,
        "name_ar": "حضرموت",
        "elevation": 650,
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
# Weather Generation Functions
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

    if humidity < 30:
        if random.random() < 0.2:
            return WeatherCondition.DUST

    if humidity > 80 and temp < 20:
        if random.random() < 0.3:
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
    forecast: List[DailyForecast], location_id: str
) -> List[WeatherAlert]:
    """Check forecast for agricultural weather alerts"""
    alerts = []

    for i, day in enumerate(forecast):
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


def get_spray_windows(hourly: List[HourlyForecast]) -> List[str]:
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
        "status": "ok",
        "service": "weather-advanced",
        "version": "15.3.0",
        "locations_count": len(YEMEN_LOCATIONS),
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
def get_current_weather(location_id: str):
    """الطقس الحالي لموقع معين"""
    import random

    if location_id not in YEMEN_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

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
def get_forecast(location_id: str, days: int = Query(default=7, ge=1, le=14)):
    """تقرير الطقس الزراعي الشامل مع التنبؤات"""
    import random

    if location_id not in YEMEN_LOCATIONS:
        raise HTTPException(status_code=404, detail=f"Location {location_id} not found")

    location = YEMEN_LOCATIONS[location_id]
    now = datetime.utcnow()

    # Get current weather
    current = get_current_weather(location_id)

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
        irrig_ar = "💧 احتياج ري عالي اليوم ({} ملم) - ري صباحي ومسائي مطلوب".format(
            et0
        )
        irrig_en = "💧 High irrigation need today ({} mm) - morning and evening irrigation required".format(
            et0
        )
    elif et0 > 4:
        irrig_ar = "💧 احتياج ري متوسط ({} ملم) - ري واحد كافي".format(et0)
        irrig_en = (
            "💧 Medium irrigation need ({} mm) - one irrigation sufficient".format(et0)
        )
    else:
        irrig_ar = "💧 احتياج ري منخفض ({} ملم) - تقليل الري ممكن".format(et0)
        irrig_en = (
            "💧 Low irrigation need ({} mm) - reduced irrigation possible".format(et0)
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
def get_weather_alerts(location_id: str):
    """تنبيهات الطقس الزراعية"""
    forecast_report = get_forecast(location_id, days=7)
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
