"""
SAHOOL Weather Core - Main API Service
Agricultural weather assessment and alerts
Port: 8092

Multi-Provider Support:
- Open-Meteo (Free - No API key required)
- OpenWeatherMap (Set OPENWEATHERMAP_API_KEY)
- WeatherAPI (Set WEATHERAPI_KEY)
"""

import os
import sys
from contextlib import asynccontextmanager
from enum import StrEnum
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException

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
import structlog

# Configure structured logging (replaces stdlib logging init)
from shared.logging_config import setup_logging

setup_logging("weather-service")
logger = structlog.get_logger()

# OpenTelemetry tracing (must be called before FastAPI instrumentation)
from shared.observability.tracing import setup_tracing

_tracer = setup_tracing("weather-service")

# Authentication imports
from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import (
    ExternalServiceException,
    InternalServerException,
    add_request_id_middleware,
    setup_exception_handlers,
)

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


# Shared weather alerts module integration
try:
    from shared.weather_alerts import AlertGeneratorConfig, WeatherAlertGenerator

    HAS_SHARED_ALERTS = True
except ImportError:
    HAS_SHARED_ALERTS = False

# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from datetime import UTC

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

# Prometheus metric definitions
if HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "weather_requests_total",
        "Total weather API requests",
        ["endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "weather_request_duration_seconds",
        "Weather API request latency",
        ["endpoint"],
    )
    PROVIDER_FALLBACK = Counter(
        "weather_provider_fallback_total",
        "Weather provider fallback events",
        ["from_provider", "to_provider"],
    )


# Prometheus middleware to record metrics per request
if HAS_PROMETHEUS:
    from starlette.middleware.base import BaseHTTPMiddleware

    class PrometheusMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            import time as _time

            endpoint = request.url.path
            start = _time.time()
            response = await call_next(request)
            duration = _time.time() - start
            REQUEST_COUNT.labels(endpoint=endpoint, status=response.status_code).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
            return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", service="weather-service")

    # Initialize weather provider
    if USE_MOCK_WEATHER:
        app.state.weather_provider = MockWeatherProvider()
        app.state.multi_provider = None
        logger.info("weather_provider_initialized", provider="mock")
    elif USE_MULTI_PROVIDER:
        app.state.multi_provider = MultiWeatherService()
        app.state.weather_provider = OpenMeteoProvider()  # Fallback
        providers = app.state.multi_provider.get_available_providers()
        provider_names = [p["name"] for p in providers if p["configured"]]
        logger.info("weather_provider_initialized", provider="multi", providers=provider_names)
    else:
        app.state.weather_provider = OpenMeteoProvider()
        app.state.multi_provider = None
        logger.info("weather_provider_initialized", provider="open-meteo")

    # Initialize shared weather alerts module
    if HAS_SHARED_ALERTS:
        app.state.shared_alert_generator = WeatherAlertGenerator(AlertGeneratorConfig())
        logger.info("shared_alert_generator_initialized")
    else:
        app.state.shared_alert_generator = None
        logger.info("shared_alert_generator_unavailable", reason="import_failed")

    # Initialize publisher
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        logger.info("service_ready", service="weather-service", port=8092)
    except Exception as e:
        logger.warning("nats_connection_failed", error=str(e))
        app.state.publisher = None

    yield

    # Cleanup
    logger.info("service_shutting_down", service="weather-service")
    for name in ("multi_provider", "weather_provider", "publisher"):
        resource = getattr(app.state, name, None)
        if resource:
            try:
                await resource.close()
            except Exception as e:
                logger.warning("shutdown_close_error", resource=name, error=str(e))
    logger.info("service_shutdown_complete", service="weather-service")


app = FastAPI(
    title="SAHOOL Weather Core",
    description="Agricultural weather assessment, forecasting, and alerts",
    version="16.0.0",
    lifespan=lifespan,
)

# Instrument FastAPI with OpenTelemetry
_tracer.instrument_fastapi(app)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Prometheus request metrics middleware
if HAS_PROMETHEUS:
    app.add_middleware(PrometheusMiddleware)

# CORS - Secure configuration
try:
    from starlette.middleware.cors import CORSMiddleware

    try:
        from shared.cors_config import CORS_SETTINGS

        app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
    except ImportError:
        ALLOWED_ORIGINS = [
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
            ).split(",")
            if o.strip()
        ]
        _allow_credentials = "*" not in ALLOWED_ORIGINS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=ALLOWED_ORIGINS,
            allow_credentials=_allow_credentials,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
        )
except ImportError:
    pass

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Add tenant context middleware
try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
except ImportError:
    pass


