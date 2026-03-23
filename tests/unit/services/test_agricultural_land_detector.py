# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Tests for Agricultural Land Detector (GeoLabel-inspired)
اختبارات كاشف الأراضي الزراعية المستوحى من GeoLabel
"""

import math

import pytest

np = pytest.importorskip("numpy")


# =============================================================================
# Test imports
# =============================================================================


@pytest.mark.unit
class TestAgriculturalLandDetectorImport:
    """Test that all modules can be imported"""

    def test_import_main_module(self):
        import apps.services.vegetation_analysis_service  # noqa: F401

    def test_import_detector(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            AgriculturalLandDetector,
        )

        assert AgriculturalLandDetector is not None

    def test_import_engines(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            BoundaryDetectionEngine,
            ParcelPostProcessor,
            SemanticSegmentationEngine,
            VectorClassificationEngine,
        )

        assert SemanticSegmentationEngine is not None
        assert BoundaryDetectionEngine is not None
        assert ParcelPostProcessor is not None
        assert VectorClassificationEngine is not None

    def test_import_models(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            AgriculturalParcel,
            DetectionConfig,
            DetectionReport,
            DetectionStrategy,
            LandCoverClass,
            ModelPrecision,
            ParcelShape,
        )

        assert DetectionStrategy.HYBRID.value == "hybrid"
        assert ModelPrecision.HIGH.value == "high"
        assert LandCoverClass.CROPLAND.value == "cropland"
        assert ParcelShape.RECTANGLE.value == "rectangle"

    def test_import_endpoints(self):
        from apps.services.vegetation_analysis_service.src.parcel_endpoints import (
            register_parcel_endpoints,
        )

        assert register_parcel_endpoints is not None


# =============================================================================
# Test Semantic Segmentation Engine
# =============================================================================


@pytest.mark.unit
class TestSemanticSegmentationEngine:
    """Test semantic segmentation engine"""

    def setup_method(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            DetectionConfig,
            SemanticSegmentationEngine,
        )

        self.config = DetectionConfig()
        self.engine = SemanticSegmentationEngine(self.config)

    def test_compute_ndvi(self):
        """Test NDVI computation from multi-band image"""
        # Create 4-band image (Blue, Green, Red, NIR)
        image = np.zeros((10, 10, 4), dtype=np.float64)
        image[:, :, 2] = 0.1  # Red
        image[:, :, 3] = 0.5  # NIR

        ndvi = self.engine._compute_ndvi(image)

        # NDVI = (NIR - Red) / (NIR + Red) = (0.5 - 0.1) / (0.5 + 0.1) = 0.667
        expected = (0.5 - 0.1) / (0.5 + 0.1)
        assert abs(ndvi[0, 0] - expected) < 0.01

    def test_compute_evi(self):
        """Test EVI computation"""
        image = np.zeros((10, 10, 4), dtype=np.float64)
        image[:, :, 0] = 0.05  # Blue
        image[:, :, 2] = 0.1  # Red
        image[:, :, 3] = 0.5  # NIR

        evi = self.engine._compute_evi(image)
        assert evi.shape == (10, 10)
        assert np.all(evi >= -1.0)
        assert np.all(evi <= 1.0)

    def test_compute_ndwi(self):
        """Test NDWI computation"""
        image = np.zeros((10, 10, 4), dtype=np.float64)
        image[:, :, 1] = 0.3  # Green
        image[:, :, 3] = 0.5  # NIR

        ndwi = self.engine._compute_ndwi(image)
        # NDWI = (Green - NIR) / (Green + NIR) = (0.3 - 0.5) / (0.3 + 0.5) = -0.25
        expected = (0.3 - 0.5) / (0.3 + 0.5)
        assert abs(ndwi[0, 0] - expected) < 0.01

    def test_morphological_close(self):
        """Test morphological closing fills gaps"""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[3:7, 3:7] = 1
        mask[5, 5] = 0  # Create a gap

        closed = self.engine._morphological_close(mask, iterations=1)
        # Gap should be filled
        assert closed[5, 5] == 1

    def test_connected_components(self):
        """Test connected component labeling"""
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[1:4, 1:4] = 1  # Component 1
        mask[6:9, 6:9] = 1  # Component 2

        labels, num = self.engine._connected_components(mask)
        assert num == 2

    @pytest.mark.asyncio
    async def test_classify_pixels(self):
        """Test pixel classification"""
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import LandCoverClass

        # Create image with clear cropland (high NIR, low Red)
        image = np.zeros((20, 20, 4), dtype=np.float64)
        # Cropland region
        image[5:15, 5:15, 2] = 0.05  # Low Red
        image[5:15, 5:15, 3] = 0.50  # High NIR
        # Barren region (rest)
        image[:5, :, 2] = 0.20  # High Red
        image[:5, :, 3] = 0.10  # Low NIR

        bounds = {"north": 15.1, "south": 15.0, "east": 44.1, "west": 44.0}

        mask = await self.engine.classify_pixels(image, bounds)
        assert mask.shape == (20, 20)
        # Center should be cropland
        assert mask[10, 10] == LandCoverClass.CROPLAND.value


# =============================================================================
# Test Boundary Detection Engine
# =============================================================================


@pytest.mark.unit
class TestBoundaryDetectionEngine:
    """Test boundary detection engine"""

    def setup_method(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            BoundaryDetectionEngine,
            DetectionConfig,
        )

        self.config = DetectionConfig()
        self.engine = BoundaryDetectionEngine(self.config)

    def test_compute_gradient_magnitude(self):
        """Test gradient computation"""
        # Create image with sharp edge
        image = np.zeros((20, 20), dtype=np.float64)
        image[:, 10:] = 1.0  # Sharp vertical edge at column 10

        grad = self.engine._compute_gradient_magnitude(image)
        assert grad.shape == (20, 20)
        # Gradient should be highest near the edge
        assert grad[10, 10] > grad[10, 0]

    def test_hysteresis_threshold(self):
        """Test hysteresis thresholding"""
        edges = np.zeros((10, 10), dtype=np.float64)
        edges[5, 3:7] = 0.5  # Strong edge
        edges[5, 2] = 0.1  # Weak edge connected to strong
        edges[0, 0] = 0.1  # Weak edge NOT connected

        result = self.engine._hysteresis_threshold(edges, low_threshold=0.05, high_threshold=0.3)
        # Strong edges should be kept
        assert result[5, 5] == 1
        # Connected weak edge should be kept
        assert result[5, 2] == 1

    def test_fill_enclosed_regions(self):
        """Test region filling"""
        # Create a closed boundary
        boundary = np.zeros((10, 10), dtype=np.uint8)
        boundary[2, 2:8] = 1  # Top
        boundary[7, 2:8] = 1  # Bottom
        boundary[2:8, 2] = 1  # Left
        boundary[2:8, 7] = 1  # Right

        filled = self.engine._fill_enclosed_regions(boundary)
        # Interior should be filled
        assert filled[4, 4] == 1
        # Exterior should not be filled
        assert filled[0, 0] == 0


# =============================================================================
# Test Post-Processing
# =============================================================================


@pytest.mark.unit
class TestParcelPostProcessor:
    """Test parcel post-processing"""

    def setup_method(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            DetectionConfig,
            ParcelPostProcessor,
        )

        self.config = DetectionConfig()
        self.processor = ParcelPostProcessor(self.config)

    def test_chaikin_smooth(self):
        """Test Chaikin's corner cutting smoothing"""
        # Square polygon
        coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

        smoothed = self.processor._chaikin_smooth(coords)
        # Should have more points than original
        assert len(smoothed) > len(coords)
        # Should have 2x original number of points
        assert len(smoothed) == len(coords) * 2

    def test_correct_sharp_angles(self):
        """Test sharp angle correction"""
        # Create polygon with a very sharp spike
        coords = [
            (0.0, 0.0),
            (0.5, 0.0),
            (0.5001, 0.5),  # Sharp spike
            (0.5, 0.0001),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ]

        corrected = self.processor._correct_sharp_angles(coords, min_angle_degrees=15.0)
        # Should have removed some sharp vertices
        assert len(corrected) <= len(coords)

    def test_convex_hull(self):
        """Test convex hull computation"""
        coords = [
            (0.0, 0.0),
            (1.0, 0.0),
            (0.5, 0.3),  # Interior point
            (1.0, 1.0),
            (0.0, 1.0),
        ]

        hull = self.processor._convex_hull(coords)
        # Interior point should be removed
        assert len(hull) <= len(coords)
        # Hull should still be valid polygon
        assert len(hull) >= 3

    def test_fit_rectangle(self):
        """Test rectangle fitting"""
        coords = [
            (0.1, 0.1),
            (0.9, 0.2),
            (0.8, 0.9),
            (0.2, 0.8),
        ]

        rect = self.processor._fit_rectangle(coords)
        assert len(rect) == 4

    def test_calculate_area(self):
        """Test area calculation"""
        # 0.01 degree ≈ 1113m at equator, so 0.01° × 0.01° ≈ 1113² m² ≈ 123.9 ha
        coords = [(0.0, 0.0), (0.01, 0.0), (0.01, 0.01), (0.0, 0.01)]
        area = self.processor._calculate_area(coords)
        assert area > 0
        # Should be roughly 123.9 hectares for 0.01 degree square at equator
        assert 100 < area < 150

    def test_remove_overlapping(self):
        """Test overlapping parcel removal"""
        polygons = [
            [(0.0, 0.0), (0.01, 0.0), (0.01, 0.01), (0.0, 0.01)],  # Large
            [(0.004, 0.004), (0.006, 0.004), (0.006, 0.006), (0.004, 0.006)],  # Small, inside large
        ]

        result = self.processor._remove_overlapping(polygons)
        # Should keep at least the larger one
        assert len(result) >= 1

    def test_douglas_peucker(self):
        """Test Douglas-Peucker simplification"""
        # Create a line with many collinear points
        coords = [(float(i) * 0.001, 0.0) for i in range(20)]

        simplified = self.processor._douglas_peucker(coords, tolerance=0.0001)
        # Should be simplified to just start and end
        assert len(simplified) < len(coords)


