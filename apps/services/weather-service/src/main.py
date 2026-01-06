"""
SAHOOL Weather Core - Main API Service
Agricultural weather assessment and alerts
Port: 8108

Multi-Provider Support:
- Open-Meteo (Free - No API key required)
- OpenWeatherMap (Set OPENWEATHERMAP_API_KEY)
- WeatherAPI (Set WEATHERAPI_KEY)
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import ObservabilityMiddleware

from pydantic import BaseModel, Field

# Add shared modules to path
SHARED_PATH = Path("/app/shared")
if not SHARED_PATH.exists():
    # Fallback for local development
    SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# Import unified error handling
from errors_py import (
    ExternalServiceException,
    InternalServerException,
    add_request_id_middleware,
    setup_exception_handlers,
)

from .events import get_publisher
from .providers import MockWeatherProvider, MultiWeatherService, OpenMeteoProvider
from .risks import assess_weather, get_irrigation_adjustment, heat_stress_risk

# Configuration
USE_MOCK_WEATHER = os.getenv("USE_MOCK_WEATHER", "false").lower() == "true"
USE_MULTI_PROVIDER = os.getenv("USE_MULTI_PROVIDER", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌤️ Starting Weather Core Service...")

    # Initialize weather provider
    if USE_MOCK_WEATHER:
        app.state.weather_provider = MockWeatherProvider()
        app.state.multi_provider = None
        print("📋 Using mock weather provider")
    elif USE_MULTI_PROVIDER:
        app.state.multi_provider = MultiWeatherService()
        app.state.weather_provider = OpenMeteoProvider()  # Fallback
        providers = app.state.multi_provider.get_available_providers()
        provider_names = [p["name"] for p in providers if p["configured"]]
        print(f"🌐 Using multi-provider weather service: {', '.join(provider_names)}")
    else:
        app.state.weather_provider = OpenMeteoProvider()
        app.state.multi_provider = None
        print("🌐 Using Open-Meteo weather provider")

    # Initialize publisher
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        print("✅ Weather Core ready on port 8108")
    except Exception as e:
        print(f"⚠️ NATS connection failed: {e}")
        app.state.publisher = None

    yield

    # Cleanup
    if app.state.multi_provider:
        await app.state.multi_provider.close()
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

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)


# ============== Health Check ==============


@app.get("/healthz")
def health():
    """Health check endpoint with service info"""
    from datetime import datetime

    return {
        "status": "healthy",
        "service": "weather-service",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============== Request Models ==============


class WeatherAssessRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: float | None = None
    wind_speed_kmh: float | None = None
    precipitation_mm: float | None = None
    uv_index: float | None = None
    correlation_id: str | None = None


class LocationRequest(BaseModel):
    tenant_id: str
    field_id: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    correlation_id: str | None = None


class IrrigationRequest(BaseModel):
    tenant_id: str
    field_id: str
    temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    precipitation_mm: float = 0
    correlation_id: str | None = None


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

    Uses multi-provider service with automatic fallback:
    - Open-Meteo (free)
    - OpenWeatherMap (if OPENWEATHERMAP_API_KEY set)
    - WeatherAPI (if WEATHERAPI_KEY set)
    """
    try:
        # Use multi-provider service if available
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_current(req.lat, req.lon)
            if not result.success:
                raise ExternalServiceException.weather_service(
                    details={
                        "error": result.error,
                        "error_ar": result.error_ar,
                        "failed_providers": result.failed_providers,
                    }
                )
            weather = result.data
            provider = result.provider
        else:
            weather = await app.state.weather_provider.get_current(req.lat, req.lon)
            provider = "Open-Meteo"

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
            "provider": provider,
            "current": {
                "temperature_c": weather.temperature_c,
                "humidity_pct": weather.humidity_pct,
                "wind_speed_kmh": weather.wind_speed_kmh,
                "wind_direction_deg": weather.wind_direction_deg,
                "wind_direction": getattr(weather, "wind_direction", None),
                "precipitation_mm": weather.precipitation_mm,
                "cloud_cover_pct": weather.cloud_cover_pct,
                "pressure_hpa": weather.pressure_hpa,
                "uv_index": weather.uv_index,
                "condition": getattr(weather, "condition", None),
                "condition_ar": getattr(weather, "condition_ar", None),
                "timestamp": weather.timestamp,
            },
            "alerts": [a.to_dict() for a in alerts],
            "event_ids": event_ids,
        }

    except (ExternalServiceException, InternalServerException):
        raise
    except Exception as e:
        raise ExternalServiceException.weather_service(e) from e


@app.post("/weather/forecast")
async def get_forecast(req: LocationRequest, days: int = 7):
    """
    Get weather forecast

    Args:
        days: Number of forecast days (1-16)
    """
    try:
        # Use multi-provider service if available
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_daily_forecast(
                req.lat, req.lon, min(days, 16)
            )
            if not result.success:
                raise ExternalServiceException.weather_service(
                    details={
                        "error": result.error,
                        "error_ar": result.error_ar,
                        "failed_providers": result.failed_providers,
                    }
                )
            forecast = result.data
            provider = result.provider
        else:
            forecast = await app.state.weather_provider.get_daily_forecast(
                req.lat, req.lon, min(days, 16)
            )
            provider = "Open-Meteo"

        return {
            "field_id": req.field_id,
            "location": {"lat": req.lat, "lon": req.lon},
            "provider": provider,
            "forecast": [
                {
                    "date": f.date,
                    "temp_max_c": f.temp_max_c,
                    "temp_min_c": f.temp_min_c,
                    "precipitation_mm": f.precipitation_mm,
                    "precipitation_probability_pct": f.precipitation_probability_pct,
                    "wind_speed_max_kmh": f.wind_speed_max_kmh,
                    "uv_index_max": f.uv_index_max,
                    "condition": getattr(f, "condition", None),
                    "condition_ar": getattr(f, "condition_ar", None),
                    "sunrise": getattr(f, "sunrise", None),
                    "sunset": getattr(f, "sunset", None),
                }
                for f in forecast
            ],
            "days": len(forecast),
        }

    except (ExternalServiceException, InternalServerException):
        raise
    except Exception as e:
        raise ExternalServiceException.weather_service(e) from e


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


@app.get("/weather/providers")
async def get_providers():
    """
    Get list of available weather providers
    الحصول على قائمة مزودي الطقس المتاحين
    """
    if app.state.multi_provider:
        providers = app.state.multi_provider.get_available_providers()
        return {
            "multi_provider_enabled": True,
            "providers": providers,
            "total": len(providers),
            "configured": len([p for p in providers if p["configured"]]),
        }
    else:
        return {
            "multi_provider_enabled": False,
            "providers": [
                {"name": "Open-Meteo", "configured": True, "type": "OpenMeteoProvider"}
            ],
            "total": 1,
            "configured": 1,
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8108))
    uvicorn.run(app, host="0.0.0.0", port=port)
