"""
SAHOOL Weather Core - Main API Service
Agricultural weather assessment and alerts
Port: 8098

Enhanced with GDD, ET0, Spray Windows from v15.3
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .agricultural import (
    CropType,
    calculate_et0,
    calculate_gdd,
    find_spray_windows,
    get_crop_calendar,
)
from .events import get_publisher
from .providers import MockWeatherProvider, OpenMeteoProvider
from .risks import assess_weather, get_irrigation_adjustment, heat_stress_risk

# Configuration
USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌤️ Starting Weather Core Service...")

    # Initialize weather provider
    if USE_MOCK_WEATHER:
        app.state.weather_provider = MockWeatherProvider()
        print("📋 Using mock weather provider")
    else:
        app.state.weather_provider = OpenMeteoProvider()
        print("🌐 Using Open-Meteo weather provider")

    # Initialize publisher
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        print("✅ Weather Core ready on port 8098")
    except Exception as e:
        print(f"⚠️ NATS connection failed: {e}")
        app.state.publisher = None

    yield

    # Cleanup
    await app.state.weather_provider.close()
    if app.state.publisher:
        await app.state.publisher.close()
    print("👋 Weather Core shutting down")


app = FastAPI(
    title="SAHOOL Weather Core",
    description="Agricultural weather assessment, forecasting, and alerts",
    version="15.3.3",
    lifespan=lifespan,
)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    return {"status": "ok", "service": "weather_core", "version": "15.3.3"}


# ============== Request Models ==============


class WeatherAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    precipitation_mm: Optional[float] = None
    uv_index: Optional[float] = None
    correlation_id: Optional[str] = None


class LocationRequest(BaseModel):
    tenant_id: str
    field_id: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    correlation_id: Optional[str] = None


class IrrigationRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    precipitation_mm: float = 0
    correlation_id: Optional[str] = None


# ============== Weather Endpoints ==============


@app.post("/weather/assess")
async def assess(req: WeatherAssessRequest):
    """
    Assess weather conditions and generate alerts

    Manual weather data input for assessment
    """
    alerts = assess_weather(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_mm=req.precipitation_mm,
        uv_index=req.uv_index,
    )

    # Publish alerts
    event_ids = []
    if app.state.publisher and alerts:
        for alert in alerts:
            event_id = await app.state.publisher.publish_weather_alert(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                window_hours=alert.window_hours,
                title_ar=alert.title_ar,
                title_en=alert.title_en,
                correlation_id=req.correlation_id,
            )
            event_ids.append(event_id)

    return {
        "field_id": req.field_id,
        "alerts": [a.to_dict() for a in alerts],
        "alert_count": len(alerts),
        "event_ids": event_ids,
        "published": len(event_ids) > 0,
    }


@app.post("/weather/current")
async def get_current_weather(req: LocationRequest):
    """
    Get current weather from API provider

    Uses Open-Meteo (free) or mock provider
    """
    try:
        weather = await app.state.weather_provider.get_current(req.lat, req.lon)

        # Assess risks
        alerts = assess_weather(
            temp_c=weather.temperature_c,
            humidity_pct=weather.humidity_pct,
            wind_speed_kmh=weather.wind_speed_kmh,
            precipitation_mm=weather.precipitation_mm,
            uv_index=weather.uv_index,
        )

        # Publish alerts
        event_ids = []
        if app.state.publisher and alerts:
            for alert in alerts:
                event_id = await app.state.publisher.publish_weather_alert(
                    tenant_id=req.tenant_id,
                    field_id=req.field_id,
                    alert_type=alert.alert_type,
                    severity=alert.severity,
                    window_hours=alert.window_hours,
                    title_ar=alert.title_ar,
                    title_en=alert.title_en,
                    correlation_id=req.correlation_id,
                )
                event_ids.append(event_id)

        return {
            "field_id": req.field_id,
            "location": {"lat": req.lat, "lon": req.lon},
            "current": {
                "temperature_c": weather.temperature_c,
                "humidity_pct": weather.humidity_pct,
                "wind_speed_kmh": weather.wind_speed_kmh,
                "wind_direction_deg": weather.wind_direction_deg,
                "precipitation_mm": weather.precipitation_mm,
                "cloud_cover_pct": weather.cloud_cover_pct,
                "pressure_hpa": weather.pressure_hpa,
                "uv_index": weather.uv_index,
                "timestamp": weather.timestamp,
            },
            "alerts": [a.to_dict() for a in alerts],
            "event_ids": event_ids,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@app.post("/weather/forecast")
async def get_forecast(req: LocationRequest, days: int = 7):
    """
    Get weather forecast

    Args:
        days: Number of forecast days (1-16)
    """
    try:
        forecast = await app.state.weather_provider.get_daily_forecast(
            req.lat, req.lon, min(days, 16)
        )

        return {
            "field_id": req.field_id,
            "location": {"lat": req.lat, "lon": req.lon},
            "forecast": [
                {
                    "date": f.date,
                    "temp_max_c": f.temp_max_c,
                    "temp_min_c": f.temp_min_c,
                    "precipitation_mm": f.precipitation_mm,
                    "precipitation_probability_pct": f.precipitation_probability_pct,
                    "wind_speed_max_kmh": f.wind_speed_max_kmh,
                    "uv_index_max": f.uv_index_max,
                    "sunrise": f.sunrise,
                    "sunset": f.sunset,
                }
                for f in forecast
            ],
            "days": len(forecast),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@app.post("/weather/irrigation")
async def irrigation_adjustment(req: IrrigationRequest):
    """
    Calculate irrigation adjustment based on weather

    Returns adjustment factor and recommendations
    """
    adjustment = get_irrigation_adjustment(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_mm=req.precipitation_mm,
    )

    # Publish event
    event_id = None
    if app.state.publisher:
        event_id = await app.state.publisher.publish_irrigation_adjustment(
            tenant_id=req.tenant_id,
            field_id=req.field_id,
            adjustment_factor=adjustment["adjustment_factor"],
            recommendation_ar=adjustment["recommendation_ar"],
            recommendation_en=adjustment["recommendation_en"],
            correlation_id=req.correlation_id,
        )

    return {
        "field_id": req.field_id,
        "weather_input": {
            "temp_c": req.temp_c,
            "humidity_pct": req.humidity_pct,
            "wind_speed_kmh": req.wind_speed_kmh,
            "precipitation_mm": req.precipitation_mm,
        },
        **adjustment,
        "event_id": event_id,
        "published": event_id is not None,
    }


@app.get("/weather/heat-stress/{temp_c}")
def check_heat_stress(temp_c: float):
    """Quick heat stress check for a temperature"""
    alert_type, severity = heat_stress_risk(temp_c)

    return {
        "temperature_c": temp_c,
        "alert_type": alert_type,
        "severity": severity,
        "at_risk": severity != "none",
    }


# ============== Agricultural Endpoints (from v15.3) ==============


class GDDRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_max_c: float = Field(ge=-50, le=60)
    temp_min_c: float = Field(ge=-50, le=60)
    crop: str = "tomato"
    accumulated_gdd: float = 0
    correlation_id: Optional[str] = None


class ET0Request(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0)
    solar_radiation_mj: float = Field(default=20.0, ge=0)
    elevation_m: float = Field(default=1000, ge=0)
    correlation_id: Optional[str] = None


@app.post("/weather/gdd")
async def calculate_growing_degree_days(req: GDDRequest):
    """
    Calculate Growing Degree Days (GDD) for crop development tracking

    GDD helps predict crop development stages based on heat accumulation.
    Different crops have different base temperatures for growth.

    Returns:
        - gdd_today: Today's GDD contribution
        - gdd_accumulated: Total accumulated GDD
        - progress_pct: Progress toward maturity (if known)
        - days_to_maturity: Estimated days remaining
    """
    try:
        crop_type = CropType(req.crop.lower())
    except ValueError:
        crop_type = CropType.TOMATO

    result = calculate_gdd(
        temp_max_c=req.temp_max_c,
        temp_min_c=req.temp_min_c,
        crop=crop_type,
        accumulated_gdd=req.accumulated_gdd,
    )

    return {
        "field_id": req.field_id,
        "crop": result.crop,
        "crop_name_ar": result.crop_name_ar,
        "base_temp_c": result.base_temp_c,
        "gdd_today": result.gdd_today,
        "gdd_accumulated": result.gdd_accumulated,
        "gdd_to_maturity": result.gdd_to_maturity,
        "progress_pct": result.progress_pct,
        "days_to_maturity": result.days_to_maturity,
    }


@app.post("/weather/et0")
async def calculate_evapotranspiration(req: ET0Request):
    """
    Calculate Reference Evapotranspiration (ET0) using Penman-Monteith

    ET0 indicates crop water requirements based on weather conditions.
    Higher ET0 = more water loss = more irrigation needed.

    Returns:
        - et0_mm: Reference ET in mm/day
        - irrigation_need_ar/en: Irrigation recommendation
        - factors: Input factors used in calculation
    """
    result = calculate_et0(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        solar_radiation_mj=req.solar_radiation_mj,
        elevation_m=req.elevation_m,
    )

    return {
        "field_id": req.field_id,
        "et0_mm": result.et0_mm,
        "irrigation_need_ar": result.irrigation_need_ar,
        "irrigation_need_en": result.irrigation_need_en,
        "factors": result.factors,
    }


@app.post("/weather/spray-windows")
async def get_spray_windows(req: LocationRequest):
    """
    Find optimal spray windows in the forecast

    Analyzes hourly forecast to find windows where:
    - Wind speed < 15 km/h
    - No rain expected (< 20% probability)
    - Temperature 15-35°C
    - Humidity 40-80%

    Returns:
        List of spray windows sorted by suitability score
    """
    try:
        # Get hourly forecast
        hourly = await app.state.weather_provider.get_hourly_forecast(
            req.lat, req.lon, hours=48
        )

        # Convert to format expected by find_spray_windows
        hourly_data = [
            {
                "datetime": h.datetime,
                "temp_c": h.temperature_c,
                "humidity_pct": h.humidity_pct,
                "wind_speed_kmh": h.wind_speed_kmh,
                "precipitation_prob_pct": h.precipitation_probability_pct,
            }
            for h in hourly
        ]

        windows = find_spray_windows(hourly_data, min_hours=2)

        return {
            "field_id": req.field_id,
            "location": {"lat": req.lat, "lon": req.lon},
            "windows": [
                {
                    "start_time": w.start_time.isoformat() if w.start_time else None,
                    "end_time": w.end_time.isoformat() if w.end_time else None,
                    "suitability_score": w.suitability_score,
                    "conditions": w.conditions,
                }
                for w in windows
            ],
            "windows_count": len(windows),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spray window error: {str(e)}")


@app.get("/weather/crop-calendar/{crop}")
def get_crop_calendar_info(
    crop: str,
    month: int = Query(default=None, ge=1, le=12, description="Month (1-12), defaults to current"),
):
    """
    Get agricultural calendar for a specific crop

    Provides:
    - Current activity phase (planting/growing/harvest)
    - Optimal temperature range
    - Water requirements
    - Planting and harvest months

    Supported crops: tomato, wheat, coffee, banana, potato, corn,
                    cotton, sorghum, mango, grape, date_palm, qat, onion
    """
    try:
        crop_type = CropType(crop.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown crop: {crop}. Supported: {[c.value for c in CropType]}",
        )

    current_month = month or datetime.now().month
    calendar = get_crop_calendar(crop_type, current_month)

    return calendar


@app.get("/weather/crops")
def list_supported_crops():
    """List all supported crops with their Arabic names"""
    from .agricultural import CROP_CALENDARS

    return {
        "crops": [
            {
                "id": crop.value,
                "name_ar": info["name_ar"],
                "optimal_temp": info["optimal_temp"],
                "water_need": info["water_need"],
            }
            for crop, info in CROP_CALENDARS.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8098))
    uvicorn.run(app, host="0.0.0.0", port=port)