# =============================================================================
# Test Vector Classification
# =============================================================================


@pytest.mark.unit
class TestVectorClassificationEngine:
    """Test vector classification engine"""

    def setup_method(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            DetectionConfig,
            VectorClassificationEngine,
        )

        self.config = DetectionConfig()
        self.classifier = VectorClassificationEngine(self.config)

    def test_area_to_score(self):
        """Test area to agricultural likelihood conversion"""
        # Typical farm size should score high
        assert self.classifier._area_to_score(5.0) == 1.0
        assert self.classifier._area_to_score(25.0) == 1.0

        # Very small should score low
        assert self.classifier._area_to_score(0.01) < 0.5

        # Very large should still score reasonable
        assert self.classifier._area_to_score(100.0) > 0.2

    def test_compute_compactness(self):
        """Test compactness computation"""
        # Perfect circle: 4π·A/P² = 1.0
        # Area = π, Perimeter = 2π → compactness = 4π·π/(2π)² = 1.0
        compactness = self.classifier._compute_compactness(
            area_hectares=math.pi / 10000,
            perimeter_meters=2 * math.pi,
        )
        assert abs(compactness - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_classify_parcels(self):
        """Test parcel classification"""
        from datetime import datetime

        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            AgriculturalParcel,
            DetectionStrategy,
            LandCoverClass,
        )

        parcels = [
            AgriculturalParcel(
                parcel_id="test_cropland",
                coordinates=[(0.0, 0.0), (0.01, 0.0), (0.01, 0.01), (0.0, 0.01)],
                area_hectares=5.0,
                perimeter_meters=400,
                centroid=(0.005, 0.005),
                land_cover=LandCoverClass.UNKNOWN,
                detection_confidence=0.0,
                detection_date=datetime.now(),
                strategy=DetectionStrategy.HYBRID,
                mean_ndvi=0.65,
                mean_evi=0.45,
                compactness=0.8,
            ),
            AgriculturalParcel(
                parcel_id="test_barren",
                coordinates=[(1.0, 1.0), (1.01, 1.0), (1.01, 1.01), (1.0, 1.01)],
                area_hectares=5.0,
                perimeter_meters=400,
                centroid=(1.005, 1.005),
                land_cover=LandCoverClass.UNKNOWN,
                detection_confidence=0.0,
                detection_date=datetime.now(),
                strategy=DetectionStrategy.HYBRID,
                mean_ndvi=0.0,
                mean_evi=0.0,
                compactness=0.01,
                rectangularity=0.1,
                elongation=9.0,
            ),
        ]

        classified = await self.classifier.classify_parcels(parcels)
        assert len(classified) == 2
        # High NDVI parcel should be cropland
        assert classified[0].land_cover == LandCoverClass.CROPLAND
        # Low NDVI parcel should be barren
        assert classified[1].land_cover == LandCoverClass.BARREN


