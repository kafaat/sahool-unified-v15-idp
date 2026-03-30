"""
Tests for shared/satellite/sentinel_ndvi.py
============================================

Tests cover:
- Enums: VegetationIndex, CloudCoverage
- Dataclass models: SatelliteFieldBoundary (FieldBoundary alias),
  NDVIResult, TimeSeriesNDVI
- Health status classification (healthy, moderate, stressed, critical)
- Bilingual labels (Arabic/English)
- NDVI validation (range checks)
- Bounding box computation
- Time series trend calculation (improving, stable, declining)
- SentinelNDVIAnalyzer: initialization, mock NDVI, crop health analysis
- All external API calls are mocked (no Sentinel Hub dependency)
"""

import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

from shared.satellite.sentinel_ndvi import (
    CloudCoverage,
    FieldBoundary,
    NDVIResult,
    SatelliteFieldBoundary,
    SentinelNDVIAnalyzer,
    TimeSeriesNDVI,
    VegetationIndex,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_field() -> FieldBoundary:
    """Create a sample field boundary for testing."""
    return FieldBoundary(
        field_id="FIELD-001",
        coordinates=[(46.7, 24.7), (46.8, 24.7), (46.8, 24.8), (46.7, 24.8)],
        area_hectares=10.0,
    )


@pytest.fixture
def sample_date() -> datetime:
    return datetime(2026, 3, 15, tzinfo=UTC)


@pytest.fixture
def analyzer() -> SentinelNDVIAnalyzer:
    """Create an analyzer without credentials (will use mock data)."""
    return SentinelNDVIAnalyzer()


def _make_ndvi_result(mean: float, field_id: str = "FIELD-001") -> NDVIResult:
    """Helper to create an NDVIResult with a given mean value."""
    return NDVIResult(
        field_id=field_id,
        timestamp=datetime(2026, 3, 15, tzinfo=UTC),
        index_type=VegetationIndex.NDVI,
        mean_value=mean,
        min_value=max(-1.0, mean - 0.1),
        max_value=min(1.0, mean + 0.1),
        std_value=0.05,
        cloud_coverage=10.0,
        pixel_count=1000,
    )


# ─────────────────────────────────────────────────────────────────────────────
# VegetationIndex Enum
# ─────────────────────────────────────────────────────────────────────────────


class TestVegetationIndex:
    @pytest.mark.unit
    def test_all_values(self):
        assert VegetationIndex.NDVI.value == "ndvi"
        assert VegetationIndex.LAI.value == "lai"
        assert VegetationIndex.EVI.value == "evi"
        assert VegetationIndex.SAVI.value == "savi"
        assert VegetationIndex.NDWI.value == "ndwi"
        assert VegetationIndex.MSAVI.value == "msavi"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(VegetationIndex) == 6

    @pytest.mark.unit
    def test_string_enum(self):
        """VegetationIndex inherits from StrEnum so it should be usable as a string."""
        assert str(VegetationIndex.NDVI) == "ndvi"
        assert f"Index: {VegetationIndex.LAI}" == "Index: lai"


# ─────────────────────────────────────────────────────────────────────────────
# CloudCoverage Enum
# ─────────────────────────────────────────────────────────────────────────────


class TestCloudCoverage:
    @pytest.mark.unit
    def test_all_values(self):
        assert CloudCoverage.CLEAR.value == "clear"
        assert CloudCoverage.LOW.value == "low"
        assert CloudCoverage.MEDIUM.value == "medium"
        assert CloudCoverage.HIGH.value == "high"

    @pytest.mark.unit
    def test_member_count(self):
        assert len(CloudCoverage) == 4


# ─────────────────────────────────────────────────────────────────────────────
# SatelliteFieldBoundary / FieldBoundary
# ─────────────────────────────────────────────────────────────────────────────


class TestFieldBoundary:
    @pytest.mark.unit
    def test_alias(self):
        """FieldBoundary is a backward-compatible alias for SatelliteFieldBoundary."""
        assert FieldBoundary is SatelliteFieldBoundary

    @pytest.mark.unit
    def test_creation(self, sample_field):
        assert sample_field.field_id == "FIELD-001"
        assert len(sample_field.coordinates) == 4
        assert sample_field.area_hectares == 10.0
        assert sample_field.crs == "EPSG:4326"

    @pytest.mark.unit
    def test_default_values(self):
        fb = FieldBoundary(field_id="F1", coordinates=[(0, 0), (1, 1)])
        assert fb.area_hectares == 0.0
        assert fb.crs == "EPSG:4326"

    @pytest.mark.unit
    def test_to_bbox(self, sample_field):
        bbox = sample_field.to_bbox()
        assert bbox == (46.7, 24.7, 46.8, 24.8)

    @pytest.mark.unit
    def test_to_bbox_single_point(self):
        fb = FieldBoundary(field_id="F2", coordinates=[(10.5, 20.5)])
        bbox = fb.to_bbox()
        assert bbox == (10.5, 20.5, 10.5, 20.5)

    @pytest.mark.unit
    def test_to_bbox_irregular_shape(self):
        fb = FieldBoundary(
            field_id="F3",
            coordinates=[(1.0, 5.0), (3.0, 2.0), (5.0, 8.0), (2.0, 4.0)],
        )
        bbox = fb.to_bbox()
        assert bbox == (1.0, 2.0, 5.0, 8.0)


# ─────────────────────────────────────────────────────────────────────────────
# NDVIResult - Health Classification
# ─────────────────────────────────────────────────────────────────────────────


class TestNDVIResult:
    @pytest.mark.unit
    def test_healthy_status(self):
        result = _make_ndvi_result(0.7)
        assert result.health_status == "healthy"
        assert result.health_status_ar == "صحي"

    @pytest.mark.unit
    def test_healthy_boundary(self):
        """NDVI == 0.6 should be classified as healthy."""
        result = _make_ndvi_result(0.6)
        assert result.health_status == "healthy"

    @pytest.mark.unit
    def test_moderate_status(self):
        result = _make_ndvi_result(0.5)
        assert result.health_status == "moderate"
        assert result.health_status_ar == "معتدل"

    @pytest.mark.unit
    def test_moderate_boundary(self):
        """NDVI == 0.4 should be classified as moderate."""
        result = _make_ndvi_result(0.4)
        assert result.health_status == "moderate"

    @pytest.mark.unit
    def test_stressed_status(self):
        result = _make_ndvi_result(0.3)
        assert result.health_status == "stressed"
        assert result.health_status_ar == "مجهد"

    @pytest.mark.unit
    def test_stressed_boundary(self):
        """NDVI == 0.2 should be classified as stressed."""
        result = _make_ndvi_result(0.2)
        assert result.health_status == "stressed"

    @pytest.mark.unit
    def test_critical_status(self):
        result = _make_ndvi_result(0.1)
        assert result.health_status == "critical"
        assert result.health_status_ar == "حرج"

    @pytest.mark.unit
    def test_critical_near_zero(self):
        result = _make_ndvi_result(0.0)
        assert result.health_status == "critical"

    @pytest.mark.unit
    def test_ndvi_out_of_range_raises(self):
        """NDVI values outside [-1.0, 1.0] should raise ValueError."""
        with pytest.raises(ValueError, match="outside valid range"):
            NDVIResult(
                field_id="F1",
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=1.5,
                min_value=0.5,
                max_value=1.5,
                std_value=0.1,
                cloud_coverage=0.0,
                pixel_count=100,
            )

    @pytest.mark.unit
    def test_ndvi_negative_out_of_range_raises(self):
        with pytest.raises(ValueError, match="outside valid range"):
            NDVIResult(
                field_id="F1",
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=0.5,
                min_value=-1.5,
                max_value=0.8,
                std_value=0.1,
                cloud_coverage=0.0,
                pixel_count=100,
            )

    @pytest.mark.unit
    def test_non_ndvi_index_no_health_classification(self):
        """Non-NDVI indices should not set health status in __post_init__."""
        result = NDVIResult(
            field_id="F1",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            index_type=VegetationIndex.LAI,
            mean_value=3.5,
            min_value=2.0,
            max_value=5.0,
            std_value=0.5,
            cloud_coverage=5.0,
            pixel_count=500,
        )
        # LAI values outside [-1,1] are valid; health status left empty
        assert result.health_status == ""
        assert result.health_status_ar == ""

    @pytest.mark.unit
    def test_default_data_source(self):
        result = _make_ndvi_result(0.5)
        assert result.data_source == "sentinel-2"

    @pytest.mark.unit
    def test_negative_ndvi_valid(self):
        """Negative NDVI (water bodies, bare soil) is valid within range."""
        result = _make_ndvi_result(-0.2)
        assert result.health_status == "critical"
        assert result.health_status_ar == "حرج"


# ─────────────────────────────────────────────────────────────────────────────
# TimeSeriesNDVI
# ─────────────────────────────────────────────────────────────────────────────


class TestTimeSeriesNDVI:
    @pytest.mark.unit
    def test_insufficient_data_trend(self):
        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 31, tzinfo=UTC),
            measurements=[_make_ndvi_result(0.5)],
        )
        ts.calculate_trend()
        assert ts.trend == "insufficient_data"
        assert ts.trend_ar == "بيانات غير كافية"

    @pytest.mark.unit
    def test_improving_trend(self):
        measurements = [
            _make_ndvi_result(0.3),
            _make_ndvi_result(0.35),
            _make_ndvi_result(0.5),
            _make_ndvi_result(0.6),
        ]
        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 20, tzinfo=UTC),
            measurements=measurements,
        )
        ts.calculate_trend()
        assert ts.trend == "improving"
        assert ts.trend_ar == "تحسن"

    @pytest.mark.unit
    def test_declining_trend(self):
        measurements = [
            _make_ndvi_result(0.7),
            _make_ndvi_result(0.65),
            _make_ndvi_result(0.4),
            _make_ndvi_result(0.3),
        ]
        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 20, tzinfo=UTC),
            measurements=measurements,
        )
        ts.calculate_trend()
        assert ts.trend == "declining"
        assert ts.trend_ar == "تراجع"

    @pytest.mark.unit
    def test_stable_trend(self):
        measurements = [
            _make_ndvi_result(0.5),
            _make_ndvi_result(0.52),
            _make_ndvi_result(0.51),
            _make_ndvi_result(0.50),
        ]
        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 20, tzinfo=UTC),
            measurements=measurements,
        )
        ts.calculate_trend()
        assert ts.trend == "stable"
        assert ts.trend_ar == "مستقر"

    @pytest.mark.unit
    def test_empty_measurements(self):
        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 1, 31, tzinfo=UTC),
        )
        assert ts.measurements == []
        ts.calculate_trend()
        assert ts.trend == "insufficient_data"


