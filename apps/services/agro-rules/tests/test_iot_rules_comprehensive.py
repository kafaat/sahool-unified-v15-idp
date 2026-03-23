"""
Comprehensive edge case tests for iot_rules.py
Covers all sensor types, crop-specific thresholds, boundary conditions, combined rules
"""

import pytest
from src.iot_rules import (
    THRESHOLDS,
    TaskRecommendation,
    evaluate_combined_rules,
    get_threshold,
    rule_from_sensor,
)


class TestTaskRecommendationDataclass:
    """Tests for TaskRecommendation"""

    def test_to_dict_with_metadata(self):
        """Test to_dict includes metadata"""
        rec = TaskRecommendation(
            title_ar="أ",
            title_en="A",
            description_ar="ب",
            description_en="B",
            task_type="t",
            priority="p",
            urgency_hours=1,
            metadata={"key": "val"},
        )
        d = rec.to_dict()
        assert d["metadata"] == {"key": "val"}

    def test_to_dict_default_metadata(self):
        """Test to_dict returns empty dict when metadata is None"""
        rec = TaskRecommendation(
            title_ar="أ",
            title_en="A",
            description_ar="ب",
            description_en="B",
            task_type="t",
            priority="p",
            urgency_hours=1,
        )
        d = rec.to_dict()
        assert d["metadata"] == {}

    def test_to_dict_all_keys(self):
        """Test to_dict has all expected keys"""
        rec = TaskRecommendation(
            title_ar="أ",
            title_en="A",
            description_ar="ب",
            description_en="B",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )
        d = rec.to_dict()
        expected_keys = {
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "task_type",
            "priority",
            "urgency_hours",
            "metadata",
        }
        assert set(d.keys()) == expected_keys


class TestGetThreshold:
    """Tests for threshold lookup"""

    def test_default_crop_returns_defaults(self):
        """Test default crop returns default thresholds"""
        t = get_threshold("soil_moisture", "default")
        assert t["low"] == 20
        assert t["critical_low"] == 10
        assert t["high"] == 80

    def test_unknown_crop_falls_back_to_default(self):
        """Test unknown crop type falls back to default"""
        t = get_threshold("soil_moisture", "mango")
        assert t == THRESHOLDS["default"]["soil_moisture"]

    def test_crop_specific_threshold_override(self):
        """Test crop-specific overrides only the defined sensors"""
        t = get_threshold("air_humidity", "tomato")
        # Tomato doesn't define air_humidity, should fall back to default
        assert t == THRESHOLDS["default"]["air_humidity"]

    def test_unknown_sensor_type(self):
        """Test unknown sensor type returns empty dict"""
        t = get_threshold("unknown_sensor", "default")
        assert t == {}

    def test_coffee_soil_temperature(self):
        """Test coffee-specific soil temperature thresholds"""
        t = get_threshold("soil_temperature", "coffee")
        assert t["low"] == 18
        assert t["high"] == 28


class TestWaterFlowRules:
    """Tests for water flow sensor rules"""

    def test_zero_flow_urgent_maintenance(self):
        """Test zero water flow triggers urgent maintenance"""
        rec = rule_from_sensor("water_flow", 0)
        assert rec is not None
        assert rec.priority == "urgent"
        assert rec.task_type == "maintenance"

    def test_positive_flow_no_task(self):
        """Test positive water flow returns None"""
        rec = rule_from_sensor("water_flow", 5.0)
        assert rec is None

    def test_water_flow_metadata(self):
        """Test water flow result includes metadata"""
        rec = rule_from_sensor("water_flow", 0)
        assert rec.metadata["sensor_type"] == "water_flow"
        assert rec.metadata["value"] == 0


class TestWaterLevelRules:
    """Tests for water level sensor rules"""

    def test_low_level_triggers_refill(self):
        """Test tank level below 20% triggers refill"""
        rec = rule_from_sensor("water_level", 15)
        assert rec is not None
        assert rec.task_type == "maintenance"
        assert rec.priority == "high"

    def test_boundary_20_percent(self):
        """Test boundary: 20% does not trigger"""
        rec = rule_from_sensor("water_level", 20)
        assert rec is None

    def test_boundary_19_percent(self):
        """Test boundary: 19% triggers"""
        rec = rule_from_sensor("water_level", 19)
        assert rec is not None

    def test_full_tank_no_task(self):
        """Test full tank returns None"""
        rec = rule_from_sensor("water_level", 90)
        assert rec is None


