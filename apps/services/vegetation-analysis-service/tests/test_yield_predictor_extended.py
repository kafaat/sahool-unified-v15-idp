"""
Tests for yield_predictor module.
Tests cover YieldPredictor methods: NDVI integral, GDD, water stress,
yield predictions, growth stage, confidence, and recommendations.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.yield_predictor import YieldPredictor, YieldPrediction


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def predictor():
    return YieldPredictor()


# =============================================================================
# calculate_ndvi_integral Tests
# =============================================================================


class TestNDVIIntegral:
    def test_basic_series(self, predictor):
        series = [0.3, 0.5, 0.7, 0.8, 0.6]
        result = predictor.calculate_ndvi_integral(series)
        assert result > 0

    def test_empty_series(self, predictor):
        assert predictor.calculate_ndvi_integral([]) == 0.0

    def test_single_value(self, predictor):
        assert predictor.calculate_ndvi_integral([0.5]) == 0.0

    def test_two_values(self, predictor):
        result = predictor.calculate_ndvi_integral([0.4, 0.6])
        assert result == 0.5  # (0.4 + 0.6) / 2

    def test_constant_series(self, predictor):
        series = [0.5, 0.5, 0.5, 0.5]
        result = predictor.calculate_ndvi_integral(series)
        assert result == 1.5  # 3 intervals * 0.5


# =============================================================================
# calculate_gdd Tests
# =============================================================================


class TestCalculateGDD:
    def test_basic(self, predictor):
        temp_min = [10.0, 12.0, 15.0]
        temp_max = [25.0, 28.0, 30.0]
        result = predictor.calculate_gdd(temp_min, temp_max, base_temp=10.0)
        assert result > 0

    def test_empty_series(self, predictor):
        assert predictor.calculate_gdd([], []) == 0.0

    def test_below_base(self, predictor):
        temp_min = [3.0, 5.0]
        temp_max = [8.0, 9.0]
        result = predictor.calculate_gdd(temp_min, temp_max, base_temp=10.0)
        assert result == 0.0

    def test_unequal_lengths(self, predictor):
        temp_min = [10.0, 12.0, 15.0]
        temp_max = [25.0, 28.0]
        result = predictor.calculate_gdd(temp_min, temp_max, base_temp=10.0)
        # Should use min(len) = 2
        assert result > 0


# =============================================================================
# calculate_water_stress Tests
# =============================================================================


class TestWaterStress:
    def test_no_stress(self, predictor):
        result = predictor.calculate_water_stress(
            precipitation=200.0, et0=150.0, kc=1.0, soil_moisture=0.5
        )
        assert result >= 0.9

    def test_full_stress(self, predictor):
        result = predictor.calculate_water_stress(
            precipitation=0.0, et0=200.0, kc=1.0, soil_moisture=0.1
        )
        assert result < 0.5

    def test_no_soil_moisture(self, predictor):
        result = predictor.calculate_water_stress(
            precipitation=100.0, et0=200.0, kc=1.0, soil_moisture=None
        )
        assert 0 <= result <= 1

    def test_zero_et0(self, predictor):
        result = predictor.calculate_water_stress(
            precipitation=100.0, et0=0.0, kc=1.0, soil_moisture=0.5
        )
        assert result == 1.0

    def test_low_soil_moisture(self, predictor):
        result = predictor.calculate_water_stress(
            precipitation=100.0, et0=100.0, kc=1.0, soil_moisture=0.1
        )
        assert result < 1.0


# =============================================================================
# predict_from_ndvi Tests
# =============================================================================


class TestPredictFromNDVI:
    def test_wheat_above_baseline(self, predictor):
        result = predictor.predict_from_ndvi("WHEAT", 2.0, 0.7, 50.0)
        assert result > 0

    def test_wheat_below_baseline(self, predictor):
        result = predictor.predict_from_ndvi("WHEAT", 2.0, 0.7, 30.0)
        assert result > 0

    def test_low_peak_ndvi(self, predictor):
        result = predictor.predict_from_ndvi("WHEAT", 2.0, 0.3, 45.0)
        # Peak below minimum causes penalty
        assert result < 2.0

    def test_unknown_crop_uses_default(self, predictor):
        result = predictor.predict_from_ndvi("UNKNOWN_CROP", 2.0, 0.7, 45.0)
        assert result > 0


# =============================================================================
# predict_from_gdd Tests
# =============================================================================


class TestPredictFromGDD:
    def test_optimal_gdd(self, predictor):
        result = predictor.predict_from_gdd("WHEAT", 2.0, 2000.0)
        assert result >= 1.8  # Should be close to base yield

    def test_below_minimum(self, predictor):
        result = predictor.predict_from_gdd("WHEAT", 2.0, 500.0)
        assert result < 2.0

    def test_above_maximum(self, predictor):
        result = predictor.predict_from_gdd("WHEAT", 2.0, 4000.0)
        assert result < 2.0

    def test_between_min_and_optimal(self, predictor):
        result = predictor.predict_from_gdd("WHEAT", 2.0, 1700.0)
        assert 0.5 < result < 2.5

    def test_between_optimal_and_max(self, predictor):
        result = predictor.predict_from_gdd("WHEAT", 2.0, 2200.0)
        assert 0.5 < result < 2.5

    def test_unknown_crop(self, predictor):
        result = predictor.predict_from_gdd("UNKNOWN", 2.0, 2000.0)
        assert result > 0


# =============================================================================
# predict_from_soil_moisture Tests
# =============================================================================


class TestPredictFromSoilMoisture:
    def test_optimal_moisture(self, predictor):
        result = predictor.predict_from_soil_moisture(2.0, 0.5)
        assert result == 2.0

    def test_low_moisture(self, predictor):
        result = predictor.predict_from_soil_moisture(2.0, 0.2)
        assert result < 2.0

    def test_high_moisture(self, predictor):
        result = predictor.predict_from_soil_moisture(2.0, 0.8)
        assert result < 2.0

    def test_none_moisture(self, predictor):
        result = predictor.predict_from_soil_moisture(2.0, None)
        assert result == 2.0  # Assumes optimal

    def test_very_low_moisture(self, predictor):
        result = predictor.predict_from_soil_moisture(2.0, 0.05)
        assert result > 0  # Min factor is 0.4


# =============================================================================
# estimate_growth_stage Tests
# =============================================================================


class TestEstimateGrowthStage:
    def test_no_planting_date(self, predictor):
        stage, days = predictor.estimate_growth_stage(None, 0, "WHEAT", None)
        assert stage == "unknown"
        assert days is None

    def test_germination(self, predictor):
        planting = datetime.now(timezone.utc) - timedelta(days=5)
        stage, days = predictor.estimate_growth_stage(planting, 50, "WHEAT", None)
        assert stage == "germination"

    def test_vegetative(self, predictor):
        planting = datetime.now(timezone.utc) - timedelta(days=25)
        stage, days = predictor.estimate_growth_stage(planting, 300, "WHEAT", None)
        assert stage == "vegetative"

    def test_flowering(self, predictor):
        planting = datetime.now(timezone.utc) - timedelta(days=50)
        stage, days = predictor.estimate_growth_stage(planting, 800, "WHEAT", None)
        assert stage == "flowering"

    def test_harvest_ready(self, predictor):
        planting = datetime.now(timezone.utc) - timedelta(days=200)
        stage, days = predictor.estimate_growth_stage(planting, 2000, "WHEAT", None)
        assert stage == "harvest_ready"
        assert days == 0


# =============================================================================
# calculate_confidence Tests
# =============================================================================


class TestCalculateConfidence:
    def test_good_data(self, predictor):
        result = predictor.calculate_confidence(
            ndvi_series=[0.4, 0.5, 0.6, 0.7, 0.8],
            ndvi_peak=0.8,
            gdd=2000,
            water_stress_factor=0.9,
            model_variance=[2.0, 2.1, 1.9, 2.0],
        )
        assert result > 0.7

    def test_poor_ndvi_data(self, predictor):
        result = predictor.calculate_confidence(
            ndvi_series=[0.3],
            ndvi_peak=0.3,
            gdd=500,
            water_stress_factor=0.4,
            model_variance=[1.0, 3.0, 0.5, 2.5],
        )
        assert result < 0.7

    def test_empty_ndvi(self, predictor):
        result = predictor.calculate_confidence(
            ndvi_series=[],
            ndvi_peak=0.0,
            gdd=0,
            water_stress_factor=0.5,
            model_variance=[1.0, 1.0],
        )
        assert 0.3 <= result <= 1.0

    def test_low_peak_ndvi(self, predictor):
        result = predictor.calculate_confidence(
            ndvi_series=[0.1, 0.2, 0.3, 0.2, 0.1],
            ndvi_peak=0.3,
            gdd=1000,
            water_stress_factor=0.8,
            model_variance=[1.0, 1.0, 1.0, 1.0],
        )
        assert result < 0.9

    def test_high_model_variance(self, predictor):
        result = predictor.calculate_confidence(
            ndvi_series=[0.5, 0.6, 0.7, 0.8, 0.7],
            ndvi_peak=0.8,
            gdd=2000,
            water_stress_factor=0.9,
            model_variance=[0.5, 5.0, 1.0, 3.0],  # High variance
        )
        # High variance should reduce confidence
        assert result < 1.0


# =============================================================================
# predict_yield Integration Tests
# =============================================================================


class TestPredictYield:
    @pytest.mark.asyncio
    async def test_basic_prediction(self, predictor):
        result = await predictor.predict_yield(
            field_id="F001",
            crop_code="WHEAT",
            ndvi_series=[0.3, 0.5, 0.7, 0.75, 0.7, 0.5],
            weather_data={
                "temp_min_series": [5.0] * 120,
                "temp_max_series": [20.0] * 120,
                "precipitation_mm": 200.0,
            },
            soil_moisture=0.5,
            planting_date=datetime.now(timezone.utc) - timedelta(days=90),
        )
        assert isinstance(result, YieldPrediction)
        assert result.field_id == "F001"
        assert result.predicted_yield_ton_ha > 0
        assert result.yield_range_min <= result.predicted_yield_ton_ha
        assert result.yield_range_max >= result.predicted_yield_ton_ha
        assert 0 < result.confidence <= 1
        assert len(result.recommendations_en) > 0
        assert len(result.recommendations_ar) > 0

    @pytest.mark.asyncio
    async def test_unknown_crop(self, predictor):
        result = await predictor.predict_yield(
            field_id="F002",
            crop_code="UNKNOWN_CROP",
            ndvi_series=[0.4, 0.6, 0.7],
            weather_data={
                "temp_min_series": [10.0] * 60,
                "temp_max_series": [25.0] * 60,
                "precipitation_mm": 150.0,
            },
        )
        assert result.predicted_yield_ton_ha > 0

    @pytest.mark.asyncio
    async def test_no_planting_date(self, predictor):
        result = await predictor.predict_yield(
            field_id="F003",
            crop_code="TOMATO",
            ndvi_series=[0.5, 0.7, 0.8],
            weather_data={
                "temp_min_series": [15.0] * 90,
                "temp_max_series": [30.0] * 90,
                "precipitation_mm": 100.0,
            },
        )
        assert result.growth_stage == "unknown"


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    def test_yemen_average_yields(self, predictor):
        assert "WHEAT" in predictor.YEMEN_AVERAGE_YIELDS
        assert "TOMATO" in predictor.YEMEN_AVERAGE_YIELDS
        assert predictor.YEMEN_AVERAGE_YIELDS["WHEAT"] > 0

    def test_ndvi_coefficients(self, predictor):
        assert "WHEAT" in predictor.NDVI_YIELD_COEFFICIENTS
        assert "DEFAULT" in predictor.NDVI_YIELD_COEFFICIENTS

    def test_gdd_requirements(self, predictor):
        assert "WHEAT" in predictor.GDD_REQUIREMENTS
        assert "DEFAULT" in predictor.GDD_REQUIREMENTS

    def test_water_stress_ky(self, predictor):
        assert "WHEAT" in predictor.WATER_STRESS_KY
        assert "DEFAULT" in predictor.WATER_STRESS_KY


# =============================================================================
# get_yield_factors Tests
# =============================================================================


class TestGetYieldFactors:
    def test_basic_factors(self, predictor):
        factors = predictor.get_yield_factors(
            ndvi_peak=0.7, ndvi_integral=50.0, gdd=2000,
            precipitation=200, water_stress_factor=0.9,
            soil_moisture=0.5, crop_code="WHEAT",
        )
        assert "vegetation_health" in factors
        assert "biomass_accumulation" in factors
        assert "thermal_time" in factors
        assert "water_availability" in factors
        assert "soil_moisture" in factors
        assert all(0 <= v <= 1 for v in factors.values())

    def test_low_values(self, predictor):
        factors = predictor.get_yield_factors(
            ndvi_peak=0.2, ndvi_integral=10.0, gdd=500,
            precipitation=50, water_stress_factor=0.3,
            soil_moisture=0.1, crop_code="WHEAT",
        )
        assert factors["vegetation_health"] < 0.5
        assert factors["water_availability"] < 0.5


# =============================================================================
# _normalize_gdd Tests
# =============================================================================


class TestNormalizeGDD:
    def test_zero_gdd(self, predictor):
        assert predictor._normalize_gdd(0.0, "WHEAT") == 0.0

    def test_optimal_gdd(self, predictor):
        assert predictor._normalize_gdd(2000.0, "WHEAT") == 1.0

    def test_above_optimal(self, predictor):
        result = predictor._normalize_gdd(3000.0, "WHEAT")
        assert 0.5 <= result < 1.0


# =============================================================================
# generate_recommendations Tests
# =============================================================================


class TestGenerateRecommendations:
    def test_water_stress_recommendations(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.7, water_stress_factor=0.4, soil_moisture=0.3,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=1.5, base_yield=2.0,
            factors={"vegetation_health": 0.8, "water_availability": 0.4},
        )
        assert any("water" in r.lower() or "irrigation" in r.lower() for r in en)

    def test_high_soil_moisture(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.7, water_stress_factor=0.9, soil_moisture=0.8,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=2.0, base_yield=2.0,
            factors={"vegetation_health": 0.8},
        )
        assert any("moisture" in r.lower() or "reduce" in r.lower() for r in en)

    def test_poor_vegetation(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.3, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=1.0, base_yield=2.0,
            factors={"vegetation_health": 0.3},
        )
        assert any("vegetation" in r.lower() or "nitrogen" in r.lower() for r in en)

    def test_excellent_performance(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.85, water_stress_factor=0.95, soil_moisture=0.5,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=3.0, base_yield=2.0,
            factors={"vegetation_health": 1.0, "water_availability": 0.95},
        )
        assert any("excellent" in r.lower() for r in en)

    def test_flowering_stage(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.7, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=2000, growth_stage="flowering",
            predicted_yield=2.0, base_yield=2.0,
            factors={},
        )
        assert any("flowering" in r.lower() for r in en)

    def test_fruiting_stage(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="TOMATO", crop_name_ar="طماطم", crop_name_en="Tomato",
            ndvi_peak=0.8, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=1000, growth_stage="fruiting",
            predicted_yield=25.0, base_yield=25.0,
            factors={},
        )
        assert any("fruiting" in r.lower() for r in en)

    def test_ripening_stage(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.6, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=2000, growth_stage="ripening",
            predicted_yield=2.0, base_yield=2.0,
            factors={},
        )
        assert any("ripening" in r.lower() for r in en)

    def test_no_issues(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.8, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=2.0, base_yield=2.0,
            factors={"vegetation_health": 0.9, "water_availability": 0.9},
        )
        assert len(en) >= 1

    def test_critical_factors(self, predictor):
        ar, en = predictor.generate_recommendations(
            crop_code="WHEAT", crop_name_ar="قمح", crop_name_en="Wheat",
            ndvi_peak=0.7, water_stress_factor=0.9, soil_moisture=0.5,
            gdd=2000, growth_stage="vegetative",
            predicted_yield=1.5, base_yield=2.0,
            factors={"vegetation_health": 0.3, "soil_moisture": 0.2},
        )
        assert any("critical" in r.lower() for r in en)
