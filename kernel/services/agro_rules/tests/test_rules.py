"""
Tests for Agro Rules Module
"""


from src.rules import (
    rule_from_ndvi,
    rule_from_weather,
    rule_from_ndvi_weather,
    rule_from_irrigation_adjustment,
    TaskRule,
)


class TestNdviRules:
    """Tests for NDVI-based rules"""

    def test_severe_ndvi_drop(self):
        """Test emergency task for severe NDVI drop"""
        rule = rule_from_ndvi(ndvi_mean=0.5, trend_7d=-0.18)

        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "inspection"
        assert rule.urgency_hours == 6

    def test_moderate_ndvi_drop(self):
        """Test high priority task for moderate NDVI drop"""
        rule = rule_from_ndvi(ndvi_mean=0.5, trend_7d=-0.12)

        assert rule is not None
        assert rule.priority == "high"
        assert rule.task_type == "inspection"

    def test_very_low_ndvi(self):
        """Test task for very low NDVI value"""
        rule = rule_from_ndvi(ndvi_mean=0.15, trend_7d=0.0)

        assert rule is not None
        assert rule.priority == "high"

    def test_low_ndvi(self):
        """Test task for low NDVI value"""
        rule = rule_from_ndvi(ndvi_mean=0.30, trend_7d=0.0)

        assert rule is not None
        assert rule.priority == "medium"

    def test_healthy_crop_no_task(self):
        """Test no task for healthy crop"""
        rule = rule_from_ndvi(ndvi_mean=0.65, trend_7d=0.08)

        assert rule is None

    def test_bilingual_content(self):
        """Test task has Arabic and English content"""
        rule = rule_from_ndvi(ndvi_mean=0.15, trend_7d=-0.05)

        assert rule is not None
        assert len(rule.title_ar) > 0
        assert len(rule.title_en) > 0
        assert len(rule.description_ar) > 0
        assert len(rule.description_en) > 0


class TestWeatherRules:
    """Tests for weather-based rules"""

    def test_critical_heat_stress(self):
        """Test emergency task for critical heat"""
        rule = rule_from_weather("heat_stress", "critical")

        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "emergency"
        assert rule.urgency_hours <= 2

    def test_high_heat_stress(self):
        """Test urgent irrigation task for high heat"""
        rule = rule_from_weather("heat_stress", "high")

        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "irrigation"

    def test_frost_emergency(self):
        """Test frost emergency task"""
        rule = rule_from_weather("frost", "critical")

        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "emergency"

    def test_heavy_rain_preparation(self):
        """Test heavy rain preparation task"""
        rule = rule_from_weather("heavy_rain", "high")

        assert rule is not None
        assert rule.priority == "high"
        assert rule.task_type == "preparation"

    def test_strong_wind_preparation(self):
        """Test strong wind preparation task"""
        rule = rule_from_weather("strong_wind", "high")

        assert rule is not None
        assert rule.priority == "high"

    def test_disease_risk_inspection(self):
        """Test disease risk inspection task"""
        rule = rule_from_weather("disease_risk", "high")

        assert rule is not None
        assert rule.task_type == "inspection"

    def test_low_severity_no_task(self):
        """Test no task for low severity alerts"""
        rule = rule_from_weather("heat_stress", "low")

        assert rule is None


class TestCombinedRules:
    """Tests for combined NDVI + Weather rules"""

    def test_heat_plus_ndvi_decline(self):
        """Test compound stress detection"""
        rule = rule_from_ndvi_weather(
            ndvi_mean=0.5,
            ndvi_trend=-0.10,
            temp_c=38,
            humidity_pct=30,
        )

        assert rule is not None
        assert rule.priority == "urgent"
        assert rule.task_type == "emergency"

    def test_humidity_plus_weak_plants(self):
        """Test disease risk with weak plants"""
        rule = rule_from_ndvi_weather(
            ndvi_mean=0.35,
            ndvi_trend=0.0,
            temp_c=25,
            humidity_pct=85,
        )

        assert rule is not None
        assert rule.task_type == "spray"

    def test_normal_conditions_no_task(self):
        """Test no task for normal combined conditions"""
        rule = rule_from_ndvi_weather(
            ndvi_mean=0.65,
            ndvi_trend=0.02,
            temp_c=25,
            humidity_pct=55,
        )

        assert rule is None


class TestIrrigationRules:
    """Tests for irrigation adjustment rules"""

    def test_increase_irrigation(self):
        """Test task for irrigation increase"""
        rule = rule_from_irrigation_adjustment(1.35, "field-123")

        assert rule is not None
        assert rule.priority == "high"
        assert rule.task_type == "irrigation"
        assert "30%" in rule.description_en or "35%" in rule.description_en

    def test_decrease_irrigation(self):
        """Test task for irrigation decrease"""
        rule = rule_from_irrigation_adjustment(0.55, "field-123")

        assert rule is not None
        assert rule.priority == "medium"
        assert rule.task_type == "irrigation"

    def test_normal_irrigation_no_task(self):
        """Test no task for normal irrigation"""
        rule = rule_from_irrigation_adjustment(1.0, "field-123")

        assert rule is None

    def test_slight_adjustment_no_task(self):
        """Test no task for slight adjustments"""
        rule = rule_from_irrigation_adjustment(1.15, "field-123")

        assert rule is None


class TestTaskRule:
    """Tests for TaskRule dataclass"""

    def test_to_tuple(self):
        """Test to_tuple method"""
        rule = TaskRule(
            title_ar="عنوان",
            title_en="Title",
            description_ar="وصف",
            description_en="Description",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

        title, desc, priority = rule.to_tuple()

        assert title == "عنوان"
        assert desc == "وصف"
        assert priority == "high"
