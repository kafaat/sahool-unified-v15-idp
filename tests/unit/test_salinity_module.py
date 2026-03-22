"""Unit tests for shared/salinity module."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.salinity import (
    SalinityModule,
    SalinityRisk,
    adjust_kc_for_salinity,
    calculate_leaching_fraction,
    calculate_sar,
    calculate_yield_reduction,
    classify_salinity_risk,
)


@pytest.mark.unit
class TestSARCalculation:
    def test_basic_sar(self):
        sar = calculate_sar(na=10.0, ca=4.0, mg=2.0)
        assert sar > 0
        # SAR = 10 / sqrt((4+2)/2) = 10 / sqrt(3) ≈ 5.77
        assert abs(sar - 5.77) < 0.1

    def test_zero_ca_mg(self):
        sar = calculate_sar(na=10.0, ca=0.0, mg=0.0)
        assert sar == 0.0

    def test_low_na(self):
        sar = calculate_sar(na=1.0, ca=10.0, mg=5.0)
        assert sar < 1.0


@pytest.mark.unit
class TestSalinityRiskClassification:
    def test_no_risk(self):
        assert classify_salinity_risk(0.3, 1.0) == SalinityRisk.NONE

    def test_moderate_risk(self):
        assert classify_salinity_risk(1.5, 2.0) == SalinityRisk.SLIGHT_MODERATE

    def test_severe_risk(self):
        assert classify_salinity_risk(5.0, 12.0) == SalinityRisk.SEVERE


@pytest.mark.unit
class TestYieldReduction:
    def test_no_reduction_below_threshold(self):
        reduction = calculate_yield_reduction(3.0, "wheat")
        assert reduction == 0.0  # Wheat threshold is 6.0

    def test_reduction_above_threshold(self):
        reduction = calculate_yield_reduction(8.0, "wheat")
        # 7.1 * (8.0 - 6.0) = 14.2%
        assert abs(reduction - 14.2) < 0.1

    def test_max_100_pct(self):
        reduction = calculate_yield_reduction(30.0, "tomato")
        assert reduction == 100.0

    def test_unknown_crop_defaults(self):
        reduction = calculate_yield_reduction(5.0, "unknown_crop")
        assert reduction > 0  # Default threshold 2.0, so 5.0 > 2.0


@pytest.mark.unit
class TestLeachingFraction:
    def test_basic_lf(self):
        lf = calculate_leaching_fraction(2.0, 6.0)
        # LF = 2.0 / (5*6.0 - 2.0) / 0.8 = 2/28/0.8 ≈ 0.089
        assert 0.05 < lf < 0.15

    def test_high_ec_water(self):
        lf = calculate_leaching_fraction(8.0, 4.0)
        # Denominator = 5*4 - 8 = 12, LF = 8/12/0.8 = 0.83 → clamped to 0.5
        assert lf == 0.5

    def test_very_low_ec(self):
        lf = calculate_leaching_fraction(0.1, 6.0)
        assert lf < 0.05


@pytest.mark.unit
class TestKcAdjustment:
    def test_no_adjustment_below_threshold(self):
        adjusted = adjust_kc_for_salinity(1.15, 3.0, "wheat")
        assert adjusted == 1.15  # Below threshold (6.0)

    def test_adjustment_above_threshold(self):
        adjusted = adjust_kc_for_salinity(1.15, 10.0, "wheat")
        assert adjusted < 1.15

    def test_floor_at_50_pct(self):
        # Very high salinity should not reduce below 50% of original
        adjusted = adjust_kc_for_salinity(1.0, 50.0, "tomato")
        assert adjusted >= 0.5


@pytest.mark.unit
class TestSalinityModule:
    @pytest.fixture
    def module(self):
        return SalinityModule()

    def test_assess_low_salinity(self, module):
        result = module.assess(ec_water=0.3, crop="wheat", kc=1.15)
        assert result.risk == SalinityRisk.NONE
        assert result.yield_reduction_pct == 0.0
        assert result.adjusted_kc == result.original_kc

    def test_assess_moderate_salinity(self, module):
        result = module.assess(
            ec_water=2.0,
            crop="tomato",
            kc=1.15,
            na=8.0,
            ca=4.0,
            mg=2.0,
        )
        assert result.risk in [SalinityRisk.SLIGHT_MODERATE, SalinityRisk.SEVERE]
        assert result.sar > 0
        assert result.leaching_fraction > 0
        assert len(result.recommendations) > 0
        assert len(result.recommendations_ar) > 0

    def test_assess_severe_salinity(self, module):
        result = module.assess(ec_water=6.0, crop="tomato", kc=1.15)
        assert result.risk == SalinityRisk.SEVERE
        assert result.yield_reduction_pct > 0
        assert result.adjusted_kc < result.original_kc

    def test_leaching_requirement(self, module):
        lr = module.calculate_leaching_requirement(
            ec_water=3.0,
            crop="wheat",
            irrigation_depth_mm=40.0,
        )
        assert lr.leaching_fraction > 0
        assert lr.extra_water_mm > 0
        assert lr.total_water_mm > 40.0
        assert lr.ec_drainage > 0
