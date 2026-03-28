"""
SAHOOL Satellite Service v15.6
خدمة الأقمار الصناعية - Sentinel-2, Landsat, MODIS Integration

Multi-Provider Support:
- Sentinel Hub (ESA Copernicus) - Free tier available
- Copernicus STAC - Free, no auth required for search
- NASA Earthdata - Free with registration
- Simulated - Always available fallback

Field-First Architecture:
- NATS integration for real-time event publishing
- ActionTemplate output for mobile app task cards
"""

import io
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from enum import Enum, StrEnum
from typing import Any

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from shared.auth.dependencies import get_current_user
from shared.auth.models import User

logger = structlog.get_logger(__name__)


def _validate_field_id(field_id: str) -> None:
    """Validate field_id path parameter."""
    if not field_id or len(field_id) > 100:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid field_id", "error_ar": "معرف الحقل غير صالح"},
        )


def _validate_planting_date_not_future(planting_date: date | None) -> None:
    """Validate that planting_date is not in the future."""
    if planting_date and planting_date > date.today():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Planting date cannot be in the future",
                "error_ar": "تاريخ الزراعة لا يمكن أن يكون في المستقبل",
            },
        )


def _validate_crop_type(crop_type: str | None) -> None:
    """Validate that crop_type is not null or empty."""
    if not crop_type or not crop_type.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "error": "crop_type is required and cannot be empty",
                "error_ar": "نوع المحصول مطلوب ولا يمكن أن يكون فارغاً",
            },
        )


def _validate_days_range(days: int) -> None:
    """Validate days parameter is within 1-365 range."""
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "days must be between 1 and 365",
                "error_ar": "عدد الأيام يجب أن يكون بين 1 و 365",
            },
        )


def _validate_ndvi_value(ndvi: float, label: str = "NDVI") -> None:
    """Validate NDVI value is within -1 to 1 range."""
    if ndvi < -1.0 or ndvi > 1.0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{label} value must be between -1.0 and 1.0",
                "error_ar": f"قيمة {label} يجب أن تكون بين -1.0 و 1.0",
            },
        )


# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Multi-provider service
USE_MULTI_PROVIDER = os.getenv("USE_MULTI_PROVIDER", "true").lower() == "true"
_multi_provider = None
_phenology_detector = None
_boundary_detector = None
_change_detector = None

try:
    from .multi_provider import (
        MultiSatelliteService,
    )
    from .multi_provider import (
        SatelliteType as MultiSatelliteType,
    )

    logger.info("Multi-provider satellite service loaded")
except ImportError as e:
    logger.warning(f"Multi-provider module not available: {e}")
    MultiSatelliteService = None

# SAR Processor for soil moisture
_sar_processor = None

# Yield predictor instance (will be initialized with imports)
_yield_predictor = None

# Cloud masker instance
_cloud_masker = None

try:
    from .sar_processor import (
        IrrigationEvent,
        SARDataPoint,
        SARProcessor,
        SoilMoistureResult,
    )

    logger.info("SAR Processor module loaded")
except ImportError as e:
    logger.warning(f"SAR Processor module not available: {e}")
    SARProcessor = None

# Redis cache integration
_cache_available = False
try:
    from .cache import (
        cache_analysis,
        cache_health_check,
        cache_timeseries,
        get_cache_stats,
        get_cached_analysis,
        get_cached_timeseries,
        is_cache_available,
    )

    _cache_available = True
    logger.info("Redis cache module loaded")
except ImportError:
    logger.info("Cache module not available - running without caching")

    async def is_cache_available():
        return False


# Import eo-learn integration
# Import boundary endpoints
from .boundary_endpoints import register_boundary_endpoints

# Import agricultural land detector (GeoLabel-inspired)
_land_detector = None
try:
    from .agricultural_land_detector import AgriculturalLandDetector
    from .parcel_endpoints import register_parcel_endpoints

    logger.info("Agricultural Land Detector module loaded (GeoLabel-inspired)")
except ImportError as e:
    logger.warning(f"Agricultural Land Detector module not available: {e}")
    AgriculturalLandDetector = None
    register_parcel_endpoints = None

# Import change detector
from .change_detector import (
    ChangeDetector,
    NDVIDataPoint,
)

# Import cloud masking system
from .cloud_masking import (
    get_cloud_masker,
)

# Import data exporter
from .data_exporter import DataExporter, ExportFormat
from .eo_integration import (
    EO_LEARN_AVAILABLE,
    SENTINEL_HUB_CONFIGURED,
    check_eo_configuration,
    convert_eo_result_to_api_format,
    fetch_real_satellite_data,
    get_data_source_status,
)

# Import field boundary detector
from .field_boundary_detector import (
    FieldBoundaryDetector,
)

# Import phenology detector
from .phenology_detector import (
    GrowthStage,
    PhenologyDetector,
    PhenologyResult,
)

# Import VRA endpoints
from .vra_endpoints import register_vra_endpoints

# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# Prometheus metric definitions
if HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "vegetation_requests_total",
        "Total vegetation API requests",
        ["endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "vegetation_request_duration_seconds",
        "Vegetation API request latency",
        ["endpoint"],
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


# Import weather integration
# Import yield predictor
from .yield_predictor import YieldPredictor

# Import advanced vegetation indices
try:
    from .vegetation_indices import (
        AllIndices,
        BandData,
        CropType,
        HealthStatus,
        IndexInterpreter,
        VegetationIndex,
        VegetationIndicesCalculator,
    )
    from .vegetation_indices import (
        GrowthStage as VegGrowthStage,
    )

    _indices_available = True
    logger.info("Advanced vegetation indices module loaded")
except ImportError as e:
    logger.warning(f"Advanced vegetation indices module not available: {e}")
    _indices_available = False

# Import VRA Generator
_vra_generator = None
try:
    from .vra_generator import (
        ManagementZone,
        PrescriptionMap,
        VRAGenerator,
        VRAType,
        ZoneLevel,
        ZoneMethod,
        ZoneStatistics,
    )

    logger.info("VRA Generator module loaded")
except ImportError as e:
    logger.warning(f"VRA Generator module not available: {e}")
    VRAGenerator = None

# Import NDVI Time-Series Analyzer
_ndvi_timeseries_analyzer = None
try:
    from .ndvi_timeseries import (
        AnomalyResult,
        ChangeDetectionResult,
        NDVIPoint,
        NDVITimeSeriesAnalyzer,
        SeasonalMetrics,
        TrendResult,
        create_ndvi_timeseries,
        export_results_to_dict,
    )

    _ndvi_timeseries_analyzer = NDVITimeSeriesAnalyzer(smoothing_window=5)
    logger.info("NDVI Time-Series Analyzer module loaded")
except ImportError as e:
    logger.warning(f"NDVI Time-Series Analyzer module not available: {e}")
    NDVITimeSeriesAnalyzer = None

# NATS publisher (optional)
_nats_available = False
try:
    # Add project root to path for shared imports (dynamic path instead of hardcoded)
    _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from shared.libs.events.nats_publisher import publish_analysis_completed_sync

    _nats_available = True
except ImportError:
    logger.info("NATS publisher not available - running without event publishing")
    publish_analysis_completed_sync = None

# ActionTemplate factory (optional)
_action_factory_available = False
try:
    from shared.contracts.actions import ActionTemplateFactory, ActionType, UrgencyLevel

    _action_factory_available = True
except ImportError:
    logger.info("ActionTemplate not available")
    ActionTemplateFactory = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global \
        _multi_provider, \
        _sar_processor, \
        _yield_predictor, \
        _phenology_detector, \
        _cloud_masker, \
        _change_detector, \
        _vra_generator, \
        _land_detector, \
        _boundary_detector

    logger.info("service_starting", service="satellite-service")

    # Initialize multi-provider service
    if USE_MULTI_PROVIDER and MultiSatelliteService:
        _multi_provider = MultiSatelliteService()
        providers = _multi_provider.get_available_providers()
        configured = [p["name"] for p in providers if p["configured"]]
        logger.info("multi_provider_initialized", providers=configured)
    else:
        _multi_provider = None
        logger.info("using_legacy_eolearn_integration")

    # Initialize phenology detector
    _phenology_detector = PhenologyDetector()
    logger.info("phenology_detector_loaded", crops_supported=len(_phenology_detector.YEMEN_CROP_SEASONS))

    # Initialize field boundary detector
    _boundary_detector = FieldBoundaryDetector(multi_provider=_multi_provider)
    logger.info("field_boundary_detector_initialized")

    # Initialize SAR processor
    if SARProcessor:
        _sar_processor = SARProcessor()
        logger.info("sar_processor_initialized")

    # Initialize Yield Predictor
    if YieldPredictor:
        _yield_predictor = YieldPredictor()
        logger.info("yield_predictor_initialized")

    # Initialize Change Detector
    _change_detector = ChangeDetector()
    logger.info("change_detector_initialized")

    # Initialize Cloud Masker
    _cloud_masker = get_cloud_masker()
    logger.info("cloud_masker_initialized")

    # Initialize VRA Generator
    if VRAGenerator:
        _vra_generator = VRAGenerator(multi_provider=_multi_provider)
        logger.info("vra_generator_initialized")

    # Initialize Agricultural Land Detector (GeoLabel-inspired)
    if AgriculturalLandDetector:
        _land_detector = AgriculturalLandDetector(multi_provider=_multi_provider)
        logger.info("agricultural_land_detector_initialized")

    # Register boundary detection endpoints
    if _boundary_detector:
        register_boundary_endpoints(app, _boundary_detector)

    # Register agricultural parcel detection endpoints
    if _land_detector and register_parcel_endpoints:
        register_parcel_endpoints(app, _land_detector)

    # Register VRA endpoints
    if _vra_generator:
        register_vra_endpoints(app, _vra_generator)

    logger.info("service_ready", service="satellite-service", port=8090)

    yield

    # Cleanup
    logger.info("service_shutting_down", service="satellite-service")
    if _multi_provider:
        try:
            await _multi_provider.close()
        except Exception as e:
            logger.warning(f"Error closing multi-provider: {e}")
    if _sar_processor:
        try:
            await _sar_processor.close()
        except Exception as e:
            logger.warning(f"Error closing SAR processor: {e}")
    logger.info("service_shutdown_complete", service="satellite-service")


app = FastAPI(
    title="SAHOOL Satellite Service | خدمة الأقمار الصناعية",
    version="16.0.0",
    description="Multi-provider satellite monitoring with automatic fallback. Supports Sentinel Hub, Copernicus STAC, NASA Earthdata. Includes Sentinel-1 SAR for soil moisture estimation. Now with GDD (Growing Degree Days) tracking for 40+ Yemen crops.",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Prometheus request metrics middleware
if HAS_PROMETHEUS:
    app.add_middleware(PrometheusMiddleware)

# Add tenant context middleware
try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
except ImportError:
    pass

# Register weather endpoints
from .weather_endpoints import register_weather_endpoints

register_weather_endpoints(app)

# Register GDD (Growing Degree Days) endpoints
from .gdd_endpoints import register_gdd_endpoints

register_gdd_endpoints(app)

# Register spray advisor endpoints
from .spray_endpoints import register_spray_endpoints

register_spray_endpoints(app)


# =============================================================================
# Enums & Models
# =============================================================================


class SatelliteSource(StrEnum):
    SENTINEL2 = "sentinel-2"
    LANDSAT8 = "landsat-8"
    LANDSAT9 = "landsat-9"
    MODIS = "modis"


class BandType(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    NIR = "nir"  # Near Infrared
    SWIR1 = "swir1"  # Short Wave Infrared 1
    SWIR2 = "swir2"  # Short Wave Infrared 2
    THERMAL = "thermal"


class ImageryRequest(BaseModel):
    field_id: str = Field(..., description="معرف الحقل")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    satellite: SatelliteSource = SatelliteSource.SENTINEL2
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None
    cloud_cover_max: float = Field(default=20.0, ge=0, le=100)


class SatelliteBand(BaseModel):
    band_name: str
    wavelength_nm: str
    resolution_m: int
    value: float


class SatelliteImagery(BaseModel):
    imagery_id: str
    field_id: str
    satellite: SatelliteSource
    acquisition_date: datetime
    cloud_cover_percent: float
    sun_elevation: float
    bands: list[SatelliteBand]
    scene_id: str
    tile_id: str
    processing_level: str


class VegetationIndices(BaseModel):
    ndvi: float = Field(..., description="Normalized Difference Vegetation Index")
    ndwi: float = Field(..., description="Normalized Difference Water Index")
    evi: float = Field(..., description="Enhanced Vegetation Index")
    savi: float = Field(..., description="Soil Adjusted Vegetation Index")
    lai: float = Field(..., description="Leaf Area Index estimate")
    ndmi: float = Field(..., description="Normalized Difference Moisture Index")


class FieldAnalysis(BaseModel):
    field_id: str
    analysis_date: datetime
    satellite: SatelliteSource
    imagery: SatelliteImagery
    indices: VegetationIndices
    health_score: float = Field(..., ge=0, le=100)
    health_status: str
    anomalies: list[str]
    recommendations_ar: list[str]
    recommendations_en: list[str]


class AdvancedVegetationIndices(BaseModel):
    """Extended vegetation indices including all advanced indices"""

    # Basic indices
    ndvi: float
    ndwi: float
    evi: float
    savi: float
    lai: float
    ndmi: float

    # Chlorophyll & Nitrogen
    ndre: float
    cvi: float
    mcari: float
    tcari: float
    sipi: float

    # Early Stress Detection
    gndvi: float
    vari: float
    gli: float
    grvi: float

    # Soil/Atmosphere Corrected
    msavi: float
    osavi: float
    arvi: float


class InterpretRequest(BaseModel):
    """Request for interpreting indices"""

    field_id: str = Field(..., description="معرف الحقل")
    indices: dict[str, float] = Field(..., description="Index values to interpret")
    crop_type: str | None = Field(default="unknown", description="نوع المحصول")
    growth_stage: str | None = Field(default="vegetative", description="مرحلة النمو")


class IndexInterpretationResponse(BaseModel):
    """Response for index interpretation"""

    index_name: str
    value: float
    status: str
    description_ar: str
    description_en: str
    confidence: float
    threshold_info: dict[str, float]


# =============================================================================
# Satellite Configuration
# =============================================================================

SATELLITE_CONFIGS = {
    SatelliteSource.SENTINEL2: {
        "name": "Sentinel-2 MSI",
        "operator": "ESA",
        "revisit_days": 5,
        "resolution_m": 10,
        "bands": {
            "B02": {"name": "Blue", "wavelength": "490nm", "resolution": 10},
            "B03": {"name": "Green", "wavelength": "560nm", "resolution": 10},
            "B04": {"name": "Red", "wavelength": "665nm", "resolution": 10},
            "B08": {"name": "NIR", "wavelength": "842nm", "resolution": 10},
            "B11": {"name": "SWIR1", "wavelength": "1610nm", "resolution": 20},
            "B12": {"name": "SWIR2", "wavelength": "2190nm", "resolution": 20},
        },
    },
    SatelliteSource.LANDSAT8: {
        "name": "Landsat-8 OLI/TIRS",
        "operator": "NASA/USGS",
        "revisit_days": 16,
        "resolution_m": 30,
        "bands": {
            "B2": {"name": "Blue", "wavelength": "482nm", "resolution": 30},
            "B3": {"name": "Green", "wavelength": "561nm", "resolution": 30},
            "B4": {"name": "Red", "wavelength": "654nm", "resolution": 30},
            "B5": {"name": "NIR", "wavelength": "865nm", "resolution": 30},
            "B6": {"name": "SWIR1", "wavelength": "1609nm", "resolution": 30},
            "B10": {"name": "Thermal", "wavelength": "10895nm", "resolution": 100},
        },
    },
    SatelliteSource.MODIS: {
        "name": "MODIS Terra/Aqua",
        "operator": "NASA",
        "revisit_days": 1,
        "resolution_m": 250,
        "bands": {
            "B01": {"name": "Red", "wavelength": "645nm", "resolution": 250},
            "B02": {"name": "NIR", "wavelength": "858nm", "resolution": 250},
            "B03": {"name": "Blue", "wavelength": "469nm", "resolution": 500},
            "B04": {"name": "Green", "wavelength": "555nm", "resolution": 500},
        },
    },
}

# Yemen regions monitoring - جميع محافظات اليمن الـ 22
YEMEN_REGIONS = {
    # المنطقة الشمالية
    "sana'a": {
        "lat": 15.3694,
        "lon": 44.1910,
        "name_ar": "صنعاء",
        "region": "highland",
    },
    "amanat_al_asimah": {
        "lat": 15.3556,
        "lon": 44.2067,
        "name_ar": "أمانة العاصمة",
        "region": "highland",
    },
    "amran": {"lat": 15.6594, "lon": 43.9439, "name_ar": "عمران", "region": "highland"},
    "saadah": {"lat": 16.9400, "lon": 43.7614, "name_ar": "صعدة", "region": "highland"},
    "al_jawf": {"lat": 16.5833, "lon": 45.5000, "name_ar": "الجوف", "region": "desert"},
    "hajjah": {"lat": 15.6917, "lon": 43.6028, "name_ar": "حجة", "region": "highland"},
    "al_mahwit": {
        "lat": 15.4700,
        "lon": 43.5447,
        "name_ar": "المحويت",
        "region": "highland",
    },
    # المنطقة الوسطى
    "dhamar": {"lat": 14.5500, "lon": 44.4000, "name_ar": "ذمار", "region": "highland"},
    "ibb": {"lat": 13.9667, "lon": 44.1667, "name_ar": "إب", "region": "highland"},
    "taiz": {"lat": 13.5789, "lon": 44.0219, "name_ar": "تعز", "region": "highland"},
    "al_bayda": {
        "lat": 13.9833,
        "lon": 45.5667,
        "name_ar": "البيضاء",
        "region": "highland",
    },
    "raymah": {"lat": 14.6333, "lon": 43.7167, "name_ar": "ريمة", "region": "highland"},
    "marib": {"lat": 15.4667, "lon": 45.3333, "name_ar": "مأرب", "region": "desert"},
    # المنطقة الساحلية الغربية
    "hodeidah": {
        "lat": 14.7979,
        "lon": 42.9540,
        "name_ar": "الحديدة",
        "region": "coastal",
    },
    # المنطقة الجنوبية
    "aden": {"lat": 12.7855, "lon": 45.0187, "name_ar": "عدن", "region": "coastal"},
    "lahij": {"lat": 13.0500, "lon": 44.8833, "name_ar": "لحج", "region": "highland"},
    "ad_dali": {
        "lat": 13.7000,
        "lon": 44.7333,
        "name_ar": "الضالع",
        "region": "highland",
    },
    "abyan": {"lat": 13.0167, "lon": 45.3667, "name_ar": "أبين", "region": "coastal"},
    # المنطقة الشرقية
    "hadramaut": {
        "lat": 15.9500,
        "lon": 48.7833,
        "name_ar": "حضرموت",
        "region": "desert",
    },
    "shabwah": {"lat": 14.5333, "lon": 46.8333, "name_ar": "شبوة", "region": "desert"},
    "al_mahrah": {
        "lat": 16.0667,
        "lon": 52.2333,
        "name_ar": "المهرة",
        "region": "coastal",
    },
    # الجزر
    "socotra": {"lat": 12.4634, "lon": 53.8237, "name_ar": "سقطرى", "region": "island"},
}


# =============================================================================
# Calculation Functions
# =============================================================================


def calculate_ndvi(nir: float, red: float) -> float:
    """NDVI = (NIR - Red) / (NIR + Red)"""
    if nir + red == 0:
        return 0.0
    return round((nir - red) / (nir + red), 4)


def calculate_ndwi(nir: float, swir: float) -> float:
    """NDWI = (NIR - SWIR) / (NIR + SWIR)"""
    if nir + swir == 0:
        return 0.0
    return round((nir - swir) / (nir + swir), 4)


def calculate_evi(nir: float, red: float, blue: float) -> float:
    """EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)"""
    denominator = nir + 6 * red - 7.5 * blue + 1
    if denominator == 0:
        return 0.0
    return round(2.5 * (nir - red) / denominator, 4)


def calculate_savi(nir: float, red: float, L: float = 0.5) -> float:
    """SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)"""
    if nir + red + L == 0:
        return 0.0
    return round(((nir - red) / (nir + red + L)) * (1 + L), 4)


def calculate_lai(ndvi: float) -> float:
    """Estimate LAI from NDVI using empirical relationship"""
    if ndvi <= 0:
        return 0.0
    # LAI = -ln((0.69 - NDVI) / 0.59) / 0.91
    import math

    try:
        lai = -math.log((0.69 - min(ndvi, 0.68)) / 0.59) / 0.91
        return round(max(0, min(lai, 8)), 2)
    except (ValueError, ZeroDivisionError, OverflowError):
        return 0.0


def calculate_ndmi(nir: float, swir: float) -> float:
    """NDMI = (NIR - SWIR1) / (NIR + SWIR1)"""
    if nir + swir == 0:
        return 0.0
    return round((nir - swir) / (nir + swir), 4)


def assess_vegetation_health(
    indices: VegetationIndices,
) -> tuple[float, str, list[str]]:
    """Assess crop health based on vegetation indices"""
    anomalies = []
    score = 50.0  # Base score

    # NDVI analysis
    if indices.ndvi >= 0.6:
        score += 20
    elif indices.ndvi >= 0.4:
        score += 10
    elif indices.ndvi >= 0.2:
        score += 0
    else:
        score -= 20
        anomalies.append("low_vegetation_cover")

    # Water stress (NDWI)
    if indices.ndwi < -0.2:
        score -= 15
        anomalies.append("water_stress_detected")
    elif indices.ndwi > 0.3:
        score += 10

    # Moisture stress (NDMI)
    if indices.ndmi < 0:
        score -= 10
        anomalies.append("moisture_deficit")

    # EVI analysis
    if indices.evi >= 0.4:
        score += 10
    elif indices.evi < 0.2:
        score -= 10
        anomalies.append("poor_canopy_structure")

    # LAI analysis
    if indices.lai >= 3:
        score += 10
    elif indices.lai < 1:
        score -= 5
        anomalies.append("sparse_leaf_coverage")

    score = max(0, min(100, score))

    if score >= 80:
        status = "ممتاز | Excellent"
    elif score >= 60:
        status = "جيد | Good"
    elif score >= 40:
        status = "متوسط | Fair"
    elif score >= 20:
        status = "ضعيف | Poor"
    else:
        status = "حرج | Critical"

    return score, status, anomalies


def generate_recommendations(indices: VegetationIndices, anomalies: list[str]) -> tuple[list[str], list[str]]:
    """Generate bilingual recommendations based on analysis"""
    recommendations_ar = []
    recommendations_en = []

    if "low_vegetation_cover" in anomalies:
        recommendations_ar.append("🌱 الغطاء النباتي منخفض - تحقق من صحة المحصول أو أعد الزراعة")
        recommendations_en.append("🌱 Low vegetation cover - check crop health or consider replanting")

    if "water_stress_detected" in anomalies:
        recommendations_ar.append("💧 إجهاد مائي - زيادة الري فوراً")
        recommendations_en.append("💧 Water stress detected - increase irrigation immediately")

    if "moisture_deficit" in anomalies:
        recommendations_ar.append("🌡️ نقص الرطوبة - ري تكميلي مطلوب")
        recommendations_en.append("🌡️ Moisture deficit - supplemental irrigation needed")

    if "poor_canopy_structure" in anomalies:
        recommendations_ar.append("🍃 بنية المظلة ضعيفة - تحقق من التسميد والآفات")
        recommendations_en.append("🍃 Poor canopy structure - check fertilization and pests")

    if "sparse_leaf_coverage" in anomalies:
        recommendations_ar.append("🌿 تغطية الأوراق متناثرة - قد يحتاج المحصول تسميد نيتروجيني")
        recommendations_en.append("🌿 Sparse leaf coverage - crop may need nitrogen fertilization")

    if not anomalies:
        recommendations_ar.append("✅ المحصول في حالة صحية جيدة - استمر في الممارسات الحالية")
        recommendations_en.append("✅ Crop is healthy - continue current practices")

    return recommendations_ar, recommendations_en


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
async def health():
    """Health check endpoint with comprehensive dependency status"""
    providers_info = None
    if _multi_provider:
        providers = _multi_provider.get_available_providers()
        providers_info = {
            "multi_provider_enabled": True,
            "total": len(providers),
            "configured": len([p for p in providers if p["configured"]]),
            "providers": [p["name"] for p in providers if p["configured"]],
        }

    cache_status = _cache_available and await is_cache_available()

    # Determine overall health status
    is_healthy = _nats_available or (providers_info and providers_info["configured"] > 0)

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "vegetation-analysis-service",
        "version": "16.0.0",
        "satellites": list(SATELLITE_CONFIGS.keys()),
        "multi_provider": providers_info,
        "eo_learn": get_data_source_status(),
        "nats_available": _nats_available,
        "action_factory_available": _action_factory_available,
        "cache_available": cache_status,
        "sar_processor_available": _sar_processor is not None,
    }


@app.get("/readyz")
async def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    checks = {}

    # Check database
    db_pool = getattr(app.state, "db_pool", None)
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "disconnected"
    else:
        checks["database"] = "not_configured"

    # Check NATS
    nc = getattr(app.state, "nc", None)
    if nc:
        checks["nats"] = "connected" if not nc.is_closed else "disconnected"
    else:
        checks["nats"] = "not_configured"

    all_ready = all(v != "disconnected" for v in checks.values())
    return {
        "status": "ready" if all_ready else "degraded",
        "service": "vegetation-analysis-service",
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


@app.get("/v1/providers")
async def get_providers():
    """
    Get list of available satellite data providers
    الحصول على قائمة مزودي بيانات الأقمار الصناعية المتاحين
    """
    if _multi_provider:
        providers = _multi_provider.get_available_providers()
        return {
            "multi_provider_enabled": True,
            "providers": providers,
            "total": len(providers),
            "configured": len([p for p in providers if p["configured"]]),
            "note": "Providers are tried in order until one succeeds",
        }
    else:
        return {
            "multi_provider_enabled": False,
            "providers": [
                {
                    "name": "eo-learn",
                    "name_ar": "معالجة محلية",
                    "configured": EO_LEARN_AVAILABLE and SENTINEL_HUB_CONFIGURED,
                    "satellites": ["sentinel-2", "landsat-8"],
                    "type": "SahoolEOClient",
                }
            ],
            "total": 1,
            "configured": 1 if (EO_LEARN_AVAILABLE and SENTINEL_HUB_CONFIGURED) else 0,
        }


@app.get("/v1/cache/stats")
async def cache_statistics():
    """إحصائيات الـCache"""
    if not _cache_available:
        return {"available": False, "message": "Cache module not loaded"}
    return await get_cache_stats()


@app.get("/v1/cache/health")
async def cache_health():
    """فحص صحة الـCache"""
    if not _cache_available:
        return {"status": "unavailable", "message": "Cache module not loaded"}
    return await cache_health_check()


@app.get("/v1/eo-status")
def eo_status():
    """حالة تكامل eo-learn"""
    return {
        "status": get_data_source_status(),
        "configuration": check_eo_configuration(),
        "setup_instructions": {
            "1_install": "pip install sahool-eo[full]",
            "2_credentials": "Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET",
            "3_optional": "Get credentials at https://www.sentinel-hub.com/",
        },
    }


@app.get("/v1/satellites", response_model=dict)
def list_satellites():
    """قائمة الأقمار الصناعية المتاحة"""
    return {
        "satellites": [
            {
                "id": sat.value,
                "name": config["name"],
                "operator": config["operator"],
                "revisit_days": config["revisit_days"],
                "resolution_m": config["resolution_m"],
                "bands_count": len(config["bands"]),
            }
            for sat, config in SATELLITE_CONFIGS.items()
        ]
    }


@app.get("/v1/regions", response_model=dict)
def list_monitored_regions():
    """المناطق المراقبة في اليمن"""
    return {
        "regions": [
            {
                "id": region_id,
                "name_ar": data["name_ar"],
                "latitude": data["lat"],
                "longitude": data["lon"],
            }
            for region_id, data in YEMEN_REGIONS.items()
        ]
    }


def _enforce_tenant(user: User, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant."""
    if user.tenant_id and user.tenant_id != requested_tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                "message_en": "Cannot access another tenant's data",
            },
        )


@app.post("/v1/imagery/request", response_model=SatelliteImagery)
async def request_imagery(request: ImageryRequest, user: User = Depends(get_current_user)):
    """طلب صور الأقمار الصناعية لحقل معين"""

    config = SATELLITE_CONFIGS[request.satellite]

    # Simulate satellite imagery acquisition
    import random

    # Generate realistic band values (reflectance 0-1)
    band_values = {
        "blue": random.uniform(0.02, 0.08),
        "green": random.uniform(0.03, 0.12),
        "red": random.uniform(0.02, 0.15),
        "nir": random.uniform(0.15, 0.55),
        "swir1": random.uniform(0.08, 0.35),
        "swir2": random.uniform(0.05, 0.25),
    }

    bands = []
    for band_id, band_info in config["bands"].items():
        band_type = band_info["name"].lower()
        value = band_values.get(band_type, random.uniform(0.05, 0.3))
        bands.append(
            SatelliteBand(
                band_name=band_id,
                wavelength_nm=band_info["wavelength"],
                resolution_m=band_info["resolution"],
                value=round(value, 4),
            )
        )

    return SatelliteImagery(
        imagery_id=str(uuid.uuid4()),
        field_id=request.field_id,
        satellite=request.satellite,
        acquisition_date=datetime.now(UTC),
        cloud_cover_percent=random.uniform(0, request.cloud_cover_max),
        sun_elevation=random.uniform(45, 75),
        bands=bands,
        scene_id=f"{request.satellite.value.upper()}_{datetime.now().strftime('%Y%m%d')}_{random.randint(1000, 9999)}",
        tile_id=f"T{random.randint(30, 40)}Q{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}",
        processing_level=("L2A" if request.satellite == SatelliteSource.SENTINEL2 else "L2"),
    )


@app.post("/v1/analyze", response_model=FieldAnalysis)
async def analyze_field(request: ImageryRequest, user: User = Depends(get_current_user)):
    """تحليل شامل للحقل باستخدام بيانات الأقمار الصناعية"""
    _validate_field_id(request.field_id)

    # Get imagery first
    imagery = await request_imagery(request)

    # Extract band values for calculations
    bands_dict = {b.band_name: b.value for b in imagery.bands}

    # Map to standard names based on satellite
    if request.satellite == SatelliteSource.SENTINEL2:
        red = bands_dict.get("B04", 0.1)
        bands_dict.get("B03", 0.1)
        blue = bands_dict.get("B02", 0.05)
        nir = bands_dict.get("B08", 0.3)
        swir1 = bands_dict.get("B11", 0.2)
    elif request.satellite in [SatelliteSource.LANDSAT8, SatelliteSource.LANDSAT9]:
        red = bands_dict.get("B4", 0.1)
        bands_dict.get("B3", 0.1)
        blue = bands_dict.get("B2", 0.05)
        nir = bands_dict.get("B5", 0.3)
        swir1 = bands_dict.get("B6", 0.2)
    else:  # MODIS
        red = bands_dict.get("B01", 0.1)
        bands_dict.get("B04", 0.1)
        blue = bands_dict.get("B03", 0.05)
        nir = bands_dict.get("B02", 0.3)
        swir1 = 0.2  # MODIS doesn't have SWIR at this resolution

    # Calculate vegetation indices
    indices = VegetationIndices(
        ndvi=calculate_ndvi(nir, red),
        ndwi=calculate_ndwi(nir, swir1),
        evi=calculate_evi(nir, red, blue),
        savi=calculate_savi(nir, red),
        lai=calculate_lai(calculate_ndvi(nir, red)),
        ndmi=calculate_ndmi(nir, swir1),
    )

    # Assess health
    health_score, health_status, anomalies = assess_vegetation_health(indices)

    # Generate recommendations
    recommendations_ar, recommendations_en = generate_recommendations(indices, anomalies)

    return FieldAnalysis(
        field_id=request.field_id,
        analysis_date=datetime.now(UTC),
        satellite=request.satellite,
        imagery=imagery,
        indices=indices,
        health_score=health_score,
        health_status=health_status,
        anomalies=anomalies,
        recommendations_ar=recommendations_ar,
        recommendations_en=recommendations_en,
    )


class AnalyzeWithActionRequest(BaseModel):
    """Request for analysis with ActionTemplate output"""

    field_id: str = Field(..., description="معرف الحقل")
    farmer_id: str | None = Field(None, description="معرف المزارع")
    tenant_id: str | None = Field(None, description="معرف المستأجر")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    satellite: SatelliteSource = SatelliteSource.SENTINEL2
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None
    cloud_cover_max: float = Field(default=20.0, ge=0, le=100)
    publish_event: bool = Field(default=True, description="نشر الحدث عبر NATS")


def _determine_urgency_from_anomalies(anomalies: list[str], health_score: float) -> str:
    """Determine urgency level based on anomalies and health score"""
    if health_score < 20 or "water_stress_detected" in anomalies:
        return "high"
    elif health_score < 40 or len(anomalies) >= 2:
        return "medium"
    elif anomalies:
        return "low"
    return "low"


def _create_satellite_action_template(
    analysis: FieldAnalysis,
    farmer_id: str | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """Create an ActionTemplate from satellite analysis"""

    urgency = _determine_urgency_from_anomalies(analysis.anomalies, analysis.health_score)

    # Determine action type based on anomalies
    if "water_stress_detected" in analysis.anomalies or "moisture_deficit" in analysis.anomalies:
        action_type = "irrigation"
        title_ar = "ري الحقل - إجهاد مائي مكتشف"
        title_en = "Field Irrigation - Water Stress Detected"
    elif "low_vegetation_cover" in analysis.anomalies:
        action_type = "inspection"
        title_ar = "فحص الحقل - انخفاض الغطاء النباتي"
        title_en = "Field Inspection - Low Vegetation Cover"
    elif "poor_canopy_structure" in analysis.anomalies:
        action_type = "fertilization"
        title_ar = "تسميد الحقل - بنية مظلة ضعيفة"
        title_en = "Field Fertilization - Poor Canopy Structure"
    else:
        action_type = "monitoring"
        title_ar = "مراقبة الحقل - تحديث منتظم"
        title_en = "Field Monitoring - Regular Update"

    return {
        "action_id": str(uuid.uuid4()),
        "action_type": action_type,
        "title_ar": title_ar,
        "title_en": title_en,
        "description_ar": " | ".join(analysis.recommendations_ar),
        "description_en": " | ".join(analysis.recommendations_en),
        "summary_ar": f"صحة الحقل: {analysis.health_status} (NDVI: {analysis.indices.ndvi})",
        "source_service": "satellite-service",
        "source_analysis_type": "satellite_vegetation_analysis",
        "confidence": round(analysis.health_score / 100, 2),
        "urgency": urgency,
        "field_id": analysis.field_id,
        "farmer_id": farmer_id,
        "tenant_id": tenant_id,
        "offline_executable": True,
        "fallback_instructions_ar": "في حال عدم توفر البيانات، قم بفحص الحقل بصرياً وتحقق من رطوبة التربة",
        "fallback_instructions_en": "If data unavailable, visually inspect field and check soil moisture",
        "estimated_duration_minutes": 60,
        "data": {
            "indices": {
                "ndvi": analysis.indices.ndvi,
                "ndwi": analysis.indices.ndwi,
                "evi": analysis.indices.evi,
                "savi": analysis.indices.savi,
                "lai": analysis.indices.lai,
                "ndmi": analysis.indices.ndmi,
            },
            "health_score": analysis.health_score,
            "health_status": analysis.health_status,
            "anomalies": analysis.anomalies,
            "satellite": analysis.satellite.value,
            "analysis_date": analysis.analysis_date.isoformat(),
        },
        "created_at": datetime.now(UTC).isoformat(),
    }


@app.post("/v1/analyze-with-action")
async def analyze_field_with_action(
    request: AnalyzeWithActionRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    تحليل الحقل مع إنتاج ActionTemplate

    Field-First: ينتج قالب إجراء للتطبيق المحمول
    ينشر الحدث عبر NATS للإشعارات الفورية
    """
    # Enforce tenant isolation
    if request.tenant_id:
        _enforce_tenant(user, request.tenant_id)

    # Perform analysis
    imagery_request = ImageryRequest(
        field_id=request.field_id,
        latitude=request.latitude,
        longitude=request.longitude,
        satellite=request.satellite,
        start_date=request.start_date,
        end_date=request.end_date,
        cloud_cover_max=request.cloud_cover_max,
    )

    analysis = await analyze_field(imagery_request)

    # Create ActionTemplate
    action_template = _create_satellite_action_template(
        analysis=analysis,
        farmer_id=request.farmer_id,
        tenant_id=request.tenant_id,
    )

    # Publish event to NATS (in background)
    if request.publish_event and _nats_available and publish_analysis_completed_sync:
        try:
            publish_analysis_completed_sync(
                event_type="satellite.analysis_completed",
                source_service="satellite-service",
                field_id=request.field_id,
                data=action_template.get("data", {}),
                action_template=action_template,
                priority=action_template.get("urgency", "medium"),
                farmer_id=request.farmer_id,
                tenant_id=request.tenant_id,
            )
            logger.info(f"NATS: Published satellite analysis event for field {request.field_id}")
        except Exception as e:
            logger.error(f"Failed to publish NATS event: {e}")

    # Create task card for mobile app
    task_card = {
        "id": action_template["action_id"],
        "type": action_template["action_type"],
        "title_ar": action_template["title_ar"],
        "title_en": action_template["title_en"],
        "urgency": {
            "level": action_template["urgency"],
            "color": {
                "low": "#22C55E",
                "medium": "#EAB308",
                "high": "#F97316",
                "critical": "#EF4444",
            }.get(action_template["urgency"], "#6B7280"),
        },
        "field_id": request.field_id,
        "confidence_percent": int(action_template["confidence"] * 100),
        "offline_ready": action_template["offline_executable"],
        "health_score": analysis.health_score,
        "health_status": analysis.health_status,
    }

    return {
        "analysis": {
            "field_id": analysis.field_id,
            "satellite": analysis.satellite.value,
            "indices": {
                "ndvi": analysis.indices.ndvi,
                "ndwi": analysis.indices.ndwi,
                "evi": analysis.indices.evi,
                "savi": analysis.indices.savi,
                "lai": analysis.indices.lai,
                "ndmi": analysis.indices.ndmi,
            },
            "health_score": analysis.health_score,
            "health_status": analysis.health_status,
            "anomalies": analysis.anomalies,
            "recommendations_ar": analysis.recommendations_ar,
            "recommendations_en": analysis.recommendations_en,
        },
        "action_template": action_template,
        "task_card": task_card,
        "nats_published": request.publish_event and _nats_available,
    }


class RealAnalysisRequest(BaseModel):
    """Request model for real satellite analysis"""

    field_id: str = Field(..., description="معرف الحقل")
    tenant_id: str = Field(default="default", description="معرف المستأجر")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: date = Field(default_factory=date.today)
    end_date: date | None = None
    cloud_cover_max: float = Field(default=30.0, ge=0, le=100)


@app.post("/v1/analyze/real")
async def analyze_field_real(
    request: RealAnalysisRequest,
    user: User = Depends(get_current_user),
):
    """
    تحليل الحقل باستخدام بيانات الأقمار الصناعية الحقيقية

    يستخدم sahool-eo و Sentinel Hub للحصول على بيانات حقيقية.
    إذا لم تكن الاعتمادات مكونة، يعود إلى البيانات المحاكاة.
    """
    _validate_field_id(request.field_id)

    # Enforce tenant isolation
    _enforce_tenant(user, request.tenant_id)

    # Try real data first
    if EO_LEARN_AVAILABLE and SENTINEL_HUB_CONFIGURED:
        result = await fetch_real_satellite_data(
            field_id=request.field_id,
            tenant_id=request.tenant_id,
            latitude=request.latitude,
            longitude=request.longitude,
            start_date=request.start_date,
            end_date=request.end_date,
            max_cloud_cover=request.cloud_cover_max,
        )

        if result:
            return convert_eo_result_to_api_format(
                result,
                request.field_id,
            )

    # Fallback to simulated analysis
    simulated_request = ImageryRequest(
        field_id=request.field_id,
        latitude=request.latitude,
        longitude=request.longitude,
        start_date=request.start_date,
        end_date=request.end_date,
        cloud_cover_max=request.cloud_cover_max,
    )

    analysis = await analyze_field(simulated_request)

    return {
        "field_id": analysis.field_id,
        "analysis_date": analysis.analysis_date.isoformat(),
        "satellite": analysis.satellite.value,
        "data_source": "simulated",
        "indices": {
            "ndvi": analysis.indices.ndvi,
            "ndwi": analysis.indices.ndwi,
            "evi": analysis.indices.evi,
            "savi": analysis.indices.savi,
            "lai": analysis.indices.lai,
            "ndmi": analysis.indices.ndmi,
        },
        "health_score": analysis.health_score,
        "health_status": analysis.health_status,
        "anomalies": analysis.anomalies,
        "recommendations_ar": analysis.recommendations_ar,
        "recommendations_en": analysis.recommendations_en,
        "note": "Using simulated data. Configure Sentinel Hub for real data.",
    }


async def _get_timeseries_data(
    field_id: str,
    days: int = 30,
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
) -> dict:
    """Internal helper for timeseries data generation (no auth required)."""
    _validate_field_id(field_id)

    import random

    # Generate time series data
    timeseries = []
    base_ndvi = random.uniform(0.3, 0.5)

    for i in range(0, days, SATELLITE_CONFIGS[satellite]["revisit_days"]):
        date_point = datetime.now(UTC) - timedelta(days=days - i)
        # Add realistic variation
        ndvi = base_ndvi + random.uniform(-0.1, 0.15) + (i / days) * 0.2
        ndvi = max(0, min(1, ndvi))

        timeseries.append(
            {
                "date": date_point.isoformat(),
                "ndvi": round(ndvi, 4),
                "ndwi": round(random.uniform(-0.2, 0.4), 4),
                "evi": round(ndvi * 0.8, 4),
                "cloud_cover": round(random.uniform(0, 30), 1),
            }
        )

    return {
        "field_id": field_id,
        "satellite": satellite.value,
        "period_days": days,
        "data_points": len(timeseries),
        "timeseries": timeseries,
        "trend": ("improving" if timeseries[-1]["ndvi"] > timeseries[0]["ndvi"] else "declining"),
    }



@app.get("/v1/timeseries/{field_id}")
async def get_timeseries(
    field_id: str,
    days: int = Query(default=30, ge=7, le=365),
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
    user: User = Depends(get_current_user),
):
    """الحصول على سلسلة زمنية للمؤشرات النباتية"""
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="timeseries")

    return await _get_timeseries_data(field_id, days, satellite)


# =============================================================================
# NDVI Time-Series Analysis Endpoints
# نقاط نهاية تحليل السلاسل الزمنية لمؤشر NDVI
# =============================================================================


@app.post("/v1/ndvi-timeseries/analyze/{field_id}")
async def analyze_ndvi_timeseries(
    field_id: str,
    days: int = Query(default=60, ge=14, le=365, description="Days of historical data"),
    anomaly_threshold: float = Query(
        default=2.0, ge=1.0, le=4.0, description="Z-score threshold for anomaly detection"
    ),
    user: User = Depends(get_current_user),
):
    """
    تحليل شامل للسلسلة الزمنية لمؤشر NDVI
    Comprehensive NDVI time-series analysis

    Includes:
    - Anomaly detection (كشف الشذوذ)
    - Trend analysis (تحليل الاتجاه)
    - Phenological stage detection (كشف مراحل النمو)
    - Seasonal metrics (المقاييس الموسمية)
    - 7-day forecast (تنبؤ 7 أيام)
    """
    _validate_field_id(field_id)
    if not _ndvi_timeseries_analyzer or NDVITimeSeriesAnalyzer is None:
        raise HTTPException(status_code=500, detail="NDVI Time-Series Analyzer not initialized")

    # Get NDVI time series data
    timeseries_data = await _get_timeseries_data(field_id, days)

    # Convert to NDVIPoint objects
    ndvi_points = []
    for point in timeseries_data["timeseries"]:
        try:
            point_date = datetime.fromisoformat(point["date"].replace("Z", "+00:00")).date()
            ndvi_points.append(
                NDVIPoint(
                    date=point_date,
                    value=point["ndvi"],
                    quality=1.0 - (point.get("cloud_cover", 0) / 100),
                    cloud_coverage=point.get("cloud_cover", 0),
                )
            )
        except (ValueError, KeyError):
            continue

    if len(ndvi_points) < 5:
        raise HTTPException(status_code=400, detail="Insufficient data points for analysis")

    # Sort by date
    ndvi_points.sort(key=lambda p: p.date)
    dates = [p.date for p in ndvi_points]
    values = [p.value for p in ndvi_points]

    # Perform analysis
    anomalies = _ndvi_timeseries_analyzer.detect_anomalies(ndvi_points, threshold=anomaly_threshold)
    trend = _ndvi_timeseries_analyzer.calculate_trend(values, dates)
    phenology_stages = _ndvi_timeseries_analyzer.detect_phenological_stages(ndvi_points)
    predictions = _ndvi_timeseries_analyzer.predict_next_values(ndvi_points, periods=7)

    # Calculate seasonal metrics
    season_start = _ndvi_timeseries_analyzer.identify_growing_season_start(ndvi_points)
    peak = _ndvi_timeseries_analyzer.identify_peak_greenness(ndvi_points)
    seasonal_integral = _ndvi_timeseries_analyzer.calculate_seasonal_integral(ndvi_points)

    seasonal_metrics = SeasonalMetrics(
        season_start=season_start,
        peak_date=peak[0] if peak else None,
        peak_ndvi=peak[1] if peak else None,
        integrated_ndvi=seasonal_integral,
    )

    # Publish NDVI trend event to NATS
    if _nats_available and publish_analysis_completed_sync:
        try:
            trend_direction = trend.trend_type.value
            current_ndvi = round(values[-1], 4) if values else None
            avg_ndvi = round(sum(values) / len(values), 4) if values else None
            publish_analysis_completed_sync(
                event_type="satellite.ndvi.trend",
                source_service="vegetation-analysis-service",
                field_id=field_id,
                data={
                    "field_id": field_id,
                    "trend_direction": trend_direction,
                    "current_ndvi": current_ndvi,
                    "average_ndvi": avg_ndvi,
                    "period_days": days,
                    "data_points": len(ndvi_points),
                    "has_anomalies": len(anomalies) > 0,
                    "anomaly_count": len(anomalies),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                priority="high" if trend_direction == "declining" else "medium",
            )
            logger.info(
                "nats_ndvi_trend_published",
                field_id=field_id,
                trend_direction=trend_direction,
            )
        except Exception as e:
            logger.error("nats_publish_failed", subject="satellite.ndvi.trend", error=str(e))

    return {
        "field_id": field_id,
        "analysis_date": datetime.now(UTC).isoformat(),
        "period_days": days,
        "data_points": len(ndvi_points),
        "anomalies": {"count": len(anomalies), "items": [a.to_dict() for a in anomalies]},
        "trend": trend.to_dict(),
        "phenology": {
            "stages_detected": len(phenology_stages),
            "stages": [
                {"date": s[0].isoformat(), "stage": s[1].value, "confidence": s[2]}
                for s in phenology_stages[:10]  # First 10
            ],
        },
        "seasonal_metrics": seasonal_metrics.to_dict(),
        "forecast": {
            "period_days": 7,
            "predictions": [{"date": p[0].isoformat(), "predicted_ndvi": round(p[1], 4)} for p in predictions],
        },
        "summary": {
            "current_ndvi": round(values[-1], 4) if values else None,
            "average_ndvi": round(sum(values) / len(values), 4) if values else None,
            "has_anomalies": len(anomalies) > 0,
            "trend_direction": trend.trend_type.value,
            "health_status": "good" if values[-1] > 0.4 else "moderate" if values[-1] > 0.2 else "poor",
        },
    }


@app.post("/v1/ndvi-timeseries/compare/{field_id}")
async def compare_ndvi_periods(
    field_id: str,
    period1_start: str = Query(..., description="Period 1 start date (YYYY-MM-DD)"),
    period1_end: str = Query(..., description="Period 1 end date (YYYY-MM-DD)"),
    period2_start: str = Query(..., description="Period 2 start date (YYYY-MM-DD)"),
    period2_end: str = Query(..., description="Period 2 end date (YYYY-MM-DD)"),
    user: User = Depends(get_current_user),
):
    """
    مقارنة فترتين زمنيتين لكشف التغييرات
    Compare two time periods to detect changes

    Useful for:
    - Year-over-year comparison (مقارنة سنوية)
    - Before/after events (قبل/بعد الأحداث)
    - Seasonal comparisons (مقارنات موسمية)
    """
    _validate_field_id(field_id)

    if not _ndvi_timeseries_analyzer or NDVITimeSeriesAnalyzer is None:
        raise HTTPException(status_code=500, detail="NDVI Time-Series Analyzer not initialized")

    try:
        p1_start = datetime.fromisoformat(period1_start).date()
        p1_end = datetime.fromisoformat(period1_end).date()
        p2_start = datetime.fromisoformat(period2_start).date()
        p2_end = datetime.fromisoformat(period2_end).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get data for both periods (simulated for now)
    import random

    period1_values = [random.uniform(0.3, 0.6) for _ in range((p1_end - p1_start).days)]
    period2_values = [random.uniform(0.35, 0.65) for _ in range((p2_end - p2_start).days)]

    # Compare periods
    change_result = _ndvi_timeseries_analyzer.compare_periods(period1_values, period2_values)

    return {
        "field_id": field_id,
        "comparison_date": datetime.now(UTC).isoformat(),
        "period1": {
            "start": period1_start,
            "end": period1_end,
            "days": (p1_end - p1_start).days,
            "mean_ndvi": round(sum(period1_values) / len(period1_values), 4) if period1_values else None,
        },
        "period2": {
            "start": period2_start,
            "end": period2_end,
            "days": (p2_end - p2_start).days,
            "mean_ndvi": round(sum(period2_values) / len(period2_values), 4) if period2_values else None,
        },
        "change_analysis": change_result.to_dict(),
        "recommendation_ar": change_result.description_ar,
        "recommendation_en": change_result.description_en,
    }


# =============================================================================
# Phenology Detection Endpoints
# =============================================================================


@app.get("/v1/phenology/{field_id}")
async def get_phenology(
    field_id: str,
    crop_type: str = Query(..., description="نوع المحصول (wheat, sorghum, tomato, etc.)"),
    lat: float = Query(..., ge=-90, le=90, description="Field latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Field longitude"),
    planting_date: str | None = Query(None, description="Planting date (YYYY-MM-DD)"),
    days: int = Query(default=60, ge=14, le=365, description="Days of historical data"),
    user: User = Depends(get_current_user),
):
    """
    Detect current crop growth stage from NDVI time series
    كشف مرحلة نمو المحصول الحالية من بيانات NDVI

    This endpoint:
    1. Retrieves NDVI time series for the field
    2. Detects phenological events (SOS, POS, EOS)
    3. Determines current growth stage (BBCH scale)
    4. Provides stage-specific recommendations
    """
    _validate_field_id(field_id)
    _validate_crop_type(crop_type)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="phenology")

    if not _phenology_detector:
        raise HTTPException(status_code=500, detail="Phenology detector not initialized")

    # Get NDVI time series
    timeseries_data = await _get_timeseries_data(field_id, days)
    ndvi_series = [{"date": point["date"], "value": point["ndvi"]} for point in timeseries_data["timeseries"]]

    # Parse planting date
    planting_dt = None
    if planting_date:
        try:
            planting_dt = datetime.fromisoformat(planting_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid planting_date format. Use YYYY-MM-DD")
        _validate_planting_date_not_future(planting_dt)

    # Detect phenology
    try:
        result = _phenology_detector.detect_current_stage(
            field_id=field_id,
            crop_type=crop_type,
            ndvi_series=ndvi_series,
            planting_date=planting_dt,
        )
    except ValueError as e:
        logger.error("phenology_detection_failed", error=str(e), field_id=field_id, crop_type=crop_type)
        raise HTTPException(status_code=400, detail="Invalid phenology detection parameters") from e

    return {
        "field_id": result.field_id,
        "crop_type": result.crop_type,
        "current_stage": {
            "id": result.current_stage.value,
            "name_ar": result.current_stage.label_ar,
            "name_en": result.current_stage.label_en,
            "days_in_stage": result.days_in_stage,
            "stage_start_date": (result.stage_start_date.isoformat() if result.stage_start_date else None),
        },
        "next_stage": {
            "id": result.expected_next_stage.value,
            "name_ar": result.expected_next_stage.label_ar,
            "name_en": result.expected_next_stage.label_en,
            "days_to_next_stage": result.days_to_next_stage,
        },
        "season_progress": {
            "percent": result.season_progress_percent,
            "sos_date": result.sos_date.isoformat() if result.sos_date else None,
            "pos_date": result.pos_date.isoformat() if result.pos_date else None,
            "eos_date": result.eos_date.isoformat() if result.eos_date else None,
            "estimated_harvest_date": (
                result.estimated_harvest_date.isoformat() if result.estimated_harvest_date else None
            ),
        },
        "ndvi_at_detection": result.ndvi_at_detection,
        "confidence": result.confidence,
        "recommendations_ar": result.recommendations_ar,
        "recommendations_en": result.recommendations_en,
        "data_source": "satellite-ndvi-timeseries",
    }


@app.get("/v1/phenology/{field_id}/timeline")
async def get_phenology_timeline(
    field_id: str,
    crop_type: str = Query(..., description="نوع المحصول"),
    planting_date: str = Query(..., description="Planting date (YYYY-MM-DD)"),
    user: User = Depends(get_current_user),
):
    """
    Get expected phenology timeline for crop planning
    الحصول على الجدول الزمني المتوقع لمراحل نمو المحصول

    Returns expected dates for all growth stages based on planting date.
    Useful for planning irrigation, fertilization, and harvest.
    """
    _validate_field_id(field_id)
    _validate_crop_type(crop_type)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="phenology_timeline")

    if not _phenology_detector:
        raise HTTPException(status_code=500, detail="Phenology detector not initialized")

    # Parse planting date
    try:
        planting_dt = datetime.fromisoformat(planting_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid planting_date format. Use YYYY-MM-DD")
    _validate_planting_date_not_future(planting_dt)

    # Generate timeline
    try:
        timeline = _phenology_detector.get_phenology_timeline(
            field_id=field_id, crop_type=crop_type, planting_date=planting_dt
        )
    except ValueError as e:
        logger.error("phenology_timeline_failed", error=str(e), field_id=field_id, crop_type=crop_type)
        raise HTTPException(status_code=400, detail="Invalid phenology timeline parameters") from e

    return {
        "field_id": timeline.field_id,
        "crop_type": timeline.crop_type,
        "planting_date": timeline.planting_date.isoformat(),
        "harvest_estimate": timeline.harvest_estimate.isoformat(),
        "season_length_days": timeline.season_length_days,
        "stages": timeline.stages,
        "critical_periods": timeline.critical_periods,
    }


@app.get("/v1/phenology/recommendations/{crop_type}/{stage}")
async def get_stage_recommendations(crop_type: str, stage: str):
    """
    Get recommendations for a specific crop and growth stage
    الحصول على توصيات لمحصول ومرحلة نمو محددة

    Example: /v1/phenology/recommendations/wheat/flowering
    """
    _validate_crop_type(crop_type)

    if not _phenology_detector:
        raise HTTPException(status_code=500, detail="Phenology detector not initialized")

    # Validate crop type
    crop_type = crop_type.lower()
    if crop_type not in _phenology_detector.YEMEN_CROP_SEASONS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown crop type: {crop_type}. Use /v1/phenology/crops to see supported crops.",
        )

    # Parse stage
    try:
        growth_stage = GrowthStage(stage.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage: {stage}. Valid stages: {[s.value for s in GrowthStage]}",
        )

    crop_params = _phenology_detector.YEMEN_CROP_SEASONS[crop_type]

    # Get recommendations
    recommendations_ar, recommendations_en = _phenology_detector._get_stage_recommendations(
        crop_type=crop_type,
        stage=growth_stage,
        days_to_next=7,  # Default estimate
        current_ndvi=0.5,  # Default
        crop_params=crop_params,
    )

    return {
        "crop_type": crop_type,
        "crop_name_ar": crop_params["name_ar"],
        "stage": {
            "id": growth_stage.value,
            "name_ar": growth_stage.label_ar,
            "name_en": growth_stage.label_en,
        },
        "recommendations_ar": recommendations_ar,
        "recommendations_en": recommendations_en,
    }


@app.get("/v1/phenology/crops")
async def list_supported_crops():
    """
    List all supported crops for phenology detection
    قائمة جميع المحاصيل المدعومة لكشف مراحل النمو
    """
    if not _phenology_detector:
        raise HTTPException(status_code=500, detail="Phenology detector not initialized")

    return {
        "crops": _phenology_detector.get_supported_crops(),
        "total": len(_phenology_detector.YEMEN_CROP_SEASONS),
    }


class PhenologyActionRequest(BaseModel):
    """Request for phenology detection with ActionTemplate output"""

    field_id: str = Field(..., description="معرف الحقل")
    farmer_id: str | None = Field(None, description="معرف المزارع")
    tenant_id: str | None = Field(None, description="معرف المستأجر")
    crop_type: str = Field(..., description="نوع المحصول")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    planting_date: str | None = Field(None, description="تاريخ الزراعة")
    days: int = Field(default=60, ge=14, le=365)
    publish_event: bool = Field(default=True, description="نشر الحدث عبر NATS")


@app.post("/v1/phenology/{field_id}/analyze-with-action")
async def analyze_phenology_with_action(
    request: PhenologyActionRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    Detect phenology stage and generate ActionTemplate
    كشف مرحلة النمو وإنشاء قالب إجراء

    This endpoint:
    1. Detects current growth stage
    2. Creates stage-specific ActionTemplate for mobile app
    3. Publishes event via NATS if enabled
    """
    _validate_field_id(request.field_id)
    _validate_crop_type(request.crop_type)

    # Enforce tenant isolation
    if request.tenant_id:
        _enforce_tenant(user, request.tenant_id)

    if not _phenology_detector:
        raise HTTPException(status_code=500, detail="Phenology detector not initialized")

    # Get NDVI time series
    timeseries_data = await _get_timeseries_data(request.field_id, request.days)
    ndvi_series = [{"date": point["date"], "value": point["ndvi"]} for point in timeseries_data["timeseries"]]

    # Parse planting date
    planting_dt = None
    if request.planting_date:
        try:
            planting_dt = datetime.fromisoformat(request.planting_date).date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid planting_date format")
        _validate_planting_date_not_future(planting_dt)

    # Detect phenology
    try:
        result = _phenology_detector.detect_current_stage(
            field_id=request.field_id,
            crop_type=request.crop_type,
            ndvi_series=ndvi_series,
            planting_date=planting_dt,
        )
    except ValueError as e:
        logger.error(
            "phenology_action_detection_failed", error=str(e), field_id=request.field_id, crop_type=request.crop_type
        )
        raise HTTPException(status_code=400, detail="Invalid phenology detection parameters") from e

    # Create ActionTemplate based on growth stage
    action_template = _create_phenology_action_template(
        result=result,
        farmer_id=request.farmer_id,
        tenant_id=request.tenant_id,
    )

    # Publish event to NATS (in background)
    if request.publish_event and _nats_available and publish_analysis_completed_sync:
        try:
            publish_analysis_completed_sync(
                event_type="phenology.stage_detected",
                source_service="satellite-service",
                field_id=request.field_id,
                data={
                    "crop_type": result.crop_type,
                    "current_stage": result.current_stage.value,
                    "stage_ar": result.current_stage.label_ar,
                    "stage_en": result.current_stage.label_en,
                    "days_in_stage": result.days_in_stage,
                    "season_progress_percent": result.season_progress_percent,
                    "confidence": result.confidence,
                },
                action_template=action_template,
                priority=action_template.get("urgency", "medium"),
                farmer_id=request.farmer_id,
                tenant_id=request.tenant_id,
            )
            logger.info(f"NATS: Published phenology event for field {request.field_id}")
        except Exception as e:
            logger.error(f"Failed to publish NATS event: {e}")

    # Create task card for mobile app
    task_card = {
        "id": action_template["action_id"],
        "type": action_template["action_type"],
        "title_ar": action_template["title_ar"],
        "title_en": action_template["title_en"],
        "urgency": {
            "level": action_template["urgency"],
            "color": {
                "low": "#22C55E",
                "medium": "#EAB308",
                "high": "#F97316",
                "critical": "#EF4444",
            }.get(action_template["urgency"], "#6B7280"),
        },
        "field_id": request.field_id,
        "confidence_percent": int(action_template["confidence"] * 100),
        "offline_ready": action_template["offline_executable"],
        "crop_type": result.crop_type,
        "current_stage": result.current_stage.label_ar,
        "season_progress": result.season_progress_percent,
    }

    return {
        "phenology": {
            "field_id": result.field_id,
            "crop_type": result.crop_type,
            "current_stage": {
                "id": result.current_stage.value,
                "name_ar": result.current_stage.label_ar,
                "name_en": result.current_stage.label_en,
            },
            "days_in_stage": result.days_in_stage,
            "season_progress_percent": result.season_progress_percent,
            "confidence": result.confidence,
            "recommendations_ar": result.recommendations_ar,
            "recommendations_en": result.recommendations_en,
        },
        "action_template": action_template,
        "task_card": task_card,
        "nats_published": request.publish_event and _nats_available,
    }


def _create_phenology_action_template(
    result: PhenologyResult,
    farmer_id: str | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """Create an ActionTemplate from phenology detection"""

    stage = result.current_stage
    crop_params = _phenology_detector.YEMEN_CROP_SEASONS[result.crop_type]

    # Determine urgency based on stage and critical periods
    is_critical = any(cp["stage"] == stage.value for cp in crop_params.get("critical_periods", []))

    if is_critical:
        urgency = "high"
    elif stage in [GrowthStage.FLOWERING, GrowthStage.FRUIT_DEVELOPMENT]:
        urgency = "medium"
    elif stage == GrowthStage.RIPENING and result.days_to_next_stage <= 7:
        urgency = "high"
    else:
        urgency = "low"

    # Determine action type based on stage
    if stage in [GrowthStage.BARE_SOIL, GrowthStage.GERMINATION]:
        action_type = "planting"
        title_ar = f"تحضير للزراعة - {crop_params['name_ar']}"
        title_en = f"Prepare for Planting - {result.crop_type}"
    elif stage in [GrowthStage.LEAF_DEVELOPMENT, GrowthStage.TILLERING]:
        action_type = "fertilization"
        title_ar = f"تسميد - مرحلة {stage.label_ar}"
        title_en = f"Fertilization - {stage.label_en} Stage"
    elif stage == GrowthStage.FLOWERING:
        action_type = "monitoring"
        title_ar = "مراقبة دقيقة - مرحلة الإزهار الحرجة"
        title_en = "Close Monitoring - Critical Flowering Stage"
    elif stage == GrowthStage.RIPENING:
        action_type = "harvest_prep"
        title_ar = f"تحضير للحصاد - {result.days_to_next_stage} يوم متبقي"
        title_en = f"Prepare for Harvest - {result.days_to_next_stage} days remaining"
    elif stage == GrowthStage.SENESCENCE:
        action_type = "harvest"
        title_ar = f"حصاد - {crop_params['name_ar']}"
        title_en = f"Harvest - {result.crop_type}"
    else:
        action_type = "monitoring"
        title_ar = f"مراقبة الحقل - {stage.label_ar}"
        title_en = f"Field Monitoring - {stage.label_en}"

    return {
        "action_id": str(uuid.uuid4()),
        "action_type": action_type,
        "title_ar": title_ar,
        "title_en": title_en,
        "description_ar": " | ".join(result.recommendations_ar),
        "description_en": " | ".join(result.recommendations_en),
        "summary_ar": f"المحصول في مرحلة {stage.label_ar} - تقدم الموسم: {result.season_progress_percent:.0f}%",
        "source_service": "satellite-service",
        "source_analysis_type": "phenology_detection",
        "confidence": result.confidence,
        "urgency": urgency,
        "field_id": result.field_id,
        "farmer_id": farmer_id,
        "tenant_id": tenant_id,
        "offline_executable": True,
        "fallback_instructions_ar": "في حال عدم توفر البيانات، قم بفحص المحصول بصرياً وتقييم مرحلة النمو حسب الخبرة",
        "fallback_instructions_en": "If data unavailable, visually inspect crop and assess growth stage based on experience",
        "estimated_duration_minutes": 45,
        "data": {
            "crop_type": result.crop_type,
            "current_stage": stage.value,
            "stage_ar": stage.label_ar,
            "stage_en": stage.label_en,
            "days_in_stage": result.days_in_stage,
            "days_to_next_stage": result.days_to_next_stage,
            "season_progress_percent": result.season_progress_percent,
            "ndvi_at_detection": result.ndvi_at_detection,
            "sos_date": result.sos_date.isoformat() if result.sos_date else None,
            "pos_date": result.pos_date.isoformat() if result.pos_date else None,
            "eos_date": result.eos_date.isoformat() if result.eos_date else None,
            "estimated_harvest_date": (
                result.estimated_harvest_date.isoformat() if result.estimated_harvest_date else None
            ),
        },
        "created_at": datetime.now(UTC).isoformat(),
    }


# =============================================================================
# SAR / Soil Moisture Endpoints
# =============================================================================


@app.get("/v1/soil-moisture/{field_id}")
async def get_soil_moisture(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Field latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Field longitude"),
    date: str | None = Query(None, description="Target date (YYYY-MM-DD), defaults to today"),
    user: User = Depends(get_current_user),
):
    """
    تقدير رطوبة التربة من بيانات SAR سنتينل-1
    Estimate soil moisture from Sentinel-1 SAR backscatter

    Uses VV and VH polarization data to estimate:
    - Soil moisture percentage (0-100%)
    - Volumetric water content (m³/m³)
    - Confidence level

    Works in all weather conditions (cloud-independent).
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="soil_moisture")

    if not _sar_processor:
        raise HTTPException(status_code=503, detail="SAR Processor not available")

    # Parse date if provided
    target_date = None
    if date:
        try:
            target_date = datetime.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get soil moisture estimate
    result = await _sar_processor.get_soil_moisture(
        latitude=lat,
        longitude=lon,
        field_id=field_id,
        date=target_date,
    )

    # Get interpretation
    interpretation = _sar_processor.get_moisture_interpretation(result.soil_moisture_percent)

    return {
        "field_id": result.field_id,
        "timestamp": result.timestamp.isoformat(),
        "soil_moisture": {
            "percent": result.soil_moisture_percent,
            "volumetric_water_content": result.volumetric_water_content,
            "status": interpretation["status"],
            "status_ar": interpretation["status_ar"],
        },
        "sar_data": {
            "vv_backscatter_db": result.vv_backscatter,
            "vh_backscatter_db": result.vh_backscatter,
            "incidence_angle_deg": result.incidence_angle,
            "data_source": result.data_source,
        },
        "confidence": result.confidence,
        "recommendation_ar": interpretation["recommendation_ar"],
        "recommendation_en": interpretation["recommendation_en"],
    }


@app.get("/v1/irrigation-events/{field_id}")
async def get_irrigation_events(
    field_id: str,
    days: int = Query(default=30, ge=7, le=90, description="Days to look back"),
    user: User = Depends(get_current_user),
):
    """
    كشف أحداث الري من تغيرات رطوبة التربة
    Detect irrigation events from soil moisture changes

    Analyzes SAR time series to identify:
    - Sudden moisture increases (irrigation/rainfall)
    - Estimated water application depth
    - Event confidence level

    Useful for:
    - Irrigation scheduling verification
    - Water use monitoring
    - Rainfall vs irrigation discrimination
    """
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="irrigation_events")
    _validate_field_id(field_id)

    if not _sar_processor:
        raise HTTPException(status_code=503, detail="SAR Processor not available")

    # Detect irrigation events
    events = await _sar_processor.detect_irrigation_event(
        field_id=field_id,
        days_back=days,
    )

    # Format response
    events_list = []
    for event in events:
        events_list.append(
            {
                "detected_date": event.detected_date.isoformat(),
                "moisture_change": {
                    "before_percent": event.moisture_before,
                    "after_percent": event.moisture_after,
                    "increase_percent": round(event.moisture_after - event.moisture_before, 2),
                },
                "estimated_water_mm": event.estimated_water_mm,
                "confidence": event.confidence,
                "detection_method": event.detection_method,
            }
        )

    # Sort by date (most recent first)
    events_list.sort(key=lambda x: x["detected_date"], reverse=True)

    return {
        "field_id": field_id,
        "period_days": days,
        "events_detected": len(events_list),
        "events": events_list,
        "summary": {
            "total_water_applied_mm": round(sum(e["estimated_water_mm"] for e in events_list), 1),
            "average_application_mm": (
                round(
                    sum(e["estimated_water_mm"] for e in events_list) / len(events_list),
                    1,
                )
                if events_list
                else 0
            ),
        },
    }


@app.get("/v1/sar-timeseries/{field_id}")
async def get_sar_timeseries(
    field_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    lat: float | None = Query(None, ge=-90, le=90, description="Field latitude"),
    lon: float | None = Query(None, ge=-180, le=180, description="Field longitude"),
    user: User = Depends(get_current_user),
):
    """
    سلسلة زمنية لبيانات SAR ورطوبة التربة
    Time series of SAR backscatter and soil moisture

    Returns:
    - SAR backscatter values (VV, VH)
    - Derived soil moisture
    - Orbit direction (ascending/descending)
    - Incidence angle

    Sentinel-1 revisit: every 6 days
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="sar_timeseries")

    if not _sar_processor:
        raise HTTPException(status_code=503, detail="SAR Processor not available")

    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    if (end_dt - start_dt).days > 365:
        raise HTTPException(status_code=400, detail="Maximum time range is 365 days")

    # Get SAR time series
    timeseries = await _sar_processor.get_sar_timeseries(
        field_id=field_id,
        start_date=start_dt,
        end_date=end_dt,
        latitude=lat,
        longitude=lon,
    )

    # Format response
    data_points = []
    for point in timeseries:
        data_points.append(
            {
                "acquisition_date": point.acquisition_date.isoformat(),
                "scene_id": point.scene_id,
                "orbit_direction": point.orbit_direction,
                "backscatter": {
                    "vv_db": point.vv_backscatter,
                    "vh_db": point.vh_backscatter,
                    "vv_vh_ratio": point.vv_vh_ratio,
                },
                "incidence_angle_deg": point.incidence_angle,
                "soil_moisture_percent": point.soil_moisture_percent,
            }
        )

    # Calculate statistics
    if data_points:
        moisture_values = [p["soil_moisture_percent"] for p in data_points]
        avg_moisture = sum(moisture_values) / len(moisture_values)
        min_moisture = min(moisture_values)
        max_moisture = max(moisture_values)
        moisture_trend = "increasing" if moisture_values[-1] > moisture_values[0] else "decreasing"
    else:
        avg_moisture = min_moisture = max_moisture = 0
        moisture_trend = "stable"

    return {
        "field_id": field_id,
        "start_date": start_date,
        "end_date": end_date,
        "data_points_count": len(data_points),
        "timeseries": data_points,
        "statistics": {
            "average_moisture_percent": round(avg_moisture, 2),
            "min_moisture_percent": round(min_moisture, 2),
            "max_moisture_percent": round(max_moisture, 2),
            "moisture_range_percent": round(max_moisture - min_moisture, 2),
            "trend": moisture_trend,
        },
    }


# =============================================================================
# Advanced Vegetation Indices Endpoints
# =============================================================================


@app.get("/v1/indices/{field_id}")
async def get_all_indices(
    field_id: str,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
    user: User = Depends(get_current_user),
):
    """
    Get all vegetation indices for a field location
    الحصول على جميع المؤشرات النباتية لموقع الحقل

    Returns 18+ vegetation indices including:
    - Basic: NDVI, NDWI, EVI, SAVI, LAI, NDMI
    - Chlorophyll: NDRE, CVI, MCARI, TCARI, SIPI
    - Early Stress: GNDVI, VARI, GLI, GRVI
    - Corrected: MSAVI, OSAVI, ARVI
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="indices")

    if not _indices_available:
        raise HTTPException(status_code=503, detail="Advanced indices module not available")

    import random

    # Generate realistic Sentinel-2 band data
    # In production, this would come from actual satellite imagery
    bands = BandData(
        B02_blue=random.uniform(0.02, 0.08),
        B03_green=random.uniform(0.03, 0.12),
        B04_red=random.uniform(0.02, 0.15),
        B05_red_edge1=random.uniform(0.05, 0.20),
        B06_red_edge2=random.uniform(0.08, 0.25),
        B07_red_edge3=random.uniform(0.10, 0.30),
        B08_nir=random.uniform(0.15, 0.55),
        B8A_nir_narrow=random.uniform(0.15, 0.50),
        B11_swir1=random.uniform(0.08, 0.35),
        B12_swir2=random.uniform(0.05, 0.25),
    )

    # Calculate all indices
    calculator = VegetationIndicesCalculator()
    all_indices = calculator.calculate_all(bands)

    return {
        "field_id": field_id,
        "location": {"latitude": lat, "longitude": lon},
        "satellite": satellite.value,
        "acquisition_date": datetime.now(UTC).isoformat(),
        "indices": all_indices.to_dict(),
        "data_source": "simulated",
        "note": "Advanced indices calculated from Sentinel-2 bands. Configure real data provider for actual satellite imagery.",
    }


@app.get("/v1/indices/{field_id}/{index_name}")
async def get_specific_index(
    field_id: str,
    index_name: str,
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    crop_type: str | None = Query(default="unknown", description="نوع المحصول"),
    growth_stage: str | None = Query(default="vegetative", description="مرحلة النمو"),
    satellite: SatelliteSource = SatelliteSource.SENTINEL2,
    user: User = Depends(get_current_user),
):
    """
    Get a specific vegetation index with interpretation
    الحصول على مؤشر نباتي محدد مع التفسير

    Parameters:
    - index_name: ndvi, ndre, gndvi, mcari, etc.
    - crop_type: wheat, sorghum, coffee, qat, etc.
    - growth_stage: emergence, vegetative, reproductive, maturation
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="specific_index")

    if not _indices_available:
        raise HTTPException(status_code=503, detail="Advanced indices module not available")

    # Validate index name
    try:
        VegetationIndex(index_name.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown index '{index_name}'. Valid indices: {[i.value for i in VegetationIndex]}",
        )

    # Validate crop type and growth stage
    try:
        crop_enum = CropType(crop_type.lower())
    except ValueError:
        crop_enum = CropType.UNKNOWN

    try:
        stage_enum = VegGrowthStage(growth_stage.lower())
    except ValueError:
        stage_enum = VegGrowthStage.VEGETATIVE

    # Get all indices first
    all_indices_response = await get_all_indices(field_id, lat, lon, satellite)
    indices_dict = all_indices_response["indices"]

    # Get the requested index value
    if index_name.lower() not in indices_dict:
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    index_value = indices_dict[index_name.lower()]

    # Interpret the index
    interpreter = IndexInterpreter()
    interpretation = interpreter.interpret_index(
        index_name=index_name.lower(),
        value=index_value,
        crop_type=crop_enum,
        growth_stage=stage_enum,
    )

    # Get recommended indices for this growth stage
    recommended = interpreter.get_recommended_indices(stage_enum)

    return {
        "field_id": field_id,
        "location": {"latitude": lat, "longitude": lon},
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "index": {
            "name": interpretation.index_name,
            "value": interpretation.value,
            "status": interpretation.status.value,
            "description_ar": interpretation.description_ar,
            "description_en": interpretation.description_en,
            "confidence": interpretation.confidence,
            "thresholds": interpretation.threshold_info,
        },
        "recommended_indices_for_stage": recommended,
        "acquisition_date": all_indices_response["acquisition_date"],
        "satellite": satellite.value,
    }


@app.post("/v1/indices/interpret")
async def interpret_indices(request: InterpretRequest, user: User = Depends(get_current_user)):
    """
    Interpret multiple vegetation indices for a specific crop and growth stage
    تفسير عدة مؤشرات نباتية حسب نوع المحصول ومرحلة النمو

    Body:
    {
        "field_id": "field123",
        "indices": {"ndvi": 0.65, "ndre": 0.28, "gndvi": 0.55},
        "crop_type": "wheat",
        "growth_stage": "reproductive"
    }
    """
    if not _indices_available:
        raise HTTPException(status_code=503, detail="Advanced indices module not available")

    # Validate crop type and growth stage
    try:
        crop_enum = CropType(request.crop_type.lower())
    except ValueError:
        crop_enum = CropType.UNKNOWN

    try:
        stage_enum = VegGrowthStage(request.growth_stage.lower())
    except ValueError:
        stage_enum = VegGrowthStage.VEGETATIVE

    # Interpret each index
    interpreter = IndexInterpreter()
    interpretations = []

    for index_name, value in request.indices.items():
        try:
            interpretation = interpreter.interpret_index(
                index_name=index_name.lower(),
                value=value,
                crop_type=crop_enum,
                growth_stage=stage_enum,
            )
            interpretations.append(
                {
                    "name": interpretation.index_name,
                    "value": interpretation.value,
                    "status": interpretation.status.value,
                    "description_ar": interpretation.description_ar,
                    "description_en": interpretation.description_en,
                    "confidence": interpretation.confidence,
                    "thresholds": interpretation.threshold_info,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to interpret index {index_name}: {e}")
            continue

    # Determine overall health status
    status_weights = {
        HealthStatus.EXCELLENT: 5,
        HealthStatus.GOOD: 4,
        HealthStatus.FAIR: 3,
        HealthStatus.POOR: 2,
        HealthStatus.CRITICAL: 1,
    }

    if interpretations:
        avg_weight = sum(status_weights.get(HealthStatus(i["status"]), 3) for i in interpretations) / len(
            interpretations
        )
        if avg_weight >= 4.5:
            overall_status = "excellent"
            overall_ar = "ممتاز"
        elif avg_weight >= 3.5:
            overall_status = "good"
            overall_ar = "جيد"
        elif avg_weight >= 2.5:
            overall_status = "fair"
            overall_ar = "متوسط"
        elif avg_weight >= 1.5:
            overall_status = "poor"
            overall_ar = "ضعيف"
        else:
            overall_status = "critical"
            overall_ar = "حرج"
    else:
        overall_status = "unknown"
        overall_ar = "غير معروف"

    # Get recommended indices for this growth stage
    recommended = interpreter.get_recommended_indices(stage_enum)

    return {
        "field_id": request.field_id,
        "crop_type": request.crop_type,
        "growth_stage": request.growth_stage,
        "overall_status": overall_status,
        "overall_status_ar": overall_ar,
        "interpretations": interpretations,
        "recommended_indices_for_stage": recommended,
        "analysis_date": datetime.now(UTC).isoformat(),
    }


@app.get("/v1/indices/guide")
async def get_indices_guide():
    """
    Get usage guide for vegetation indices by growth stage
    الحصول على دليل استخدام المؤشرات النباتية حسب مراحل النمو
    """
    return {
        "guide": {
            "emergence": {
                "stage_ar": "البزوغ",
                "stage_en": "Emergence",
                "best_indices": ["GNDVI", "VARI", "GLI", "NDVI"],
                "description_ar": "في مرحلة البزوغ، ركز على الكشف المبكر عن الإجهاد",
                "description_en": "During emergence, focus on early stress detection",
            },
            "vegetative": {
                "stage_ar": "النمو الخضري",
                "stage_en": "Vegetative",
                "best_indices": ["NDVI", "LAI", "CVI", "GNDVI", "NDRE"],
                "description_ar": "في النمو الخضري، راقب كتلة النبات والنيتروجين",
                "description_en": "During vegetative growth, monitor biomass and nitrogen",
            },
            "reproductive": {
                "stage_ar": "الإزهار والإثمار",
                "stage_en": "Reproductive",
                "best_indices": ["NDRE", "MCARI", "NDVI", "NDWI", "LAI"],
                "description_ar": "في مرحلة التكاثر، راقب الكلوروفيل والماء",
                "description_en": "During reproduction, monitor chlorophyll and water",
            },
            "maturation": {
                "stage_ar": "النضج",
                "stage_en": "Maturation",
                "best_indices": ["NDVI", "NDMI", "NDWI", "EVI"],
                "description_ar": "في النضج، راقب رطوبة المحصول لتوقيت الحصاد",
                "description_en": "During maturation, monitor crop moisture for harvest timing",
            },
        },
        "indices_reference": {
            "ndvi": {
                "name": "Normalized Difference Vegetation Index",
                "name_ar": "مؤشر الفرق الطبيعي للنباتات",
                "range": "-1 to 1",
                "best_for": "Overall vegetation health and biomass",
                "best_for_ar": "الصحة العامة للنبات والكتلة الحيوية",
            },
            "ndre": {
                "name": "Normalized Difference Red Edge",
                "name_ar": "مؤشر الحافة الحمراء الطبيعية",
                "range": "-1 to 1",
                "best_for": "Chlorophyll content and nitrogen status",
                "best_for_ar": "محتوى الكلوروفيل وحالة النيتروجين",
            },
            "gndvi": {
                "name": "Green NDVI",
                "name_ar": "مؤشر NDVI الأخضر",
                "range": "-1 to 1",
                "best_for": "Early nitrogen stress detection",
                "best_for_ar": "الكشف المبكر عن نقص النيتروجين",
            },
            "ndwi": {
                "name": "Normalized Difference Water Index",
                "name_ar": "مؤشر الفرق الطبيعي للماء",
                "range": "-1 to 1",
                "best_for": "Water content and irrigation monitoring",
                "best_for_ar": "محتوى الماء ومراقبة الري",
            },
            "mcari": {
                "name": "Modified Chlorophyll Absorption Ratio",
                "name_ar": "نسبة امتصاص الكلوروفيل المعدلة",
                "range": "0 to 1.5",
                "best_for": "Chlorophyll concentration",
                "best_for_ar": "تركيز الكلوروفيل",
            },
        },
    }


# =============================================================================
# Yield Prediction Endpoints
# =============================================================================


class YieldPredictionRequest(BaseModel):
    """Request for crop yield prediction"""

    field_id: str = Field(..., description="معرف الحقل")
    crop_code: str = Field(..., description="رمز المحصول (WHEAT, TOMATO, etc.)")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    planting_date: date | None = Field(None, description="تاريخ الزراعة")
    field_area_ha: float = Field(default=1.0, ge=0.01, description="مساحة الحقل بالهكتار")

    # Optional: provide NDVI time series (if available)
    ndvi_series: list[float] | None = Field(
        None,
        description="سلسلة زمنية من قيم NDVI (اختياري - سيتم جلبها تلقائياً إذا لم تقدم)",
    )

    @field_validator("ndvi_series")
    @classmethod
    def validate_ndvi_range(cls, v: list[float] | None) -> list[float] | None:
        """Validate all NDVI values are within [-1.0, 1.0]."""
        if v is not None:
            for idx, val in enumerate(v):
                if not (-1.0 <= val <= 1.0):
                    raise ValueError(
                        f"ndvi_series[{idx}]={val} outside valid range [-1.0, 1.0] | "
                        f"قيمة NDVI في الموضع {idx} خارج النطاق الصالح"
                    )
        return v

    # Weather data (optional - will be estimated if not provided)
    precipitation_mm: float | None = Field(None, description="الأمطار الكلية (مم)")
    avg_temp_min: float | None = Field(None, description="متوسط درجة الحرارة الصغرى (°س)")
    avg_temp_max: float | None = Field(None, description="متوسط درجة الحرارة الكبرى (°س)")

    # Optional: soil moisture from SAR
    soil_moisture: float | None = Field(None, ge=0, le=1, description="رطوبة التربة (0-1)")


class YieldPredictionResponse(BaseModel):
    """Response for crop yield prediction"""

    field_id: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    predicted_yield_ton_ha: float
    predicted_yield_total_ton: float  # predicted_yield_ton_ha * field_area_ha
    yield_range_min: float
    yield_range_max: float
    confidence: float
    factors: dict[str, float]
    comparison_to_average: float
    comparison_to_base: float
    recommendations_ar: list[str]
    recommendations_en: list[str]
    prediction_date: str
    growth_stage: str
    days_to_harvest: int | None
    data_sources_used: list[str]


class YieldHistoryItem(BaseModel):
    """Historical yield prediction item"""

    prediction_id: str
    prediction_date: str
    crop_code: str
    crop_name_ar: str
    predicted_yield_ton_ha: float
    actual_yield_ton_ha: float | None
    confidence: float
    growth_stage: str


class RegionalYieldStats(BaseModel):
    """Regional yield statistics"""

    governorate: str
    governorate_ar: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    average_yield_ton_ha: float
    min_yield_ton_ha: float
    max_yield_ton_ha: float
    field_count: int
    data_source: str


# =============================================================================
# VRA (Variable Rate Application) Models
# =============================================================================


class VRARequest(BaseModel):
    """Request for VRA prescription map generation"""

    field_id: str = Field(..., description="معرف الحقل")
    latitude: float = Field(..., ge=-90, le=90, description="خط العرض")
    longitude: float = Field(..., ge=-180, le=180, description="خط الطول")
    vra_type: str = Field(..., description="نوع التطبيق (fertilizer, seed, lime, pesticide, irrigation)")
    target_rate: float = Field(..., gt=0, description="المعدل المستهدف")
    unit: str = Field(..., description="وحدة القياس (kg/ha, seeds/ha, L/ha, mm/ha)")
    num_zones: int = Field(default=3, ge=3, le=5, description="عدد مناطق الإدارة (3 أو 5)")
    zone_method: str = Field(default="ndvi", description="طريقة تصنيف المناطق")
    min_rate: float | None = Field(None, gt=0, description="الحد الأدنى للمعدل")
    max_rate: float | None = Field(None, gt=0, description="الحد الأقصى للمعدل")
    product_price_per_unit: float | None = Field(None, description="سعر الوحدة للمنتج")
    notes: str | None = Field(None, description="ملاحظات (إنجليزي)")
    notes_ar: str | None = Field(None, description="ملاحظات (عربي)")


class ManagementZoneResponse(BaseModel):
    """Management zone in prescription map"""

    zone_id: int
    zone_name: str
    zone_name_ar: str
    zone_level: str
    ndvi_min: float
    ndvi_max: float
    area_ha: float
    percentage: float
    centroid: list[float]  # [lon, lat]
    recommended_rate: float
    unit: str
    total_product: float
    color: str


class PrescriptionMapResponse(BaseModel):
    """VRA prescription map response"""

    id: str
    field_id: str
    vra_type: str
    created_at: str
    target_rate: float
    min_rate: float
    max_rate: float
    unit: str
    num_zones: int
    zone_method: str
    zones: list[ManagementZoneResponse]
    total_area_ha: float
    total_product_needed: float
    flat_rate_product: float
    savings_percent: float
    savings_amount: float
    cost_savings: float | None
    notes: str | None
    notes_ar: str | None
    geojson_url: str | None
    shapefile_url: str | None
    isoxml_url: str | None


# =============================================================================
# Change Detection Models
# =============================================================================


class ChangeEventResponse(BaseModel):
    """Response model for a single change event"""

    field_id: str
    change_type: str
    severity: str
    detected_date: str
    location: dict[str, float]
    ndvi_before: float
    ndvi_after: float
    ndvi_change: float
    change_percent: float
    confidence: float
    description_ar: str
    description_en: str
    recommended_action_ar: str
    recommended_action_en: str
    additional_metrics: dict[str, float] | None = None


class ChangeReportResponse(BaseModel):
    """Response model for comprehensive change detection report"""

    field_id: str
    analysis_period: dict[str, str]
    events: list[ChangeEventResponse]
    overall_trend: str
    ndvi_trend: float
    anomaly_count: int
    severity_summary: dict[str, int]
    change_type_summary: dict[str, int]
    summary_ar: str
    summary_en: str
    recommendations_ar: list[str]
    recommendations_en: list[str]


# =============================================================================
# Yield Prediction Endpoints
# =============================================================================


@app.post("/v1/yield-prediction", response_model=YieldPredictionResponse)
async def predict_yield(request: YieldPredictionRequest, user: User = Depends(get_current_user)):
    """
    التنبؤ بإنتاجية المحصول | Predict Crop Yield

    Uses ML-based ensemble model combining:
    - NDVI-based regression (40%)
    - Growing Degree Days model (30%)
    - Water balance model (20%)
    - Soil moisture model (10%)

    Returns predicted yield with confidence interval and actionable recommendations.
    """
    _validate_field_id(request.field_id)
    _validate_planting_date_not_future(request.planting_date)

    import random

    if not _yield_predictor:
        raise HTTPException(status_code=503, detail="Yield predictor not initialized")

    data_sources = []

    # Get NDVI time series if not provided
    if request.ndvi_series is None or len(request.ndvi_series) == 0:
        # Fetch from timeseries endpoint
        try:
            timeseries_data = await _get_timeseries_data(
                field_id=request.field_id,
                days=90,  # Last 3 months
                satellite=SatelliteSource.SENTINEL2,
            )
            request.ndvi_series = [point["ndvi"] for point in timeseries_data["timeseries"]]
            data_sources.append("sentinel-2_ndvi_timeseries")
        except Exception as e:
            logger.warning(f"Failed to fetch NDVI timeseries: {e}")
            # Generate realistic NDVI series based on crop growth
            request.ndvi_series = [
                max(0.2, min(0.8, 0.3 + (i / 10) * 0.5 + random.uniform(-0.05, 0.05))) for i in range(10)
            ]
            data_sources.append("simulated_ndvi")
    else:
        data_sources.append("user_provided_ndvi")

    # Prepare weather data
    if request.avg_temp_min is not None and request.avg_temp_max is not None:
        # Generate daily temperature series (assume 90 days)
        temp_min_series = [request.avg_temp_min + random.uniform(-3, 3) for _ in range(90)]
        temp_max_series = [request.avg_temp_max + random.uniform(-3, 3) for _ in range(90)]
        data_sources.append("user_provided_weather")
    else:
        # Use Yemen regional defaults based on location
        # Highland: cooler, Coastal: warmer
        if request.latitude > 14.5:  # Highland region
            temp_min_series = [15 + random.uniform(-2, 2) for _ in range(90)]
            temp_max_series = [28 + random.uniform(-3, 3) for _ in range(90)]
        else:  # Coastal/lowland
            temp_min_series = [22 + random.uniform(-2, 2) for _ in range(90)]
            temp_max_series = [35 + random.uniform(-3, 3) for _ in range(90)]
        data_sources.append("estimated_weather_from_location")

    # Precipitation
    precipitation = request.precipitation_mm or random.uniform(100, 400)
    if request.precipitation_mm:
        data_sources.append("user_provided_precipitation")
    else:
        data_sources.append("estimated_precipitation")

    # Get soil moisture from SAR if available
    soil_moisture = request.soil_moisture
    if soil_moisture is None and _sar_processor:
        try:
            # Try to fetch soil moisture from SAR processor
            sar_result = await _sar_processor.estimate_soil_moisture(
                field_id=request.field_id,
                latitude=request.latitude,
                longitude=request.longitude,
                start_date=date.today() - timedelta(days=30),
                end_date=date.today(),
            )
            if sar_result and sar_result.soil_moisture_timeseries:
                soil_moisture = sar_result.soil_moisture_timeseries[-1].soil_moisture_m3m3
                data_sources.append("sentinel-1_sar_soil_moisture")
        except Exception as e:
            logger.warning(f"Failed to fetch SAR soil moisture: {e}")

    if soil_moisture is None:
        soil_moisture = random.uniform(0.3, 0.5)  # Assume moderate moisture
        data_sources.append("estimated_soil_moisture")

    # Prepare weather data dict
    weather_data = {
        "temp_min_series": temp_min_series,
        "temp_max_series": temp_max_series,
        "precipitation_mm": precipitation,
        "et0_mm": precipitation * 1.2,  # Simple ET0 estimate
    }

    # Call yield predictor
    prediction = await _yield_predictor.predict_yield(
        field_id=request.field_id,
        crop_code=request.crop_code,
        ndvi_series=request.ndvi_series,
        weather_data=weather_data,
        soil_moisture=soil_moisture,
        planting_date=request.planting_date,
        field_area_ha=request.field_area_ha,
    )

    # Calculate total yield
    total_yield = prediction.predicted_yield_ton_ha * request.field_area_ha

    return YieldPredictionResponse(
        field_id=prediction.field_id,
        crop_code=prediction.crop_code,
        crop_name_ar=prediction.crop_name_ar,
        crop_name_en=prediction.crop_name_en,
        predicted_yield_ton_ha=prediction.predicted_yield_ton_ha,
        predicted_yield_total_ton=round(total_yield, 2),
        yield_range_min=prediction.yield_range_min,
        yield_range_max=prediction.yield_range_max,
        confidence=prediction.confidence,
        factors=prediction.factors,
        comparison_to_average=prediction.comparison_to_average,
        comparison_to_base=prediction.comparison_to_base,
        recommendations_ar=prediction.recommendations_ar,
        recommendations_en=prediction.recommendations_en,
        prediction_date=prediction.prediction_date.isoformat(),
        growth_stage=prediction.growth_stage,
        days_to_harvest=prediction.days_to_harvest,
        data_sources_used=data_sources,
    )


@app.get("/v1/yield-history/{field_id}")
async def get_yield_history(
    field_id: str,
    seasons: int = Query(default=5, ge=1, le=20, description="Number of past seasons to retrieve"),
    crop_code: str | None = Query(None, description="Filter by crop code"),
    user: User = Depends(get_current_user),
):
    """
    الحصول على سجل التنبؤات السابقة | Get Yield Prediction History

    Returns historical yield predictions for a field, optionally filtered by crop.
    In production, this would fetch from a database. Currently returns simulated data.
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="yield_history")

    import random

    # Import shared crop catalog
    try:
        # Add project root to path for shared imports (dynamic path instead of hardcoded)
        _proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        if _proj_root not in sys.path:
            sys.path.insert(0, _proj_root)
        from apps.services.shared.crops import ALL_CROPS

        # Get crops for this region (simulated)
        if crop_code:
            crop_codes = [crop_code] if crop_code in ALL_CROPS else ["WHEAT"]
        else:
            # Random selection of common Yemen crops
            crop_codes = random.sample(
                ["WHEAT", "SORGHUM", "TOMATO", "POTATO", "ONION", "CORN"],
                k=min(seasons, 3),
            )
    except (ValueError, KeyError, IndexError) as e:
        logger.warning(f"Error selecting crop codes: {e}")
        crop_codes = ["WHEAT", "TOMATO", "POTATO"]

    # Generate historical predictions
    history = []
    for i in range(seasons):
        crop_code_selected = crop_code if crop_code else random.choice(crop_codes)

        try:
            from apps.services.shared.crops import get_crop

            crop_info = get_crop(crop_code_selected)
            crop_name_ar = crop_info.name_ar if crop_info else crop_code_selected
            base_yield = crop_info.base_yield_ton_ha if crop_info else 2.0
        except (ImportError, AttributeError, KeyError) as e:
            logger.debug(f"Could not get crop info for {crop_code_selected}: {e}")
            crop_name_ar = crop_code_selected
            base_yield = 2.0

        # Historical prediction (months ago)
        prediction_date = datetime.now(UTC) - timedelta(days=120 * i)

        # Simulated prediction and actual yield
        predicted = round(base_yield * random.uniform(0.7, 1.3), 2)

        # Actual yield (if harvest completed)
        if i > 0:  # Past seasons have actual yields
            actual = round(predicted * random.uniform(0.85, 1.15), 2)
        else:  # Current season - no actual yet
            actual = None

        history.append(
            YieldHistoryItem(
                prediction_id=str(uuid.uuid4()),
                prediction_date=prediction_date.isoformat(),
                crop_code=crop_code_selected,
                crop_name_ar=crop_name_ar,
                predicted_yield_ton_ha=predicted,
                actual_yield_ton_ha=actual,
                confidence=random.uniform(0.7, 0.95),
                growth_stage="harvest_completed" if actual else "ripening",
            )
        )

    return {
        "field_id": field_id,
        "seasons": seasons,
        "crop_filter": crop_code,
        "history": history,
        "summary": {
            "total_predictions": len(history),
            "completed_harvests": len([h for h in history if h.actual_yield_ton_ha]),
            "average_predicted_yield": (
                round(sum(h.predicted_yield_ton_ha for h in history) / len(history), 2) if history else 0
            ),
            "average_actual_yield": (
                round(
                    sum(h.actual_yield_ton_ha for h in history if h.actual_yield_ton_ha)
                    / len([h for h in history if h.actual_yield_ton_ha]),
                    2,
                )
                if any(h.actual_yield_ton_ha for h in history)
                else None
            ),
        },
    }


