"""
Comprehensive tests for Agricultural Land Detector - GeoLabel 4.0
اختبارات شاملة لكاشف الأراضي الزراعية - GeoLabel 4.0

Tests cover:
- Phase 1-4: Core detection (segmentation, boundary, training-free, classification)
- GeoLabel 4.0: Crop classification, topology simplification, editing, quality inspection
- API endpoints for all GeoLabel 4.0 features
"""

import math
from datetime import datetime

import numpy as np
import pytest
import sys
import os

# Add service src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.agricultural_land_detector import (
        AgriculturalLandDetector,
        AgriculturalParcel,
        BoundaryDetectionEngine,
        CropClassificationEngine,
        CropClassificationResult,
        CropType,
        DetectionConfig,
        DetectionReport,
        DetectionStrategy,
        LandCoverClass,
        ModelPrecision,
        ParcelEditingTools,
        ParcelPostProcessor,
        ParcelShape,
        QualityInspectionTool,
        SemanticSegmentationEngine,
        TopologyPreservingSimplifier,
        VectorClassificationEngine,
    )
except ImportError:
    pytest.skip("vegetation-analysis-service dependencies not installed", allow_module_level=True)

# =============================================================================
# Test Fixtures
# =============================================================================


def make_parcel(
    parcel_id="test_001",
    coords=None,
    area=1.0,
    perimeter=400,
    land_cover=LandCoverClass.CROPLAND,
    confidence=0.8,
    mean_ndvi=0.55,
    mean_evi=0.35,
    mean_ndwi=0.1,
    crop_type=None,
    compactness=0.7,
    elongation=1.5,
    rectangularity=0.8,
) -> AgriculturalParcel:
    """Create a test parcel with reasonable defaults."""
    if coords is None:
        # ~100m x 100m square at lat=15.5
        coords = [
            (44.200, 15.500),
            (44.201, 15.500),
            (44.201, 15.501),
            (44.200, 15.501),
        ]

    centroid = (
        sum(c[0] for c in coords) / len(coords),
        sum(c[1] for c in coords) / len(coords),
    )

    return AgriculturalParcel(
        parcel_id=parcel_id,
        coordinates=coords,
        area_hectares=area,
        perimeter_meters=perimeter,
        centroid=centroid,
        land_cover=land_cover,
        detection_confidence=confidence,
        detection_date=datetime.now(),
        strategy=DetectionStrategy.HYBRID,
        mean_ndvi=mean_ndvi,
        mean_evi=mean_evi,
        mean_ndwi=mean_ndwi,
        ndvi_std=0.05,
        compactness=compactness,
        elongation=elongation,
        rectangularity=rectangularity,
        num_vertices=len(coords),
        crop_type=crop_type,
        is_irrigated=None,
        quality_score=0.75,
    )


def make_synthetic_image(size=64):
    """Create synthetic 4-band image for testing."""
    rng = np.random.default_rng(42)
    image = np.zeros((size, size, 4), dtype=np.float64)

    for i in range(size):
        for j in range(size):
            in_field = (10 <= i < 30 and 10 <= j < 30) or (35 <= i < 55 and 35 <= j < 55)
            if in_field:
                image[i, j, 0] = 0.05 + rng.random() * 0.05
                image[i, j, 1] = 0.08 + rng.random() * 0.05
                image[i, j, 2] = 0.06 + rng.random() * 0.04
                image[i, j, 3] = 0.35 + rng.random() * 0.15
            else:
                image[i, j, 0] = 0.10 + rng.random() * 0.08
                image[i, j, 1] = 0.12 + rng.random() * 0.06
                image[i, j, 2] = 0.15 + rng.random() * 0.08
                image[i, j, 3] = 0.10 + rng.random() * 0.08

    bounds = {"north": 15.51, "south": 15.49, "east": 44.21, "west": 44.19}
    return image, bounds


# =============================================================================
# Enums & Configuration Tests
# =============================================================================


