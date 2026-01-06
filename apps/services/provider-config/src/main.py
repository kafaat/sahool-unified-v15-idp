"""
═══════════════════════════════════════════════════════════════════════════════
SAHOOL - Provider Configuration Service
خدمة إدارة المزودين الخارجيين
Port: 8104
═══════════════════════════════════════════════════════════════════════════════
"""

from datetime import datetime
from enum import Enum
from typing import Any
import os

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import database models and services
from models import Database, ProviderConfig as DBProviderConfig
from database_service import CacheManager, ProviderConfigService

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
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
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
    PAYMENT = "payment"
    SMS = "sms"


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
    GOOGLE_EARTH_ENGINE = "google_earth_engine"
    COPERNICUS = "copernicus"


class PaymentProviderName(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MOYASAR = "moyasar"
    HYPERPAY = "hyperpay"
    TAP = "tap"
    PAYFORT = "payfort"
    TELR = "telr"
    THARWATT = "tharwatt"  # بوابة ثروات اليمنية


class NotificationProviderName(str, Enum):
    FIREBASE_FCM = "firebase_fcm"
    ONESIGNAL = "onesignal"
    PUSHER = "pusher"
    TWILIO_SMS = "twilio_sms"
    VONAGE_SMS = "vonage_sms"


class SMSProviderName(str, Enum):
    TWILIO = "twilio"
    VONAGE = "vonage"
    UNIFONIC = "unifonic"
    YAMAMAH = "yamamah"


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
    SatelliteProviderName.GOOGLE_EARTH_ENGINE: {
        "name": "Google Earth Engine",
        "name_ar": "محرك الأرض من جوجل",
        "base_url": "https://earthengine.googleapis.com",
        "requires_api_key": True,
        "resolution_meters": 10,
        "revisit_days": 5,
        "indices": ["NDVI", "NDWI", "EVI", "SAVI", "LAI", "FAPAR"],
        "cost_per_km2": 0,  # Free for research
        "default_priority": ProviderPriority.SECONDARY,
    },
    SatelliteProviderName.COPERNICUS: {
        "name": "Copernicus Open Access Hub",
        "name_ar": "كوبرنيكوس",
        "base_url": "https://scihub.copernicus.eu",
        "requires_api_key": True,
        "resolution_meters": 10,
        "revisit_days": 5,
        "indices": ["NDVI", "NDWI", "EVI", "SAVI"],
        "cost_per_km2": 0,  # Free
        "default_priority": ProviderPriority.TERTIARY,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENT PROVIDERS - مزودي الدفع
# ═══════════════════════════════════════════════════════════════════════════════

PAYMENT_PROVIDERS = {
    PaymentProviderName.STRIPE: {
        "name": "Stripe",
        "name_ar": "سترايب",
        "base_url": "https://api.stripe.com/v1",
        "requires_api_key": True,
        "supported_currencies": ["USD", "EUR", "SAR", "AED", "YER"],
        "supported_countries": ["US", "EU", "SA", "AE", "YE"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "transaction_fee_percent": 2.9,
        "transaction_fee_fixed": 0.30,
        "payout_delay_days": 2,
        "default_priority": ProviderPriority.PRIMARY,
    },
    PaymentProviderName.PAYPAL: {
        "name": "PayPal",
        "name_ar": "باي بال",
        "base_url": "https://api.paypal.com/v2",
        "requires_api_key": True,
        "supported_currencies": ["USD", "EUR", "SAR", "AED"],
        "supported_countries": ["US", "EU", "SA", "AE"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "transaction_fee_percent": 3.49,
        "transaction_fee_fixed": 0.49,
        "payout_delay_days": 1,
        "default_priority": ProviderPriority.SECONDARY,
    },
    PaymentProviderName.MOYASAR: {
        "name": "Moyasar",
        "name_ar": "ميسر",
        "base_url": "https://api.moyasar.com/v1",
        "requires_api_key": True,
        "supported_currencies": ["SAR"],
        "supported_countries": ["SA"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "supports_mada": True,
        "transaction_fee_percent": 2.0,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 2,
        "default_priority": ProviderPriority.PRIMARY,  # Primary for Saudi Arabia
    },
    PaymentProviderName.HYPERPAY: {
        "name": "HyperPay",
        "name_ar": "هايبر باي",
        "base_url": "https://eu-prod.oppwa.com/v1",
        "requires_api_key": True,
        "supported_currencies": ["SAR", "AED", "BHD", "KWD", "OMR", "QAR", "YER"],
        "supported_countries": ["SA", "AE", "BH", "KW", "OM", "QA", "YE"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "supports_mada": True,
        "transaction_fee_percent": 2.5,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 3,
        "default_priority": ProviderPriority.SECONDARY,
    },
    PaymentProviderName.TAP: {
        "name": "Tap Payments",
        "name_ar": "تاب للمدفوعات",
        "base_url": "https://api.tap.company/v2",
        "requires_api_key": True,
        "supported_currencies": [
            "SAR",
            "AED",
            "BHD",
            "KWD",
            "OMR",
            "QAR",
            "EGP",
            "JOD",
        ],
        "supported_countries": ["SA", "AE", "BH", "KW", "OM", "QA", "EG", "JO"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "supports_mada": True,
        "transaction_fee_percent": 2.75,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 2,
        "default_priority": ProviderPriority.SECONDARY,
    },
    PaymentProviderName.PAYFORT: {
        "name": "PayFort (Amazon Payment Services)",
        "name_ar": "باي فورت",
        "base_url": "https://paymentservices.payfort.com/FortAPI/paymentApi",
        "requires_api_key": True,
        "supported_currencies": ["AED", "SAR", "EGP", "JOD", "LBP"],
        "supported_countries": ["AE", "SA", "EG", "JO", "LB"],
        "supports_subscriptions": True,
        "supports_refunds": True,
        "supports_mada": True,
        "transaction_fee_percent": 2.8,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 3,
        "default_priority": ProviderPriority.TERTIARY,
    },
    PaymentProviderName.TELR: {
        "name": "Telr",
        "name_ar": "تلر",
        "base_url": "https://secure.telr.com/gateway/order.json",
        "requires_api_key": True,
        "supported_currencies": ["AED", "SAR", "BHD", "KWD", "OMR", "QAR"],
        "supported_countries": ["AE", "SA", "BH", "KW", "OM", "QA"],
        "supports_subscriptions": False,
        "supports_refunds": True,
        "transaction_fee_percent": 2.85,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 3,
        "default_priority": ProviderPriority.TERTIARY,
    },
    PaymentProviderName.THARWATT: {
        "name": "Tharwatt",
        "name_ar": "ثروات",
        "base_url": "https://developers-test.tharwatt.com:5253",
        "production_url": "https://api.tharwatt.com",
        "requires_api_key": True,
        "supported_currencies": ["YER"],
        "supported_countries": ["YE"],
        "supports_subscriptions": False,
        "supports_refunds": True,
        "supports_mobile_topup": True,
        "supports_wallet": True,
        "supported_operators": ["yemen_mobile", "mtn", "sabafon", "y_telecom"],
        "transaction_fee_percent": 1.5,
        "transaction_fee_fixed": 0,
        "payout_delay_days": 1,
        "default_priority": ProviderPriority.PRIMARY,  # Primary for Yemen
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SMS PROVIDERS - مزودي الرسائل النصية
# ═══════════════════════════════════════════════════════════════════════════════

SMS_PROVIDERS = {
    SMSProviderName.TWILIO: {
        "name": "Twilio",
        "name_ar": "تويليو",
        "base_url": "https://api.twilio.com/2010-04-01",
        "requires_api_key": True,
        "supported_countries": ["*"],  # Global
        "supports_unicode": True,
        "supports_delivery_reports": True,
        "cost_per_sms_usd": 0.0075,
        "default_priority": ProviderPriority.PRIMARY,
    },
    SMSProviderName.VONAGE: {
        "name": "Vonage (Nexmo)",
        "name_ar": "فوناج",
        "base_url": "https://rest.nexmo.com/sms/json",
        "requires_api_key": True,
        "supported_countries": ["*"],  # Global
        "supports_unicode": True,
        "supports_delivery_reports": True,
        "cost_per_sms_usd": 0.0068,
        "default_priority": ProviderPriority.SECONDARY,
    },
    SMSProviderName.UNIFONIC: {
        "name": "Unifonic",
        "name_ar": "يونيفونيك",
        "base_url": "https://el.cloud.unifonic.com/rest",
        "requires_api_key": True,
        "supported_countries": ["SA", "AE", "EG", "JO", "KW", "BH", "OM", "QA", "YE"],
        "supports_unicode": True,
        "supports_delivery_reports": True,
        "supports_arabic_sender": True,
        "cost_per_sms_usd": 0.035,
        "default_priority": ProviderPriority.PRIMARY,  # Primary for Middle East
    },
    SMSProviderName.YAMAMAH: {
        "name": "Yamamah",
        "name_ar": "اليمامة",
        "base_url": "https://api.yamamah.com/sms/v1",
        "requires_api_key": True,
        "supported_countries": ["SA", "YE"],
        "supports_unicode": True,
        "supports_delivery_reports": True,
        "supports_arabic_sender": True,
        "cost_per_sms_usd": 0.03,
        "default_priority": ProviderPriority.PRIMARY,  # Primary for Yemen
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION PROVIDERS - مزودي الإشعارات
# ═══════════════════════════════════════════════════════════════════════════════

NOTIFICATION_PROVIDERS = {
    NotificationProviderName.FIREBASE_FCM: {
        "name": "Firebase Cloud Messaging",
        "name_ar": "إشعارات فايربيس",
        "base_url": "https://fcm.googleapis.com/v1",
        "requires_api_key": True,
        "supports_android": True,
        "supports_ios": True,
        "supports_web": True,
        "cost_per_1k_notifications": 0,  # Free
        "default_priority": ProviderPriority.PRIMARY,
    },
    NotificationProviderName.ONESIGNAL: {
        "name": "OneSignal",
        "name_ar": "ون سيجنال",
        "base_url": "https://onesignal.com/api/v1",
        "requires_api_key": True,
        "supports_android": True,
        "supports_ios": True,
        "supports_web": True,
        "cost_per_1k_notifications": 0,  # Free tier: 10K/month
        "default_priority": ProviderPriority.SECONDARY,
    },
    NotificationProviderName.PUSHER: {
        "name": "Pusher Beams",
        "name_ar": "بوشر",
        "base_url": "https://api.pusherplatform.io/push_notifications/v1",
        "requires_api_key": True,
        "supports_android": True,
        "supports_ios": True,
        "supports_web": True,
        "cost_per_1k_notifications": 0.02,
        "default_priority": ProviderPriority.TERTIARY,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class ProviderConfig(BaseModel):
    provider_name: str
    api_key: str | None = None
    priority: ProviderPriority = ProviderPriority.PRIMARY
    enabled: bool = True


class TenantProviderConfig(BaseModel):
    tenant_id: str
    map_providers: list[ProviderConfig] = []
    weather_providers: list[ProviderConfig] = []
    satellite_providers: list[ProviderConfig] = []


class ProviderStatusResponse(BaseModel):
    provider_name: str
    status: ProviderStatus
    last_check: datetime
    response_time_ms: float | None = None
    error_message: str | None = None


class HealthCheckRequest(BaseModel):
    provider_type: ProviderType
    provider_name: str
    api_key: str | None = None


class ProvidersListResponse(BaseModel):
    map_providers: list[dict[str, Any]]
    weather_providers: list[dict[str, Any]]
    satellite_providers: list[dict[str, Any]]


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE & CACHE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

# Database and cache instances (initialized on startup)
database: Database | None = None
cache_manager: CacheManager | None = None
config_service: ProviderConfigService | None = None


def get_db_session():
    """Get database session dependency"""
    if not database:
        raise HTTPException(status_code=503, detail="Database not initialized")
    session = next(database.get_session())
    try:
        yield session
    finally:
        session.close()


@app.on_event("startup")
async def startup_event():
    """Initialize database and cache on startup"""
    global database, cache_manager, config_service

    # Get configuration from environment
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://sahool:sahool@pgbouncer:6432/sahool"
    )
    redis_url = os.getenv("REDIS_URL", "redis://:password@redis:6379/0")

    # Initialize database
    try:
        database = Database(database_url)
        database.create_tables()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise

    # Initialize cache
    try:
        cache_manager = CacheManager(redis_url, cache_ttl=300)
        print("✓ Cache initialized successfully")
    except Exception as e:
        print(f"⚠ Cache initialization failed: {e} (continuing without cache)")
        # Create a dummy cache manager that doesn't actually cache
        cache_manager = CacheManager(redis_url, cache_ttl=0)

    # Initialize config service
    config_service = ProviderConfigService(database, cache_manager)
    print("✓ Provider Config Service initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global database, cache_manager
    if cache_manager and cache_manager.redis_client:
        cache_manager.redis_client.close()
    print("✓ Service shutdown complete")


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def check_map_provider_health(
    provider_name: MapProviderName, api_key: str | None = None
) -> ProviderStatusResponse:
    """Check if a map provider is available"""
    provider = MAP_PROVIDERS.get(provider_name)
    if not provider:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message="Unknown provider",
        )

    # Build test URL
    url_template = provider["url_template"]
    test_url = (
        url_template.replace("{z}", "10").replace("{x}", "512").replace("{y}", "512")
    )
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
                    response_time_ms=response_time,
                )
            elif response.status_code == 429:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                    response_time_ms=response_time,
                )
            else:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}",
                )
    except Exception as e:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message=str(e),
        )


async def check_weather_provider_health(
    provider_name: WeatherProviderName, api_key: str | None = None
) -> ProviderStatusResponse:
    """Check if a weather provider is available"""
    provider = WEATHER_PROVIDERS.get(provider_name)
    if not provider:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message="Unknown provider",
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
                error_message="API key required",
            )
        test_url = f"{provider['base_url']}/weather?lat=15.37&lon=44.19&appid={api_key}"
    elif provider_name == WeatherProviderName.WEATHER_API:
        if not api_key:
            return ProviderStatusResponse(
                provider_name=provider_name.value,
                status=ProviderStatus.ERROR,
                last_check=datetime.utcnow(),
                error_message="API key required",
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
                    response_time_ms=response_time,
                )
            elif response.status_code == 429:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.RATE_LIMITED,
                    last_check=datetime.utcnow(),
                )
            else:
                return ProviderStatusResponse(
                    provider_name=provider_name.value,
                    status=ProviderStatus.UNAVAILABLE,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}",
                )
    except Exception as e:
        return ProviderStatusResponse(
            provider_name=provider_name.value,
            status=ProviderStatus.ERROR,
            last_check=datetime.utcnow(),
            error_message=str(e),
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


@app.get("/healthz")
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
            {**v, "id": k.value, "type": "map"} for k, v in MAP_PROVIDERS.items()
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
        "providers": [{**v, "id": k.value} for k, v in MAP_PROVIDERS.items()],
        "free_providers": [
            k.value for k, v in MAP_PROVIDERS.items() if not v["requires_api_key"]
        ],
    }


@app.get("/providers/weather")
async def list_weather_providers():
    """List all weather providers"""
    return {
        "providers": [{**v, "id": k.value} for k, v in WEATHER_PROVIDERS.items()],
        "free_providers": [
            k.value for k, v in WEATHER_PROVIDERS.items() if not v["requires_api_key"]
        ],
    }


@app.get("/providers/satellite")
async def list_satellite_providers():
    """List all satellite providers"""
    return {
        "providers": [{**v, "id": k.value} for k, v in SATELLITE_PROVIDERS.items()],
        "free_providers": [
            k.value for k, v in SATELLITE_PROVIDERS.items() if not v["requires_api_key"]
        ],
    }


@app.get("/providers/payment")
async def list_payment_providers():
    """List all payment providers - قائمة مزودي الدفع"""
    return {
        "providers": [{**v, "id": k.value} for k, v in PAYMENT_PROVIDERS.items()],
        "by_country": {
            "SA": ["moyasar", "hyperpay", "tap", "payfort", "stripe"],
            "AE": ["hyperpay", "tap", "payfort", "stripe", "paypal"],
            "YE": ["tharwatt", "hyperpay", "stripe"],  # Tharwatt is primary for Yemen
            "global": ["stripe", "paypal"],
        },
        "supports_mada": [
            k.value
            for k, v in PAYMENT_PROVIDERS.items()
            if v.get("supports_mada", False)
        ],
    }


@app.get("/providers/sms")
async def list_sms_providers():
    """List all SMS providers - قائمة مزودي الرسائل النصية"""
    return {
        "providers": [{**v, "id": k.value} for k, v in SMS_PROVIDERS.items()],
        "by_region": {
            "middle_east": ["unifonic", "yamamah"],
            "global": ["twilio", "vonage"],
        },
        "supports_arabic_sender": [
            k.value
            for k, v in SMS_PROVIDERS.items()
            if v.get("supports_arabic_sender", False)
        ],
    }


@app.get("/providers/notification")
async def list_notification_providers():
    """List all notification providers - قائمة مزودي الإشعارات"""
    return {
        "providers": [{**v, "id": k.value} for k, v in NOTIFICATION_PROVIDERS.items()],
        "free_providers": [
            k.value
            for k, v in NOTIFICATION_PROVIDERS.items()
            if v.get("cost_per_1k_notifications", 1) == 0
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# SMART PROVIDER SELECTION - اختيار المزود الذكي
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/providers/select/{provider_type}")
async def select_provider(
    provider_type: ProviderType,
    country: str = "YE",
    currency: str = "YER",
    fallback: bool = True,
):
    """
    Smart provider selection based on country and requirements
    اختيار المزود الذكي بناءً على البلد والمتطلبات
    """
    result = {
        "provider_type": provider_type.value,
        "country": country,
        "currency": currency,
        "selected": [],
        "fallback_providers": [],
    }

    if provider_type == ProviderType.PAYMENT:
        # Select payment providers based on country
        primary = []
        fallbacks = []

        for name, provider in PAYMENT_PROVIDERS.items():
            if country in provider.get("supported_countries", []):
                if provider["default_priority"] == ProviderPriority.PRIMARY:
                    primary.append({"id": name.value, **provider})
                else:
                    fallbacks.append({"id": name.value, **provider})

        # Sort by transaction fee
        primary.sort(key=lambda x: x.get("transaction_fee_percent", 100))
        fallbacks.sort(key=lambda x: x.get("transaction_fee_percent", 100))

        result["selected"] = primary[:2] if primary else fallbacks[:1]
        result["fallback_providers"] = fallbacks if fallback else []

    elif provider_type == ProviderType.SMS:
        primary = []
        fallbacks = []

        for name, provider in SMS_PROVIDERS.items():
            countries = provider.get("supported_countries", [])
            if "*" in countries or country in countries:
                if provider["default_priority"] == ProviderPriority.PRIMARY:
                    primary.append({"id": name.value, **provider})
                else:
                    fallbacks.append({"id": name.value, **provider})

        result["selected"] = primary[:1] if primary else fallbacks[:1]
        result["fallback_providers"] = fallbacks if fallback else []

    elif provider_type == ProviderType.SATELLITE:
        # Select satellite providers - prefer free/low cost
        providers_list = []
        for name, provider in SATELLITE_PROVIDERS.items():
            providers_list.append({"id": name.value, **provider})

        # Sort by cost
        providers_list.sort(key=lambda x: x.get("cost_per_km2", 0))
        result["selected"] = providers_list[:2]
        result["fallback_providers"] = providers_list[2:] if fallback else []

    elif provider_type == ProviderType.WEATHER:
        providers_list = []
        for name, provider in WEATHER_PROVIDERS.items():
            providers_list.append({"id": name.value, **provider})

        # Free providers first
        free = [p for p in providers_list if not p.get("requires_api_key")]
        paid = [p for p in providers_list if p.get("requires_api_key")]

        result["selected"] = free[:1] if free else paid[:1]
        result["fallback_providers"] = (free[1:] + paid) if fallback else []

    return result


@app.get("/providers/failover-chain/{provider_type}")
async def get_failover_chain(
    provider_type: ProviderType,
    country: str = "YE",
):
    """
    Get ordered failover chain for a provider type
    سلسلة الاحتياط المرتبة لنوع المزود
    """
    chain = []

    if provider_type == ProviderType.PAYMENT:
        # Build payment failover chain
        for priority in [
            ProviderPriority.PRIMARY,
            ProviderPriority.SECONDARY,
            ProviderPriority.TERTIARY,
        ]:
            for name, provider in PAYMENT_PROVIDERS.items():
                if provider["default_priority"] == priority:
                    if country in provider.get("supported_countries", []):
                        chain.append(
                            {
                                "order": len(chain) + 1,
                                "provider_id": name.value,
                                "name": provider["name"],
                                "name_ar": provider["name_ar"],
                                "priority": priority.value,
                                "fee_percent": provider.get("transaction_fee_percent"),
                            }
                        )

    elif provider_type == ProviderType.SMS:
        for priority in [
            ProviderPriority.PRIMARY,
            ProviderPriority.SECONDARY,
            ProviderPriority.TERTIARY,
        ]:
            for name, provider in SMS_PROVIDERS.items():
                if provider["default_priority"] == priority:
                    countries = provider.get("supported_countries", [])
                    if "*" in countries or country in countries:
                        chain.append(
                            {
                                "order": len(chain) + 1,
                                "provider_id": name.value,
                                "name": provider["name"],
                                "name_ar": provider["name_ar"],
                                "priority": priority.value,
                                "cost_per_sms": provider.get("cost_per_sms_usd"),
                            }
                        )

    elif provider_type == ProviderType.SATELLITE:
        for priority in [
            ProviderPriority.PRIMARY,
            ProviderPriority.SECONDARY,
            ProviderPriority.TERTIARY,
        ]:
            for name, provider in SATELLITE_PROVIDERS.items():
                if provider["default_priority"] == priority:
                    chain.append(
                        {
                            "order": len(chain) + 1,
                            "provider_id": name.value,
                            "name": provider["name"],
                            "name_ar": provider["name_ar"],
                            "priority": priority.value,
                            "resolution_meters": provider.get("resolution_meters"),
                            "cost_per_km2": provider.get("cost_per_km2"),
                        }
                    )

    return {
        "provider_type": provider_type.value,
        "country": country,
        "failover_chain": chain,
        "total_providers": len(chain),
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
            raise HTTPException(
                status_code=400, detail=f"Unknown map provider: {request.provider_name}"
            )

    elif request.provider_type == ProviderType.WEATHER:
        try:
            provider_name = WeatherProviderName(request.provider_name)
            return await check_weather_provider_health(provider_name, request.api_key)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown weather provider: {request.provider_name}",
            )

    raise HTTPException(
        status_code=400, detail=f"Unsupported provider type: {request.provider_type}"
    )


@app.get("/providers/check/all")
async def check_all_free_providers():
    """Check health of all free providers (no API key required)"""
    results = {
        "map_providers": [],
        "weather_providers": [],
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Check free map providers
    free_map_providers = [
        k for k, v in MAP_PROVIDERS.items() if not v["requires_api_key"]
    ]
    for provider_name in free_map_providers:
        status = await check_map_provider_health(provider_name)
        results["map_providers"].append(status.dict())

    # Check free weather providers
    free_weather_providers = [
        k for k, v in WEATHER_PROVIDERS.items() if not v["requires_api_key"]
    ]
    for provider_name in free_weather_providers:
        status = await check_weather_provider_health(provider_name)
        results["weather_providers"].append(status.dict())

    return results


# ─────────────────────────────────────────────────────────────────────────────
# TENANT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/config/{tenant_id}")
async def get_tenant_config(tenant_id: str, session: Session = Depends(get_db_session)):
    """Get provider configuration for a tenant"""
    if not config_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Get configs from database
    map_configs = config_service.get_tenant_configs(session, tenant_id, "map")
    weather_configs = config_service.get_tenant_configs(session, tenant_id, "weather")
    satellite_configs = config_service.get_tenant_configs(session, tenant_id, "satellite")
    payment_configs = config_service.get_tenant_configs(session, tenant_id, "payment")
    sms_configs = config_service.get_tenant_configs(session, tenant_id, "sms")
    notification_configs = config_service.get_tenant_configs(
        session, tenant_id, "notification"
    )

    # If no configs exist, return defaults
    if not (map_configs or weather_configs or satellite_configs):
        return {
            "tenant_id": tenant_id,
            "map_providers": [
                {
                    "provider_name": "openstreetmap",
                    "priority": "primary",
                    "enabled": True,
                },
                {
                    "provider_name": "esri_satellite",
                    "priority": "secondary",
                    "enabled": True,
                },
            ],
            "weather_providers": [
                {"provider_name": "open_meteo", "priority": "primary", "enabled": True},
            ],
            "satellite_providers": [],
            "payment_providers": [],
            "sms_providers": [],
            "notification_providers": [],
            "is_default": True,
        }

    # Return stored configs
    return {
        "tenant_id": tenant_id,
        "map_providers": [c.to_dict() for c in map_configs] if map_configs else [],
        "weather_providers": [c.to_dict() for c in weather_configs]
        if weather_configs
        else [],
        "satellite_providers": [c.to_dict() for c in satellite_configs]
        if satellite_configs
        else [],
        "payment_providers": [c.to_dict() for c in payment_configs]
        if payment_configs
        else [],
        "sms_providers": [c.to_dict() for c in sms_configs] if sms_configs else [],
        "notification_providers": [c.to_dict() for c in notification_configs]
        if notification_configs
        else [],
        "is_default": False,
    }


@app.post("/config/{tenant_id}")
async def update_tenant_config(
    tenant_id: str, config: TenantProviderConfig, session: Session = Depends(get_db_session)
):
    """Update provider configuration for a tenant"""
    if not config_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Update map providers
        for provider in config.map_providers:
            existing = config_service.get_config_by_name(
                session, tenant_id, "map", provider.provider_name
            )
            if existing:
                config_service.update_config(
                    session,
                    tenant_id,
                    "map",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )
            else:
                config_service.create_config(
                    session,
                    tenant_id,
                    "map",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )

        # Update weather providers
        for provider in config.weather_providers:
            existing = config_service.get_config_by_name(
                session, tenant_id, "weather", provider.provider_name
            )
            if existing:
                config_service.update_config(
                    session,
                    tenant_id,
                    "weather",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )
            else:
                config_service.create_config(
                    session,
                    tenant_id,
                    "weather",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )

        # Update satellite providers
        for provider in config.satellite_providers:
            existing = config_service.get_config_by_name(
                session, tenant_id, "satellite", provider.provider_name
            )
            if existing:
                config_service.update_config(
                    session,
                    tenant_id,
                    "satellite",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )
            else:
                config_service.create_config(
                    session,
                    tenant_id,
                    "satellite",
                    provider.provider_name,
                    api_key=provider.api_key,
                    priority=provider.priority,
                    enabled=provider.enabled,
                )

        return {"success": True, "message": "Configuration updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@app.delete("/config/{tenant_id}")
async def reset_tenant_config(tenant_id: str, session: Session = Depends(get_db_session)):
    """Reset tenant configuration to defaults"""
    if not config_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Get all configs for tenant
        all_configs = config_service.get_tenant_configs(session, tenant_id)

        # Delete all configs
        for config in all_configs:
            config_service.delete_config(
                session, tenant_id, config.provider_type, config.provider_name
            )

        return {"success": True, "message": "Configuration reset to defaults"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset config: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# VERSION HISTORY
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/config/{tenant_id}/history")
async def get_config_history(
    tenant_id: str,
    provider_type: str | None = None,
    limit: int = 100,
    session: Session = Depends(get_db_session),
):
    """Get configuration change history for a tenant"""
    if not config_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        history = config_service.get_config_history(
            session, tenant_id, provider_type, limit
        )
        return {
            "tenant_id": tenant_id,
            "provider_type": provider_type,
            "history": [h.to_dict() for h in history],
            "total": len(history),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get history: {str(e)}"
        )


@app.post("/config/{tenant_id}/rollback")
async def rollback_config(
    tenant_id: str,
    config_id: str,
    version: int,
    session: Session = Depends(get_db_session),
):
    """Rollback configuration to a specific version"""
    if not config_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        config = config_service.rollback_to_version(session, config_id, version)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration or version not found")

        return {
            "success": True,
            "message": f"Configuration rolled back to version {version}",
            "config": config.to_dict(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to rollback: {str(e)}"
        )


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
            {
                "provider": "openstreetmap",
                "reason": "مجاني، يدعم الاستخدام غير المتصل",
                "reason_en": "Free, supports offline",
            },
            {
                "provider": "esri_satellite",
                "reason": "صور أقمار صناعية مجانية",
                "reason_en": "Free satellite imagery",
            },
        ]
        recommendations["weather"] = [
            {
                "provider": "open_meteo",
                "reason": "مجاني، 16 يوم توقعات",
                "reason_en": "Free, 16-day forecast",
            },
        ]
    elif budget in ["low", "medium"]:
        recommendations["map"] = [
            {
                "provider": "mapbox_streets",
                "reason": "جودة عالية، تكلفة منخفضة",
                "reason_en": "High quality, low cost",
            },
            {
                "provider": "mapbox_satellite",
                "reason": "صور أقمار صناعية عالية الجودة",
                "reason_en": "High quality satellite",
            },
        ]
        recommendations["weather"] = [
            {
                "provider": "open_meteo",
                "reason": "مجاني كمصدر أساسي",
                "reason_en": "Free as primary",
            },
            {
                "provider": "openweathermap",
                "reason": "تنبيهات جوية",
                "reason_en": "Weather alerts",
            },
        ]
        recommendations["satellite"] = [
            {
                "provider": "sentinel_hub",
                "reason": "أفضل قيمة للزراعة",
                "reason_en": "Best value for agriculture",
            },
        ]
    else:  # high budget
        recommendations["map"] = [
            {
                "provider": "google_hybrid",
                "reason": "أفضل جودة وتفاصيل",
                "reason_en": "Best quality and detail",
            },
        ]
        recommendations["satellite"] = [
            {
                "provider": "planet_labs",
                "reason": "صور يومية، دقة 3 متر",
                "reason_en": "Daily imagery, 3m resolution",
            },
        ]

    return recommendations


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8104)
