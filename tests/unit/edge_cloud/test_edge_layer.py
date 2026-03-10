"""
SAHOOL Edge-Cloud Edge Layer Tests
اختبارات طبقة الحافة للحوسبة الحافة-السحابة

Tests for the edge layer including:
- Data cleaning and validation
- Local inference execution
- Offline autonomy capabilities
- Latency requirements (300ms target)
- Auto-irrigation triggering

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .conftest import (
    DataQuality,
    DeviceStatus,
    InferenceMode,
    SensorType,
    SyncStatus,
)


# ==============================================================================
# Edge Layer Components (Test Target Mocks)
# ==============================================================================


class DataCleaner:
    """Data cleaning and validation for edge layer"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._sensor_ranges = {
            SensorType.SOIL_MOISTURE.value: (0, 100),
            SensorType.TEMPERATURE.value: (-40, 60),
            SensorType.HUMIDITY.value: (0, 100),
            SensorType.PH.value: (0, 14),
            SensorType.EC.value: (0, 20),
            SensorType.LIGHT.value: (0, 200000),
        }

    def clean(self, readings: list[dict[str, Any]]) -> dict[str, Any]:
        """Clean and validate sensor readings"""
        cleaned = []
        rejected = []
        interpolated = []

        for reading in readings:
            validation = self._validate_reading(reading)

            if validation["valid"]:
                cleaned.append(reading)
            elif validation["can_interpolate"]:
                interpolated_reading = self._interpolate(reading, readings)
                if interpolated_reading:
                    interpolated_reading["quality"] = DataQuality.ACCEPTABLE.value
                    interpolated_reading["interpolated"] = True
                    interpolated.append(interpolated_reading)
            else:
                rejected.append(
                    {
                        "reading": reading,
                        "reason": validation["reason"],
                    }
                )

        return {
            "cleaned": cleaned,
            "interpolated": interpolated,
            "rejected": rejected,
            "stats": {
                "total": len(readings),
                "valid": len(cleaned),
                "interpolated": len(interpolated),
                "rejected": len(rejected),
                "quality_score": len(cleaned) / max(len(readings), 1),
            },
        }

    def _validate_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Validate a single reading"""
        value = reading.get("value")
        sensor_type = reading.get("sensor_type")

        # Check for null/missing values
        if value is None:
            return {
                "valid": False,
                "can_interpolate": True,
                "reason": "missing_value",
            }

        # Check range
        if sensor_type in self._sensor_ranges:
            min_val, max_val = self._sensor_ranges[sensor_type]
            if value < min_val or value > max_val:
                return {
                    "valid": False,
                    "can_interpolate": False,
                    "reason": f"out_of_range: {value} not in [{min_val}, {max_val}]",
                }

        return {"valid": True, "can_interpolate": False, "reason": None}

    def _interpolate(self, reading: dict[str, Any], all_readings: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Interpolate missing value from surrounding readings"""
        device_id = reading.get("device_id")
        sensor_type = reading.get("sensor_type")

        # Find valid readings of same type
        valid_values = [
            r["value"]
            for r in all_readings
            if r.get("device_id") == device_id and r.get("sensor_type") == sensor_type and r.get("value") is not None
        ]

        if len(valid_values) >= 2:
            interpolated_value = sum(valid_values) / len(valid_values)
            return {
                **reading,
                "value": round(interpolated_value, 2),
            }

        return None

    def detect_spikes(
        self,
        readings: list[dict[str, Any]],
        threshold_percent: float = 50.0,
    ) -> list[dict[str, Any]]:
        """Detect sudden spikes in sensor data"""
        spikes = []
        sorted_readings = sorted(readings, key=lambda r: r.get("timestamp", ""))

        for i in range(1, len(sorted_readings)):
            prev = sorted_readings[i - 1]
            curr = sorted_readings[i]

            if prev.get("value") is not None and curr.get("value") is not None:
                if prev.get("sensor_type") == curr.get("sensor_type"):
                    change_percent = (abs(curr["value"] - prev["value"]) / max(abs(prev["value"]), 0.01)) * 100

                    if change_percent > threshold_percent:
                        spikes.append(
                            {
                                "reading": curr,
                                "previous_value": prev["value"],
                                "change_percent": round(change_percent, 2),
                            }
                        )

        return spikes