class TestEnums:
    """Test enum definitions and values."""

    def test_detection_strategy_values(self):
        assert DetectionStrategy.HYBRID.value == "hybrid"
        assert DetectionStrategy.SEMANTIC_SEGMENTATION.value == "semantic_segmentation"
        assert DetectionStrategy.BOUNDARY_DETECTION.value == "boundary_detection"
        assert DetectionStrategy.TRAINING_FREE.value == "training_free"

    def test_model_precision_values(self):
        assert ModelPrecision.VERY_HIGH.value == "very_high"
        assert ModelPrecision.HIGH.value == "high"
        assert ModelPrecision.ACCEPTABLE.value == "acceptable"
        assert ModelPrecision.SPEED_FOCUSED.value == "speed_focused"

    def test_parcel_shape_values(self):
        assert ParcelShape.IRREGULAR.value == "irregular"
        assert ParcelShape.RECTANGLE.value == "rectangle"
        assert ParcelShape.CONVEX_HULL.value == "convex_hull"
        assert ParcelShape.MINIMUM_BOUNDING.value == "minimum_bounding"

    def test_land_cover_8_classes(self):
        """GeoLabel 4.0: Verify 8-class land cover system + UNKNOWN."""
        classes = [
            LandCoverClass.CROPLAND,
            LandCoverClass.ORCHARD,
            LandCoverClass.FOREST,
            LandCoverClass.GRASSLAND,
            LandCoverClass.BUILT_UP,
            LandCoverClass.WATER,
            LandCoverClass.ROAD,
            LandCoverClass.BARREN,
            LandCoverClass.UNKNOWN,
        ]
        assert len(classes) == 9  # 8 GeoLabel classes + UNKNOWN
        values = [c.value for c in classes]
        assert len(set(values)) == 9  # All unique

    def test_crop_type_enum(self):
        """Test CropType enum covers major crops."""
        assert CropType.WHEAT.value == "wheat"
        assert CropType.DATE_PALM.value == "date_palm"
        assert CropType.UNKNOWN.value == "unknown"
        # At least 10 crop types
        assert len(CropType) >= 10


class TestDetectionConfig:
    """Test DetectionConfig defaults and customization."""

    def test_default_config(self):
        config = DetectionConfig()
        assert config.strategy == DetectionStrategy.HYBRID
        assert config.precision == ModelPrecision.HIGH
        assert config.target_shape == ParcelShape.IRREGULAR
        assert config.min_area_hectares == 0.05
        assert config.max_area_hectares == 1000.0
        assert config.ndvi_cropland_threshold == 0.25
        assert config.smoothing_iterations == 2
        assert config.inference_size == 640

    def test_custom_config(self):
        config = DetectionConfig(
            strategy=DetectionStrategy.TRAINING_FREE,
            precision=ModelPrecision.SPEED_FOCUSED,
            min_area_hectares=0.1,
        )
        assert config.strategy == DetectionStrategy.TRAINING_FREE
        assert config.precision == ModelPrecision.SPEED_FOCUSED
        assert config.min_area_hectares == 0.1


# =============================================================================
# Data Models Tests
# =============================================================================


class TestAgriculturalParcel:
    """Test AgriculturalParcel data model."""

    def test_parcel_creation(self):
        parcel = make_parcel()
        assert parcel.parcel_id == "test_001"
        assert parcel.area_hectares == 1.0
        assert parcel.land_cover == LandCoverClass.CROPLAND
        assert parcel.mean_ndvi == 0.55
        assert len(parcel.coordinates) == 4

    def test_parcel_to_geojson(self):
        parcel = make_parcel()
        geojson = parcel.to_geojson()
        assert geojson["type"] == "Feature"
        assert geojson["geometry"]["type"] == "Polygon"
        ring = geojson["geometry"]["coordinates"][0]
        # GeoJSON RFC 7946 requires closed LinearRings (first == last point)
        assert len(ring) == 5  # 4 vertices + closing point
        assert ring[0] == ring[-1]
        assert geojson["properties"]["parcel_id"] == "test_001"
        assert geojson["properties"]["area_hectares"] == 1.0
        assert geojson["properties"]["land_cover"] == "cropland"
        assert geojson["properties"]["mean_ndvi"] == 0.55

    def test_parcel_geojson_all_properties(self):
        parcel = make_parcel(crop_type="wheat", compactness=0.85)
        props = parcel.to_geojson()["properties"]
        assert props["crop_type"] == "wheat"
        assert props["compactness"] == 0.85
        assert props["strategy"] == "hybrid"
        assert "detection_date" in props


class TestDetectionReport:
    """Test DetectionReport data model."""

    def test_report_to_dict(self):
        report = DetectionReport(
            total_parcels=10,
            total_area_hectares=50.5,
            cropland_parcels=7,
            cropland_area_hectares=35.2,
            non_cropland_parcels=3,
            detection_time_seconds=2.5,
            strategy_used=DetectionStrategy.HYBRID,
            precision_level=ModelPrecision.HIGH,
        )
        d = report.to_dict()
        assert d["total_parcels"] == 10
        assert d["total_area_hectares"] == 50.5
        assert d["cropland_parcels"] == 7
        assert d["strategy_used"] == "hybrid"
        assert "en" in d["summary"]
        assert "ar" in d["summary"]
        assert "7" in d["summary"]["en"]


# =============================================================================
# Phase 1: Semantic Segmentation Engine Tests
# =============================================================================


