# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Comprehensive unit tests for Edge Orchestrator Service.

Targets >60% code coverage across:
- schemas (models, enums, validators)
- device_manager (DeviceConnection, DeviceManager)
- config (Settings)
- API endpoints (devices, jobs, sync)
- websocket manager
"""

import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

# Set test env vars before importing anything from the service
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------
class TestSchemaEnums:
    """Test all StrEnum definitions in schemas."""

    def test_device_type_values(self):
        from src.api.schemas import DeviceType

        assert DeviceType.JETSON_ORIN_NANO == "jetson_orin_nano"
        assert DeviceType.RASPBERRY_PI_5 == "raspberry_pi_5"
        assert len(DeviceType) == 5

    def test_device_status_values(self):
        from src.api.schemas import DeviceStatus

        assert DeviceStatus.ONLINE == "online"
        assert DeviceStatus.OFFLINE == "offline"
        assert DeviceStatus.DEPLOYING == "deploying"
        assert len(DeviceStatus) == 8

    def test_job_type_values(self):
        from src.api.schemas import JobType

        assert JobType.INFERENCE == "inference"
        assert JobType.MODEL_DEPLOY == "model_deploy"
        assert len(JobType) == 7

    def test_job_status_values(self):
        from src.api.schemas import JobStatus

        assert JobStatus.PENDING == "pending"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.TIMEOUT == "timeout"

    def test_job_priority_values(self):
        from src.api.schemas import JobPriority

        assert JobPriority.LOW == "low"
        assert JobPriority.CRITICAL == "critical"

    def test_sync_direction_values(self):
        from src.api.schemas import SyncDirection

        assert SyncDirection.UPLOAD == "upload"
        assert SyncDirection.BIDIRECTIONAL == "bidirectional"

    def test_model_format_values(self):
        from src.api.schemas import ModelFormat

        assert ModelFormat.TENSORRT == "tensorrt"
        assert ModelFormat.ONNX == "onnx"

    def test_ws_message_type_values(self):
        from src.api.schemas import WSMessageType

        assert WSMessageType.HEARTBEAT == "heartbeat"
        assert WSMessageType.DETECTION == "detection"


class TestSchemaModels:
    """Test Pydantic models for serialization and validation."""

    def test_device_capabilities_defaults(self):
        from src.api.schemas import DeviceCapabilities

        caps = DeviceCapabilities()
        assert caps.gpu_memory_gb == 8.0
        assert caps.cpu_cores == 6
        assert "csi" in caps.camera_interfaces

    def test_device_metrics_bounds(self):
        from src.api.schemas import DeviceMetrics

        m = DeviceMetrics(cpu_usage_percent=50.0, gpu_usage_percent=75.0)
        assert m.cpu_usage_percent == 50.0
        assert m.power_usage_watts == 0.0

    def test_geo_location_validation(self):
        from src.api.schemas import GeoLocation

        loc = GeoLocation(latitude=24.7, longitude=46.7)
        assert loc.latitude == 24.7

        with pytest.raises((ValueError, ValidationError, Exception)):
            GeoLocation(latitude=200, longitude=46.7)

    def test_edge_device_create_mac_validation(self):
        from src.api.schemas import EdgeDeviceCreate

        # Valid MAC with dashes (should be normalised)
        dev = EdgeDeviceCreate(
            name="Dev1",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            mac_address="aa-bb-cc-dd-ee-ff",
        )
        assert dev.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_edge_device_create_invalid_mac(self):
        from src.api.schemas import EdgeDeviceCreate

        with pytest.raises((ValueError, ValidationError, Exception)):
            EdgeDeviceCreate(
                name="Dev1",
                device_type="jetson_orin_nano",
                farm_id=uuid4(),
                mac_address="ZZ:ZZ:ZZ:ZZ:ZZ:ZZ",
            )

    def test_edge_device_create_mac_wrong_format(self):
        from src.api.schemas import EdgeDeviceCreate

        with pytest.raises((ValueError, ValidationError, Exception)):
            EdgeDeviceCreate(
                name="Dev1",
                device_type="jetson_orin_nano",
                farm_id=uuid4(),
                mac_address="AABB",
            )

    def test_edge_device_create_mac_none(self):
        from src.api.schemas import EdgeDeviceCreate

        dev = EdgeDeviceCreate(
            name="Dev1",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            mac_address=None,
        )
        assert dev.mac_address is None

    def test_job_config_defaults(self):
        from src.api.schemas import JobConfig

        cfg = JobConfig()
        assert cfg.confidence_threshold == 0.5
        assert cfg.batch_size == 1

    def test_job_result_model(self):
        from src.api.schemas import JobResult

        r = JobResult(success=True, message="Done", execution_time_ms=120)
        assert r.success is True
        assert r.execution_time_ms == 120

    def test_sync_data_item(self):
        from src.api.schemas import SyncDataItem

        item = SyncDataItem(item_type="sensor", item_id="s-1", data={"temp": 30})
        assert item.item_type == "sensor"

    def test_deploy_request(self):
        from src.api.schemas import DeployRequest

        dr = DeployRequest(device_id=uuid4(), model_name="yolo26-s")
        assert dr.model_version == "latest"
        assert dr.validate_after_deploy is True

    def test_detection_result(self):
        from src.api.schemas import DetectionResult

        d = DetectionResult(class_name="aphid", confidence=0.92)
        assert d.confidence == 0.92

    def test_inference_result(self):
        from src.api.schemas import InferenceResult

        ir = InferenceResult(
            device_id=uuid4(),
            model_name="yolo26-s",
            model_version="1.0",
            inference_time_ms=5.5,
        )
        assert ir.inference_time_ms == 5.5

    def test_health_status_defaults(self):
        from src.api.schemas import HealthStatus

        hs = HealthStatus()
        assert hs.status == "ok"

    def test_readiness_status(self):
        from src.api.schemas import ReadinessStatus

        rs = ReadinessStatus(active_devices=3, active_jobs=1)
        assert rs.active_devices == 3
        assert rs.database is False

    def test_ws_message(self):
        from src.api.schemas import WSMessage, WSMessageType

        msg = WSMessage(type=WSMessageType.ALERT, payload={"msg": "test"})
        assert msg.type == "alert"

    def test_edge_device_list(self):
        from src.api.schemas import EdgeDeviceList

        el = EdgeDeviceList(items=[], total=0, pages=1)
        assert el.total == 0

    def test_edge_job_list(self):
        from src.api.schemas import EdgeJobList

        jl = EdgeJobList(items=[], total=0, pages=1)
        assert jl.total == 0


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------
class TestConfig:
    """Test Settings from config.py."""

    def test_settings_defaults(self):
        from src.core.config import Settings

        s = Settings(environment="test")
        assert s.service_name == "edge-orchestrator-service"
        assert s.port == 8180
        assert s.version == "16.0.0"

    def test_settings_is_development(self):
        from src.core.config import Settings

        s = Settings(environment="development")
        assert s.is_development is True
        assert s.is_production is False

    def test_settings_is_production(self):
        from src.core.config import Settings

        s = Settings(environment="production")
        assert s.is_production is True

    def test_validate_log_level_valid(self):
        from src.core.config import Settings

        s = Settings(environment="test", log_level="debug")
        assert s.log_level == "DEBUG"

    def test_validate_log_level_invalid(self):
        from src.core.config import Settings

        with pytest.raises((ValueError, ValidationError, Exception)):
            Settings(environment="test", log_level="INVALID")

    def test_supported_models_default(self):
        from src.core.config import Settings

        s = Settings(environment="test")
        assert "yolo26-s" in s.supported_models
        assert len(s.supported_models) == 6


# ---------------------------------------------------------------------------
# DeviceConnection tests
# ---------------------------------------------------------------------------
class TestDeviceConnection:
    """Test DeviceConnection class."""

    def test_init(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="192.168.1.1")
        assert conn.base_url == "http://192.168.1.1:8000"
        assert conn.is_connected is False

    def test_is_connected_false_when_no_heartbeat(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        conn._connected = True
        # No heartbeat set => not connected
        assert conn.is_connected is False

    def test_is_connected_true_recent_heartbeat(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        conn._connected = True
        conn._last_heartbeat = datetime.utcnow()
        assert conn.is_connected is True

    def test_is_connected_stale_heartbeat(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        conn._connected = True
        conn._last_heartbeat = datetime.utcnow() - timedelta(seconds=300)
        assert conn.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        conn._client = AsyncMock()
        conn._connected = True
        await conn.disconnect()
        assert conn._connected is False
        assert conn._client is None

    @pytest.mark.asyncio
    async def test_heartbeat_no_client(self):
        from src.utils.device_manager import DeviceConnection

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        result = await conn.heartbeat()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_metrics_not_connected(self):
        from src.utils.device_manager import DeviceConnection, DeviceConnectionError

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        with pytest.raises(DeviceConnectionError):
            await conn.get_metrics()

    @pytest.mark.asyncio
    async def test_execute_job_not_connected(self):
        from src.utils.device_manager import DeviceConnection, DeviceConnectionError

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        with pytest.raises(DeviceConnectionError):
            await conn.execute_job("inference", {"timeout_seconds": 10})

    @pytest.mark.asyncio
    async def test_run_inference_not_connected(self):
        from src.utils.device_manager import DeviceConnection, DeviceConnectionError

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        with pytest.raises(DeviceConnectionError):
            await conn.run_inference("yolo26-s", {"image": "test"})

    @pytest.mark.asyncio
    async def test_deploy_model_not_connected(self):
        from src.api.schemas import DeployRequest
        from src.utils.device_manager import DeviceConnection, DeviceConnectionError

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        req = DeployRequest(device_id=uuid4(), model_name="yolo26-s")
        with pytest.raises(DeviceConnectionError):
            await conn.deploy_model(req)

    @pytest.mark.asyncio
    async def test_sync_data_not_connected(self):
        from src.api.schemas import SyncRequest
        from src.utils.device_manager import DeviceConnection, DeviceConnectionError

        conn = DeviceConnection(device_id=uuid4(), ip_address="10.0.0.1")
        req = SyncRequest(device_id=uuid4())
        with pytest.raises(DeviceConnectionError):
            await conn.sync_data(req)


# ---------------------------------------------------------------------------
# DeviceManager tests
# ---------------------------------------------------------------------------
class TestDeviceManager:
    """Test DeviceManager class."""

    def test_initial_state(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        assert dm.total_devices == 0
        assert dm.connected_devices == []

    @pytest.mark.asyncio
    async def test_register_device_no_ip(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        device = EdgeDevice(
            id=uuid4(),
            tenant_id=uuid4(),
            name="TestDev",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            status=DeviceStatus.OFFLINE,
            capabilities=DeviceCapabilities(),
            metrics=DeviceMetrics(),
        )
        result = await dm.register_device(device)
        assert result is None
        assert dm.total_devices == 1

    @pytest.mark.asyncio
    async def test_get_device(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        dev_id = uuid4()
        device = EdgeDevice(
            id=dev_id,
            tenant_id=uuid4(),
            name="TestDev",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            status=DeviceStatus.OFFLINE,
            capabilities=DeviceCapabilities(),
            metrics=DeviceMetrics(),
        )
        await dm.register_device(device)
        retrieved = await dm.get_device(dev_id)
        assert retrieved is not None
        assert retrieved.name == "TestDev"

    @pytest.mark.asyncio
    async def test_get_device_not_found(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        assert await dm.get_device(uuid4()) is None

    @pytest.mark.asyncio
    async def test_unregister_device(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        dev_id = uuid4()
        device = EdgeDevice(
            id=dev_id,
            tenant_id=uuid4(),
            name="TestDev",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            status=DeviceStatus.OFFLINE,
            capabilities=DeviceCapabilities(),
            metrics=DeviceMetrics(),
        )
        await dm.register_device(device)
        result = await dm.unregister_device(dev_id)
        assert result is True
        assert dm.total_devices == 0

    @pytest.mark.asyncio
    async def test_unregister_nonexistent(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        result = await dm.unregister_device(uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_update_device_status(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        dev_id = uuid4()
        device = EdgeDevice(
            id=dev_id,
            tenant_id=uuid4(),
            name="TestDev",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            status=DeviceStatus.OFFLINE,
            capabilities=DeviceCapabilities(),
            metrics=DeviceMetrics(),
        )
        await dm.register_device(device)
        await dm.update_device_status(dev_id, DeviceStatus.ONLINE)
        updated = await dm.get_device(dev_id)
        assert updated.status == DeviceStatus.ONLINE

    @pytest.mark.asyncio
    async def test_update_device_metrics(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        dev_id = uuid4()
        device = EdgeDevice(
            id=dev_id,
            tenant_id=uuid4(),
            name="TestDev",
            device_type="jetson_orin_nano",
            farm_id=uuid4(),
            status=DeviceStatus.OFFLINE,
            capabilities=DeviceCapabilities(),
            metrics=DeviceMetrics(),
        )
        await dm.register_device(device)
        new_metrics = DeviceMetrics(cpu_usage_percent=75.0)
        await dm.update_device_metrics(dev_id, new_metrics)
        updated = await dm.get_device(dev_id)
        assert updated.metrics.cpu_usage_percent == 75.0

    @pytest.mark.asyncio
    async def test_get_all_devices(self):
        from src.api.schemas import DeviceCapabilities, DeviceMetrics, DeviceStatus, EdgeDevice
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        for _ in range(3):
            device = EdgeDevice(
                id=uuid4(),
                tenant_id=uuid4(),
                name="Dev",
                device_type="jetson_orin_nano",
                farm_id=uuid4(),
                status=DeviceStatus.OFFLINE,
                capabilities=DeviceCapabilities(),
                metrics=DeviceMetrics(),
            )
            await dm.register_device(device)
        devices = await dm.get_all_devices()
        assert len(devices) == 3

    @pytest.mark.asyncio
    async def test_get_connection_none(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        assert await dm.get_connection(uuid4()) is None


# ---------------------------------------------------------------------------
# get_device_manager singleton test
# ---------------------------------------------------------------------------
class TestGetDeviceManager:
    def test_singleton(self):
        from src.utils.device_manager import get_device_manager

        dm1 = get_device_manager()
        dm2 = get_device_manager()
        assert dm1 is dm2


# ---------------------------------------------------------------------------
# devices endpoint helper
# ---------------------------------------------------------------------------
class TestGetDefaultCapabilities:
    def test_jetson_orin_nano(self):
        from src.api.endpoints.devices import _get_default_capabilities
        from src.api.schemas import DeviceType

        caps = _get_default_capabilities(DeviceType.JETSON_ORIN_NANO)
        assert caps.gpu_memory_gb == 8.0
        assert caps.max_power_watts == 15

    def test_jetson_agx_orin(self):
        from src.api.endpoints.devices import _get_default_capabilities
        from src.api.schemas import DeviceType

        caps = _get_default_capabilities(DeviceType.JETSON_AGX_ORIN)
        assert caps.gpu_memory_gb == 64.0

    def test_raspberry_pi_5(self):
        from src.api.endpoints.devices import _get_default_capabilities
        from src.api.schemas import DeviceType

        caps = _get_default_capabilities(DeviceType.RASPBERRY_PI_5)
        assert caps.gpu_memory_gb == 0.0
        assert caps.max_power_watts == 5

    def test_generic_edge(self):
        from src.api.endpoints.devices import _get_default_capabilities
        from src.api.schemas import DeviceType

        caps = _get_default_capabilities(DeviceType.GENERIC_EDGE)
        assert caps.ram_gb == 4.0


# ---------------------------------------------------------------------------
# WebSocketManager tests
# ---------------------------------------------------------------------------
class TestWebSocketManager:
    """Test WebSocketManager methods."""

    def test_initial_connection_count(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        assert mgr.connection_count == 0

    @pytest.mark.asyncio
    async def test_subscribe_nonexistent_client(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        result = await mgr.subscribe("no-such-client", ["metrics"])
        assert result is False

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_client(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        result = await mgr.unsubscribe("no-such-client", ["metrics"])
        assert result is False

    @pytest.mark.asyncio
    async def test_send_to_client_nonexistent(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        result = await mgr.send_to_client("no-client", {"type": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_send_to_device_subscribers_empty(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.send_to_device_subscribers(uuid4(), {"type": "test"})
        assert count == 0

    @pytest.mark.asyncio
    async def test_send_to_tenant_empty(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.send_to_tenant(uuid4(), {"type": "test"})
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_empty(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.broadcast({"type": "test"})
        assert count == 0

    @pytest.mark.asyncio
    async def test_handle_client_message_ping(self):
        from src.events.websocket import WebSocketConnection, WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        conn = WebSocketConnection(
            websocket=ws_mock,
            client_id="client-1",
        )
        mgr._connections["client-1"] = conn
        await mgr.handle_client_message("client-1", {"type": "ping"})
        ws_mock.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_client_message_subscribe(self):
        from src.events.websocket import WebSocketConnection, WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        mgr._connections["c1"] = conn
        await mgr.handle_client_message(
            "c1", {"type": "subscribe", "event_types": ["metrics", "alert"]}
        )
        assert "metrics" in conn.subscriptions
        assert "alert" in conn.subscriptions

    @pytest.mark.asyncio
    async def test_handle_client_message_unsubscribe(self):
        from src.events.websocket import WebSocketConnection, WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        conn.subscriptions = {"metrics", "alert"}
        mgr._connections["c1"] = conn
        await mgr.handle_client_message("c1", {"type": "unsubscribe", "event_types": ["metrics"]})
        assert "metrics" not in conn.subscriptions
        assert "alert" in conn.subscriptions

    @pytest.mark.asyncio
    async def test_disconnect_cleans_indices(self):
        from src.events.websocket import WebSocketConnection, WebSocketManager

        mgr = WebSocketManager()
        device_id = uuid4()
        tenant_id = uuid4()
        ws_mock = AsyncMock()
        conn = WebSocketConnection(
            websocket=ws_mock,
            client_id="c1",
            device_id=device_id,
            tenant_id=tenant_id,
        )
        mgr._connections["c1"] = conn
        mgr._device_connections[device_id] = {"c1"}
        mgr._tenant_connections[tenant_id] = {"c1"}

        await mgr.disconnect("c1")

        assert "c1" not in mgr._connections
        assert device_id not in mgr._device_connections
        assert tenant_id not in mgr._tenant_connections

    @pytest.mark.asyncio
    async def test_broadcast_alert_with_device_id(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.broadcast_alert(
            device_id=uuid4(),
            tenant_id=None,
            alert_type="test_alert",
            message_en="Test",
            message_ar="اختبار",
        )
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_alert_with_tenant_id(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.broadcast_alert(
            device_id=None,
            tenant_id=uuid4(),
            alert_type="test_alert",
            message_en="Test",
            message_ar="اختبار",
        )
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_alert_global(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.broadcast_alert(
            device_id=None,
            tenant_id=None,
            alert_type="test_alert",
            message_en="Test",
            message_ar="اختبار",
        )
        assert count == 0


# ---------------------------------------------------------------------------
# WebSocketConnection tests
# ---------------------------------------------------------------------------
class TestWebSocketConnection:
    @pytest.mark.asyncio
    async def test_send_message_dict(self):
        from src.events.websocket import WebSocketConnection

        ws_mock = AsyncMock()
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        result = await conn.send_message({"type": "test"})
        assert result is True
        ws_mock.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_failure(self):
        from src.events.websocket import WebSocketConnection

        ws_mock = AsyncMock()
        ws_mock.send_json.side_effect = Exception("closed")
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        result = await conn.send_message({"type": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_close(self):
        from src.events.websocket import WebSocketConnection

        ws_mock = AsyncMock()
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        await conn.close()
        ws_mock.close.assert_called_once()


# ---------------------------------------------------------------------------
# Exception classes
# ---------------------------------------------------------------------------
class TestExceptions:
    def test_device_connection_error(self):
        from src.utils.device_manager import DeviceConnectionError

        err = DeviceConnectionError("test error")
        assert str(err) == "test error"

    def test_device_timeout_error(self):
        from src.utils.device_manager import DeviceTimeoutError

        err = DeviceTimeoutError("timeout")
        assert str(err) == "timeout"

    def test_model_deployment_error(self):
        from src.utils.device_manager import ModelDeploymentError

        err = ModelDeploymentError("deploy fail")
        assert str(err) == "deploy fail"


# ---------------------------------------------------------------------------
# API Endpoint integration tests via TestClient
# ---------------------------------------------------------------------------
try:
    from fastapi.testclient import TestClient

    from src.main import app

    _CLIENT_AVAILABLE = True
except Exception:
    _CLIENT_AVAILABLE = False


@pytest.fixture
def api_client():
    if not _CLIENT_AVAILABLE:
        pytest.skip("TestClient not available")
    try:
        from shared.auth.dependencies import get_current_user
        from shared.auth.models import User

        mock_user = User(
            id="test-user",
            tenant_id="00000000-0000-0000-0000-000000000001",
            email="test@test.com",
            roles=["admin"],
        )
        app.dependency_overrides[get_current_user] = lambda: mock_user
    except ImportError:
        pass
    client = TestClient(app, headers={"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"})
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def tenant_headers():
    return {
        "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
        "Content-Type": "application/json",
    }


class TestHealthAPI:
    """Test health endpoints via HTTP."""

    def test_healthz(self, api_client):
        resp = api_client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "edge-orchestrator-service"
        assert "version" in data

    def test_health_live(self, api_client):
        resp = api_client.get("/health/live")
        assert resp.status_code == 200

    def test_readyz(self, api_client):
        resp = api_client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert "database" in data
        assert "nats" in data
        assert "redis" in data
        assert "active_devices" in data

    def test_health_ready(self, api_client):
        resp = api_client.get("/health/ready")
        assert resp.status_code == 200

    def test_combined_health(self, api_client):
        resp = api_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "connections" in data
        assert "devices" in data
        assert "websockets" in data
        assert data["service"] == "edge-orchestrator-service"


class TestDevicesAPI:
    """Test device CRUD endpoints."""

    def _make_device(self):
        return {
            "name": "Test Jetson",
            "name_ar": "جهاز اختبار",
            "device_type": "jetson_orin_nano",
            "farm_id": str(uuid4()),
            "ip_address": "192.168.1.100",
            "mac_address": "AA:BB:CC:DD:EE:01",
            "serial_number": "SN-001",
            "tags": ["test"],
        }

    def test_list_devices(self, api_client, tenant_headers):
        resp = api_client.get("/api/v1/edge/devices", headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "pages" in data

    def test_create_device(self, api_client, tenant_headers):
        device_data = self._make_device()
        resp = api_client.post("/api/v1/edge/devices", json=device_data, headers=tenant_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == device_data["name"]
        assert data["device_type"] == "jetson_orin_nano"
        assert "id" in data
        assert "capabilities" in data

    def test_get_device_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/devices/{uuid4()}", headers=tenant_headers)
        assert resp.status_code == 404

    def test_create_and_get_device(self, api_client, tenant_headers):
        device_data = self._make_device()
        device_data["mac_address"] = "AA:BB:CC:DD:EE:02"
        create_resp = api_client.post(
            "/api/v1/edge/devices", json=device_data, headers=tenant_headers
        )
        assert create_resp.status_code == 201
        device_id = create_resp.json()["id"]

        get_resp = api_client.get(f"/api/v1/edge/devices/{device_id}", headers=tenant_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == device_id

    def test_update_device(self, api_client, tenant_headers):
        device_data = self._make_device()
        device_data["mac_address"] = "AA:BB:CC:DD:EE:03"
        create_resp = api_client.post(
            "/api/v1/edge/devices", json=device_data, headers=tenant_headers
        )
        device_id = create_resp.json()["id"]

        update_resp = api_client.put(
            f"/api/v1/edge/devices/{device_id}",
            json={"name": "Updated Name"},
            headers=tenant_headers,
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Updated Name"

    def test_delete_device(self, api_client, tenant_headers):
        device_data = self._make_device()
        device_data["mac_address"] = "AA:BB:CC:DD:EE:04"
        create_resp = api_client.post(
            "/api/v1/edge/devices", json=device_data, headers=tenant_headers
        )
        device_id = create_resp.json()["id"]

        del_resp = api_client.delete(f"/api/v1/edge/devices/{device_id}", headers=tenant_headers)
        assert del_resp.status_code == 204

        get_resp = api_client.get(f"/api/v1/edge/devices/{device_id}", headers=tenant_headers)
        assert get_resp.status_code == 404

    def test_delete_device_not_found(self, api_client, tenant_headers):
        resp = api_client.delete(f"/api/v1/edge/devices/{uuid4()}", headers=tenant_headers)
        assert resp.status_code == 404

    def test_reconnect_device_not_found(self, api_client, tenant_headers):
        resp = api_client.post(f"/api/v1/edge/devices/{uuid4()}/reconnect", headers=tenant_headers)
        assert resp.status_code == 404

    def test_get_metrics_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/devices/{uuid4()}/metrics", headers=tenant_headers)
        assert resp.status_code == 404

    def test_create_device_invalid_mac(self, api_client, tenant_headers):
        device_data = self._make_device()
        device_data["mac_address"] = "invalid"
        resp = api_client.post("/api/v1/edge/devices", json=device_data, headers=tenant_headers)
        assert resp.status_code == 422

    def test_list_devices_with_filters(self, api_client, tenant_headers):
        resp = api_client.get(
            "/api/v1/edge/devices",
            params={"status": "online", "device_type": "jetson_orin_nano"},
            headers=tenant_headers,
        )
        assert resp.status_code == 200

    def test_list_devices_with_search(self, api_client, tenant_headers):
        resp = api_client.get(
            "/api/v1/edge/devices",
            params={"search": "jetson"},
            headers=tenant_headers,
        )
        assert resp.status_code == 200

    def test_invalid_tenant_id(self, api_client):
        resp = api_client.get(
            "/api/v1/edge/devices",
            headers={"X-Tenant-ID": "not-a-uuid"},
        )
        assert resp.status_code == 400


class TestJobsAPI:
    """Test job management endpoints."""

    def test_list_all_jobs(self, api_client, tenant_headers):
        resp = api_client.get("/api/v1/edge/jobs", headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    def test_get_job_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/jobs/{uuid4()}", headers=tenant_headers)
        assert resp.status_code == 404

    def test_cancel_job_not_found(self, api_client, tenant_headers):
        resp = api_client.post(f"/api/v1/edge/jobs/{uuid4()}/cancel", headers=tenant_headers)
        assert resp.status_code == 404

    def test_retry_job_not_found(self, api_client, tenant_headers):
        resp = api_client.post(f"/api/v1/edge/jobs/{uuid4()}/retry", headers=tenant_headers)
        assert resp.status_code == 404

    def test_list_device_jobs_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/devices/{uuid4()}/jobs", headers=tenant_headers)
        assert resp.status_code == 404

    def test_list_jobs_with_filters(self, api_client, tenant_headers):
        resp = api_client.get(
            "/api/v1/edge/jobs",
            params={"status": "pending", "job_type": "inference"},
            headers=tenant_headers,
        )
        assert resp.status_code == 200

    def test_create_job_device_not_found(self, api_client, tenant_headers):
        job_data = {
            "job_type": "inference",
            "device_id": str(uuid4()),
            "priority": "normal",
            "config": {"model_name": "yolo26-s", "confidence_threshold": 0.5},
        }
        resp = api_client.post("/api/v1/edge/jobs", json=job_data, headers=tenant_headers)
        assert resp.status_code == 404


class TestSyncDeployAPI:
    """Test sync and deploy endpoints."""

    def test_list_models(self, api_client):
        resp = api_client.get("/api/v1/edge/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert "yolo26-s" in data["models"]
        assert "crop-disease-v3" in data["models"]
        assert data["total"] == 6

    def test_get_sync_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/sync/{uuid4()}/status", headers=tenant_headers)
        assert resp.status_code == 404

    def test_get_deploy_not_found(self, api_client, tenant_headers):
        resp = api_client.get(f"/api/v1/edge/deploy/{uuid4()}/status", headers=tenant_headers)
        assert resp.status_code == 404

    def test_cancel_deploy_not_found(self, api_client, tenant_headers):
        resp = api_client.post(f"/api/v1/edge/deploy/{uuid4()}/cancel", headers=tenant_headers)
        assert resp.status_code == 404

    def test_sync_device_not_found(self, api_client, tenant_headers):
        resp = api_client.post(f"/api/v1/edge/sync/{uuid4()}", headers=tenant_headers)
        assert resp.status_code == 404

    def test_deploy_device_not_found(self, api_client, tenant_headers):
        resp = api_client.post(
            f"/api/v1/edge/deploy/{uuid4()}",
            params={"model_name": "yolo26-s"},
            headers=tenant_headers,
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Extended Device CRUD + Job workflow tests to cover deeper code paths
# ---------------------------------------------------------------------------
class TestDeviceWorkflows:
    """Test deeper device + job + sync workflows."""

    def _create_device(self, api_client, tenant_headers, mac="AA:BB:CC:DD:EE:10"):
        """Helper to create a device and return its ID."""
        device_data = {
            "name": "Workflow Device",
            "device_type": "jetson_orin_nano",
            "farm_id": str(uuid4()),
            "ip_address": "10.0.0.50",
            "mac_address": mac,
        }
        resp = api_client.post("/api/v1/edge/devices", json=device_data, headers=tenant_headers)
        assert resp.status_code == 201
        return resp.json()["id"]

    def test_reconnect_device_no_ip(self, api_client, tenant_headers):
        """Test reconnect on device without IP."""
        device_data = {
            "name": "No IP Device",
            "device_type": "generic_edge",
            "farm_id": str(uuid4()),
        }
        resp = api_client.post("/api/v1/edge/devices", json=device_data, headers=tenant_headers)
        assert resp.status_code == 201
        dev_id = resp.json()["id"]

        resp = api_client.post(f"/api/v1/edge/devices/{dev_id}/reconnect", headers=tenant_headers)
        assert resp.status_code == 400

    def test_reconnect_device_with_ip(self, api_client, tenant_headers):
        """Test reconnect on device with IP - will fail to connect but exercises the code path."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:11")
        resp = api_client.post(f"/api/v1/edge/devices/{dev_id}/reconnect", headers=tenant_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("online", "offline")

    def test_get_metrics_device_not_connected(self, api_client, tenant_headers):
        """Test getting metrics for offline device."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:12")
        resp = api_client.get(f"/api/v1/edge/devices/{dev_id}/metrics", headers=tenant_headers)
        assert resp.status_code == 503

    def test_update_device_ip_change(self, api_client, tenant_headers):
        """Test updating device with IP change triggers reconnection."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:13")
        resp = api_client.put(
            f"/api/v1/edge/devices/{dev_id}",
            json={"ip_address": "10.0.0.99"},
            headers=tenant_headers,
        )
        assert resp.status_code == 200

    def test_create_job_device_offline(self, api_client, tenant_headers):
        """Creating a job for offline device without schedule should fail."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:14")
        job_data = {
            "job_type": "inference",
            "device_id": dev_id,
            "priority": "normal",
            "config": {"model_name": "yolo26-s"},
        }
        resp = api_client.post("/api/v1/edge/jobs", json=job_data, headers=tenant_headers)
        assert resp.status_code == 503

    def test_create_job_unsupported_model(self, api_client, tenant_headers):
        """Creating a job with unsupported model should fail with 503 (device offline)
        or 400 (model not supported)."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:15")
        job_data = {
            "job_type": "inference",
            "device_id": dev_id,
            "priority": "high",
            "config": {"model_name": "nonexistent-model"},
        }
        resp = api_client.post("/api/v1/edge/jobs", json=job_data, headers=tenant_headers)
        # Could be 400 (model not supported) or 503 (offline) depending on check order
        assert resp.status_code in (400, 503)

    def test_list_device_jobs(self, api_client, tenant_headers):
        """List jobs for a specific device."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:16")
        resp = api_client.get(f"/api/v1/edge/devices/{dev_id}/jobs", headers=tenant_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_sync_device_offline(self, api_client, tenant_headers):
        """Syncing with offline device should fail."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:17")
        resp = api_client.post(f"/api/v1/edge/sync/{dev_id}", headers=tenant_headers)
        assert resp.status_code == 503

    def test_deploy_device_offline(self, api_client, tenant_headers):
        """Deploying to offline device should fail."""
        dev_id = self._create_device(api_client, tenant_headers, mac="AA:BB:CC:DD:EE:18")
        resp = api_client.post(
            f"/api/v1/edge/deploy/{dev_id}",
            params={"model_name": "yolo26-s"},
            headers=tenant_headers,
        )
        assert resp.status_code == 503

    def test_device_forbidden_access(self, api_client):
        """Test accessing device with wrong tenant."""
        headers_a = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}
        headers_b = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000002"}

        device_data = {
            "name": "Tenant A Device",
            "device_type": "jetson_orin_nano",
            "farm_id": str(uuid4()),
            "mac_address": "AA:BB:CC:DD:EE:19",
        }
        resp = api_client.post("/api/v1/edge/devices", json=device_data, headers=headers_a)
        dev_id = resp.json()["id"]

        resp = api_client.get(f"/api/v1/edge/devices/{dev_id}", headers=headers_b)
        assert resp.status_code == 403

    def test_list_devices_pagination(self, api_client, tenant_headers):
        resp = api_client.get(
            "/api/v1/edge/devices",
            params={"page": 1, "page_size": 5},
            headers=tenant_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 5


# ---------------------------------------------------------------------------
# Sync/deploy endpoint tenant_id validation tests
# ---------------------------------------------------------------------------
class TestTenantValidation:
    def test_devices_invalid_tenant(self, api_client):
        resp = api_client.get(
            "/api/v1/edge/devices",
            headers={"X-Tenant-ID": "bad-uuid"},
        )
        assert resp.status_code == 400

    def test_jobs_invalid_tenant(self, api_client):
        resp = api_client.get(
            "/api/v1/edge/jobs",
            headers={"X-Tenant-ID": "bad-uuid"},
        )
        assert resp.status_code == 400

    def test_sync_invalid_tenant(self, api_client):
        resp = api_client.get(
            f"/api/v1/edge/sync/{uuid4()}/status",
            headers={"X-Tenant-ID": "bad-uuid"},
        )
        assert resp.status_code == 400

    def test_deploy_invalid_tenant(self, api_client):
        resp = api_client.get(
            f"/api/v1/edge/deploy/{uuid4()}/status",
            headers={"X-Tenant-ID": "bad-uuid"},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Background task / sync-deploy operation store tests
# ---------------------------------------------------------------------------
class TestSyncDeployStores:
    """Test in-memory sync/deploy operation stores."""

    def test_sync_operations_store(self):
        from src.api.endpoints.sync import _sync_operations

        assert isinstance(_sync_operations, dict)

    def test_deploy_operations_store(self):
        from src.api.endpoints.sync import _deploy_operations

        assert isinstance(_deploy_operations, dict)

    def test_jobs_store(self):
        from src.api.endpoints.jobs import _job_queues, _jobs_store

        assert isinstance(_jobs_store, dict)
        assert isinstance(_job_queues, dict)


class TestExecuteSyncOperation:
    """Test execute_sync_operation background function."""

    @pytest.mark.asyncio
    async def test_execute_sync_no_op(self):
        from src.api.endpoints.sync import execute_sync_operation
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        fake_sync_id = uuid4()
        # sync_op not in store => early return
        await execute_sync_operation(fake_sync_id, MagicMock(), dm)

    @pytest.mark.asyncio
    async def test_execute_sync_connection_error(self):
        from src.api.endpoints.sync import SyncResponse, _sync_operations, execute_sync_operation
        from src.api.schemas import SyncDirection, SyncProgress, SyncRequest
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        sync_id = uuid4()
        device_id = uuid4()

        sync_op = SyncResponse(
            sync_id=sync_id,
            device_id=device_id,
            status="pending",
            direction=SyncDirection.UPLOAD,
            progress=SyncProgress(),
        )
        _sync_operations[sync_id] = sync_op

        req = SyncRequest(device_id=device_id, direction=SyncDirection.UPLOAD)
        await execute_sync_operation(sync_id, req, dm)

        assert _sync_operations[sync_id].status == "failed"
        # Cleanup
        del _sync_operations[sync_id]


class TestExecuteDeployOperation:
    """Test execute_deploy_operation background function."""

    @pytest.mark.asyncio
    async def test_execute_deploy_no_op(self):
        from src.api.endpoints.sync import execute_deploy_operation
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        await execute_deploy_operation(uuid4(), MagicMock(), dm)

    @pytest.mark.asyncio
    async def test_execute_deploy_connection_error(self):
        from src.api.endpoints.sync import (
            DeployResponse,
            _deploy_operations,
            execute_deploy_operation,
        )
        from src.api.schemas import DeployProgress, DeployRequest
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        deploy_id = uuid4()
        device_id = uuid4()

        deploy_op = DeployResponse(
            deploy_id=deploy_id,
            device_id=device_id,
            model_name="yolo26-s",
            model_version="latest",
            status="pending",
            progress=DeployProgress(),
        )
        _deploy_operations[deploy_id] = deploy_op

        req = DeployRequest(device_id=device_id, model_name="yolo26-s")
        await execute_deploy_operation(deploy_id, req, dm)

        assert _deploy_operations[deploy_id].status == "failed"
        del _deploy_operations[deploy_id]


class TestExecuteJobOnDevice:
    """Test execute_job_on_device background function."""

    @pytest.mark.asyncio
    async def test_execute_job_device_not_connected(self):
        from src.api.endpoints.jobs import EdgeJob, JobStatus, _jobs_store, execute_job_on_device
        from src.api.schemas import JobConfig, JobType
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        job_id = uuid4()
        device_id = uuid4()

        job = EdgeJob(
            id=job_id,
            tenant_id=uuid4(),
            job_type=JobType.INFERENCE,
            device_id=device_id,
            config=JobConfig(),
            status=JobStatus.PENDING,
            max_retries=0,  # No retries so the test doesn't loop
        )
        _jobs_store[job_id] = job

        await execute_job_on_device(job, dm)

        updated = _jobs_store[job_id]
        assert updated.status == JobStatus.FAILED
        del _jobs_store[job_id]


# ---------------------------------------------------------------------------
# WebSocketManager - more coverage of start/stop
# ---------------------------------------------------------------------------
class TestWSManagerStartStop:
    @pytest.mark.asyncio
    async def test_start_stop(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        await mgr.start()
        assert mgr._running is True
        assert mgr._ping_task is not None
        await mgr.stop()
        assert mgr._running is False

    @pytest.mark.asyncio
    async def test_broadcast_device_metrics(self):
        from src.api.schemas import DeviceMetrics
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        metrics = DeviceMetrics(cpu_usage_percent=50.0)
        count = await mgr.broadcast_device_metrics(uuid4(), metrics)
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_detection_result(self):
        from src.api.schemas import InferenceResult
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        result = InferenceResult(
            device_id=uuid4(),
            model_name="yolo26-s",
            model_version="1.0",
            inference_time_ms=5.0,
        )
        count = await mgr.broadcast_detection_result(uuid4(), result)
        assert count == 0

    @pytest.mark.asyncio
    async def test_broadcast_job_status(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        count = await mgr.broadcast_job_status(
            device_id=uuid4(),
            job_id=uuid4(),
            status="completed",
            progress=100.0,
        )
        assert count == 0


# ---------------------------------------------------------------------------
# DeviceManager start/stop
# ---------------------------------------------------------------------------
class TestMainModule:
    """Test main.py module-level entities."""

    def test_app_exists(self):
        from src.main import app

        assert app is not None
        assert app.title.startswith("Edge Orchestrator")

    def test_global_exception_handler(self, api_client):
        """Trigger the global exception handler via an invalid path that can raise."""
        # This tests the app routing at a minimum
        resp = api_client.get("/nonexistent")
        assert resp.status_code in (404, 405, 500)

    @pytest.mark.asyncio
    async def test_setup_nats_subscriptions(self):
        """Test _setup_nats_subscriptions function."""
        from src.events.websocket import WebSocketManager
        from src.main import _setup_nats_subscriptions

        nc_mock = AsyncMock()
        ws_mgr = WebSocketManager()
        await _setup_nats_subscriptions(nc_mock, ws_mgr)
        assert nc_mock.subscribe.call_count == 2

    @pytest.mark.asyncio
    async def test_nats_device_metrics_handler(self):
        """Test the NATS device_metrics handler via _setup_nats_subscriptions."""
        import json as json_mod

        from src.events.websocket import WebSocketManager
        from src.main import _setup_nats_subscriptions

        nc_mock = AsyncMock()
        ws_mgr = WebSocketManager()

        # Capture the callback
        handlers = {}

        async def capture_subscribe(subject, cb=None):
            handlers[subject] = cb

        nc_mock.subscribe = capture_subscribe
        await _setup_nats_subscriptions(nc_mock, ws_mgr)

        # Call the metrics handler
        handler = handlers.get("sahool.tenant.*.edge.metrics")
        assert handler is not None
        msg = MagicMock()
        msg.data = json_mod.dumps(
            {
                "device_id": str(uuid4()),
                "metrics": {"cpu_usage": 50},
            }
        ).encode()
        await handler(msg)

    @pytest.mark.asyncio
    async def test_nats_detection_handler(self):
        """Test the NATS detection handler."""
        import json as json_mod

        from src.events.websocket import WebSocketManager
        from src.main import _setup_nats_subscriptions

        nc_mock = AsyncMock()
        ws_mgr = WebSocketManager()
        handlers = {}

        async def capture_subscribe(subject, cb=None):
            handlers[subject] = cb

        nc_mock.subscribe = capture_subscribe
        await _setup_nats_subscriptions(nc_mock, ws_mgr)

        handler = handlers.get("sahool.tenant.*.edge.detection")
        assert handler is not None
        msg = MagicMock()
        msg.data = json_mod.dumps(
            {
                "device_id": str(uuid4()),
                "detections": [],
            }
        ).encode()
        await handler(msg)

    @pytest.mark.asyncio
    async def test_nats_handler_duplicate_event(self):
        """Test idempotency guard in NATS handler."""
        import json as json_mod

        from src.events.websocket import WebSocketManager
        from src.main import _setup_nats_subscriptions

        nc_mock = AsyncMock()
        ws_mgr = WebSocketManager()
        handlers = {}

        async def capture_subscribe(subject, cb=None):
            handlers[subject] = cb

        nc_mock.subscribe = capture_subscribe
        await _setup_nats_subscriptions(nc_mock, ws_mgr)

        handler = handlers["sahool.tenant.*.edge.metrics"]
        event_id = str(uuid4())
        msg = MagicMock()
        msg.data = json_mod.dumps(
            {
                "event_id": event_id,
                "device_id": str(uuid4()),
                "metrics": {},
            }
        ).encode()

        # Call twice - second should be deduped
        await handler(msg)
        await handler(msg)

    @pytest.mark.asyncio
    async def test_nats_handler_bad_json(self):
        """Test handler with invalid JSON - should not crash."""
        from src.events.websocket import WebSocketManager
        from src.main import _setup_nats_subscriptions

        nc_mock = AsyncMock()
        ws_mgr = WebSocketManager()
        handlers = {}

        async def capture_subscribe(subject, cb=None):
            handlers[subject] = cb

        nc_mock.subscribe = capture_subscribe
        await _setup_nats_subscriptions(nc_mock, ws_mgr)

        handler = handlers["sahool.tenant.*.edge.metrics"]
        msg = MagicMock()
        msg.data = b"not-json"
        await handler(msg)  # Should not raise


class TestDeviceManagerStartStop:
    @pytest.mark.asyncio
    async def test_start_stop(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        await dm.start()
        assert dm._running is True
        await dm.stop()
        assert dm._running is False

    @pytest.mark.asyncio
    async def test_broadcast_message_no_connections(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        results = await dm.broadcast_message("test", {"key": "val"})
        assert results == {}

    @pytest.mark.asyncio
    async def test_broadcast_message_with_device_ids(self):
        from src.utils.device_manager import DeviceManager

        dm = DeviceManager()
        results = await dm.broadcast_message("test", {}, device_ids=[uuid4()])
        assert len(results) == 1
        assert list(results.values())[0] is False


class TestWSManagerConnect:
    """Test WebSocketManager connect/disconnect flow."""

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        device_id = uuid4()
        tenant_id = uuid4()

        await mgr.connect(
            websocket=ws_mock,
            client_id="test-client",
            device_id=device_id,
            tenant_id=tenant_id,
        )
        assert mgr.connection_count == 1
        assert "test-client" in mgr._connections
        assert device_id in mgr._device_connections
        assert tenant_id in mgr._tenant_connections

        await mgr.disconnect("test-client")
        assert mgr.connection_count == 0

    @pytest.mark.asyncio
    async def test_connect_no_device_no_tenant(self):
        from src.events.websocket import WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        await mgr.connect(websocket=ws_mock, client_id="bare-client")
        assert mgr.connection_count == 1
        await mgr.disconnect("bare-client")

    @pytest.mark.asyncio
    async def test_broadcast_with_subscription_filter(self):
        from src.events.websocket import WebSocketConnection, WebSocketManager

        mgr = WebSocketManager()
        ws_mock = AsyncMock()
        conn = WebSocketConnection(websocket=ws_mock, client_id="c1")
        conn.subscriptions = {"metrics"}
        mgr._connections["c1"] = conn

        # Broadcast with event_type="alert" should skip c1 (only subscribed to metrics)
        count = await mgr.broadcast({"type": "alert"}, event_type="alert")
        assert count == 0

        # Broadcast with event_type="metrics" should reach c1
        count = await mgr.broadcast({"type": "metrics"}, event_type="metrics")
        assert count == 1


class TestEdgeDeviceUpdate:
    """Test EdgeDeviceUpdate schema."""

    def test_update_forbids_extra(self):
        from src.api.schemas import EdgeDeviceUpdate

        with pytest.raises((ValidationError, Exception)):
            EdgeDeviceUpdate(nonexistent_field="value")

    def test_update_partial(self):
        from src.api.schemas import EdgeDeviceUpdate

        upd = EdgeDeviceUpdate(name="New Name")
        dumped = upd.model_dump(exclude_unset=True)
        assert dumped == {"name": "New Name"}


class TestSyncRequest:
    """Test SyncRequest schema."""

    def test_defaults(self):
        from src.api.schemas import SyncRequest

        req = SyncRequest(device_id=uuid4())
        assert req.direction == "upload"
        assert req.force is False
        assert "inference_results" in req.data_types


class TestDeployProgress:
    """Test DeployProgress schema."""

    def test_defaults(self):
        from src.api.schemas import DeployProgress

        dp = DeployProgress()
        assert dp.stage == "initializing"
        assert dp.percent_complete == 0.0


class TestSyncProgress:
    """Test SyncProgress schema."""

    def test_defaults(self):
        from src.api.schemas import SyncProgress

        sp = SyncProgress()
        assert sp.total_items == 0
        assert sp.percent_complete == 0.0
