"""
Weather Service - Signal Producer (Layer 2)
خدمة الطقس - منتج الإشارات

Responsibilities:
1. Fetch weather data from Open-Meteo API
2. Detect weather anomalies based on Yemen thresholds
3. Publish weather events to NATS
4. NO public API (Layer 2 rule)

Events Produced:
- weather.daily.summary
- weather.anomaly.detected
- weather.forecast.updated
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI
import uvicorn
import httpx
import nats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.insert(0, "/app")
from shared.events.base_event import create_event, EventTypes
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, init_service_info

configure_logging(service_name="weather-service")
logger = get_logger(__name__)
event_logger = EventLogger("weather-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "weather-service"
SERVICE_LAYER = "signal-producer"


# ============================================
# Data Models
# ============================================


class WeatherCondition(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    DUST = "dust"
    FOG = "fog"


@dataclass
class WeatherData:
    timestamp: str
    location_lat: float
    location_lon: float
    region: str
    location_name: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction: str
    precipitation_mm: float
    cloud_cover_percent: float
    uv_index: float
    condition: WeatherCondition

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "location": {
                "lat": self.location_lat,
                "lon": self.location_lon,
                "region": self.region,
                "name": self.location_name,
            },
            "current": {
                "temperature_c": self.temperature_c,
                "feels_like_c": self.feels_like_c,
                "humidity_percent": self.humidity_percent,
                "pressure_hpa": self.pressure_hpa,
                "wind_speed_kmh": self.wind_speed_kmh,
                "wind_direction": self.wind_direction,
                "precipitation_mm": self.precipitation_mm,
                "cloud_cover_percent": self.cloud_cover_percent,
                "uv_index": self.uv_index,
                "condition": self.condition.value,
            },
        }


@dataclass
class WeatherAnomaly:
    anomaly_type: str
    severity: str
    description_ar: str
    description_en: str
    current_value: float
    threshold: float
    impact_crops: List[str]
    recommended_action_ar: str
    recommended_action_en: str


# ============================================
# Yemen Regional Thresholds
# ============================================

YEMEN_THRESHOLDS = {
    "المرتفعات": {
        "temp_high": 38,
        "temp_low": 5,
        "humidity_high": 85,
        "humidity_low": 15,
        "wind_high": 50,
        "rain_heavy": 30,
    },
    "تهامة": {
        "temp_high": 45,
        "temp_low": 18,
        "humidity_high": 95,
        "humidity_low": 20,
        "wind_high": 60,
        "rain_heavy": 50,
    },
    "حضرموت": {
        "temp_high": 48,
        "temp_low": 10,
        "humidity_high": 80,
        "humidity_low": 10,
        "wind_high": 70,
        "rain_heavy": 25,
    },
}

# Monitoring Locations
MONITORING_LOCATIONS = [
    {
        "lat": 15.3694,
        "lon": 44.1910,
        "region": "المرتفعات",
        "name": "صنعاء",
        "name_en": "Sanaa",
    },
    {
        "lat": 14.7979,
        "lon": 42.9540,
        "region": "تهامة",
        "name": "الحديدة",
        "name_en": "Hodeidah",
    },
    {
        "lat": 15.9543,
        "lon": 48.9902,
        "region": "حضرموت",
        "name": "المكلا",
        "name_en": "Mukalla",
    },
    {
        "lat": 13.5775,
        "lon": 44.0178,
        "region": "المرتفعات",
        "name": "تعز",
        "name_en": "Taiz",
    },
    {
        "lat": 12.7797,
        "lon": 45.0358,
        "region": "تهامة",
        "name": "عدن",
        "name_en": "Aden",
    },
    {
        "lat": 16.9389,
        "lon": 43.8650,
        "region": "المرتفعات",
        "name": "صعدة",
        "name_en": "Saada",
    },
    {
        "lat": 14.5425,
        "lon": 49.1260,
        "region": "حضرموت",
        "name": "سيئون",
        "name_en": "Seiyun",
    },
    {
        "lat": 13.9792,
        "lon": 44.1739,
        "region": "المرتفعات",
        "name": "إب",
        "name_en": "Ibb",
    },
]


# ============================================
# Open-Meteo Client
# ============================================


class OpenMeteoClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    async def fetch_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
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
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "uv_index_max",
                "wind_speed_10m_max",
            ],
            "timezone": "Asia/Aden",
            "forecast_days": 7,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("weather_fetch_failed", error=str(e))
            return None

    def parse_response(self, data: dict, location: dict) -> Optional[WeatherData]:
        if not data or "current" not in data:
            return None

        current = data["current"]
        daily = data.get("daily", {})

        return WeatherData(
            timestamp=datetime.utcnow().isoformat() + "Z",
            location_lat=location["lat"],
            location_lon=location["lon"],
            region=location["region"],
            location_name=location["name"],
            temperature_c=round(current.get("temperature_2m", 0), 1),
            feels_like_c=round(current.get("apparent_temperature", 0), 1),
            humidity_percent=round(current.get("relative_humidity_2m", 0), 1),
            pressure_hpa=round(current.get("pressure_msl", 1013), 1),
            wind_speed_kmh=round(current.get("wind_speed_10m", 0), 1),
            wind_direction=self._degrees_to_direction(
                current.get("wind_direction_10m", 0)
            ),
            precipitation_mm=round(current.get("precipitation", 0), 1),
            cloud_cover_percent=round(current.get("cloud_cover", 0), 1),
            uv_index=round(
                daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0, 1
            ),
            condition=self._map_weather_code(current.get("weather_code", 0)),
        )

    def _map_weather_code(self, code: int) -> WeatherCondition:
        if code == 0:
            return WeatherCondition.CLEAR
        elif code in [1, 2, 3]:
            return WeatherCondition.CLOUDY
        elif code in [45, 48]:
            return WeatherCondition.FOG
        elif code in [51, 53, 55, 61, 63]:
            return WeatherCondition.RAIN
        elif code in [65, 67, 80, 81, 82]:
            return WeatherCondition.HEAVY_RAIN
        elif code in [95, 96, 99]:
            return WeatherCondition.STORM
        else:
            return WeatherCondition.CLOUDY

    def _degrees_to_direction(self, degrees: float) -> str:
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        return directions[round(degrees / 45) % 8]


# ============================================
# Anomaly Detector
# ============================================


class AnomalyDetector:
    """Detect weather anomalies based on regional thresholds"""

    def detect(self, weather: WeatherData) -> List[WeatherAnomaly]:
        anomalies = []
        thresholds = YEMEN_THRESHOLDS.get(weather.region, YEMEN_THRESHOLDS["المرتفعات"])

        # Extreme heat
        if weather.temperature_c > thresholds["temp_high"]:
            severity = (
                "critical"
                if weather.temperature_c > thresholds["temp_high"] + 7
                else "high"
            )
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="extreme_heat",
                    severity=severity,
                    description_ar=f"درجة حرارة مرتفعة جداً: {weather.temperature_c}°C",
                    description_en=f"Extreme heat: {weather.temperature_c}°C",
                    current_value=weather.temperature_c,
                    threshold=thresholds["temp_high"],
                    impact_crops=["الطماطم", "الخيار", "الفلفل", "الباذنجان"],
                    recommended_action_ar="زيادة الري، تظليل المحاصيل، الري في الصباح الباكر أو المساء",
                    recommended_action_en="Increase irrigation, shade crops, water early morning or evening",
                )
            )

        # Frost risk
        if weather.temperature_c < thresholds["temp_low"]:
            severity = "critical" if weather.temperature_c < 0 else "high"
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="frost_risk",
                    severity=severity,
                    description_ar=f"خطر الصقيع: {weather.temperature_c}°C",
                    description_en=f"Frost risk: {weather.temperature_c}°C",
                    current_value=weather.temperature_c,
                    threshold=thresholds["temp_low"],
                    impact_crops=["الموز", "البابايا", "المانجو", "الحمضيات"],
                    recommended_action_ar="تغطية المحاصيل الحساسة، إشعال نيران صغيرة بين الأشجار",
                    recommended_action_en="Cover sensitive crops, light small fires between trees",
                )
            )

        # High humidity (disease risk)
        if weather.humidity_percent > thresholds["humidity_high"]:
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="high_humidity",
                    severity="high",
                    description_ar=f"رطوبة عالية: {weather.humidity_percent}%",
                    description_en=f"High humidity: {weather.humidity_percent}%",
                    current_value=weather.humidity_percent,
                    threshold=thresholds["humidity_high"],
                    impact_crops=["العنب", "الطماطم", "البطاطس", "البصل"],
                    recommended_action_ar="مراقبة الأمراض الفطرية، تحسين التهوية، تجنب الري العلوي",
                    recommended_action_en="Monitor fungal diseases, improve ventilation, avoid overhead irrigation",
                )
            )

        # Heavy rain
        if weather.precipitation_mm > thresholds["rain_heavy"]:
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="heavy_rain",
                    severity="high",
                    description_ar=f"أمطار غزيرة: {weather.precipitation_mm} مم",
                    description_en=f"Heavy rain: {weather.precipitation_mm} mm",
                    current_value=weather.precipitation_mm,
                    threshold=thresholds["rain_heavy"],
                    impact_crops=["القمح", "الشعير", "البن", "القات"],
                    recommended_action_ar="التأكد من الصرف الجيد، منع تجمع المياه حول النباتات",
                    recommended_action_en="Ensure good drainage, prevent water pooling around plants",
                )
            )

        # Strong wind
        if weather.wind_speed_kmh > thresholds["wind_high"]:
            severity = "critical" if weather.wind_speed_kmh > 80 else "high"
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="strong_wind",
                    severity=severity,
                    description_ar=f"رياح قوية: {weather.wind_speed_kmh} كم/س",
                    description_en=f"Strong wind: {weather.wind_speed_kmh} km/h",
                    current_value=weather.wind_speed_kmh,
                    threshold=thresholds["wind_high"],
                    impact_crops=["الموز", "النخيل", "الذرة", "البابايا"],
                    recommended_action_ar="دعم النباتات الطويلة، تأمين البيوت البلاستيكية",
                    recommended_action_en="Support tall plants, secure greenhouses",
                )
            )

        # Low humidity (irrigation needed)
        if weather.humidity_percent < thresholds.get("humidity_low", 15):
            anomalies.append(
                WeatherAnomaly(
                    anomaly_type="low_humidity",
                    severity="medium",
                    description_ar=f"رطوبة منخفضة: {weather.humidity_percent}%",
                    description_en=f"Low humidity: {weather.humidity_percent}%",
                    current_value=weather.humidity_percent,
                    threshold=thresholds.get("humidity_low", 15),
                    impact_crops=["الخضروات الورقية", "الخيار", "الفراولة"],
                    recommended_action_ar="زيادة الري، استخدام الرش الضبابي",
                    recommended_action_en="Increase irrigation, use mist spraying",
                )
            )

        return anomalies


# ============================================
# Weather Service
# ============================================


class WeatherService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.scheduler = AsyncIOScheduler()
        self.client = OpenMeteoClient()
        self.detector = AnomalyDetector()
        self.last_readings: Dict[str, WeatherData] = {}

    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("weather_service_connected")

    async def start(self):
        # Schedule regular checks
        self.scheduler.add_job(
            self.check_all_locations,
            CronTrigger(minute="0,30"),  # Every 30 minutes
            id="weather_check",
            replace_existing=True,
        )

        # Daily summary at 6 AM Yemen time
        self.scheduler.add_job(
            self.publish_daily_summaries,
            CronTrigger(hour=6, minute=0, timezone="Asia/Aden"),
            id="daily_summary",
            replace_existing=True,
        )

        self.scheduler.start()

        # Initial check
        await self.check_all_locations()
        logger.info("weather_service_started", locations=len(MONITORING_LOCATIONS))

    async def check_all_locations(self):
        """Check weather for all monitored locations"""
        logger.info("checking_all_locations")

        for location in MONITORING_LOCATIONS:
            try:
                await self.check_location(location)
                await asyncio.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(
                    "location_check_failed", location=location["name"], error=str(e)
                )

    async def check_location(self, location: dict):
        """Check weather for a single location and publish events"""
        raw_data = await self.client.fetch_weather(location["lat"], location["lon"])
        if not raw_data:
            return

        weather = self.client.parse_response(raw_data, location)
        if not weather:
            return

        # Store reading
        self.last_readings[location["name"]] = weather

        logger.info(
            "weather_fetched",
            location=location["name"],
            temp=weather.temperature_c,
            humidity=weather.humidity_percent,
            condition=weather.condition.value,
        )

        # Detect and publish anomalies
        anomalies = self.detector.detect(weather)
        for anomaly in anomalies:
            await self.publish_anomaly(weather, anomaly, location)

    async def publish_anomaly(
        self, weather: WeatherData, anomaly: WeatherAnomaly, location: dict
    ):
        """Publish weather anomaly event"""
        event = create_event(
            event_type=EventTypes.WEATHER_ANOMALY_DETECTED,
            payload={
                "anomaly": {
                    "type": anomaly.anomaly_type,
                    "severity": anomaly.severity,
                    "description": {
                        "ar": anomaly.description_ar,
                        "en": anomaly.description_en,
                    },
                    "current_value": anomaly.current_value,
                    "threshold": anomaly.threshold,
                    "impact_crops": anomaly.impact_crops,
                    "recommended_action": {
                        "ar": anomaly.recommended_action_ar,
                        "en": anomaly.recommended_action_en,
                    },
                },
                "weather": weather.to_dict(),
                "location": {
                    "name": location["name"],
                    "name_en": location["name_en"],
                    "region": location["region"],
                    "lat": location["lat"],
                    "lon": location["lon"],
                },
            },
            tenant_id="default",
        )

        await self.js.publish(
            subject=EventTypes.WEATHER_ANOMALY_DETECTED,
            payload=json.dumps(event, ensure_ascii=False).encode(),
        )

        event_logger.published(
            EventTypes.WEATHER_ANOMALY_DETECTED,
            anomaly_type=anomaly.anomaly_type,
            severity=anomaly.severity,
            location=location["name"],
        )

        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.WEATHER_ANOMALY_DETECTED,
            tenant_id="default",
        ).inc()

    async def publish_daily_summaries(self):
        """Publish daily weather summary for each location"""
        for location in MONITORING_LOCATIONS:
            try:
                raw_data = await self.client.fetch_weather(
                    location["lat"], location["lon"]
                )
                if not raw_data:
                    continue

                weather = self.client.parse_response(raw_data, location)
                if not weather:
                    continue

                event = create_event(
                    event_type=EventTypes.WEATHER_DAILY_SUMMARY,
                    payload={
                        "date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "location": {
                            "name": location["name"],
                            "name_en": location["name_en"],
                            "region": location["region"],
                        },
                        "summary": weather.to_dict(),
                        "agricultural_impact": self._assess_agricultural_impact(
                            weather
                        ),
                        "forecast_available": True,
                    },
                    tenant_id="default",
                )

                await self.js.publish(
                    subject=EventTypes.WEATHER_DAILY_SUMMARY,
                    payload=json.dumps(event, ensure_ascii=False).encode(),
                )

                event_logger.published(
                    EventTypes.WEATHER_DAILY_SUMMARY, location=location["name"]
                )
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(
                    "daily_summary_failed", location=location["name"], error=str(e)
                )

    def _assess_agricultural_impact(self, weather: WeatherData) -> dict:
        """Assess agricultural impact of current weather"""
        return {
            "irrigation_needed": weather.precipitation_mm < 5
            and weather.temperature_c > 25,
            "spray_conditions_good": (
                weather.wind_speed_kmh < 15
                and weather.precipitation_mm == 0
                and weather.humidity_percent < 80
            ),
            "harvest_conditions_good": (
                weather.precipitation_mm == 0 and weather.humidity_percent < 70
            ),
            "frost_risk": weather.temperature_c < 5,
            "heat_stress_risk": weather.temperature_c > 38,
            "disease_risk_high": weather.humidity_percent > 85
            and weather.temperature_c > 20,
            "pollination_conditions": 20 < weather.temperature_c < 30
            and weather.wind_speed_kmh < 20,
        }

    async def stop(self):
        self.scheduler.shutdown()
        if self.nc:
            await self.nc.close()
        logger.info("weather_service_stopped")


# ============================================
# FastAPI Application
# ============================================

weather_service = WeatherService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await weather_service.connect()
    await weather_service.start()
    yield
    await weather_service.stop()


app = FastAPI(
    title="Weather Service",
    description="SAHOOL - Weather Signal Producer (Layer 2) - NO PUBLIC API",
    version="1.0.0",
    lifespan=lifespan,
)


# Internal endpoints only (Layer 2 rule - no public routes)
@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = weather_service.nc and weather_service.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


@app.get("/internal/status")
async def internal_status():
    """Internal only - not exposed via Kong"""
    return {
        "service": SERVICE_NAME,
        "layer": SERVICE_LAYER,
        "monitoring_locations": len(MONITORING_LOCATIONS),
        "last_readings_count": len(weather_service.last_readings),
        "scheduler_running": (
            weather_service.scheduler.running if weather_service.scheduler else False
        ),
    }


@app.post("/internal/trigger")
async def internal_trigger():
    """Internal trigger for immediate check"""
    await weather_service.check_all_locations()
    return {
        "message": "Weather check triggered",
        "locations": len(MONITORING_LOCATIONS),
    }


@app.get("/metrics")
async def metrics():
    from shared.metrics import get_metrics, get_metrics_content_type
    from fastapi.responses import Response

    return Response(content=get_metrics(), media_type=get_metrics_content_type())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8084")))
