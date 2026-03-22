"""
Tests for endpoint helper functions (build_*, calculate_*, generate_*, etc.)
اختبارات الدوال المساعدة لنقاط النهاية
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.utils.hydrology_algorithms import (
    DEMData,
    HydrologyAnalyzer,
    DepressionData,
    DrainageSegmentData,
    generate_mock_dem,
    cells_to_coordinates,
    classify_drainage_pattern,
    calculate_slope,
    calculate_d8_flow_direction,
)
from src.api.schemas import (
    DepressionRisk,
    DrainageType,
    WetnessLevel,
    WETNESS_LEVEL_AR,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_analyzer():
    """Create a HydrologyAnalyzer with mock data already analyzed."""
    dem = generate_mock_dem(rows=50, cols=50, resolution=30.0, bounds=(45.0, 15.0, 45.1, 15.1))
    analyzer = HydrologyAnalyzer()
    analyzer.load_dem(dem)
    analyzer.run_full_analysis(flow_threshold=50, depression_max_depth=2.0, min_basin_cells=50)
    return analyzer, dem


@pytest.fixture
def mock_analyzer_no_bounds():
    """Create an analyzer with DEM that has no bounds."""
    dem = generate_mock_dem(rows=30, cols=30, resolution=30.0, bounds=None)
    analyzer = HydrologyAnalyzer()
    analyzer.load_dem(dem)
    analyzer.run_full_analysis(flow_threshold=30, depression_max_depth=2.0, min_basin_cells=30)
    return analyzer, dem


# ==============================================================================
# validate_field_id Tests
# ==============================================================================


class TestValidateFieldId:
    """Tests for SSRF-safe field ID validation."""

    def test_valid_field_ids(self):
        from src.api.endpoints.hydrology import validate_field_id

        assert validate_field_id("FIELD-001") == "FIELD-001"
        assert validate_field_id("field_123") == "field_123"
        assert validate_field_id("abc") == "abc"
        assert validate_field_id("A") == "A"

    def test_invalid_field_ids(self):
        from src.api.endpoints.hydrology import validate_field_id

        with pytest.raises(ValueError):
            validate_field_id("")
        with pytest.raises(ValueError):
            validate_field_id("../../../etc/passwd")
        with pytest.raises(ValueError):
            validate_field_id("field id with spaces")
        with pytest.raises(ValueError):
            validate_field_id("field;drop table")


# ==============================================================================
# build_drainage_network Tests
# ==============================================================================


class TestBuildDrainageNetwork:
    """Tests for build_drainage_network helper."""

    def test_builds_drainage_with_bounds(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_drainage_network

        analyzer, dem = mock_analyzer
        result = build_drainage_network(analyzer, dem, "FIELD-001")

        assert result.field_id == "FIELD-001"
        assert result.total_length_m >= 0
        assert result.drainage_density >= 0
        assert isinstance(result.pattern, DrainageType)
        assert result.pattern_ar is not None
        assert isinstance(result.segments, list)
        assert "segment_count" in result.statistics

    def test_builds_drainage_without_bounds(self, mock_analyzer_no_bounds):
        from src.api.endpoints.hydrology import build_drainage_network

        analyzer, dem = mock_analyzer_no_bounds
        result = build_drainage_network(analyzer, dem, "FIELD-002")

        assert result.field_id == "FIELD-002"
        # Should still work with pixel coordinates
        assert result.total_length_m >= 0

    def test_bifurcation_ratio_calculation(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_drainage_network

        analyzer, dem = mock_analyzer
        result = build_drainage_network(analyzer, dem, "F1")

        assert result.bifurcation_ratio > 0


# ==============================================================================
# build_wetness_analysis Tests
# ==============================================================================


class TestBuildWetnessAnalysis:
    """Tests for build_wetness_analysis helper."""

    def test_builds_wetness_without_rainfall(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_wetness_analysis

        analyzer, dem = mock_analyzer
        result = build_wetness_analysis(analyzer, dem, "FIELD-001")

        assert result.field_id == "FIELD-001"
        assert result.total_area_ha > 0
        assert result.twi_mean != 0
        assert len(result.zones) > 0
        assert result.waterlogging_prediction is None
        assert 0 <= result.irrigation_efficiency_score <= 100

    def test_builds_wetness_with_rainfall(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_wetness_analysis

        analyzer, dem = mock_analyzer
        rainfall_data = {"total_rainfall_mm": 50.0}
        result = build_wetness_analysis(analyzer, dem, "FIELD-001", rainfall_data)

        assert result.waterlogging_prediction is not None
        pred = result.waterlogging_prediction
        assert pred.rainfall_mm == 50.0
        assert pred.risk_level == DepressionRisk.MEDIUM
        assert pred.affected_area_ha > 0

    def test_builds_wetness_low_rainfall(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_wetness_analysis

        analyzer, dem = mock_analyzer
        rainfall_data = {"total_rainfall_mm": 10.0}
        result = build_wetness_analysis(analyzer, dem, "FIELD-001", rainfall_data)

        pred = result.waterlogging_prediction
        assert pred.risk_level == DepressionRisk.LOW

    def test_wetness_zones_have_arabic_labels(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_wetness_analysis

        analyzer, dem = mock_analyzer
        result = build_wetness_analysis(analyzer, dem, "F1")

        for zone in result.zones:
            assert zone.level_ar is not None
            assert len(zone.level_ar) > 0
            assert len(zone.recommendations_ar) >= 0
            assert len(zone.recommendations_en) >= 0


# ==============================================================================
# build_depression_analysis Tests
# ==============================================================================


class TestBuildDepressionAnalysis:
    """Tests for build_depression_analysis helper."""

    def test_builds_depression_analysis(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_depression_analysis

        analyzer, dem = mock_analyzer
        result = build_depression_analysis(analyzer, dem, "FIELD-001")

        assert result.field_id == "FIELD-001"
        assert result.total_depressions >= 0
        assert result.field_area_ha > 0
        assert result.summary_ar is not None
        assert result.summary_en is not None

    def test_depression_risk_classification(self):
        """Test that depression risk is classified correctly by depth."""
        from src.api.endpoints.hydrology import build_depression_analysis

        dem = generate_mock_dem(rows=10, cols=10, resolution=30.0, bounds=(45.0, 15.0, 45.1, 15.1))
        analyzer = HydrologyAnalyzer()
        analyzer.load_dem(dem)
        analyzer.run_full_analysis()

        # Inject custom depressions to test risk classification
        analyzer.depressions = [
            DepressionData("dep-1", [(5, 5)], depth_m=1.5, volume_m3=1350, spill_elevation=110),
            DepressionData("dep-2", [(3, 3)], depth_m=0.7, volume_m3=630, spill_elevation=105),
            DepressionData("dep-3", [(7, 7)], depth_m=0.3, volume_m3=270, spill_elevation=102),
            DepressionData("dep-4", [(2, 2)], depth_m=0.1, volume_m3=90, spill_elevation=100),
        ]

        result = build_depression_analysis(analyzer, dem, "F1")

        assert result.critical_count == 1  # depth >= 1.0
        assert result.high_risk_count == 1  # depth >= 0.5
        assert result.total_depressions == 4

    def test_depression_summary_critical(self):
        """Test summary for critical depressions."""
        from src.api.endpoints.hydrology import build_depression_analysis

        dem = generate_mock_dem(rows=10, cols=10, resolution=30.0, bounds=(45.0, 15.0, 45.1, 15.1))
        analyzer = HydrologyAnalyzer()
        analyzer.load_dem(dem)
        analyzer.run_full_analysis()

        analyzer.depressions = [
            DepressionData("dep-1", [(5, 5)], depth_m=2.0, volume_m3=1800, spill_elevation=110),
        ]

        result = build_depression_analysis(analyzer, dem, "F1")
        assert "critical" in result.summary_en.lower() or "حرج" in result.summary_ar


# ==============================================================================
# build_stream_network Tests
# ==============================================================================


class TestBuildStreamNetwork:
    """Tests for build_stream_network helper."""

    def test_builds_stream_network(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_stream_network

        analyzer, dem = mock_analyzer
        result = build_stream_network(analyzer, dem, "FIELD-001")

        assert result.field_id == "FIELD-001"
        assert result.total_streams >= 0
        assert result.max_order >= 1
        assert isinstance(result.hydraulic_geometry, dict)

    def test_stream_perennial_classification(self, mock_analyzer):
        """Test that streams with order >= 3 are marked perennial."""
        from src.api.endpoints.hydrology import build_stream_network

        analyzer, dem = mock_analyzer
        result = build_stream_network(analyzer, dem, "F1")

        for stream in result.streams:
            if stream.order >= 3:
                assert stream.is_perennial is True
            else:
                assert stream.is_perennial is False


# ==============================================================================
# build_basin_delineation Tests
# ==============================================================================


class TestBuildBasinDelineation:
    """Tests for build_basin_delineation helper."""

    def test_builds_basin_delineation(self, mock_analyzer):
        from src.api.endpoints.hydrology import build_basin_delineation

        analyzer, dem = mock_analyzer
        result = build_basin_delineation(analyzer, dem, "FIELD-001")

        assert result.field_id == "FIELD-001"
        assert result.total_basins >= 0
        assert result.outlet_point is not None
        assert 0 <= result.runoff_coefficient <= 1
        assert result.elongation_ratio > 0
        assert result.circularity_ratio > 0

    def test_basin_no_basins(self):
        """Test basin delineation with no basins."""
        from src.api.endpoints.hydrology import build_basin_delineation

        dem = generate_mock_dem(rows=5, cols=5, resolution=30.0, bounds=(45.0, 15.0, 45.1, 15.1))
        analyzer = HydrologyAnalyzer()
        analyzer.load_dem(dem)
        analyzer.run_full_analysis(min_basin_cells=1000)  # high threshold = no basins

        result = build_basin_delineation(analyzer, dem, "F1")
        assert result.total_basins == 0
        assert result.outlet_point is not None  # fallback point


# ==============================================================================
# calculate_flood_risk Tests
# ==============================================================================


class TestCalculateFloodRisk:
    """Tests for flood risk calculation."""

    def test_critical_risk(self):
        from src.api.endpoints.hydrology import calculate_flood_risk

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.WATERLOGGED

        depressions = MagicMock()
        depressions.critical_count = 2
        depressions.high_risk_count = 0
        depressions.depressions_percentage = 6.0

        result = calculate_flood_risk(wetness, depressions)
        assert result == DepressionRisk.CRITICAL

    def test_low_risk(self):
        from src.api.endpoints.hydrology import calculate_flood_risk

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.DRY

        depressions = MagicMock()
        depressions.critical_count = 0
        depressions.high_risk_count = 0
        depressions.depressions_percentage = 0.5

        result = calculate_flood_risk(wetness, depressions)
        assert result == DepressionRisk.LOW

    def test_medium_risk(self):
        from src.api.endpoints.hydrology import calculate_flood_risk

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.WET

        depressions = MagicMock()
        depressions.critical_count = 0
        depressions.high_risk_count = 0
        depressions.depressions_percentage = 0.5

        result = calculate_flood_risk(wetness, depressions)
        assert result == DepressionRisk.MEDIUM


# ==============================================================================
# calculate_drainage_quality_score Tests
# ==============================================================================


class TestCalculateDrainageQualityScore:
    """Tests for drainage quality score calculation."""

    def test_high_quality_drainage(self):
        from src.api.endpoints.hydrology import calculate_drainage_quality_score

        drainage = MagicMock()
        drainage.drainage_density = 200

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.MODERATE
        wetness.irrigation_efficiency_score = 85.0

        score = calculate_drainage_quality_score(drainage, wetness)
        assert score == 100.0

    def test_low_quality_drainage(self):
        from src.api.endpoints.hydrology import calculate_drainage_quality_score

        drainage = MagicMock()
        drainage.drainage_density = 30  # low

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.WATERLOGGED
        wetness.irrigation_efficiency_score = 40.0

        score = calculate_drainage_quality_score(drainage, wetness)
        assert score == 30.0  # 100 - 20 - 30 - 20

    def test_score_clamped(self):
        from src.api.endpoints.hydrology import calculate_drainage_quality_score

        drainage = MagicMock()
        drainage.drainage_density = 10  # -20

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.WATERLOGGED  # -30
        wetness.irrigation_efficiency_score = 30.0  # -20

        score = calculate_drainage_quality_score(drainage, wetness)
        assert score >= 0
        assert score <= 100


# ==============================================================================
# generate_recommendations Tests
# ==============================================================================


class TestGenerateRecommendations:
    """Tests for recommendation generation."""

    def test_recommendations_for_poor_drainage(self):
        from src.api.endpoints.hydrology import generate_recommendations

        drainage = MagicMock()
        drainage.drainage_density = 30  # low

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.MODERATE
        wetness.irrigation_efficiency_score = 80.0

        depressions = MagicMock()
        depressions.critical_count = 0
        depressions.high_risk_count = 0

        ar, en = generate_recommendations(drainage, wetness, depressions, DepressionRisk.LOW)
        assert len(en) > 0
        assert any("drainage" in r.lower() for r in en)

    def test_recommendations_default_when_good(self):
        from src.api.endpoints.hydrology import generate_recommendations

        drainage = MagicMock()
        drainage.drainage_density = 200

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.MODERATE
        wetness.irrigation_efficiency_score = 90.0

        depressions = MagicMock()
        depressions.critical_count = 0
        depressions.high_risk_count = 0

        ar, en = generate_recommendations(drainage, wetness, depressions, DepressionRisk.LOW)
        assert len(ar) > 0
        assert any("maintenance" in r.lower() or "good condition" in r.lower() for r in en)

    def test_recommendations_for_critical_flood(self):
        from src.api.endpoints.hydrology import generate_recommendations

        drainage = MagicMock()
        drainage.drainage_density = 30

        wetness = MagicMock()
        wetness.dominant_level = WetnessLevel.WATERLOGGED
        wetness.irrigation_efficiency_score = 30.0

        depressions = MagicMock()
        depressions.critical_count = 5
        depressions.high_risk_count = 0

        ar, en = generate_recommendations(drainage, wetness, depressions, DepressionRisk.CRITICAL)
        assert any("flood" in r.lower() or "urgent" in r.lower() for r in en)


# ==============================================================================
# Wetness/Depression Recommendations Tests
# ==============================================================================


class TestRecommendationFunctions:
    """Tests for get_wetness_recommendations and get_depression_recommendations."""

    def test_wetness_recommendations_ar_all_levels(self):
        from src.api.endpoints.hydrology import get_wetness_recommendations_ar

        for level in WetnessLevel:
            recs = get_wetness_recommendations_ar(level)
            assert isinstance(recs, list)
            assert len(recs) > 0

    def test_wetness_recommendations_en_all_levels(self):
        from src.api.endpoints.hydrology import get_wetness_recommendations_en

        for level in WetnessLevel:
            recs = get_wetness_recommendations_en(level)
            assert isinstance(recs, list)
            assert len(recs) > 0

    def test_depression_recommendations_ar_all_levels(self):
        from src.api.endpoints.hydrology import get_depression_recommendations_ar

        for risk in DepressionRisk:
            recs = get_depression_recommendations_ar(risk)
            assert isinstance(recs, list)
            assert len(recs) > 0

    def test_depression_recommendations_en_all_levels(self):
        from src.api.endpoints.hydrology import get_depression_recommendations_en

        for risk in DepressionRisk:
            recs = get_depression_recommendations_en(risk)
            assert isinstance(recs, list)
            assert len(recs) > 0


# ==============================================================================
# cells_to_coordinates Tests
# ==============================================================================


class TestCellsToCoordinates:
    """Tests for cells_to_coordinates utility."""

    def test_with_bounds(self):
        dem = DEMData(
            elevation=np.ones((10, 10), dtype=np.float32),
            resolution=30.0,
            bounds=(45.0, 15.0, 45.1, 15.1),
        )
        cells = [(0, 0), (5, 5), (9, 9)]
        coords = cells_to_coordinates(cells, dem)
        assert len(coords) == 3
        # Coordinates should be [lon, lat]
        for c in coords:
            assert len(c) == 2
            assert 45.0 <= c[0] <= 45.1
            assert 15.0 <= c[1] <= 15.1

    def test_without_bounds(self):
        dem = DEMData(
            elevation=np.ones((10, 10), dtype=np.float32),
            resolution=30.0,
            bounds=None,
        )
        cells = [(3, 7)]
        coords = cells_to_coordinates(cells, dem)
        assert coords == [[7, 3]]  # col, row as pixel coords


# ==============================================================================
# classify_drainage_pattern Tests
# ==============================================================================


class TestClassifyDrainagePattern:
    """Tests for drainage pattern classification."""

    def test_classify_parallel_pattern(self):
        """Uniform flow direction should be classified as parallel."""
        flow_dir = np.full((10, 10), 4, dtype=np.uint8)  # All flow south
        dem = DEMData(elevation=np.ones((10, 10), dtype=np.float32), resolution=30.0)
        slope = np.ones((10, 10)) * 5.0
        pattern = classify_drainage_pattern(dem, flow_dir, slope)
        assert pattern == "parallel"

    def test_classify_deranged_flat(self):
        """Flat terrain with low slope should be deranged."""
        # Mix of directions on flat terrain
        flow_dir = np.random.choice([1, 2, 4, 8, 16, 32, 64, 128], size=(10, 10)).astype(np.uint8)
        dem = DEMData(elevation=np.ones((10, 10), dtype=np.float32), resolution=30.0)
        slope = np.ones((10, 10)) * 0.5  # very flat
        pattern = classify_drainage_pattern(dem, flow_dir, slope)
        assert pattern == "deranged"

    def test_classify_no_flow(self):
        """All zero flow direction returns unknown."""
        flow_dir = np.zeros((10, 10), dtype=np.uint8)
        dem = DEMData(elevation=np.ones((10, 10), dtype=np.float32), resolution=30.0)
        slope = np.ones((10, 10)) * 5.0
        pattern = classify_drainage_pattern(dem, flow_dir, slope)
        assert pattern == "unknown"


# ==============================================================================
# generate_mock_analysis_data Tests
# ==============================================================================


class TestGenerateMockAnalysisData:
    """Tests for mock analysis data generation used by endpoints."""

    def test_generates_complete_data(self):
        from src.api.endpoints.hydrology import generate_mock_analysis_data

        dem, analyzer = generate_mock_analysis_data("FIELD-TEST", 30.0)

        assert dem.rows == 100
        assert dem.cols == 100
        assert dem.bounds is not None
        assert analyzer.dem is not None
        assert analyzer.flow_data is not None
        assert analyzer.twi is not None


# ==============================================================================
# fetch_dem_from_terrain_service Tests
# ==============================================================================


class TestFetchDemFromTerrainService:
    """Tests for terrain service integration."""

    @pytest.mark.asyncio
    async def test_fetch_dem_invalid_field_id(self):
        from src.api.endpoints.hydrology import fetch_dem_from_terrain_service

        with patch("src.api.endpoints.hydrology.logger"):
            result = await fetch_dem_from_terrain_service("../../../etc/passwd")
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_dem_connection_error(self):
        from src.api.endpoints.hydrology import fetch_dem_from_terrain_service
        from unittest.mock import AsyncMock as AM

        class _FakeClient:
            def __init__(self, **kw):
                pass
            async def __aenter__(self):
                raise Exception("Connection refused")
            async def __aexit__(self, *a):
                return False

        with patch("src.api.endpoints.hydrology.httpx.AsyncClient", _FakeClient), \
             patch("src.api.endpoints.hydrology.logger"):
            result = await fetch_dem_from_terrain_service("FIELD-001")
            assert result is None
