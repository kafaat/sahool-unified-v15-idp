"""
SAHOOL Edge-Cloud Cooperative System Tests
اختبارات النظام التعاوني للحوسبة الحافة-السحابة

Tests for the cooperative system including:
- Full pipeline execution
- Edge-cloud synchronization
- Fallback to edge when cloud unavailable
- System metrics and monitoring

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .conftest import (
    DataQuality,
    InferenceMode,
    SensorType,
    SyncStatus,
)


# ==============================================================================
# Cooperative System Components (Test Target Mocks)
# ==============================================================================


class CooperativeOrchestrator:
    """Orchestrates edge-cloud cooperative computing"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._mode = InferenceMode.HYBRID.value
        self._edge_status = "online"
        self._cloud_status = "connected"
        self._metrics: dict[str, Any] = {
            "edge_inference_count": 0,
            "cloud_inference_count": 0,
            "sync_count": 0,
            "fallback_count": 0,
        }
        self._sync_history: list[dict[str, Any]] = []

    def set_mode(self, mode: str) -> None:
        """Set inference mode"""
        if mode not in [m.value for m in InferenceMode]:
            raise ValueError(f"Invalid mode: {mode}")
        self._mode = mode

    def set_edge_status(self, status: str) -> None:
        """Set edge status"""
        self._edge_status = status

    def set_cloud_status(self, status: str) -> None:
        """Set cloud status"""
        self._cloud_status = status

    def route_inference(self, task_type: str, latency_required_ms: int) -> dict[str, Any]:
        """Determine where to execute inference"""
        edge_tasks = self.config.get("edge_config", {}).get("primary_tasks", [])
        cloud_tasks = self.config.get("cloud_config", {}).get("primary_tasks", [])
        max_edge_latency = self.config.get("edge_config", {}).get("max_latency_ms", 300)

        # Decision logic
        if self._mode == InferenceMode.EDGE.value:
            return {
                "execution_layer": "edge",
                "reason": "edge_only_mode",
                "fallback_available": False,
            }

        if self._mode == InferenceMode.CLOUD.value:
            if self._cloud_status != "connected":
                return {
                    "execution_layer": "edge",
                    "reason": "cloud_unavailable_fallback",
                    "fallback_available": False,
                }
            return {
                "execution_layer": "cloud",
                "reason": "cloud_only_mode",
                "fallback_available": True,
            }

        # Hybrid mode logic
        if latency_required_ms < max_edge_latency and task_type in edge_tasks:
            return {
                "execution_layer": "edge",
                "reason": "latency_requirement",
                "fallback_available": self._cloud_status == "connected",
            }

        if task_type in cloud_tasks and self._cloud_status == "connected":
            return {
                "execution_layer": "cloud",
                "reason": "task_complexity",
                "fallback_available": self._edge_status == "online",
            }

        # Default to edge
        return {
            "execution_layer": "edge",
            "reason": "default_edge",
            "fallback_available": self._cloud_status == "connected",
        }

    async def execute_pipeline(
        self,
        sensor_data: dict[str, Any],
        task_type: str = "irrigation_decision",
    ) -> dict[str, Any]:
        """Execute full inference pipeline"""
        pipeline_id = str(uuid.uuid4())
        start_time = datetime.now(UTC)

        # Route inference
        routing = self.route_inference(task_type, latency_required_ms=200)
        execution_layer = routing["execution_layer"]

        # Simulate execution
        if execution_layer == "edge":
            self._metrics["edge_inference_count"] += 1
            result = await self._execute_edge_inference(sensor_data)
        else:
            self._metrics["cloud_inference_count"] += 1
            result = await self._execute_cloud_inference(sensor_data)

        end_time = datetime.now(UTC)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        return {
            "pipeline_id": pipeline_id,
            "task_type": task_type,
            "execution_layer": execution_layer,
            "routing_reason": routing["reason"],
            "result": result,
            "latency_ms": latency_ms,
            "timestamp": end_time.isoformat(),
        }

    async def _execute_edge_inference(self, sensor_data: dict[str, Any]) -> dict[str, Any]:
        """Execute inference on edge"""
        await asyncio.sleep(0.05)  # Simulate fast edge inference
        soil_moisture = sensor_data.get("soil_moisture", 50)

        return {
            "decision": "irrigate" if soil_moisture < 35 else "wait",
            "confidence": 0.88,
            "model": "edge-irrigation-v1.2",
        }

    async def _execute_cloud_inference(self, sensor_data: dict[str, Any]) -> dict[str, Any]:
        """Execute inference on cloud"""
        await asyncio.sleep(0.2)  # Simulate slower cloud inference
        soil_moisture = sensor_data.get("soil_moisture", 50)

        return {
            "decision": "irrigate" if soil_moisture < 35 else "wait",
            "confidence": 0.95,
            "model": "cloud-irrigation-v2.0",
            "additional_analysis": {
                "yield_impact": "+5%",
                "water_savings": "12%",
            },
        }

    async def sync_edge_to_cloud(
        self,
        data: list[dict[str, Any]],
        force: bool = False,
    ) -> dict[str, Any]:
        """Sync data from edge to cloud"""
        sync_id = str(uuid.uuid4())

        if self._cloud_status != "connected" and not force:
            return {
                "sync_id": sync_id,
                "success": False,
                "reason": "cloud_unavailable",
                "records_pending": len(data),
            }

        # Simulate sync
        await asyncio.sleep(0.1)

        sync_record = {
            "sync_id": sync_id,
            "success": True,
            "records_synced": len(data),
            "direction": "edge_to_cloud",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._sync_history.append(sync_record)
        self._metrics["sync_count"] += 1

        return sync_record

    async def sync_cloud_to_edge(
        self,
        model_updates: bool = True,
        config_updates: bool = True,
    ) -> dict[str, Any]:
        """Sync updates from cloud to edge"""
        sync_id = str(uuid.uuid4())

        if self._cloud_status != "connected":
            return {
                "sync_id": sync_id,
                "success": False,
                "reason": "cloud_unavailable",
            }

        updates = []
        if model_updates:
            updates.append({"type": "model", "version": "1.3.0"})
        if config_updates:
            updates.append({"type": "config", "updated_at": datetime.now(UTC).isoformat()})

        return {
            "sync_id": sync_id,
            "success": True,
            "updates": updates,
            "direction": "cloud_to_edge",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def handle_fallback(self, original_layer: str, error: str) -> dict[str, Any]:
        """Handle fallback when primary layer fails"""
        self._metrics["fallback_count"] += 1

        if original_layer == "cloud":
            return {
                "fallback_to": "edge",
                "reason": error,
                "degraded_mode": True,
                "capabilities_available": ["basic_inference", "buffered_sync"],
            }
        else:
            return {
                "fallback_to": "buffered",
                "reason": error,
                "degraded_mode": True,
                "capabilities_available": ["data_buffering", "offline_alerts"],
            }

    def get_system_metrics(self) -> dict[str, Any]:
        """Get system metrics"""
        total_inferences = self._metrics["edge_inference_count"] + self._metrics["cloud_inference_count"]

        return {
            "mode": self._mode,
            "edge_status": self._edge_status,
            "cloud_status": self._cloud_status,
            "edge_inference_count": self._metrics["edge_inference_count"],
            "cloud_inference_count": self._metrics["cloud_inference_count"],
            "total_inference_count": total_inferences,
            "sync_count": self._metrics["sync_count"],
            "fallback_count": self._metrics["fallback_count"],
            "edge_inference_ratio": (self._metrics["edge_inference_count"] / max(total_inferences, 1)),
        }


# ==============================================================================
# Test Classes
# ==============================================================================


class TestFullPipeline:
    """Tests for full pipeline execution"""

    @pytest.fixture
    def orchestrator(self, cooperative_system_config: dict[str, Any]) -> CooperativeOrchestrator:
        return CooperativeOrchestrator(cooperative_system_config)

    @pytest.mark.asyncio
    async def test_execute_pipeline_success(
        self,
        orchestrator: CooperativeOrchestrator,
        full_pipeline_data: dict[str, Any],
    ):
        """Test successful full pipeline execution"""
        result = await orchestrator.execute_pipeline(
            sensor_data=full_pipeline_data["sensor_data"],
            task_type="irrigation_decision",
        )

        assert "pipeline_id" in result
        assert result["task_type"] == "irrigation_decision"
        assert result["execution_layer"] in ["edge", "cloud"]
        assert "result" in result
        assert result["latency_ms"] > 0

    @pytest.mark.asyncio
    async def test_pipeline_routes_to_edge_for_latency(self, orchestrator: CooperativeOrchestrator):
        """Test pipeline routes to edge for latency-sensitive tasks"""
        result = await orchestrator.execute_pipeline(
            sensor_data={"soil_moisture": 30},
            task_type="irrigation_decision",
        )

        # Irrigation decisions are edge tasks in config
        assert result["execution_layer"] == "edge"
        assert result["routing_reason"] == "latency_requirement"

    @pytest.mark.asyncio
    async def test_pipeline_routes_to_cloud_for_complex_tasks(self, orchestrator: CooperativeOrchestrator):
        """Test pipeline routes to cloud for complex tasks"""
        result = await orchestrator.execute_pipeline(
            sensor_data={"soil_moisture": 30},
            task_type="pest_detection",
        )

        # Pest detection is a cloud task
        assert result["execution_layer"] == "cloud"
        assert result["routing_reason"] == "task_complexity"

    @pytest.mark.asyncio
    async def test_pipeline_edge_inference_result(self, orchestrator: CooperativeOrchestrator):
        """Test edge inference returns expected result structure"""
        orchestrator.set_mode(InferenceMode.EDGE.value)

        result = await orchestrator.execute_pipeline(
            sensor_data={"soil_moisture": 25},  # Low moisture
        )

        assert result["execution_layer"] == "edge"
        assert result["result"]["decision"] == "irrigate"
        assert "confidence" in result["result"]

    @pytest.mark.asyncio
    async def test_pipeline_cloud_inference_has_additional_analysis(self, orchestrator: CooperativeOrchestrator):
        """Test cloud inference includes additional analysis"""
        orchestrator.set_mode(InferenceMode.CLOUD.value)

        result = await orchestrator.execute_pipeline(
            sensor_data={"soil_moisture": 25},
        )

        assert result["execution_layer"] == "cloud"
        assert "additional_analysis" in result["result"]

    @pytest.mark.asyncio
    async def test_pipeline_multiple_executions(self, orchestrator: CooperativeOrchestrator):
        """Test multiple pipeline executions"""
        results = []
        for moisture in [25, 35, 45, 55, 65]:
            result = await orchestrator.execute_pipeline(
                sensor_data={"soil_moisture": moisture},
            )
            results.append(result)

        assert len(results) == 5
        # Low moisture should trigger irrigation
        assert results[0]["result"]["decision"] == "irrigate"
        # High moisture should wait
        assert results[4]["result"]["decision"] == "wait"


class TestEdgeCloudSync:
    """Tests for edge-cloud synchronization"""

    @pytest.fixture
    def orchestrator(self, cooperative_system_config: dict[str, Any]) -> CooperativeOrchestrator:
        return CooperativeOrchestrator(cooperative_system_config)

    @pytest.mark.asyncio
    async def test_sync_edge_to_cloud_success(self, orchestrator: CooperativeOrchestrator):
        """Test successful edge to cloud sync"""
        data = [{"reading_id": str(uuid.uuid4()), "value": 45.0} for _ in range(100)]

        result = await orchestrator.sync_edge_to_cloud(data)

        assert result["success"] is True
        assert result["records_synced"] == 100
        assert result["direction"] == "edge_to_cloud"

    @pytest.mark.asyncio
    async def test_sync_fails_when_cloud_unavailable(self, orchestrator: CooperativeOrchestrator):
        """Test sync fails when cloud is unavailable"""
        orchestrator.set_cloud_status("disconnected")

        data = [{"reading_id": str(uuid.uuid4())}]
        result = await orchestrator.sync_edge_to_cloud(data)

        assert result["success"] is False
        assert result["reason"] == "cloud_unavailable"
        assert result["records_pending"] == 1

    @pytest.mark.asyncio
    async def test_sync_cloud_to_edge_model_updates(self, orchestrator: CooperativeOrchestrator):
        """Test cloud to edge sync includes model updates"""
        result = await orchestrator.sync_cloud_to_edge(
            model_updates=True,
            config_updates=False,
        )

        assert result["success"] is True
        assert len(result["updates"]) == 1
        assert result["updates"][0]["type"] == "model"

    @pytest.mark.asyncio
    async def test_sync_cloud_to_edge_all_updates(self, orchestrator: CooperativeOrchestrator):
        """Test cloud to edge sync with all update types"""
        result = await orchestrator.sync_cloud_to_edge(
            model_updates=True,
            config_updates=True,
        )

        assert result["success"] is True
        assert len(result["updates"]) == 2
        update_types = [u["type"] for u in result["updates"]]
        assert "model" in update_types
        assert "config" in update_types

    @pytest.mark.asyncio
    async def test_sync_metrics_tracked(self, orchestrator: CooperativeOrchestrator):
        """Test sync operations update metrics"""
        initial_metrics = orchestrator.get_system_metrics()
        initial_sync_count = initial_metrics["sync_count"]

        await orchestrator.sync_edge_to_cloud([{"test": "data"}])

        updated_metrics = orchestrator.get_system_metrics()
        assert updated_metrics["sync_count"] == initial_sync_count + 1


class TestFallbackToEdge:
    """Tests for fallback to edge when cloud unavailable"""

    @pytest.fixture
    def orchestrator(self, cooperative_system_config: dict[str, Any]) -> CooperativeOrchestrator:
        return CooperativeOrchestrator(cooperative_system_config)

    def test_fallback_from_cloud_to_edge(self, orchestrator: CooperativeOrchestrator):
        """Test fallback from cloud to edge"""
        result = orchestrator.handle_fallback("cloud", "connection_timeout")

        assert result["fallback_to"] == "edge"
        assert result["reason"] == "connection_timeout"
        assert result["degraded_mode"] is True
        assert "basic_inference" in result["capabilities_available"]

    def test_fallback_from_edge_to_buffered(self, orchestrator: CooperativeOrchestrator):
        """Test fallback from edge to buffered mode"""
        result = orchestrator.handle_fallback("edge", "hardware_failure")

        assert result["fallback_to"] == "buffered"
        assert result["reason"] == "hardware_failure"
        assert "data_buffering" in result["capabilities_available"]

    @pytest.mark.asyncio
    async def test_automatic_fallback_in_pipeline(self, orchestrator: CooperativeOrchestrator):
        """Test automatic fallback in pipeline execution"""
        # Set cloud mode but make cloud unavailable
        orchestrator.set_mode(InferenceMode.CLOUD.value)
        orchestrator.set_cloud_status("disconnected")

        result = await orchestrator.execute_pipeline(
            sensor_data={"soil_moisture": 30},
        )

        # Should fall back to edge
        assert result["execution_layer"] == "edge"
        assert result["routing_reason"] == "cloud_unavailable_fallback"

    def test_fallback_metrics_tracked(self, orchestrator: CooperativeOrchestrator):
        """Test fallback operations update metrics"""
        initial_metrics = orchestrator.get_system_metrics()
        initial_fallback = initial_metrics["fallback_count"]

        orchestrator.handle_fallback("cloud", "test_error")

        updated_metrics = orchestrator.get_system_metrics()
        assert updated_metrics["fallback_count"] == initial_fallback + 1

    @pytest.mark.asyncio
    async def test_routing_with_edge_fallback(self, orchestrator: CooperativeOrchestrator):
        """Test routing includes fallback availability"""
        # Cloud connected - fallback available
        routing = orchestrator.route_inference("pest_detection", latency_required_ms=500)
        assert routing["fallback_available"] is True

        # Cloud disconnected - no fallback for cloud tasks
        orchestrator.set_cloud_status("disconnected")
        routing = orchestrator.route_inference("pest_detection", latency_required_ms=500)
        # Should route to edge, no cloud fallback
        assert routing["execution_layer"] == "edge"


class TestSystemMetrics:
    """Tests for system metrics and monitoring"""

    @pytest.fixture
    def orchestrator(self, cooperative_system_config: dict[str, Any]) -> CooperativeOrchestrator:
        return CooperativeOrchestrator(cooperative_system_config)

    def test_initial_metrics(self, orchestrator: CooperativeOrchestrator):
        """Test initial metrics state"""
        metrics = orchestrator.get_system_metrics()

        assert metrics["edge_inference_count"] == 0
        assert metrics["cloud_inference_count"] == 0
        assert metrics["sync_count"] == 0
        assert metrics["fallback_count"] == 0

    @pytest.mark.asyncio
    async def test_metrics_after_edge_inference(self, orchestrator: CooperativeOrchestrator):
        """Test metrics updated after edge inference"""
        orchestrator.set_mode(InferenceMode.EDGE.value)

        await orchestrator.execute_pipeline(sensor_data={"soil_moisture": 30})

        metrics = orchestrator.get_system_metrics()
        assert metrics["edge_inference_count"] == 1
        assert metrics["cloud_inference_count"] == 0

    @pytest.mark.asyncio
    async def test_metrics_after_cloud_inference(self, orchestrator: CooperativeOrchestrator):
        """Test metrics updated after cloud inference"""
        orchestrator.set_mode(InferenceMode.CLOUD.value)

        await orchestrator.execute_pipeline(sensor_data={"soil_moisture": 30})

        metrics = orchestrator.get_system_metrics()
        assert metrics["cloud_inference_count"] == 1

    @pytest.mark.asyncio
    async def test_edge_inference_ratio(self, orchestrator: CooperativeOrchestrator):
        """Test edge inference ratio calculation"""
        # Run some edge inferences
        orchestrator.set_mode(InferenceMode.EDGE.value)
        for _ in range(3):
            await orchestrator.execute_pipeline(sensor_data={"soil_moisture": 30})

        # Run some cloud inferences
        orchestrator.set_mode(InferenceMode.CLOUD.value)
        for _ in range(2):
            await orchestrator.execute_pipeline(sensor_data={"soil_moisture": 30})

        metrics = orchestrator.get_system_metrics()
        assert metrics["edge_inference_count"] == 3
        assert metrics["cloud_inference_count"] == 2
        assert metrics["total_inference_count"] == 5
        assert metrics["edge_inference_ratio"] == 0.6  # 3/5

    def test_metrics_include_status(self, orchestrator: CooperativeOrchestrator):
        """Test metrics include system status"""
        metrics = orchestrator.get_system_metrics()

        assert "mode" in metrics
        assert "edge_status" in metrics
        assert "cloud_status" in metrics

    @pytest.mark.asyncio
    async def test_comprehensive_metrics_scenario(self, orchestrator: CooperativeOrchestrator):
        """Test comprehensive metrics in realistic scenario"""
        # Simulate mixed workload
        for _ in range(5):
            await orchestrator.execute_pipeline(
                sensor_data={"soil_moisture": 30},
                task_type="irrigation_decision",  # Goes to edge
            )

        for _ in range(3):
            await orchestrator.execute_pipeline(
                sensor_data={"soil_moisture": 30},
                task_type="pest_detection",  # Goes to cloud
            )

        await orchestrator.sync_edge_to_cloud([{"data": "test"}])
        orchestrator.handle_fallback("cloud", "test")

        metrics = orchestrator.get_system_metrics()

        assert metrics["edge_inference_count"] == 5
        assert metrics["cloud_inference_count"] == 3
        assert metrics["sync_count"] == 1
        assert metrics["fallback_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