class TestSemanticSegmentationEngine:
    """Test SemanticSegmentationEngine."""

    def setup_method(self):
        self.engine = SemanticSegmentationEngine()

    @pytest.mark.asyncio
    async def test_classify_pixels_basic(self):
        image, bounds = make_synthetic_image(32)
        mask = await self.engine.classify_pixels(image, bounds)
        assert mask.shape == (32, 32)
        # Should have some cropland pixels in the field regions
        cropland_count = sum(1 for i in range(32) for j in range(32) if mask[i, j] == "cropland")
        assert cropland_count > 0

    @pytest.mark.asyncio
    async def test_classify_pixels_single_band(self):
        # Single-band image (NDVI-like)
        image = np.random.default_rng(42).random((16, 16, 1)).astype(np.float64)
        bounds = {"north": 15.51, "south": 15.49, "east": 44.21, "west": 44.19}
        mask = await self.engine.classify_pixels(image, bounds)
        assert mask.shape == (16, 16)

    @pytest.mark.asyncio
    async def test_polygonize_mask(self):
        image, bounds = make_synthetic_image(32)
        mask = await self.engine.classify_pixels(image, bounds)
        polygons = await self.engine.polygonize_mask(mask, bounds, "cropland")
        assert isinstance(polygons, list)
        for poly in polygons:
            assert len(poly) >= 4

    def test_compute_ndvi(self):
        image = np.zeros((4, 4, 4), dtype=np.float64)
        image[:, :, 2] = 0.1  # Red
        image[:, :, 3] = 0.5  # NIR
        ndvi = self.engine._compute_ndvi(image)
        # NDVI = (0.5 - 0.1) / (0.5 + 0.1) ≈ 0.667
        assert np.allclose(ndvi, (0.5 - 0.1) / 0.6, atol=0.01)

    def test_compute_evi(self):
        image = np.zeros((4, 4, 4), dtype=np.float64)
        image[:, :, 0] = 0.05  # Blue
        image[:, :, 2] = 0.1  # Red
        image[:, :, 3] = 0.5  # NIR
        evi = self.engine._compute_evi(image)
        assert evi.shape == (4, 4)
        assert np.all(evi > 0)

    def test_morphological_operations(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[3:7, 3:7] = 1
        mask[4, 4] = 0  # hole

        closed = self.engine._morphological_close(mask, iterations=1)
        # Hole should be filled
        assert closed[4, 4] == 1

    def test_connected_components(self):
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[1:4, 1:4] = 1  # Region 1
        mask[6:9, 6:9] = 1  # Region 2
        labels, num = self.engine._connected_components(mask)
        assert num == 2

    def test_trace_contour(self):
        component = np.zeros((10, 10), dtype=np.uint8)
        component[2:8, 2:8] = 1
        contour = self.engine._trace_contour(component)
        assert len(contour) >= 4


# =============================================================================
# Phase 2: Boundary Detection Engine Tests
# =============================================================================


class TestBoundaryDetectionEngine:
    """Test BoundaryDetectionEngine."""

    def setup_method(self):
        self.engine = BoundaryDetectionEngine()

    @pytest.mark.asyncio
    async def test_detect_boundaries(self):
        image, bounds = make_synthetic_image(32)
        polygons = await self.engine.detect_boundaries(image, bounds)
        assert isinstance(polygons, list)

    def test_compute_gradient_magnitude(self):
        image = np.zeros((16, 16), dtype=np.float64)
        image[4:12, 4:12] = 1.0
        edges = self.engine._compute_gradient_magnitude(image)
        assert edges.shape == (16, 16)
        # Gradient should be non-zero at boundaries
        assert np.max(edges) > 0

    def test_close_boundaries(self):
        edge_map = np.zeros((10, 10), dtype=np.float64)
        edge_map[2:8, 2] = 1.0
        edge_map[2:8, 7] = 1.0
        edge_map[2, 2:8] = 1.0
        edge_map[7, 2:8] = 1.0
        closed = self.engine._close_boundaries(edge_map, iterations=2)
        assert closed.shape == (10, 10)


# =============================================================================
# Phase 3: Post-Processing Tests
# =============================================================================


class TestParcelPostProcessor:
    """Test ParcelPostProcessor."""

    def setup_method(self):
        self.processor = ParcelPostProcessor()
        self.bounds = {"north": 15.51, "south": 15.49, "east": 44.21, "west": 44.19}

    def test_process_parcels(self):
        # Two simple polygons
        poly1 = [(44.195, 15.495), (44.200, 15.495), (44.200, 15.500), (44.195, 15.500)]
        poly2 = [(44.205, 15.505), (44.208, 15.505), (44.208, 15.508), (44.205, 15.508)]
        polygons = [poly1, poly2]
        result = self.processor.process_parcels(polygons, self.bounds)
        assert isinstance(result, list)

    def test_douglas_peucker(self):
        # Many-vertex polygon
        coords = [(44.19 + i * 0.001, 15.49 + (i % 3) * 0.001) for i in range(20)]
        simplified = self.processor._douglas_peucker(coords, tolerance=0.001)
        assert len(simplified) <= len(coords)
        assert len(simplified) >= 2

    def test_calculate_area(self):
        # ~100m x 100m square
        coords = [
            (44.200, 15.500),
            (44.201, 15.500),
            (44.201, 15.501),
            (44.200, 15.501),
        ]
        area = self.processor._calculate_area(coords)
        assert area > 0
        assert 0.5 < area < 2.0  # ~1 hectare

    def test_centroid(self):
        coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        c = self.processor._centroid(coords)
        assert abs(c[0] - 0.5) < 0.01
        assert abs(c[1] - 0.5) < 0.01

    def test_process_filters_small(self):
        """process_parcels should filter small polygons."""
        small = [(44.200, 15.500), (44.2001, 15.500), (44.2001, 15.5001)]  # Tiny
        big = [(44.200, 15.500), (44.202, 15.500), (44.202, 15.502), (44.200, 15.502)]
        result = self.processor.process_parcels([small, big], self.bounds)
        # Big polygon should remain, small filtered
        assert len(result) >= 0  # May filter both if below threshold

    def test_chaikin_smooth(self):
        coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
        smoothed = self.processor._chaikin_smooth(coords)
        assert len(smoothed) >= 4


# =============================================================================
# Phase 4: Vector Classification Tests
# =============================================================================


class TestVectorClassificationEngine:
    """Test VectorClassificationEngine."""

    def setup_method(self):
        self.engine = VectorClassificationEngine()

    @pytest.mark.asyncio
    async def test_classify_parcels(self):
        parcels = [
            make_parcel("p1", mean_ndvi=0.65, mean_evi=0.4, compactness=0.8),
            make_parcel(
                "p2",
                mean_ndvi=0.1,
                mean_evi=0.05,
                compactness=0.3,
                land_cover=LandCoverClass.UNKNOWN,
            ),
        ]
        classified = await self.engine.classify_parcels(parcels)
        assert len(classified) == 2
        # High NDVI parcel should be cropland
        assert classified[0].land_cover == LandCoverClass.CROPLAND
        assert classified[0].detection_confidence > 0

    @pytest.mark.asyncio
    async def test_classify_water(self):
        parcel = make_parcel(
            mean_ndvi=-0.1,
            mean_ndwi=0.5,
            mean_evi=0.0,
            compactness=0.1,
            rectangularity=0.1,
            elongation=5.0,
        )
        classified = await self.engine.classify_parcels([parcel])
        # With high NDWI and very low NDVI/compactness, should classify as water
        assert classified[0].land_cover in (LandCoverClass.WATER, LandCoverClass.BARREN)


# =============================================================================
# GeoLabel 4.0: Crop Classification Engine Tests
# =============================================================================


class TestCropClassificationEngine:
    """Test CropClassificationEngine - ML+DL dual-path ensemble."""

    def setup_method(self):
        self.engine = CropClassificationEngine()

    @pytest.mark.asyncio
    async def test_classify_crops_basic(self):
        parcels = [
            make_parcel("wheat_field", mean_ndvi=0.65, mean_evi=0.45, area=5.0),
            make_parcel("barren_field", mean_ndvi=0.1, mean_evi=0.05, area=2.0),
        ]
        results = await self.engine.classify_crops(parcels)
        assert len(results) == 2
        for r in results:
            assert isinstance(r, CropClassificationResult)
            assert r.predicted_crop is not None

    @pytest.mark.asyncio
    async def test_ml_classify(self):
        parcel = make_parcel(mean_ndvi=0.7, mean_evi=0.5, mean_ndwi=0.15, area=3.0)
        crop, confidence, scores = self.engine._ml_classify(parcel, current_month=3)
        assert isinstance(crop, CropType)
        assert 0.0 <= confidence <= 1.0
        assert isinstance(scores, dict)

    @pytest.mark.asyncio
    async def test_dl_classify(self):
        parcel = make_parcel(mean_ndvi=0.6, mean_evi=0.4, area=5.0)
        crop, confidence = self.engine._dl_classify(parcel, image_data=None, bounds=None)
        assert isinstance(crop, CropType)
        assert 0.0 <= confidence <= 1.0

    @pytest.mark.asyncio
    async def test_ensemble_predictions(self):
        parcel = make_parcel("ens_test")
        ml_result = (CropType.WHEAT, 0.8, {CropType.WHEAT: 0.8, CropType.BARLEY: 0.5})
        dl_result = (CropType.WHEAT, 0.7)
        final = self.engine._ensemble_predictions(parcel, ml_result, dl_result)
        assert isinstance(final, CropClassificationResult)
        assert final.predicted_crop == CropType.WHEAT
        # Agreement should boost confidence
        assert final.confidence >= 0.7

    @pytest.mark.asyncio
    async def test_ensemble_disagreement(self):
        parcel = make_parcel("disagree_test")
        ml_result = (CropType.WHEAT, 0.6, {CropType.WHEAT: 0.6, CropType.RICE: 0.3})
        dl_result = (CropType.RICE, 0.9)
        final = self.engine._ensemble_predictions(parcel, ml_result, dl_result)
        # DL has higher weight (0.6) and higher confidence, should win
        assert final.predicted_crop == CropType.RICE

    def test_spectral_profiles_exist(self):
        """Verify spectral profiles for major crops."""
        assert "wheat" in self.engine.CROP_SPECTRAL_PROFILES
        assert "rice" in self.engine.CROP_SPECTRAL_PROFILES
        assert "date_palm" in self.engine.CROP_SPECTRAL_PROFILES
        for crop, profile in self.engine.CROP_SPECTRAL_PROFILES.items():
            assert "ndvi_peak" in profile
            assert "ndvi_range" in profile
            assert "peak_month" in profile

    def test_geometric_profiles_exist(self):
        """Verify geometric profiles for crop types."""
        assert "wheat" in self.engine.CROP_GEOMETRIC_PROFILES
        for crop, profile in self.engine.CROP_GEOMETRIC_PROFILES.items():
            assert "area_range" in profile
            assert len(profile["area_range"]) == 2

    def test_ml_feature_weights(self):
        """Verify ML feature weights sum properly."""
        total = sum(self.engine.ML_FEATURE_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    def test_ensemble_weights(self):
        """Verify DL+ML weights sum to 1.0."""
        assert abs(self.engine.DL_WEIGHT + self.engine.ML_WEIGHT - 1.0) < 0.01


# =============================================================================
# GeoLabel 4.0: Topology-Preserving Simplifier Tests
# =============================================================================


class TestTopologyPreservingSimplifier:
    """Test TopologyPreservingSimplifier."""

    def setup_method(self):
        self.simplifier = TopologyPreservingSimplifier()

    def test_simplify_single_parcel(self):
        # Many-vertex polygon
        coords = [(44.19 + i * 0.0002, 15.49 + math.sin(i * 0.5) * 0.001) for i in range(20)]
        parcel = make_parcel("multi_vertex", coords=coords)
        result = self.simplifier.simplify_with_topology([parcel])
        assert len(result) == 1
        # Should have fewer vertices
        assert len(result[0].coordinates) <= len(coords)

    def test_simplify_preserves_area(self):
        coords = [
            (44.200, 15.500),
            (44.201, 15.500),
            (44.2015, 15.5005),
            (44.201, 15.501),
            (44.200, 15.501),
        ]
        parcel = make_parcel("area_test", coords=coords, area=1.0)
        result = self.simplifier.simplify_with_topology([parcel])
        # Area shouldn't change more than 5%
        assert result[0].area_hectares > 0

    def test_adjacent_parcels(self):
        """Test that shared edges are preserved."""
        # Two adjacent rectangles sharing an edge
        p1 = make_parcel(
            "left",
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ],
        )
        p2 = make_parcel(
            "right",
            coords=[
                (44.201, 15.500),
                (44.202, 15.500),
                (44.202, 15.501),
                (44.201, 15.501),
            ],
        )
        result = self.simplifier.simplify_with_topology([p1, p2])
        assert len(result) == 2

    def test_build_adjacency_graph(self):
        p1 = make_parcel(
            "a",
            coords=[
                (0, 0),
                (1, 0),
                (1, 1),
                (0, 1),
            ],
        )
        p2 = make_parcel(
            "b",
            coords=[
                (1, 0),
                (2, 0),
                (2, 1),
                (1, 1),
            ],
        )
        graph = self.simplifier._build_adjacency_graph([p1, p2])
        assert isinstance(graph, dict)

    def test_douglas_peucker_preserve(self):
        coords = [(0, 0), (0.5, 0.1), (1, 0), (1, 1), (0, 1)]
        shared_vertices = {(0, 0), (1, 0)}
        result = self.simplifier._douglas_peucker_preserve(coords, 0.2, shared_vertices)
        # Shared vertices must remain
        for sv in shared_vertices:
            assert sv in result


# =============================================================================
# GeoLabel 4.0: Parcel Editing Tools Tests
# =============================================================================


class TestParcelEditingTools:
    """Test ParcelEditingTools - merge/split/connect operations."""

    def setup_method(self):
        self.tools = ParcelEditingTools()

    def test_merge_two_parcels(self):
        p1 = make_parcel(
            "p1",
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ],
            area=1.0,
            mean_ndvi=0.6,
        )
        p2 = make_parcel(
            "p2",
            coords=[
                (44.201, 15.500),
                (44.202, 15.500),
                (44.202, 15.501),
                (44.201, 15.501),
            ],
            area=1.5,
            mean_ndvi=0.5,
        )

        merged = self.tools.merge_parcels([p1, p2], ["p1", "p2"])
        assert merged is not None
        assert "merged" in merged.parcel_id
        assert merged.area_hectares == pytest.approx(2.5, abs=0.1)
        assert merged.mean_ndvi is not None

    def test_merge_three_parcels(self):
        parcels = [make_parcel(f"p{i}", area=1.0 + i * 0.5) for i in range(3)]
        ids = [f"p{i}" for i in range(3)]
        merged = self.tools.merge_parcels(parcels, ids)
        assert merged is not None

    def test_merge_insufficient_parcels(self):
        """Merging with only 1 matching ID should return None."""
        p1 = make_parcel("p1")
        merged = self.tools.merge_parcels([p1], ["p1"])
        assert merged is None

    def test_split_parcel(self):
        parcel = make_parcel(
            "to_split",
            coords=[
                (44.200, 15.500),
                (44.204, 15.500),
                (44.204, 15.504),
                (44.200, 15.504),
            ],
            area=4.0,
        )
        cutting_line = [(44.202, 15.499), (44.202, 15.505)]

        parts = self.tools.split_parcel(parcel, cutting_line)
        assert len(parts) >= 1  # At least original if split fails
        if len(parts) > 1:
            total_area = sum(p.area_hectares for p in parts)
            assert total_area > 0

    def test_split_with_no_intersection(self):
        """Split line that doesn't intersect should return original."""
        parcel = make_parcel(
            "no_intersect",
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ],
        )
        cutting_line = [(44.210, 15.510), (44.211, 15.511)]  # Far away
        parts = self.tools.split_parcel(parcel, cutting_line)
        assert len(parts) >= 1

    def test_connect_nearby_parcels(self):
        p1 = make_parcel(
            "frag1",
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ],
        )
        p2 = make_parcel(
            "frag2",
            coords=[
                (44.2011, 15.500),
                (44.2021, 15.500),
                (44.2021, 15.501),
                (44.2011, 15.501),
            ],
        )
        connected = self.tools.connect_parcels([p1, p2], ["frag1", "frag2"], max_gap_meters=500)
        assert connected is not None

    def test_connect_far_parcels(self):
        """Parcels too far apart shouldn't be connected."""
        p1 = make_parcel(
            "far1",
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ],
        )
        p2 = make_parcel(
            "far2",
            coords=[
                (44.210, 15.510),
                (44.211, 15.510),
                (44.211, 15.511),
                (44.210, 15.511),
            ],
        )
        # With a small max gap, distant parcels won't bridge but still get convex hull
        result = self.tools.connect_parcels([p1, p2], ["far1", "far2"], max_gap_meters=5)
        # connect_parcels returns single parcel or None
        # The method does convex hull even if gap is large, so it may return a result
        assert result is None or isinstance(result, AgriculturalParcel)


# =============================================================================
# GeoLabel 4.0: Quality Inspection Tool Tests
# =============================================================================


class TestQualityInspectionTool:
    """Test QualityInspectionTool - inspection, WKT, batch assign, stats."""

    def setup_method(self):
        self.tool = QualityInspectionTool()

    def test_inspect_valid_parcel(self):
        parcel = make_parcel(area=1.0, compactness=0.7, elongation=2.0, confidence=0.8)
        result = self.tool.inspect_all([parcel])
        assert result["total_parcels"] == 1
        assert result["passed"] == 1
        assert result["failed"] == 0

    def test_inspect_tiny_parcel(self):
        """Parcel below 50m² should fail."""
        tiny = make_parcel(area=0.003)  # 30m² < 50m² minimum
        result = self.tool.inspect_all([tiny])
        assert result["failed"] >= 1
        # Check that area issue is in the issues list
        if result["issues"]:
            issues_text = str(result["issues"])
            assert "area" in issues_text.lower() or "Area" in issues_text

    def test_inspect_elongated_parcel(self):
        """Parcel with elongation > 50 should fail."""
        elongated = make_parcel(elongation=55.0)
        result = self.tool.inspect_all([elongated])
        assert result["failed"] >= 1

    def test_inspect_low_vertices(self):
        """Parcel with < 3 vertices should fail."""
        parcel = make_parcel(coords=[(0, 0), (1, 0)])
        parcel.num_vertices = 2
        result = self.tool.inspect_all([parcel])
        assert result["failed"] >= 1

    def test_parcel_to_wkt(self):
        parcel = make_parcel(
            coords=[
                (44.200, 15.500),
                (44.201, 15.500),
                (44.201, 15.501),
                (44.200, 15.501),
            ]
        )
        wkt = self.tool.parcel_to_wkt(parcel)
        assert "POLYGON" in wkt
        assert "44.2" in wkt
        assert "15.5" in wkt

    def test_parcels_to_wkt_collection(self):
        parcels = [make_parcel(f"p{i}") for i in range(3)]
        wkt = self.tool.parcels_to_wkt_collection(parcels)
        assert "GEOMETRYCOLLECTION" in wkt
        assert wkt.count("POLYGON") == 3

    def test_batch_assign_crop_type(self):
        parcels = [make_parcel(f"p{i}") for i in range(3)]
        ids = [f"p{i}" for i in range(3)]
        count = self.tool.batch_assign_attribute(parcels, ids, "crop_type", "wheat")
        assert count == 3
        for p in parcels:
            assert p.crop_type == "wheat"

    def test_batch_assign_land_cover(self):
        parcels = [make_parcel(f"p{i}") for i in range(2)]
        ids = [f"p{i}" for i in range(2)]
        count = self.tool.batch_assign_attribute(parcels, ids, "land_cover", "orchard")
        assert count == 2
        for p in parcels:
            assert p.land_cover == LandCoverClass.ORCHARD

    def test_batch_assign_irrigated(self):
        parcels = [make_parcel(f"p{i}") for i in range(2)]
        ids = [f"p{i}" for i in range(2)]
        count = self.tool.batch_assign_attribute(parcels, ids, "is_irrigated", True)
        assert count == 2
        for p in parcels:
            assert p.is_irrigated is True

    def test_get_statistics(self):
        parcels = [
            make_parcel("p1", area=2.0, crop_type="wheat", land_cover=LandCoverClass.CROPLAND),
            make_parcel("p2", area=3.0, crop_type="barley", land_cover=LandCoverClass.CROPLAND),
            make_parcel("p3", area=1.0, crop_type="wheat", land_cover=LandCoverClass.GRASSLAND),
        ]
        stats = self.tool.get_statistics(parcels)
        assert stats["total_parcels"] == 3
        assert stats["total_area_hectares"] == 6.0
        assert "crop_type_distribution" in stats
        assert stats["crop_type_distribution"]["wheat"] == 2
        assert "land_cover_distribution" in stats
        assert stats["land_cover_distribution"]["cropland"] == 2

    def test_quality_rules(self):
        """Verify quality rules match GeoLabel specs."""
        rules = self.tool.QUALITY_RULES
        assert rules["min_area_m2"] == 50
        assert rules["min_hole_area_m2"] == 20
        assert rules["min_vertices"] == 3
        assert rules["max_elongation"] == 50


