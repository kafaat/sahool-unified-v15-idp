"""
Tests for gdd_tracker module.
Tests cover GDDTracker calculation methods, growth stage determination,
milestones, data models, and crop requirements.
"""

import sys
import os
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.gdd_tracker import (
    CropGDDRequirements,
    GDDChart,
    GDDDataPoint,
    GDDMethod,
    GDDTracker,
    GrowthMilestone,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestGDDMethod:
    def test_methods(self):
        assert GDDMethod.SIMPLE.value == "simple"
        assert GDDMethod.MODIFIED.value == "modified"
        assert GDDMethod.SINE.value == "sine"


# =============================================================================
# Data Model Tests
# =============================================================================


class TestGDDDataPoint:
    def test_to_dict(self):
        point = GDDDataPoint(
            date=date(2025, 3, 15),
            temp_min=10.0,
            temp_max=25.0,
            temp_avg=17.5,
            daily_gdd=17.5,
            accumulated_gdd=350.0,
        )
        d = point.to_dict()
        assert d["date"] == "2025-03-15"
        assert d["temp_min_c"] == 10.0
        assert d["temp_max_c"] == 25.0
        assert d["daily_gdd"] == 17.5
        assert d["accumulated_gdd"] == 350.0


class TestGrowthMilestone:
    def test_to_dict_reached(self):
        m = GrowthMilestone(
            stage_name_en="Emergence",
            stage_name_ar="الإنبات",
            gdd_required=150.0,
            gdd_accumulated=200.0,
            is_reached=True,
            reached_date=date(2025, 1, 20),
            expected_date=None,
            days_remaining=0,
            description_ar="ظهور البادرات",
            description_en="Seedling emergence",
        )
        d = m.to_dict()
        assert d["stage_name_en"] == "Emergence"
        assert d["is_reached"] is True
        assert d["reached_date"] == "2025-01-20"
        assert d["expected_date"] is None

    def test_to_dict_not_reached(self):
        m = GrowthMilestone(
            stage_name_en="Flowering",
            stage_name_ar="الإزهار",
            gdd_required=1500.0,
            gdd_accumulated=500.0,
            is_reached=False,
            reached_date=None,
            expected_date=date(2025, 5, 1),
            days_remaining=60,
            description_ar="الإزهار",
            description_en="Flowering",
        )
        d = m.to_dict()
        assert d["is_reached"] is False
        assert d["expected_date"] == "2025-05-01"
        assert d["days_remaining"] == 60


class TestCropGDDRequirements:
    def test_to_dict(self):
        req = CropGDDRequirements(
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            base_temp=0.0,
            upper_temp=30.0,
            total_gdd_required=2000.0,
            stages=[{"name_en": "Emergence", "gdd": 150}],
        )
        d = req.to_dict()
        assert d["crop_code"] == "WHEAT"
        assert d["base_temp_c"] == 0.0
        assert d["total_gdd_required"] == 2000.0
        assert len(d["stages"]) == 1


# =============================================================================
# GDDTracker Tests
# =============================================================================


class TestGDDTracker:
    @pytest.fixture
    def tracker(self):
        return GDDTracker()

    # =========================================================================
    # calculate_daily_gdd Tests
    # =========================================================================

    def test_simple_method_basic(self, tracker):
        # (25 + 15) / 2 - 10 = 10
        result = tracker.calculate_daily_gdd(15.0, 25.0, 10.0, method="simple")
        assert result == 10.0

    def test_simple_method_no_gdd(self, tracker):
        # Both below base: (5 + 3) / 2 - 10 = -6, clamped to 0
        result = tracker.calculate_daily_gdd(3.0, 5.0, 10.0, method="simple")
        assert result == 0.0

    def test_simple_method_zero(self, tracker):
        # (10 + 10) / 2 - 10 = 0
        result = tracker.calculate_daily_gdd(10.0, 10.0, 10.0, method="simple")
        assert result == 0.0

    def test_modified_method(self, tracker):
        result = tracker.calculate_daily_gdd(15.0, 25.0, 10.0, upper_temp=30.0, method="modified")
        assert result == 10.0

    def test_modified_method_upper_cutoff(self, tracker):
        # temp_max capped at 30, temp_min stays
        # (30 + 15) / 2 - 10 = 12.5
        result = tracker.calculate_daily_gdd(15.0, 35.0, 10.0, upper_temp=30.0, method="modified")
        assert result == 12.5

    def test_modified_method_both_below_base(self, tracker):
        # Both clamped to base
        result = tracker.calculate_daily_gdd(3.0, 5.0, 10.0, upper_temp=30.0, method="modified")
        assert result == 0.0

    def test_sine_method_both_above_base(self, tracker):
        # Both above base, simple average
        result = tracker.calculate_daily_gdd(15.0, 25.0, 10.0, method="sine")
        assert result == 10.0

    def test_sine_method_both_below_base(self, tracker):
        result = tracker.calculate_daily_gdd(3.0, 5.0, 10.0, method="sine")
        assert result == 0.0

    def test_sine_method_crossing_base(self, tracker):
        # Min below base, max above
        result = tracker.calculate_daily_gdd(5.0, 25.0, 10.0, method="sine")
        assert result > 0
        assert result < 7.5  # Should be less than simple method

    def test_unknown_method_defaults_to_simple(self, tracker):
        result = tracker.calculate_daily_gdd(15.0, 25.0, 10.0, method="unknown")
        assert result == 10.0

    # =========================================================================
    # get_current_stage Tests
    # =========================================================================

    def test_current_stage_planting(self, tracker):
        en, ar, next_en, next_ar, gdd_to_next = tracker.get_current_stage("WHEAT", 0.0)
        assert en == "Planting"
        assert next_en == "Emergence"
        assert gdd_to_next == 150.0

    def test_current_stage_emergence(self, tracker):
        en, ar, next_en, next_ar, gdd_to_next = tracker.get_current_stage("WHEAT", 200.0)
        assert en == "Emergence"
        assert next_en == "Tillering"

    def test_current_stage_last(self, tracker):
        en, ar, next_en, next_ar, gdd_to_next = tracker.get_current_stage("WHEAT", 2000.0)
        assert next_en == "Harvest"
        assert gdd_to_next == 0.0

    def test_current_stage_unknown_crop(self, tracker):
        en, ar, next_en, next_ar, gdd_to_next = tracker.get_current_stage("UNKNOWN_CROP", 100.0)
        assert en == "Unknown"

    def test_current_stage_corn(self, tracker):
        en, _, _, _, _ = tracker.get_current_stage("CORN", 800.0)
        assert en in ["8-Leaf", "4-Leaf", "Emergence"]

    def test_current_stage_tomato(self, tracker):
        en, _, _, _, _ = tracker.get_current_stage("TOMATO", 500.0)
        assert en in ["Vegetative", "Transplant"]

    def test_current_stage_sorghum(self, tracker):
        en, _, _, _, _ = tracker.get_current_stage("SORGHUM", 1000.0)
        assert en in ["5-Leaf", "3-Leaf"]

    def test_current_stage_case_insensitive(self, tracker):
        en1, _, _, _, _ = tracker.get_current_stage("wheat", 200.0)
        en2, _, _, _, _ = tracker.get_current_stage("WHEAT", 200.0)
        assert en1 == en2

    # =========================================================================
    # get_milestones Tests
    # =========================================================================

    def test_milestones_wheat(self, tracker):
        daily_data = [
            GDDDataPoint(date=date(2025, 1, 1) + timedelta(days=i), temp_min=5, temp_max=15, temp_avg=10, daily_gdd=10, accumulated_gdd=i * 10)
            for i in range(50)
        ]
        milestones = tracker.get_milestones("WHEAT", 400.0, 10.0, date(2025, 2, 19), daily_data)
        assert len(milestones) > 0

        # First milestone (Emergence at 150 GDD) should be reached
        assert milestones[0].stage_name_en == "Emergence"
        assert milestones[0].is_reached is True
        assert milestones[0].days_remaining == 0

    def test_milestones_none_reached(self, tracker):
        milestones = tracker.get_milestones("WHEAT", 50.0, 10.0, date(2025, 1, 5), [])
        assert len(milestones) > 0
        assert all(not m.is_reached for m in milestones)

    def test_milestones_unknown_crop(self, tracker):
        milestones = tracker.get_milestones("UNKNOWN", 100.0, 10.0, date(2025, 1, 1), [])
        assert milestones == []

    def test_milestones_predicted_dates(self, tracker):
        milestones = tracker.get_milestones("WHEAT", 100.0, 10.0, date(2025, 1, 10), [])
        # Emergence needs 150, we have 100, so 50 more GDD at 10/day = 5 days
        emergence = milestones[0]
        assert emergence.is_reached is False
        assert emergence.expected_date == date(2025, 1, 15)
        assert emergence.days_remaining == 5

    def test_milestones_zero_daily_gdd(self, tracker):
        milestones = tracker.get_milestones("WHEAT", 50.0, 0.0, date(2025, 1, 1), [])
        for m in milestones:
            if not m.is_reached:
                assert m.days_remaining is None

    # =========================================================================
    # CROP_BASE_TEMPS Tests
    # =========================================================================

    def test_crop_base_temps_wheat(self, tracker):
        assert "WHEAT" in tracker.CROP_BASE_TEMPS
        assert tracker.CROP_BASE_TEMPS["WHEAT"]["base"] == 0

    def test_crop_base_temps_cotton(self, tracker):
        assert tracker.CROP_BASE_TEMPS["COTTON"]["base"] == 15.5

    def test_crop_base_temps_date_palm(self, tracker):
        assert tracker.CROP_BASE_TEMPS["DATE_PALM"]["upper"] is None

    def test_multiple_crops_exist(self, tracker):
        expected_crops = ["WHEAT", "CORN", "SORGHUM", "TOMATO", "COTTON", "COFFEE", "QAT", "RICE"]
        for crop in expected_crops:
            assert crop in tracker.CROP_BASE_TEMPS, f"{crop} not found"

    # =========================================================================
    # CROP_GDD_REQUIREMENTS Tests
    # =========================================================================

    def test_wheat_requirements(self, tracker):
        assert "WHEAT" in tracker.CROP_GDD_REQUIREMENTS
        wheat = tracker.CROP_GDD_REQUIREMENTS["WHEAT"]
        assert wheat["total"] == 2000
        assert len(wheat["stages"]) > 0

    def test_corn_requirements(self, tracker):
        assert "CORN" in tracker.CROP_GDD_REQUIREMENTS
        corn = tracker.CROP_GDD_REQUIREMENTS["CORN"]
        assert corn["total"] == 2700

    def test_all_stages_have_required_fields(self, tracker):
        for crop_code, crop_data in tracker.CROP_GDD_REQUIREMENTS.items():
            assert "total" in crop_data, f"{crop_code} missing total"
            assert "stages" in crop_data, f"{crop_code} missing stages"
            for stage in crop_data["stages"]:
                assert "name_en" in stage, f"{crop_code} stage missing name_en"
                assert "name_ar" in stage, f"{crop_code} stage missing name_ar"
                assert "gdd" in stage, f"{crop_code} stage missing gdd"

    # =========================================================================
    # get_crop_requirements Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_crop_requirements_wheat(self, tracker):
        req = await tracker.get_crop_requirements("WHEAT")
        assert isinstance(req, CropGDDRequirements)
        assert req.crop_code == "WHEAT"
        assert req.base_temp == 0
        assert req.total_gdd_required == 2000

    @pytest.mark.asyncio
    async def test_get_crop_requirements_unknown(self, tracker):
        req = await tracker.get_crop_requirements("UNKNOWN_CROP")
        assert req is None

    @pytest.mark.asyncio
    async def test_get_crop_requirements_case_insensitive(self, tracker):
        req = await tracker.get_crop_requirements("wheat")
        assert req is not None
        assert req.crop_code == "WHEAT"


# =============================================================================
# GDDChart Tests
# =============================================================================


class TestGDDChart:
    def test_to_dict(self):
        chart = GDDChart(
            field_id="F001",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            planting_date=date(2025, 1, 1),
            base_temp=0.0,
            upper_temp=30.0,
            current_date=date(2025, 2, 1),
            total_gdd=350.0,
            days_since_planting=31,
            avg_daily_gdd=11.3,
            daily_data=[],
            milestones=[],
            current_stage="Tillering",
            current_stage_ar="التفريع",
            next_stage="Jointing",
            next_stage_ar="العقد",
            gdd_to_next_stage=100.0,
            estimated_harvest_date=date(2025, 5, 15),
            gdd_to_harvest=1650.0,
            days_to_harvest=103,
            vs_normal_year=5.0,
            vs_normal_description_ar="أسرع 5% من المعتاد",
            vs_normal_description_en="5% ahead of normal",
            calculation_method="simple",
            confidence=0.85,
        )
        d = chart.to_dict()
        assert d["field_id"] == "F001"
        assert d["crop"]["code"] == "WHEAT"
        assert d["current_status"]["total_gdd"] == 350.0
        assert d["harvest_prediction"]["days_remaining"] == 103
        assert d["comparison"]["vs_normal_percent"] == 5.0