class TestSoilMoistureRulesBoundaries:
    """Boundary tests for soil moisture rules"""

    def test_critical_low_boundary(self):
        """Test boundary: value == critical_low (10 for default)"""
        rec = rule_from_sensor("soil_moisture", 10)
        # 10 is NOT < 10, should fall to low check (< 20)
        assert rec is not None
        assert rec.priority == "high"

    def test_just_below_critical_low(self):
        """Test boundary: value == 9"""
        rec = rule_from_sensor("soil_moisture", 9)
        assert rec is not None
        assert rec.priority == "urgent"

    def test_low_boundary(self):
        """Test boundary: value == low threshold (20 for default)"""
        rec = rule_from_sensor("soil_moisture", 20)
        # 20 is NOT < 20, no task from low check
        assert rec is None

    def test_just_below_low(self):
        """Test boundary: value == 19"""
        rec = rule_from_sensor("soil_moisture", 19)
        assert rec is not None
        assert rec.priority == "high"

    def test_high_boundary(self):
        """Test boundary: value == high threshold (80 for default)"""
        rec = rule_from_sensor("soil_moisture", 80)
        # 80 is NOT > 80
        assert rec is None

    def test_just_above_high(self):
        """Test boundary: value == 81"""
        rec = rule_from_sensor("soil_moisture", 81)
        assert rec is not None
        assert rec.task_type == "inspection"
        assert rec.priority == "medium"

    def test_crop_specific_moisture_wheat(self):
        """Test wheat has lower moisture thresholds"""
        # Wheat critical_low = 8
        rec = rule_from_sensor("soil_moisture", 9, crop="wheat")
        assert rec is not None
        assert rec.priority == "high"  # Between 8 and 15 for wheat

    def test_crop_specific_moisture_coffee(self):
        """Test coffee has higher moisture thresholds"""
        # Coffee low = 30
        rec = rule_from_sensor("soil_moisture", 25, crop="coffee")
        assert rec is not None
        assert rec.priority == "high"


class TestAirTemperatureRulesBoundaries:
    """Boundary tests for air temperature rules"""

    def test_critical_high_boundary(self):
        """Test boundary: value == critical_high (42 for default)"""
        rec = rule_from_sensor("air_temperature", 42)
        # 42 is NOT > 42
        assert rec is not None
        # Should fall to high check (> 38)
        assert rec.priority == "high"

    def test_above_critical_high(self):
        """Test value above critical high"""
        rec = rule_from_sensor("air_temperature", 43)
        assert rec is not None
        assert rec.priority == "urgent"
        assert rec.task_type == "emergency"

    def test_high_boundary(self):
        """Test boundary: value == high (38 for default)"""
        rec = rule_from_sensor("air_temperature", 38)
        # 38 is NOT > 38
        assert rec is None

    def test_above_high(self):
        """Test value just above high"""
        rec = rule_from_sensor("air_temperature", 39)
        assert rec is not None
        assert rec.priority == "high"

    def test_low_boundary(self):
        """Test boundary: value == low (5 for default)"""
        rec = rule_from_sensor("air_temperature", 5)
        # 5 is NOT < 5
        assert rec is None

    def test_below_low(self):
        """Test value below low (frost)"""
        rec = rule_from_sensor("air_temperature", 4)
        assert rec is not None
        assert rec.priority == "urgent"
        assert "frost" in rec.title_en.lower()

    def test_normal_temperature_no_task(self):
        """Test normal temperature creates no task"""
        rec = rule_from_sensor("air_temperature", 25)
        assert rec is None

    def test_tomato_critical_high(self):
        """Test tomato has lower critical_high (38)"""
        rec = rule_from_sensor("air_temperature", 39, crop="tomato")
        assert rec is not None
        assert rec.priority == "urgent"


class TestSoilTemperatureRules:
    """Tests for soil temperature rules"""

    def test_critical_high_soil_temp(self):
        """Test critical high soil temperature"""
        rec = rule_from_sensor("soil_temperature", 41)
        assert rec is not None
        assert rec.task_type == "manual"
        assert rec.priority == "high"

    def test_high_soil_temp(self):
        """Test high soil temperature"""
        rec = rule_from_sensor("soil_temperature", 36)
        assert rec is not None
        assert rec.task_type == "irrigation"
        assert rec.priority == "medium"

    def test_normal_soil_temp(self):
        """Test normal soil temperature"""
        rec = rule_from_sensor("soil_temperature", 25)
        assert rec is None

    def test_crop_specific_soil_temp(self):
        """Test coffee-specific soil temperature threshold"""
        # Coffee critical_high = 32
        rec = rule_from_sensor("soil_temperature", 33, crop="coffee")
        assert rec is not None
        assert rec.task_type == "manual"


class TestSoilEcRules:
    """Tests for soil EC (salinity) rules"""

    def test_critical_salinity(self):
        """Test critical salinity triggers urgent leaching"""
        rec = rule_from_sensor("soil_ec", 7.0)
        assert rec is not None
        assert rec.priority == "urgent"

    def test_high_salinity(self):
        """Test high salinity alert"""
        rec = rule_from_sensor("soil_ec", 5.0)
        assert rec is not None
        assert rec.priority == "high"

    def test_normal_salinity(self):
        """Test normal salinity"""
        rec = rule_from_sensor("soil_ec", 2.0)
        assert rec is None

    def test_critical_boundary(self):
        """Test boundary: value == 6.0 (not > 6.0)"""
        rec = rule_from_sensor("soil_ec", 6.0)
        # 6.0 is NOT > 6.0, falls to high check (> 4.0)
        assert rec is not None
        assert rec.priority == "high"


