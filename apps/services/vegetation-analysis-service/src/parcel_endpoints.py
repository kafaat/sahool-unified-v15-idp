"""
SAHOOL Agricultural Land Parcel Detection Endpoints
نقاط نهاية كشف قطع الأراضي الزراعية

API endpoints for automatic agricultural parcel detection inspired by GeoLabel.
Supports 4 detection strategies:
1. Semantic Segmentation
2. Boundary Detection
3. Training-Free (spectral indices only)
4. Hybrid (combined approach)
"""

import logging
from datetime import datetime

from fastapi import Depends, HTTPException, Query

from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from pydantic import BaseModel, Field

from shared.auth.dependencies import get_current_user
from shared.auth.models import User

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class ParcelDetectionRequest(BaseModel):
    """Request model for parcel detection"""

    strategy: str = Field(
        "hybrid",
        description="Detection strategy: semantic_segmentation, boundary_detection, training_free, hybrid",
    )
    precision: str = Field(
        "high",
        description="Model precision: very_high, high, acceptable, speed_focused",
    )
    target_shape: str = Field(
        "irregular",
        description="Shape regularization: irregular, rectangle, convex_hull, minimum_bounding",
    )
    min_area_hectares: float = Field(0.05, description="Minimum parcel area in hectares")
    max_area_hectares: float = Field(1000.0, description="Maximum parcel area in hectares")
    ndvi_threshold: float = Field(0.25, description="NDVI threshold for cropland detection")
    smoothing_iterations: int = Field(2, description="Number of boundary smoothing iterations")
    use_gpu: bool = Field(True, description="Use GPU for inference if available")


class RegionDetectionRequest(BaseModel):
    """Request model for region-based detection"""

    north: float = Field(..., description="North latitude bound")
    south: float = Field(..., description="South latitude bound")
    east: float = Field(..., description="East longitude bound")
    west: float = Field(..., description="West longitude bound")
    strategy: str = Field("hybrid", description="Detection strategy")
    precision: str = Field("high", description="Model precision level")
    min_area_hectares: float = Field(0.05, description="Minimum parcel area")


class ParcelClassifyRequest(BaseModel):
    """Request model for vector classification"""

    parcels: list[dict] = Field(..., description="List of GeoJSON features to classify")


class ParcelMergeRequest(BaseModel):
    """Request model for merging parcels"""

    parcel_ids: list[str] = Field(..., description="IDs of parcels to merge")
    parcels: list[dict] = Field(..., description="GeoJSON features of parcels to merge")


class ParcelSplitRequest(BaseModel):
    """Request model for splitting a parcel"""

    parcel: dict = Field(..., description="GeoJSON feature of parcel to split")
    cutting_line: list[list[float]] = Field(..., description="Cutting line coordinates [[lon, lat], ...]")


class ParcelConnectRequest(BaseModel):
    """Request model for connecting parcels"""

    parcels: list[dict] = Field(..., description="GeoJSON features of fragments to connect")
    max_gap_meters: float = Field(10.0, description="Maximum gap to bridge in meters")


class BatchAssignRequest(BaseModel):
    """Request model for batch attribute assignment"""

    parcel_ids: list[str] = Field(..., description="IDs of parcels to update")
    parcels: list[dict] = Field(..., description="GeoJSON features to update")
    attribute: str = Field(..., description="Attribute name: crop_type, land_cover, is_irrigated")
    value: str = Field(..., description="Value to assign")


# =============================================================================
# Endpoint Registration
# =============================================================================


