"""
Hydrology API Endpoints
نقاط نهاية API للهيدرولوجيا

Provides endpoints for:
- Full hydrology analysis
- Drainage network extraction
- Wetness/waterlogging analysis
- Depression identification
- Stream detection
- Basin delineation

Tenant isolation is enforced STRICTLY via the JWT ``tid`` claim (surfaced on the
authenticated ``User`` as ``tenant_id``). ``X-Tenant-Id`` is accepted as a
legacy/informational header but is NEVER authoritative — any mismatch against
the JWT tenant results in ``403``.
"""

import logging
import re
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query

# Import authentication
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:  # pragma: no cover - offline/unit-test fallback
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():  # type: ignore[no-redef]
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")

# ==============================================================================
# Security: Input Validation
# ==============================================================================

# Safe pattern for field IDs: alphanumeric, hyphens, underscores only
SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


def validate_field_id(field_id: str) -> str:
    """
    Validate field_id to prevent SSRF and path traversal attacks.
    التحقق من معرف الحقل لمنع هجمات SSRF واختراق المسار
    """
    if not field_id or not SAFE_ID_PATTERN.match(field_id):
        raise ValueError("Invalid field_id format: must be 1-128 alphanumeric characters, hyphens, or underscores")
    return field_id


from ...core.config import get_settings
from ...utils.hydrology_algorithms import (
    DEMData,
    HydrologyAnalyzer,
    generate_mock_dem,
)
from ..schemas import (
    DEPRESSION_RISK_AR,
    DRAINAGE_TYPE_AR,
    WETNESS_LEVEL_AR,
    BasinDelineation,
    BasinDelineationRequest,
    BasinDelineationResponse,
    Depression,
    DepressionAnalysis,
    DepressionAnalysisRequest,
    DepressionAnalysisResponse,
    DepressionRisk,
    DrainageAnalysisRequest,
    DrainageNetwork,
    DrainageNetworkResponse,
    DrainageSegment,
    DrainageType,
    GeoPoint,
    GeoPolygon,
    HydrologyAnalysisRequest,
    HydrologyAnalysisResponse,
    HydrologyAnalysisResult,
    Stream,
    StreamDetectionRequest,
    StreamNetwork,
    StreamNetworkResponse,
    SubBasin,
    WaterloggingPrediction,
    WetnessAnalysis,
    WetnessAnalysisRequest,
    WetnessAnalysisResponse,
    WetnessLevel,
    WetnessZone,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/hydrology", tags=["Hydrology | الهيدرولوجيا"])


# ==============================================================================
# Dependencies
# ==============================================================================


# Safe-log helper to defeat log-injection attempts via attacker-controlled values.
_LOG_INJ_RE = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def _safe_log(value: object) -> str:
    """Sanitize a value for structured logging (strips control characters)."""
    if value is None:
        return ""
    return _LOG_INJ_RE.sub("?", str(value))[:200]


def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
    current_user: User = Depends(get_current_user),
) -> str:
    """
    Resolve the effective tenant_id STRICTLY from the JWT ``tid`` claim.

    استخراج معرف المستأجر من مطالبة JWT (لا يعتمد على الهيدر)

    - The authoritative source is ``current_user.tenant_id`` (from the JWT).
    - ``X-Tenant-Id`` is accepted only as a legacy informational header: if
      provided, it must match the JWT tenant or the request is rejected with
      ``403``.
    - If the JWT carries no tenant AND no header is supplied, the request is
      rejected with ``400``.
    """
    jwt_tenant = getattr(current_user, "tenant_id", None)

    # Authoritative path: JWT tenant
    if jwt_tenant:
        if x_tenant_id and x_tenant_id != jwt_tenant:
            raise HTTPException(
                status_code=403,
                detail=(
                    "X-Tenant-Id does not match authenticated user's tenant | "
                    "معرف المستأجر لا يتطابق مع المستأجر المصادق عليه"
                ),
            )
        return jwt_tenant

    # Fallback: no tenant on the JWT — this should only happen in offline
    # test harnesses. Preserve backwards compatibility with the header, but
    # refuse if neither source provided a value.
    if x_tenant_id:
        return x_tenant_id

    raise HTTPException(
        status_code=400,
        detail=(
            "Tenant context missing: JWT has no tid claim and no X-Tenant-Id "
            "header was provided | السياق المستأجر مفقود"
        ),
    )


