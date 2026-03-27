"""
Comprehensive edge case tests for rules.py
Covers boundary conditions, all branches, and data model methods
"""

import pytest
from src.rules import (
    TaskRule,
    rule_from_irrigation_adjustment,
    rule_from_ndvi,
    rule_from_ndvi_weather,
    rule_from_weather,
)


class TestTaskRuleDataclass:
    """Thorough tests for TaskRule dataclass"""

    def test_all_fields_populated(self):
        """Test all fields are accessible"""
        rule = TaskRule(
            title_ar="عنوان",
            title_en="Title",
            description_ar="وصف",
            description_en="Description",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )
        assert rule.title_ar == "عنوان"
        assert rule.title_en == "Title"
        assert rule.description_ar == "وصف"
        assert rule.description_en == "Description"
        assert rule.task_type == "inspection"
        assert rule.priority == "high"
        assert rule.urgency_hours == 24

    def test_to_tuple_returns_correct_types(self):
        """Test to_tuple returns tuple of 3 strings"""
        rule = TaskRule(
            title_ar="أ",
            title_en="A",
            description_ar="ب",
            description_en="B",
            task_type="t",
            priority="p",
            urgency_hours=1,
        )
        result = rule.to_tuple()
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert all(isinstance(x, str) for x in result)

    def test_equality(self):
        """Test dataclass equality"""
        kwargs = dict(  # noqa: C408
            title_ar="x",
            title_en="y",
            description_ar="a",
            description_en="b",
            task_type="t",
            priority="p",
            urgency_hours=1,
        )
        r1 = TaskRule(**kwargs)
        r2 = TaskRule(**kwargs)
        assert r1 == r2


class TestNdviBoundaryConditions:
    """Boundary condition tests for rule_from_ndvi"""

    def test_trend_exactly_minus_0_15(self):
        """Test boundary: trend_7d == -0.15 (severe threshold)"""
        rule = rule_from_ndvi(0.5, -0.15)
        assert rule is not None
        assert rule.priority == "urgent"

    def test_trend_just_above_minus_0_15(self):
        """Test boundary: trend_7d == -0.14 (not severe)"""
        rule = rule_from_ndvi(0.5, -0.14)
        assert rule is not None
        # Should fall into moderate drop (-0.10 threshold)
        assert rule.priority == "high"

    def test_trend_exactly_minus_0_10(self):
        """Test boundary: trend_7d == -0.10 (moderate threshold)"""
        rule = rule_from_ndvi(0.5, -0.10)
        assert rule is not None
        assert rule.priority == "high"

    def test_trend_just_above_minus_0_10(self):
        """Test boundary: trend_7d == -0.09 with good NDVI"""
        rule = rule_from_ndvi(0.65, -0.09)
        # NDVI is good and trend is not bad enough
        assert rule is None

    def test_ndvi_exactly_0_2(self):
        """Test boundary: ndvi_mean == 0.2 (not below 0.2)"""
        rule = rule_from_ndvi(0.2, 0.0)
        # 0.2 is NOT < 0.2, so should fall to low NDVI (< 0.35)
        assert rule is not None
        assert rule.priority == "medium"

    def test_ndvi_just_below_0_2(self):
        """Test boundary: ndvi_mean == 0.19"""
        rule = rule_from_ndvi(0.19, 0.0)
        assert rule is not None
        assert rule.priority == "high"

    def test_ndvi_exactly_0_35(self):
        """Test boundary: ndvi_mean == 0.35 (not below 0.35)"""
        rule = rule_from_ndvi(0.35, 0.0)
        assert rule is None

    def test_ndvi_just_below_0_35(self):
        """Test boundary: ndvi_mean == 0.34"""
        rule = rule_from_ndvi(0.34, 0.0)
        assert rule is not None
        assert rule.priority == "medium"

    def test_positive_trend_moderate_ndvi(self):
        """Test positive trend with moderate NDVI returns None"""
        rule = rule_from_ndvi(0.55, 0.06)
        assert rule is None

    def test_ndvi_zero(self):
        """Test NDVI value of 0"""
        rule = rule_from_ndvi(0.0, 0.0)
        assert rule is not None
        assert rule.priority == "high"

    def test_description_contains_values(self):
        """Test descriptions include actual NDVI values"""
        rule = rule_from_ndvi(0.5, -0.20)
        assert "-0.20" in rule.description_ar
        assert "-0.20" in rule.description_en

    def test_severe_drop_overrides_low_ndvi(self):
        """Test severe trend drop is checked before low NDVI"""
        rule = rule_from_ndvi(0.15, -0.20)
        # Should match severe drop first, not very low NDVI
        assert rule.urgency_hours == 6
        assert rule.priority == "urgent"


