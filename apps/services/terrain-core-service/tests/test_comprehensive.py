"""
Comprehensive unit tests for Terrain Core Service.

Targets >60% code coverage across:
- schemas (enums, validators, geometry models, request/response models)
- config (Settings)
- algorithms/dem_processor (DEMBounds, DEMMetadata, DEMData, DEMProcessor)
- algorithms/terrain_indicators (TerrainIndicatorCalculator)
"""

import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

# Ensure service root is on path

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------
class TestConfig:
    """Test terrain service configuration."""

    def test_default_settings(self):
        from src.core.config import Settings

        s = Settings()
        assert s.SERVICE_NAME == "terrain-core-service"
        assert s.VERSION == "16.0.0"
        assert s.PORT == 8185
        assert s.DEFAULT_RESOLUTION_M == 30.0

    def test_default_dem_source(self):
        from src.core.config import DEMSource, Settings

        s = Settings()
        assert s.DEFAULT_DEM_SOURCE == DEMSource.COPERNICUS

    def test_resampling_method_enum(self):
        from src.core.config import ResamplingMethod

        assert ResamplingMethod.BILINEAR == "bilinear"
        assert ResamplingMethod.LANCZOS == "lanczos"
        assert len(ResamplingMethod) == 5
# ---------------------------------------------------------------------------
# Schema enum tests
# ---------------------------------------------------------------------------
class TestSchemaEnums:
    def test_dem_source_type(self):
        from src.api.schemas import DEMSourceType

        assert DEMSourceType.COPERNICUS == "copernicus"
        assert DEMSourceType.LOCAL == "local"
        assert len(DEMSourceType) == 4

    def test_slope_unit(self):
        from src.api.schemas import SlopeUnit

        assert SlopeUnit.DEGREES == "degrees"
        assert SlopeUnit.PERCENT == "percent"

    def test_aspect_classification(self):
        from src.api.schemas import AspectClassification

        assert AspectClassification.NORTH == "north"
        assert AspectClassification.FLAT == "flat"

    def test_flow_direction_method(self):
        from src.api.schemas import FlowDirectionMethod

        assert FlowDirectionMethod.D8 == "d8"
        assert FlowDirectionMethod.MFD == "mfd"

    def test_curvature_type(self):
        from src.api.schemas import CurvatureType

        assert CurvatureType.PLAN == "plan"
        assert CurvatureType.TOTAL == "total"

    def test_terrain_category(self):
        from src.api.schemas import TerrainCategory

        assert TerrainCategory.FLAT == "flat"
        assert TerrainCategory.VERY_STEEP == "very_steep"
