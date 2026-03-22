"""
IoT Rules Tests - Agro Rules
"""

import pytest

try:
    from src.iot_rules import (
        TaskRecommendation,
        evaluate_combined_rules,
        get_threshold,
        rule_from_sensor,
    )
except ImportError:
    pytest.skip("agro-rules dependencies not installed", allow_module_level=True)


class TestSingleSensorRules:
    """Test single sensor rule evaluation"""

    def test_low_soil_moisture_triggers_irrigation(self):
        """Test that low soil moisture triggers irrigation task"""
        result = rule_from_sensor("soil_moisture", 15)

        assert result is not None
        assert result.task_type == "irrigation"
        assert result.priority == "high"

    def test_critical_low_moisture_triggers_urgent(self):
        """Test critical low moisture triggers urgent irrigation"""
        result = rule_from_sensor("soil_moisture", 5)

        assert result is not None
        assert result.priority == "urgent"
        assert result.urgency_hours <= 2

    def test_normal_moisture_no_task(self):
        """Test that normal moisture doesn't trigger task"""
        result = rule_from_sensor("soil_moisture", 45)
        assert result is None

    def test_high_moisture_triggers_inspection(self):
        """Test high moisture triggers drainage check"""
        result = rule_from_sensor("soil_moisture", 85)

        assert result is not None
        assert result.task_type == "inspection"

    def test_high_temperature_alert(self):
        """Test high temperature alert"""
        result = rule_from_sensor("air_temperature", 40)

        assert result is not None
        assert "temperature" in result.title_en.lower() or "temp" in result.title_en.lower()

    def test_critical_temperature_emergency(self):
        """Test critical temperature triggers emergency"""
        result = rule_from_sensor("air_temperature", 45)

        assert result is not None
        assert result.priority == "urgent"
        assert result.task_type == "emergency"

    def test_frost_warning(self):
        """Test low temperature frost warning"""
        result = rule_from_sensor("air_temperature", 2)

        assert result is not None
        assert result.priority == "urgent"
        assert "frost" in result.title_en.lower()

    def test_high_salinity_alert(self):
        """Test high soil EC triggers alert"""
        result = rule_from_sensor("soil_ec", 5.0)

        assert result is not None
        assert "salinity" in result.title_en.lower()

    def test_critical_salinity_urgent(self):
        """Test critical salinity triggers urgent task"""
        result = rule_from_sensor("soil_ec", 7.0)

        assert result is not None
        assert result.priority == "urgent"

    def test_water_flow_stopped(self):
        """Test zero water flow triggers maintenance"""
        result = rule_from_sensor("water_flow", 0)

        assert result is not None
        assert result.task_type == "maintenance"
        assert result.priority == "urgent"

    def test_low_tank_level(self):
        """Test low tank level triggers refill"""
        result = rule_from_sensor("water_level", 15)

        assert result is not None
        assert result.task_type == "maintenance"

    def test_water_flow_normal_no_task(self):
        """Test normal water flow doesn't trigger task"""
        result = rule_from_sensor("water_flow", 50)
        assert result is None

    def test_water_level_normal_no_task(self):
        """Test normal water level doesn't trigger task"""
        result = rule_from_sensor("water_level", 60)
        assert result is None

    def test_unknown_sensor_type_no_task(self):
        """Test unknown sensor type returns None"""
        result = rule_from_sensor("unknown_sensor", 42)
        assert result is None

    def test_critical_soil_temperature(self):
        """Test critical soil temperature triggers mulching task"""
        result = rule_from_sensor("soil_temperature", 42)

        assert result is not None
        assert result.task_type == "manual"
        assert result.priority == "high"
        assert "soil temperature" in result.title_en.lower() or "Soil Temperature" in result.title_en

    def test_high_soil_temperature(self):
        """Test high soil temperature triggers cooling irrigation"""
        result = rule_from_sensor("soil_temperature", 37)

        assert result is not None
        assert result.task_type == "irrigation"
        assert result.priority == "medium"

    def test_normal_soil_temperature_no_task(self):
        """Test normal soil temperature doesn't trigger task"""
        result = rule_from_sensor("soil_temperature", 25)
        assert result is None

    def test_high_air_humidity_disease_risk(self):
        """Test high air humidity triggers disease risk alert"""
        result = rule_from_sensor("air_humidity", 95)

        assert result is not None
        assert result.task_type == "inspection"
        assert result.priority == "medium"
        assert "humidity" in result.title_en.lower()

    def test_low_air_humidity(self):
        """Test low air humidity triggers irrigation check"""
        result = rule_from_sensor("air_humidity", 20)

        assert result is not None
        assert result.task_type == "inspection"
        assert result.priority == "low"

    def test_normal_air_humidity_no_task(self):
        """Test normal air humidity doesn't trigger task"""
        result = rule_from_sensor("air_humidity", 55)
        assert result is None

    def test_sensor_with_crop_specific_threshold(self):
        """Test sensor rules use crop-specific thresholds"""
        # Tomato critical low is 15, default is 10
        # Value 12 is below default low (20) but above tomato critical_low (15)
        result_default = rule_from_sensor("soil_moisture", 12, crop="default")
        result_tomato = rule_from_sensor("soil_moisture", 12, crop="tomato")

        # For default: 12 > critical_low (10) but < low (20) -> high priority
        assert result_default is not None
        assert result_default.priority == "high"

        # For tomato: 12 < critical_low (15) -> urgent
        assert result_tomato is not None
        assert result_tomato.priority == "urgent"

    def test_sensor_with_context(self):
        """Test sensor rules accept context parameter"""
        result = rule_from_sensor(
            "soil_moisture", 5,
            context={"field_id": "F001", "device_id": "D001"},
        )
        assert result is not None
        assert result.metadata is not None
        assert result.metadata["sensor_type"] == "soil_moisture"

    def test_normal_soil_ec_no_task(self):
        """Test normal soil EC doesn't trigger task"""
        result = rule_from_sensor("soil_ec", 2.0)
        assert result is None

    def test_normal_air_temperature_no_task(self):
        """Test normal air temperature doesn't trigger task"""
        result = rule_from_sensor("air_temperature", 25)
        assert result is None

    def test_normal_soil_moisture_no_task_midrange(self):
        """Test soil moisture in normal range (between low and high)"""
        result = rule_from_sensor("soil_moisture", 50)
        assert result is None