@app.get("/v1/regional-yields/{governorate}")
async def get_regional_yields(
    governorate: str,
    crop: str | None = Query(None, description="Filter by crop code (e.g., 'WHEAT', 'TOMATO')"),
):
    """
    الحصول على إحصائيات الإنتاجية الإقليمية | Get Regional Yield Statistics

    Returns average yields for a specific governorate in Yemen.
    In production, this would aggregate data from multiple fields.
    """
    import random

    # Validate governorate
    if governorate.lower() not in YEMEN_REGIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Governorate '{governorate}' not found. Available: {', '.join(YEMEN_REGIONS.keys())}",
        )

    gov_info = YEMEN_REGIONS[governorate.lower()]
    gov_name_ar = gov_info["name_ar"]
    region_type = gov_info["region"]

    # Import crop catalog
    try:
        # Add project root to path for shared imports (dynamic path instead of hardcoded)
        _proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        if _proj_root not in sys.path:
            sys.path.insert(0, _proj_root)
        from apps.services.shared.crops import ALL_CROPS

        # Get crops suitable for this region
        if crop:
            crops_to_show = [ALL_CROPS[crop]] if crop in ALL_CROPS else []
        else:
            # Get common crops for this region type
            if region_type == "highland":
                crop_codes = [
                    "WHEAT",
                    "BARLEY",
                    "POTATO",
                    "TOMATO",
                    "FABA_BEAN",
                    "COFFEE",
                ]
            elif region_type == "coastal":
                crop_codes = [
                    "SORGHUM",
                    "MILLET",
                    "BANANA",
                    "MANGO",
                    "SESAME",
                    "COTTON",
                ]
            else:  # desert
                crop_codes = ["DATE_PALM", "WHEAT", "BARLEY", "ALFALFA"]

            crops_to_show = [ALL_CROPS[c] for c in crop_codes if c in ALL_CROPS]
    except Exception as e:
        logger.warning(f"Failed to load crop catalog: {e}")
        crops_to_show = []

    if not crops_to_show:
        raise HTTPException(status_code=404, detail=f"No crop data available for {governorate}")

    # Generate regional statistics
    regional_stats = []
    for crop_info in crops_to_show:
        # Simulate regional variation (±20% from base yield)
        base_yield = crop_info.base_yield_ton_ha
        avg_yield = base_yield * random.uniform(0.8, 1.2)
        min_yield = avg_yield * 0.6
        max_yield = avg_yield * 1.4
        field_count = random.randint(50, 500)

        regional_stats.append(
            RegionalYieldStats(
                governorate=governorate.lower(),
                governorate_ar=gov_name_ar,
                crop_code=crop_info.code,
                crop_name_ar=crop_info.name_ar,
                crop_name_en=crop_info.name_en,
                average_yield_ton_ha=round(avg_yield, 2),
                min_yield_ton_ha=round(min_yield, 2),
                max_yield_ton_ha=round(max_yield, 2),
                field_count=field_count,
                data_source="simulated_regional_data",
            )
        )

    return {
        "governorate": governorate.lower(),
        "governorate_ar": gov_name_ar,
        "region_type": region_type,
        "crop_filter": crop,
        "statistics": regional_stats,
        "summary": {
            "total_crops": len(regional_stats),
            "total_fields": sum(s.field_count for s in regional_stats),
            "highest_yield_crop": (
                max(regional_stats, key=lambda x: x.average_yield_ton_ha).crop_name_en if regional_stats else None
            ),
        },
        "note": "Production system would aggregate real field data. Currently showing simulated regional averages.",
    }


