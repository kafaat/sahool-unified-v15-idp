"""
Tests for cloud_masking module.
Tests cover CloudMasker, SCLClass, CloudMaskResult, ClearObservation,
quality scoring, interpolation methods, and all helper methods.
"""

import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cloud_masking import (
    ClearObservation,
    CloudMasker,
    CloudMaskResult,
    SCLClass,
    get_cloud_masker,
)

# =============================================================================
# SCLClass Tests
# =============================================================================


class TestSCLClass:
    def test_all_classes(self):
        assert SCLClass.NO_DATA.value == 0
        assert SCLClass.SATURATED.value == 1
        assert SCLClass.DARK_AREA.value == 2
        assert SCLClass.CLOUD_SHADOW.value == 3
        assert SCLClass.VEGETATION.value == 4
        assert SCLClass.BARE_SOIL.value == 5
        assert SCLClass.WATER.value == 6
        assert SCLClass.UNCLASSIFIED.value == 7
        assert SCLClass.CLOUD_MEDIUM.value == 8
        assert SCLClass.CLOUD_HIGH.value == 9
        assert SCLClass.THIN_CIRRUS.value == 10
        assert SCLClass.SNOW_ICE.value == 11

    def test_class_count(self):
        assert len(SCLClass) == 12


# =============================================================================
# CloudMaskResult Tests
# =============================================================================


class TestCloudMaskResult:
    def test_to_dict(self):
        ts = datetime(2025, 3, 15, 10, 30, 0)
        result = CloudMaskResult(
            field_id="F001",
            timestamp=ts,
            cloud_cover_percent=10.5,
            shadow_cover_percent=3.2,
            clear_cover_percent=80.0,
            usable=True,
            quality_score=0.85,
            scl_distribution={"VEGETATION": 80.0, "CLOUD_MEDIUM": 10.5},
            recommendation="Good quality",
        )
        d = result.to_dict()
        assert d["field_id"] == "F001"
        assert d["timestamp"] == "2025-03-15T10:30:00"
        assert d["cloud_cover_percent"] == 10.5
        assert d["usable"] is True
        assert d["quality_score"] == 0.85

    def test_to_dict_serialization(self):
        result = CloudMaskResult(
            field_id="F002",
            timestamp=datetime(2025, 1, 1),
            cloud_cover_percent=50.0,
            shadow_cover_percent=10.0,
            clear_cover_percent=30.0,
            usable=False,
            quality_score=0.3,
            scl_distribution={},
            recommendation="Too cloudy",
        )
        d = result.to_dict()
        assert isinstance(d["timestamp"], str)


# =============================================================================
# ClearObservation Tests
# =============================================================================


class TestClearObservation:
    def test_to_dict(self):
        obs = ClearObservation(
            date=datetime(2025, 3, 15),
            cloud_cover=5.0,
            quality_score=0.95,
            satellite="Sentinel-2A",
            shadow_cover=2.0,
            clear_pixels=90.0,
        )
        d = obs.to_dict()
        assert d["date"] == "2025-03-15T00:00:00"
        assert d["cloud_cover"] == 5.0
        assert d["satellite"] == "Sentinel-2A"

    def test_defaults(self):
        obs = ClearObservation(
            date=datetime(2025, 1, 1),
            cloud_cover=10.0,
            quality_score=0.8,
            satellite="Sentinel-2B",
        )
        assert obs.shadow_cover == 0.0
        assert obs.clear_pixels == 0.0


# =============================================================================
# CloudMasker Tests
# =============================================================================