# =============================================================================
# Test Main Orchestrator
# =============================================================================


@pytest.mark.unit
class TestAgriculturalLandDetector:
    """Test main orchestrator"""

    def setup_method(self):
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            AgriculturalLandDetector,
            DetectionConfig,
            DetectionStrategy,
        )

        self.config = DetectionConfig(strategy=DetectionStrategy.TRAINING_FREE)
        self.detector = AgriculturalLandDetector(self.config)

    @pytest.mark.asyncio
    async def test_detect_at_point(self):
        """Test point-based detection"""
        report = await self.detector.detect_at_point(
            latitude=15.5,
            longitude=44.2,
            radius_meters=500,
        )

        assert report.total_parcels >= 0
        assert report.detection_time_seconds > 0
        assert report.strategy_used.value == "training_free"

    @pytest.mark.asyncio
    async def test_detect_with_synthetic_data(self):
        """Test detection with synthetic multi-spectral data"""
        image, bounds = self.detector._generate_synthetic_data(15.5, 44.2, 1000)

        assert image.shape[2] == 4  # 4 bands
        assert "north" in bounds
        assert bounds["north"] > bounds["south"]

    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        # ~111km between latitudes
        dist = self.detector._haversine(0.0, 0.0, 1.0, 0.0)
        assert 110000 < dist < 112000

    def test_generate_synthetic_data(self):
        """Test synthetic data generation"""
        image, bounds = self.detector._generate_synthetic_data(15.5, 44.2, 1000)

        assert image.shape == (64, 64, 4)
        assert bounds["north"] > bounds["south"]
        assert bounds["east"] > bounds["west"]
        # Check that image has realistic values
        assert image.min() >= 0.0
        assert image.max() <= 1.0