# =============================================================================
# Cloud Masking Endpoints
# =============================================================================


@app.get("/v1/cloud-cover/{field_id}")
async def get_cloud_cover(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Field latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Field longitude"),
    date: str | None = Query(None, description="Target date (YYYY-MM-DD), defaults to today"),
    user: User = Depends(get_current_user),
):
    """
    Analyze cloud cover for a field location using Sentinel-2 SCL
    تحليل الغطاء السحابي لموقع الحقل

    Returns detailed cloud coverage analysis including:
    - Cloud coverage percentage
    - Shadow coverage percentage
    - Clear pixel percentage
    - Quality score (0-1)
    - Usability assessment
    - SCL class distribution
    - Recommendation

    Example:
        GET /v1/cloud-cover/field_123?lat=15.5&lon=44.2&date=2024-01-15
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="cloud_cover")

    if not _cloud_masker:
        raise HTTPException(status_code=503, detail="Cloud masker not initialized")

    try:
        # Parse date if provided
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Analyze cloud cover
        result = await _cloud_masker.analyze_cloud_cover(
            field_id=field_id, latitude=lat, longitude=lon, date=target_date
        )

        return {
            "success": True,
            "field_id": field_id,
            "location": {"latitude": lat, "longitude": lon},
            "analysis": result.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Cloud cover analysis failed for {field_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/v1/clear-observations/{field_id}")
async def find_clear_observations(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Field latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Field longitude"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    max_cloud: float = Query(20.0, ge=0, le=100, description="Maximum cloud cover %"),
    user: User = Depends(get_current_user),
):
    """
    Find all clear (low cloud) observations in date range
    البحث عن جميع الأرصاد الصافية في فترة زمنية

    Returns list of clear observations sorted by quality score.
    Useful for selecting best images for analysis.

    Example:
        GET /v1/clear-observations/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31&max_cloud=15
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="clear_observations")

    if not _cloud_masker:
        raise HTTPException(status_code=503, detail="Cloud masker not initialized")

    try:
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Validate date range
        if end_dt < start_dt:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        # Find clear observations
        observations = await _cloud_masker.find_clear_observations(
            field_id=field_id,
            latitude=lat,
            longitude=lon,
            start_date=start_dt,
            end_date=end_dt,
            max_cloud_cover=max_cloud,
        )

        return {
            "success": True,
            "field_id": field_id,
            "location": {"latitude": lat, "longitude": lon},
            "date_range": {"start": start_date, "end": end_date},
            "max_cloud_threshold": max_cloud,
            "observation_count": len(observations),
            "observations": [obs.to_dict() for obs in observations],
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear observations search failed for {field_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.get("/v1/best-observation/{field_id}")
async def get_best_observation(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Field latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Field longitude"),
    target_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    tolerance_days: int = Query(15, ge=1, le=90, description="Days before/after to search"),
    user: User = Depends(get_current_user),
):
    """
    Find the best (lowest cloud) observation near target date
    البحث عن أفضل رصد (أقل غيوم) قريب من التاريخ المستهدف

    Returns the highest quality observation within tolerance window.
    Useful for finding best image for a specific date.

    Example:
        GET /v1/best-observation/field_123?lat=15.5&lon=44.2&target_date=2024-02-15&tolerance_days=10
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="best_observation")

    if not _cloud_masker:
        raise HTTPException(status_code=503, detail="Cloud masker not initialized")

    try:
        # Parse target date
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Find best observation
        best_obs = await _cloud_masker.get_best_observation(
            field_id=field_id,
            latitude=lat,
            longitude=lon,
            target_date=target_dt,
            days_tolerance=tolerance_days,
        )

        if best_obs is None:
            return {
                "success": False,
                "field_id": field_id,
                "location": {"latitude": lat, "longitude": lon},
                "target_date": target_date,
                "tolerance_days": tolerance_days,
                "observation": None,
                "message": f"No clear observations found within {tolerance_days} days of {target_date}",
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "success": True,
            "field_id": field_id,
            "location": {"latitude": lat, "longitude": lon},
            "target_date": target_date,
            "tolerance_days": tolerance_days,
            "observation": best_obs.to_dict(),
            "days_from_target": abs((best_obs.date - target_dt).days),
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Best observation search failed for {field_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@app.post("/v1/interpolate-cloudy")
async def interpolate_cloudy_pixels(
    field_id: str = Query(..., description="Field identifier"),
    method: str = Query("linear", description="Interpolation method: linear, spline, previous"),
    ndvi_series: list[dict] = None,
    user: User = Depends(get_current_user),
):
    """
    Interpolate cloudy observations using temporal neighbors
    استكمال الأرصاد الملبدة بالغيوم باستخدام القيم المجاورة زمنياً

    Methods:
    - linear: Linear interpolation between valid neighbors
    - spline: Smooth spline interpolation (better for curves)
    - previous: Use previous valid value (forward fill)

    Request body:
    {
        "field_id": "field_123",
        "method": "linear",
        "ndvi_series": [
            {"date": "2024-01-01", "ndvi": 0.65, "cloudy": false},
            {"date": "2024-01-10", "ndvi": 0.45, "cloudy": true},
            {"date": "2024-01-20", "ndvi": 0.75, "cloudy": false}
        ]
    }
    """
    _validate_field_id(field_id)

    if not _cloud_masker:
        raise HTTPException(status_code=503, detail="Cloud masker not initialized")

    if ndvi_series is None:
        raise HTTPException(status_code=400, detail="ndvi_series is required")

    try:
        # Validate method
        valid_methods = ["linear", "spline", "previous"]
        if method not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid method. Choose from: {', '.join(valid_methods)}",
            )

        # Interpolate
        interpolated = await _cloud_masker.interpolate_cloudy_pixels(
            field_id=field_id, ndvi_series=ndvi_series, method=method
        )

        # Count interpolations
        interpolated_count = sum(1 for obs in interpolated if obs.get("interpolated", False))

        return {
            "success": True,
            "field_id": field_id,
            "method": method,
            "total_observations": len(interpolated),
            "interpolated_count": interpolated_count,
            "ndvi_series": interpolated,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Interpolation failed for {field_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


# =============================================================================
# Data Export Endpoints
# =============================================================================


@app.get("/v1/export/analysis/{field_id}")
async def export_analysis(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    format: str = Query(default="geojson", description="Export format: geojson, csv, json, kml"),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export field analysis data in specified format.

    Formats:
    - geojson: Geographic data with analysis properties
    - csv: Tabular format with flattened data
    - json: Complete JSON structure
    - kml: Google Earth compatible format
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="export_analysis")

    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: geojson, csv, json, kml",
        )

    # Get analysis data
    try:
        # Use the existing analyze endpoint logic
        analysis_data = await _perform_analysis(field_id, lat, lon)

        # Export data
        exporter = DataExporter()
        result = exporter.export_field_analysis(field_id=field_id, analysis_data=analysis_data, format=export_format)

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode("utf-8") if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Export analysis error: {e}")
        raise HTTPException(status_code=500, detail="Export failed") from e


@app.get("/v1/export/timeseries/{field_id}")
async def export_timeseries(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query(default="csv", description="Export format: csv, json, geojson"),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export time series data (NDVI over time) in specified format.

    Best for tracking vegetation health trends over time.
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="export_timeseries")

    try:
        export_format = ExportFormat(format.lower())
        if export_format == ExportFormat.KML:
            raise HTTPException(
                status_code=400,
                detail="KML format not supported for timeseries. Use csv, json, or geojson",
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: csv, json, geojson",
        )

    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get timeseries data using existing endpoint logic
    try:
        # Simulate timeseries data collection
        timeseries_data = []
        current_date = start_dt

        while current_date <= end_dt:
            # Get analysis for each date
            analysis = await _perform_analysis(field_id, lat, lon, analysis_date=current_date)

            point = {
                "date": current_date.isoformat(),
                "latitude": lat,
                "longitude": lon,
                "ndvi": analysis.get("indices", {}).get("ndvi", 0),
                "ndwi": analysis.get("indices", {}).get("ndwi", 0),
                "evi": analysis.get("indices", {}).get("evi", 0),
                "health_score": analysis.get("health_score", 0),
                "health_status": analysis.get("health_status", "unknown"),
                "cloud_cover": analysis.get("imagery", {}).get("cloud_cover_percent", 0),
            }
            timeseries_data.append(point)

            # Move to next week (reduce data points)
            current_date += timedelta(days=7)

        # Export data
        exporter = DataExporter()
        result = exporter.export_timeseries(field_id=field_id, timeseries_data=timeseries_data, format=export_format)

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode("utf-8") if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Data-Points": str(len(timeseries_data)),
            },
        )
    except Exception as e:
        logger.error(f"Export timeseries error: {e}")
        raise HTTPException(status_code=500, detail="Export failed") from e


@app.get("/v1/export/boundaries")
async def export_boundaries(
    field_ids: str = Query(..., description="Comma-separated field IDs"),
    format: str = Query(default="geojson", description="Export format: geojson, json, kml"),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export field boundaries in specified format.

    Useful for GIS systems and mapping applications.
    """
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_ids=field_ids, endpoint="export_boundaries")

    try:
        export_format = ExportFormat(format.lower())
        if export_format == ExportFormat.CSV:
            raise HTTPException(
                status_code=400,
                detail="CSV format not supported for boundaries. Use geojson, json, or kml",
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: geojson, json, kml",
        )

    # Parse field IDs
    field_id_list = [fid.strip() for fid in field_ids.split(",") if fid.strip()]

    if not field_id_list:
        raise HTTPException(status_code=400, detail="No field IDs provided")

    if len(field_id_list) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 fields per export")

    # Collect boundary data for each field
    boundaries = []
    for field_id in field_id_list:
        # Simulate boundary data (in production, fetch from database)
        boundary = {
            "field_id": field_id,
            "name": f"Field {field_id}",
            "area_hectares": 2.5,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [44.0, 15.0],
                        [44.01, 15.0],
                        [44.01, 15.01],
                        [44.0, 15.01],
                        [44.0, 15.0],
                    ]
                ],
            },
        }
        boundaries.append(boundary)

    # Export data
    try:
        exporter = DataExporter()
        result = exporter.export_boundaries(boundaries=boundaries, format=export_format)

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode("utf-8") if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Field-Count": str(len(boundaries)),
            },
        )
    except Exception as e:
        logger.error(f"Export boundaries error: {e}")
        raise HTTPException(status_code=500, detail="Export failed") from e


