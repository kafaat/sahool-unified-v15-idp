"""
Tests for IoT Rules Worker - sensor event processing and task creation
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.iot_worker import IoTRulesWorker


def _make_msg(data: dict) -> MagicMock:
    """Create a mock NATS message"""
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    return msg
class TestIoTRulesWorkerInit:
    """Tests for IoT worker initialization"""

    def test_initial_state(self):
        """Test worker starts with correct initial state"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            assert worker.nc is None
            assert worker._running is False
            assert worker._recent_readings == {}
            assert worker._recent_tasks == {}
            assert worker._cooldown_minutes == 30
class TestHandleSensorReading:
    """Tests for sensor reading handler"""

    @pytest.mark.asyncio
    async def test_critical_moisture_creates_urgent_task(self):
        """Test critical low moisture creates urgent irrigation task"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "soil_moisture",
                    "value": 5,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)

            worker.fieldops.create_task.assert_called_once()
            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["priority"] == "urgent"
            assert call_kwargs["source"] == "iot_rules"

    @pytest.mark.asyncio
    async def test_normal_reading_no_task(self):
        """Test normal soil moisture creates no task"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "soil_moisture",
                    "value": 50,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)
            worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_tenant_id_skips(self):
        """Test messages without tenant_id are skipped"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "soil_moisture",
                    "value": 5,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)
            worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_required_fields_skips(self):
        """Test messages missing field_id/sensor_type/value are skipped"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            # Missing sensor_type
            msg = _make_msg({
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "value": 5,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)
            worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_direct_payload_format(self):
        """Test handling messages without envelope wrapper"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "tenant_id": "t1",
                "field_id": "f1",
                "sensor_type": "soil_moisture",
                "value": 5,
                "device_id": "dev-1",
            })

            await worker._handle_sensor_reading(msg)
            worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_error_doesnt_crash(self):
        """Test handler recovers from bad data"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            bad_msg = MagicMock()
            bad_msg.data = b"not-json"

            await worker._handle_sensor_reading(bad_msg)

    @pytest.mark.asyncio
    async def test_stores_recent_reading(self):
        """Test sensor readings are stored for combined evaluation"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "tenant_id": "t1",
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "soil_moisture",
                    "value": 50,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)
            assert "f1" in worker._recent_readings
            assert len(worker._recent_readings["f1"]) == 1

    @pytest.mark.asyncio
    async def test_correlation_id_passed_through(self):
        """Test correlation_id is passed to task creation"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "tenant_id": "t1",
                "correlation_id": "corr-xyz",
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "water_flow",
                    "value": 0,
                    "device_id": "dev-1",
                },
            })

            await worker._handle_sensor_reading(msg)
            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["correlation_id"] == "corr-xyz"
class TestStoreReading:
    """Tests for _store_reading"""

    def test_store_new_field(self):
        """Test storing reading for new field"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker._store_reading("f1", "soil_moisture", 40.0, "dev-1", "t1")
            assert len(worker._recent_readings["f1"]) == 1

    def test_store_limits_to_ten(self):
        """Test readings are capped at 10 per field"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            for i in range(15):
                worker._store_reading("f1", "soil_moisture", float(i), "dev-1", "t1")
            assert len(worker._recent_readings["f1"]) == 10
class TestCreateTaskFromRecommendation:
    """Tests for task creation with cooldown"""

    @pytest.mark.asyncio
    async def test_creates_task_and_records_timestamp(self):
        """Test task creation records timestamp for cooldown"""
        from src.iot_rules import TaskRecommendation

        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            rec = TaskRecommendation(
                title_ar="تست",
                title_en="Test",
                description_ar="وصف",
                description_en="Desc",
                task_type="irrigation",
                priority="high",
                urgency_hours=6,
            )

            await worker._create_task_from_recommendation(
                tenant_id="t1",
                field_id="f1",
                recommendation=rec,
                device_id="dev-1",
            )

            worker.fieldops.create_task.assert_called_once()
            assert "f1:irrigation:high" in worker._recent_tasks

    @pytest.mark.asyncio
    async def test_cooldown_prevents_duplicate(self):
        """Test cooldown prevents duplicate task creation"""
        from src.iot_rules import TaskRecommendation

        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            rec = TaskRecommendation(
                title_ar="تست",
                title_en="Test",
                description_ar="وصف",
                description_en="Desc",
                task_type="irrigation",
                priority="high",
                urgency_hours=6,
            )

            await worker._create_task_from_recommendation("t1", "f1", rec)
            await worker._create_task_from_recommendation("t1", "f1", rec)

            # Second call should be skipped due to cooldown
            assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_cooldown_expires(self):
        """Test task can be created after cooldown expires"""
        from src.iot_rules import TaskRecommendation

        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            rec = TaskRecommendation(
                title_ar="تست",
                title_en="Test",
                description_ar="وصف",
                description_en="Desc",
                task_type="irrigation",
                priority="high",
                urgency_hours=6,
            )

            # First creation
            await worker._create_task_from_recommendation("t1", "f1", rec)

            # Simulate cooldown expiry
            task_key = "f1:irrigation:high"
            worker._recent_tasks[task_key] = datetime.now(UTC) - timedelta(minutes=31)

            # Second creation should succeed
            await worker._create_task_from_recommendation("t1", "f1", rec)
            assert worker.fieldops.create_task.call_count == 2

    @pytest.mark.asyncio
    async def test_metadata_includes_device_id(self):
        """Test metadata includes device_id when provided"""
        from src.iot_rules import TaskRecommendation

        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()

            rec = TaskRecommendation(
                title_ar="تست",
                title_en="Test",
                description_ar="وصف",
                description_en="Desc",
                task_type="irrigation",
                priority="high",
                urgency_hours=6,
            )

            await worker._create_task_from_recommendation(
                "t1", "f1", rec, device_id="sensor-42",
            )

            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["metadata"]["device_id"] == "sensor-42"
            assert call_kwargs["metadata"]["title_en"] == "Test"

    @pytest.mark.asyncio
    async def test_create_task_handles_fieldops_error(self):
        """Test handles fieldops client errors gracefully"""
        from src.iot_rules import TaskRecommendation

        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.fieldops = AsyncMock()
            worker.fieldops.create_task = AsyncMock(side_effect=RuntimeError("fail"))

            rec = TaskRecommendation(
                title_ar="تست", title_en="Test",
                description_ar="وصف", description_en="Desc",
                task_type="x", priority="low", urgency_hours=24,
            )

            # Should not raise
            await worker._create_task_from_recommendation("t1", "f1", rec)
class TestIoTWorkerLifecycle:
    """Tests for worker start/stop"""

    @pytest.mark.asyncio
    async def test_stop_closes_connections(self):
        """Test stop closes NATS and fieldops"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.nc = AsyncMock()
            worker.fieldops = AsyncMock()
            worker._running = True

            await worker.stop()
            assert worker._running is False
            worker.nc.close.assert_called_once()
            worker.fieldops.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_without_nats(self):
        """Test stop when NATS not connected"""
        with patch("src.iot_worker.FieldOpsClient"):
            worker = IoTRulesWorker()
            worker.nc = None
            worker.fieldops = AsyncMock()

            await worker.stop()
            assert worker._running is False
