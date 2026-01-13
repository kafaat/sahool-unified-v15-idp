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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

# Add shared modules to path
SHARED_PATH = Path("/app/shared")
if not SHARED_PATH.exists():
    # Fallback for local development
    SHARED_PATH = Path(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# Import unified error handling
from shared.errors_py import (
    ExternalServiceException,
    InternalServerException,
    add_request_id_middleware,
    setup_exception_handlers,
)

from .events import get_publisher
from .providers import MockWeatherProvider, MultiWeatherService, OpenMeteoProvider
from .risks import (
    assess_weather,
    calculate_chill_hours,
    calculate_drought_index,
    calculate_evapotranspiration,
    calculate_frost_risk,
    calculate_growing_degree_days,
    calculate_heat_stress_index,
    calculate_spray_window,
    get_irrigation_adjustment,
    heat_stress_risk,
)

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
            "providers": [{"name": "Open-Meteo", "configured": True, "type": "OpenMeteoProvider"}],
            "total": 1,
            "configured": 1,
        }


# ============== Advanced Agricultural Endpoints ==============


class ETRequest(BaseModel):
    """Evapotranspiration calculation request"""

    tenant_id: str
    field_id: str
    temp_c: float = Field(ge=-50, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0)
    solar_radiation_mj: float = Field(default=15.0, ge=0, le=50)


class GDDRequest(BaseModel):
    """Growing Degree Days calculation request"""

    tenant_id: str
    field_id: str
    temp_max_c: float = Field(ge=-50, le=60)
    temp_min_c: float = Field(ge=-50, le=60)
    base_temp_c: float = Field(default=10.0, ge=0, le=30)
    upper_temp_c: float = Field(default=30.0, ge=20, le=50)


class SprayWindowRequest(BaseModel):
    """Spray window assessment request"""

    tenant_id: str
    field_id: str
    temp_c: float = Field(ge=-50, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0)
    precipitation_probability: float = Field(default=0, ge=0, le=100)


@app.post("/weather/evapotranspiration")
async def calculate_et(req: ETRequest):
    """
    Calculate Reference Evapotranspiration (ET0)
    حساب التبخر-نتح المرجعي

    Uses FAO-56 Penman-Monteith equation (simplified).
    Essential for irrigation scheduling.

    Returns:
        ET0 in mm/day with irrigation recommendations
    """
    result = calculate_evapotranspiration(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        solar_radiation_mj=req.solar_radiation_mj,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "evapotranspiration": result,
    }


@app.post("/weather/gdd")
async def calculate_gdd(req: GDDRequest):
    """
    Calculate Growing Degree Days (GDD)
    حساب أيام النمو الحراري

    GDD predicts crop development stages based on accumulated heat.
    Essential for phenology modeling and harvest prediction.

    Returns:
        Daily GDD with growth rate classification
    """
    result = calculate_growing_degree_days(
        temp_max_c=req.temp_max_c,
        temp_min_c=req.temp_min_c,
        base_temp_c=req.base_temp_c,
        upper_temp_c=req.upper_temp_c,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "growing_degree_days": result,
    }


@app.post("/weather/spray-window")
async def assess_spray_window(req: SprayWindowRequest):
    """
    Assess spray window suitability
    تقييم مدى ملاءمة نافذة الرش

    Evaluates if current conditions are suitable for pesticide/herbicide application.
    Considers temperature, humidity, wind, and precipitation probability.

    Returns:
        Spray suitability score and recommendations
    """
    result = calculate_spray_window(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_probability=req.precipitation_probability,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "spray_window": result,
    }