class TestCropSpecificThresholds:
    """Test crop-specific thresholds"""

    def test_tomato_thresholds(self):
        """Test tomato has different thresholds"""
        threshold = get_threshold("soil_moisture", "tomato")
        default = get_threshold("soil_moisture", "default")

        assert threshold["low"] != default["low"]

    def test_wheat_thresholds(self):
        """Test wheat thresholds"""
        threshold = get_threshold("soil_moisture", "wheat")
        assert threshold["low"] == 15  # Wheat tolerates drier soil

    def test_coffee_thresholds(self):
        """Test coffee thresholds"""
        threshold = get_threshold("soil_moisture", "coffee")
        assert threshold["low"] == 30  # Coffee needs more moisture

    def test_unknown_crop_uses_default(self):
        """Test unknown crop falls back to default thresholds"""
        threshold = get_threshold("soil_moisture", "mango")
        default = get_threshold("soil_moisture", "default")
        assert threshold == default

    def test_unknown_sensor_type_threshold(self):
        """Test unknown sensor type returns empty dict"""
        threshold = get_threshold("unknown_sensor", "default")
        assert threshold == {}

    def test_crop_missing_sensor_uses_default(self):
        """Test crop without specific sensor type uses default"""
        # Wheat doesn't define air_humidity thresholds
        threshold = get_threshold("air_humidity", "wheat")
        default = get_threshold("air_humidity", "default")
        assert threshold == default


class TestCombinedRules:
    """Test combined rule evaluation"""

    def test_heat_drought_combined(self):
        """Test high temp + low moisture triggers combined rule"""
        readings = [
            {"sensor_type": "air_temperature", "value": 38},
            {"sensor_type": "soil_moisture", "value": 18},
        ]

        results = evaluate_combined_rules(readings)

        assert len(results) > 0
        assert any(r.priority == "urgent" for r in results)

    def test_humidity_leaf_wetness_disease_risk(self):
        """Test high humidity + leaf wetness triggers disease alert"""
        readings = [
            {"sensor_type": "air_humidity", "value": 90},
            {"sensor_type": "leaf_wetness", "value": 85},
        ]

        results = evaluate_combined_rules(readings)

        assert len(results) > 0
        assert any("disease" in r.title_en.lower() for r in results)

    def test_normal_combined_no_task(self):
        """Test normal combined readings don't trigger"""
        readings = [
            {"sensor_type": "air_temperature", "value": 25},
            {"sensor_type": "soil_moisture", "value": 50},
        ]

        results = evaluate_combined_rules(readings)
        assert len(results) == 0


class TestTaskRecommendation:
    """Test TaskRecommendation dataclass"""

    def test_to_dict(self):
        """Test conversion to dict"""
        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

        d = rec.to_dict()

        assert d["title_ar"] == "اختبار"
        assert d["title_en"] == "Test"
        assert d["task_type"] == "irrigation"
        assert d["priority"] == "high"
        assert d["metadata"] == {}

    def test_to_dict_with_metadata(self):
        """Test conversion to dict with metadata"""
        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
            metadata={"sensor_type": "soil_moisture", "value": 5},
        )

        d = rec.to_dict()
        assert d["metadata"]["sensor_type"] == "soil_moisture"
        assert d["metadata"]["value"] == 5