# ─────────────────────────────────────────────────────────────────────────────
# SentinelNDVIAnalyzer
# ─────────────────────────────────────────────────────────────────────────────


class TestSentinelNDVIAnalyzer:
    @pytest.mark.unit
    def test_init_no_credentials(self):
        analyzer = SentinelNDVIAnalyzer()
        assert analyzer.client_id is None
        assert analyzer.client_secret is None
        assert analyzer._initialized is False

    @pytest.mark.unit
    def test_init_with_credentials(self):
        analyzer = SentinelNDVIAnalyzer(
            client_id="test-id",
            client_secret="test-secret",
            instance_id="test-instance",
        )
        assert analyzer.client_id == "test-id"
        assert analyzer.client_secret == "test-secret"
        assert analyzer.instance_id == "test-instance"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_without_credentials_returns_false(self):
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.initialize()
        assert result is False
        assert analyzer._initialized is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_import_error(self):
        """When sentinelhub is not installed, initialize returns False."""
        analyzer = SentinelNDVIAnalyzer(
            client_id="test", client_secret="test"
        )
        with patch.dict("sys.modules", {"sentinelhub": None}):
            result = await analyzer.initialize()
        # The ImportError path returns False
        assert result is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_ndvi_falls_back_to_mock(self, sample_field, sample_date):
        """Without credentials, get_ndvi should return mock data."""
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.get_ndvi(sample_field, sample_date)
        assert result is not None
        assert result.field_id == "FIELD-001"
        assert result.data_source == "mock"
        assert result.index_type == VegetationIndex.NDVI
        assert -1.0 <= result.mean_value <= 1.0

    @pytest.mark.unit
    def test_mock_ndvi_data_source(self, sample_field, sample_date):
        analyzer = SentinelNDVIAnalyzer()
        result = analyzer._get_mock_ndvi(sample_field, sample_date)
        assert result.data_source == "mock"
        assert result.field_id == "FIELD-001"
        assert result.index_type == VegetationIndex.NDVI

    @pytest.mark.unit
    def test_mock_ndvi_pixel_count(self, sample_field, sample_date):
        """Pixel count should be area_hectares * 10000 / 100 (10m resolution)."""
        analyzer = SentinelNDVIAnalyzer()
        result = analyzer._get_mock_ndvi(sample_field, sample_date)
        assert result.pixel_count == 1000  # 10 ha * 10000 / 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_vegetation_index_ndvi(self, sample_field, sample_date):
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.get_vegetation_index(
            sample_field, VegetationIndex.NDVI, sample_date
        )
        assert result is not None
        assert result.index_type == VegetationIndex.NDVI

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_vegetation_index_lai(self, sample_field, sample_date):
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.get_vegetation_index(
            sample_field, VegetationIndex.LAI, sample_date
        )
        assert result is not None
        assert result.index_type == VegetationIndex.LAI
        # LAI values are clamped to [0, 8]
        assert 0.0 <= result.mean_value <= 8.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_vegetation_index_other(self, sample_field, sample_date):
        """Other indices reuse NDVI result with modified index_type."""
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.get_vegetation_index(
            sample_field, VegetationIndex.EVI, sample_date
        )
        assert result is not None
        assert result.index_type == VegetationIndex.EVI

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_crop_health_returns_dict(self, sample_field, sample_date):
        analyzer = SentinelNDVIAnalyzer()
        result = await analyzer.analyze_crop_health(sample_field, sample_date)
        assert isinstance(result, dict)
        assert "field_id" in result
        assert result["field_id"] == "FIELD-001"
        assert "health_status" in result
        assert "health_status_ar" in result
        assert "ndvi" in result
        assert "trend" in result
        assert "trend_ar" in result
        assert "recommendations" in result
        assert "recommendations_ar" in result
        assert "time_series" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_crop_health_recommendations_critical(self, sample_field):
        """Critical NDVI should produce irrigation and pest-check recommendations."""
        analyzer = SentinelNDVIAnalyzer()
        # Patch _get_mock_ndvi to return critical value
        critical_result = NDVIResult(
            field_id="FIELD-001",
            timestamp=datetime(2026, 3, 15, tzinfo=UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=0.1,
            min_value=0.0,
            max_value=0.2,
            std_value=0.05,
            cloud_coverage=5.0,
            pixel_count=1000,
            data_source="mock",
        )
        with patch.object(analyzer, "get_ndvi", new_callable=AsyncMock, return_value=critical_result):
            with patch.object(analyzer, "get_time_series", new_callable=AsyncMock) as mock_ts:
                mock_ts.return_value = TimeSeriesNDVI(
                    field_id="FIELD-001",
                    start_date=datetime(2026, 2, 13, tzinfo=UTC),
                    end_date=datetime(2026, 3, 15, tzinfo=UTC),
                    measurements=[critical_result],
                )
                mock_ts.return_value.calculate_trend()

                result = await analyzer.analyze_crop_health(sample_field)

        assert result["health_status"] == "critical"
        assert "Immediate irrigation required" in result["recommendations"]
        assert "مطلوب ري فوري" in result["recommendations_ar"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_crop_health_recommendations_stressed(self, sample_field):
        """Stressed NDVI should produce fertilization and moisture recommendations."""
        analyzer = SentinelNDVIAnalyzer()
        stressed_result = NDVIResult(
            field_id="FIELD-001",
            timestamp=datetime(2026, 3, 15, tzinfo=UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=0.3,
            min_value=0.2,
            max_value=0.4,
            std_value=0.05,
            cloud_coverage=5.0,
            pixel_count=1000,
            data_source="mock",
        )
        with patch.object(analyzer, "get_ndvi", new_callable=AsyncMock, return_value=stressed_result):
            with patch.object(analyzer, "get_time_series", new_callable=AsyncMock) as mock_ts:
                mock_ts.return_value = TimeSeriesNDVI(
                    field_id="FIELD-001",
                    start_date=datetime(2026, 2, 13, tzinfo=UTC),
                    end_date=datetime(2026, 3, 15, tzinfo=UTC),
                    measurements=[stressed_result],
                )
                mock_ts.return_value.calculate_trend()

                result = await analyzer.analyze_crop_health(sample_field)

        assert result["health_status"] == "stressed"
        assert "Consider additional fertilization" in result["recommendations"]
        assert "فكر في تسميد إضافي" in result["recommendations_ar"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_time_series(self, sample_field):
        analyzer = SentinelNDVIAnalyzer()
        start = datetime(2026, 3, 1, tzinfo=UTC)
        end = datetime(2026, 3, 15, tzinfo=UTC)
        ts = await analyzer.get_time_series(sample_field, start, end, interval_days=5)
        assert isinstance(ts, TimeSeriesNDVI)
        assert ts.field_id == "FIELD-001"
        assert ts.start_date == start
        assert ts.end_date == end
        # With 15 days and 5-day interval: days 1, 6, 11 = 3 measurements
        assert len(ts.measurements) == 3
        assert ts.trend != ""  # trend should be calculated


# ─────────────────────────────────────────────────────────────────────────────
# Module-level imports (from __init__.py)
# ─────────────────────────────────────────────────────────────────────────────


class TestModuleExports:
    @pytest.mark.unit
    def test_public_exports(self):
        """Verify all public names are importable from shared.satellite."""
        from shared.satellite import (
            FieldBoundary,
            NDVIResult,
            SentinelNDVIAnalyzer,
            TimeSeriesNDVI,
            VegetationIndex,
        )

        assert FieldBoundary is SatelliteFieldBoundary
        assert NDVIResult is not None
        assert SentinelNDVIAnalyzer is not None
        assert TimeSeriesNDVI is not None
        assert VegetationIndex is not None
