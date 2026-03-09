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

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

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
    precision: str = Field("high", description="Model precision: very_high, high, acceptable, speed_focused")
    target_shape: str = Field("irregular", description="Shape regularization: irregular, rectangle, convex_hull, minimum_bounding")
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

    parcels: list[dict] = Field(
        ..., description="List of GeoJSON features to classify"
    )


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
            raise HTTPException(status_code=503, detail={
                "en": "Agricultural land detector not initialized",
                "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
            })

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

            # Update detector config
            land_detector.config = config
            land_detector.segmentation.config = config
            land_detector.boundary_detection.config = config
            land_detector.post_processor.config = config

            # Run detection
            report = await land_detector.detect_at_point(lat, lon, radius_m)

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
            logger.error(f"Parcel auto-generation failed: {e}")
            raise HTTPException(status_code=500, detail={
                "en": f"Parcel detection failed: {str(e)}",
                "ar": f"فشل كشف القطع: {str(e)}",
            }) from e

    @app.post("/v1/parcels/detect-region", response_model=dict)
    async def detect_parcels_in_region(request: RegionDetectionRequest):
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
            raise HTTPException(status_code=503, detail={
                "en": "Agricultural land detector not initialized",
                "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
            })

        try:
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

            report = await land_detector.detect_in_region(bounds)

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
            logger.error(f"Region detection failed: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.post("/v1/parcels/classify", response_model=dict)
    async def classify_parcels(request: ParcelClassifyRequest):
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
            raise HTTPException(status_code=503, detail={
                "en": "Agricultural land detector not initialized",
                "ar": "لم يتم تهيئة كاشف الأراضي الزراعية",
            })

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
            logger.error(f"Parcel classification failed: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    @app.get("/v1/parcels/strategies", response_model=dict)
    async def list_detection_strategies():
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
                    "description": {"en": "Best accuracy, slowest processing", "ar": "أعلى دقة، أبطأ معالجة"},
                },
                {
                    "id": "high",
                    "name": {"en": "High Precision (Default)", "ar": "دقة عالية (افتراضي)"},
                    "description": {"en": "Good balance of accuracy and speed", "ar": "توازن جيد بين الدقة والسرعة"},
                },
                {
                    "id": "acceptable",
                    "name": {"en": "Acceptable Precision", "ar": "دقة مقبولة"},
                    "description": {"en": "Faster processing, adequate accuracy", "ar": "معالجة أسرع، دقة مقبولة"},
                },
                {
                    "id": "speed_focused",
                    "name": {"en": "Speed Focused", "ar": "التركيز على السرعة"},
                    "description": {"en": "Fastest processing, basic accuracy", "ar": "أسرع معالجة، دقة أساسية"},
                },
            ],
            "shape_options": [
                {"id": "irregular", "name": {"en": "Irregular (Original)", "ar": "غير منتظم (أصلي)"}},
                {"id": "rectangle", "name": {"en": "Rectangle", "ar": "مستطيل"}},
                {"id": "convex_hull", "name": {"en": "Convex Hull", "ar": "غلاف محدب"}},
                {"id": "minimum_bounding", "name": {"en": "Minimum Bounding Rectangle", "ar": "أصغر مستطيل محيط"}},
            ],
        }

    logger.info("Agricultural parcel detection endpoints registered")