# ============== Tenant Isolation ==============


def _enforce_tenant(user: User, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "missing_tenant",
                "message_en": "Token missing tenant ID",
                "message_ar": "الرمز لا يحتوي على معرف المستأجر",
            },
        )
    if user.tenant_id != requested_tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                "message_en": "Cannot access another tenant's data",
            },
        )


# ============== Health Check ==============


@app.get("/healthz")
def health():
    """Health check endpoint (liveness probe)"""
    from datetime import datetime, timezone

    return {
        "status": "healthy",
        "service": "weather-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz")
def readiness():
    checks = {}

    # Check NATS connection
    publisher = getattr(app.state, "publisher", None)
    if publisher is not None:
        checks["nats"] = "connected" if getattr(publisher, "_connected", False) else "disconnected"
    else:
        checks["nats"] = "not_configured"

    # Check if providers are available
    multi_provider = getattr(app.state, "multi_provider", None)
    weather_provider = getattr(app.state, "weather_provider", None)
    if multi_provider is not None or weather_provider is not None:
        checks["providers"] = "available"
    else:
        checks["providers"] = "not_initialized"

    all_ready = all(v not in ("disconnected", "not_initialized") for v in checks.values())

    return {
        "status": "ready" if all_ready else "degraded",
        "service": "weather-service",
        "version": "16.0.0",
        "checks": checks,
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not HAS_PROMETHEUS:
        from starlette.responses import Response

        return Response(content="prometheus_client not installed", status_code=501)
    from starlette.responses import Response

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ============== Request Models ==============


class WeatherAssessRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(max_length=100)
    temp_c: float = Field(ge=-60, le=60)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    wind_speed_kmh: float | None = Field(default=None, ge=0, le=400)
    precipitation_mm: float | None = Field(default=None, ge=0, le=500)
    uv_index: float | None = Field(default=None, ge=0, le=20)
    correlation_id: str | None = Field(default=None, max_length=200)


class LocationRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    correlation_id: str | None = Field(default=None, max_length=200)


class IrrigationRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(max_length=100)
    temp_c: float = Field(ge=-60, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0, le=400)
    precipitation_mm: float = Field(default=0, ge=0, le=500)
    correlation_id: str | None = Field(default=None, max_length=200)


# ============== Weather Endpoints ==============


@app.post("/weather/assess")
async def assess(req: WeatherAssessRequest, user: User = Depends(get_current_user)):
    """
    Assess weather conditions and generate alerts

    Manual weather data input for assessment
    """
    _enforce_tenant(user, req.tenant_id)

    alerts = assess_weather(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_mm=req.precipitation_mm,
        uv_index=req.uv_index,
    )

    # Publish alerts
    event_ids = []
    if getattr(app.state, "publisher", None) and alerts:
        for alert in alerts:
            try:
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
            except Exception as e:
                logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

    return {
        "field_id": req.field_id,
        "alerts": [a.to_dict() for a in alerts],
        "alert_count": len(alerts),
        "event_ids": event_ids,
        "published": len(event_ids) > 0,
    }


@app.post("/weather/current")
async def get_current_weather(req: LocationRequest, user: User = Depends(get_current_user)):
    """
    Get current weather from API provider

    Uses multi-provider service with automatic fallback:
    - Open-Meteo (free)
    - OpenWeatherMap (if OPENWEATHERMAP_API_KEY set)
    - WeatherAPI (if WEATHERAPI_KEY set)
    """
    _enforce_tenant(user, req.tenant_id)

    try:
        # Use multi-provider service if available
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_current(req.lat, req.lon, tenant_id=req.tenant_id)
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
        publisher = getattr(app.state, "publisher", None)
        if publisher and alerts:
            for alert in alerts:
                try:
                    event_id = await publisher.publish_weather_alert(
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
                except Exception as e:
                    logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

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
async def get_forecast(req: LocationRequest, days: int = 7, user: User = Depends(get_current_user)):
    """
    Get weather forecast

    Args:
        days: Number of forecast days (1-16)
    """
    _enforce_tenant(user, req.tenant_id)
    days = max(1, min(days, 16))

    try:
        # Use multi-provider service if available
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_daily_forecast(req.lat, req.lon, days, tenant_id=req.tenant_id)
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
            forecast = await app.state.weather_provider.get_daily_forecast(req.lat, req.lon, days)
            provider = "Open-Meteo"

        # Publish forecast issued event
        event_id = None
        publisher = getattr(app.state, "publisher", None)
        if publisher and forecast:
            try:
                event_id = await publisher.publish_forecast_issued(
                    tenant_id=req.tenant_id,
                    field_id=req.field_id,
                    provider=provider,
                    days=len(forecast),
                    correlation_id=req.correlation_id,
                )
            except Exception as pub_err:
                logger.warning("nats_publish_failed", error=str(pub_err), exc_info=True)

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
            "event_id": event_id,
        }

    except (ExternalServiceException, InternalServerException):
        raise
    except Exception as e:
        raise ExternalServiceException.weather_service(e) from e


# ─────────────────────────────────────────────────────────────────────────────
# Yemen-location-scoped weather endpoints
#
# These satisfy `WEATHER_ENDPOINTS.KONG_CURRENT_BY_LOCATION`,
# `KONG_FORECAST_BY_LOCATION`, and `KONG_LOCATIONS` in
# packages/shared-types/src/contracts/api-endpoints.ts. Web/mobile clients
# call them via the Kong-routed paths `/api/v1/weather/v1/{current,forecast,
# locations}`; the gateway strips `/api/v1/weather` and prepends `/weather`,
# so the upstream URLs the backend sees are `/weather/v1/...` — exactly what
# we register below.
#
# The locations table is a static dictionary of the 22 Yemen governorates
# (apps/services/weather-service/src/locations.py), so resolving a
# `location_id` to lat/lon is an in-process lookup with no extra latency.
# Once resolved, both endpoints reuse the existing multi-provider weather
# pipeline.
# ─────────────────────────────────────────────────────────────────────────────

from .locations import get_all_locations, get_location  # noqa: E402  (kept near the routes that use it)


@app.get("/weather/v1/locations")
async def list_yemen_locations(
    region: str | None = None,
    user: User = Depends(get_current_user),
):
    """List Yemen governorates with id/name/coords/region/elevation.

    Optional `?region=highland|coastal|desert|island` filters the result.
    Auth is required so we can enforce per-tenant rate limits even though
    the data itself is non-sensitive (all 22 governorates are public).
    """
    locations = get_all_locations()
    if region:
        region_norm = region.lower()
        locations = [loc for loc in locations if loc.get("region") == region_norm]
    return {
        "success": True,
        "data": locations,
        "total": len(locations),
    }


def _resolve_tenant_or_403(user: User) -> str:
    """Pull tenant_id off the authenticated user or raise 403.

    The Yemen-location endpoints are GET-only with no `tenant_id`
    query/body — the caller's tenant MUST come from the JWT. Falling
    back to a shared sentinel like "unknown" would silently merge
    quota/rate-limit counters across unrelated requests AND give us
    no way to attribute downstream provider charges, so we fail loud
    instead.

    Status code matches `_enforce_tenant` above (403 with
    error="missing_tenant") so a single client-side handler covers
    both endpoints families.
    """
    tenant_id = getattr(user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "missing_tenant",
                "message_en": "Token missing tenant ID",
                "message_ar": "الرمز لا يحتوي على معرف المستأجر",
            },
        )
    return str(tenant_id)


@app.get("/weather/v1/current/{location_id}")
async def get_current_weather_by_location(
    location_id: str,
    field_id: str = "",
    user: User = Depends(get_current_user),
):
    """Current weather for a Yemen governorate.

    Translates `location_id` → lat/lon via the static locations table, then
    delegates to the same multi-provider service used by `POST /weather/current`.
    Tenant scope comes from the JWT (no body / no `tenant_id` query) — keeps
    the contract aligned with how web/mobile call it (a plain GET with the
    bearer token only).
    """
    location = get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Yemen location '{location_id}' not found. Use /weather/v1/locations to list valid IDs.",
        )

    tenant_id = _resolve_tenant_or_403(user)

    # Wrap provider calls in the same try/except shape as POST /weather/current
    # (line 496) so transient network/timeout errors come out as a 502
    # ExternalServiceException via the unified error handler — NOT as a bare
    # 500 from the catch-all in shared/errors_py.
    try:
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_current(location["lat"], location["lon"], tenant_id=tenant_id)
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
            weather = await app.state.weather_provider.get_current(location["lat"], location["lon"])
            provider = "Open-Meteo"
    except (ExternalServiceException, InternalServerException):
        raise
    except Exception as exc:
        raise ExternalServiceException.weather_service(
            details={
                "error": f"Provider failed for location '{location_id.lower()}': {exc}",
                "location_id": location_id.lower(),
            }
        ) from exc

    return {
        "success": True,
        "data": {
            "location": {
                "id": location_id.lower(),
                "name_ar": location["name_ar"],
                "lat": location["lat"],
                "lon": location["lon"],
                "elevation": location["elevation"],
                "region": location["region"],
            },
            "field_id": field_id,
            "provider": provider,
            "current": {
                "temperature_c": weather.temperature_c,
                "humidity_pct": weather.humidity_pct,
                "wind_speed_kmh": weather.wind_speed_kmh,
                "wind_direction_deg": weather.wind_direction_deg,
                "precipitation_mm": weather.precipitation_mm,
                "cloud_cover_pct": weather.cloud_cover_pct,
                "pressure_hpa": weather.pressure_hpa,
                "uv_index": weather.uv_index,
                "condition": getattr(weather, "condition", None),
                "condition_ar": getattr(weather, "condition_ar", None),
                "timestamp": weather.timestamp,
            },
        },
    }


@app.get("/weather/v1/forecast/{location_id}")
async def get_forecast_by_location(
    location_id: str,
    days: int = 7,
    field_id: str = "",
    user: User = Depends(get_current_user),
):
    """N-day forecast for a Yemen governorate.

    Same lookup strategy as `/weather/v1/current/{location_id}`. `days`
    is aligned with POST /weather/forecast: 1..16 inclusive (Open-Meteo
    supports up to 16, the multi-provider service inherits that range).
    """
    if days < 1 or days > 16:
        raise HTTPException(status_code=422, detail="days must be between 1 and 16")

    location = get_location(location_id)
    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Yemen location '{location_id}' not found. Use /weather/v1/locations to list valid IDs.",
        )

    tenant_id = _resolve_tenant_or_403(user)

    # Mirror the existing POST /weather/forecast handler — it calls
    # get_daily_forecast (NOT get_forecast). The providers in
    # src/providers/multi_provider.py expose get_daily_forecast on every
    # adapter, returning a list[DailyForecast] directly. try/except
    # converts unexpected provider failures (timeouts, network) into the
    # ExternalServiceException 502 response shape — the catch-all in
    # shared/errors_py would otherwise emit a bare 500.
    try:
        if app.state.multi_provider:
            result = await app.state.multi_provider.get_daily_forecast(
                location["lat"], location["lon"], days, tenant_id=tenant_id
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
            forecast = await app.state.weather_provider.get_daily_forecast(location["lat"], location["lon"], days)
            provider = "Open-Meteo"
    except (ExternalServiceException, InternalServerException):
        raise
    except Exception as exc:
        raise ExternalServiceException.weather_service(
            details={
                "error": f"Provider failed for forecast at '{location_id.lower()}': {exc}",
                "location_id": location_id.lower(),
            }
        ) from exc

    # Match POST /weather/forecast's response shape so existing
    # web/mobile parsers continue to work — `forecast` is already a
    # list[DailyForecast], no `.daily` accessor needed. `days` reports
    # the actual returned horizon (POST /weather/forecast does the same
    # — `days: len(forecast)` at line 567), so an empty result honestly
    # advertises 0, not the requested ceiling.
    return {
        "success": True,
        "data": {
            "location": {
                "id": location_id.lower(),
                "name_ar": location["name_ar"],
                "lat": location["lat"],
                "lon": location["lon"],
                "elevation": location["elevation"],
                "region": location["region"],
            },
            "field_id": field_id,
            "provider": provider,
            "days": len(forecast or []),
            "forecast": [
                {
                    "date": getattr(f, "date", None),
                    "temp_max_c": getattr(f, "temp_max_c", None),
                    "temp_min_c": getattr(f, "temp_min_c", None),
                    "precipitation_mm": getattr(f, "precipitation_mm", None),
                    "precipitation_probability_pct": getattr(f, "precipitation_probability_pct", None),
                    "wind_speed_max_kmh": getattr(f, "wind_speed_max_kmh", None),
                    "uv_index_max": getattr(f, "uv_index_max", None),
                    "condition": getattr(f, "condition", None),
                    "condition_ar": getattr(f, "condition_ar", None),
                    "sunrise": getattr(f, "sunrise", None),
                    "sunset": getattr(f, "sunset", None),
                }
                for f in (forecast or [])
            ],
        },
    }


@app.post("/weather/irrigation")
async def irrigation_adjustment(req: IrrigationRequest, user: User = Depends(get_current_user)):
    """
    Calculate irrigation adjustment based on weather

    Returns adjustment factor and recommendations
    """
    _enforce_tenant(user, req.tenant_id)

    adjustment = get_irrigation_adjustment(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_mm=req.precipitation_mm,
    )

    # Publish event
    event_id = None
    publisher = getattr(app.state, "publisher", None)
    if publisher:
        try:
            event_id = await publisher.publish_irrigation_adjustment(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                adjustment_factor=adjustment["adjustment_factor"],
                recommendation_ar=adjustment["recommendation_ar"],
                recommendation_en=adjustment["recommendation_en"],
                correlation_id=req.correlation_id,
            )
        except Exception as e:
            logger.error("nats_publish_failed", subject="irrigation_adjustment", error=str(e), exc_info=True)

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
def check_heat_stress(temp_c: float, user: User = Depends(get_current_user)):
    """Quick heat stress check for a temperature"""
    alert_type, severity = heat_stress_risk(temp_c)

    return {
        "temperature_c": temp_c,
        "alert_type": alert_type,
        "severity": severity,
        "at_risk": severity != "none",
    }


@app.get("/weather/providers")
async def get_providers(user: User = Depends(get_current_user)):
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

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    temp_c: float = Field(ge=-50, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0, le=400)
    solar_radiation_mj: float = Field(default=15.0, ge=0, le=50)
    correlation_id: str | None = Field(default=None, max_length=200)


class GDDRequest(BaseModel):
    """Growing Degree Days calculation request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    temp_max_c: float = Field(ge=-50, le=60)
    temp_min_c: float = Field(ge=-50, le=60)
    base_temp_c: float = Field(default=10.0, ge=0, le=30)
    upper_temp_c: float = Field(default=30.0, ge=20, le=50)
    correlation_id: str | None = Field(default=None, max_length=200)


class SprayWindowRequest(BaseModel):
    """Spray window assessment request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    temp_c: float = Field(ge=-50, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_kmh: float = Field(ge=0, le=400)
    precipitation_probability: float = Field(default=0, ge=0, le=100)
    correlation_id: str | None = Field(default=None, max_length=200)


@app.post("/weather/evapotranspiration")
async def calculate_et(req: ETRequest, user: User = Depends(get_current_user)):
    """
    Calculate Reference Evapotranspiration (ET0)
    حساب التبخر-نتح المرجعي

    Uses FAO-56 Penman-Monteith equation (simplified).
    Essential for irrigation scheduling.

    Returns:
        ET0 in mm/day with irrigation recommendations
    """
    _enforce_tenant(user, req.tenant_id)

    result = calculate_evapotranspiration(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        solar_radiation_mj=req.solar_radiation_mj,
    )

    # Publish event for high ET conditions
    et0_mm = result.get("et0_mm", 0)
    if app.state.publisher and et0_mm > 7.0:
        try:
            await app.state.publisher.publish_weather_alert(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                alert_type="high_evapotranspiration",
                severity="warning",
                window_hours=24,
            )
        except Exception as e:
            logger.error("nats_publish_failed", subject="weather_alert", error=str(e))

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "evapotranspiration": result,
    }


@app.post("/weather/gdd")
async def calculate_gdd(req: GDDRequest, user: User = Depends(get_current_user)):
    """
    Calculate Growing Degree Days (GDD)
    حساب أيام النمو الحراري

    GDD predicts crop development stages based on accumulated heat.
    Essential for phenology modeling and harvest prediction.

    Returns:
        Daily GDD with growth rate classification
    """
    _enforce_tenant(user, req.tenant_id)

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
async def assess_spray_window(req: SprayWindowRequest, user: User = Depends(get_current_user)):
    """
    Assess spray window suitability
    تقييم مدى ملاءمة نافذة الرش

    Evaluates if current conditions are suitable for pesticide/herbicide application.
    Considers temperature, humidity, wind, and precipitation probability.

    Returns:
        Spray suitability score and recommendations
    """
    _enforce_tenant(user, req.tenant_id)

    result = calculate_spray_window(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        precipitation_probability=req.precipitation_probability,
    )

    if app.state.publisher and not result.get("is_suitable", True):
        try:
            await app.state.publisher.publish_weather_alert(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                alert_type="spray_window_unsuitable",
                severity="advisory",
                window_hours=6,
            )
        except Exception as e:
            logger.error("nats_publish_failed", subject="weather_alert", error=str(e))

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "spray_window": result,
    }


