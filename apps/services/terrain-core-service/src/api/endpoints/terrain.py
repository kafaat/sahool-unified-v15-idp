"""
Terrain Analysis API Endpoints
نقاط نهاية واجهة برمجة تحليل التضاريس

Provides REST API endpoints for terrain analysis:
- POST /api/v1/terrain/analyze - Full terrain analysis
- GET /api/v1/terrain/slope/{field_id} - Slope analysis
- GET /api/v1/terrain/flow/{field_id} - Flow direction/accumulation
- GET /api/v1/terrain/twi/{field_id} - Topographic Wetness Index
- GET /api/v1/terrain/contours/{field_id} - Contour lines
"""

import json
import time
import uuid
from datetime import UTC, datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request

# Import authentication
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


from ...algorithms.dem_processor import DEMBounds, DEMProcessor, DEMSource
from ...algorithms.terrain_indicators import (
    CurvatureType as CalcCurvatureType,
)
from ...algorithms.terrain_indicators import (
    FlowMethod,
    TerrainIndicatorCalculator,
)
from ...algorithms.terrain_indicators import (
    SlopeUnit as CalcSlopeUnit,
)
from ...core.config import settings
from ..schemas import (
    AspectClassification,
    AspectResult,
    BilingualField,
    ContourAnalysisResponse,
    ContourLine,
    ContourRequest,
    ContourResult,
    CurvatureResult,
    CurvatureType,
    DEMDataBounds,
    DEMDataRequest,
    DEMDataResponse,
    DEMSourceInfo,
    DEMSourcesResponse,
    DEMSourceType,
    DEMStatistics,
    FlowAnalysisRequest,
    FlowAnalysisResponse,
    FlowDirectionMethod,
    GeoJSONFeatureCollection,
    SlopeAnalysisRequest,
    SlopeAnalysisResponse,
    SlopeUnit,
    TerrainAnalysisRequest,
    TerrainAnalysisResponse,
    TerrainCategory,
    TerrainIrrigationRecommendation,
    TWIAnalysisResponse,
    TWIRequest,
)
from ..schemas import (
    DEMMetadata as DEMMetadataSchema,
)
from ..schemas import (
    FlowAccumulationResult as FlowAccumulationResultSchema,
)
from ..schemas import (
    FlowDirectionResult as FlowDirectionResultSchema,
)
from ..schemas import (
    SlopeResult as SlopeResultSchema,
)
from ..schemas import (
    TWIResult as TWIResultSchema,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/terrain", tags=["terrain | التضاريس"])


# =============================================================================
# Dependency Injection
# =============================================================================


def get_dem_processor(request: Request) -> DEMProcessor:
    """Get DEM processor from app state | الحصول على معالج الارتفاعات"""
    return getattr(request.app.state, "dem_processor", None) or DEMProcessor(
        cache_dir=settings.DEM_CACHE_DIR,
        default_source=DEMSource(settings.DEFAULT_DEM_SOURCE.value),
        default_resolution_m=settings.DEFAULT_RESOLUTION_M,
    )


def get_terrain_calculator(request: Request) -> TerrainIndicatorCalculator:
    """Get terrain calculator from app state | الحصول على حاسبة التضاريس"""
    return getattr(request.app.state, "terrain_calculator", None) or TerrainIndicatorCalculator(
        cell_size_m=settings.DEFAULT_RESOLUTION_M,
    )


# =============================================================================
# Helper Functions
# =============================================================================


def get_bounds_from_field_id(field_id: str) -> DEMBounds:
    """
    Get field bounds from field_id
    الحصول على حدود الحقل من معرف الحقل

    In production, this would query the field-management-service.
    For demo, generates synthetic bounds in Middle East region.
    """
    # Generate deterministic bounds from field_id hash
    # MD5 used for deterministic demo data generation, not security
    import hashlib

    hash_bytes = hashlib.md5(field_id.encode(), usedforsecurity=False).digest()

    # Middle East region bounds (roughly Saudi Arabia)
    base_lon = 38 + (hash_bytes[0] / 255) * 10  # 38-48
    base_lat = 20 + (hash_bytes[1] / 255) * 8  # 20-28

    # Field size (0.01-0.1 degrees, roughly 1-10 km)
    size = 0.01 + (hash_bytes[2] / 255) * 0.09

    return DEMBounds(
        min_lon=base_lon,
        min_lat=base_lat,
        max_lon=base_lon + size,
        max_lat=base_lat + size * 0.8,  # Slightly shorter N-S
    )


def classify_terrain(mean_slope_pct: float) -> tuple[TerrainCategory, BilingualField]:
    """Classify terrain based on slope | تصنيف التضاريس بناءً على الميل"""
    if mean_slope_pct < 2:
        return TerrainCategory.FLAT, BilingualField(en="Flat", ar="مسطح")
    elif mean_slope_pct < 5:
        return TerrainCategory.GENTLE, BilingualField(en="Gentle", ar="لطيف")
    elif mean_slope_pct < 10:
        return TerrainCategory.MODERATE, BilingualField(en="Moderate", ar="معتدل")
    elif mean_slope_pct < 20:
        return TerrainCategory.STEEP, BilingualField(en="Steep", ar="حاد")
    else:
        return TerrainCategory.VERY_STEEP, BilingualField(en="Very Steep", ar="حاد جداً")


def generate_irrigation_recommendations(
    mean_slope_pct: float,
    mean_twi: float,
    field_id: str,
) -> list[TerrainIrrigationRecommendation]:
    """
    Generate irrigation recommendations based on terrain
    إنشاء توصيات الري بناءً على التضاريس
    """
    recommendations = []

    # Zone classification based on TWI and slope
    if mean_twi > 10:
        # High moisture accumulation zones
        recommendations.append(
            TerrainIrrigationRecommendation(
                zone_id=f"{field_id}_zone_1",
                zone_name=BilingualField(en="High Moisture Zone", ar="منطقة عالية الرطوبة"),
                area_ha=2.5,  # Example value
                mean_slope_pct=mean_slope_pct,
                mean_twi=mean_twi,
                irrigation_suitability="excellent",
                suitability_name=BilingualField(en="Excellent", ar="ممتاز"),
                recommended_method=BilingualField(en="Drip Irrigation", ar="الري بالتنقيط"),
                water_retention_capacity="high",
                erosion_risk="low",
                notes=BilingualField(
                    en="Natural water accumulation zone, ideal for water-intensive crops",
                    ar="منطقة تراكم مياه طبيعية، مثالية للمحاصيل كثيفة المياه",
                ),
            )
        )
    elif mean_twi > 5:
        # Moderate moisture zones
        recommendations.append(
            TerrainIrrigationRecommendation(
                zone_id=f"{field_id}_zone_2",
                zone_name=BilingualField(en="Moderate Moisture Zone", ar="منطقة متوسطة الرطوبة"),
                area_ha=5.0,
                mean_slope_pct=mean_slope_pct,
                mean_twi=mean_twi,
                irrigation_suitability="good",
                suitability_name=BilingualField(en="Good", ar="جيد"),
                recommended_method=BilingualField(en="Sprinkler Irrigation", ar="الري بالرش"),
                water_retention_capacity="moderate",
                erosion_risk="moderate" if mean_slope_pct > 5 else "low",
                notes=BilingualField(
                    en="Suitable for most crops with standard irrigation",
                    ar="مناسب لمعظم المحاصيل مع الري القياسي",
                ),
            )
        )
    else:
        # Low moisture / ridge zones
        recommendations.append(
            TerrainIrrigationRecommendation(
                zone_id=f"{field_id}_zone_3",
                zone_name=BilingualField(en="Ridge Zone", ar="منطقة التلال"),
                area_ha=1.5,
                mean_slope_pct=mean_slope_pct,
                mean_twi=mean_twi,
                irrigation_suitability="fair" if mean_slope_pct < 10 else "poor",
                suitability_name=BilingualField(
                    en="Fair" if mean_slope_pct < 10 else "Poor",
                    ar="مقبول" if mean_slope_pct < 10 else "ضعيف",
                ),
                recommended_method=BilingualField(en="Micro-sprinkler or Drip", ar="الرش الدقيق أو التنقيط"),
                water_retention_capacity="low",
                erosion_risk="high" if mean_slope_pct > 10 else "moderate",
                notes=BilingualField(
                    en="Requires careful water management, consider terracing",
                    ar="يتطلب إدارة مياه حذرة، ينصح بالمصاطب",
                ),
            )
        )

    return recommendations


# =============================================================================
# API Endpoints
# =============================================================================


@router.post(
    "/analyze",
    response_model=TerrainAnalysisResponse,
    summary="Full Terrain Analysis | تحليل التضاريس الكامل",
    description="""
    Performs comprehensive terrain analysis for a field including:
    - Slope and aspect
    - Flow direction and accumulation
    - Topographic Wetness Index (TWI)
    - Curvature (plan and profile)
    - Contour generation
    - Irrigation recommendations

    يجري تحليلاً شاملاً للتضاريس للحقل بما في ذلك:
    - الميل والجانب
    - اتجاه التدفق وتراكمه
    - مؤشر الرطوبة الطبوغرافية
    - الانحناء (أفقي وطولي)
    - إنشاء خطوط الكنتور
    - توصيات الري
    """,
)
async def analyze_terrain(
    request_data: TerrainAnalysisRequest,
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    terrain_calculator: TerrainIndicatorCalculator = Depends(get_terrain_calculator),
    current_user: User = Depends(get_current_user),
):
    """Perform full terrain analysis for a field | إجراء تحليل كامل للتضاريس"""
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    warnings = []

    logger.info(
        "Starting terrain analysis",
        field_id=request_data.field_id,
        analysis_id=analysis_id,
        dem_source=request_data.dem_source.value,
    )

    try:
        # Get field bounds
        if request_data.geometry:
            # Extract bounds from geometry
            coords = request_data.geometry.coordinates[0]
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            bounds = DEMBounds(
                min_lon=min(lons),
                min_lat=min(lats),
                max_lon=max(lons),
                max_lat=max(lats),
            )
        else:
            bounds = get_bounds_from_field_id(request_data.field_id)

        # Acquire DEM data
        dem_source = DEMSource(request_data.dem_source.value)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=dem_source,
            resolution_m=request_data.target_resolution_m or settings.DEFAULT_RESOLUTION_M,
        )

        # Fill holes if any
        if dem_data.nodata_mask.any():
            dem_data = await dem_processor.fill_holes(dem_data)
            warnings.append("DEM holes were filled using interpolation")

        # Reproject if requested
        if request_data.target_crs and request_data.target_crs != dem_data.metadata.crs:
            dem_data = await dem_processor.reproject(
                dem_data,
                target_crs=request_data.target_crs,
            )

        # Calculate terrain indicators
        results = {}

        # Slope
        slope_result = None
        if request_data.include_slope:
            calc_unit = CalcSlopeUnit(request_data.slope_unit.value)
            slope_result = terrain_calculator.calculate_slope(dem_data, unit=calc_unit)
            results["slope"] = slope_result

        # Aspect
        aspect_result = None
        if request_data.include_aspect:
            aspect_result = terrain_calculator.calculate_aspect(dem_data)
            results["aspect"] = aspect_result

        # Flow direction and accumulation
        flow_dir_result = None
        flow_acc_result = None
        if request_data.include_flow_direction or request_data.include_flow_accumulation or request_data.include_twi:
            flow_method = FlowMethod(request_data.flow_method.value)
            flow_dir_result = terrain_calculator.calculate_flow_direction(dem_data, method=flow_method)
            results["flow_direction"] = flow_dir_result

            if request_data.include_flow_accumulation or request_data.include_twi:
                flow_acc_result = terrain_calculator.calculate_flow_accumulation(dem_data, flow_dir_result)
                results["flow_accumulation"] = flow_acc_result

        # TWI
        twi_result = None
        if request_data.include_twi:
            twi_result = terrain_calculator.calculate_twi(
                dem_data,
                flow_accumulation=flow_acc_result,
            )
            results["twi"] = twi_result

        # Curvature
        plan_curv_result = None
        profile_curv_result = None
        if request_data.include_curvature:
            plan_curv_result = terrain_calculator.calculate_curvature(dem_data, CalcCurvatureType.PLAN)
            profile_curv_result = terrain_calculator.calculate_curvature(dem_data, CalcCurvatureType.PROFILE)
            results["plan_curvature"] = plan_curv_result
            results["profile_curvature"] = profile_curv_result

        # Contours
        contour_result = None
        if request_data.include_contours:
            contour_result = terrain_calculator.generate_contours(
                dem_data,
                interval_m=request_data.contour_interval_m or settings.CONTOUR_INTERVAL_M,
            )
            results["contours"] = contour_result

        # Calculate statistics from DEM
        import numpy as np

        valid_data = dem_data.data[~dem_data.nodata_mask]

        dem_statistics = DEMStatistics(
            min_elevation_m=float(np.min(valid_data)),
            max_elevation_m=float(np.max(valid_data)),
            mean_elevation_m=float(np.mean(valid_data)),
            std_elevation_m=float(np.std(valid_data)),
            elevation_range_m=float(np.max(valid_data) - np.min(valid_data)),
            total_pixels=int(dem_data.data.size),
            valid_pixels=int(np.sum(~dem_data.nodata_mask)),
        )

        # Build DEM metadata schema
        source_info = dem_processor.get_source_info(dem_source)
        dem_metadata_schema = DEMMetadataSchema(
            source=request_data.dem_source,
            source_name=BilingualField(
                en=source_info["name_en"],
                ar=source_info["name_ar"],
            ),
            resolution_m=dem_data.metadata.resolution_m,
            crs=dem_data.metadata.crs,
            bounds=dem_data.metadata.bounds.__dict__,
            acquisition_date=dem_data.metadata.acquisition_date,
            vertical_datum=dem_data.metadata.vertical_datum,
            nodata_value=dem_data.metadata.nodata_value,
        )

        # Build response components
        slope_schema = None
        if slope_result:
            slope_schema = SlopeResultSchema(
                unit=SlopeUnit(slope_result.unit.value),
                unit_name=BilingualField(
                    en=slope_result.unit.value.capitalize(),
                    ar="درجات" if slope_result.unit == CalcSlopeUnit.DEGREES else "نسبة مئوية",
                ),
                min_slope=slope_result.min_value,
                max_slope=slope_result.max_value,
                mean_slope=slope_result.mean_value,
                std_slope=slope_result.std_value,
                classification=slope_result.classification,
            )

        aspect_schema = None
        if aspect_result:
            aspect_schema = AspectResult(
                dominant_direction=AspectClassification(aspect_result.dominant_direction.lower()),
                dominant_direction_name=BilingualField(
                    en=aspect_result.dominant_direction,
                    ar=terrain_calculator.D8_DIRECTIONS_AR.get(
                        aspect_result.dominant_direction, aspect_result.dominant_direction
                    ),
                ),
                distribution=aspect_result.distribution,
                mean_aspect_degrees=aspect_result.mean_aspect,
            )

        flow_dir_schema = None
        if flow_dir_result:
            flow_dir_schema = FlowDirectionResultSchema(
                method=FlowDirectionMethod(flow_dir_result.method.value),
                method_name=BilingualField(
                    en="D8 Algorithm" if flow_dir_result.method == FlowMethod.D8 else flow_dir_result.method.value,
                    ar="خوارزمية D8" if flow_dir_result.method == FlowMethod.D8 else flow_dir_result.method.value,
                ),
                dominant_direction=flow_dir_result.dominant_direction,
                direction_distribution=flow_dir_result.direction_distribution,
            )

        flow_acc_schema = None
        if flow_acc_result:
            flow_acc_schema = FlowAccumulationResultSchema(
                max_accumulation=flow_acc_result.max_accumulation,
                mean_accumulation=flow_acc_result.mean_accumulation,
                drainage_density=flow_acc_result.drainage_density,
                channel_pixels=flow_acc_result.channel_pixels,
                threshold_used=flow_acc_result.threshold,
                streams_geojson=GeoJSONFeatureCollection(
                    features=flow_acc_result.streams or [],
                ),
            )

        twi_schema = None
        if twi_result:
            interpretation = "High moisture accumulation potential"
            interpretation_ar = "إمكانية تراكم رطوبة عالية"
            if twi_result.mean_twi < 5:
                interpretation = "Low moisture accumulation, well-drained"
                interpretation_ar = "تراكم رطوبة منخفض، تصريف جيد"
            elif twi_result.mean_twi < 10:
                interpretation = "Moderate moisture accumulation"
                interpretation_ar = "تراكم رطوبة معتدل"

            twi_schema = TWIResultSchema(
                min_twi=twi_result.min_twi,
                max_twi=twi_result.max_twi,
                mean_twi=twi_result.mean_twi,
                std_twi=twi_result.std_twi,
                high_moisture_area_pct=twi_result.high_moisture_pct,
                interpretation=BilingualField(en=interpretation, ar=interpretation_ar),
            )

        plan_curv_schema = None
        if plan_curv_result:
            plan_curv_schema = CurvatureResult(
                curvature_type=CurvatureType.PLAN,
                type_name=BilingualField(en="Plan Curvature", ar="الانحناء الأفقي"),
                min_curvature=plan_curv_result.min_value,
                max_curvature=plan_curv_result.max_value,
                mean_curvature=plan_curv_result.mean_value,
                convex_pct=plan_curv_result.convex_pct,
                concave_pct=plan_curv_result.concave_pct,
                flat_pct=plan_curv_result.flat_pct,
            )

        profile_curv_schema = None
        if profile_curv_result:
            profile_curv_schema = CurvatureResult(
                curvature_type=CurvatureType.PROFILE,
                type_name=BilingualField(en="Profile Curvature", ar="الانحناء الطولي"),
                min_curvature=profile_curv_result.min_value,
                max_curvature=profile_curv_result.max_value,
                mean_curvature=profile_curv_result.mean_value,
                convex_pct=profile_curv_result.convex_pct,
                concave_pct=profile_curv_result.concave_pct,
                flat_pct=profile_curv_result.flat_pct,
            )

        contour_schema = None
        if contour_result:
            contour_lines = [
                ContourLine(
                    elevation_m=c["properties"]["elevation_m"],
                    length_m=c["properties"]["length_m"],
                    is_major=c["properties"]["is_major"],
                    geometry=c["geometry"],
                )
                for c in contour_result.contours[:100]  # Limit for response size
            ]
            contour_schema = ContourResult(
                interval_m=contour_result.interval_m,
                min_elevation_m=contour_result.min_elevation,
                max_elevation_m=contour_result.max_elevation,
                total_contours=contour_result.total_contours,
                major_interval_m=contour_result.major_interval_m,
                contours=contour_lines,
            )

        # Classify terrain and generate recommendations
        mean_slope_pct = (
            np.tan(np.radians(slope_result.mean_value)) * 100
            if slope_result and slope_result.unit == CalcSlopeUnit.DEGREES
            else slope_result.mean_value
            if slope_result
            else 0
        )
        terrain_category, terrain_category_name = classify_terrain(mean_slope_pct)

        irrigation_recommendations = generate_irrigation_recommendations(
            mean_slope_pct=mean_slope_pct,
            mean_twi=twi_result.mean_twi if twi_result else 5.0,
            field_id=request_data.field_id,
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        response = TerrainAnalysisResponse(
            field_id=request_data.field_id,
            analysis_id=analysis_id,
            status="completed",
            analyzed_at=datetime.now(UTC),
            dem_metadata=dem_metadata_schema,
            dem_statistics=dem_statistics,
            slope=slope_schema,
            aspect=aspect_schema,
            flow_direction=flow_dir_schema,
            flow_accumulation=flow_acc_schema,
            twi=twi_schema,
            plan_curvature=plan_curv_schema,
            profile_curvature=profile_curv_schema,
            contours=contour_schema,
            terrain_category=terrain_category,
            terrain_category_name=terrain_category_name,
            irrigation_recommendations=irrigation_recommendations,
            processing_time_ms=processing_time_ms,
            warnings=warnings,
        )

        logger.info(
            "Terrain analysis completed",
            field_id=request_data.field_id,
            analysis_id=analysis_id,
            processing_time_ms=processing_time_ms,
        )

        return response

    except Exception as e:
        logger.error(
            "Terrain analysis failed",
            field_id=request_data.field_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TERRAIN_ANALYSIS_ERROR",
                "message": f"Terrain analysis failed: {str(e)}",
                "message_ar": f"فشل تحليل التضاريس: {str(e)}",
            },
        )


