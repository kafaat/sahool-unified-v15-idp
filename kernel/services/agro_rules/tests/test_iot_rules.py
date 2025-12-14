"""
IoT Rules Tests - Agro Rules
"""

from kernel.services.agro_rules.src.iot_rules import (
    TaskRecommendation,
    evaluate_combined_rules,
    get_threshold,
    rule_from_sensor,
)


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
        assert (
            "temperature" in result.title_en.lower()
            or "temp" in result.title_en.lower()
        )

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