@app.post("/weather/agricultural-report")
async def get_agricultural_report(req: LocationRequest, user: User = Depends(get_current_user)):
    """
    Comprehensive agricultural weather report
    تقرير الطقس الزراعي الشامل

    Combines current weather, alerts, ET0, GDD, and spray window
    into a single comprehensive report for farmers.
    """
    _enforce_tenant(user, req.tenant_id)

    # Get current weather
    if app.state.multi_provider:
        result = await app.state.multi_provider.get_current(lat=req.lat, lon=req.lon)
        if not result.success:
            raise ExternalServiceException.weather_service(
                details={
                    "error": result.error,
                    "error_ar": result.error_ar,
                    "failed_providers": result.failed_providers,
                }
            )
        weather = result.data
        provider = getattr(result, "provider", "Open-Meteo")
    else:
        weather = await app.state.weather_provider.get_current(lat=req.lat, lon=req.lon)
        provider = "Open-Meteo"

    temp_c = weather.temperature_c
    humidity_pct = weather.humidity_pct
    wind_speed_kmh = weather.wind_speed_kmh

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

    # Publish alerts via NATS (consistent with /weather/current)
    event_ids = []
    publisher = getattr(app.state, "publisher", None)
    if publisher and alerts:
        for alert in alerts:
            try:
                event_id = await publisher.publish_weather_alert(
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
            except Exception as e:
                logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

    # Publish report generated event
    if publisher:
        try:
            await publisher.publish_forecast_issued(
                tenant_id=req.tenant_id,
                field_id=req.field_id,
                provider=provider,
                days=1,
                correlation_id=req.correlation_id,
            )
        except Exception as e:
            logger.error("nats_publish_failed", subject="forecast_issued", error=str(e))

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "location": {"lat": req.lat, "lon": req.lon},
        "evapotranspiration": et_result,
        "growing_degree_days": gdd_result,
        "spray_window": spray_result,
        "irrigation_adjustment": irrigation,
        "alerts": [a.to_dict() for a in alerts],
        "alert_count": len(alerts),
        "event_ids": event_ids,
    }