@app.get("/v1/export/report/{field_id}")
async def export_report(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    report_type: str = Query(default="full", description="Report type: full, summary, changes"),
    format: str = Query(default="json", description="Export format: json, csv, geojson"),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export comprehensive field report.

    Report types:
    - full: Complete analysis with all indices and recommendations
    - summary: High-level health metrics
    - changes: Change detection over time
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="export_report")

    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: json, csv, geojson",
        )

    if report_type not in ["full", "summary", "changes"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid report_type. Use: full, summary, or changes",
        )

    try:
        # Get analysis data
        analysis_data = await _perform_analysis(field_id, lat, lon)

        # Build report based on type
        if report_type == "full":
            report_data = analysis_data
        elif report_type == "summary":
            report_data = {
                "field_id": field_id,
                "health_score": analysis_data.get("health_score"),
                "health_status": analysis_data.get("health_status"),
                "ndvi": analysis_data.get("indices", {}).get("ndvi"),
                "analysis_date": analysis_data.get("analysis_date"),
                "anomalies_count": len(analysis_data.get("anomalies", [])),
            }
        else:  # changes
            # Get historical data for comparison
            week_ago = date.today() - timedelta(days=7)
            historical = await _perform_analysis(field_id, lat, lon, analysis_date=week_ago)

            current_ndvi = analysis_data.get("indices", {}).get("ndvi", 0)
            historical_ndvi = historical.get("indices", {}).get("ndvi", 0)

            report_data = {
                "field_id": field_id,
                "current_date": date.today().isoformat(),
                "comparison_date": week_ago.isoformat(),
                "changes": {
                    "ndvi_change": current_ndvi - historical_ndvi,
                    "ndvi_change_percent": (
                        ((current_ndvi - historical_ndvi) / historical_ndvi * 100) if historical_ndvi else 0
                    ),
                    "health_score_change": analysis_data.get("health_score", 0) - historical.get("health_score", 0),
                    "status_change": f"{historical.get('health_status')} → {analysis_data.get('health_status')}",
                },
                "current": {
                    "ndvi": current_ndvi,
                    "health_score": analysis_data.get("health_score"),
                },
                "historical": {
                    "ndvi": historical_ndvi,
                    "health_score": historical.get("health_score"),
                },
            }

        # Export based on format
        exporter = DataExporter()

        if report_type == "changes":
            # Use changes export
            result = exporter.export_changes_report(changes=[report_data], format=export_format)
        else:
            # Use field analysis export
            result = exporter.export_field_analysis(field_id=field_id, analysis_data=report_data, format=export_format)

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode("utf-8") if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Report-Type": report_type,
            },
        )
    except Exception as e:
        logger.error(f"Export report error: {e}")
        raise HTTPException(status_code=500, detail="Export failed") from e


