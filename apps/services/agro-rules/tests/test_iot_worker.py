"""
Tests for IoTRulesWorker
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.iot_rules import TaskRecommendation
    from src.iot_worker import IoTRulesWorker
except ImportError:
    pytest.skip("agro-rules dependencies not installed", allow_module_level=True)


class TestIoTRulesWorkerInit:
    """Test IoTRulesWorker initialization"""

    def test_init_defaults(self):
        """Test worker initializes with correct defaults"""
        worker = IoTRulesWorker()
        assert worker.nc is None
        assert worker._running is False
        assert worker._recent_readings == {}
        assert worker._recent_tasks == {}
        assert worker._cooldown_minutes == 30


class TestIoTRulesWorkerHandleSensorReading:
    """Test sensor reading handling"""

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_triggers_rule(self):
        """Test sensor reading that triggers a rule creates task"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "tenant-1",
                "correlation_id": "corr-1",
                "payload": {
                    "field_id": "field-1",
                    "sensor_type": "soil_moisture",
                    "value": 5,
                    "device_id": "dev-1",
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_no_trigger(self):
        """Test sensor reading with normal values doesn't create task"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "tenant-1",
                "payload": {
                    "field_id": "field-1",
                    "sensor_type": "soil_moisture",
                    "value": 50,
                    "device_id": "dev-1",
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_direct_payload(self):
        """Test handling direct payload (not wrapped in envelope)"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "tenant-1",
                "field_id": "field-1",
                "sensor_type": "soil_moisture",
                "value": 5,
                "device_id": "dev-1",
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_missing_tenant(self):
        """Test reading without tenant_id is skipped"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "payload": {
                    "field_id": "field-1",
                    "sensor_type": "soil_moisture",
                    "value": 5,
                    "device_id": "dev-1",
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_missing_fields(self):
        """Test reading with missing required fields is skipped"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "tenant-1",
                "payload": {
                    "field_id": "field-1",
                    # Missing sensor_type and value
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_sensor_reading_error_handled(self):
        """Test error in handler doesn't crash"""
        worker = IoTRulesWorker()

        msg = MagicMock()
        msg.data = b"invalid json"

        await worker._handle_sensor_reading(msg)

    @pytest.mark.asyncio
    async def test_handle_sensor_stores_reading(self):
        """Test sensor readings are stored for combined evaluation"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "tenant-1",
                "payload": {
                    "field_id": "field-1",
                    "sensor_type": "air_temperature",
                    "value": 25,
                    "device_id": "dev-1",
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        assert "field-1" in worker._recent_readings
        assert len(worker._recent_readings["field-1"]) == 1
        assert worker._recent_readings["field-1"][0]["sensor_type"] == "air_temperature"

    @pytest.mark.asyncio
    async def test_correlation_id_passed_through(self):
        """Test correlation_id is passed to task creation"""
        worker = IoTRulesWorker()
        worker.fieldops = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "tenant_id": "t1",
                "correlation_id": "corr-xyz",
                "payload": {
                    "field_id": "f1",
                    "sensor_type": "water_flow",
                    "value": 0,
                    "device_id": "dev-1",
                },
            }
        ).encode()

        await worker._handle_sensor_reading(msg)
        if worker.fieldops.create_task.called:
            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["correlation_id"] == "corr-xyz"


class TestIoTRulesWorkerStoreReading:
    """Test reading storage"""

    def test_store_reading_creates_list(self):
        """Test store_reading creates reading list for new field"""
        worker = IoTRulesWorker()
        worker._store_reading("field-1", "soil_moisture", 45, "dev-1", "tenant-1")

        assert "field-1" in worker._recent_readings
        assert len(worker._recent_readings["field-1"]) == 1

    def test_store_reading_appends(self):
        """Test store_reading appends to existing list"""
        worker = IoTRulesWorker()
        worker._store_reading("field-1", "soil_moisture", 45, "dev-1", "tenant-1")
        worker._store_reading("field-1", "air_temperature", 30, "dev-2", "tenant-1")

        assert len(worker._recent_readings["field-1"]) == 2

    def test_store_reading_limits_to_10(self):
        """Test store_reading keeps only last 10 readings"""
        worker = IoTRulesWorker()
        for i in range(15):
            worker._store_reading("field-1", "soil_moisture", i, "dev-1", "tenant-1")

        assert len(worker._recent_readings["field-1"]) == 10
        # Last value should be 14
        assert worker._recent_readings["field-1"][-1]["value"] == 14


class TestIoTRulesWorkerCreateTaskFromRecommendation:
    """Test task creation from recommendation"""

    @pytest.mark.asyncio
    async def test_create_task_with_device_id(self):
        """Test task creation includes device_id in metadata"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
            metadata={"sensor_type": "soil_moisture"},
        )

        await worker._create_task_from_recommendation(
            tenant_id="tenant-1",
            field_id="field-1",
            recommendation=rec,
            device_id="dev-1",
            correlation_id="corr-1",
        )

        worker.fieldops.create_task.assert_called_once()
        call_kwargs = worker.fieldops.create_task.call_args.kwargs
        assert call_kwargs["metadata"]["device_id"] == "dev-1"

    @pytest.mark.asyncio
    async def test_create_task_cooldown(self):
        """Test task not created within cooldown period"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

        # First call should succeed
        await worker._create_task_from_recommendation(
            "tenant-1",
            "field-1",
            rec,
        )
        assert worker.fieldops.create_task.call_count == 1

        # Second call should be skipped (within cooldown)
        await worker._create_task_from_recommendation(
            "tenant-1",
            "field-1",
            rec,
        )
        assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_create_task_after_cooldown_expired(self):
        """Test task created after cooldown expires"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

        # Simulate expired cooldown
        task_key = "field-1:irrigation:high"
        worker._recent_tasks[task_key] = datetime.now(UTC) - timedelta(minutes=31)

        await worker._create_task_from_recommendation(
            "tenant-1",
            "field-1",
            rec,
        )
        assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_create_task_error_handled(self):
        """Test fieldops error in task creation doesn't crash"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(side_effect=Exception("fail"))

        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="irrigation",
            priority="high",
            urgency_hours=6,
        )

        # Should not raise
        await worker._create_task_from_recommendation(
            "tenant-1",
            "field-1",
            rec,
        )

    @pytest.mark.asyncio
    async def test_create_task_without_device_id(self):
        """Test task creation without device_id"""
        worker = IoTRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        rec = TaskRecommendation(
            title_ar="اختبار",
            title_en="Test",
            description_ar="وصف",
            description_en="Description",
            task_type="inspection",
            priority="medium",
            urgency_hours=24,
        )

        await worker._create_task_from_recommendation(
            "tenant-1",
            "field-1",
            rec,
        )

        call_kwargs = worker.fieldops.create_task.call_args.kwargs
        assert "device_id" not in call_kwargs["metadata"]
        assert call_kwargs["metadata"]["title_en"] == "Test"

    @pytest.mark.asyncio
    async def test_metadata_includes_device_id(self):
        """Test metadata includes device_id when provided"""
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
            "t1",
            "f1",
            rec,
            device_id="sensor-42",
        )

        call_kwargs = worker.fieldops.create_task.call_args.kwargs
        assert call_kwargs["metadata"]["device_id"] == "sensor-42"
        assert call_kwargs["metadata"]["title_en"] == "Test"


class TestIoTWorkerLifecycle:
    """Tests for worker start/stop"""

    @pytest.mark.asyncio
    async def test_stop_closes_connections(self):
        """Test stop closes NATS and fieldops"""
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
        worker = IoTRulesWorker()
        worker.nc = None
        worker.fieldops = AsyncMock()

        await worker.stop()
        assert worker._running is False