# ============== Frost, Heat Stress & Chill Hours Endpoints ==============


class FrostRiskRequest(BaseModel):
    """Frost risk assessment request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    temp_c: float = Field(ge=-50, le=60, description="Temperature °C")
    humidity_pct: float = Field(ge=0, le=100, description="Humidity %")
    wind_speed_kmh: float = Field(ge=0, le=400, description="Wind speed km/h")
    cloud_cover_pct: float = Field(default=0, ge=0, le=100, description="Cloud cover %")
    dew_point_c: float | None = Field(default=None, ge=-50, le=50, description="Dew point °C")
    correlation_id: str | None = Field(default=None, max_length=200)


class HeatStressRequest(BaseModel):
    """Heat stress assessment request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    temp_c: float = Field(ge=-50, le=60, description="Temperature °C")
    humidity_pct: float = Field(ge=0, le=100, description="Humidity %")
    solar_radiation_mj: float = Field(default=15.0, ge=0, le=50, description="Solar radiation MJ/m²/day")
    wind_speed_kmh: float = Field(default=10.0, ge=0, le=400, description="Wind speed km/h")
    correlation_id: str | None = Field(default=None, max_length=200)


class ChillModel(StrEnum):
    SIMPLE = "simple"
    UTAH = "utah"
    DYNAMIC = "dynamic"