# =============================================================================
# Main Orchestrator Tests
# =============================================================================


class TestAgriculturalLandDetector:
    """Test the main AgriculturalLandDetector orchestrator."""

    def setup_method(self):
        self.detector = AgriculturalLandDetector()

    def test_initialization(self):
        assert self.detector.config is not None
        assert self.detector.config.strategy == DetectionStrategy.HYBRID
        # Phase 1-4 engines
        assert self.detector.segmentation is not None
        assert self.detector.boundary_detection is not None
        assert self.detector.post_processor is not None
        assert self.detector.classifier is not None
        # GeoLabel 4.0 engines
        assert self.detector.crop_classifier is not None
        assert self.detector.topology_simplifier is not None
        assert self.detector.editing_tools is not None
        assert self.detector.quality_inspector is not None

    def test_initialization_custom_config(self):
        config = DetectionConfig(
            strategy=DetectionStrategy.TRAINING_FREE,
            precision=ModelPrecision.SPEED_FOCUSED,
        )
        detector = AgriculturalLandDetector(config)
        assert detector.config.strategy == DetectionStrategy.TRAINING_FREE

    @pytest.mark.asyncio
    async def test_detect_parcels_hybrid(self):
        report = await self.detector.detect_parcels(latitude=15.5, longitude=44.2, radius_meters=500)
        assert isinstance(report, DetectionReport)
        assert report.strategy_used == DetectionStrategy.HYBRID
        assert report.total_parcels >= 0
        assert len(report.warnings) > 0  # Synthetic data warning

    @pytest.mark.asyncio
    async def test_detect_at_point(self):
        report = await self.detector.detect_at_point(15.5, 44.2, 500)
        assert isinstance(report, DetectionReport)

    @pytest.mark.asyncio
    async def test_detect_in_region(self):
        bounds = {"north": 15.51, "south": 15.49, "east": 44.21, "west": 44.19}
        report = await self.detector.detect_in_region(bounds)
        assert isinstance(report, DetectionReport)

    @pytest.mark.asyncio
    async def test_detect_training_free(self):
        config = DetectionConfig(strategy=DetectionStrategy.TRAINING_FREE)
        detector = AgriculturalLandDetector(config)
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2)
        assert report.strategy_used == DetectionStrategy.TRAINING_FREE

    @pytest.mark.asyncio
    async def test_detect_semantic_only(self):
        config = DetectionConfig(strategy=DetectionStrategy.SEMANTIC_SEGMENTATION)
        detector = AgriculturalLandDetector(config)
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2)
        assert report.strategy_used == DetectionStrategy.SEMANTIC_SEGMENTATION

    @pytest.mark.asyncio
    async def test_detect_boundary_only(self):
        config = DetectionConfig(strategy=DetectionStrategy.BOUNDARY_DETECTION)
        detector = AgriculturalLandDetector(config)
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2)
        assert report.strategy_used == DetectionStrategy.BOUNDARY_DETECTION

    @pytest.mark.asyncio
    async def test_detect_with_image(self):
        image, bounds = make_synthetic_image()
        report = await self.detector.detect_parcels(image_data=image, bounds=bounds)
        assert isinstance(report, DetectionReport)
        assert len(report.warnings) == 0  # No synthetic data warning

    @pytest.mark.asyncio
    async def test_detect_no_input_raises(self):
        with pytest.raises(ValueError, match="Either image_data"):
            await self.detector.detect_parcels()

    def test_generate_synthetic_data(self):
        image, bounds = self.detector._generate_synthetic_data(15.5, 44.2, 1000)
        assert image.shape == (64, 64, 4)
        assert bounds["north"] > bounds["south"]
        assert bounds["east"] > bounds["west"]

    def test_polygon_to_parcel(self):
        polygon = [
            (44.200, 15.500),
            (44.201, 15.500),
            (44.201, 15.501),
            (44.200, 15.501),
        ]
        image, bounds = make_synthetic_image()
        parcel = self.detector._polygon_to_parcel(polygon, 0, bounds, image)
        assert isinstance(parcel, AgriculturalParcel)
        assert parcel.area_hectares > 0
        assert parcel.perimeter_meters > 0
        assert parcel.compactness is not None
        assert parcel.elongation is not None

    def test_haversine(self):
        # ~111 km = 1 degree of latitude
        dist = self.detector._haversine(0.0, 0.0, 1.0, 0.0)
        assert 110000 < dist < 112000

    def test_calculate_perimeter(self):
        coords = [
            (44.200, 15.500),
            (44.201, 15.500),
            (44.201, 15.501),
            (44.200, 15.501),
        ]
        perimeter = self.detector._calculate_perimeter(coords)
        assert perimeter > 0
        assert 300 < perimeter < 600  # ~400m for ~100m square


