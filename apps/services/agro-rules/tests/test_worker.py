"""
Tests for Agro Rules Worker - event-driven task generation from NDVI/Weather events
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.worker import AgroRulesWorker


def _make_msg(data: dict) -> MagicMock:
    """Create a mock NATS message"""
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    return msg


class TestAgroRulesWorkerInit:
    """Tests for worker initialization"""

    def test_worker_initial_state(self):
        """Test worker starts with correct initial state"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            assert worker.nc is None
            assert worker._running is False
            assert worker._recent_ndvi == {}
            assert worker._recent_weather == {}
            assert worker._processed_events == set()


class TestHandleNdviComputed:
    """Tests for NDVI computed event handler"""

    @pytest.mark.asyncio
    async def test_ndvi_severe_drop_creates_task(self):
        """Test severe NDVI drop creates urgent task"""
        with patch("src.worker.FieldOpsClient") as MockClient:
            mock_fieldops = AsyncMock()
            MockClient.return_value = mock_fieldops

            worker = AgroRulesWorker()
            worker.fieldops = mock_fieldops

            msg = _make_msg({
                "event_id": "evt-1",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "ndvi_mean": 0.5,
                    "ndvi_trend_7d": -0.20,
                },
            })

            await worker._handle_ndvi_computed(msg)

            mock_fieldops.create_task.assert_called_once()
            call_kwargs = mock_fieldops.create_task.call_args.kwargs
            assert call_kwargs["priority"] == "urgent"
            assert call_kwargs["tenant_id"] == "t1"
            assert call_kwargs["field_id"] == "field-1"

    @pytest.mark.asyncio
    async def test_ndvi_deduplication(self):
        """Test duplicate events are ignored"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-dup",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"ndvi_mean": 0.1, "ndvi_trend_7d": -0.20},
            })

            await worker._handle_ndvi_computed(msg)
            await worker._handle_ndvi_computed(msg)

            # Should only create task once
            assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_ndvi_healthy_no_task(self):
        """Test healthy NDVI does not create task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-healthy",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"ndvi_mean": 0.7, "ndvi_trend_7d": 0.06},
            })

            await worker._handle_ndvi_computed(msg)
            worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_ndvi_combined_with_weather(self):
        """Test combined NDVI+weather rule triggers when weather data is cached"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            # Pre-populate weather data
            worker._recent_weather["field-1"] = {
                "temp_c": 40,
                "humidity_pct": 30,
            }

            msg = _make_msg({
                "event_id": "evt-combined",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"ndvi_mean": 0.5, "ndvi_trend_7d": -0.10},
            })

            await worker._handle_ndvi_computed(msg)

            # Should have created tasks: one from ndvi rule + one from combined rule
            assert worker.fieldops.create_task.call_count == 2

    @pytest.mark.asyncio
    async def test_ndvi_stores_recent_data(self):
        """Test NDVI data is stored for combined rule evaluation"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-store",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"ndvi_mean": 0.6, "ndvi_trend_7d": 0.02},
            })

            await worker._handle_ndvi_computed(msg)
            assert "field-1" in worker._recent_ndvi

    @pytest.mark.asyncio
    async def test_ndvi_handler_error_doesnt_crash(self):
        """Test handler recovers from JSON decode error"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            bad_msg = MagicMock()
            bad_msg.data = b"not-json"

            # Should not raise
            await worker._handle_ndvi_computed(bad_msg)


class TestHandleNdviAnomaly:
    """Tests for NDVI anomaly event handler"""

    @pytest.mark.asyncio
    async def test_high_severity_anomaly_creates_task(self):
        """Test high severity anomaly creates high-priority inspection"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-anomaly-1",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-1",
                "payload": {
                    "anomaly_type": "sudden_drop",
                    "severity": "high",
                    "z_score": -2.5,
                },
            })

            await worker._handle_ndvi_anomaly(msg)

            worker.fieldops.create_task.assert_called_once()
            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["priority"] == "high"
            assert call_kwargs["task_type"] == "inspection"

    @pytest.mark.asyncio
    async def test_medium_severity_anomaly_creates_task(self):
        """Test medium severity anomaly creates medium-priority task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-anomaly-2",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {
                    "anomaly_type": "gradual_decline",
                    "severity": "medium",
                    "z_score": -1.5,
                },
            })

            await worker._handle_ndvi_anomaly(msg)

            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_low_severity_anomaly_no_task(self):
        """Test low severity anomaly does not create task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-anomaly-low",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {
                    "anomaly_type": "minor",
                    "severity": "low",
                    "z_score": -0.5,
                },
            })

            await worker._handle_ndvi_anomaly(msg)
            worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_anomaly_deduplication(self):
        """Test duplicate anomaly events are ignored"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-dup-anomaly",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"anomaly_type": "x", "severity": "high", "z_score": -2.0},
            })

            await worker._handle_ndvi_anomaly(msg)
            await worker._handle_ndvi_anomaly(msg)
            assert worker.fieldops.create_task.call_count == 1


class TestHandleWeatherAlert:
    """Tests for weather alert event handler"""

    @pytest.mark.asyncio
    async def test_weather_alert_creates_task(self):
        """Test weather alert creates appropriate task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-weather-1",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-w1",
                "payload": {
                    "alert_type": "heat_stress",
                    "severity": "critical",
                    "temp_c": 45,
                    "humidity_pct": 15,
                },
            })

            await worker._handle_weather_alert(msg)

            worker.fieldops.create_task.assert_called_once()
            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["priority"] == "urgent"

    @pytest.mark.asyncio
    async def test_weather_stores_recent_data(self):
        """Test weather data is stored for combined rules"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-weather-store",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {
                    "alert_type": "heat_stress",
                    "severity": "low",
                    "temp_c": 30,
                    "humidity_pct": 50,
                },
            })

            await worker._handle_weather_alert(msg)
            assert "field-1" in worker._recent_weather
            assert worker._recent_weather["field-1"]["temp_c"] == 30

    @pytest.mark.asyncio
    async def test_weather_low_severity_no_task(self):
        """Test low severity weather alert creates no task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-weather-low",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {
                    "alert_type": "heat_stress",
                    "severity": "low",
                },
            })

            await worker._handle_weather_alert(msg)
            worker.fieldops.create_task.assert_not_called()