@router.get(
    "/slope/{field_id}",
    response_model=SlopeAnalysisResponse,
    summary="Get Slope Analysis | الحصول على تحليل الميل",
)
async def get_slope_analysis(
    field_id: str,
    dem_source: DEMSourceType = Query(default=DEMSourceType.COPERNICUS),
    slope_unit: SlopeUnit = Query(default=SlopeUnit.DEGREES),
    classify: bool = Query(default=True, description="Include slope classification"),
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    terrain_calculator: TerrainIndicatorCalculator = Depends(get_terrain_calculator),
    current_user: User = Depends(get_current_user),
):
    """Get slope analysis for a field | الحصول على تحليل الميل للحقل"""
    start_time = time.time()

    logger.info("Calculating slope", field_id=field_id)

    try:
        bounds = get_bounds_from_field_id(field_id)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=DEMSource(dem_source.value),
        )

        calc_unit = CalcSlopeUnit(slope_unit.value)
        slope_result = terrain_calculator.calculate_slope(dem_data, unit=calc_unit)

        slope_schema = SlopeResultSchema(
            unit=slope_unit,
            unit_name=BilingualField(
                en=slope_unit.value.capitalize(),
                ar="درجات" if slope_unit == SlopeUnit.DEGREES else "نسبة مئوية",
            ),
            min_slope=slope_result.min_value,
            max_slope=slope_result.max_value,
            mean_slope=slope_result.mean_value,
            std_slope=slope_result.std_value,
            classification=slope_result.classification if classify else None,
        )

        return SlopeAnalysisResponse(
            field_id=field_id,
            analyzed_at=datetime.now(UTC),
            dem_source=dem_source,
            slope=slope_schema,
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.error("Slope analysis failed", field_id=field_id, error=str(e))
        raise HTTPException(status_code=500, detail="Slope analysis failed")


@router.get(
    "/flow/{field_id}",
    response_model=FlowAnalysisResponse,
    summary="Get Flow Analysis | الحصول على تحليل التدفق",
)
async def get_flow_analysis(
    field_id: str,
    dem_source: DEMSourceType = Query(default=DEMSourceType.COPERNICUS),
    method: FlowDirectionMethod = Query(default=FlowDirectionMethod.D8),
    accumulation_threshold: int = Query(default=100, ge=1),
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    terrain_calculator: TerrainIndicatorCalculator = Depends(get_terrain_calculator),
    current_user: User = Depends(get_current_user),
):
    """Get flow direction and accumulation analysis | الحصول على تحليل اتجاه التدفق وتراكمه"""
    start_time = time.time()

    logger.info("Calculating flow", field_id=field_id)

    try:
        bounds = get_bounds_from_field_id(field_id)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=DEMSource(dem_source.value),
        )

        flow_dir_result = terrain_calculator.calculate_flow_direction(dem_data, method=FlowMethod(method.value))
        flow_acc_result = terrain_calculator.calculate_flow_accumulation(
            dem_data, flow_dir_result, threshold=accumulation_threshold
        )

        flow_dir_schema = FlowDirectionResultSchema(
            method=method,
            method_name=BilingualField(
                en="D8 Algorithm",
                ar="خوارزمية D8",
            ),
            dominant_direction=flow_dir_result.dominant_direction,
            direction_distribution=flow_dir_result.direction_distribution,
        )

        flow_acc_schema = FlowAccumulationResultSchema(
            max_accumulation=flow_acc_result.max_accumulation,
            mean_accumulation=flow_acc_result.mean_accumulation,
            drainage_density=flow_acc_result.drainage_density,
            channel_pixels=flow_acc_result.channel_pixels,
            threshold_used=flow_acc_result.threshold,
            streams_geojson={
                "type": "FeatureCollection",
                "features": flow_acc_result.streams or [],
            },
        )

        return FlowAnalysisResponse(
            field_id=field_id,
            analyzed_at=datetime.now(UTC),
            dem_source=dem_source,
            flow_direction=flow_dir_schema,
            flow_accumulation=flow_acc_schema,
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.error("Flow analysis failed", field_id=field_id, error=str(e))
        raise HTTPException(status_code=500, detail="Flow analysis failed")


@router.get(
    "/twi/{field_id}",
    response_model=TWIAnalysisResponse,
    summary="Get Topographic Wetness Index | الحصول على مؤشر الرطوبة الطبوغرافية",
)
async def get_twi_analysis(
    field_id: str,
    dem_source: DEMSourceType = Query(default=DEMSourceType.COPERNICUS),
    flow_method: FlowDirectionMethod = Query(default=FlowDirectionMethod.D8),
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    terrain_calculator: TerrainIndicatorCalculator = Depends(get_terrain_calculator),
    current_user: User = Depends(get_current_user),
):
    """Get Topographic Wetness Index analysis | الحصول على تحليل مؤشر الرطوبة الطبوغرافية"""
    start_time = time.time()

    logger.info("Calculating TWI", field_id=field_id)

    try:
        bounds = get_bounds_from_field_id(field_id)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=DEMSource(dem_source.value),
        )

        twi_result = terrain_calculator.calculate_twi(dem_data)

        interpretation = "High moisture accumulation potential"
        interpretation_ar = "إمكانية تراكم رطوبة عالية"
        if twi_result.mean_twi < 5:
            interpretation = "Low moisture accumulation, well-drained"
            interpretation_ar = "تراكم رطوبة منخفض، تصريف جيد"
        elif twi_result.mean_twi < 10:
            interpretation = "Moderate moisture accumulation"
            interpretation_ar = "تراكم رطوبة معتدل"

        twi_schema = TWIResultSchema(
            min_twi=twi_result.min_twi,
            max_twi=twi_result.max_twi,
            mean_twi=twi_result.mean_twi,
            std_twi=twi_result.std_twi,
            high_moisture_area_pct=twi_result.high_moisture_pct,
            interpretation=BilingualField(en=interpretation, ar=interpretation_ar),
        )

        return TWIAnalysisResponse(
            field_id=field_id,
            analyzed_at=datetime.now(UTC),
            dem_source=dem_source,
            twi=twi_schema,
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.error("TWI analysis failed", field_id=field_id, error=str(e))
        raise HTTPException(status_code=500, detail="TWI analysis failed")


@router.get(
    "/contours/{field_id}",
    response_model=ContourAnalysisResponse,
    summary="Get Contour Lines | الحصول على خطوط الكنتور",
)
async def get_contours(
    field_id: str,
    dem_source: DEMSourceType = Query(default=DEMSourceType.COPERNICUS),
    interval_m: float = Query(default=5.0, gt=0, description="Contour interval in meters"),
    simplify_tolerance: float = Query(default=1.0, ge=0),
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    terrain_calculator: TerrainIndicatorCalculator = Depends(get_terrain_calculator),
    current_user: User = Depends(get_current_user),
):
    """Get contour lines for a field | الحصول على خطوط الكنتور للحقل"""
    start_time = time.time()

    logger.info("Generating contours", field_id=field_id, interval_m=interval_m)

    try:
        bounds = get_bounds_from_field_id(field_id)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=DEMSource(dem_source.value),
        )

        contour_result = terrain_calculator.generate_contours(
            dem_data,
            interval_m=interval_m,
            simplify_tolerance=simplify_tolerance,
        )

        contour_lines = [
            ContourLine(
                elevation_m=c["properties"]["elevation_m"],
                length_m=c["properties"]["length_m"],
                is_major=c["properties"]["is_major"],
                geometry=c["geometry"],
            )
            for c in contour_result.contours[:200]  # Limit response size
        ]

        contour_schema = ContourResult(
            interval_m=contour_result.interval_m,
            min_elevation_m=contour_result.min_elevation,
            max_elevation_m=contour_result.max_elevation,
            total_contours=contour_result.total_contours,
            major_interval_m=contour_result.major_interval_m,
            contours=contour_lines,
        )

        return ContourAnalysisResponse(
            field_id=field_id,
            analyzed_at=datetime.now(UTC),
            dem_source=dem_source,
            contours=contour_schema,
            processing_time_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.error("Contour generation failed", field_id=field_id, error=str(e))
        raise HTTPException(status_code=500, detail="Contour generation failed")


@router.get(
    "/sources",
    response_model=DEMSourcesResponse,
    summary="List Available DEM Sources | قائمة مصادر الارتفاعات المتاحة",
)
async def list_dem_sources(
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    current_user: User = Depends(get_current_user),
) -> DEMSourcesResponse:
    """List available DEM data sources | قائمة مصادر بيانات الارتفاعات المتاحة"""
    raw_sources = dem_processor.list_available_sources()

    # Convert to typed response
    sources = [
        DEMSourceInfo(
            source=DEMSourceType(src.get("source", src.get("id", "local"))),
            name=src.get("name_en", src.get("name", "Unknown")),
            name_ar=src.get("name_ar", "غير معروف"),
            description=src.get("description_en", src.get("description", "")),
            description_ar=src.get("description_ar", ""),
            resolution_m=src.get("resolution_m", 30.0),
            coverage=src.get("coverage", "Global"),
            is_available=src.get("is_available", True),
        )
        for src in raw_sources
    ]

    default_source = settings.DEFAULT_DEM_SOURCE
    default_info = dem_processor.get_source_info(DEMSource(default_source.value))

    return DEMSourcesResponse(
        sources=sources,
        default=default_source.value,
        default_name=BilingualField(
            en=default_info.get("name_en", "Copernicus DEM"),
            ar=default_info.get("name_ar", "ارتفاعات كوبرنيكوس"),
        ),
    )


@router.get(
    "/dem/{field_id}",
    response_model=DEMDataResponse,
    summary="Get DEM Data for Field | الحصول على بيانات الارتفاعات للحقل",
    description="""
    Retrieves Digital Elevation Model data for a specific field.
    Used by downstream services (hydrology, leveling) for terrain analysis.

    يسترجع بيانات نموذج الارتفاع الرقمي لحقل محدد.
    يستخدم من قبل الخدمات المتصلة (الهيدرولوجيا، التسوية) لتحليل التضاريس.
    """,
)
async def get_dem_data(
    field_id: str,
    dem_source: DEMSourceType = Query(default=DEMSourceType.COPERNICUS),
    resolution_m: float = Query(default=30.0, ge=1.0, le=1000.0),
    include_data: bool = Query(
        default=False,
        description="Include raw elevation data (for small fields only) | تضمين بيانات الارتفاع الخام",
    ),
    dem_processor: DEMProcessor = Depends(get_dem_processor),
    current_user: User = Depends(get_current_user),
):
    """
    Get DEM data for a field - used by hydrology and leveling services.
    الحصول على بيانات الارتفاعات للحقل - يستخدم من قبل خدمات الهيدرولوجيا والتسوية
    """
    import numpy as np

    logger.info("Fetching DEM data", field_id=field_id, source=dem_source.value)

    try:
        bounds = get_bounds_from_field_id(field_id)
        dem_data = await dem_processor.acquire_dem(
            bounds=bounds,
            source=DEMSource(dem_source.value),
            resolution_m=resolution_m,
        )

        # Fill holes if any
        if dem_data.nodata_mask.any():
            dem_data = await dem_processor.fill_holes(dem_data)

        # Calculate statistics
        valid_data = dem_data.data[~dem_data.nodata_mask]
        elevation_min = float(np.min(valid_data))
        elevation_max = float(np.max(valid_data))
        elevation_mean = float(np.mean(valid_data))

        # Optionally include raw data for small fields
        elevation_data = None
        max_cells_for_inline = 10000  # 100x100 max for inline data
        if include_data and dem_data.data.size <= max_cells_for_inline:
            # Replace nodata with a sentinel value
            data_copy = dem_data.data.copy()
            data_copy[dem_data.nodata_mask] = -9999.0
            elevation_data = data_copy.tolist()

        return DEMDataResponse(
            field_id=field_id,
            dem_source=dem_source,
            bounds=DEMDataBounds(
                min_lon=bounds.min_lon,
                min_lat=bounds.min_lat,
                max_lon=bounds.max_lon,
                max_lat=bounds.max_lat,
            ),
            resolution_m=dem_data.metadata.resolution_m,
            rows=dem_data.data.shape[0],
            cols=dem_data.data.shape[1],
            crs=dem_data.metadata.crs,
            nodata_value=dem_data.metadata.nodata_value,
            elevation_min=elevation_min,
            elevation_max=elevation_max,
            elevation_mean=elevation_mean,
            elevation_data=elevation_data,
            download_url=None,  # Could be S3 URL for large datasets
            analyzed_at=datetime.now(UTC),
        )

    except Exception as e:
        logger.error("DEM data fetch failed", field_id=field_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DEM_FETCH_ERROR",
                "message": f"Failed to fetch DEM data: {str(e)}",
                "message_ar": f"فشل جلب بيانات الارتفاعات: {str(e)}",
            },
        )