@app.post("/weather/agricultural-report")
async def get_agricultural_report(req: LocationRequest):
    """
    Comprehensive agricultural weather report
    تقرير الطقس الزراعي الشامل

    Combines current weather, alerts, ET0, GDD, and spray window
    into a single comprehensive report for farmers.
    """
    # Get current weather
    if app.state.multi_provider:
        weather_data = await app.state.multi_provider.get_current_weather(lat=req.lat, lon=req.lon)
    else:
        weather_data = await app.state.weather_provider.get_current_weather(
            lat=req.lat, lon=req.lon
        )

    if "error" in weather_data:
        raise ExternalServiceException(
            service_name="Weather Provider", message=weather_data["error"]
        )

    temp_c = weather_data.get("temperature_c", 25)
    humidity_pct = weather_data.get("humidity_percent", 50)
    wind_speed_kmh = weather_data.get("wind_speed_kmh", 10)

    # Calculate all metrics
    et_result = calculate_evapotranspiration(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    gdd_result = calculate_growing_degree_days(
        temp_max_c=temp_c + 5,  # Estimated daily range
        temp_min_c=temp_c - 5,
    )

    spray_result = calculate_spray_window(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    # Assess alerts
    alerts = assess_weather(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    # Irrigation adjustment
    irrigation = get_irrigation_adjustment(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "location": {"lat": req.lat, "lon": req.lon},
        "current_weather": weather_data,
        "evapotranspiration": et_result,
        "growing_degree_days": gdd_result,
        "spray_window": spray_result,
        "irrigation_adjustment": irrigation,
        "alerts": [a.to_dict() for a in alerts],
        "alert_count": len(alerts),
    }


# ============== Frost, Heat Stress & Chill Hours Endpoints ==============


class FrostRiskRequest(BaseModel):
    """Frost risk assessment request"""

    tenant_id: str
    field_id: str
    temp_c: float = Field(ge=-50, le=60, description="Temperature °C")
    humidity_pct: float = Field(ge=0, le=100, description="Humidity %")
    wind_speed_kmh: float = Field(ge=0, description="Wind speed km/h")
    cloud_cover_pct: float = Field(default=0, ge=0, le=100, description="Cloud cover %")
    dew_point_c: float | None = Field(default=None, ge=-50, le=50, description="Dew point °C")


class HeatStressRequest(BaseModel):
    """Heat stress assessment request"""

    tenant_id: str
    field_id: str
    temp_c: float = Field(ge=-50, le=60, description="Temperature °C")
    humidity_pct: float = Field(ge=0, le=100, description="Humidity %")
    solar_radiation_mj: float = Field(
        default=15.0, ge=0, le=50, description="Solar radiation MJ/m²/day"
    )
    wind_speed_kmh: float = Field(default=10.0, ge=0, description="Wind speed km/h")


class ChillHoursRequest(BaseModel):
    """Chill hours calculation request"""

    tenant_id: str
    field_id: str
    hourly_temps: list[float] = Field(..., description="List of hourly temperatures °C")
    model: str = Field(default="utah", description="Model: simple, utah, or dynamic")
    base_temp_c: float = Field(default=7.2, ge=0, le=15, description="Base temp for simple model")


class DroughtIndexRequest(BaseModel):
    """Drought index calculation request"""

    tenant_id: str
    field_id: str
    precipitation_mm: float = Field(ge=0, description="Total precipitation mm")
    et0_mm: float = Field(ge=0, description="Total ET0 mm")
    days: int = Field(default=30, ge=1, le=365, description="Period in days")


@app.post("/weather/frost-risk")
async def assess_frost_risk(req: FrostRiskRequest):
    """
    Assess frost risk and get protection recommendations
    تقييم خطر الصقيع والحصول على توصيات الحماية

    Evaluates frost risk based on temperature, humidity, wind, and cloud cover.
    Returns protection measures for different risk levels.
    """
    result = calculate_frost_risk(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        cloud_cover_pct=req.cloud_cover_pct,
        dew_point_c=req.dew_point_c,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "frost_risk": result,
    }


@app.post("/weather/heat-stress")
async def assess_heat_stress(req: HeatStressRequest):
    """
    Calculate heat stress index for crops
    حساب مؤشر الإجهاد الحراري للمحاصيل

    Evaluates heat stress using Temperature-Humidity Index (THI).
    Returns mitigation recommendations for high stress conditions.
    """
    result = calculate_heat_stress_index(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        solar_radiation_mj=req.solar_radiation_mj,
        wind_speed_kmh=req.wind_speed_kmh,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "heat_stress": result,
    }


@app.post("/weather/chill-hours")
async def calculate_chill(req: ChillHoursRequest):
    """
    Calculate chill hours/units for fruit trees
    حساب ساعات البرودة للأشجار المثمرة

    Supports multiple chill models:
    - simple: Hours below threshold
    - utah: Utah Chill Unit model (default, more accurate)
    - dynamic: Dynamic model for mild winters

    Returns chill units and which crops' requirements are satisfied.
    """
    result = calculate_chill_hours(
        hourly_temps=req.hourly_temps,
        model=req.model,
        base_temp_c=req.base_temp_c,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "chill_hours": result,
    }


@app.post("/weather/drought-index")
async def calculate_drought(req: DroughtIndexRequest):
    """
    Calculate drought stress index
    حساب مؤشر الإجهاد الجفافي

    Based on water balance (precipitation vs evapotranspiration).
    Returns irrigation recommendations.
    """
    result = calculate_drought_index(
        precipitation_mm=req.precipitation_mm,
        et0_mm=req.et0_mm,
        days=req.days,
    )

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "drought_index": result,
    }


@app.post("/weather/comprehensive-stress-report")
async def get_stress_report(req: LocationRequest):
    """
    Comprehensive weather stress report
    تقرير الإجهاد الجوي الشامل

    Combines frost risk, heat stress, spray window, and alerts
    into a single comprehensive stress assessment.
    """
    # Get current weather
    if app.state.multi_provider:
        weather_data = await app.state.multi_provider.get_current_weather(lat=req.lat, lon=req.lon)
    else:
        weather_data = await app.state.weather_provider.get_current_weather(
            lat=req.lat, lon=req.lon
        )

    if "error" in weather_data:
        raise ExternalServiceException(
            service_name="Weather Provider", message=weather_data["error"]
        )

    temp_c = weather_data.get("temperature_c", 25)
    humidity_pct = weather_data.get("humidity_percent", 50)
    wind_speed_kmh = weather_data.get("wind_speed_kmh", 10)
    cloud_cover_pct = weather_data.get("cloud_cover_percent", 50)

    # Calculate stress metrics
    frost_result = calculate_frost_risk(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
        cloud_cover_pct=cloud_cover_pct,
    )

    heat_result = calculate_heat_stress_index(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    spray_result = calculate_spray_window(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
    )

    # Determine overall stress level
    if frost_result["risk_level"] in ["critical", "high"] or heat_result["stress_level"] in [
        "extreme",
        "severe",
    ]:
        overall_status = "critical"
        overall_color = "red"
    elif frost_result["risk_level"] == "moderate" or heat_result["stress_level"] in ["high"]:
        overall_status = "warning"
        overall_color = "orange"
    elif frost_result["risk_level"] == "low" or heat_result["stress_level"] == "moderate":
        overall_status = "caution"
        overall_color = "yellow"
    else:
        overall_status = "normal"
        overall_color = "green"

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "location": {"lat": req.lat, "lon": req.lon},
        "current_weather": weather_data,
        "overall_status": overall_status,
        "overall_color": overall_color,
        "frost_risk": frost_result,
        "heat_stress": heat_result,
        "spray_window": spray_result,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8108))
    uvicorn.run(app, host="0.0.0.0", port=port)