# ---------------------------------------------------------------------------
# Schema model tests
# ---------------------------------------------------------------------------
class TestSchemaModels:
    def test_coordinate(self):
        from src.api.schemas import Coordinate

        c = Coordinate(longitude=46.7, latitude=24.7)
        assert c.longitude == 46.7

        with pytest.raises((ValueError, Exception)):
            Coordinate(longitude=200, latitude=24.7)

    def test_bounding_box_valid(self):
        from src.api.schemas import BoundingBox

        bb = BoundingBox(min_lon=46.0, min_lat=24.0, max_lon=47.0, max_lat=25.0)
        assert bb.min_lon == 46.0

    def test_bounding_box_invalid_lon(self):
        from src.api.schemas import BoundingBox

        with pytest.raises((ValueError, Exception)):
            BoundingBox(min_lon=47.0, min_lat=24.0, max_lon=46.0, max_lat=25.0)

    def test_bounding_box_invalid_lat(self):
        from src.api.schemas import BoundingBox

        with pytest.raises((ValueError, Exception)):
            BoundingBox(min_lon=46.0, min_lat=25.0, max_lon=47.0, max_lat=24.0)

    def test_bilingual_field(self):
        from src.api.schemas import BilingualField

        bf = BilingualField(en="Slope", ar="الميل")
        assert bf.en == "Slope"

    def test_geojson_point(self):
        from src.api.schemas import GeoJSONPoint

        p = GeoJSONPoint(coordinates=[46.7, 24.7])
        assert p.type == "Point"

    def test_geojson_polygon(self):
        from src.api.schemas import GeoJSONPolygon

        poly = GeoJSONPolygon(
            coordinates=[[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]]
        )
        assert poly.type == "Polygon"

    def test_field_geometry(self):
        from src.api.schemas import FieldGeometry, GeoJSONPolygon

        fg = FieldGeometry(
            field_id="FIELD-001",
            geometry=GeoJSONPolygon(
                coordinates=[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            ),
        )
        assert fg.crs == "EPSG:4326"

    def test_terrain_analysis_request_valid(self):
        from src.api.schemas import TerrainAnalysisRequest

        req = TerrainAnalysisRequest(field_id="FIELD-001")
        assert req.include_slope is True
        assert req.include_twi is True

    def test_terrain_analysis_request_empty_field_id(self):
        from src.api.schemas import TerrainAnalysisRequest

        with pytest.raises((ValueError, Exception)):
            TerrainAnalysisRequest(field_id="   ")

    def test_terrain_analysis_request_crs_validation(self):
        from src.api.schemas import TerrainAnalysisRequest

        req = TerrainAnalysisRequest(field_id="F1", target_crs="EPSG:4326")
        assert req.target_crs == "EPSG:4326"

        with pytest.raises((ValueError, Exception)):
            TerrainAnalysisRequest(field_id="F1", target_crs="INVALID")

    def test_contour_request_valid(self):
        from src.api.schemas import ContourRequest

        req = ContourRequest(field_id="F1", interval_m=10.0)
        assert req.simplify_tolerance == 1.0

    def test_contour_request_invalid_elevation_range(self):
        from src.api.schemas import ContourRequest

        with pytest.raises((ValueError, Exception)):
            ContourRequest(field_id="F1", min_elevation=500.0, max_elevation=400.0)

    def test_dem_source_info(self):
        from src.api.schemas import DEMSourceInfo

        info = DEMSourceInfo(
            source="copernicus",
            name="Copernicus DEM",
            name_ar="كوبرنيكوس",
            description="Global coverage",
            description_ar="تغطية عالمية",
            resolution_m=30.0,
            coverage="global",
        )
        assert info.is_available is True

    def test_terrain_error_detail(self):
        from src.api.schemas import TerrainErrorDetail

        err = TerrainErrorDetail(
            code="TERRAIN_001",
            message="DEM not found",
            message_ar="لم يتم العثور على بيانات الارتفاعات",
        )
        assert err.code == "TERRAIN_001"

    def test_slope_analysis_request(self):
        from src.api.schemas import SlopeAnalysisRequest

        req = SlopeAnalysisRequest(field_id="F1")
        assert req.classify is True

    def test_flow_analysis_request(self):
        from src.api.schemas import FlowAnalysisRequest

        req = FlowAnalysisRequest(field_id="F1", accumulation_threshold=500)
        assert req.accumulation_threshold == 500

    def test_twi_request(self):
        from src.api.schemas import TWIRequest

        req = TWIRequest(field_id="F1")
        assert req.dem_source == "copernicus"
# ---------------------------------------------------------------------------
# DEMBounds tests
# ---------------------------------------------------------------------------
class TestDEMBounds:
    def test_as_tuple(self):
        from src.algorithms.dem_processor import DEMBounds

        b = DEMBounds(min_lon=46.0, min_lat=24.0, max_lon=47.0, max_lat=25.0)
        assert b.as_tuple == (46.0, 24.0, 47.0, 25.0)
# ---------------------------------------------------------------------------
# DEMMetadata tests
# ---------------------------------------------------------------------------
class TestDEMMetadata:
    def test_to_dict(self):
        from src.algorithms.dem_processor import DEMBounds, DEMMetadata, DEMSource

        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=100,
            height=100,
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        d = meta.to_dict()
        assert d["source"] == "copernicus"
        assert d["width"] == 100
        assert d["acquisition_date"] is None

    def test_to_dict_with_acquisition(self):
        from src.algorithms.dem_processor import DEMBounds, DEMMetadata, DEMSource

        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        now = datetime.now()
        meta = DEMMetadata(
            source=DEMSource.SRTM,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=50,
            height=50,
            nodata_value=-9999.0,
            vertical_datum="EGM96",
            acquisition_date=now,
        )
        d = meta.to_dict()
        assert d["acquisition_date"] == now.isoformat()
# ---------------------------------------------------------------------------
# DEMData tests
# ---------------------------------------------------------------------------
class TestDEMData:
    def test_shape(self):
        from src.algorithms.dem_processor import DEMBounds, DEMData, DEMMetadata, DEMSource

        data = np.ones((10, 20), dtype=np.float32) * 500
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=20,
            height=10,
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        dem = DEMData(data=data, metadata=meta, transform=None, nodata_mask=np.zeros((10, 20), dtype=bool))
        assert dem.shape == (10, 20)

    def test_valid_data(self):
        from src.algorithms.dem_processor import DEMBounds, DEMData, DEMMetadata, DEMSource

        data = np.array([[500, 600], [700, -9999]], dtype=np.float32)
        mask = np.array([[False, False], [False, True]])
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=2,
            height=2,
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        dem = DEMData(data=data, metadata=meta, transform=None, nodata_mask=mask)
        valid = dem.valid_data
        assert valid[1, 1] is np.ma.masked
# ---------------------------------------------------------------------------
# DEMProcessor tests
# ---------------------------------------------------------------------------
class TestDEMProcessor:
    def test_init_defaults(self, tmp_path):
        from src.algorithms.dem_processor import DEMProcessor

        proc = DEMProcessor(cache_dir=str(tmp_path))
        assert proc.default_source.value == "copernicus"
        assert proc.default_resolution_m == 30.0

    def test_cache_key_generation(self, tmp_path):
        from src.algorithms.dem_processor import DEMBounds, DEMProcessor, DEMSource

        proc = DEMProcessor(cache_dir=str(tmp_path))
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        key = proc._get_cache_key(bounds, DEMSource.COPERNICUS, 30.0)
        assert isinstance(key, str) and len(key) == 32

    def test_get_cached_dem_path_miss(self, tmp_path):
        from src.algorithms.dem_processor import DEMProcessor

        proc = DEMProcessor(cache_dir=str(tmp_path))
        assert proc._get_cached_dem_path("nonexistent_key") is None

    def test_get_source_info(self, tmp_path):
        from src.algorithms.dem_processor import DEMProcessor, DEMSource

        proc = DEMProcessor(cache_dir=str(tmp_path))
        info = proc.get_source_info(DEMSource.COPERNICUS)
        assert info["name_en"] == "Copernicus DEM"
        assert info["has_30m"] is True

    def test_list_available_sources(self, tmp_path):
        from src.algorithms.dem_processor import DEMProcessor

        proc = DEMProcessor(cache_dir=str(tmp_path))
        sources = proc.list_available_sources()
        assert len(sources) == 4
        names = [s["source"] for s in sources]
        assert "copernicus" in names

    @pytest.mark.asyncio
    async def test_acquire_dem_synthetic(self, tmp_path):
        from src.algorithms.dem_processor import DEMBounds, DEMProcessor

        proc = DEMProcessor(cache_dir=str(tmp_path))
        bounds = DEMBounds(46.7, 24.7, 46.71, 24.71)
        dem = await proc.acquire_dem(bounds, use_cache=False)
        assert dem.data.shape[0] > 0
        assert dem.data.shape[1] > 0
        assert dem.metadata.source.value == "copernicus"

    @pytest.mark.asyncio
    async def test_acquire_dem_local_raises(self, tmp_path):
        from src.algorithms.dem_processor import DEMBounds, DEMProcessor, DEMSource

        proc = DEMProcessor(cache_dir=str(tmp_path))
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        with pytest.raises(ValueError, match="LOCAL source"):
            await proc.acquire_dem(bounds, source=DEMSource.LOCAL)

    @pytest.mark.asyncio
    async def test_fill_holes_no_holes(self, tmp_path):
        from src.algorithms.dem_processor import DEMBounds, DEMData, DEMMetadata, DEMProcessor, DEMSource

        proc = DEMProcessor(cache_dir=str(tmp_path))
        data = np.ones((10, 10), dtype=np.float32) * 500
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=10,
            height=10,
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        dem = DEMData(data=data, metadata=meta, transform=None, nodata_mask=np.zeros((10, 10), dtype=bool))
        result = await proc.fill_holes(dem)
        assert np.array_equal(result.data, data)

    @pytest.mark.asyncio
    async def test_close(self, tmp_path):
        from src.algorithms.dem_processor import DEMProcessor

        proc = DEMProcessor(cache_dir=str(tmp_path))
        await proc.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_resample_same_resolution(self, tmp_path):
        from src.algorithms.dem_processor import DEMBounds, DEMData, DEMMetadata, DEMProcessor, DEMSource

        proc = DEMProcessor(cache_dir=str(tmp_path))
        data = np.ones((10, 10), dtype=np.float32) * 500
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=10,
            height=10,
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        dem = DEMData(data=data, metadata=meta, transform=None, nodata_mask=np.zeros((10, 10), dtype=bool))
        result = await proc.resample(dem, 30.0)
        assert result is dem  # Same object since resolution matches
# ---------------------------------------------------------------------------
# TerrainIndicatorCalculator tests
# ---------------------------------------------------------------------------
class TestTerrainIndicatorCalculator:
    """Test all terrain indicator calculations."""

    def _make_dem_data(self, shape=(20, 20)):
        """Helper to create synthetic DEM data."""
        from src.algorithms.dem_processor import DEMBounds, DEMData, DEMMetadata, DEMSource

        np.random.seed(42)
        x = np.linspace(0, 2 * np.pi, shape[1])
        y = np.linspace(0, 2 * np.pi, shape[0])
        xx, yy = np.meshgrid(x, y)
        data = (500 + 50 * np.sin(xx) * np.cos(yy) + 5 * np.random.randn(*shape)).astype(np.float32)
        bounds = DEMBounds(46.0, 24.0, 47.0, 25.0)
        meta = DEMMetadata(
            source=DEMSource.COPERNICUS,
            resolution_m=30.0,
            crs="EPSG:4326",
            bounds=bounds,
            width=shape[1],
            height=shape[0],
            nodata_value=-9999.0,
            vertical_datum="EGM2008",
        )
        mask = np.zeros(shape, dtype=bool)
        return DEMData(data=data, metadata=meta, transform=None, nodata_mask=mask)

    def test_init(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        assert calc.cell_size_m == 30.0

    def test_calculate_slope_degrees(self):
        from src.algorithms.terrain_indicators import SlopeUnit, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_slope(dem, SlopeUnit.DEGREES)
        assert result.unit == SlopeUnit.DEGREES
        assert result.min_value >= 0
        assert result.max_value >= result.min_value
        assert result.data.shape == dem.data.shape

    def test_calculate_slope_percent(self):
        from src.algorithms.terrain_indicators import SlopeUnit, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_slope(dem, SlopeUnit.PERCENT)
        assert result.unit == SlopeUnit.PERCENT
        assert result.min_value >= 0

    def test_calculate_slope_radians(self):
        from src.algorithms.terrain_indicators import SlopeUnit, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_slope(dem, SlopeUnit.RADIANS)
        assert result.unit == SlopeUnit.RADIANS

    def test_slope_classification(self):
        from src.algorithms.terrain_indicators import SlopeUnit, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_slope(dem, SlopeUnit.DEGREES)
        assert "flat" in result.classification
        assert "steep" in result.classification
        total_pct = sum(result.classification.values())
        assert abs(total_pct - 100.0) < 1.0

    def test_calculate_aspect(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_aspect(dem)
        assert result.dominant_direction in ["flat", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        assert result.data.shape == dem.data.shape
        assert "N" in result.distribution

    def test_calculate_flow_direction(self):
        from src.algorithms.terrain_indicators import FlowMethod, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data((10, 10))  # Smaller for speed
        result = calc.calculate_flow_direction(dem, FlowMethod.D8)
        assert result.method == FlowMethod.D8
        assert result.data.shape == dem.data.shape
        assert result.dominant_direction in ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]

    def test_calculate_flow_accumulation(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data((10, 10))
        flow_dir = calc.calculate_flow_direction(dem)
        result = calc.calculate_flow_accumulation(dem, flow_dir, threshold=5)
        assert result.max_accumulation >= 1
        assert result.mean_accumulation >= 0
        assert result.threshold == 5

    def test_calculate_twi(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data((10, 10))
        result = calc.calculate_twi(dem)
        assert result.min_twi <= result.mean_twi <= result.max_twi
        assert 0 <= result.high_moisture_pct <= 100

    def test_calculate_curvature_plan(self):
        from src.algorithms.terrain_indicators import CurvatureType, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_curvature(dem, CurvatureType.PLAN)
        assert result.curvature_type == CurvatureType.PLAN
        assert result.convex_pct + result.concave_pct + result.flat_pct == pytest.approx(100.0, abs=0.1)

    def test_calculate_curvature_profile(self):
        from src.algorithms.terrain_indicators import CurvatureType, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_curvature(dem, CurvatureType.PROFILE)
        assert result.curvature_type == CurvatureType.PROFILE

    def test_calculate_curvature_total(self):
        from src.algorithms.terrain_indicators import CurvatureType, TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.calculate_curvature(dem, CurvatureType.TOTAL)
        assert result.curvature_type == CurvatureType.TOTAL

    def test_generate_contours(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data()
        result = calc.generate_contours(dem, interval_m=20.0)
        assert result.interval_m == 20.0
        assert result.major_interval_m == 100.0
        assert result.min_elevation <= result.max_elevation

    def test_calculate_all_indicators(self):
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator

        calc = TerrainIndicatorCalculator(cell_size_m=30.0)
        dem = self._make_dem_data((10, 10))
        results = calc.calculate_all_indicators(dem, contour_interval_m=10.0, flow_threshold=5)
        assert "slope" in results
        assert "aspect" in results
        assert "flow_direction" in results
        assert "flow_accumulation" in results
        assert "twi" in results
        assert "plan_curvature" in results
        assert "profile_curvature" in results
        assert "contours" in results