async def _perform_analysis(field_id: str, lat: float, lon: float, analysis_date: date = None) -> dict:
    """
    Helper function to perform field analysis.
    This reuses logic from the existing /v1/analyze endpoint.
    """
    # Use multi-provider if available
    if USE_MULTI_PROVIDER and _multi_provider:
        try:
            result = await _multi_provider.analyze_field(
                latitude=lat,
                longitude=lon,
                date=analysis_date or date.today(),
                satellite_type=MultiSatelliteType.SENTINEL2,
            )

            # Convert to expected format
            analysis_data = {
                "field_id": field_id,
                "analysis_date": datetime.now().isoformat(),
                "latitude": lat,
                "longitude": lon,
                "satellite": result.get("satellite", "sentinel2"),
                "indices": result.get("indices", {}),
                "health_score": result.get("health_score", 0),
                "health_status": result.get("health_status", "unknown"),
                "anomalies": result.get("anomalies", []),
                "recommendations_ar": result.get("recommendations_ar", []),
                "recommendations_en": result.get("recommendations_en", []),
                "imagery": result.get("imagery", {}),
            }

            return analysis_data
        except Exception as e:
            logger.warning(f"Multi-provider analysis failed: {e}, using simulated data")

    # Fallback to simulated data
    import random

    ndvi = random.uniform(0.3, 0.9)
    health_score = ndvi * 100

    return {
        "field_id": field_id,
        "analysis_date": datetime.now().isoformat(),
        "latitude": lat,
        "longitude": lon,
        "satellite": "sentinel2",
        "indices": {
            "ndvi": round(ndvi, 3),
            "ndwi": round(random.uniform(0.2, 0.6), 3),
            "evi": round(random.uniform(0.3, 0.8), 3),
            "savi": round(random.uniform(0.2, 0.7), 3),
            "lai": round(random.uniform(1.0, 5.0), 2),
            "ndmi": round(random.uniform(0.2, 0.6), 3),
        },
        "health_score": round(health_score, 1),
        "health_status": ("excellent" if health_score > 80 else "good" if health_score > 60 else "fair"),
        "anomalies": [],
        "recommendations_ar": ["مراقبة مستمرة"],
        "recommendations_en": ["Continue monitoring"],
        "imagery": {
            "acquisition_date": (analysis_date or date.today()).isoformat(),
            "cloud_cover_percent": random.uniform(0, 15),
            "scene_id": f"S2A_MSIL2A_{field_id}",
            "latitude": lat,
            "longitude": lon,
        },
    }