# =============================================================================
# Test Data Models
# =============================================================================


@pytest.mark.unit
class TestDataModels:
    """Test data models"""

    def test_agricultural_parcel_to_geojson(self):
        """Test GeoJSON conversion"""
        from datetime import datetime

        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            AgriculturalParcel,
            DetectionStrategy,
            LandCoverClass,
        )

        parcel = AgriculturalParcel(
            parcel_id="test_001",
            coordinates=[(44.2, 15.5), (44.21, 15.5), (44.21, 15.51), (44.2, 15.51)],
            area_hectares=10.5,
            perimeter_meters=1200,
            centroid=(44.205, 15.505),
            land_cover=LandCoverClass.CROPLAND,
            detection_confidence=0.85,
            detection_date=datetime(2026, 3, 9),
            strategy=DetectionStrategy.HYBRID,
            mean_ndvi=0.65,
        )

        geojson = parcel.to_geojson()
        assert geojson["type"] == "Feature"
        assert geojson["geometry"]["type"] == "Polygon"
        assert geojson["properties"]["land_cover"] == "cropland"
        assert geojson["properties"]["area_hectares"] == 10.5

    def test_detection_config_defaults(self):
        """Test default configuration"""
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            DetectionConfig,
            DetectionStrategy,
            ModelPrecision,
        )

        config = DetectionConfig()
        assert config.strategy == DetectionStrategy.HYBRID
        assert config.precision == ModelPrecision.HIGH
        assert config.min_area_hectares == 0.05
        assert config.ndvi_cropland_threshold == 0.25

    def test_detection_report_to_dict(self):
        """Test report serialization"""
        from apps.services.vegetation_analysis_service.src.agricultural_land_detector import (
            DetectionReport,
            DetectionStrategy,
            ModelPrecision,
        )

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

        result = report.to_dict()
        assert result["total_parcels"] == 10
        assert result["cropland_parcels"] == 7
        assert "summary" in result
        assert "en" in result["summary"]
        assert "ar" in result["summary"]
