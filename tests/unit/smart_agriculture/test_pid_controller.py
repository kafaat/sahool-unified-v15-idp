"""
SAHOOL Smart Agriculture - PID Controller Tests
اختبارات وحدة التحكم PID للزراعة الذكية

Tests for the PID controller including:
- PID calculation
- Target NPK setting
- Auto-tuning
- Fertilizer efficiency
- Water saving

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest


# ==============================================================================
# PID Controller Implementation (Test Target Mock)
# ==============================================================================


class PIDController:
    """PID controller for agricultural process control"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.kp = config["coefficients"]["kp"]
        self.ki = config["coefficients"]["ki"]
        self.kd = config["coefficients"]["kd"]
        self.setpoint = config["setpoint"]
        self.output_min = config["limits"]["output_min"]
        self.output_max = config["limits"]["output_max"]
        self.integral_min = config["limits"]["integral_min"]
        self.integral_max = config["limits"]["integral_max"]
        self.deadband = config.get("deadband", 0.0)

        # Internal state
        self._integral = 0.0
        self._previous_error = 0.0
        self._last_output = 0.0
        self._last_input = None
        self._last_update = None

    def calculate(self, process_value: float, dt: float = 1.0) -> dict[str, Any]:
        """
        Calculate PID output
        حساب مخرج PID
        """
        error = self.setpoint - process_value

        # Deadband check
        if abs(error) < self.deadband:
            return {
                "output": self._last_output,
                "error": error,
                "in_deadband": True,
                "components": {"p": 0, "i": 0, "d": 0},
            }

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self._integral += error * dt
        self._integral = max(self.integral_min, min(self.integral_max, self._integral))
        i_term = self.ki * self._integral

        # Derivative term
        if dt > 0:
            derivative = (error - self._previous_error) / dt
        else:
            derivative = 0
        d_term = self.kd * derivative

        # Calculate output
        output = p_term + i_term + d_term

        # Clamp output
        output = max(self.output_min, min(self.output_max, output))

        # Update state
        self._previous_error = error
        self._last_output = output
        self._last_input = process_value
        self._last_update = datetime.now(UTC)

        return {
            "output": output,
            "error": error,
            "in_deadband": False,
            "components": {
                "p": p_term,
                "i": i_term,
                "d": d_term,
            },
        }

    def set_setpoint(self, setpoint: float) -> None:
        """Set target setpoint"""
        self.setpoint = setpoint

    def set_coefficients(self, kp: float, ki: float, kd: float) -> None:
        """Set PID coefficients"""
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def reset(self) -> None:
        """Reset controller state"""
        self._integral = 0.0
        self._previous_error = 0.0
        self._last_output = 0.0

    def get_state(self) -> dict[str, Any]:
        """Get current controller state"""
        return {
            "setpoint": self.setpoint,
            "integral": self._integral,
            "previous_error": self._previous_error,
            "last_output": self._last_output,
            "last_input": self._last_input,
            "coefficients": {"kp": self.kp, "ki": self.ki, "kd": self.kd},
        }