class ChillHoursRequest(BaseModel):
    """Chill hours calculation request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(max_length=100)
    hourly_temps: list[float] = Field(..., description="List of hourly temperatures °C")
    model: ChillModel = Field(default=ChillModel.UTAH, description="Model: simple, utah, or dynamic")
    base_temp_c: float = Field(default=7.2, ge=0, le=15, description="Base temp for simple model")


class DroughtIndexRequest(BaseModel):
    """Drought index calculation request"""

    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(default="", max_length=100)
    precipitation_mm: float = Field(ge=0, description="Total precipitation mm")
    et0_mm: float = Field(ge=0, description="Total ET0 mm")
    days: int = Field(default=30, ge=1, le=365, description="Period in days")
    correlation_id: str | None = Field(default=None, max_length=200)


@app.post("/weather/frost-risk")
async def assess_frost_risk(req: FrostRiskRequest, user: User = Depends(get_current_user)):
    """
    Assess frost risk and get protection recommendations
    تقييم خطر الصقيع والحصول على توصيات الحماية

    Evaluates frost risk based on temperature, humidity, wind, and cloud cover.
    Returns protection measures for different risk levels.
    """
    _enforce_tenant(user, req.tenant_id)

    result = calculate_frost_risk(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        wind_speed_kmh=req.wind_speed_kmh,
        cloud_cover_pct=req.cloud_cover_pct,
        dew_point_c=req.dew_point_c,
    )

    # Publish alert for high/critical frost risk
    event_id = None
    if result.get("frost_likely"):
        publisher = getattr(app.state, "publisher", None)
        if publisher:
            try:
                event_id = await publisher.publish_weather_alert(
                    tenant_id=req.tenant_id,
                    field_id=req.field_id,
                    alert_type="frost_risk",
                    severity=result["risk_level"],
                    window_hours=12,
                    title_ar=result.get("recommendation_ar", "خطر صقيع"),
                    title_en=result.get("recommendation_en", "Frost risk"),
                )
            except Exception as e:
                logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "frost_risk": result,
        "event_id": event_id,
    }


@app.post("/weather/heat-stress")
async def assess_heat_stress(req: HeatStressRequest, user: User = Depends(get_current_user)):
    """
    Calculate heat stress index for crops
    حساب مؤشر الإجهاد الحراري للمحاصيل

    Evaluates heat stress using Temperature-Humidity Index (THI).
    Returns mitigation recommendations for high stress conditions.
    """
    _enforce_tenant(user, req.tenant_id)

    result = calculate_heat_stress_index(
        temp_c=req.temp_c,
        humidity_pct=req.humidity_pct,
        solar_radiation_mj=req.solar_radiation_mj,
        wind_speed_kmh=req.wind_speed_kmh,
    )

    # Publish alert for severe/extreme heat stress
    event_id = None
    if result.get("is_critical"):
        publisher = getattr(app.state, "publisher", None)
        if publisher:
            try:
                event_id = await publisher.publish_weather_alert(
                    tenant_id=req.tenant_id,
                    field_id=req.field_id,
                    alert_type="heat_stress",
                    severity=result["stress_level"],
                    window_hours=24,
                    title_ar=result.get("recommendation_ar", "إجهاد حراري"),
                    title_en=result.get("recommendation_en", "Heat stress"),
                )
            except Exception as e:
                logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "heat_stress": result,
        "event_id": event_id,
    }


@app.post("/weather/chill-hours")
async def calculate_chill(req: ChillHoursRequest, user: User = Depends(get_current_user)):
    """
    Calculate chill hours/units for fruit trees
    حساب ساعات البرودة للأشجار المثمرة

    Supports multiple chill models:
    - simple: Hours below threshold
    - utah: Utah Chill Unit model (default, more accurate)
    - dynamic: Dynamic model for mild winters

    Returns chill units and which crops' requirements are satisfied.
    """
    _enforce_tenant(user, req.tenant_id)

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
async def calculate_drought(req: DroughtIndexRequest, user: User = Depends(get_current_user)):
    """
    Calculate drought stress index
    حساب مؤشر الإجهاد الجفافي

    Based on water balance (precipitation vs evapotranspiration).
    Returns irrigation recommendations.
    """
    _enforce_tenant(user, req.tenant_id)

    result = calculate_drought_index(
        precipitation_mm=req.precipitation_mm,
        et0_mm=req.et0_mm,
        days=req.days,
    )

    # Publish alert for severe/extreme drought
    event_id = None
    if result.get("drought_level") in ("severe", "extreme"):
        publisher = getattr(app.state, "publisher", None)
        if publisher:
            try:
                event_id = await publisher.publish_weather_alert(
                    tenant_id=req.tenant_id,
                    field_id=req.field_id,
                    alert_type="drought",
                    severity=result["drought_level"],
                    window_hours=48,
                    title_ar=result.get("recommendation_ar", "جفاف"),
                    title_en=result.get("recommendation_en", "Drought"),
                )
            except Exception as e:
                logger.error("nats_publish_failed", subject="weather_alert", error=str(e), exc_info=True)

    return {
        "tenant_id": req.tenant_id,
        "field_id": req.field_id,
        "drought_index": result,
        "event_id": event_id,
    }


@app.post("/weather/comprehensive-stress-report")
async def get_stress_report(req: LocationRequest, user: User = Depends(get_current_user)):
    """
    Comprehensive weather stress report
    تقرير الإجهاد الجوي الشامل

    Combines frost risk, heat stress, spray window, and alerts
    into a single comprehensive stress assessment.
    """
    _enforce_tenant(user, req.tenant_id)

    # Get current weather
    if app.state.multi_provider:
        result = await app.state.multi_provider.get_current(lat=req.lat, lon=req.lon)
        if not result.success:
            raise ExternalServiceException.weather_service(
                details={
                    "error": result.error,
                    "error_ar": result.error_ar,
                    "failed_providers": result.failed_providers,
                }
            )
        weather = result.data
    else:
        weather = await app.state.weather_provider.get_current(lat=req.lat, lon=req.lon)

    temp_c = weather.temperature_c
    humidity_pct = weather.humidity_pct
    wind_speed_kmh = weather.wind_speed_kmh
    cloud_cover_pct = weather.cloud_cover_pct

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
        "overall_status": overall_status,
        "overall_color": overall_color,
        "frost_risk": frost_result,
        "heat_stress": heat_result,
        "spray_window": spray_result,
    }


# ---------------------------------------------------------------------------
# Weather Graph URL endpoints (Farmonaut-style get-past-weather-graph)
# نقاط نهاية رسم الطقس — يعيد رابط URL للرسم بدل JSON
# ---------------------------------------------------------------------------

from src.graph import (  # noqa: E402
    DailyPoint,
    GraphRequest,
    GraphStore,
    WeatherGraphRenderer,
)


class WeatherGraphGenerateRequest(BaseModel):
    tenant_id: str = Field(min_length=1, max_length=100)
    field_id: str = Field(min_length=1, max_length=100)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    days: int = Field(default=14, ge=1, le=90)
    metric: Literal["temperature", "precipitation", "humidity", "wind", "combined"] = "combined"
    language: Literal["ar", "en"] = "ar"


@app.post("/api/v1/weather/fields/{field_id}/graph")
async def generate_weather_graph(
    field_id: str,
    req: WeatherGraphGenerateRequest,
    user: User = Depends(get_current_user),
):
    """
    Generate a weather history graph for a field and return its URL.

    Farmonaut-style: the API returns a signed URL to a server-rendered
    SVG chart. The client loads it as an <img src="..."> instead of
    receiving JSON + rendering the chart in Dart/JS. This is much
    lighter on the mobile client and gives identical visuals across
    platforms.

    Response:
      {
        "success": true,
        "data": {
          "graph_id": "...",
          "url": "/api/v1/weather/graphs/{id}?tid=...&sig=...",
          "expires_at": "2026-04-11T18:30:00Z",
          "metric": "combined",
          "days": 14
        }
      }
    """
    _enforce_tenant(user, req.tenant_id)

    # Initialise lazy singletons on first call (one per process).
    if not hasattr(app.state, "graph_renderer"):
        app.state.graph_renderer = WeatherGraphRenderer()
    if not hasattr(app.state, "graph_store"):
        app.state.graph_store = GraphStore()

    # Pull historical daily weather — the multi-provider service
    # already exposes get_daily_forecast; for past data we use the
    # provider's history method when available, else we gracefully
    # fall back to an empty series so the SVG still renders.
    daily_points: list[DailyPoint] = []
    if app.state.multi_provider and hasattr(app.state.multi_provider, "get_historical_daily"):
        try:
            history_result = await app.state.multi_provider.get_historical_daily(
                req.lat, req.lon, req.days, tenant_id=req.tenant_id
            )
            if history_result and getattr(history_result, "success", False):
                for row in history_result.data or []:
                    daily_points.append(
                        DailyPoint(
                            date=row.get("date", ""),
                            temp_min_c=row.get("temp_min_c"),
                            temp_max_c=row.get("temp_max_c"),
                            precipitation_mm=row.get("precipitation_mm"),
                            humidity_pct=row.get("humidity_pct"),
                            wind_speed_kmh=row.get("wind_speed_kmh"),
                        )
                    )
        except Exception as e:  # pragma: no cover - provider-specific
            logger.warning("Historical fetch failed, rendering empty graph", error=str(e))

    svg = app.state.graph_renderer.render(
        GraphRequest(
            field_id=field_id,
            tenant_id=req.tenant_id,
            metric=req.metric,
            points=daily_points,
            language=req.language,
        )
    )
    graph_id, url_path, expires_at = app.state.graph_store.store(svg=svg, field_id=field_id, tenant_id=req.tenant_id)

    return {
        "success": True,
        "data": {
            "graph_id": graph_id,
            "url": url_path,
            "expires_at": expires_at.isoformat(),
            "metric": req.metric,
            "days": req.days,
            "points_count": len(daily_points),
        },
    }


@app.get("/api/v1/weather/graphs/{graph_id}")
async def fetch_weather_graph(graph_id: str, tid: str, sig: str):
    """
    Serve the rendered SVG for a previously-generated graph.

    The URL is signed with HMAC-SHA256 (stored tenant + graph_id),
    so only clients who went through POST /fields/:id/graph can
    fetch the resulting SVG. No JWT required on this read — the
    signature is the authorisation. Cache-Control: private so
    proxies don't leak per-tenant graphs.
    """
    from starlette.responses import Response as StarletteResponse

    if not hasattr(app.state, "graph_store"):
        raise HTTPException(status_code=404, detail="Graph not found")

    svg = app.state.graph_store.fetch(graph_id, tid, sig)
    if svg is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Graph not found or expired",
                "message_ar": "الرسم غير موجود أو انتهت صلاحيته",
            },
        )

    return StarletteResponse(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": "private, max-age=3600",
            "Content-Disposition": f'inline; filename="weather-{graph_id}.svg"',
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8092))
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec B104 - binding to all interfaces required for Docker container