def register_parcel_endpoints(app, land_detector):
    """
    Register agricultural land parcel detection endpoints.

    Args:
        app: FastAPI application instance
        land_detector: AgriculturalLandDetector instance
    """

    @app.post("/v1/parcels/auto-generate", response_model=dict)
    async def auto_generate_parcels(
        lat: float = Query(..., description="Center latitude"),
        lon: float = Query(..., description="Center longitude"),
        radius_m: float = Query(1000, description="Search radius in meters"),
        strategy: str = Query("hybrid", description="Detection strategy"),
        precision: str = Query("high", description="Model precision level"),
        min_area: float = Query(0.05, description="Minimum parcel area (hectares)"),
        smoothing: int = Query(2, description="Smoothing iterations"),
        target_shape: str = Query("irregular", description="Shape regularization"),
        _user: User = Depends(get_current_user),
    ):
        """
        Automatically generate agricultural parcels around a point.
        توليد تلقائي لقطع الأراضي الزراعية حول نقطة محددة

        Uses GeoLabel-inspired multi-strategy detection:
        - **hybrid**: Combined semantic segmentation + boundary detection (recommended)
        - **semantic_segmentation**: Pixel-level cropland classification
        - **boundary_detection**: Edge-based parcel boundary detection
        - **training_free**: NDVI threshold-based (no training required)

        Precision levels (inspired by GeoLabel 3.6.0):
        - **very_high**: Highest accuracy, slowest
        - **high**: Good balance (default)
        - **acceptable**: Faster, lower accuracy
        - **speed_focused**: Fastest processing

        Returns GeoJSON FeatureCollection with detected agricultural parcels.

        Example:
            POST /v1/parcels/auto-generate?lat=15.5&lon=44.2&radius_m=1000&strategy=hybrid
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            from .agricultural_land_detector import (
                DetectionConfig,
                DetectionStrategy,
                ModelPrecision,
                ParcelShape,
            )

            # Parse configuration
            try:
                det_strategy = DetectionStrategy(strategy)
            except ValueError:
                det_strategy = DetectionStrategy.HYBRID

            try:
                det_precision = ModelPrecision(precision)
            except ValueError:
                det_precision = ModelPrecision.HIGH

            try:
                det_shape = ParcelShape(target_shape)
            except ValueError:
                det_shape = ParcelShape.IRREGULAR

            config = DetectionConfig(
                strategy=det_strategy,
                precision=det_precision,
                target_shape=det_shape,
                min_area_hectares=min_area,
                smoothing_iterations=smoothing,
            )

            # Create per-request detector to avoid race conditions on shared state
            from .agricultural_land_detector import AgriculturalLandDetector

            request_detector = AgriculturalLandDetector(
                config,
                multi_provider=land_detector.multi_provider if land_detector else None,
            )

            # Run detection
            report = await request_detector.detect_at_point(lat, lon, radius_m)

            # Convert to GeoJSON FeatureCollection
            features = [parcel.to_geojson() for parcel in report.parcels]

            return {
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "center": {"lat": lat, "lon": lon},
                    "radius_meters": radius_m,
                    "detection_date": datetime.now().isoformat(),
                    "strategy": report.strategy_used.value,
                    "precision": report.precision_level.value,
                    **report.to_dict(),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Parcel auto-generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "en": "Parcel detection failed. Please try again or adjust parameters.",
                    "ar": "فشل كشف القطع. يرجى المحاولة مرة أخرى أو تعديل المعلمات.",
                },
            ) from e

    @app.post("/v1/parcels/detect-region", response_model=dict)
    async def detect_parcels_in_region(request: RegionDetectionRequest, _user: User = Depends(get_current_user)):
        """
        Detect agricultural parcels in a geographic region.
        كشف القطع الزراعية في منطقة جغرافية محددة

        Provide bounding box coordinates to analyze a specific area.
        Similar to GeoLabel's "custom range" annotation mode.

        Example:
            POST /v1/parcels/detect-region
            Body: {
                "north": 15.6, "south": 15.4,
                "east": 44.3, "west": 44.1,
                "strategy": "hybrid"
            }
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            from .agricultural_land_detector import (
                AgriculturalLandDetector,
                DetectionConfig,
                DetectionStrategy,
                ModelPrecision,
            )

            bounds = {
                "north": request.north,
                "south": request.south,
                "east": request.east,
                "west": request.west,
            }

            # Validate bounds
            if request.north <= request.south:
                raise HTTPException(status_code=400, detail="North must be greater than south")
            if request.east <= request.west:
                raise HTTPException(status_code=400, detail="East must be greater than west")

            # Apply request config parameters
            try:
                det_strategy = DetectionStrategy(request.strategy)
            except ValueError:
                det_strategy = DetectionStrategy.HYBRID
            try:
                det_precision = ModelPrecision(request.precision)
            except ValueError:
                det_precision = ModelPrecision.HIGH

            config = DetectionConfig(
                strategy=det_strategy,
                precision=det_precision,
                min_area_hectares=request.min_area_hectares,
            )
            request_detector = AgriculturalLandDetector(
                config,
                multi_provider=land_detector.multi_provider if land_detector else None,
            )

            report = await request_detector.detect_in_region(bounds)

            features = [parcel.to_geojson() for parcel in report.parcels]

            return {
                "type": "FeatureCollection",
                "features": features,
                "metadata": {
                    "bounds": bounds,
                    "detection_date": datetime.now().isoformat(),
                    **report.to_dict(),
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Region detection failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/classify", response_model=dict)
    async def classify_parcels(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Classify existing vector parcels as agricultural/non-agricultural.
        تصنيف القطع المتجهة الموجودة كأراضي زراعية/غير زراعية

        Takes GeoJSON features and classifies them based on spectral
        and geometric characteristics.

        GeoLabel equivalent: Vector classification of farmland/non-farmland.

        Example:
            POST /v1/parcels/classify
            Body: {
                "parcels": [
                    {"type": "Feature", "geometry": {...}, "properties": {...}}
                ]
            }
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            from .agricultural_land_detector import (
                AgriculturalParcel,
                LandCoverClass,
            )

            # Convert GeoJSON to AgriculturalParcel objects
            parcels = []
            for feature in request.parcels:
                coords = feature.get("geometry", {}).get("coordinates", [[]])
                if coords and coords[0]:
                    coord_tuples = [(c[0], c[1]) for c in coords[0]]
                    props = feature.get("properties", {})

                    parcel = AgriculturalParcel(
                        parcel_id=props.get("parcel_id", f"parcel_{len(parcels)}"),
                        coordinates=coord_tuples,
                        area_hectares=props.get("area_hectares", 0),
                        perimeter_meters=props.get("perimeter_meters", 0),
                        centroid=(
                            sum(c[0] for c in coord_tuples) / len(coord_tuples),
                            sum(c[1] for c in coord_tuples) / len(coord_tuples),
                        ),
                        land_cover=LandCoverClass.UNKNOWN,
                        detection_confidence=0.0,
                        detection_date=datetime.now(),
                        strategy=land_detector.config.strategy,
                        mean_ndvi=props.get("mean_ndvi", 0.0),
                        mean_evi=props.get("mean_evi"),
                        mean_ndwi=props.get("mean_ndwi"),
                    )
                    parcels.append(parcel)

            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            # Classify
            classified = await land_detector.classifier.classify_parcels(parcels)

            # Build response
            features = [p.to_geojson() for p in classified]
            cropland = [p for p in classified if p.land_cover == LandCoverClass.CROPLAND]

            return {
                "type": "FeatureCollection",
                "features": features,
                "classification_summary": {
                    "total_parcels": len(classified),
                    "cropland": len(cropland),
                    "non_cropland": len(classified) - len(cropland),
                    "cropland_area_hectares": round(sum(p.area_hectares for p in cropland), 2),
                    "classification_method": "spectral_geometric_features",
                    "summary": {
                        "en": f"Classified {len(cropland)}/{len(classified)} parcels as agricultural land",
                        "ar": f"تم تصنيف {len(cropland)}/{len(classified)} قطعة كأرض زراعية",
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Parcel classification failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.get("/v1/parcels/strategies", response_model=dict)
    async def list_detection_strategies(_user: User = Depends(get_current_user)):
        """
        List available detection strategies and their descriptions.
        عرض استراتيجيات الكشف المتاحة ووصفها

        Returns information about each strategy inspired by GeoLabel.
        """
        return {
            "strategies": [
                {
                    "id": "hybrid",
                    "name": {"en": "Hybrid (Recommended)", "ar": "هجين (موصى به)"},
                    "description": {
                        "en": "Combines semantic segmentation and boundary detection for best results",
                        "ar": "يجمع بين التقسيم الدلالي وكشف الحدود للحصول على أفضل النتائج",
                    },
                    "accuracy": "highest",
                    "speed": "slowest",
                },
                {
                    "id": "semantic_segmentation",
                    "name": {"en": "Semantic Segmentation", "ar": "التقسيم الدلالي"},
                    "description": {
                        "en": "Pixel-level cropland classification using spectral indices",
                        "ar": "تصنيف الأراضي المزروعة على مستوى البكسل باستخدام المؤشرات الطيفية",
                    },
                    "accuracy": "high",
                    "speed": "medium",
                },
                {
                    "id": "boundary_detection",
                    "name": {"en": "Boundary Detection", "ar": "كشف الحدود"},
                    "description": {
                        "en": "Edge detection to find field boundaries, then close into parcels",
                        "ar": "كشف الحواف لإيجاد حدود الحقول ثم إغلاقها في قطع",
                    },
                    "accuracy": "high",
                    "speed": "medium",
                },
                {
                    "id": "training_free",
                    "name": {"en": "Training-Free", "ar": "بدون تدريب"},
                    "description": {
                        "en": "NDVI threshold-based detection, no model training needed",
                        "ar": "كشف بعتبة NDVI، لا حاجة لتدريب النماذج",
                    },
                    "accuracy": "moderate",
                    "speed": "fastest",
                },
            ],
            "precision_levels": [
                {
                    "id": "very_high",
                    "name": {"en": "Very High Precision", "ar": "دقة عالية جداً"},
                    "description": {
                        "en": "Best accuracy, slowest processing",
                        "ar": "أعلى دقة، أبطأ معالجة",
                    },
                },
                {
                    "id": "high",
                    "name": {
                        "en": "High Precision (Default)",
                        "ar": "دقة عالية (افتراضي)",
                    },
                    "description": {
                        "en": "Good balance of accuracy and speed",
                        "ar": "توازن جيد بين الدقة والسرعة",
                    },
                },
                {
                    "id": "acceptable",
                    "name": {"en": "Acceptable Precision", "ar": "دقة مقبولة"},
                    "description": {
                        "en": "Faster processing, adequate accuracy",
                        "ar": "معالجة أسرع، دقة مقبولة",
                    },
                },
                {
                    "id": "speed_focused",
                    "name": {"en": "Speed Focused", "ar": "التركيز على السرعة"},
                    "description": {
                        "en": "Fastest processing, basic accuracy",
                        "ar": "أسرع معالجة، دقة أساسية",
                    },
                },
            ],
            "shape_options": [
                {
                    "id": "irregular",
                    "name": {"en": "Irregular (Original)", "ar": "غير منتظم (أصلي)"},
                },
                {"id": "rectangle", "name": {"en": "Rectangle", "ar": "مستطيل"}},
                {"id": "convex_hull", "name": {"en": "Convex Hull", "ar": "غلاف محدب"}},
                {
                    "id": "minimum_bounding",
                    "name": {
                        "en": "Minimum Bounding Rectangle",
                        "ar": "أصغر مستطيل محيط",
                    },
                },
            ],
        }

    # =========================================================================
    # GeoLabel 4.0: Crop Classification Endpoint
    # =========================================================================

    @app.post("/v1/parcels/classify-crops", response_model=dict)
    async def classify_crops(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Classify crop types for parcels using ML+DL dual-path engine.
        تصنيف أنواع المحاصيل للقطع باستخدام محرك مزدوج (تعلم آلي + تعلم عميق)

        GeoLabel 4.0 equivalent: Scene classification + statistical classification
        Uses spectral profiles (NDVI, EVI, NDWI) + geometric features.

        Returns parcels with crop_type and classification confidence.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            from .agricultural_land_detector import (
                AgriculturalParcel,
                LandCoverClass,
            )

            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            # classify_crops returns CropClassificationResult list and updates parcels in-place
            await land_detector.crop_classifier.classify_crops(parcels)

            features = [p.to_geojson() for p in parcels]
            crop_stats = {}
            for p in parcels:
                ct = p.crop_type or "unknown"
                crop_stats[ct] = crop_stats.get(ct, 0) + 1

            return {
                "type": "FeatureCollection",
                "features": features,
                "classification_summary": {
                    "total_parcels": len(parcels),
                    "crop_distribution": crop_stats,
                    "method": "ml_dl_dual_path_ensemble",
                    "ml_weight": 0.4,
                    "dl_weight": 0.6,
                    "summary": {
                        "en": f"Classified {len(parcels)} parcels into {len(crop_stats)} crop types",
                        "ar": f"تم تصنيف {len(parcels)} قطعة إلى {len(crop_stats)} أنواع محاصيل",
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Crop classification failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    # =========================================================================
    # GeoLabel 4.0: Parcel Editing Endpoints (Merge / Split / Connect)
    # =========================================================================

    @app.post("/v1/parcels/merge", response_model=dict)
    async def merge_parcels(request: ParcelMergeRequest, _user: User = Depends(get_current_user)):
        """
        Merge multiple parcels into one (GeoLabel fast merge).
        دمج عدة قطع في قطعة واحدة (دمج سريع GeoLabel)

        Uses convex hull merge with weighted spectral property preservation.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if len(parcels) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 parcels to merge")

            parcel_ids = request.parcel_ids or [p.parcel_id for p in parcels]
            merged = land_detector.editing_tools.merge_parcels(parcels, parcel_ids)

            return {
                "merged_parcel": merged.to_geojson(),
                "merge_stats": {
                    "input_parcels": len(parcels),
                    "merged_area_hectares": round(merged.area_hectares, 2),
                    "merged_vertices": merged.num_vertices,
                    "summary": {
                        "en": f"Merged {len(parcels)} parcels into 1 ({merged.area_hectares:.2f} ha)",
                        "ar": f"تم دمج {len(parcels)} قطع في قطعة واحدة ({merged.area_hectares:.2f} هكتار)",
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Parcel merge failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/split", response_model=dict)
    async def split_parcel(request: ParcelSplitRequest, _user: User = Depends(get_current_user)):
        """
        Split a parcel along a cutting line (GeoLabel fast split).
        تقسيم قطعة على طول خط القطع (تقسيم سريع GeoLabel)

        The cutting line must intersect the parcel boundary at 2+ points.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels([request.parcel], land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="Invalid parcel")

            cutting_line = [(c[0], c[1]) for c in request.cutting_line]
            if len(cutting_line) < 2:
                raise HTTPException(status_code=400, detail="Cutting line needs at least 2 points")

            result_parcels = land_detector.editing_tools.split_parcel(parcels[0], cutting_line)
            features = [p.to_geojson() for p in result_parcels]

            return {
                "type": "FeatureCollection",
                "features": features,
                "split_stats": {
                    "input_area_hectares": round(parcels[0].area_hectares, 2),
                    "output_parcels": len(result_parcels),
                    "output_areas": [round(p.area_hectares, 2) for p in result_parcels],
                    "summary": {
                        "en": f"Split into {len(result_parcels)} parcels",
                        "ar": f"تم التقسيم إلى {len(result_parcels)} قطع",
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Parcel split failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/connect", response_model=dict)
    async def connect_parcels(request: ParcelConnectRequest, _user: User = Depends(get_current_user)):
        """
        Connect nearby parcel fragments (GeoLabel fast connect).
        ربط أجزاء القطع القريبة (ربط سريع GeoLabel)

        Bridges gaps between fragments within max_gap_meters distance.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if len(parcels) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 parcels to connect")

            parcel_ids = [p.parcel_id for p in parcels]
            connected = land_detector.editing_tools.connect_parcels(
                parcels, parcel_ids, max_gap_meters=request.max_gap_meters
            )

            if connected:
                return {
                    "connected_parcel": connected.to_geojson(),
                    "connect_stats": {
                        "input_fragments": len(parcels),
                        "max_gap_meters": request.max_gap_meters,
                        "connected_area_hectares": round(connected.area_hectares, 2),
                        "summary": {
                            "en": f"Connected {len(parcels)} fragments into 1 parcel",
                            "ar": f"تم ربط {len(parcels)} جزء في قطعة واحدة",
                        },
                    },
                }
            else:
                raise HTTPException(status_code=400, detail="Could not connect parcels")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Parcel connect failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    # =========================================================================
    # GeoLabel 4.0: Quality Inspection & WKT Export
    # =========================================================================

    @app.post("/v1/parcels/inspect", response_model=dict)
    async def inspect_parcels(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Run quality inspection on parcels (GeoLabel quality browser).
        فحص جودة القطع (متصفح جودة GeoLabel)

        Checks: min area (50m²), min vertices (3), compactness,
        elongation (<50), self-intersection, closure, confidence.
        Returns quality issues for each parcel.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            result = land_detector.quality_inspector.inspect_all(parcels)
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Quality inspection failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/export-wkt", response_model=dict)
    async def export_wkt(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Export parcels as WKT (Well-Known Text) format.
        تصدير القطع بتنسيق WKT

        GeoLabel equivalent: Feature quick browser → WKT export.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            wkt_list = []
            for parcel in parcels:
                wkt = land_detector.quality_inspector.parcel_to_wkt(parcel)
                wkt_list.append(
                    {
                        "parcel_id": parcel.parcel_id,
                        "wkt": wkt,
                        "area_hectares": parcel.area_hectares,
                    }
                )

            collection_wkt = land_detector.quality_inspector.parcels_to_wkt_collection(parcels)

            return {
                "parcels_wkt": wkt_list,
                "collection_wkt": collection_wkt,
                "total_parcels": len(parcels),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"WKT export failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/batch-assign", response_model=dict)
    async def batch_assign_attribute(request: BatchAssignRequest, _user: User = Depends(get_current_user)):
        """
        Batch assign attribute to multiple parcels (GeoLabel attribute brush).
        تعيين سمة مجمّعة لعدة قطع (فرشاة السمات GeoLabel)

        Supports: crop_type, land_cover, is_irrigated.
        GeoLabel equivalent: 8-class land cover attribute assignment brush.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            valid_attributes = {"crop_type", "land_cover", "is_irrigated"}
            if request.attribute not in valid_attributes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid attribute. Must be one of: {', '.join(valid_attributes)}",
                )

            # Parse value for is_irrigated
            value = request.value
            if request.attribute == "is_irrigated":
                value = request.value.lower() in ("true", "1", "yes")

            parcel_ids = request.parcel_ids or [p.parcel_id for p in parcels]
            count = land_detector.quality_inspector.batch_assign_attribute(
                parcels, parcel_ids, request.attribute, value
            )
            features = [p.to_geojson() for p in parcels]

            return {
                "type": "FeatureCollection",
                "features": features,
                "update_summary": {
                    "parcels_updated": count,
                    "attribute": request.attribute,
                    "value": request.value,
                    "summary": {
                        "en": f"Updated {request.attribute}={request.value} for {count} parcels",
                        "ar": f"تم تحديث {request.attribute}={request.value} لـ {count} قطعة",
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Batch assign failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    @app.post("/v1/parcels/statistics", response_model=dict)
    async def get_parcel_statistics(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Get statistical summary of parcels.
        الحصول على ملخص إحصائي للقطع

        Returns area statistics, crop distribution, and land cover distribution.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            stats = land_detector.quality_inspector.get_statistics(parcels)
            return stats

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    # =========================================================================
    # GeoLabel 4.0: Topology-Preserving Simplification
    # =========================================================================

    @app.post("/v1/parcels/simplify-topology", response_model=dict)
    async def simplify_with_topology(request: ParcelClassifyRequest, _user: User = Depends(get_current_user)):
        """
        Simplify parcel boundaries while preserving topology.
        تبسيط حدود القطع مع الحفاظ على الطوبولوجيا

        GeoLabel equivalent: Topology-preserving boundary simplification.
        Ensures no gaps or overlaps between adjacent parcels after simplification.
        """
        if not land_detector:
            raise HTTPException(
                status_code=503,
                detail={
                    "en": "Agricultural land detector not initialized",
                    "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
                },
            )

        try:
            parcels = _geojson_to_parcels(request.parcels, land_detector)
            if not parcels:
                raise HTTPException(status_code=400, detail="No valid parcels provided")

            simplified = land_detector.topology_simplifier.simplify_with_topology(parcels)
            features = [p.to_geojson() for p in simplified]

            original_vertices = sum(len(p.coordinates) for p in parcels)
            simplified_vertices = sum(len(p.coordinates) for p in simplified)

            return {
                "type": "FeatureCollection",
                "features": features,
                "simplification_stats": {
                    "total_parcels": len(simplified),
                    "original_vertices": original_vertices,
                    "simplified_vertices": simplified_vertices,
                    "reduction_percent": (
                        round((1 - simplified_vertices / original_vertices) * 100, 1) if original_vertices > 0 else 0
                    ),
                    "topology_preserved": True,
                    "summary": {
                        "en": (
                            f"Simplified {len(simplified)} parcels: {original_vertices}→{simplified_vertices} vertices"
                        ),
                        "ar": (f"تم تبسيط {len(simplified)} قطعة: {original_vertices}→{simplified_vertices} رأس"),
                    },
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Topology simplification failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error") from e

    logger.info("Agricultural parcel detection endpoints registered (with GeoLabel 4.0)")


def _geojson_to_parcels(features: list[dict], land_detector) -> list:
    """
    Convert GeoJSON features to AgriculturalParcel objects.
    تحويل عناصر GeoJSON إلى كائنات AgriculturalParcel

    Helper function shared by all GeoLabel 4.0 endpoints.
    """
    from .agricultural_land_detector import (
        AgriculturalParcel,
        LandCoverClass,
    )

    parcels = []
    for feature in features:
        coords = feature.get("geometry", {}).get("coordinates", [[]])
        if coords and coords[0]:
            coord_tuples = [(c[0], c[1]) for c in coords[0]]
            props = feature.get("properties", {})

            # Parse land_cover
            try:
                land_cover = LandCoverClass(props.get("land_cover", "unknown"))
            except ValueError:
                land_cover = LandCoverClass.UNKNOWN

            parcel = AgriculturalParcel(
                parcel_id=props.get("parcel_id", f"parcel_{len(parcels)}"),
                coordinates=coord_tuples,
                area_hectares=props.get("area_hectares", 0),
                perimeter_meters=props.get("perimeter_meters", 0),
                centroid=(
                    sum(c[0] for c in coord_tuples) / len(coord_tuples),
                    sum(c[1] for c in coord_tuples) / len(coord_tuples),
                ),
                land_cover=land_cover,
                detection_confidence=props.get("detection_confidence", 0.0),
                detection_date=datetime.now(),
                strategy=land_detector.config.strategy,
                mean_ndvi=props.get("mean_ndvi", 0.0),
                mean_evi=props.get("mean_evi"),
                mean_ndwi=props.get("mean_ndwi"),
                ndvi_std=props.get("ndvi_std"),
                compactness=props.get("compactness"),
                elongation=props.get("elongation"),
                rectangularity=props.get("rectangularity"),
                num_vertices=len(coord_tuples),
                crop_type=props.get("crop_type"),
                is_irrigated=props.get("is_irrigated"),
                quality_score=props.get("quality_score"),
            )
            parcels.append(parcel)
    return parcels