# =============================================================================
# Change Detection Endpoints
# =============================================================================


@app.get("/v1/changes/{field_id}", response_model=ChangeReportResponse)
async def detect_changes(
    field_id: str,
    lat: float = Query(..., description="Field latitude", ge=-90, le=90),
    lon: float = Query(..., description="Field longitude", ge=-180, le=180),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    crop_type: str | None = Query(None, description="Crop type (e.g., wheat, sorghum, coffee, qat)"),
,
    user: User = Depends(get_current_user),
)
    """
    كشف التغييرات الزراعية | Detect Agricultural Changes

    Analyzes satellite time series to detect significant changes in agricultural fields:
    - Vegetation growth or decline
    - Water stress and drought
    - Flooding events
    - Harvest and planting detection
    - Crop damage from pests/weather
    - Land clearing

    Returns comprehensive report with detected events, trends, and recommendations.

    Example:
        GET /v1/changes/field_123?lat=15.5&lon=44.2&start_date=2024-01-01&end_date=2024-03-31&crop_type=wheat
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="changes")

    if not _change_detector:
        raise HTTPException(status_code=503, detail="Change detector not available")

    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Validate date range
        if end < start:
            raise HTTPException(status_code=400, detail="End date must be after start date")

        if (end - start).days > 365:
            raise HTTPException(status_code=400, detail="Maximum analysis period is 365 days")

        # Fetch NDVI time series from the satellite service
        # In production, this would call the timeseries endpoint
        # For now, we'll use simulated data or empty
        logger.info(f"Fetching NDVI time series for field {field_id}")

        # Try to get real time series data
        ndvi_timeseries = await _fetch_ndvi_timeseries(field_id, lat, lon, start, end)

        # Detect changes
        report = await _change_detector.detect_changes(
            field_id=field_id,
            latitude=lat,
            longitude=lon,
            start_date=start,
            end_date=end,
            crop_type=crop_type,
            ndvi_timeseries=ndvi_timeseries,
        )

        # Convert to response model
        return ChangeReportResponse(**report.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format") from e
    except Exception as e:
        logger.error(f"Error detecting changes: {str(e)}")
        raise HTTPException(status_code=500, detail="Change detection failed") from e


@app.get("/v1/changes/{field_id}/compare", response_model=ChangeEventResponse)
async def compare_dates(
    field_id: str,
    lat: float = Query(..., description="Field latitude", ge=-90, le=90),
    lon: float = Query(..., description="Field longitude", ge=-180, le=180),
    date1: str = Query(..., description="First date (YYYY-MM-DD)"),
    date2: str = Query(..., description="Second date (YYYY-MM-DD)"),
,
    user: User = Depends(get_current_user),
)
    """
    مقارنة تاريخين | Compare Two Dates

    Compares satellite imagery from two specific dates to identify changes.
    Useful for before/after analysis of specific events.

    Example:
        GET /v1/changes/field_123/compare?lat=15.5&lon=44.2&date1=2024-01-01&date2=2024-02-01
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="changes_compare")

    if not _change_detector:
        raise HTTPException(status_code=503, detail="Change detector not available")

    try:
        # Parse dates
        d1 = datetime.strptime(date1, "%Y-%m-%d").date()
        d2 = datetime.strptime(date2, "%Y-%m-%d").date()

        # Ensure date1 is before date2
        if d2 < d1:
            d1, d2 = d2, d1

        # Fetch NDVI values for both dates
        logger.info(f"Fetching NDVI for dates {d1} and {d2}")

        # In production, fetch from satellite service
        # For now, use simulated values
        ndvi1, ndwi1 = await _fetch_single_ndvi(field_id, lat, lon, d1)
        ndvi2, ndwi2 = await _fetch_single_ndvi(field_id, lat, lon, d2)

        # Compare dates
        event = await _change_detector.compare_dates(
            field_id=field_id,
            latitude=lat,
            longitude=lon,
            date1=d1,
            date2=d2,
            ndvi1=ndvi1,
            ndvi2=ndvi2,
            ndwi1=ndwi1,
            ndwi2=ndwi2,
        )

        # Convert to response model
        return ChangeEventResponse(**event.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format") from e
    except Exception as e:
        logger.error(f"Error comparing dates: {str(e)}")
        raise HTTPException(status_code=500, detail="Date comparison failed") from e


@app.get("/v1/changes/{field_id}/anomalies")
async def get_anomalies(
    field_id: str,
    lat: float = Query(..., description="Field latitude", ge=-90, le=90),
    lon: float = Query(..., description="Field longitude", ge=-180, le=180),
    days: int = Query(90, description="Number of days to analyze (default: 90)", ge=1, le=365),
    crop_type: str | None = Query(None, description="Crop type for expected pattern"),
,
    user: User = Depends(get_current_user),
)
    """
    كشف الشذوذ | Detect Anomalies

    Detects anomalies (unusual NDVI values) in recent satellite time series.
    Anomalies are deviations from normal patterns that may indicate problems.

    Example:
        GET /v1/changes/field_123/anomalies?lat=15.5&lon=44.2&days=90&crop_type=wheat
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", "") if user else ""
    if not tenant_id:
        logger.warning("missing_tenant_context", field_id=field_id, endpoint="anomalies")

    if not _change_detector:
        raise HTTPException(status_code=503, detail="Change detector not available")

    try:
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Fetch NDVI time series
        logger.info("Fetching NDVI time series for anomaly detection")
        ndvi_timeseries = await _fetch_ndvi_timeseries(field_id, lat, lon, start_date, end_date)

        if not ndvi_timeseries:
            return {
                "field_id": field_id,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
                "anomalies": [],
                "message": "Insufficient data for anomaly detection",
            }

        # Calculate expected pattern if crop type provided
        expected_pattern = None
        if crop_type:
            expected_pattern = _change_detector._calculate_expected_pattern(ndvi_timeseries, crop_type.lower())

        # Detect anomalies
        anomalies = await _change_detector.detect_anomalies(ndvi_timeseries, expected_pattern)

        # Publish NDVI anomaly event to NATS
        if anomalies and _nats_available and publish_analysis_completed_sync:
            try:
                severity = "mild"
                for a in anomalies:
                    a_severity = (
                        "severe"
                        if a["z_score"] >= _change_detector.ANOMALY_THRESHOLDS["severe"]
                        else (
                            "moderate"
                            if a["z_score"] >= _change_detector.ANOMALY_THRESHOLDS["moderate"]
                            else "mild"
                        )
                    )
                    if a_severity == "severe":
                        severity = "severe"
                        break
                    elif a_severity == "moderate":
                        severity = "moderate"

                publish_analysis_completed_sync(
                    event_type="satellite.ndvi.anomaly",
                    source_service="vegetation-analysis-service",
                    field_id=field_id,
                    data={
                        "field_id": field_id,
                        "anomaly_count": len(anomalies),
                        "severity": severity,
                        "crop_type": crop_type,
                        "analysis_period": {
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                        },
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                    priority="critical" if severity == "severe" else "high" if severity == "moderate" else "medium",
                )
                logger.info(
                    "nats_ndvi_anomaly_published",
                    field_id=field_id,
                    anomaly_count=len(anomalies),
                    severity=severity,
                )
            except Exception as e:
                logger.error("nats_publish_failed", subject="satellite.ndvi.anomaly", error=str(e))

        # Format response
        return {
            "field_id": field_id,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "anomaly_count": len(anomalies),
            "anomalies": [
                {
                    "date": a["date"].isoformat(),
                    "ndvi": a["ndvi"],
                    "expected": a["expected"],
                    "deviation": a["deviation"],
                    "z_score": a["z_score"],
                    "severity": (
                        "severe"
                        if a["z_score"] >= _change_detector.ANOMALY_THRESHOLDS["severe"]
                        else ("moderate" if a["z_score"] >= _change_detector.ANOMALY_THRESHOLDS["moderate"] else "mild")
                    ),
                    "ndwi": a.get("ndwi"),
                    "ndmi": a.get("ndmi"),
                }
                for a in anomalies
            ],
            "crop_type": crop_type,
            "expected_pattern_used": expected_pattern is not None,
        }

    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail="Anomaly detection failed") from e


# =============================================================================
# Helper Functions for Change Detection
# =============================================================================


async def _fetch_ndvi_timeseries(
    field_id: str,
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
) -> list[NDVIDataPoint]:
    """
    Fetch NDVI time series for change detection.
    In production, this would call the actual timeseries endpoint.
    """
    try:
        # Try to fetch from the timeseries endpoint
        # For now, return simulated data
        import math
        import random

        data_points = []
        current = start_date
        day_count = 0

        while current <= end_date:
            # Simulate seasonal NDVI pattern with some noise
            day_of_year = current.timetuple().tm_yday
            base_ndvi = 0.5 + 0.25 * math.sin(2 * math.pi * day_of_year / 365)
            noise = random.uniform(-0.1, 0.1)
            ndvi = max(0.1, min(0.9, base_ndvi + noise))

            # Simulate NDWI (water index)
            ndwi = max(-0.2, min(0.4, 0.15 + random.uniform(-0.15, 0.15)))

            # Simulate cloud cover
            cloud_cover = random.uniform(0, 50)

            data_points.append(
                NDVIDataPoint(
                    date=current,
                    ndvi=round(ndvi, 3),
                    ndwi=round(ndwi, 3),
                    ndmi=round(ndwi, 3),  # NDMI similar to NDWI
                    cloud_cover=round(cloud_cover, 1),
                )
            )

            # Move to next observation (every 5-10 days for Sentinel-2)
            current += timedelta(days=random.randint(5, 10))
            day_count += 1

            # Limit to reasonable number of points
            if day_count > 50:
                break

        logger.info(f"Generated {len(data_points)} simulated NDVI data points")
        return data_points

    except Exception as e:
        logger.warning(f"Error fetching NDVI time series: {str(e)}")
        return []


async def _fetch_single_ndvi(
    field_id: str,
    lat: float,
    lon: float,
    target_date: date,
) -> tuple[float, float | None]:
    """
    Fetch NDVI and NDWI for a single date.
    In production, this would call the actual analysis endpoint.
    Returns (ndvi, ndwi)
    """
    try:
        import math
        import random

        # Simulate seasonal pattern
        day_of_year = target_date.timetuple().tm_yday
        base_ndvi = 0.5 + 0.25 * math.sin(2 * math.pi * day_of_year / 365)
        noise = random.uniform(-0.1, 0.1)
        ndvi = max(0.1, min(0.9, base_ndvi + noise))

        ndwi = max(-0.2, min(0.4, 0.15 + random.uniform(-0.15, 0.15)))

        return (round(ndvi, 3), round(ndwi, 3))

    except Exception as e:
        logger.warning(f"Error fetching NDVI for date: {str(e)}")
        return (0.5, 0.2)  # Default values


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8090))
    uvicorn.run(app, host="0.0.0.0", port=port)