class EdgeInferenceEngine:
    """Local inference engine for edge layer"""

    def __init__(self, models: dict[str, Any] | None = None):
        self.models = models or {}
        self._inference_count = 0
        self._total_latency_ms = 0

    async def run_inference(self, model_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """Run inference on edge model"""
        start_time = time.monotonic()

        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")

        # Simulate inference
        prediction = model.predict(input_data)
        latency_ms = (time.monotonic() - start_time) * 1000

        self._inference_count += 1
        self._total_latency_ms += latency_ms

        return {
            "inference_id": str(uuid.uuid4()),
            "model_id": model_id,
            "prediction": prediction["prediction"],
            "confidence": prediction["confidence"],
            "latency_ms": round(latency_ms, 2),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def run_batch_inference(self, model_id: str, inputs: list[dict[str, Any]]) -> dict[str, Any]:
        """Run batch inference"""
        start_time = time.monotonic()

        results = []
        for input_data in inputs:
            result = await self.run_inference(model_id, input_data)
            results.append(result)

        total_latency = (time.monotonic() - start_time) * 1000

        return {
            "batch_id": str(uuid.uuid4()),
            "results": results,
            "total_latency_ms": round(total_latency, 2),
            "avg_latency_ms": round(total_latency / len(inputs), 2),
        }

    def get_average_latency_ms(self) -> float:
        """Get average inference latency"""
        if self._inference_count == 0:
            return 0.0
        return self._total_latency_ms / self._inference_count


class OfflineManager:
    """Manages offline capabilities for edge layer"""

    def __init__(self, buffer_size: int = 100000):
        self._buffer: list[dict[str, Any]] = []
        self._buffer_size = buffer_size
        self._sync_status = SyncStatus.SYNCED.value
        self._last_sync = datetime.now(UTC)
        self._cloud_available = True

    def is_offline(self) -> bool:
        """Check if operating in offline mode"""
        return not self._cloud_available

    def set_cloud_status(self, available: bool) -> None:
        """Set cloud availability status"""
        self._cloud_available = available
        if not available:
            self._sync_status = SyncStatus.OFFLINE.value

    def buffer_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Buffer data for later sync"""
        if len(self._buffer) >= self._buffer_size:
            # Remove oldest entry
            self._buffer.pop(0)

        self._buffer.append(
            {
                **data,
                "buffered_at": datetime.now(UTC).isoformat(),
            }
        )

        return {
            "buffered": True,
            "buffer_size": len(self._buffer),
            "sync_status": self._sync_status,
        }

    def get_buffer_size(self) -> int:
        """Get current buffer size"""
        return len(self._buffer)

    def get_buffered_data(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Get buffered data for sync"""
        if limit:
            return self._buffer[:limit]
        return list(self._buffer)

    def clear_synced_data(self, count: int) -> None:
        """Clear synced data from buffer"""
        self._buffer = self._buffer[count:]

    async def sync_to_cloud(self) -> dict[str, Any]:
        """Sync buffered data to cloud"""
        if not self._cloud_available:
            return {
                "success": False,
                "reason": "cloud_unavailable",
                "buffer_size": len(self._buffer),
            }

        records_to_sync = len(self._buffer)
        # Simulate sync
        await asyncio.sleep(0.01)  # Minimal delay for testing

        self._buffer.clear()
        self._last_sync = datetime.now(UTC)
        self._sync_status = SyncStatus.SYNCED.value

        return {
            "success": True,
            "records_synced": records_to_sync,
            "sync_time": self._last_sync.isoformat(),
        }

    def get_offline_duration(self) -> timedelta:
        """Get duration since last successful sync"""
        return datetime.now(UTC) - self._last_sync


class AutoIrrigationController:
    """Controller for automatic irrigation triggering"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._triggers: list[dict[str, Any]] = []
        self._enabled = True

    def configure_thresholds(
        self,
        soil_moisture_min: float = 30.0,
        soil_moisture_max: float = 70.0,
        temperature_max: float = 40.0,
    ) -> None:
        """Configure irrigation thresholds"""
        self.config["soil_moisture_min"] = soil_moisture_min
        self.config["soil_moisture_max"] = soil_moisture_max
        self.config["temperature_max"] = temperature_max

    def evaluate_conditions(self, sensor_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate if irrigation should be triggered"""
        soil_moisture = sensor_data.get("soil_moisture", 50)
        temperature = sensor_data.get("temperature", 25)

        threshold_min = self.config.get("soil_moisture_min", 30)
        threshold_max = self.config.get("soil_moisture_max", 70)
        temp_max = self.config.get("temperature_max", 40)

        should_irrigate = False
        reasons = []
        urgency = "normal"

        if soil_moisture < threshold_min:
            should_irrigate = True
            reasons.append(f"Soil moisture ({soil_moisture}%) below threshold ({threshold_min}%)")
            if soil_moisture < threshold_min * 0.7:
                urgency = "high"

        if temperature > temp_max and soil_moisture < 50:
            should_irrigate = True
            reasons.append(f"High temperature ({temperature}C) with low moisture")
            urgency = "high"

        return {
            "should_irrigate": should_irrigate,
            "urgency": urgency,
            "reasons": reasons,
            "current_conditions": {
                "soil_moisture": soil_moisture,
                "temperature": temperature,
            },
        }

    async def trigger_irrigation(self, zone_id: str, amount_mm: float, evaluation: dict[str, Any]) -> dict[str, Any]:
        """Trigger automatic irrigation"""
        if not self._enabled:
            return {
                "success": False,
                "reason": "auto_irrigation_disabled",
            }

        trigger = {
            "trigger_id": str(uuid.uuid4()),
            "zone_id": zone_id,
            "amount_mm": amount_mm,
            "urgency": evaluation.get("urgency", "normal"),
            "reasons": evaluation.get("reasons", []),
            "triggered_at": datetime.now(UTC).isoformat(),
            "status": "triggered",
        }

        self._triggers.append(trigger)

        return {
            "success": True,
            "trigger": trigger,
        }

    def get_trigger_history(self) -> list[dict[str, Any]]:
        """Get history of auto-irrigation triggers"""
        return list(self._triggers)

    def enable(self) -> None:
        """Enable auto-irrigation"""
        self._enabled = True

    def disable(self) -> None:
        """Disable auto-irrigation"""
        self._enabled = False


# ==============================================================================
# Test Classes
# ==============================================================================


class TestDataCleaning:
    """Tests for data cleaning functionality"""

    @pytest.fixture
    def cleaner(self) -> DataCleaner:
        return DataCleaner()

    def test_clean_valid_readings(self, cleaner: DataCleaner, sample_sensor_readings: list[dict[str, Any]]):
        """Test cleaning valid sensor readings"""
        result = cleaner.clean(sample_sensor_readings)

        assert len(result["cleaned"]) == len(sample_sensor_readings)
        assert len(result["rejected"]) == 0
        assert result["stats"]["quality_score"] == 1.0

    def test_clean_removes_out_of_range_high(self, cleaner: DataCleaner):
        """Test cleaning removes values above maximum range"""
        readings = [
            {
                "device_id": "test",
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 150.0,  # Invalid: > 100%
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

        result = cleaner.clean(readings)

        assert len(result["cleaned"]) == 0
        assert len(result["rejected"]) == 1
        assert "out_of_range" in result["rejected"][0]["reason"]

    def test_clean_removes_out_of_range_low(self, cleaner: DataCleaner):
        """Test cleaning removes values below minimum range"""
        readings = [
            {
                "device_id": "test",
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": -10.0,  # Invalid: < 0%
                "timestamp": datetime.now(UTC).isoformat(),
            }
        ]

        result = cleaner.clean(readings)

        assert len(result["cleaned"]) == 0
        assert len(result["rejected"]) == 1

    def test_clean_interpolates_null_values(self, cleaner: DataCleaner):
        """Test cleaning interpolates null values from surrounding data"""
        device_id = "test-device"
        readings = [
            {
                "device_id": device_id,
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 40.0,
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "device_id": device_id,
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": None,  # Missing value
                "timestamp": "2024-01-01T10:05:00Z",
            },
            {
                "device_id": device_id,
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 50.0,
                "timestamp": "2024-01-01T10:10:00Z",
            },
        ]

        result = cleaner.clean(readings)

        assert len(result["cleaned"]) == 2
        assert len(result["interpolated"]) == 1
        # Interpolated value should be average of 40 and 50 = 45
        assert result["interpolated"][0]["value"] == 45.0
        assert result["interpolated"][0]["interpolated"] is True

    def test_clean_handles_anomalous_readings(
        self, cleaner: DataCleaner, sample_anomalous_readings: list[dict[str, Any]]
    ):
        """Test cleaning handles various anomalous data"""
        result = cleaner.clean(sample_anomalous_readings)

        # Should have some valid, some rejected
        assert result["stats"]["total"] == 6
        assert result["stats"]["rejected"] > 0
        assert result["stats"]["quality_score"] < 1.0

    def test_detect_spikes(self, cleaner: DataCleaner):
        """Test spike detection in sensor data"""
        readings = [
            {
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 45.0,
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 44.0,  # Normal variation
                "timestamp": "2024-01-01T10:05:00Z",
            },
            {
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 95.0,  # Spike!
                "timestamp": "2024-01-01T10:10:00Z",
            },
            {
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 46.0,  # Back to normal
                "timestamp": "2024-01-01T10:15:00Z",
            },
        ]

        spikes = cleaner.detect_spikes(readings, threshold_percent=50.0)

        assert len(spikes) >= 1
        # The spike from 44 to 95 should be detected
        spike_values = [s["reading"]["value"] for s in spikes]
        assert 95.0 in spike_values


class TestLocalInference:
    """Tests for local edge inference"""

    @pytest.fixture
    def mock_model(self, mock_edge_model) -> MagicMock:
        return mock_edge_model

    @pytest.fixture
    def inference_engine(self, mock_model: MagicMock) -> EdgeInferenceEngine:
        return EdgeInferenceEngine(models={"irrigation-edge-v1.2": mock_model})

    @pytest.mark.asyncio
    async def test_run_inference_success(self, inference_engine: EdgeInferenceEngine):
        """Test successful local inference execution"""
        input_data = {
            "soil_moisture": 35.0,
            "temperature": 32.0,
            "humidity": 45.0,
            "et0": 6.2,
        }

        result = await inference_engine.run_inference("irrigation-edge-v1.2", input_data)

        assert "inference_id" in result
        assert result["model_id"] == "irrigation-edge-v1.2"
        assert result["prediction"] == "irrigate"
        assert result["confidence"] == 0.92
        assert "latency_ms" in result

    @pytest.mark.asyncio
    async def test_run_inference_model_not_found(self, inference_engine: EdgeInferenceEngine):
        """Test inference fails for unknown model"""
        with pytest.raises(ValueError, match="Model not found"):
            await inference_engine.run_inference("unknown-model", {})

    @pytest.mark.asyncio
    async def test_batch_inference(self, inference_engine: EdgeInferenceEngine):
        """Test batch inference execution"""
        inputs = [
            {"soil_moisture": 35.0, "temperature": 30.0},
            {"soil_moisture": 55.0, "temperature": 28.0},
            {"soil_moisture": 25.0, "temperature": 35.0},
        ]

        result = await inference_engine.run_batch_inference("irrigation-edge-v1.2", inputs)

        assert "batch_id" in result
        assert len(result["results"]) == 3
        assert "total_latency_ms" in result
        assert "avg_latency_ms" in result


class TestOfflineAutonomy:
    """Tests for offline autonomy capabilities"""

    @pytest.fixture
    def offline_manager(self) -> OfflineManager:
        return OfflineManager(buffer_size=1000)

    def test_detect_offline_mode(self, offline_manager: OfflineManager):
        """Test detecting offline mode"""
        assert offline_manager.is_offline() is False

        offline_manager.set_cloud_status(False)

        assert offline_manager.is_offline() is True

    def test_buffer_data_when_offline(self, offline_manager: OfflineManager):
        """Test buffering data when offline"""
        offline_manager.set_cloud_status(False)

        data = {
            "device_id": "test-device",
            "readings": [{"sensor": "moisture", "value": 45.0}],
        }

        result = offline_manager.buffer_data(data)

        assert result["buffered"] is True
        assert result["buffer_size"] == 1
        assert result["sync_status"] == SyncStatus.OFFLINE.value

    def test_buffer_respects_size_limit(self, offline_manager: OfflineManager):
        """Test buffer respects maximum size"""
        offline_manager._buffer_size = 5

        for i in range(10):
            offline_manager.buffer_data({"index": i})

        assert offline_manager.get_buffer_size() == 5

    @pytest.mark.asyncio
    async def test_sync_to_cloud_when_available(self, offline_manager: OfflineManager):
        """Test syncing buffered data when cloud available"""
        # Buffer some data
        for i in range(100):
            offline_manager.buffer_data({"index": i})

        assert offline_manager.get_buffer_size() == 100

        result = await offline_manager.sync_to_cloud()

        assert result["success"] is True
        assert result["records_synced"] == 100
        assert offline_manager.get_buffer_size() == 0

    @pytest.mark.asyncio
    async def test_sync_fails_when_cloud_unavailable(self, offline_manager: OfflineManager):
        """Test sync fails when cloud unavailable"""
        offline_manager.set_cloud_status(False)
        offline_manager.buffer_data({"test": "data"})

        result = await offline_manager.sync_to_cloud()

        assert result["success"] is False
        assert result["reason"] == "cloud_unavailable"
        assert offline_manager.get_buffer_size() == 1  # Data still buffered

    def test_offline_duration_tracking(self, offline_manager: OfflineManager):
        """Test tracking offline duration"""
        duration = offline_manager.get_offline_duration()

        # Should be very small (just created)
        assert duration.total_seconds() < 1.0

    def test_get_buffered_data_with_limit(self, offline_manager: OfflineManager):
        """Test getting limited buffered data"""
        for i in range(100):
            offline_manager.buffer_data({"index": i})

        data = offline_manager.get_buffered_data(limit=10)

        assert len(data) == 10

    def test_clear_synced_data(self, offline_manager: OfflineManager):
        """Test clearing synced data from buffer"""
        for i in range(100):
            offline_manager.buffer_data({"index": i})

        offline_manager.clear_synced_data(50)

        assert offline_manager.get_buffer_size() == 50


class TestLatencyRequirements:
    """Tests for 300ms latency requirement"""

    @pytest.fixture
    def fast_model(self) -> MagicMock:
        model = MagicMock()
        model.predict = MagicMock(
            return_value={
                "prediction": "irrigate",
                "confidence": 0.9,
            }
        )
        return model

    @pytest.fixture
    def inference_engine(self, fast_model: MagicMock) -> EdgeInferenceEngine:
        return EdgeInferenceEngine(models={"fast-model": fast_model})

    @pytest.mark.asyncio
    async def test_inference_under_300ms(self, inference_engine: EdgeInferenceEngine):
        """Test that inference completes under 300ms target"""
        input_data = {
            "soil_moisture": 35.0,
            "temperature": 32.0,
        }

        result = await inference_engine.run_inference("fast-model", input_data)

        # Should be well under 300ms for mock model
        assert result["latency_ms"] < 300

    @pytest.mark.asyncio
    async def test_batch_inference_latency(self, inference_engine: EdgeInferenceEngine):
        """Test batch inference maintains reasonable latency"""
        inputs = [{"soil_moisture": i} for i in range(10)]

        result = await inference_engine.run_batch_inference("fast-model", inputs)

        # Average latency should be low
        assert result["avg_latency_ms"] < 100

    @pytest.mark.asyncio
    async def test_average_latency_tracking(self, inference_engine: EdgeInferenceEngine):
        """Test average latency is tracked correctly"""
        for _ in range(10):
            await inference_engine.run_inference("fast-model", {"test": "data"})

        avg_latency = inference_engine.get_average_latency_ms()

        assert avg_latency > 0
        assert avg_latency < 300

    @pytest.mark.asyncio
    async def test_latency_measurement_accuracy(self, inference_engine: EdgeInferenceEngine):
        """Test latency measurement includes actual processing time"""
        result = await inference_engine.run_inference("fast-model", {"test": "data"})

        # Latency should be positive and reasonable
        assert result["latency_ms"] > 0
        assert result["latency_ms"] < 1000


class TestAutoIrrigationTrigger:
    """Tests for automatic irrigation triggering"""

    @pytest.fixture
    def irrigation_controller(self) -> AutoIrrigationController:
        controller = AutoIrrigationController()
        controller.configure_thresholds(
            soil_moisture_min=30.0,
            soil_moisture_max=70.0,
            temperature_max=40.0,
        )
        return controller

    def test_evaluate_low_moisture_triggers(self, irrigation_controller: AutoIrrigationController):
        """Test irrigation triggered when moisture below threshold"""
        sensor_data = {
            "soil_moisture": 25.0,  # Below 30% threshold
            "temperature": 28.0,
        }

        result = irrigation_controller.evaluate_conditions(sensor_data)

        assert result["should_irrigate"] is True
        assert len(result["reasons"]) > 0
        assert "below threshold" in result["reasons"][0].lower()

    def test_evaluate_normal_conditions_no_trigger(self, irrigation_controller: AutoIrrigationController):
        """Test no irrigation for normal conditions"""
        sensor_data = {
            "soil_moisture": 50.0,  # Within normal range
            "temperature": 28.0,
        }

        result = irrigation_controller.evaluate_conditions(sensor_data)

        assert result["should_irrigate"] is False
        assert len(result["reasons"]) == 0

    def test_evaluate_high_temp_with_low_moisture(self, irrigation_controller: AutoIrrigationController):
        """Test irrigation triggered for high temp + low moisture"""
        sensor_data = {
            "soil_moisture": 45.0,  # Below 50% but above min
            "temperature": 42.0,  # Above 40C threshold
        }

        result = irrigation_controller.evaluate_conditions(sensor_data)

        assert result["should_irrigate"] is True
        assert result["urgency"] == "high"

    def test_evaluate_urgency_levels(self, irrigation_controller: AutoIrrigationController):
        """Test different urgency levels based on conditions"""
        # Normal urgency (just below threshold)
        result_normal = irrigation_controller.evaluate_conditions(
            {
                "soil_moisture": 28.0,
                "temperature": 25.0,
            }
        )
        assert result_normal["urgency"] == "normal"

        # High urgency (critically low moisture)
        result_high = irrigation_controller.evaluate_conditions(
            {
                "soil_moisture": 15.0,  # < 30 * 0.7 = 21
                "temperature": 25.0,
            }
        )
        assert result_high["urgency"] == "high"

    @pytest.mark.asyncio
    async def test_trigger_irrigation_success(self, irrigation_controller: AutoIrrigationController):
        """Test successful irrigation trigger"""
        evaluation = irrigation_controller.evaluate_conditions(
            {
                "soil_moisture": 25.0,
                "temperature": 30.0,
            }
        )

        result = await irrigation_controller.trigger_irrigation(
            zone_id="zone-001",
            amount_mm=15.0,
            evaluation=evaluation,
        )

        assert result["success"] is True
        assert "trigger" in result
        assert result["trigger"]["zone_id"] == "zone-001"
        assert result["trigger"]["amount_mm"] == 15.0
        assert result["trigger"]["status"] == "triggered"

    @pytest.mark.asyncio
    async def test_trigger_irrigation_when_disabled(self, irrigation_controller: AutoIrrigationController):
        """Test irrigation trigger fails when disabled"""
        irrigation_controller.disable()

        result = await irrigation_controller.trigger_irrigation(
            zone_id="zone-001",
            amount_mm=15.0,
            evaluation={"urgency": "high", "reasons": ["test"]},
        )

        assert result["success"] is False
        assert result["reason"] == "auto_irrigation_disabled"

    def test_trigger_history(self, irrigation_controller: AutoIrrigationController):
        """Test trigger history is maintained"""
        import asyncio

        async def trigger_multiple():
            for i in range(3):
                await irrigation_controller.trigger_irrigation(
                    zone_id=f"zone-{i}",
                    amount_mm=15.0 + i,
                    evaluation={"urgency": "normal", "reasons": [f"test {i}"]},
                )

        asyncio.get_event_loop().run_until_complete(trigger_multiple())

        history = irrigation_controller.get_trigger_history()
        assert len(history) == 3

    def test_enable_disable_toggle(self, irrigation_controller: AutoIrrigationController):
        """Test enabling and disabling auto-irrigation"""
        irrigation_controller.disable()
        assert irrigation_controller._enabled is False

        irrigation_controller.enable()
        assert irrigation_controller._enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