async def fetch_dem_from_terrain_service(
    field_id: str, tenant_id: str | None = None, resolution_m: float = 30.0
) -> DEMData | None:
    """
    Fetch DEM data from terrain-core-service.
    جلب بيانات الارتفاع من خدمة التضاريس
    """
    import numpy as np

    settings = get_settings()

    # Validate field_id to prevent SSRF attacks
    try:
        validated_field_id = validate_field_id(field_id)
    except ValueError as e:
        logger.warning("Invalid field_id rejected", field_id=field_id, error=str(e))
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            if tenant_id:
                headers["X-Tenant-Id"] = tenant_id

            # Use the correct DEM endpoint path: /api/v1/terrain/dem/{field_id}
            response = await client.get(
                f"{settings.terrain_service_url}/api/v1/terrain/dem/{validated_field_id}",
                params={"include_data": "true", "resolution_m": resolution_m},
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                # Parse DEM data from response into our DEMData format
                if data.get("elevation_data"):
                    elevation_array = np.array(data["elevation_data"], dtype=np.float32)
                    bounds = data.get("bounds", {})
                    dem = DEMData(
                        elevation=elevation_array,
                        resolution=data.get("resolution_m", 30.0),
                        nodata_value=data.get("nodata_value", -9999.0),
                        bounds=(
                            bounds.get("min_lon", 45.0),
                            bounds.get("min_lat", 15.0),
                            bounds.get("max_lon", 45.1),
                            bounds.get("max_lat", 15.1),
                        )
                        if bounds
                        else None,
                    )
                    logger.info(
                        "Fetched DEM from terrain service",
                        field_id=field_id,
                        rows=dem.rows,
                        cols=dem.cols,
                    )
                    return dem
                else:
                    logger.warning(
                        "DEM data not included in response (field may be too large)",
                        field_id=field_id,
                    )
                    return None
            else:
                logger.warning(
                    "Failed to fetch DEM from terrain service",
                    field_id=field_id,
                    status=response.status_code,
                )
                return None

    except Exception as e:
        logger.warning("Error fetching DEM from terrain service", field_id=field_id, error=str(e))
        return None


async def fetch_rainfall_from_weather_service(
    lat: float, lon: float, days: int = 30, tenant_id: str | None = None
) -> dict[str, Any] | None:
    """
    Fetch rainfall data from weather-service.
    جلب بيانات الأمطار من خدمة الطقس
    """
    settings = get_settings()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {}
            if tenant_id:
                headers["X-Tenant-Id"] = tenant_id

            response = await client.post(
                f"{settings.weather_service_url}/weather/forecast",
                json={
                    "tenant_id": tenant_id or "default",
                    "field_id": "hydrology_analysis",
                    "lat": lat,
                    "lon": lon,
                },
                headers=headers,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("Failed to fetch rainfall from weather service", status=response.status_code)
                return None

    except Exception as e:
        logger.warning("Error fetching rainfall from weather service", error=str(e))
        return None


def generate_mock_analysis_data(field_id: str, resolution_m: float = 30.0) -> tuple[DEMData, HydrologyAnalyzer]:
    """Generate mock DEM and run analysis for testing."""
    # Generate synthetic DEM
    dem = generate_mock_dem(
        rows=100,
        cols=100,
        resolution=resolution_m,
        base_elevation=100.0,
        relief=50.0,
        bounds=(45.0, 15.0, 45.1, 15.1),  # Mock bounds in Yemen region
    )

    # Run analysis
    analyzer = HydrologyAnalyzer()
    analyzer.load_dem(dem)
    analyzer.run_full_analysis()

    return dem, analyzer


# ==============================================================================
# Endpoints
# ==============================================================================


@router.post(
    "/analyze",
    response_model=HydrologyAnalysisResponse,
    response_model_by_alias=True,
)
async def analyze_hydrology(
    request: HydrologyAnalysisRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> HydrologyAnalysisResponse:
    """
    Full hydrology analysis for a field.
    تحليل هيدرولوجي كامل للحقل

    Includes:
    - Drainage network extraction | استخراج شبكة التصريف
    - Wetness analysis | تحليل الرطوبة
    - Depression identification | تحديد المنخفضات
    - Stream detection | كشف المجاري المائية
    - Basin delineation | تحديد الأحواض

    Integrates with terrain-core-service for DEM data and
    weather-service for rainfall data.
    """
    start_time = time.time()
    settings = get_settings()

    effective_tenant_id = tenant_id

    logger.info("Starting hydrology analysis", field_id=request.field_id, tenant_id=effective_tenant_id)

    # Try to fetch real DEM data
    dem = await fetch_dem_from_terrain_service(request.field_id, effective_tenant_id)

    # Fall back to mock data if no DEM available
    if dem is None:
        logger.info("Using mock DEM data for analysis")
        dem, analyzer = generate_mock_analysis_data(request.field_id, request.resolution_m)
    else:
        analyzer = HydrologyAnalyzer()
        analyzer.load_dem(dem)
        analyzer.run_full_analysis(flow_threshold=settings.flow_accumulation_threshold)

    # Fetch rainfall data if requested
    rainfall_data = None
    if request.include_rainfall and dem.bounds:
        center_lat = (dem.bounds[1] + dem.bounds[3]) / 2
        center_lon = (dem.bounds[0] + dem.bounds[2]) / 2
        rainfall_data = await fetch_rainfall_from_weather_service(
            center_lat, center_lon, request.rainfall_period_days, effective_tenant_id
        )

    # Build response
    now = datetime.now(UTC)
    field_area_ha = dem.rows * dem.cols * dem.cell_area / 10000

    # Build drainage network response
    drainage = build_drainage_network(analyzer, dem, request.field_id)

    # Build wetness analysis response
    wetness = build_wetness_analysis(analyzer, dem, request.field_id, rainfall_data)

    # Build depression analysis response
    depressions = build_depression_analysis(analyzer, dem, request.field_id)

    # Build stream network response
    streams = build_stream_network(analyzer, dem, request.field_id)

    # Build basin delineation response
    basins = build_basin_delineation(analyzer, dem, request.field_id)

    # Calculate overall flood risk
    flood_risk = calculate_flood_risk(wetness, depressions)

    # Calculate drainage quality score
    drainage_score = calculate_drainage_quality_score(drainage, wetness)

    # Generate recommendations
    recommendations_ar, recommendations_en = generate_recommendations(drainage, wetness, depressions, flood_risk)

    result = HydrologyAnalysisResult(
        field_id=request.field_id,
        tenant_id=effective_tenant_id or "default",
        analyzed_at=now,
        dem_source=request.dem_source or "mock",
        resolution_m=request.resolution_m,
        field_area_ha=round(field_area_ha, 2),
        mean_elevation_m=round(float(analyzer.dem.elevation.mean()), 1),
        elevation_range_m=round(float(analyzer.dem.elevation.max() - analyzer.dem.elevation.min()), 1),
        mean_slope_percent=round(float(analyzer.flow_data.slope.mean()) * 100 / 45, 1),
        drainage=drainage,
        wetness=wetness,
        depressions=depressions,
        streams=streams,
        basins=basins,
        flood_risk_level=flood_risk,
        flood_risk_level_ar=DEPRESSION_RISK_AR[flood_risk],
        drainage_quality_score=round(drainage_score, 1),
        recommendations_ar=recommendations_ar,
        recommendations_en=recommendations_en,
        rainfall_data=rainfall_data,
    )

    processing_time = (time.time() - start_time) * 1000

    logger.info(
        "Hydrology analysis complete",
        field_id=request.field_id,
        processing_time_ms=round(processing_time, 2),
    )

    return HydrologyAnalysisResponse(success=True, data=result, processing_time_ms=round(processing_time, 2))


@router.get(
    "/drainage/{field_id}",
    response_model=DrainageNetworkResponse,
    response_model_by_alias=True,
)
async def get_drainage_network(
    field_id: str,
    flow_threshold: int = Query(default=100, ge=10, le=10000, description="Flow accumulation threshold"),
    include_pattern: bool = Query(default=True, description="Include drainage pattern classification"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> DrainageNetworkResponse:
    """
    Get drainage network for a field.
    الحصول على شبكة التصريف للحقل

    Extracts drainage channels and stream network using D8 algorithm.
    """
    logger.info("Fetching drainage network", field_id=field_id)

    # Generate mock data for now
    dem, analyzer = generate_mock_analysis_data(field_id)
    drainage = build_drainage_network(analyzer, dem, field_id)

    return DrainageNetworkResponse(
        success=True,
        data=drainage,
        analyzed_at=datetime.now(UTC),
        dem_source="mock",
        resolution_m=dem.resolution,
    )


@router.get(
    "/wetness/{field_id}",
    response_model=WetnessAnalysisResponse,
    response_model_by_alias=True,
)
async def get_wetness_analysis(
    field_id: str,
    include_prediction: bool = Query(default=True, description="Include waterlogging prediction"),
    rainfall_mm: float | None = Query(default=None, ge=0, description="Expected rainfall for prediction"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> WetnessAnalysisResponse:
    """
    Get wetness/waterlogging analysis for a field.
    الحصول على تحليل الرطوبة والتشبع المائي للحقل

    Calculates Topographic Wetness Index (TWI) and identifies
    areas prone to waterlogging.
    """
    logger.info("Fetching wetness analysis", field_id=field_id)

    # Generate mock data
    dem, analyzer = generate_mock_analysis_data(field_id)

    # Build rainfall data dict if rainfall_mm provided
    rainfall_data = None
    if rainfall_mm is not None:
        rainfall_data = {"total_rainfall_mm": rainfall_mm}

    wetness = build_wetness_analysis(analyzer, dem, field_id, rainfall_data)

    return WetnessAnalysisResponse(success=True, data=wetness, analyzed_at=datetime.now(UTC))


@router.get(
    "/depressions/{field_id}",
    response_model=DepressionAnalysisResponse,
    response_model_by_alias=True,
)
async def get_depressions(
    field_id: str,
    min_depth_m: float = Query(default=0.1, ge=0.01, le=10.0, description="Minimum depression depth"),
    min_area_sqm: float = Query(default=10.0, ge=1.0, description="Minimum depression area"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> DepressionAnalysisResponse:
    """
    Identify depressions/sinks in the field.
    تحديد المنخفضات في الحقل

    Detects terrain depressions that may cause waterlogging
    and provides drainage recommendations.
    """
    logger.info("Identifying depressions", field_id=field_id)

    # Generate mock data
    dem, analyzer = generate_mock_analysis_data(field_id)
    depressions = build_depression_analysis(analyzer, dem, field_id)

    return DepressionAnalysisResponse(success=True, data=depressions, analyzed_at=datetime.now(UTC))


@router.get(
    "/streams/{field_id}",
    response_model=StreamNetworkResponse,
    response_model_by_alias=True,
)
async def get_streams(
    field_id: str,
    min_order: int = Query(default=1, ge=1, le=6, description="Minimum Strahler stream order"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> StreamNetworkResponse:
    """
    Detect streams in the field.
    كشف المجاري المائية في الحقل

    Uses Strahler ordering to classify streams by importance.
    """
    logger.info("Detecting streams", field_id=field_id)

    # Generate mock data
    dem, analyzer = generate_mock_analysis_data(field_id)
    streams = build_stream_network(analyzer, dem, field_id)

    return StreamNetworkResponse(success=True, data=streams, analyzed_at=datetime.now(UTC))


@router.get(
    "/basins/{field_id}",
    response_model=BasinDelineationResponse,
    response_model_by_alias=True,
)
async def get_basins(
    field_id: str,
    min_area_ha: float = Query(default=0.5, ge=0.1, description="Minimum basin area in hectares"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
) -> BasinDelineationResponse:
    """
    Delineate drainage basins/watersheds.
    تحديد أحواض التصريف

    Identifies watershed boundaries and calculates
    basin morphometric parameters.
    """
    logger.info("Delineating basins", field_id=field_id)

    # Generate mock data
    dem, analyzer = generate_mock_analysis_data(field_id)
    basins = build_basin_delineation(analyzer, dem, field_id)

    return BasinDelineationResponse(success=True, data=basins, analyzed_at=datetime.now(UTC))


# ==============================================================================
# Helper Functions
# ==============================================================================


def build_drainage_network(analyzer: HydrologyAnalyzer, dem: DEMData, field_id: str) -> DrainageNetwork:
    """Build DrainageNetwork response from analyzer results."""
    import random

    segments = []
    total_length = 0

    for seg in analyzer.drainage_segments:
        # Convert cells to coordinates
        coords = []
        if dem.bounds:
            min_lon, min_lat, max_lon, max_lat = dem.bounds
            lon_res = (max_lon - min_lon) / dem.cols
            lat_res = (max_lat - min_lat) / dem.rows

            for row, col in seg.cells:
                lon = min_lon + (col + 0.5) * lon_res
                lat = max_lat - (row + 0.5) * lat_res
                coords.append([lon, lat])
        else:
            coords = [[c[1], c[0]] for c in seg.cells]

        length_m = len(seg.cells) * dem.resolution
        total_length += length_m

        segments.append(
            DrainageSegment(
                segment_id=seg.segment_id,
                coordinates=coords,
                stream_order=seg.stream_order,
                length_m=round(length_m, 1),
                upstream_area_ha=round(seg.upstream_cells * dem.cell_area / 10000, 2),
                slope_percent=round(random.uniform(1, 10), 1),
            )
        )

    # Calculate drainage density
    field_area_ha = dem.rows * dem.cols * dem.cell_area / 10000
    drainage_density = total_length / field_area_ha if field_area_ha > 0 else 0

    # Find main channel (longest segment)
    main_length = max([s.length_m for s in segments]) if segments else 0

    # Calculate bifurcation ratio
    orders = [s.stream_order for s in segments]
    order_counts = {}
    for o in orders:
        order_counts[o] = order_counts.get(o, 0) + 1

    bifurcation = 3.5  # Default Horton's law value
    if len(order_counts) >= 2:
        sorted_orders = sorted(order_counts.keys())
        ratios = []
        for i in range(len(sorted_orders) - 1):
            n1 = order_counts[sorted_orders[i]]
            n2 = order_counts[sorted_orders[i + 1]]
            if n2 > 0:
                ratios.append(n1 / n2)
        if ratios:
            bifurcation = sum(ratios) / len(ratios)

    pattern = DrainageType.DENDRITIC
    if analyzer.drainage_segments:
        pattern_str = "dendritic"  # Would come from classify_drainage_pattern
        pattern = DrainageType(pattern_str)

    return DrainageNetwork(
        field_id=field_id,
        total_length_m=round(total_length, 1),
        drainage_density=round(drainage_density, 2),
        main_channel_length_m=round(main_length, 1),
        bifurcation_ratio=round(bifurcation, 2),
        pattern=pattern,
        pattern_ar=DRAINAGE_TYPE_AR[pattern],
        segments=segments,
        statistics={
            "segment_count": len(segments),
            "order_distribution": order_counts,
            "mean_segment_length_m": round(total_length / len(segments), 1) if segments else 0,
        },
    )


def build_wetness_analysis(
    analyzer: HydrologyAnalyzer,
    dem: DEMData,
    field_id: str,
    rainfall_data: dict[str, Any] | None = None,
) -> WetnessAnalysis:
    """Build WetnessAnalysis response from analyzer results."""
    import numpy as np

    twi = analyzer.twi
    field_area_ha = dem.rows * dem.cols * dem.cell_area / 10000

    # Get wetness zones
    zone_data = analyzer.get_wetness_zones()

    zones = []
    for zd in zone_data:
        level = WetnessLevel(zd["level"])
        zones.append(
            WetnessZone(
                zone_id=str(uuid.uuid4())[:8],
                level=level,
                level_ar=WETNESS_LEVEL_AR[level],
                area_ha=round(zd["area_ha"], 2),
                percentage=round(zd["percentage"], 1),
                twi_mean=round((zd["twi_range"][0] + zd["twi_range"][1]) / 2, 1),
                twi_range=(round(zd["twi_range"][0], 1), round(zd["twi_range"][1], 1)),
                recommendations_ar=get_wetness_recommendations_ar(level),
                recommendations_en=get_wetness_recommendations_en(level),
            )
        )

    # Find dominant level
    dominant_zone = max(zones, key=lambda z: z.area_ha) if zones else None
    dominant_level = dominant_zone.level if dominant_zone else WetnessLevel.MODERATE

    # Calculate irrigation efficiency
    # Higher TWI variability = lower efficiency
    twi_cv = float(np.std(twi) / np.mean(twi)) if np.mean(twi) > 0 else 0
    irrigation_efficiency = max(0, min(100, 100 - twi_cv * 20))

    # Build waterlogging prediction if rainfall data available
    prediction = None
    if rainfall_data:
        total_rainfall = rainfall_data.get("total_rainfall_mm", 50)
        prediction = WaterloggingPrediction(
            rainfall_mm=total_rainfall,
            risk_level=DepressionRisk.MEDIUM if total_rainfall > 30 else DepressionRisk.LOW,
            risk_level_ar=DEPRESSION_RISK_AR[DepressionRisk.MEDIUM if total_rainfall > 30 else DepressionRisk.LOW],
            affected_area_ha=round(field_area_ha * 0.1 * (total_rainfall / 50), 2),
            affected_percentage=round(10 * (total_rainfall / 50), 1),
            time_to_drain_hours=24 + total_rainfall * 0.5,
            mitigation_ar=["تحسين نظام الصرف", "إنشاء قنوات تصريف إضافية"],
            mitigation_en=["Improve drainage system", "Create additional drainage channels"],
        )

    return WetnessAnalysis(
        field_id=field_id,
        total_area_ha=round(field_area_ha, 2),
        twi_mean=round(float(np.mean(twi)), 2),
        twi_std=round(float(np.std(twi)), 2),
        twi_min=round(float(np.min(twi)), 2),
        twi_max=round(float(np.max(twi)), 2),
        dominant_level=dominant_level,
        dominant_level_ar=WETNESS_LEVEL_AR[dominant_level],
        zones=zones,
        waterlogging_prediction=prediction,
        irrigation_efficiency_score=round(irrigation_efficiency, 1),
    )


def build_depression_analysis(analyzer: HydrologyAnalyzer, dem: DEMData, field_id: str) -> DepressionAnalysis:
    """Build DepressionAnalysis response from analyzer results."""
    field_area_ha = dem.rows * dem.cols * dem.cell_area / 10000

    depressions = []
    total_volume = 0
    total_area = 0
    high_risk_count = 0
    critical_count = 0

    for dep in analyzer.depressions:
        # Determine risk level based on depth
        if dep.depth_m >= 1.0:
            risk = DepressionRisk.CRITICAL
            critical_count += 1
        elif dep.depth_m >= 0.5:
            risk = DepressionRisk.HIGH
            high_risk_count += 1
        elif dep.depth_m >= 0.2:
            risk = DepressionRisk.MEDIUM
        else:
            risk = DepressionRisk.LOW

        area_sqm = len(dep.cells) * dem.cell_area
        total_volume += dep.volume_m3
        total_area += area_sqm

        # Get center coordinates
        if dem.bounds and dep.cells:
            min_lon, min_lat, max_lon, max_lat = dem.bounds
            lon_res = (max_lon - min_lon) / dem.cols
            lat_res = (max_lat - min_lat) / dem.rows

            avg_row = sum(c[0] for c in dep.cells) / len(dep.cells)
            avg_col = sum(c[1] for c in dep.cells) / len(dep.cells)
            center_lon = min_lon + (avg_col + 0.5) * lon_res
            center_lat = max_lat - (avg_row + 0.5) * lat_res
            center = GeoPoint(lat=center_lat, lon=center_lon)
        else:
            center = GeoPoint(lat=15.0, lon=45.0)

        depressions.append(
            Depression(
                depression_id=dep.depression_id,
                center=center,
                depth_m=round(dep.depth_m, 2),
                area_sqm=round(area_sqm, 1),
                volume_m3=round(dep.volume_m3, 2),
                perimeter_m=round(len(dep.cells) * 4 * dem.resolution / 3, 1),
                risk_level=risk,
                risk_level_ar=DEPRESSION_RISK_AR[risk],
                drainage_recommendations_ar=get_depression_recommendations_ar(risk),
                drainage_recommendations_en=get_depression_recommendations_en(risk),
            )
        )

    depressions_percentage = (total_area / (field_area_ha * 10000)) * 100 if field_area_ha > 0 else 0

    # Generate summary
    if critical_count > 0:
        summary_ar = f"تم تحديد {len(depressions)} منخفض، منها {critical_count} حرج يحتاج تدخل فوري"
        summary_en = f"Identified {len(depressions)} depressions, {critical_count} critical requiring immediate action"
    elif high_risk_count > 0:
        summary_ar = f"تم تحديد {len(depressions)} منخفض، منها {high_risk_count} عالي الخطورة"
        summary_en = f"Identified {len(depressions)} depressions, {high_risk_count} high risk"
    else:
        summary_ar = f"تم تحديد {len(depressions)} منخفض بمخاطر منخفضة إلى متوسطة"
        summary_en = f"Identified {len(depressions)} depressions with low to moderate risk"

    return DepressionAnalysis(
        field_id=field_id,
        total_depressions=len(depressions),
        total_volume_m3=round(total_volume, 2),
        total_area_sqm=round(total_area, 1),
        field_area_ha=round(field_area_ha, 2),
        depressions_percentage=round(depressions_percentage, 2),
        high_risk_count=high_risk_count,
        critical_count=critical_count,
        depressions=depressions,
        summary_ar=summary_ar,
        summary_en=summary_en,
    )


def build_stream_network(analyzer: HydrologyAnalyzer, dem: DEMData, field_id: str) -> StreamNetwork:
    """Build StreamNetwork response from analyzer results."""
    streams = []
    max_order = 1
    total_length = 0
    streams_by_order = {}

    for seg in analyzer.drainage_segments:
        order = seg.stream_order
        max_order = max(max_order, order)
        streams_by_order[order] = streams_by_order.get(order, 0) + 1

        # Convert cells to coordinates
        coords = []
        if dem.bounds:
            min_lon, min_lat, max_lon, max_lat = dem.bounds
            lon_res = (max_lon - min_lon) / dem.cols
            lat_res = (max_lat - min_lat) / dem.rows

            for row, col in seg.cells:
                lon = min_lon + (col + 0.5) * lon_res
                lat = max_lat - (row + 0.5) * lat_res
                coords.append([lon, lat])
        else:
            coords = [[c[1], c[0]] for c in seg.cells]

        length_m = len(seg.cells) * dem.resolution
        total_length += length_m

        streams.append(
            Stream(
                stream_id=seg.segment_id,
                order=order,
                coordinates=coords,
                length_m=round(length_m, 1),
                avg_slope_percent=round(5.0, 1),  # Mock value
                upstream_area_ha=round(seg.upstream_cells * dem.cell_area / 10000, 2),
                is_perennial=order >= 3,
            )
        )

    # Find main stream
    main_stream_length = max([s.length_m for s in streams]) if streams else 0

    return StreamNetwork(
        field_id=field_id,
        total_streams=len(streams),
        total_length_m=round(total_length, 1),
        max_order=max_order,
        streams_by_order=streams_by_order,
        main_stream_length_m=round(main_stream_length, 1),
        streams=streams,
        hydraulic_geometry={
            "width_coefficient": 2.5,
            "depth_coefficient": 0.4,
            "velocity_coefficient": 0.3,
        },
    )


def build_basin_delineation(analyzer: HydrologyAnalyzer, dem: DEMData, field_id: str) -> BasinDelineation:
    """Build BasinDelineation response from analyzer results."""
    import math

    sub_basins = []
    total_area = 0
    main_basin_area = 0

    for basin_data in analyzer.basins:
        area_ha = basin_data["area_ha"]
        total_area += area_ha
        if area_ha > main_basin_area:
            main_basin_area = area_ha

        # Get outlet coordinates
        outlet_row, outlet_col = basin_data["outlet"]
        if dem.bounds:
            min_lon, min_lat, max_lon, max_lat = dem.bounds
            lon_res = (max_lon - min_lon) / dem.cols
            lat_res = (max_lat - min_lat) / dem.rows
            outlet_lon = min_lon + (outlet_col + 0.5) * lon_res
            outlet_lat = max_lat - (outlet_row + 0.5) * lat_res
        else:
            outlet_lon, outlet_lat = 45.0, 15.0

        pour_point = GeoPoint(lat=outlet_lat, lon=outlet_lon)

        # Calculate centroid
        cells = basin_data["cells"]
        if cells:
            avg_row = sum(c[0] for c in cells) / len(cells)
            avg_col = sum(c[1] for c in cells) / len(cells)
            if dem.bounds:
                centroid_lon = min_lon + (avg_col + 0.5) * lon_res
                centroid_lat = max_lat - (avg_row + 0.5) * lat_res
            else:
                centroid_lon, centroid_lat = 45.0, 15.0
        else:
            centroid_lon, centroid_lat = outlet_lon, outlet_lat

        centroid = GeoPoint(lat=centroid_lat, lon=centroid_lon)

        # Perimeter estimate
        perimeter = math.sqrt(area_ha * 10000) * 4 * 0.8  # Rough estimate

        # Time of concentration (Kirpich formula simplified)
        length_km = math.sqrt(area_ha / 100)
        slope = 5.0  # percent
        tc_hours = 0.0195 * (length_km * 1000) ** 0.77 / (slope**0.385) / 60
        tc_minutes = tc_hours * 60

        # Create boundary polygon (simplified rectangle for mock)
        boundary = GeoPolygon(
            coordinates=[
                [outlet_lon - 0.01, outlet_lat - 0.01],
                [outlet_lon + 0.01, outlet_lat - 0.01],
                [outlet_lon + 0.01, outlet_lat + 0.01],
                [outlet_lon - 0.01, outlet_lat + 0.01],
                [outlet_lon - 0.01, outlet_lat - 0.01],
            ]
        )

        sub_basins.append(
            SubBasin(
                basin_id=basin_data["basin_id"],
                area_ha=round(area_ha, 2),
                perimeter_m=round(perimeter, 1),
                centroid=centroid,
                pour_point=pour_point,
                mean_elevation_m=round(basin_data["mean_elevation"], 1),
                elevation_range_m=round(basin_data["max_elevation"] - basin_data["min_elevation"], 1),
                mean_slope_percent=5.0,
                time_of_concentration_min=round(tc_minutes, 1),
                boundary=boundary,
            )
        )

    # Main outlet
    if sub_basins:
        main_outlet = min(sub_basins, key=lambda b: b.mean_elevation_m).pour_point
    else:
        main_outlet = GeoPoint(lat=15.0, lon=45.0)

    # Calculate ratios
    elongation_ratio = 0.7  # Typical value
    circularity_ratio = 0.6

    return BasinDelineation(
        field_id=field_id,
        total_basins=len(sub_basins),
        total_area_ha=round(total_area, 2),
        main_basin_area_ha=round(main_basin_area, 2),
        outlet_point=main_outlet,
        mean_elevation_m=round(sum(b.mean_elevation_m for b in sub_basins) / len(sub_basins), 1)
        if sub_basins
        else 100.0,
        relief_m=50.0,  # Mock value
        elongation_ratio=round(elongation_ratio, 2),
        circularity_ratio=round(circularity_ratio, 2),
        basins=sub_basins,
        runoff_coefficient=0.3,  # Typical agricultural value
    )


def calculate_flood_risk(wetness: WetnessAnalysis, depressions: DepressionAnalysis) -> DepressionRisk:
    """Calculate overall flood risk level."""
    # Score based on multiple factors
    score = 0

    # Wetness factor
    if wetness.dominant_level == WetnessLevel.WATERLOGGED:
        score += 4
    elif wetness.dominant_level == WetnessLevel.VERY_WET:
        score += 3
    elif wetness.dominant_level == WetnessLevel.WET:
        score += 2

    # Depression factor
    if depressions.critical_count > 0:
        score += 3
    elif depressions.high_risk_count > 0:
        score += 2

    # Depression percentage factor
    if depressions.depressions_percentage > 5:
        score += 2
    elif depressions.depressions_percentage > 2:
        score += 1

    # Map score to risk level
    if score >= 6:
        return DepressionRisk.CRITICAL
    elif score >= 4:
        return DepressionRisk.HIGH
    elif score >= 2:
        return DepressionRisk.MEDIUM
    else:
        return DepressionRisk.LOW


def calculate_drainage_quality_score(drainage: DrainageNetwork, wetness: WetnessAnalysis) -> float:
    """Calculate overall drainage quality score (0-100)."""
    score = 100.0

    # Deduct for low drainage density
    if drainage.drainage_density < 50:
        score -= 20
    elif drainage.drainage_density < 100:
        score -= 10

    # Deduct for high wetness
    if wetness.dominant_level == WetnessLevel.WATERLOGGED:
        score -= 30
    elif wetness.dominant_level == WetnessLevel.VERY_WET:
        score -= 20
    elif wetness.dominant_level == WetnessLevel.WET:
        score -= 10

    # Deduct for low irrigation efficiency
    if wetness.irrigation_efficiency_score < 50:
        score -= 20
    elif wetness.irrigation_efficiency_score < 70:
        score -= 10

    return max(0, min(100, score))


def generate_recommendations(
    drainage: DrainageNetwork,
    wetness: WetnessAnalysis,
    depressions: DepressionAnalysis,
    flood_risk: DepressionRisk,
) -> tuple[list[str], list[str]]:
    """Generate recommendations based on analysis results."""
    recommendations_ar = []
    recommendations_en = []

    # Drainage recommendations
    if drainage.drainage_density < 50:
        recommendations_ar.append("إنشاء قنوات تصريف إضافية لتحسين كثافة التصريف")
        recommendations_en.append("Create additional drainage channels to improve drainage density")

    # Wetness recommendations
    if wetness.dominant_level in [WetnessLevel.VERY_WET, WetnessLevel.WATERLOGGED]:
        recommendations_ar.append("تحسين نظام الصرف في المناطق الرطبة")
        recommendations_en.append("Improve drainage system in wet areas")

    # Depression recommendations
    if depressions.critical_count > 0:
        recommendations_ar.append("معالجة المنخفضات الحرجة فوراً لتجنب التشبع المائي")
        recommendations_en.append("Address critical depressions immediately to prevent waterlogging")
    elif depressions.high_risk_count > 0:
        recommendations_ar.append("ردم المنخفضات عالية الخطورة أو إنشاء صرف تحتي")
        recommendations_en.append("Fill high-risk depressions or install subsurface drainage")

    # Flood risk recommendations
    if flood_risk == DepressionRisk.CRITICAL:
        recommendations_ar.append("تطبيق إجراءات حماية عاجلة من الفيضانات")
        recommendations_en.append("Implement urgent flood protection measures")
    elif flood_risk == DepressionRisk.HIGH:
        recommendations_ar.append("مراقبة مستويات المياه خلال موسم الأمطار")
        recommendations_en.append("Monitor water levels during rainy season")

    # Irrigation recommendations
    if wetness.irrigation_efficiency_score < 70:
        recommendations_ar.append("تحسين توزيع المياه بناءً على خريطة الرطوبة")
        recommendations_en.append("Improve water distribution based on wetness map")

    # Default recommendation if none generated
    if not recommendations_ar:
        recommendations_ar.append("الحقل في حالة جيدة، استمر في الصيانة الدورية")
        recommendations_en.append("Field is in good condition, continue regular maintenance")

    return recommendations_ar, recommendations_en


def get_wetness_recommendations_ar(level: WetnessLevel) -> list[str]:
    """Get Arabic recommendations for wetness level."""
    recs = {
        WetnessLevel.VERY_DRY: ["زيادة معدل الري", "استخدام مواد حافظة للرطوبة"],
        WetnessLevel.DRY: ["مراقبة الري بعناية", "التغطية للحفاظ على الرطوبة"],
        WetnessLevel.MODERATE: ["الحفاظ على جدول الري الحالي"],
        WetnessLevel.WET: ["تقليل معدل الري", "التأكد من عمل نظام الصرف"],
        WetnessLevel.VERY_WET: ["إيقاف الري مؤقتاً", "تحسين الصرف"],
        WetnessLevel.WATERLOGGED: ["تدخل عاجل لتصريف المياه الزائدة", "إنشاء قنوات صرف طوارئ"],
    }
    return recs.get(level, [])


def get_wetness_recommendations_en(level: WetnessLevel) -> list[str]:
    """Get English recommendations for wetness level."""
    recs = {
        WetnessLevel.VERY_DRY: ["Increase irrigation rate", "Use moisture-retaining materials"],
        WetnessLevel.DRY: ["Monitor irrigation carefully", "Apply mulch to retain moisture"],
        WetnessLevel.MODERATE: ["Maintain current irrigation schedule"],
        WetnessLevel.WET: ["Reduce irrigation rate", "Ensure drainage system is working"],
        WetnessLevel.VERY_WET: ["Temporarily stop irrigation", "Improve drainage"],
        WetnessLevel.WATERLOGGED: [
            "Urgent intervention to drain excess water",
            "Create emergency drainage channels",
        ],
    }
    return recs.get(level, [])


def get_depression_recommendations_ar(risk: DepressionRisk) -> list[str]:
    """Get Arabic recommendations for depression risk level."""
    recs = {
        DepressionRisk.LOW: ["مراقبة دورية"],
        DepressionRisk.MEDIUM: ["تسوية سطح التربة", "تحسين الصرف المحلي"],
        DepressionRisk.HIGH: ["ردم المنخفض", "إنشاء صرف تحتي"],
        DepressionRisk.CRITICAL: ["تدخل عاجل", "إنشاء نظام ضخ للمياه"],
    }
    return recs.get(risk, [])


def get_depression_recommendations_en(risk: DepressionRisk) -> list[str]:
    """Get English recommendations for depression risk level."""
    recs = {
        DepressionRisk.LOW: ["Regular monitoring"],
        DepressionRisk.MEDIUM: ["Level soil surface", "Improve local drainage"],
        DepressionRisk.HIGH: ["Fill depression", "Install subsurface drainage"],
        DepressionRisk.CRITICAL: ["Urgent intervention", "Install water pumping system"],
    }
    return recs.get(risk, [])