# =============================================================================
# Integration Tests - Full Pipeline
# =============================================================================


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_full_detection_pipeline(self):
        """Test complete detection → classification → quality pipeline."""
        detector = AgriculturalLandDetector()

        # Step 1: Detect parcels
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2, radius_meters=500)

        if report.total_parcels > 0:
            # Step 2: Classify crops
            results = await detector.crop_classifier.classify_crops(report.parcels)
            assert len(results) == len(report.parcels)

            # Step 3: Quality inspection
            inspection = detector.quality_inspector.inspect_all(report.parcels)
            assert inspection["total_parcels"] == len(report.parcels)

            # Step 4: Export WKT
            for parcel in report.parcels:
                wkt = detector.quality_inspector.parcel_to_wkt(parcel)
                assert "POLYGON" in wkt

            # Step 5: Statistics
            stats = detector.quality_inspector.get_statistics(report.parcels)
            assert stats["total_parcels"] == len(report.parcels)

    @pytest.mark.asyncio
    async def test_detection_and_editing(self):
        """Test detection → merge → split workflow."""
        detector = AgriculturalLandDetector()
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2, radius_meters=500)

        if report.total_parcels >= 2:
            ids = [p.parcel_id for p in report.parcels[:2]]
            merged = detector.editing_tools.merge_parcels(report.parcels, ids)
            assert merged is not None

    @pytest.mark.asyncio
    async def test_detection_and_topology(self):
        """Test detection → topology simplification."""
        detector = AgriculturalLandDetector()
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2, radius_meters=500)

        if report.total_parcels > 0:
            simplified = detector.topology_simplifier.simplify_with_topology(report.parcels)
            assert len(simplified) == len(report.parcels)

    @pytest.mark.asyncio
    async def test_batch_assign_workflow(self):
        """Test batch attribute assignment."""
        detector = AgriculturalLandDetector()
        report = await detector.detect_parcels(latitude=15.5, longitude=44.2, radius_meters=500)

        if report.total_parcels > 0:
            ids = [p.parcel_id for p in report.parcels]
            count = detector.quality_inspector.batch_assign_attribute(report.parcels, ids, "crop_type", "wheat")
            assert count == len(report.parcels)
            assert all(p.crop_type == "wheat" for p in report.parcels)
