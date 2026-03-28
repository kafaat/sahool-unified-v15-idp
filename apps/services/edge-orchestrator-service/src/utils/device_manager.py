# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Device Manager for Edge Orchestrator Service.

Manages communication with edge devices (Jetson Orin Nano, etc.)
including SSH connections, API calls, and real-time monitoring.

مدير الأجهزة لخدمة تنسيق الحافة.
يدير الاتصال مع أجهزة الحافة (Jetson Orin Nano، إلخ)
بما في ذلك اتصالات SSH واستدعاءات API والمراقبة في الوقت الفعلي.
"""

import asyncio
import contextlib
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import httpx
import structlog

from src.api.schemas import (
    DeployProgress,
    DeployRequest,
    DeviceMetrics,
    DeviceStatus,
    EdgeDevice,
    JobResult,
    SyncProgress,
    SyncRequest,
)
from src.core.config import settings

logger = structlog.get_logger(__name__)


class DeviceConnectionError(Exception):
    """Error connecting to edge device | خطأ في الاتصال بجهاز الحافة."""

    pass


class DeviceTimeoutError(Exception):
    """Device operation timed out | انتهت مهلة عملية الجهاز."""

    pass


class ModelDeploymentError(Exception):
    """Error deploying model to device | خطأ في نشر النموذج على الجهاز."""

    pass


class DeviceConnection:
    """
    Manages connection to a single edge device.

    يدير الاتصال بجهاز حافة واحد.
    """

    def __init__(
        self,
        device_id: UUID,
        ip_address: str,
        api_port: int = 8000,
        ssh_port: int = 22,
    ):
        """Initialize device connection."""
        self.device_id = device_id
        self.ip_address = ip_address
        self.api_port = api_port
        self.ssh_port = ssh_port
        self.base_url = f"http://{ip_address}:{api_port}"
        self._client: httpx.AsyncClient | None = None
        self._connected = False
        self._last_heartbeat: datetime | None = None
        self._metrics_cache: DeviceMetrics | None = None

    @property
    def is_connected(self) -> bool:
        """Check if device is connected."""
        if not self._connected:
            return False
        if self._last_heartbeat is None:
            return False
        timeout = timedelta(seconds=settings.edge_timeout_threshold)
        return datetime.utcnow() - self._last_heartbeat < timeout

    async def connect(self) -> bool:
        """
        Establish connection to the edge device.

        إنشاء اتصال بجهاز الحافة.
        """
        try:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
            )

            # Test connection with health check
            response = await self._client.get("/healthz")
            if response.status_code == 200:
                self._connected = True
                self._last_heartbeat = datetime.utcnow()
                logger.info(
                    "device_connected",
                    device_id=str(self.device_id),
                    ip_address=self.ip_address,
                )
                return True

            logger.warning(
                "device_health_check_failed",
                device_id=str(self.device_id),
                status_code=response.status_code,
            )
            return False

        except httpx.ConnectError as e:
            logger.error(
                "device_connection_failed",
                device_id=str(self.device_id),
                error=str(e),
            )
            self._connected = False
            return False
        except Exception as e:
            logger.error(
                "device_connection_error",
                device_id=str(self.device_id),
                error=str(e),
            )
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._connected = False
        logger.info("device_disconnected", device_id=str(self.device_id))

    async def heartbeat(self) -> bool:
        """
        Send heartbeat to device and get status.

        إرسال نبض القلب إلى الجهاز والحصول على الحالة.
        """
        if not self._client:
            return False

        try:
            response = await self._client.get("/healthz")
            if response.status_code == 200:
                self._last_heartbeat = datetime.utcnow()
                return True
            return False
        except Exception as e:
            logger.warning(
                "heartbeat_failed",
                device_id=str(self.device_id),
                error=str(e),
            )
            return False

    async def get_metrics(self) -> DeviceMetrics:
        """
        Get current device metrics.

        الحصول على مقاييس الجهاز الحالية.
        """
        if not self._client or not self.is_connected:
            raise DeviceConnectionError(f"Device {self.device_id} is not connected")

        try:
            response = await self._client.get("/api/v1/metrics")
            if response.status_code == 200:
                data = response.json()
                self._metrics_cache = DeviceMetrics(
                    cpu_usage_percent=data.get("cpu_usage", 0),
                    gpu_usage_percent=data.get("gpu_usage", 0),
                    memory_usage_percent=data.get("memory_usage", 0),
                    disk_usage_percent=data.get("disk_usage", 0),
                    temperature_celsius=data.get("temperature", 0),
                    power_usage_watts=data.get("power_usage", 0),
                    inference_fps=data.get("inference_fps", 0),
                    uptime_seconds=data.get("uptime", 0),
                    last_heartbeat=datetime.utcnow(),
                )
                return self._metrics_cache

            raise DeviceConnectionError(f"Failed to get metrics: {response.status_code}")
        except httpx.RequestError as e:
            raise DeviceConnectionError(f"Request error: {e}")

    async def run_inference(
        self,
        model_name: str,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run inference on the device.

        تشغيل الاستدلال على الجهاز.
        """
        if not self._client or not self.is_connected:
            raise DeviceConnectionError(f"Device {self.device_id} is not connected")

        payload = {
            "model": model_name,
            "input": input_data,
            "config": config or {},
        }

        try:
            response = await self._client.post(
                "/api/v1/inference",
                json=payload,
                timeout=httpx.Timeout(120.0),
            )

            if response.status_code == 200:
                return response.json()

            raise DeviceConnectionError(
                f"Inference failed with status {response.status_code}: {response.text}"
            )
        except httpx.TimeoutException:
            raise DeviceTimeoutError(f"Inference timed out on device {self.device_id}")
        except httpx.RequestError as e:
            raise DeviceConnectionError(f"Request error during inference: {e}")

    async def deploy_model(
        self,
        request: DeployRequest,
        progress_callback: Any | None = None,
    ) -> dict[str, Any]:
        """
        Deploy a model to the device.

        نشر نموذج على الجهاز.
        """
        if not self._client or not self.is_connected:
            raise DeviceConnectionError(f"Device {self.device_id} is not connected")

        payload = {
            "model_name": request.model_name,
            "model_version": request.model_version,
            "model_format": request.model_format.value,
            "force_update": request.force_update,
            "config": request.config_overrides,
            "validate": request.validate_after_deploy,
        }

        try:
            # Start deployment
            response = await self._client.post(
                "/api/v1/models/deploy",
                json=payload,
                timeout=httpx.Timeout(600.0),  # 10 minute timeout for deployment
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    "model_deployed",
                    device_id=str(self.device_id),
                    model=request.model_name,
                    version=request.model_version,
                )
                return result
            elif response.status_code == 202:
                # Deployment started, poll for progress
                deploy_id = response.json().get("deploy_id")
                return await self._poll_deployment_status(deploy_id, progress_callback)
            else:
                raise ModelDeploymentError(
                    f"Deployment failed: {response.status_code} - {response.text}"
                )

        except httpx.TimeoutException:
            raise DeviceTimeoutError("Model deployment timed out")
        except httpx.RequestError as e:
            raise ModelDeploymentError(f"Request error during deployment: {e}")

    async def _poll_deployment_status(
        self,
        deploy_id: str,
        progress_callback: Any | None = None,
    ) -> dict[str, Any]:
        """Poll deployment status until complete."""
        max_attempts = 120  # 10 minutes with 5 second intervals
        attempt = 0

        while attempt < max_attempts:
            try:
                response = await self._client.get(f"/api/v1/models/deploy/{deploy_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if progress_callback:
                        progress = DeployProgress(
                            stage=data.get("stage", "deploying"),
                            percent_complete=data.get("progress", 0),
                            bytes_transferred=data.get("bytes_transferred", 0),
                            total_bytes=data.get("total_bytes", 0),
                        )
                        await progress_callback(progress)

                    if status == "completed":
                        return data
                    elif status == "failed":
                        raise ModelDeploymentError(data.get("error", "Deployment failed"))

                await asyncio.sleep(5)
                attempt += 1

            except httpx.RequestError:
                await asyncio.sleep(5)
                attempt += 1

        raise DeviceTimeoutError("Deployment status polling timed out")

    async def sync_data(
        self,
        request: SyncRequest,
        progress_callback: Any | None = None,
    ) -> dict[str, Any]:
        """
        Sync data from/to the device.

        مزامنة البيانات من/إلى الجهاز.
        """
        if not self._client or not self.is_connected:
            raise DeviceConnectionError(f"Device {self.device_id} is not connected")

        payload = {
            "direction": request.direction.value,
            "data_types": request.data_types,
            "since": request.since.isoformat() if request.since else None,
            "force": request.force,
        }

        if request.items:
            payload["items"] = [
                {
                    "type": item.item_type,
                    "id": item.item_id,
                    "data": item.data,
                    "timestamp": item.timestamp.isoformat(),
                }
                for item in request.items
            ]

        try:
            response = await self._client.post(
                "/api/v1/sync",
                json=payload,
                timeout=httpx.Timeout(300.0),
            )

            if response.status_code in (200, 202):
                result = response.json()

                if response.status_code == 202:
                    # Sync started, poll for progress
                    sync_id = result.get("sync_id")
                    return await self._poll_sync_status(sync_id, progress_callback)

                return result
            else:
                raise DeviceConnectionError(
                    f"Sync failed: {response.status_code} - {response.text}"
                )

        except httpx.TimeoutException:
            raise DeviceTimeoutError("Data sync timed out")
        except httpx.RequestError as e:
            raise DeviceConnectionError(f"Request error during sync: {e}")

    async def _poll_sync_status(
        self,
        sync_id: str,
        progress_callback: Any | None = None,
    ) -> dict[str, Any]:
        """Poll sync status until complete."""
        max_attempts = 60  # 5 minutes with 5 second intervals
        attempt = 0

        while attempt < max_attempts:
            try:
                response = await self._client.get(f"/api/v1/sync/{sync_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if progress_callback:
                        progress = SyncProgress(
                            total_items=data.get("total_items", 0),
                            synced_items=data.get("synced_items", 0),
                            failed_items=data.get("failed_items", 0),
                            bytes_transferred=data.get("bytes_transferred", 0),
                            percent_complete=data.get("progress", 0),
                        )
                        await progress_callback(progress)

                    if status == "completed":
                        return data
                    elif status == "failed":
                        raise DeviceConnectionError(data.get("error", "Sync failed"))

                await asyncio.sleep(5)
                attempt += 1

            except httpx.RequestError:
                await asyncio.sleep(5)
                attempt += 1

        raise DeviceTimeoutError("Sync status polling timed out")

    async def execute_job(
        self,
        job_type: str,
        config: dict[str, Any],
    ) -> JobResult:
        """
        Execute a job on the device.

        تنفيذ مهمة على الجهاز.
        """
        if not self._client or not self.is_connected:
            raise DeviceConnectionError(f"Device {self.device_id} is not connected")

        payload = {
            "job_type": job_type,
            "config": config,
        }

        try:
            response = await self._client.post(
                "/api/v1/jobs/execute",
                json=payload,
                timeout=httpx.Timeout(config.get("timeout_seconds", 300)),
            )

            if response.status_code == 200:
                data = response.json()
                return JobResult(
                    success=data.get("success", False),
                    message=data.get("message"),
                    output_data=data.get("output", {}),
                    execution_time_ms=data.get("execution_time_ms"),
                    detections_count=data.get("detections_count"),
                    artifacts=data.get("artifacts", []),
                )
            else:
                return JobResult(
                    success=False,
                    message=f"Job failed with status {response.status_code}",
                    error_code=f"HTTP_{response.status_code}",
                )

        except httpx.TimeoutException:
            return JobResult(
                success=False,
                message="Job execution timed out",
                message_ar="انتهت مهلة تنفيذ المهمة",
                error_code="TIMEOUT",
            )
        except httpx.RequestError as e:
            return JobResult(
                success=False,
                message=f"Connection error: {e}",
                error_code="CONNECTION_ERROR",
            )


class DeviceManager:
    """
    Manages all edge device connections.

    يدير جميع اتصالات أجهزة الحافة.
    """

    def __init__(self):
        """Initialize device manager."""
        self._connections: dict[UUID, DeviceConnection] = {}
        self._devices: dict[UUID, EdgeDevice] = {}
        self._lock = asyncio.Lock()
        self._heartbeat_task: asyncio.Task | None = None
        self._running = False

    @property
    def connected_devices(self) -> list[UUID]:
        """Get list of connected device IDs."""
        return [device_id for device_id, conn in self._connections.items() if conn.is_connected]

    @property
    def total_devices(self) -> int:
        """Get total number of registered devices."""
        return len(self._devices)

    async def start(self) -> None:
        """Start the device manager and heartbeat monitoring."""
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("device_manager_started")

    async def stop(self) -> None:
        """Stop the device manager and close all connections."""
        self._running = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._heartbeat_task

        # Close all connections
        async with self._lock:
            for conn in self._connections.values():
                await conn.disconnect()
            self._connections.clear()

        logger.info("device_manager_stopped")

    async def register_device(self, device: EdgeDevice) -> DeviceConnection | None:
        """
        Register a new device and establish connection.

        تسجيل جهاز جديد وإنشاء اتصال.
        """
        async with self._lock:
            self._devices[device.id] = device

            if device.ip_address:
                conn = DeviceConnection(
                    device_id=device.id,
                    ip_address=device.ip_address,
                    api_port=settings.jetson_api_port,
                    ssh_port=settings.jetson_ssh_port,
                )

                if await conn.connect():
                    self._connections[device.id] = conn
                    logger.info(
                        "device_registered",
                        device_id=str(device.id),
                        name=device.name,
                    )
                    return conn

            logger.info(
                "device_registered_offline",
                device_id=str(device.id),
                name=device.name,
            )
            return None

    async def unregister_device(self, device_id: UUID) -> bool:
        """
        Unregister a device and close its connection.

        إلغاء تسجيل جهاز وإغلاق اتصاله.
        """
        async with self._lock:
            if device_id in self._connections:
                await self._connections[device_id].disconnect()
                del self._connections[device_id]

            if device_id in self._devices:
                del self._devices[device_id]
                logger.info("device_unregistered", device_id=str(device_id))
                return True

            return False

    async def get_connection(self, device_id: UUID) -> DeviceConnection | None:
        """Get connection for a device."""
        return self._connections.get(device_id)

    async def get_device(self, device_id: UUID) -> EdgeDevice | None:
        """Get device by ID."""
        return self._devices.get(device_id)

    async def get_all_devices(self, tenant_id: UUID | None = None) -> list[EdgeDevice]:
        """Get all registered devices, optionally filtered by tenant."""
        devices = list(self._devices.values())
        if tenant_id:
            devices = [d for d in devices if d.tenant_id == tenant_id]
        return devices

    async def update_device_status(
        self,
        device_id: UUID,
        status: DeviceStatus,
    ) -> None:
        """Update device status."""
        if device_id in self._devices:
            self._devices[device_id].status = status
            self._devices[device_id].updated_at = datetime.utcnow()

    async def update_device_metrics(
        self,
        device_id: UUID,
        metrics: DeviceMetrics,
    ) -> None:
        """Update device metrics."""
        if device_id in self._devices:
            self._devices[device_id].metrics = metrics
            self._devices[device_id].last_seen = datetime.utcnow()

    async def _heartbeat_loop(self) -> None:
        """Background task to check device heartbeats."""
        while self._running:
            try:
                await self._check_heartbeats()
                await asyncio.sleep(settings.edge_heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("heartbeat_loop_error", error=str(e))
                await asyncio.sleep(5)

    async def _check_heartbeats(self) -> None:
        """Check heartbeat for all connected devices."""
        async with self._lock:
            for device_id, conn in list(self._connections.items()):
                try:
                    if await conn.heartbeat():
                        # Update metrics
                        try:
                            metrics = await conn.get_metrics()
                            await self.update_device_metrics(device_id, metrics)
                            await self.update_device_status(
                                device_id,
                                DeviceStatus.ONLINE,
                            )
                        except Exception:
                            pass
                    else:
                        # Mark device as offline if heartbeat fails
                        timeout = timedelta(seconds=settings.edge_timeout_threshold)
                        if (
                            conn._last_heartbeat
                            and datetime.utcnow() - conn._last_heartbeat > timeout
                        ):
                            await self.update_device_status(
                                device_id,
                                DeviceStatus.OFFLINE,
                            )
                except Exception as e:
                    logger.warning(
                        "heartbeat_check_failed",
                        device_id=str(device_id),
                        error=str(e),
                    )

    async def broadcast_message(
        self,
        message_type: str,
        payload: dict[str, Any],
        device_ids: list[UUID] | None = None,
    ) -> dict[UUID, bool]:
        """
        Broadcast a message to multiple devices.

        بث رسالة إلى عدة أجهزة.
        """
        results = {}
        targets = device_ids or list(self._connections.keys())

        for device_id in targets:
            conn = self._connections.get(device_id)
            if conn and conn.is_connected:
                try:
                    response = await conn._client.post(
                        "/api/v1/messages",
                        json={"type": message_type, "payload": payload},
                        timeout=httpx.Timeout(10.0),
                    )
                    results[device_id] = response.status_code == 200
                except Exception:
                    results[device_id] = False
            else:
                results[device_id] = False

        return results


# Global device manager instance
_device_manager: DeviceManager | None = None


def get_device_manager() -> DeviceManager:
    """Get the global device manager instance."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager
