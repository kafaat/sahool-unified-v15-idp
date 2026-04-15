"""
SAHOOL Smart Agriculture - IFTTT Controller Tests
اختبارات وحدة التحكم IFTTT للزراعة الذكية

Tests for the IFTTT controller including:
- Adding rules
- Temperature triggers
- Light triggers
- Energy optimization
- Multiple conditions

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, time, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from .conftest import ActionType, TriggerType

# ==============================================================================
# IFTTT Controller Implementation (Test Target Mock)
# ==============================================================================


class IFTTTRule:
    """Single IFTTT rule"""

    def __init__(self, config: dict[str, Any]):
        self.rule_id = config.get("rule_id", str(uuid.uuid4()))
        self.name = config.get("name_en", "Unnamed Rule")
        self.name_ar = config.get("name_ar", "")
        self.enabled = config.get("enabled", True)
        self.priority = config.get("priority", 10)
        self.trigger = config.get("trigger", {})
        self.compound_trigger = config.get("compound_trigger")
        self.action = config.get("action", {})
        self.cooldown_minutes = config.get("cooldown_minutes", 5)
        self.last_triggered = None
        self.trigger_count = 0

    def is_in_cooldown(self) -> bool:
        """Check if rule is in cooldown period"""
        if self.last_triggered is None:
            return False

        cooldown_end = self.last_triggered + timedelta(minutes=self.cooldown_minutes)
        return datetime.now(UTC) < cooldown_end

    def mark_triggered(self) -> None:
        """Mark rule as triggered"""
        self.last_triggered = datetime.now(UTC)
        self.trigger_count += 1


class IFTTTController:
    """IFTTT automation controller for smart agriculture"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._rules: dict[str, IFTTTRule] = {}
        self._execution_history: list[dict[str, Any]] = []
        self._energy_mode = config.get("energy_optimization", {}).get("enabled", False)

    def add_rule(self, rule_config: dict[str, Any]) -> dict[str, Any]:
        """
        Add a new automation rule
        إضافة قاعدة أتمتة جديدة
        """
        rule = IFTTTRule(rule_config)

        # Validate rule
        if not rule.trigger and not rule.compound_trigger:
            raise ValueError("Rule must have a trigger or compound_trigger")

        if not rule.action:
            raise ValueError("Rule must have an action")

        max_rules = self.config.get("max_rules", 100)
        if len(self._rules) >= max_rules:
            raise ValueError(f"Maximum number of rules ({max_rules}) reached")

        self._rules[rule.rule_id] = rule

        return {
            "success": True,
            "rule_id": rule.rule_id,
            "name": rule.name,
        }

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> IFTTTRule | None:
        """Get a rule by ID"""
        return self._rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> list[IFTTTRule]:
        """List all rules"""
        rules = list(self._rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return sorted(rules, key=lambda r: r.priority)

    def evaluate_trigger(
        self,
        rule: IFTTTRule,
        sensor_data: dict[str, Any],
        current_time: datetime | None = None,
    ) -> bool:
        """
        Evaluate if a rule's trigger condition is met
        تقييم ما إذا كان شرط التشغيل للقاعدة متحققًا
        """
        if not rule.enabled:
            return False

        if rule.is_in_cooldown():
            return False

        if rule.compound_trigger:
            return self._evaluate_compound_trigger(rule.compound_trigger, sensor_data, current_time)

        return self._evaluate_single_trigger(rule.trigger, sensor_data, current_time)

    def _evaluate_single_trigger(
        self,
        trigger: dict[str, Any],
        sensor_data: dict[str, Any],
        current_time: datetime | None = None,
    ) -> bool:
        """Evaluate a single trigger condition"""
        trigger_type = trigger.get("type")
        condition = trigger.get("condition")
        threshold = trigger.get("threshold")

        # Get sensor value
        type_to_key = {
            TriggerType.TEMPERATURE.value: "temperature",
            TriggerType.HUMIDITY.value: "humidity",
            TriggerType.SOIL_MOISTURE.value: "soil_moisture",
            TriggerType.LIGHT.value: "light",
        }

        # Handle time-based trigger
        if trigger_type == TriggerType.TIME.value:
            return self._evaluate_time_condition(trigger, current_time)

        sensor_key = type_to_key.get(trigger_type)
        if not sensor_key:
            return False

        value = sensor_data.get(sensor_key)
        if value is None:
            return False

        # Check time window if specified
        time_window = trigger.get("time_window")
        if time_window and current_time:
            if not self._is_in_time_window(time_window, current_time):
                return False

        # Evaluate condition
        return self._compare(value, condition, threshold)

    def _evaluate_compound_trigger(
        self,
        compound: dict[str, Any],
        sensor_data: dict[str, Any],
        current_time: datetime | None = None,
    ) -> bool:
        """Evaluate compound trigger with multiple conditions"""
        operator = compound.get("operator", "AND")
        conditions = compound.get("conditions", [])

        results = []
        for cond in conditions:
            result = self._evaluate_single_trigger(cond, sensor_data, current_time)
            results.append(result)

        if operator == "AND":
            return all(results)
        elif operator == "OR":
            return any(results)
        else:
            return False

    def _compare(self, value: float, condition: str, threshold: float) -> bool:
        """Compare value against condition and threshold"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return abs(value - threshold) < 0.1
        elif condition == "greater_or_equal":
            return value >= threshold
        elif condition == "less_or_equal":
            return value <= threshold
        return False

    def _evaluate_time_condition(
        self,
        trigger: dict[str, Any],
        current_time: datetime | None = None,
    ) -> bool:
        """Evaluate time-based condition"""
        if current_time is None:
            current_time = datetime.now(UTC)

        condition = trigger.get("condition")
        if condition == "between":
            start_str = trigger.get("start", "00:00")
            end_str = trigger.get("end", "23:59")

            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))

            current_minutes = current_time.hour * 60 + current_time.minute
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min

            return start_minutes <= current_minutes <= end_minutes

        return False

    def _is_in_time_window(
        self,
        window: dict[str, str],
        current_time: datetime,
    ) -> bool:
        """Check if current time is in window"""
        start_str = window.get("start", "00:00")
        end_str = window.get("end", "23:59")

        start_hour, start_min = map(int, start_str.split(":"))
        end_hour, end_min = map(int, end_str.split(":"))

        current_minutes = current_time.hour * 60 + current_time.minute
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        return start_minutes <= current_minutes <= end_minutes

    async def execute_action(
        self,
        rule: IFTTTRule,
        actuator_service: Any,
    ) -> dict[str, Any]:
        """
        Execute the action of a triggered rule
        تنفيذ إجراء القاعدة المشغلة
        """
        action = rule.action
        action_type = action.get("type")
        params = action.get("parameters", {})

        # Check energy optimization
        if self._energy_mode and self._is_peak_hours():
            if not self._is_critical_action(action_type):
                return {
                    "success": False,
                    "reason": "deferred_peak_hours",
                    "action_type": action_type,
                }

        # Execute action
        result = await actuator_service.execute_action(action_type, params)

        # Mark rule as triggered
        rule.mark_triggered()

        execution = {
            "execution_id": str(uuid.uuid4()),
            "rule_id": rule.rule_id,
            "action_type": action_type,
            "parameters": params,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._execution_history.append(execution)

        return {
            "success": True,
            "execution": execution,
        }

    def _is_peak_hours(self) -> bool:
        """Check if current time is during peak energy hours"""
        energy_config = self.config.get("energy_optimization", {})
        peak_start = energy_config.get("peak_hours_start", "12:00")
        peak_end = energy_config.get("peak_hours_end", "17:00")

        now = datetime.now(UTC)
        return self._is_in_time_window(
            {"start": peak_start, "end": peak_end},
            now,
        )

    def _is_critical_action(self, action_type: str) -> bool:
        """Check if action is critical (cannot be deferred)"""
        critical_actions = [
            ActionType.ALERT.value,
            ActionType.IRRIGATION.value,  # Water is critical
        ]
        return action_type in critical_actions

    def evaluate_all_rules(
        self,
        sensor_data: dict[str, Any],
        current_time: datetime | None = None,
    ) -> list[IFTTTRule]:
        """Evaluate all rules and return triggered ones"""
        triggered = []
        for rule in self.list_rules(enabled_only=True):
            if self.evaluate_trigger(rule, sensor_data, current_time):
                triggered.append(rule)
        return triggered

    def get_execution_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get execution history"""
        return self._execution_history[-limit:]


# ==============================================================================
# Test Classes
# ==============================================================================


class TestAddRule:
    """Tests for adding IFTTT rules"""

    @pytest.fixture
    def controller(self, ifttt_controller_config: dict[str, Any]) -> IFTTTController:
        return IFTTTController(ifttt_controller_config)

    def test_add_rule_success(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test successfully adding a rule"""
        result = controller.add_rule(sample_ifttt_rule)

        assert result["success"] is True
        assert "rule_id" in result

        rule = controller.get_rule(result["rule_id"])
        assert rule is not None
        assert rule.name == sample_ifttt_rule["name_en"]

    def test_add_rule_without_trigger_fails(self, controller: IFTTTController):
        """Test adding rule without trigger fails"""
        invalid_rule = {
            "name_en": "Invalid Rule",
            "action": {"type": ActionType.ALERT.value},
        }

        with pytest.raises(ValueError, match="must have a trigger"):
            controller.add_rule(invalid_rule)

    def test_add_rule_without_action_fails(self, controller: IFTTTController):
        """Test adding rule without action fails"""
        invalid_rule = {
            "name_en": "Invalid Rule",
            "trigger": {
                "type": TriggerType.TEMPERATURE.value,
                "condition": "greater_than",
                "threshold": 35,
            },
        }

        with pytest.raises(ValueError, match="must have an action"):
            controller.add_rule(invalid_rule)

    def test_add_rule_respects_max_limit(self, controller: IFTTTController):
        """Test adding rules respects maximum limit"""
        controller.config["max_rules"] = 3

        for i in range(3):
            controller.add_rule(
                {
                    "name_en": f"Rule {i}",
                    "trigger": {
                        "type": TriggerType.TEMPERATURE.value,
                        "condition": "greater_than",
                        "threshold": 30 + i,
                    },
                    "action": {"type": ActionType.ALERT.value},
                }
            )

        with pytest.raises(ValueError, match="Maximum number of rules"):
            controller.add_rule(
                {
                    "name_en": "Rule 4",
                    "trigger": {
                        "type": TriggerType.TEMPERATURE.value,
                        "condition": "greater_than",
                        "threshold": 40,
                    },
                    "action": {"type": ActionType.ALERT.value},
                }
            )

    def test_remove_rule(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test removing a rule"""
        result = controller.add_rule(sample_ifttt_rule)
        rule_id = result["rule_id"]

        removed = controller.remove_rule(rule_id)
        assert removed is True
        assert controller.get_rule(rule_id) is None

    def test_list_rules_sorted_by_priority(self, controller: IFTTTController):
        """Test rules are listed sorted by priority"""
        controller.add_rule(
            {
                "name_en": "Low Priority",
                "priority": 10,
                "trigger": {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "greater_than",
                    "threshold": 35,
                },
                "action": {"type": ActionType.ALERT.value},
            }
        )
        controller.add_rule(
            {
                "name_en": "High Priority",
                "priority": 1,
                "trigger": {
                    "type": TriggerType.HUMIDITY.value,
                    "condition": "less_than",
                    "threshold": 30,
                },
                "action": {"type": ActionType.ALERT.value},
            }
        )

        rules = controller.list_rules()
        assert rules[0].name == "High Priority"
        assert rules[1].name == "Low Priority"


class TestTemperatureTrigger:
    """Tests for temperature trigger"""

    @pytest.fixture
    def controller(self, ifttt_controller_config: dict[str, Any]) -> IFTTTController:
        return IFTTTController(ifttt_controller_config)

    def test_temperature_greater_than_trigger(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test temperature greater than trigger"""
        controller.add_rule(sample_ifttt_rule)
        rule = list(controller._rules.values())[0]

        # Temperature above threshold (35)
        sensor_data = {"temperature": 38.0}
        assert controller.evaluate_trigger(rule, sensor_data) is True

        # Temperature below threshold
        sensor_data = {"temperature": 30.0}
        assert controller.evaluate_trigger(rule, sensor_data) is False

    def test_temperature_less_than_trigger(self, controller: IFTTTController):
        """Test temperature less than trigger"""
        controller.add_rule(
            {
                "name_en": "Cold Alert",
                "trigger": {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "less_than",
                    "threshold": 5.0,
                },
                "action": {"type": ActionType.HEATING.value},
            }
        )
        rule = list(controller._rules.values())[0]

        assert controller.evaluate_trigger(rule, {"temperature": 3.0}) is True
        assert controller.evaluate_trigger(rule, {"temperature": 10.0}) is False

    def test_temperature_trigger_missing_data(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test trigger returns false for missing sensor data"""
        controller.add_rule(sample_ifttt_rule)
        rule = list(controller._rules.values())[0]

        # No temperature data
        sensor_data = {"humidity": 60.0}
        assert controller.evaluate_trigger(rule, sensor_data) is False

    def test_disabled_rule_not_triggered(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test disabled rules are not triggered"""
        sample_ifttt_rule["enabled"] = False
        controller.add_rule(sample_ifttt_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {"temperature": 40.0}
        assert controller.evaluate_trigger(rule, sensor_data) is False


class TestLightTrigger:
    """Tests for light trigger"""

    @pytest.fixture
    def controller(self, ifttt_controller_config: dict[str, Any]) -> IFTTTController:
        return IFTTTController(ifttt_controller_config)

    def test_light_less_than_trigger(
        self,
        controller: IFTTTController,
        sample_light_rule: dict[str, Any],
    ):
        """Test light less than trigger"""
        controller.add_rule(sample_light_rule)
        rule = list(controller._rules.values())[0]

        # Low light during day time
        sensor_data = {"light": 5000}
        current_time = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)  # 10:00 AM
        assert controller.evaluate_trigger(rule, sensor_data, current_time) is True

    def test_light_trigger_respects_time_window(
        self,
        controller: IFTTTController,
        sample_light_rule: dict[str, Any],
    ):
        """Test light trigger respects time window"""
        controller.add_rule(sample_light_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {"light": 5000}

        # During daytime window (06:00-18:00)
        daytime = datetime(2024, 1, 15, 14, 0, tzinfo=UTC)
        assert controller.evaluate_trigger(rule, sensor_data, daytime) is True

        # Outside window (night)
        nighttime = datetime(2024, 1, 15, 22, 0, tzinfo=UTC)
        assert controller.evaluate_trigger(rule, sensor_data, nighttime) is False

    def test_light_above_threshold_not_triggered(
        self,
        controller: IFTTTController,
        sample_light_rule: dict[str, Any],
    ):
        """Test light above threshold does not trigger"""
        controller.add_rule(sample_light_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {"light": 50000}  # Bright
        current_time = datetime(2024, 1, 15, 12, 0, tzinfo=UTC)
        assert controller.evaluate_trigger(rule, sensor_data, current_time) is False


class TestEnergyOptimization:
    """Tests for energy optimization"""

    @pytest.fixture
    def controller(self, ifttt_controller_config: dict[str, Any]) -> IFTTTController:
        ifttt_controller_config["energy_optimization"]["enabled"] = True
        return IFTTTController(ifttt_controller_config)

    @pytest.mark.asyncio
    async def test_non_critical_action_deferred_during_peak(
        self, controller: IFTTTController, mock_actuator_service: MagicMock
    ):
        """Test non-critical actions are deferred during peak hours"""
        controller.add_rule(
            {
                "name_en": "Ventilation Rule",
                "trigger": {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "greater_than",
                    "threshold": 30,
                },
                "action": {"type": ActionType.VENTILATION.value, "parameters": {"fan_speed": 50}},
            }
        )
        rule = list(controller._rules.values())[0]

        # Simulate peak hours
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(controller, "_is_peak_hours", lambda: True)
            result = await controller.execute_action(rule, mock_actuator_service)

        assert result["success"] is False
        assert result["reason"] == "deferred_peak_hours"

    @pytest.mark.asyncio
    async def test_critical_action_not_deferred_during_peak(
        self, controller: IFTTTController, mock_actuator_service: MagicMock
    ):
        """Test critical actions are not deferred during peak hours"""
        controller.add_rule(
            {
                "name_en": "Emergency Irrigation",
                "trigger": {
                    "type": TriggerType.SOIL_MOISTURE.value,
                    "condition": "less_than",
                    "threshold": 20,
                },
                "action": {"type": ActionType.IRRIGATION.value, "parameters": {"duration": 30}},
            }
        )
        rule = list(controller._rules.values())[0]

        # Simulate peak hours
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(controller, "_is_peak_hours", lambda: True)
            result = await controller.execute_action(rule, mock_actuator_service)

        # Irrigation is critical, should execute
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_action_executes_outside_peak_hours(
        self, controller: IFTTTController, mock_actuator_service: MagicMock
    ):
        """Test actions execute normally outside peak hours"""
        controller.add_rule(
            {
                "name_en": "Ventilation Rule",
                "trigger": {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "greater_than",
                    "threshold": 30,
                },
                "action": {"type": ActionType.VENTILATION.value, "parameters": {"fan_speed": 50}},
            }
        )
        rule = list(controller._rules.values())[0]

        # Simulate off-peak hours
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(controller, "_is_peak_hours", lambda: False)
            result = await controller.execute_action(rule, mock_actuator_service)

        assert result["success"] is True


class TestMultipleConditions:
    """Tests for multiple conditions (compound triggers)"""

    @pytest.fixture
    def controller(self, ifttt_controller_config: dict[str, Any]) -> IFTTTController:
        return IFTTTController(ifttt_controller_config)

    def test_and_compound_trigger_all_met(
        self,
        controller: IFTTTController,
        sample_compound_rule: dict[str, Any],
    ):
        """Test AND compound trigger when all conditions are met"""
        controller.add_rule(sample_compound_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {
            "soil_moisture": 30.0,  # Below 35
            "temperature": 28.0,  # Below 35
        }
        current_time = datetime(2024, 1, 15, 6, 30, tzinfo=UTC)  # 6:30 AM

        assert controller.evaluate_trigger(rule, sensor_data, current_time) is True

    def test_and_compound_trigger_one_not_met(
        self,
        controller: IFTTTController,
        sample_compound_rule: dict[str, Any],
    ):
        """Test AND compound trigger when one condition is not met"""
        controller.add_rule(sample_compound_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {
            "soil_moisture": 30.0,  # Below 35 - MET
            "temperature": 40.0,  # Above 35 - NOT MET
        }
        current_time = datetime(2024, 1, 15, 6, 30, tzinfo=UTC)

        assert controller.evaluate_trigger(rule, sensor_data, current_time) is False

    def test_or_compound_trigger(self, controller: IFTTTController):
        """Test OR compound trigger"""
        controller.add_rule(
            {
                "name_en": "Alert Rule",
                "compound_trigger": {
                    "operator": "OR",
                    "conditions": [
                        {
                            "type": TriggerType.TEMPERATURE.value,
                            "condition": "greater_than",
                            "threshold": 40,
                        },
                        {
                            "type": TriggerType.HUMIDITY.value,
                            "condition": "greater_than",
                            "threshold": 90,
                        },
                    ],
                },
                "action": {"type": ActionType.ALERT.value},
            }
        )
        rule = list(controller._rules.values())[0]

        # Only temperature high
        assert controller.evaluate_trigger(rule, {"temperature": 42, "humidity": 50}) is True

        # Only humidity high
        assert controller.evaluate_trigger(rule, {"temperature": 30, "humidity": 95}) is True

        # Neither high
        assert controller.evaluate_trigger(rule, {"temperature": 30, "humidity": 50}) is False

    def test_compound_with_time_condition(
        self,
        controller: IFTTTController,
        sample_compound_rule: dict[str, Any],
    ):
        """Test compound trigger with time condition"""
        controller.add_rule(sample_compound_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {"soil_moisture": 30.0, "temperature": 28.0}

        # Within time window (05:00-08:00)
        within_window = datetime(2024, 1, 15, 7, 0, tzinfo=UTC)
        assert controller.evaluate_trigger(rule, sensor_data, within_window) is True

        # Outside time window
        outside_window = datetime(2024, 1, 15, 12, 0, tzinfo=UTC)
        assert controller.evaluate_trigger(rule, sensor_data, outside_window) is False

    def test_cooldown_prevents_retrigger(
        self,
        controller: IFTTTController,
        sample_ifttt_rule: dict[str, Any],
    ):
        """Test cooldown prevents immediate re-triggering"""
        sample_ifttt_rule["cooldown_minutes"] = 15
        controller.add_rule(sample_ifttt_rule)
        rule = list(controller._rules.values())[0]

        sensor_data = {"temperature": 40.0}

        # First trigger should work
        assert controller.evaluate_trigger(rule, sensor_data) is True
        rule.mark_triggered()

        # Immediate second trigger should be blocked (in cooldown)
        assert controller.evaluate_trigger(rule, sensor_data) is False

    def test_evaluate_all_rules(self, controller: IFTTTController):
        """Test evaluating all rules at once"""
        controller.add_rule(
            {
                "name_en": "Temp Alert",
                "trigger": {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "greater_than",
                    "threshold": 35,
                },
                "action": {"type": ActionType.ALERT.value},
            }
        )
        controller.add_rule(
            {
                "name_en": "Humidity Alert",
                "trigger": {
                    "type": TriggerType.HUMIDITY.value,
                    "condition": "less_than",
                    "threshold": 30,
                },
                "action": {"type": ActionType.ALERT.value},
            }
        )

        # Only temperature high
        sensor_data = {"temperature": 40, "humidity": 50}
        triggered = controller.evaluate_all_rules(sensor_data)

        assert len(triggered) == 1
        assert triggered[0].name == "Temp Alert"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