class TestCloudMasker:
    @pytest.fixture
    def masker(self):
        return CloudMasker()

    def test_class_constants(self, masker):
        assert masker.MAX_CLOUD_COVER == 20.0
        assert masker.MIN_CLEAR_PIXELS == 70.0
        assert masker.MIN_QUALITY_SCORE == 0.6
        assert SCLClass.CLOUD_MEDIUM in masker.CLOUD_CLASSES
        assert SCLClass.CLOUD_HIGH in masker.CLOUD_CLASSES
        assert SCLClass.THIN_CIRRUS in masker.CLOUD_CLASSES
        assert SCLClass.CLOUD_SHADOW in masker.SHADOW_CLASSES
        assert SCLClass.VEGETATION in masker.VALID_CLASSES

    # =========================================================================
    # calculate_quality_score Tests
    # =========================================================================

    def test_quality_score_excellent(self, masker):
        # <5% cloud, <5% shadow, >90% clear
        score = masker.calculate_quality_score(2.0, 2.0, 95.0)
        assert score > 0.9
        assert score <= 1.0

    def test_quality_score_good(self, masker):
        # <10% cloud, <10% shadow, >80% clear
        score = masker.calculate_quality_score(8.0, 8.0, 82.0)
        assert score > 0.7

    def test_quality_score_poor(self, masker):
        score = masker.calculate_quality_score(50.0, 20.0, 30.0)
        assert score < 0.5

    def test_quality_score_zero_case(self, masker):
        score = masker.calculate_quality_score(100.0, 100.0, 0.0)
        assert score >= 0.0

    def test_quality_score_perfect(self, masker):
        score = masker.calculate_quality_score(0.0, 0.0, 100.0)
        assert abs(score - 1.0) < 1e-10

    # =========================================================================
    # apply_cloud_mask Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_mask_cloud_medium(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.CLOUD_MEDIUM)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_cloud_high(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.CLOUD_HIGH)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_thin_cirrus(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.THIN_CIRRUS)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_shadow(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.CLOUD_SHADOW)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_dark_area(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.DARK_AREA)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_no_data(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.NO_DATA)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_saturated(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.SATURATED)
        assert result is None

    @pytest.mark.asyncio
    async def test_mask_unclassified(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.UNCLASSIFIED)
        assert result is None

    @pytest.mark.asyncio
    async def test_valid_vegetation(self, masker):
        result = await masker.apply_cloud_mask(0.7, SCLClass.VEGETATION)
        assert result == 0.7

    @pytest.mark.asyncio
    async def test_valid_bare_soil(self, masker):
        result = await masker.apply_cloud_mask(0.3, SCLClass.BARE_SOIL)
        assert result == 0.3

    @pytest.mark.asyncio
    async def test_valid_water(self, masker):
        result = await masker.apply_cloud_mask(-0.2, SCLClass.WATER)
        assert result == -0.2

    @pytest.mark.asyncio
    async def test_mask_snow_ice(self, masker):
        # SNOW_ICE is not in VALID_CLASSES, CLOUD_CLASSES, SHADOW_CLASSES, or INVALID_CLASSES
        result = await masker.apply_cloud_mask(0.5, SCLClass.SNOW_ICE)
        assert result is None

    # =========================================================================
    # analyze_cloud_cover Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_analyze_with_scl_data_clear(self, masker):
        # Mostly vegetation = clear scene
        scl_data = [SCLClass.VEGETATION.value] * 90 + [SCLClass.BARE_SOIL.value] * 10
        result = await masker.analyze_cloud_cover("F001", 15.5, 44.2, scl_data=scl_data)
        assert result.field_id == "F001"
        assert result.cloud_cover_percent == 0.0
        assert result.clear_cover_percent == 100.0
        assert result.usable is True
        assert result.quality_score > 0.9

    @pytest.mark.asyncio
    async def test_analyze_with_scl_data_cloudy(self, masker):
        # Mostly clouds
        scl_data = [SCLClass.CLOUD_HIGH.value] * 80 + [SCLClass.VEGETATION.value] * 20
        result = await masker.analyze_cloud_cover("F001", 15.5, 44.2, scl_data=scl_data)
        assert result.cloud_cover_percent == 80.0
        assert result.clear_cover_percent == 20.0
        assert result.usable is False

    @pytest.mark.asyncio
    async def test_analyze_with_mixed_clouds(self, masker):
        scl_data = (
            [SCLClass.CLOUD_MEDIUM.value] * 10
            + [SCLClass.THIN_CIRRUS.value] * 5
            + [SCLClass.CLOUD_SHADOW.value] * 5
            + [SCLClass.VEGETATION.value] * 75
            + [SCLClass.BARE_SOIL.value] * 5
        )
        result = await masker.analyze_cloud_cover("F001", 15.5, 44.2, scl_data=scl_data)
        assert result.cloud_cover_percent == 15.0  # 10 + 5 cloud
        assert result.shadow_cover_percent == 5.0  # Only CLOUD_SHADOW is in SHADOW_CLASSES for this data
        assert result.usable is True  # cloud < 20, clear >= 70

    @pytest.mark.asyncio
    async def test_analyze_auto_date(self, masker):
        scl_data = [SCLClass.VEGETATION.value] * 100
        result = await masker.analyze_cloud_cover("F001", 15.5, 44.2, scl_data=scl_data)
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_analyze_fetches_scl_data(self, masker):
        """Test that analyze_cloud_cover fetches SCL data when not provided."""
        result = await masker.analyze_cloud_cover("F001", 15.5, 44.2, date=datetime(2025, 1, 15))
        assert result is not None
        assert result.field_id == "F001"
        assert 0 <= result.cloud_cover_percent <= 100
        assert 0 <= result.quality_score <= 1

    # =========================================================================
    # _calculate_scl_distribution Tests
    # =========================================================================

    def test_distribution_empty(self, masker):
        result = masker._calculate_scl_distribution([])
        assert result == {}

    def test_distribution_all_vegetation(self, masker):
        scl_data = [SCLClass.VEGETATION.value] * 10
        result = masker._calculate_scl_distribution(scl_data)
        assert result["VEGETATION"] == 100.0

    def test_distribution_mixed(self, masker):
        scl_data = [SCLClass.VEGETATION.value] * 7 + [SCLClass.CLOUD_HIGH.value] * 3
        result = masker._calculate_scl_distribution(scl_data)
        assert result["VEGETATION"] == 70.0
        assert result["CLOUD_HIGH"] == 30.0

    def test_distribution_unknown_value(self, masker):
        scl_data = [SCLClass.VEGETATION.value] * 5 + [99] * 5
        result = masker._calculate_scl_distribution(scl_data)
        assert result["VEGETATION"] == 50.0
        assert result["UNKNOWN"] == 50.0

    # =========================================================================
    # _calculate coverage Tests
    # =========================================================================

    def test_cloud_cover(self, masker):
        dist = {"CLOUD_MEDIUM": 10.0, "CLOUD_HIGH": 5.0, "THIN_CIRRUS": 3.0, "VEGETATION": 82.0}
        assert masker._calculate_cloud_cover(dist) == 18.0

    def test_shadow_cover(self, masker):
        dist = {"CLOUD_SHADOW": 5.0, "DARK_AREA": 3.0, "VEGETATION": 92.0}
        assert masker._calculate_shadow_cover(dist) == 8.0

    def test_clear_cover(self, masker):
        dist = {"VEGETATION": 70.0, "BARE_SOIL": 10.0, "WATER": 5.0}
        assert masker._calculate_clear_cover(dist) == 85.0

    def test_cloud_cover_empty(self, masker):
        assert masker._calculate_cloud_cover({}) == 0.0

    # =========================================================================
    # _generate_recommendation Tests
    # =========================================================================

    def test_recommendation_excellent(self, masker):
        rec = masker._generate_recommendation(2.0, 1.0, 95.0, True)
        assert "Excellent" in rec

    def test_recommendation_good(self, masker):
        rec = masker._generate_recommendation(8.0, 5.0, 85.0, True)
        assert "Good" in rec

    def test_recommendation_acceptable(self, masker):
        rec = masker._generate_recommendation(18.0, 5.0, 72.0, True)
        assert "Acceptable" in rec

    def test_recommendation_too_cloudy(self, masker):
        rec = masker._generate_recommendation(30.0, 5.0, 60.0, False)
        assert "cloudy" in rec.lower()

    def test_recommendation_insufficient_clear(self, masker):
        rec = masker._generate_recommendation(15.0, 20.0, 50.0, False)
        assert "clear pixels" in rec.lower() or "low quality" in rec.lower()

    def test_recommendation_low_quality(self, masker):
        rec = masker._generate_recommendation(19.0, 19.0, 62.0, False)
        assert "quality" in rec.lower() or "date" in rec.lower()

    # =========================================================================
    # _get_satellite_name Tests
    # =========================================================================

    def test_satellite_name_a(self, masker):
        # Day of year 1 => 1 % 10 = 1 < 5 => Sentinel-2A
        name = masker._get_satellite_name(datetime(2025, 1, 1))
        assert name == "Sentinel-2A"

    def test_satellite_name_b(self, masker):
        # Day of year 6 => 6 % 10 = 6 >= 5 => Sentinel-2B
        name = masker._get_satellite_name(datetime(2025, 1, 6))
        assert name == "Sentinel-2B"

    # =========================================================================
    # find_clear_observations Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_find_clear_observations(self, masker):
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 30)
        observations = await masker.find_clear_observations("F001", 15.5, 44.2, start, end)
        assert isinstance(observations, list)
        # Sorted by quality (descending)
        for i in range(len(observations) - 1):
            assert observations[i].quality_score >= observations[i + 1].quality_score

    @pytest.mark.asyncio
    async def test_find_clear_observations_narrow_range(self, masker):
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 3)  # Narrow range, likely 0-1 observations
        observations = await masker.find_clear_observations("F001", 15.5, 44.2, start, end)
        assert isinstance(observations, list)

    # =========================================================================
    # get_best_observation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_best_observation(self, masker):
        result = await masker.get_best_observation("F001", 15.5, 44.2, datetime(2025, 1, 15))
        # May or may not find one depending on simulated data
        if result is not None:
            assert isinstance(result, ClearObservation)
            assert result.cloud_cover <= 20.0

    # =========================================================================
    # Interpolation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_interpolate_no_cloudy(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.5, "cloudy": False},
            {"date": "2025-01-10", "ndvi": 0.6, "cloudy": False},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series)
        assert result == series

    @pytest.mark.asyncio
    async def test_interpolate_empty_series(self, masker):
        result = await masker.interpolate_cloudy_pixels("F001", [])
        assert result == []

    @pytest.mark.asyncio
    async def test_interpolate_insufficient_valid(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.5, "cloudy": False},
            {"date": "2025-01-10", "ndvi": None, "cloudy": True},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_interpolate_linear(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.4, "cloudy": False},
            {"date": "2025-01-11", "ndvi": None, "cloudy": True},
            {"date": "2025-01-21", "ndvi": 0.8, "cloudy": False},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series, method="linear")
        assert result[1].get("interpolated") is True
        assert result[1]["interpolation_method"] == "linear"
        assert 0.55 <= result[1]["ndvi"] <= 0.65  # Should be ~0.6

    @pytest.mark.asyncio
    async def test_interpolate_previous(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.4, "cloudy": False},
            {"date": "2025-01-11", "ndvi": None, "cloudy": True},
            {"date": "2025-01-21", "ndvi": 0.8, "cloudy": False},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series, method="previous")
        assert result[1]["ndvi"] == 0.4  # Forward fill from previous

    @pytest.mark.asyncio
    async def test_interpolate_spline(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.3, "cloudy": False},
            {"date": "2025-01-11", "ndvi": 0.5, "cloudy": False},
            {"date": "2025-01-21", "ndvi": None, "cloudy": True},
            {"date": "2025-01-31", "ndvi": 0.7, "cloudy": False},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series, method="spline")
        assert result[2].get("interpolated") is True

    @pytest.mark.asyncio
    async def test_interpolate_unknown_method(self, masker):
        series = [
            {"date": "2025-01-01", "ndvi": 0.4, "cloudy": False},
            {"date": "2025-01-11", "ndvi": None, "cloudy": True},
            {"date": "2025-01-21", "ndvi": 0.8, "cloudy": False},
        ]
        result = await masker.interpolate_cloudy_pixels("F001", series, method="unknown_method")
        # Unknown method - value should not be interpolated
        assert result[1].get("interpolated") is None or result[1].get("interpolated") is not True

    # =========================================================================
    # Linear Interpolation Helper Tests
    # =========================================================================

    def test_linear_interpolate_basic(self, masker):
        valid_obs = [
            {"date": "2025-01-01", "ndvi": 0.4},
            {"date": "2025-01-21", "ndvi": 0.8},
        ]
        result = masker._linear_interpolate(datetime(2025, 1, 11), valid_obs)
        assert result is not None
        assert 0.55 <= result <= 0.65

    def test_linear_interpolate_same_date(self, masker):
        valid_obs = [{"date": "2025-01-10", "ndvi": 0.5}]
        result = masker._linear_interpolate(datetime(2025, 1, 10), valid_obs)
        # Only one observation acts as both before and after
        assert result == 0.5

    def test_linear_interpolate_no_before(self, masker):
        valid_obs = [{"date": "2025-01-20", "ndvi": 0.5}]
        result = masker._linear_interpolate(datetime(2025, 1, 10), valid_obs)
        assert result is None

    def test_linear_interpolate_no_after(self, masker):
        valid_obs = [{"date": "2025-01-01", "ndvi": 0.5}]
        result = masker._linear_interpolate(datetime(2025, 1, 10), valid_obs)
        assert result is None

    # =========================================================================
    # Previous Interpolation Helper Tests
    # =========================================================================

    def test_previous_interpolate_basic(self, masker):
        valid_obs = [
            {"date": "2025-01-01", "ndvi": 0.4},
            {"date": "2025-01-21", "ndvi": 0.8},
        ]
        result = masker._previous_interpolate(datetime(2025, 1, 11), valid_obs)
        assert result == 0.4

    def test_previous_interpolate_no_previous(self, masker):
        valid_obs = [{"date": "2025-01-20", "ndvi": 0.5}]
        result = masker._previous_interpolate(datetime(2025, 1, 10), valid_obs)
        assert result is None

    # =========================================================================
    # Spline Interpolation Helper Tests
    # =========================================================================

    def test_spline_interpolate_few_points(self, masker):
        # < 3 points falls back to linear
        valid_obs = [
            {"date": "2025-01-01", "ndvi": 0.4},
            {"date": "2025-01-21", "ndvi": 0.8},
        ]
        result = masker._spline_interpolate(datetime(2025, 1, 11), valid_obs)
        assert result is not None

    def test_spline_interpolate_enough_points(self, masker):
        valid_obs = [
            {"date": "2025-01-01", "ndvi": 0.3},
            {"date": "2025-01-10", "ndvi": 0.5},
            {"date": "2025-01-20", "ndvi": 0.7},
            {"date": "2025-01-30", "ndvi": 0.6},
        ]
        result = masker._spline_interpolate(datetime(2025, 1, 15), valid_obs)
        assert result is not None

    # =========================================================================
    # Singleton Tests
    # =========================================================================

    def test_get_cloud_masker_singleton(self):
        m1 = get_cloud_masker()
        m2 = get_cloud_masker()
        assert m1 is m2
        assert isinstance(m1, CloudMasker)