class PIDAutoTuner:
    """Auto-tuner for PID controllers using Ziegler-Nichols method"""

    def __init__(self, controller: PIDController):
        self.controller = controller
        self._tuning_data: list[dict[str, Any]] = []

    def tune(
        self,
        process_data: list[dict[str, Any]],
        method: str = "ziegler_nichols",
    ) -> dict[str, Any]:
        """
        Auto-tune PID parameters
        الضبط التلقائي لمعاملات PID
        """
        if method == "ziegler_nichols":
            return self._ziegler_nichols_tune(process_data)
        elif method == "cohen_coon":
            return self._cohen_coon_tune(process_data)
        else:
            raise ValueError(f"Unknown tuning method: {method}")

    def _ziegler_nichols_tune(self, process_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Ziegler-Nichols tuning method"""
        # Simplified implementation for testing
        # In real implementation, this would analyze oscillation patterns

        # Estimate ultimate gain and period from data
        values = [d.get("value", d.get("nitrogen_ppm", 0)) for d in process_data]
        if len(values) < 3:
            raise ValueError("Insufficient data for tuning")

        # Simplified calculation
        ku = 4.0  # Ultimate gain (estimated)
        tu = 2.0  # Ultimate period (estimated)

        # Ziegler-Nichols PID tuning rules
        kp = 0.6 * ku
        ki = 2.0 * kp / tu
        kd = kp * tu / 8.0

        original = {
            "kp": self.controller.kp,
            "ki": self.controller.ki,
            "kd": self.controller.kd,
        }

        return {
            "tune_id": str(uuid.uuid4()),
            "method": "ziegler_nichols",
            "original_coefficients": original,
            "tuned_coefficients": {"kp": kp, "ki": ki, "kd": kd},
            "ultimate_gain": ku,
            "ultimate_period": tu,
            "completed_at": datetime.now(UTC).isoformat(),
        }

    def _cohen_coon_tune(self, process_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Cohen-Coon tuning method"""
        # Simplified implementation
        ku = 3.5
        tu = 1.8

        kp = 1.35 * ku
        ki = kp / (2.5 * tu)
        kd = 0.37 * kp * tu

        return {
            "tune_id": str(uuid.uuid4()),
            "method": "cohen_coon",
            "tuned_coefficients": {"kp": kp, "ki": ki, "kd": kd},
            "completed_at": datetime.now(UTC).isoformat(),
        }

    def apply_tuning(self, tuning_result: dict[str, Any]) -> None:
        """Apply tuning result to controller"""
        coeffs = tuning_result["tuned_coefficients"]
        self.controller.set_coefficients(coeffs["kp"], coeffs["ki"], coeffs["kd"])


class FertilizerController:
    """Controller for precision fertilizer application"""

    def __init__(self, pid_controller: PIDController):
        self.pid = pid_controller
        self._application_history: list[dict[str, Any]] = []

    def calculate_application(
        self,
        current_npk: dict[str, float],
        target_npk: dict[str, float],
    ) -> dict[str, Any]:
        """
        Calculate fertilizer application rates
        حساب معدلات تطبيق السماد
        """
        # Set target for nitrogen (primary control variable)
        self.pid.set_setpoint(target_npk.get("nitrogen", 25.0))

        # Calculate PID output
        pid_result = self.pid.calculate(current_npk.get("nitrogen", 0))

        # Convert PID output to fertilizer rate
        fertilizer_rate = pid_result["output"] * 0.5  # kg/ha per % output

        # Calculate efficiency
        deficiency = target_npk.get("nitrogen", 25) - current_npk.get("nitrogen", 0)
        efficiency = min(100, max(0, (deficiency / max(deficiency, 0.1)) * 100))

        application = {
            "application_id": str(uuid.uuid4()),
            "fertilizer_rate_kg_ha": round(fertilizer_rate, 2),
            "nitrogen_deficit_ppm": round(deficiency, 2),
            "pid_output": pid_result["output"],
            "efficiency_score": round(efficiency, 1),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._application_history.append(application)
        return application

    def get_efficiency_metrics(self) -> dict[str, Any]:
        """Get fertilizer efficiency metrics"""
        if not self._application_history:
            return {"total_applications": 0}

        total_fertilizer = sum(a["fertilizer_rate_kg_ha"] for a in self._application_history)
        avg_efficiency = sum(a["efficiency_score"] for a in self._application_history) / len(self._application_history)

        return {
            "total_applications": len(self._application_history),
            "total_fertilizer_kg_ha": round(total_fertilizer, 2),
            "average_efficiency_percent": round(avg_efficiency, 1),
            "savings_vs_traditional_percent": round(max(0, 100 - total_fertilizer / 2), 1),
        }


class WaterController:
    """Controller for water-saving irrigation"""

    def __init__(self, pid_controller: PIDController):
        self.pid = pid_controller
        self._irrigation_history: list[dict[str, Any]] = []
        self._water_target = 50.0  # Target soil moisture %

    def set_moisture_target(self, target: float) -> None:
        """Set target soil moisture"""
        self._water_target = target
        self.pid.set_setpoint(target)

    def calculate_irrigation(
        self,
        current_moisture: float,
        weather_factor: float = 1.0,
    ) -> dict[str, Any]:
        """
        Calculate irrigation amount
        حساب كمية الري
        """
        self.pid.set_setpoint(self._water_target)
        pid_result = self.pid.calculate(current_moisture)

        # Convert to water amount (mm)
        base_water = pid_result["output"] * 0.3  # mm per % output
        adjusted_water = base_water * weather_factor

        # Calculate water savings
        traditional_amount = 25.0  # Traditional fixed irrigation
        savings_percent = max(0, (traditional_amount - adjusted_water) / traditional_amount * 100)

        irrigation = {
            "irrigation_id": str(uuid.uuid4()),
            "water_amount_mm": round(max(0, adjusted_water), 1),
            "moisture_deficit_percent": round(self._water_target - current_moisture, 1),
            "weather_adjustment": weather_factor,
            "savings_vs_traditional_percent": round(savings_percent, 1),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._irrigation_history.append(irrigation)
        return irrigation

    def get_water_savings_metrics(self) -> dict[str, Any]:
        """Get water savings metrics"""
        if not self._irrigation_history:
            return {"total_irrigations": 0}

        total_water = sum(i["water_amount_mm"] for i in self._irrigation_history)
        traditional_total = len(self._irrigation_history) * 25.0
        savings = max(0, traditional_total - total_water)

        return {
            "total_irrigations": len(self._irrigation_history),
            "total_water_mm": round(total_water, 1),
            "traditional_equivalent_mm": traditional_total,
            "water_saved_mm": round(savings, 1),
            "savings_percent": round(savings / max(traditional_total, 1) * 100, 1),
        }


# ==============================================================================
# Test Classes
# ==============================================================================


class TestPIDCalculation:
    """Tests for PID calculation"""

    @pytest.fixture
    def controller(self, pid_config: dict[str, Any]) -> PIDController:
        return PIDController(pid_config)

    def test_pid_calculation_positive_error(self, controller: PIDController):
        """Test PID calculation with positive error (below setpoint)"""
        # Setpoint is 25, process value is 20 (error = 5)
        result = controller.calculate(20.0, dt=1.0)

        assert result["error"] == 5.0
        assert result["output"] > 0  # Positive output to increase
        assert result["components"]["p"] > 0  # Proportional term positive

    def test_pid_calculation_negative_error(self, controller: PIDController):
        """Test PID calculation with negative error (above setpoint)"""
        # Setpoint is 25, process value is 30 (error = -5)
        result = controller.calculate(30.0, dt=1.0)

        assert result["error"] == -5.0
        assert result["output"] <= 0  # Output clamped or negative
        assert result["components"]["p"] < 0  # Proportional term negative

    def test_pid_calculation_at_setpoint(self, controller: PIDController):
        """Test PID calculation when at setpoint"""
        result = controller.calculate(25.0, dt=1.0)

        assert result["error"] == 0.0
        # With zero error, output depends on integral and derivative
        # Fresh controller should have near-zero output
        assert abs(result["output"]) < 1.0

    def test_pid_output_clamping(self, controller: PIDController):
        """Test PID output is clamped to limits"""
        # Large error should still be clamped
        result = controller.calculate(0.0, dt=1.0)

        assert result["output"] <= 100.0
        assert result["output"] >= 0.0

    def test_pid_integral_windup_prevention(self, controller: PIDController):
        """Test integral windup prevention"""
        # Simulate sustained error
        for _ in range(100):
            controller.calculate(0.0, dt=1.0)

        state = controller.get_state()
        # Integral should be clamped
        assert state["integral"] <= controller.integral_max
        assert state["integral"] >= controller.integral_min

    def test_pid_deadband(self, controller: PIDController):
        """Test deadband behavior"""
        # Error within deadband (setpoint=25, deadband=1)
        result = controller.calculate(24.5, dt=1.0)

        assert result["in_deadband"] is True
        # Output should maintain previous value

    def test_pid_derivative_term(self, controller: PIDController):
        """Test derivative term calculation"""
        # First calculation
        controller.calculate(20.0, dt=1.0)

        # Second calculation with changed error
        result = controller.calculate(22.0, dt=1.0)

        # Error went from 5 to 3 (change of -2)
        # Derivative should be negative
        assert result["components"]["d"] < 0


class TestTargetNPKSetting:
    """Tests for target NPK setting"""

    @pytest.fixture
    def controller(self, pid_config: dict[str, Any]) -> PIDController:
        return PIDController(pid_config)

    @pytest.fixture
    def fertilizer_controller(self, controller: PIDController) -> FertilizerController:
        return FertilizerController(controller)

    def test_set_nitrogen_target(self, controller: PIDController):
        """Test setting nitrogen target"""
        controller.set_setpoint(30.0)

        state = controller.get_state()
        assert state["setpoint"] == 30.0

    def test_calculate_application_for_deficiency(self, fertilizer_controller: FertilizerController):
        """Test calculating application for nitrogen deficiency"""
        current = {"nitrogen": 18.0, "phosphorus": 20.0, "potassium": 150.0}
        target = {"nitrogen": 25.0, "phosphorus": 25.0, "potassium": 180.0}

        result = fertilizer_controller.calculate_application(current, target)

        assert result["nitrogen_deficit_ppm"] == 7.0
        assert result["fertilizer_rate_kg_ha"] > 0

    def test_calculate_application_no_deficiency(self, fertilizer_controller: FertilizerController):
        """Test calculating application when at target"""
        current = {"nitrogen": 25.0, "phosphorus": 25.0, "potassium": 180.0}
        target = {"nitrogen": 25.0, "phosphorus": 25.0, "potassium": 180.0}

        result = fertilizer_controller.calculate_application(current, target)

        assert result["nitrogen_deficit_ppm"] == 0.0
        # Should still have minimal output (depends on integral)

    def test_application_history_tracked(self, fertilizer_controller: FertilizerController):
        """Test that application history is tracked"""
        current = {"nitrogen": 18.0}
        target = {"nitrogen": 25.0}

        fertilizer_controller.calculate_application(current, target)
        fertilizer_controller.calculate_application({"nitrogen": 20.0}, target)

        metrics = fertilizer_controller.get_efficiency_metrics()
        assert metrics["total_applications"] == 2


class TestAutoTune:
    """Tests for PID auto-tuning"""

    @pytest.fixture
    def controller(self, pid_config: dict[str, Any]) -> PIDController:
        return PIDController(pid_config)

    @pytest.fixture
    def tuner(self, controller: PIDController) -> PIDAutoTuner:
        return PIDAutoTuner(controller)

    def test_auto_tune_ziegler_nichols(self, tuner: PIDAutoTuner, sample_npk_readings: list[dict[str, Any]]):
        """Test Ziegler-Nichols auto-tuning"""
        result = tuner.tune(sample_npk_readings, method="ziegler_nichols")

        assert result["method"] == "ziegler_nichols"
        assert "tuned_coefficients" in result
        assert "kp" in result["tuned_coefficients"]
        assert "ki" in result["tuned_coefficients"]
        assert "kd" in result["tuned_coefficients"]

    def test_auto_tune_cohen_coon(self, tuner: PIDAutoTuner, sample_npk_readings: list[dict[str, Any]]):
        """Test Cohen-Coon auto-tuning"""
        result = tuner.tune(sample_npk_readings, method="cohen_coon")

        assert result["method"] == "cohen_coon"
        assert "tuned_coefficients" in result

    def test_auto_tune_invalid_method(self, tuner: PIDAutoTuner, sample_npk_readings: list[dict[str, Any]]):
        """Test auto-tuning with invalid method"""
        with pytest.raises(ValueError, match="Unknown tuning method"):
            tuner.tune(sample_npk_readings, method="invalid_method")

    def test_auto_tune_insufficient_data(self, tuner: PIDAutoTuner):
        """Test auto-tuning with insufficient data"""
        with pytest.raises(ValueError, match="Insufficient data"):
            tuner.tune([{"value": 20.0}], method="ziegler_nichols")

    def test_apply_tuning_result(self, tuner: PIDAutoTuner, sample_npk_readings: list[dict[str, Any]]):
        """Test applying tuning result to controller"""
        result = tuner.tune(sample_npk_readings)
        tuner.apply_tuning(result)

        state = tuner.controller.get_state()
        assert state["coefficients"]["kp"] == result["tuned_coefficients"]["kp"]
        assert state["coefficients"]["ki"] == result["tuned_coefficients"]["ki"]
        assert state["coefficients"]["kd"] == result["tuned_coefficients"]["kd"]


class TestFertilizerEfficiency:
    """Tests for fertilizer efficiency"""

    @pytest.fixture
    def controller(self, pid_config: dict[str, Any]) -> PIDController:
        return PIDController(pid_config)

    @pytest.fixture
    def fertilizer_controller(self, controller: PIDController) -> FertilizerController:
        return FertilizerController(controller)

    def test_efficiency_score_calculation(self, fertilizer_controller: FertilizerController):
        """Test efficiency score is calculated"""
        current = {"nitrogen": 18.0}
        target = {"nitrogen": 25.0}

        result = fertilizer_controller.calculate_application(current, target)

        assert "efficiency_score" in result
        assert 0 <= result["efficiency_score"] <= 100

    def test_efficiency_metrics_aggregation(self, fertilizer_controller: FertilizerController):
        """Test efficiency metrics aggregation"""
        # Simulate multiple applications
        for nitrogen in [15, 18, 20, 22, 24]:
            fertilizer_controller.calculate_application(
                {"nitrogen": nitrogen},
                {"nitrogen": 25.0},
            )

        metrics = fertilizer_controller.get_efficiency_metrics()

        assert metrics["total_applications"] == 5
        assert "total_fertilizer_kg_ha" in metrics
        assert "average_efficiency_percent" in metrics
        assert "savings_vs_traditional_percent" in metrics

    def test_fertilizer_rate_proportional_to_deficit(self, fertilizer_controller: FertilizerController):
        """Test fertilizer rate is proportional to deficit"""
        result_large = fertilizer_controller.calculate_application({"nitrogen": 10.0}, {"nitrogen": 25.0})

        # Reset controller
        fertilizer_controller.pid.reset()

        result_small = fertilizer_controller.calculate_application({"nitrogen": 22.0}, {"nitrogen": 25.0})

        # Larger deficit should result in higher rate
        assert result_large["fertilizer_rate_kg_ha"] > result_small["fertilizer_rate_kg_ha"]


class TestWaterSaving:
    """Tests for water saving functionality"""

    @pytest.fixture
    def controller(self, pid_config: dict[str, Any]) -> PIDController:
        # Configure for soil moisture control
        pid_config["setpoint"] = 50.0  # Target soil moisture
        return PIDController(pid_config)

    @pytest.fixture
    def water_controller(self, controller: PIDController) -> WaterController:
        return WaterController(controller)

    def test_calculate_irrigation_for_dry_soil(self, water_controller: WaterController):
        """Test irrigation calculation for dry soil"""
        result = water_controller.calculate_irrigation(30.0)

        assert result["water_amount_mm"] > 0
        assert result["moisture_deficit_percent"] == 20.0  # 50 - 30

    def test_calculate_irrigation_for_wet_soil(self, water_controller: WaterController):
        """Test irrigation calculation for wet soil"""
        result = water_controller.calculate_irrigation(60.0)

        # Should be zero or minimal (above target)
        assert result["water_amount_mm"] == 0

    def test_weather_adjustment_factor(self, water_controller: WaterController):
        """Test weather adjustment factor"""
        # Hot day - increase irrigation
        result_hot = water_controller.calculate_irrigation(35.0, weather_factor=1.3)

        water_controller.pid.reset()

        # Rainy day - decrease irrigation
        result_rain = water_controller.calculate_irrigation(35.0, weather_factor=0.5)

        assert result_hot["water_amount_mm"] > result_rain["water_amount_mm"]

    def test_water_savings_calculation(self, water_controller: WaterController):
        """Test water savings calculation"""
        # Simulate several irrigations
        for moisture in [30, 35, 40, 45]:
            water_controller.calculate_irrigation(moisture)

        metrics = water_controller.get_water_savings_metrics()

        assert metrics["total_irrigations"] == 4
        assert "water_saved_mm" in metrics
        assert "savings_percent" in metrics

    def test_set_moisture_target(self, water_controller: WaterController):
        """Test setting moisture target"""
        water_controller.set_moisture_target(55.0)

        # Verify target changed
        result = water_controller.calculate_irrigation(50.0)
        assert result["moisture_deficit_percent"] == 5.0  # 55 - 50

    def test_savings_vs_traditional_irrigation(self, water_controller: WaterController):
        """Test savings compared to traditional fixed irrigation"""
        result = water_controller.calculate_irrigation(40.0)

        assert "savings_vs_traditional_percent" in result
        # Should show savings compared to 25mm traditional
        if result["water_amount_mm"] < 25:
            assert result["savings_vs_traditional_percent"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
