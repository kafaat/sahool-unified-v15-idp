"""
═══════════════════════════════════════════════════════════════════════════════
SAHOOL - Provider Configuration Service
خدمة إدارة المزودين الخارجيين
Port: 8104
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import httpx
import asyncio

app = FastAPI(
    title="SAHOOL Provider Configuration Service",
    description="خدمة إدارة وتكوين المزودين الخارجيين للخرائط والطقس والأقمار الصناعية",
    version="1.0.0",
)

# CORS - Secure configuration
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.cors_config import CORS_SETTINGS
    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "https://sahool.io,https://admin.sahool.io,http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ProviderType(str, Enum):
    MAP = "map"
    WEATHER = "weather"
    SATELLITE = "satellite"
    NOTIFICATION = "notification"


class ProviderPriority(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    DISABLED = "disabled"


class ProviderStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    CHECKING = "checking"


class MapProviderName(str, Enum):
    OPENSTREETMAP = "openstreetmap"
    GOOGLE_MAPS = "google_maps"
    GOOGLE_SATELLITE = "google_satellite"
    GOOGLE_HYBRID = "google_hybrid"
    MAPBOX_STREETS = "mapbox_streets"
    MAPBOX_SATELLITE = "mapbox_satellite"
    MAPBOX_HYBRID = "mapbox_hybrid"
    ESRI_SATELLITE = "esri_satellite"
    ESRI_STREETS = "esri_streets"
    OPENTOPOMAP = "opentopomap"


class WeatherProviderName(str, Enum):
    OPEN_METEO = "open_meteo"
    OPENWEATHERMAP = "openweathermap"
    WEATHER_API = "weather_api"
    VISUAL_CROSSING = "visual_crossing"


class SatelliteProviderName(str, Enum):
    SENTINEL_HUB = "sentinel_hub"
    PLANET_LABS = "planet_labs"
    MAXAR = "maxar"
    LANDSAT = "landsat"


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER DEFINITIONS - تعريفات المزودين
# ═══════════════════════════════════════════════════════════════════════════════

MAP_PROVIDERS = {
    MapProviderName.OPENSTREETMAP: {
        "name": "OpenStreetMap",
        "name_ar": "خريطة الشارع المفتوحة",
        "url_template": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        "requires_api_key": False,
        "max_zoom": 19,
        "attribution": "© OpenStreetMap contributors",
        "supports_offline": True,
        "cost_per_1k_requests": 0,
        "default_priority": ProviderPriority.PRIMARY,
    },
    MapProviderName.GOOGLE_MAPS: {
        "name": "Google Maps",
        "name_ar": "خرائط جوجل",
        "url_template": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&key={api_key}",
        "requires_api_key": True,
        "max_zoom": 21,
        "attribution": "© Google",
        "supports_offline": False,
        "cost_per_1k_requests": 7.0,
        "default_priority": ProviderPriority.SECONDARY,
    },
    MapProviderName.GOOGLE_SATELLITE: {
        "name": "Google Satellite",
        "name_ar": "جوجل القمر الصناعي",
        "url_template": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&key={api_key}",
        "requires_api_key": True,
        "max_zoom": 21,
        "attribution": "© Google",
        "supports_offline": False,
        "cost_per_1k_requests": 7.0,
        "default_priority": ProviderPriority.SECONDARY,
    },
    MapProviderName.GOOGLE_HYBRID: {
        "name": "Google Hybrid",
        "name_ar": "جوجل هجين",
        "url_template": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}&key={api_key}",
        "requires_api_key": True,
        "max_zoom": 21,
        "attribution": "© Google",
        "supports_offline": False,
        "cost_per_1k_requests": 7.0,
        "default_priority": ProviderPriority.TERTIARY,
    },
    MapProviderName.MAPBOX_STREETS: {
        "name": "Mapbox Streets",
        "name_ar": "ماب بوكس شوارع",
        "url_template": "https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token={api_key}",
        "requires_api_key": True,
        "max_zoom": 22,
        "attribution": "© Mapbox © OpenStreetMap",
        "supports_offline": True,
        "cost_per_1k_requests": 0.5,
        "default_priority": ProviderPriority.SECONDARY,
    },
    MapProviderName.MAPBOX_SATELLITE: {
        "name": "Mapbox Satellite",
        "name_ar": "ماب بوكس قمر صناعي",
        "url_template": "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token={api_key}",
        "requires_api_key": True,
        "max_zoom": 22,
        "attribution": "© Mapbox © Maxar",
        "supports_offline": True,
        "cost_per_1k_requests": 0.5,
        "default_priority": ProviderPriority.SECONDARY,
    },
    MapProviderName.MAPBOX_HYBRID: {
        "name": "Mapbox Hybrid",
        "name_ar": "ماب بوكس هجين",
        "url_template": "https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token={api_key}",
        "requires_api_key": True,
        "max_zoom": 22,
        "attribution": "© Mapbox © Maxar © OpenStreetMap",
        "supports_offline": True,
        "cost_per_1k_requests": 0.5,
        "default_priority": ProviderPriority.TERTIARY,
    },
    MapProviderName.ESRI_SATELLITE: {
        "name": "ESRI Satellite",
        "name_ar": "ESRI قمر صناعي",
        "url_template": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "requires_api_key": False,
        "max_zoom": 19,
        "attribution": "© Esri, Maxar, Earthstar Geographics",
        "supports_offline": True,
        "cost_per_1k_requests": 0,
        "default_priority": ProviderPriority.TERTIARY,
    },
    MapProviderName.ESRI_STREETS: {
        "name": "ESRI Streets",
        "name_ar": "ESRI شوارع",
        "url_template": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        "requires_api_key": False,
        "max_zoom": 18,
        "attribution": "© Esri, HERE, Garmin, OpenStreetMap",
        "supports_offline": True,
        "cost_per_1k_requests": 0,
        "default_priority": ProviderPriority.TERTIARY,
    },
    MapProviderName.OPENTOPOMAP: {
        "name": "OpenTopoMap",
        "name_ar": "خريطة التضاريس",
        "url_template": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        "requires_api_key": False,
        "max_zoom": 17,
        "attribution": "© OpenStreetMap, SRTM",
        "supports_offline": True,
        "cost_per_1k_requests": 0,
        "default_priority": ProviderPriority.TERTIARY,
    },
}

WEATHER_PROVIDERS = {
    WeatherProviderName.OPEN_METEO: {
        "name": "Open-Meteo",
        "name_ar": "أوبن ميتيو",
        "base_url": "https://api.open-meteo.com/v1",
        "requires_api_key": False,
        "forecast_days": 16,
        "supports_historical": True,
        "supports_alerts": False,
        "rate_limit_per_minute": 10000,
        "cost_per_1k_requests": 0,
        "default_priority": ProviderPriority.PRIMARY,
    },
    WeatherProviderName.OPENWEATHERMAP: {
        "name": "OpenWeatherMap",
        "name_ar": "أوبن ويذر ماب",
        "base_url": "https://api.openweathermap.org/data/2.5",
        "requires_api_key": True,
        "forecast_days": 8,
        "supports_historical": False,
        "supports_alerts": True,
        "rate_limit_per_minute": 60,
        "cost_per_1k_requests": 0,  # Free tier: 1000/day
        "default_priority": ProviderPriority.SECONDARY,
    },
    WeatherProviderName.WEATHER_API: {
        "name": "WeatherAPI",
        "name_ar": "ويذر API",
        "base_url": "https://api.weatherapi.com/v1",
        "requires_api_key": True,
        "forecast_days": 14,
        "supports_historical": True,
        "supports_alerts": True,
        "rate_limit_per_minute": 100,
        "cost_per_1k_requests": 0,  # Free tier: 1M/month
        "default_priority": ProviderPriority.SECONDARY,
    },
    WeatherProviderName.VISUAL_CROSSING: {
        "name": "Visual Crossing",
        "name_ar": "فيجوال كروسينج",
        "base_url": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline",
        "requires_api_key": True,
        "forecast_days": 15,
        "supports_historical": True,
        "supports_alerts": True,
        "rate_limit_per_minute": 1000,
        "cost_per_1k_requests": 0.1,
        "default_priority": ProviderPriority.TERTIARY,
    },
}

SATELLITE_PROVIDERS = {
    SatelliteProviderName.SENTINEL_HUB: {
        "name": "Sentinel Hub",
        "name_ar": "سنتينيل هب",
        "base_url": "https://services.sentinel-hub.com",
        "requires_api_key": True,
        "resolution_meters": 10,
        "revisit_days": 5,
        "indices": ["NDVI", "NDWI", "EVI", "SAVI", "NDMI", "LAI"],
        "cost_per_km2": 0.001,
        "default_priority": ProviderPriority.PRIMARY,
    },
    SatelliteProviderName.PLANET_LABS: {
        "name": "Planet Labs",
        "name_ar": "بلانيت لابس",
        "base_url": "https://api.planet.com/data/v1",
        "requires_api_key": True,
        "resolution_meters": 3,
        "revisit_days": 1,
        "indices": ["NDVI", "NDWI", "EVI", "GNDVI"],
        "cost_per_km2": 0.10,
        "default_priority": ProviderPriority.SECONDARY,
    },
    SatelliteProviderName.MAXAR: {
        "name": "Maxar",
        "name_ar": "ماكسار",
        "base_url": "https://api.maxar.com/streaming/v1",
        "requires_api_key": True,
        "resolution_meters": 0.3,  # 30cm
        "revisit_days": 3,
        "indices": ["NDVI"],
        "cost_per_km2": 15.0,
        "default_priority": ProviderPriority.TERTIARY,
    },
    SatelliteProviderName.LANDSAT: {
        "name": "Landsat (USGS)",
        "name_ar": "لاندسات",
        "base_url": "https://earthexplorer.usgs.gov",
        "requires_api_key": False,
        "resolution_meters": 30,
        "revisit_days": 16,
        "indices": ["NDVI", "NDWI", "EVI", "SAVI"],
        "cost_per_km2": 0,
        "default_priority": ProviderPriority.TERTIARY,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ProviderConfig(BaseModel):
    provider_name: str
    api_key: Optional[str] = None
    priority: ProviderPriority = ProviderPriority.PRIMARY
    enabled: bool = True


class TenantProviderConfig(BaseModel):
    tenant_id: str
    map_providers: List[ProviderConfig] = []
    weather_providers: List[ProviderConfig] = []
    satellite_providers: List[ProviderConfig] = []


class ProviderStatusResponse(BaseModel):
    provider_name: str
    status: ProviderStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class HealthCheckRequest(BaseModel):
    provider_type: ProviderType
    provider_name: str
    api_key: Optional[str] = None


class ProvidersListResponse(BaseModel):
    map_providers: List[Dict[str, Any]]
    weather_providers: List[Dict[str, Any]]
    satellite_providers: List[Dict[str, Any]]


# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (Replace with database in production)
# ═══════════════════════════════════════════════════════════════════════════════

tenant_configs: Dict[str, TenantProviderConfig] = {}
provider_status_cache: Dict[str, ProviderStatusResponse] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def check_map_provider_health(provider_name: MapProviderName, api_key: Optional[str] = None) -> ProviderStatusResponse:
    """Check if a map provider is available"""
    provider = MAP_PROVIDERS.get(provider_name)
    if not provider:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message="Unknown provider"
        )

    # Build test URL
    url_template = provider["url_template"]
    test_url = url_template.replace("{z}", "10").replace("{x}", "512").replace("{y}", "512")
    if api_key:
        test_url = test_url.replace("{api_key}", api_key)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start = datetime.utcnow()
            response = await client.head(test_url)
            response_time = (datetime.utcnow() - start).total_seconds() * 1000

            if response.status_code == 200:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.AVAILABLE,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time
                )
            elif response.status_code == 429:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time
                )
            else:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}"
                )
    except Exception as e:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message=str(e)
        )


async def check_weather_provider_health(provider_name: WeatherProviderName, api_key: Optional[str] = None) -> ProviderStatusResponse:
    """Check if a weather provider is available"""
    provider = WEATHER_PROVIDERS.get(provider_name)
    if not provider:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message="Unknown provider"
        )

    # Build test URL based on provider
    test_url = ""
    if provider_name == WeatherProviderName.OPEN_METEO:
        test_url = f"{provider['base_url']}/forecast?latitude=15.37&longitude=44.19&current=temperature_2m"
    elif provider_name == WeatherProviderName.OPENWEATHERMAP:
        if not api_key:
            return ProviderStatusResponse(
                provider_name=provider_name.value,
                status=ProviderStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message="API key required"
            )
        test_url = f"{provider['base_url']}/weather?lat=15.37&lon=44.19&appid={api_key}"
    elif provider_name == WeatherProviderName.WEATHER_API:
        if not api_key:
            return ProviderStatusResponse(
                provider_name=provider_name.value,
                status=ProviderStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message="API key required"
            )
        test_url = f"{provider['base_url']}/current.json?key={api_key}&q=15.37,44.19"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            start = datetime.utcnow()
            response = await client.get(test_url)
            response_time = (datetime.utcnow() - start).total_seconds() * 1000

            if response.status_code == 200:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.AVAILABLE,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time
                )
            elif response.status_code == 429:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.RATE_LIMITED,
                    last_check=datetime.utcnow()
                )
            else:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}"
                )
    except Exception as e:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message=str(e)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "SAHOOL Provider Configuration Service",
        "service_ar": "خدمة إدارة المزودين - سهول",
        "version": "1.0.0",
        "description": "Manage external service providers (Maps, Weather, Satellite)",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ─────────────────────────────────────────────────────────────────────────────
# PROVIDER LISTING
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/providers", response_model=ProvidersListResponse)
async def list_all_providers():
    """List all available providers"""
    return ProvidersListResponse(
        map_providers=[
            {**v, "id": k.value, "type": "map"}
            for k, v in MAP_PROVIDERS.items()
        ],
        weather_providers=[
            {**v, "id": k.value, "type": "weather"}
            for k, v in WEATHER_PROVIDERS.items()
        ],
        satellite_providers=[
            {**v, "id": k.value, "type": "satellite"}
            for k, v in SATELLITE_PROVIDERS.items()
        ],
    )


@app.get("/providers/maps")
async def list_map_providers():
    """List all map providers"""
    return {
        "providers": [
            {**v, "id": k.value}
            for k, v in MAP_PROVIDERS.items()
        ],
        "free_providers": [
            k.value for k, v in MAP_PROVIDERS.items()
            if not v["requires_api_key"]
        ],
    }


@app.get("/providers/weather")
async def list_weather_providers():
    """List all weather providers"""
    return {
        "providers": [
            {**v, "id": k.value}
            for k, v in WEATHER_PROVIDERS.items()
        ],
        "free_providers": [
            k.value for k, v in WEATHER_PROVIDERS.items()
            if not v["requires_api_key"]
        ],
    }


@app.get("/providers/satellite")
async def list_satellite_providers():
    """List all satellite providers"""
    return {
        "providers": [
            {**v, "id": k.value}
            for k, v in SATELLITE_PROVIDERS.items()
        ],
        "free_providers": [
            k.value for k, v in SATELLITE_PROVIDERS.items()
            if not v["requires_api_key"]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROVIDER HEALTH CHECKS
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/providers/check", response_model=ProviderStatusResponse)
async def check_provider_health(request: HealthCheckRequest):
    """Check health of a specific provider"""
    if request.provider_type == ProviderType.MAP:
        try:
            provider_name = MapProviderName(request.provider_name)
            return await check_map_provider_health(provider_name, request.api_key)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown map provider: {request.provider_name}")

    elif request.provider_type == ProviderType.WEATHER:
        try:
            provider_name = WeatherProviderName(request.provider_name)
            return await check_weather_provider_health(provider_name, request.api_key)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown weather provider: {request.provider_name}")

    raise HTTPException(status_code=400, detail=f"Unsupported provider type: {request.provider_type}")


@app.get("/providers/check/all")
async def check_all_free_providers():
    """Check health of all free providers (no API key required)"""
    results = {
        "map_providers": [],
        "weather_providers": [],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Check free map providers
    free_map_providers = [k for k, v in MAP_PROVIDERS.items() if not v["requires_api_key"]]
    for provider_name in free_map_providers:
        status = await check_map_provider_health(provider_name)
        results["map_providers"].append(status.dict())

    # Check free weather providers
    free_weather_providers = [k for k, v in WEATHER_PROVIDERS.items() if not v["requires_api_key"]]
    for provider_name in free_weather_providers:
        status = await check_weather_provider_health(provider_name)
        results["weather_providers"].append(status.dict())

    return results


# ─────────────────────────────────────────────────────────────────────────────
# TENANT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/config/{tenant_id}")
async def get_tenant_config(tenant_id: str):
    """Get provider configuration for a tenant"""
    if tenant_id not in tenant_configs:
        # Return default config
        return {
            "tenant_id": tenant_id,
            "map_providers": [
                {"provider_name": "openstreetmap", "priority": "primary", "enabled": True},
                {"provider_name": "esri_satellite", "priority": "secondary", "enabled": True},
            ],
            "weather_providers": [
                {"provider_name": "open_meteo", "priority": "primary", "enabled": True},
            ],
            "satellite_providers": [],
            "is_default": True,
        }

    return tenant_configs[tenant_id]


@app.post("/config/{tenant_id}")
async def update_tenant_config(tenant_id: str, config: TenantProviderConfig):
    """Update provider configuration for a tenant"""
    config.tenant_id = tenant_id
    tenant_configs[tenant_id] = config
    return {"success": True, "config": config}


@app.delete("/config/{tenant_id}")
async def reset_tenant_config(tenant_id: str):
    """Reset tenant configuration to defaults"""
    if tenant_id in tenant_configs:
        del tenant_configs[tenant_id]
    return {"success": True, "message": "Configuration reset to defaults"}


# ─────────────────────────────────────────────────────────────────────────────
# PROVIDER RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/providers/recommend")
async def recommend_providers(
    use_case: str = "agricultural",
    budget: str = "free",  # free, low, medium, high
    offline_required: bool = True,
):
    """Get recommended providers based on use case and budget"""

    recommendations = {
        "use_case": use_case,
        "budget": budget,
        "offline_required": offline_required,
        "map": [],
        "weather": [],
        "satellite": [],
    }

    # Map recommendations
    if budget == "free":
        recommendations["map"] = [
            {"provider": "openstreetmap", "reason": "مجاني، يدعم الاستخدام غير المتصل", "reason_en": "Free, supports offline"},
            {"provider": "esri_satellite", "reason": "صور أقمار صناعية مجانية", "reason_en": "Free satellite imagery"},
        ]
        recommendations["weather"] = [
            {"provider": "open_meteo", "reason": "مجاني، 16 يوم توقعات", "reason_en": "Free, 16-day forecast"},
        ]
    elif budget in ["low", "medium"]:
        recommendations["map"] = [
            {"provider": "mapbox_streets", "reason": "جودة عالية، تكلفة منخفضة", "reason_en": "High quality, low cost"},
            {"provider": "mapbox_satellite", "reason": "صور أقمار صناعية عالية الجودة", "reason_en": "High quality satellite"},
        ]
        recommendations["weather"] = [
            {"provider": "open_meteo", "reason": "مجاني كمصدر أساسي", "reason_en": "Free as primary"},
            {"provider": "openweathermap", "reason": "تنبيهات جوية", "reason_en": "Weather alerts"},
        ]
        recommendations["satellite"] = [
            {"provider": "sentinel_hub", "reason": "أفضل قيمة للزراعة", "reason_en": "Best value for agriculture"},
        ]
    else:  # high budget
        recommendations["map"] = [
            {"provider": "google_hybrid", "reason": "أفضل جودة وتفاصيل", "reason_en": "Best quality and detail"},
        ]
        recommendations["satellite"] = [
            {"provider": "planet_labs", "reason": "صور يومية، دقة 3 متر", "reason_en": "Daily imagery, 3m resolution"},
        ]

    return recommendations


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8104)