class TestHandleIrrigationAdjustment:
    """Tests for irrigation adjustment event handler"""

    @pytest.mark.asyncio
    async def test_high_adjustment_creates_task(self):
        """Test high irrigation adjustment creates task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-irr-1",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "correlation_id": "corr-i1",
                "payload": {"adjustment_factor": 1.5},
            })

            await worker._handle_irrigation_adjustment(msg)
            worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_low_adjustment_creates_task(self):
        """Test low irrigation adjustment creates task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-irr-2",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"adjustment_factor": 0.5},
            })

            await worker._handle_irrigation_adjustment(msg)
            worker.fieldops.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_normal_adjustment_no_task(self):
        """Test normal irrigation adjustment creates no task"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            msg = _make_msg({
                "event_id": "evt-irr-normal",
                "tenant_id": "t1",
                "aggregate_id": "field-1",
                "payload": {"adjustment_factor": 1.0},
            })

            await worker._handle_irrigation_adjustment(msg)
            worker.fieldops.create_task.assert_not_called()


class TestCreateTask:
    """Tests for internal _create_task method"""

    @pytest.mark.asyncio
    async def test_create_task_passes_rule_data(self):
        """Test _create_task passes rule data to fieldops client"""
        from src.rules import TaskRule

        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()

            rule = TaskRule(
                title_ar="عنوان",
                title_en="Title",
                description_ar="وصف",
                description_en="Description",
                task_type="inspection",
                priority="high",
                urgency_hours=12,
            )

            await worker._create_task("t1", "f1", rule, "corr-1")

            call_kwargs = worker.fieldops.create_task.call_args.kwargs
            assert call_kwargs["title"] == "عنوان"
            assert call_kwargs["description"] == "وصف"
            assert call_kwargs["priority"] == "high"
            assert call_kwargs["task_type"] == "inspection"
            assert call_kwargs["due_hours"] == 12
            assert call_kwargs["source"] == "agro_rules"
            assert call_kwargs["metadata"]["title_en"] == "Title"
            assert call_kwargs["metadata"]["description_en"] == "Description"

    @pytest.mark.asyncio
    async def test_create_task_handles_error(self):
        """Test _create_task handles fieldops client errors"""
        from src.rules import TaskRule

        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.fieldops = AsyncMock()
            worker.fieldops.create_task = AsyncMock(side_effect=RuntimeError("fail"))

            rule = TaskRule(
                title_ar="t", title_en="t",
                description_ar="d", description_en="d",
                task_type="x", priority="low", urgency_hours=24,
            )

            # Should not raise
            await worker._create_task("t1", "f1", rule, "c1")


class TestCleanupProcessedEvents:
    """Tests for event deduplication cleanup"""

    def test_cleanup_when_under_limit(self):
        """Test cleanup does nothing when under 10000 events"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker._processed_events = {f"evt-{i}" for i in range(100)}
            worker._cleanup_processed_events()
            assert len(worker._processed_events) == 100

    def test_cleanup_when_over_limit(self):
        """Test cleanup trims to 5000 events when over 10000"""
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker._processed_events = {f"evt-{i}" for i in range(10001)}
            worker._cleanup_processed_events()
            assert len(worker._processed_events) == 5000


class TestWorkerStartStop:
    """Tests for worker lifecycle"""

    @pytest.mark.asyncio
    async def test_stop_closes_connections(self):
        """Test stop closes NATS and fieldops connections"""
        with patch("src.worker.FieldOpsClient"):
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
        with patch("src.worker.FieldOpsClient"):
            worker = AgroRulesWorker()
            worker.nc = None
            worker.fieldops = AsyncMock()

            await worker.stop()
            assert worker._running is False