class TestWeatherRuleEdgeCases:
    """Edge case tests for rule_from_weather"""

    def test_none_severity(self):
        """Test 'none' severity returns None"""
        rule = rule_from_weather("heat_stress", "none")
        assert rule is None

    def test_medium_heat_stress(self):
        """Test medium heat stress"""
        rule = rule_from_weather("heat_stress", "medium")
        assert rule is not None
        assert rule.task_type == "monitoring"
        assert rule.priority == "high"

    def test_frost_high_severity(self):
        """Test frost with high severity (same as critical)"""
        rule = rule_from_weather("frost", "high")
        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "emergency"

    def test_frost_medium_severity(self):
        """Test frost with medium severity"""
        rule = rule_from_weather("frost", "medium")
        assert rule is not None
        assert rule.priority == "high"
        assert rule.task_type == "preparation"

    def test_heavy_rain_medium_severity(self):
        """Test heavy rain with medium severity"""
        rule = rule_from_weather("heavy_rain", "medium")
        assert rule is not None
        assert rule.priority == "medium"
        assert rule.task_type == "inspection"

    def test_strong_wind_medium_no_task(self):
        """Test strong wind with medium severity returns None"""
        rule = rule_from_weather("strong_wind", "medium")
        assert rule is None

    def test_strong_wind_critical(self):
        """Test strong wind with critical severity"""
        rule = rule_from_weather("strong_wind", "critical")
        assert rule is not None
        assert rule.priority == "high"

    def test_disease_risk_medium(self):
        """Test disease risk with medium severity"""
        rule = rule_from_weather("disease_risk", "medium")
        assert rule is not None
        assert rule.task_type == "monitoring"
        assert rule.priority == "medium"

    def test_unknown_alert_type(self):
        """Test unknown alert type returns None"""
        rule = rule_from_weather("earthquake", "critical")
        assert rule is None

    def test_unknown_alert_type_low_severity(self):
        """Test unknown alert type with low severity returns None"""
        rule = rule_from_weather("unknown", "low")
        assert rule is None


class TestCombinedRuleBoundaries:
    """Boundary tests for rule_from_ndvi_weather"""

    def test_temp_exactly_35_with_ndvi_decline(self):
        """Test boundary: temp_c == 35, ndvi_trend == -0.08"""
        rule = rule_from_ndvi_weather(0.5, -0.08, 35, 50)
        assert rule is not None
        assert rule.priority == "urgent"

    def test_temp_just_below_35(self):
        """Test boundary: temp_c == 34.9"""
        rule = rule_from_ndvi_weather(0.5, -0.08, 34.9, 50)
        assert rule is None

    def test_trend_just_above_minus_0_08(self):
        """Test boundary: ndvi_trend == -0.07"""
        rule = rule_from_ndvi_weather(0.5, -0.07, 38, 50)
        assert rule is None

    def test_humidity_exactly_80_with_low_ndvi(self):
        """Test boundary: humidity_pct == 80, ndvi_mean < 0.4"""
        rule = rule_from_ndvi_weather(0.35, 0.0, 25, 80)
        assert rule is not None
        assert rule.task_type == "spray"

    def test_humidity_just_below_80(self):
        """Test boundary: humidity_pct == 79"""
        rule = rule_from_ndvi_weather(0.35, 0.0, 25, 79)
        assert rule is None

    def test_ndvi_exactly_0_4_with_high_humidity(self):
        """Test boundary: ndvi_mean == 0.4 (not < 0.4)"""
        rule = rule_from_ndvi_weather(0.4, 0.0, 25, 85)
        assert rule is None

    def test_heat_rule_takes_precedence(self):
        """Test heat+NDVI rule is checked before humidity rule"""
        rule = rule_from_ndvi_weather(0.35, -0.10, 38, 85)
        # Heat + NDVI decline should match first
        assert rule.priority == "urgent"
        assert rule.task_type == "emergency"


class TestIrrigationAdjustmentBoundaries:
    """Boundary tests for rule_from_irrigation_adjustment"""

    def test_factor_exactly_1_3(self):
        """Test boundary: adjustment_factor == 1.3"""
        rule = rule_from_irrigation_adjustment(1.3, "f1")
        assert rule is not None
        assert rule.priority == "high"

    def test_factor_just_below_1_3(self):
        """Test boundary: adjustment_factor == 1.29"""
        rule = rule_from_irrigation_adjustment(1.29, "f1")
        assert rule is None

    def test_factor_exactly_0_6(self):
        """Test boundary: adjustment_factor == 0.6"""
        rule = rule_from_irrigation_adjustment(0.6, "f1")
        assert rule is not None
        assert rule.priority == "medium"

    def test_factor_just_above_0_6(self):
        """Test boundary: adjustment_factor == 0.61"""
        rule = rule_from_irrigation_adjustment(0.61, "f1")
        assert rule is None

    def test_very_high_factor(self):
        """Test very high adjustment factor"""
        rule = rule_from_irrigation_adjustment(2.0, "f1")
        assert rule is not None
        assert "100%" in rule.description_en

    def test_very_low_factor(self):
        """Test very low adjustment factor (near 0)"""
        rule = rule_from_irrigation_adjustment(0.1, "f1")
        assert rule is not None
        assert "90%" in rule.description_en

    def test_description_percentage_calculation(self):
        """Test percentage in description is calculated correctly"""
        rule = rule_from_irrigation_adjustment(1.5, "f1")
        assert "50%" in rule.description_en
        assert "50%" in rule.description_ar