class TestAirHumidityRules:
    """Tests for air humidity rules"""

    def test_high_humidity_disease_risk(self):
        """Test high humidity triggers disease risk"""
        rec = rule_from_sensor("air_humidity", 92)
        assert rec is not None
        assert rec.task_type == "inspection"
        assert "disease" in rec.title_en.lower()

    def test_low_humidity(self):
        """Test low humidity alert"""
        rec = rule_from_sensor("air_humidity", 25)
        assert rec is not None
        assert rec.priority == "low"

    def test_normal_humidity(self):
        """Test normal humidity no task"""
        rec = rule_from_sensor("air_humidity", 60)
        assert rec is None

    def test_high_boundary(self):
        """Test boundary: 90 is NOT > 90"""
        rec = rule_from_sensor("air_humidity", 90)
        assert rec is None

    def test_low_boundary(self):
        """Test boundary: 30 is NOT < 30"""
        rec = rule_from_sensor("air_humidity", 30)
        assert rec is None


class TestUnknownSensorType:
    """Tests for unknown sensor types"""

    def test_unknown_sensor_returns_none(self):
        """Test unknown sensor type returns None"""
        rec = rule_from_sensor("wind_speed", 50)
        assert rec is None

    def test_unknown_sensor_with_crop(self):
        """Test unknown sensor with crop context returns None"""
        rec = rule_from_sensor("uv_index", 10, crop="tomato")
        assert rec is None


class TestContextParameter:
    """Tests for context parameter handling"""

    def test_none_context_defaults_to_empty(self):
        """Test None context is handled"""
        # Should not raise
        rec = rule_from_sensor("soil_moisture", 5, context=None)
        assert rec is not None

    def test_context_dict_passed(self):
        """Test context dict doesn't break anything"""
        rec = rule_from_sensor("soil_moisture", 5, context={"field_id": "f1"})
        assert rec is not None


class TestEvaluateCombinedRules:
    """Additional combined rule tests"""

    def test_empty_readings_no_recommendations(self):
        """Test empty readings list returns empty"""
        result = evaluate_combined_rules([])
        assert result == []

    def test_single_reading_no_combined_rule(self):
        """Test single sensor reading doesn't trigger combined rules"""
        result = evaluate_combined_rules([{"sensor_type": "air_temperature", "value": 40}])
        assert result == []

    def test_heat_drought_boundary(self):
        """Test boundary: temp exactly at high, moisture exactly at low"""
        readings = [
            {"sensor_type": "air_temperature", "value": 38},  # >= 38
            {"sensor_type": "soil_moisture", "value": 19},  # < 20
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) >= 1
        assert any(r.priority == "urgent" for r in result)

    def test_heat_drought_not_triggered(self):
        """Test combined rule not triggered when only one condition met"""
        readings = [
            {"sensor_type": "air_temperature", "value": 40},
            {"sensor_type": "soil_moisture", "value": 50},  # Moisture is fine
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) == 0

    def test_disease_risk_boundary(self):
        """Test disease risk boundary: humidity > 85 and leaf_wetness > 80"""
        readings = [
            {"sensor_type": "air_humidity", "value": 86},
            {"sensor_type": "leaf_wetness", "value": 81},
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) >= 1
        assert any("disease" in r.title_en.lower() for r in result)

    def test_disease_risk_not_triggered_humidity(self):
        """Test disease risk not triggered when humidity <= 85"""
        readings = [
            {"sensor_type": "air_humidity", "value": 85},
            {"sensor_type": "leaf_wetness", "value": 85},
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) == 0

    def test_disease_risk_not_triggered_wetness(self):
        """Test disease risk not triggered when leaf wetness <= 80"""
        readings = [
            {"sensor_type": "air_humidity", "value": 90},
            {"sensor_type": "leaf_wetness", "value": 80},
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) == 0

    def test_both_combined_rules_triggered(self):
        """Test both combined rules can trigger simultaneously"""
        readings = [
            {"sensor_type": "air_temperature", "value": 40},
            {"sensor_type": "soil_moisture", "value": 15},
            {"sensor_type": "air_humidity", "value": 90},
            {"sensor_type": "leaf_wetness", "value": 85},
        ]
        result = evaluate_combined_rules(readings)
        assert len(result) == 2

    def test_crop_specific_combined_rule(self):
        """Test combined rules with crop-specific thresholds"""
        readings = [
            {"sensor_type": "air_temperature", "value": 33},  # Tomato high = 32
            {"sensor_type": "soil_moisture", "value": 20},  # Tomato low = 25
        ]
        result = evaluate_combined_rules(readings, crop="tomato")
        assert len(result) >= 1

    def test_irrelevant_sensor_types(self):
        """Test unrelated sensor types don't trigger combined rules"""
        readings = [
            {"sensor_type": "soil_ec", "value": 7.0},
            {"sensor_type": "soil_temperature", "value": 45},
        ]
        result = evaluate_combined_rules(readings)
        assert result == []
