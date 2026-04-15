"""
Tests for AgroRulesWorker
"""

import json

import pytest

try:
    from unittest.mock import AsyncMock, MagicMock, patch

    from src.rules import TaskRule
    from src.worker import AgroRulesWorker
except ImportError:
    pytest.skip("agro-rules dependencies not installed", allow_module_level=True)


def _make_msg(data: dict) -> MagicMock:
    """Create a mock NATS message"""
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    return msg


class TestAgroRulesWorkerInit:
    """Test AgroRulesWorker initialization"""

    def test_init_defaults(self):
        """Test worker initializes with correct defaults"""
        worker = AgroRulesWorker()
        assert worker.nc is None
        assert worker._running is False
        assert worker._recent_ndvi == {}
        assert worker._recent_weather == {}
        assert worker._processed_events == set()


class TestAgroRulesWorkerHandleNdviComputed:
    """Test NDVI computed event handling"""

    @pytest.mark.asyncio
    async def test_handle_ndvi_computed_creates_task(self):
        """Test NDVI event with severe drop creates task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-1",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "ndvi_mean": 0.15,
                    "ndvi_trend_7d": -0.20,
                },
            }
        ).encode()

        await worker._handle_ndvi_computed(msg)
        worker.fieldops.create_task.assert_called_once()
        call_kwargs = worker.fieldops.create_task.call_args.kwargs
        assert call_kwargs["priority"] == "urgent"
        assert call_kwargs["tenant_id"] == "tenant-1"
        assert call_kwargs["field_id"] == "field-1"

    @pytest.mark.asyncio
    async def test_handle_ndvi_computed_deduplication(self):
        """Test duplicate events are skipped"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-dup",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"ndvi_mean": 0.15, "ndvi_trend_7d": -0.20},
            }
        ).encode()

        await worker._handle_ndvi_computed(msg)
        await worker._handle_ndvi_computed(msg)

        # Should only create task once
        assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_handle_ndvi_computed_healthy_no_task(self):
        """Test healthy NDVI does not create task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-2",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"ndvi_mean": 0.7, "ndvi_trend_7d": 0.05},
            }
        ).encode()

        await worker._handle_ndvi_computed(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_ndvi_combined_with_weather(self):
        """Test NDVI event triggers combined rule when weather data exists"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        # Pre-populate weather data
        worker._recent_weather["field-1"] = {
            "alert_type": "heat_stress",
            "severity": "high",
            "temp_c": 40,
            "humidity_pct": 30,
        }

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-3",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"ndvi_mean": 0.3, "ndvi_trend_7d": -0.10},
            }
        ).encode()

        await worker._handle_ndvi_computed(msg)
        # Should create at least one task (NDVI rule) and possibly combined rule
        assert worker.fieldops.create_task.call_count >= 1

    @pytest.mark.asyncio
    async def test_handle_ndvi_computed_error_handled(self):
        """Test error in NDVI handler doesn't crash"""
        worker = AgroRulesWorker()

        msg = MagicMock()
        msg.data = b"invalid json"

        # Should not raise
        await worker._handle_ndvi_computed(msg)

    @pytest.mark.asyncio
    async def test_ndvi_stores_recent_data(self):
        """Test NDVI data is stored for combined rule evaluation"""
        worker = AgroRulesWorker()
        worker.fieldops = AsyncMock()

        msg = _make_msg(
            {
                "event_id": "evt-store",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"ndvi_mean": 0.6, "ndvi_trend_7d": 0.02},
            }
        )

        await worker._handle_ndvi_computed(msg)
        assert "field-1" in worker._recent_ndvi


class TestAgroRulesWorkerHandleNdviAnomaly:
    """Test NDVI anomaly event handling"""

    @pytest.mark.asyncio
    async def test_handle_ndvi_anomaly_high(self):
        """Test high severity anomaly creates task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-a1",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "anomaly_type": "sudden_drop",
                    "severity": "high",
                    "z_score": 3.5,
                },
            }
        ).encode()

        await worker._handle_ndvi_anomaly(msg)
        worker.fieldops.create_task.assert_called_once()
        call_args = worker.fieldops.create_task.call_args
        assert call_args.kwargs["priority"] == "high"
        assert call_args.kwargs["task_type"] == "inspection"

    @pytest.mark.asyncio
    async def test_handle_ndvi_anomaly_medium(self):
        """Test medium severity anomaly creates task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-a2",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "anomaly_type": "gradual_decline",
                    "severity": "medium",
                    "z_score": 2.0,
                },
            }
        ).encode()

        await worker._handle_ndvi_anomaly(msg)
        worker.fieldops.create_task.assert_called_once()
        call_args = worker.fieldops.create_task.call_args
        assert call_args.kwargs["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_handle_ndvi_anomaly_low_no_task(self):
        """Test low severity anomaly does not create task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-a3",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "anomaly_type": "minor",
                    "severity": "low",
                    "z_score": 1.0,
                },
            }
        ).encode()

        await worker._handle_ndvi_anomaly(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_ndvi_anomaly_error_handled(self):
        """Test error in anomaly handler doesn't crash"""
        worker = AgroRulesWorker()

        msg = MagicMock()
        msg.data = b"bad json"

        await worker._handle_ndvi_anomaly(msg)

    @pytest.mark.asyncio
    async def test_anomaly_deduplication(self):
        """Test duplicate anomaly events are ignored"""
        worker = AgroRulesWorker()
        worker.fieldops = AsyncMock()

        msg = _make_msg(
            {
                "event_id": "evt-dup-anomaly",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"anomaly_type": "x", "severity": "high", "z_score": -2.0},
            }
        )

        await worker._handle_ndvi_anomaly(msg)
        await worker._handle_ndvi_anomaly(msg)
        assert worker.fieldops.create_task.call_count == 1


class TestAgroRulesWorkerHandleWeatherAlert:
    """Test weather alert event handling"""

    @pytest.mark.asyncio
    async def test_handle_weather_alert_creates_task(self):
        """Test weather alert creates task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-w1",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "alert_type": "heat_stress",
                    "severity": "critical",
                    "temp_c": 45,
                    "humidity_pct": 20,
                },
            }
        ).encode()

        await worker._handle_weather_alert(msg)
        worker.fieldops.create_task.assert_called_once()
        call_kwargs = worker.fieldops.create_task.call_args.kwargs
        assert call_kwargs["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_handle_weather_alert_stores_weather(self):
        """Test weather data is stored for combined rules"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-w2",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "alert_type": "frost",
                    "severity": "critical",
                    "temp_c": -2,
                    "humidity_pct": 90,
                },
            }
        ).encode()

        await worker._handle_weather_alert(msg)
        assert "field-1" in worker._recent_weather
        assert worker._recent_weather["field-1"]["temp_c"] == -2

    @pytest.mark.asyncio
    async def test_handle_weather_alert_low_no_task(self):
        """Test low severity weather alert doesn't create task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-w3",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"alert_type": "heat_stress", "severity": "low"},
            }
        ).encode()

        await worker._handle_weather_alert(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_weather_alert_error_handled(self):
        """Test error in weather handler doesn't crash"""
        worker = AgroRulesWorker()

        msg = MagicMock()
        msg.data = b"invalid"

        await worker._handle_weather_alert(msg)


class TestAgroRulesWorkerHandleIrrigationAdjustment:
    """Test irrigation adjustment event handling"""

    @pytest.mark.asyncio
    async def test_handle_irrigation_adjustment_high(self):
        """Test high irrigation adjustment creates task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-i1",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"adjustment_factor": 1.5},
            }
        ).encode()

        await worker._handle_irrigation_adjustment(msg)
        worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_irrigation_adjustment_low(self):
        """Test low irrigation adjustment creates task"""
        worker = AgroRulesWorker()
        worker.fieldops = AsyncMock()

        msg = _make_msg(
            {
                "event_id": "evt-irr-2",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"adjustment_factor": 0.5},
            }
        )

        await worker._handle_irrigation_adjustment(msg)
        worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_irrigation_adjustment_normal_no_task(self):
        """Test normal irrigation adjustment doesn't create task"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "evt-i2",
                "tenant_id": "tenant-1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {"adjustment_factor": 1.0},
            }
        ).encode()

        await worker._handle_irrigation_adjustment(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_irrigation_adjustment_error_handled(self):
        """Test error in irrigation handler doesn't crash"""
        worker = AgroRulesWorker()

        msg = MagicMock()
        msg.data = b"bad"

        await worker._handle_irrigation_adjustment(msg)


class TestAgroRulesWorkerCreateTask:
    """Test _create_task method"""

    @pytest.mark.asyncio
    async def test_create_task_calls_fieldops(self):
        """Test _create_task correctly calls fieldops client"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        rule = TaskRule(
            title_ar="عنوان",
            title_en="Title",
            description_ar="وصف",
            description_en="Description",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

        await worker._create_task("tenant-1", "field-1", rule, "corr-1")

        worker.fieldops.create_task.assert_called_once_with(
            tenant_id="tenant-1",
            field_id="field-1",
            title="عنوان",
            description="وصف",
            priority="high",
            correlation_id="corr-1",
            task_type="inspection",
            due_hours=24,
            source="agro_rules",
            metadata={
                "title_en": "Title",
                "description_en": "Description",
            },
        )

    @pytest.mark.asyncio
    async def test_create_task_handles_error(self):
        """Test _create_task handles fieldops errors"""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(side_effect=Exception("fail"))

        rule = TaskRule(
            title_ar="عنوان",
            title_en="Title",
            description_ar="وصف",
            description_en="Description",
            task_type="inspection",
            priority="high",
            urgency_hours=24,
        )

        # Should not raise
        await worker._create_task("tenant-1", "field-1", rule, "corr-1")


class TestAgroRulesWorkerCleanup:
    """Test event cleanup"""

    def test_cleanup_when_under_limit(self):
        """Test cleanup doesn't run when under limit"""
        worker = AgroRulesWorker()
        worker._processed_events = {"evt-1", "evt-2", "evt-3"}

        worker._cleanup_processed_events()
        assert len(worker._processed_events) == 3

    def test_cleanup_when_over_limit(self):
        """Test cleanup reduces set when over limit"""
        worker = AgroRulesWorker()
        worker._processed_events = {f"evt-{i}" for i in range(10001)}

        worker._cleanup_processed_events()
        assert len(worker._processed_events) == 5000


class TestWorkerStartStop:
    """Tests for worker lifecycle"""

    @pytest.mark.asyncio
    async def test_stop_closes_connections(self):
        """Test stop closes NATS and fieldops connections"""
        worker = AgroRulesWorker()
        worker.nc = AsyncMock()
        worker.fieldops = AsyncMock()
        worker._running = True

        await worker.stop()

        assert worker._running is False
        worker.nc.close.assert_called_once()
        worker.fieldops.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_without_nats(self):
        """Test stop handles case when NATS is not connected"""
        worker = AgroRulesWorker()
        worker.nc = None
        worker.fieldops = AsyncMock()

        await worker.stop()
        assert worker._running is False
